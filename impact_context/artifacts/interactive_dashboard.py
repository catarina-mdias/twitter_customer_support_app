
import streamlit as st
import pandas as pd
import numpy as np
import pathlib
import matplotlib.pyplot as plt

ART_DIR = pathlib.Path(__file__).resolve().parent


st.set_page_config(page_title="IMPACT Interactive Dashboard", layout="wide")
st.title("IMPACT Interactive Dashboard")
st.caption("Auto-generated on 2025-09-30_00-03-32")

# Utility loaders
@st.cache_data(show_spinner=False)
def load_csv(name):
    p = ART_DIR / name
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p)

pairs = load_csv("response_pairs_sample.csv")
resp_by_author = load_csv("response_time_by_author_sample.csv")
vol_by_author = load_csv("volume_by_author_sample.csv")
schema_df = load_csv("table_schema_overview.csv")
quality_df = load_csv("table_quality_summary.csv")

tabs = st.tabs(["Overview", "Data Quality", "Response Analysis", "Authors"])

with tabs[0]:
    st.subheader("Overview")
    st.markdown("- Loaded tables: response_pairs_sample, response_time_by_author_sample, volume_by_author_sample")
    st.write("Pairs shape:", pairs.shape)
    st.write("Authors (resp):", resp_by_author.shape, "Authors (vol):", vol_by_author.shape)

with tabs[1]:
    st.subheader("Data Quality")
    if not quality_df.empty:
        st.write("Quality Summary")
        st.dataframe(quality_df)
    if not schema_df.empty:
        st.write("Schema Overview")
        st.dataframe(schema_df)

with tabs[2]:
    st.subheader("Response Analysis")

    if pairs.empty:
        st.info("No pairs loaded.")
    else:
        # Ensure 'created_at_customer' is datetime and timezone-aware (UTC)
        pairs["created_at_customer"] = pd.to_datetime(
            pairs["created_at_customer"], errors="coerce"
        ).dt.tz_convert("UTC")  # Convert to UTC if already timezone-aware

        # Filters: date range and agent
        col1, col2 = st.columns(2)

        # Date range
        min_dt = pairs["created_at_customer"].min()
        max_dt = pairs["created_at_customer"].max()
        start, end = col1.date_input(
            "Date range (by customer tweet)",
            (min_dt.date() if pd.notna(min_dt) else None,
             max_dt.date() if pd.notna(max_dt) else None)
        )

        # Agent filter as dropdown
        agent_options = ["All"] + sorted(pairs["agent_id"].dropna().astype(str).unique().tolist())
        selected_agent = col2.selectbox("Filter by Agent ID", agent_options)

        # Apply filters
        df = pairs.copy()

        # Date filter
        if start and end:
            start_ts = pd.Timestamp(start).tz_localize("UTC")
            end_ts = pd.Timestamp(end).tz_localize("UTC") + pd.Timedelta(days=1)
            df = df[(df["created_at_customer"] >= start_ts) & (df["created_at_customer"] <= end_ts)]

        # Agent filter
        if selected_agent != "All":
            df = df[df["agent_id"].astype(str) == selected_agent]

        st.write("Filtered pairs:", df.shape[0])

        # Histogram of response times (in minutes)
        if not df.empty and "response_time_seconds" in df.columns:
            st.write("Response Time Distribution (minutes)")
            vals_min = (df["response_time_seconds"].dropna().clip(
                lower=0, upper=df["response_time_seconds"].quantile(0.99)
            ) / 60)  # convert seconds to minutes

            fig, ax = plt.subplots()
            ax.hist(vals_min, bins=50)
            ax.set_xlabel("Minutes")
            ax.set_ylabel("Frequency")
            st.pyplot(fig)
        else:
            st.info("No response times available for the selected filters.")


with tabs[3]:
    st.subheader("Authors")

    if vol_by_author.empty:
        st.info("No author volume table loaded.")
    else:
        # Step 1: Compute author-level metrics from response_pairs_sample
        author_metrics = (
            pairs.groupby("customer_id")["response_time_seconds"]
            .agg(
                n_responses="count",
                mean_mins="mean",
                median_mins="median",
                p90_mins=lambda x: x.quantile(0.9)
            )
            .reset_index()
            .rename(columns={"customer_id": "author_id"})
        )

        # Convert seconds → minutes
        for col in ["mean_mins", "median_mins", "p90_mins"]:
            author_metrics[col] = author_metrics[col] / 60

        # Step 2: Map authors to agent (first agent per author)
        author_agent = pairs.groupby("customer_id")["agent_id"].first().reset_index()
        author_agent.rename(columns={"customer_id": "author_id"}, inplace=True)

        # Ensure string types for merges
        vol_by_author["author_id"] = vol_by_author["author_id"].astype(str)
        author_metrics["author_id"] = author_metrics["author_id"].astype(str)
        author_agent["author_id"] = author_agent["author_id"].astype(str)

        # Step 3: Merge vol_by_author with author-level metrics
        merged = vol_by_author.merge(author_metrics, on="author_id", how="left")

        # Step 4: Merge agent mapping (just to have agent_id)
        merged = merged.merge(author_agent, on="author_id", how="left")
        merged["agent_id"] = merged["agent_id"].astype(str)

        # Filters: min inbound, agent filter, top N
        col1, col2, col3 = st.columns([2,1,1])
        min_in = int(merged["inbound_msgs"].min()) if "inbound_msgs" in merged else 0
        max_in = int(merged["inbound_msgs"].max()) if "inbound_msgs" in merged else 0
        inbound_min = col1.slider("Min inbound messages", min_value=min_in, max_value=max_in, value=min_in)
        agent_filter = col2.text_input("Filter by Agent ID contains", "")
        topn = col3.number_input("Top N", min_value=10, max_value=200, value=50, step=10)

        # Apply filters
        f = merged.copy()
        if "inbound_msgs" in f:
            f = f[f["inbound_msgs"] >= inbound_min]
        if agent_filter.strip():
            f = f[f["agent_id"].str.contains(agent_filter.strip(), na=False)]
        f = f.sort_values(["inbound_msgs","outbound_msgs"], ascending=False).head(int(topn))

        # Display dataframe
        st.dataframe(f)

        # Scatter plot: inbound vs mean response time (author-level, in minutes)
        if "mean_mins" in f.columns:
            valid = f[["inbound_msgs","mean_mins"]].dropna()
            if not valid.empty:
                st.write("Inbound volume vs Mean response time (minutes)")
                fig2, ax2 = plt.subplots()
                ax2.scatter(valid["inbound_msgs"], valid["mean_mins"])
                ax2.set_xlabel("Inbound messages")
                ax2.set_ylabel("Mean response time (minutes)")
                st.pyplot(fig2)



st.divider()
st.download_button("Download response_pairs_sample.csv", (ART_DIR/"response_pairs_sample.csv").read_bytes(), file_name="response_pairs_sample.csv")
st.download_button("Download response_time_by_author_sample.csv", (ART_DIR/"response_time_by_author_sample.csv").read_bytes(), file_name="response_time_by_author_sample.csv")
st.download_button("Download volume_by_author_sample.csv", (ART_DIR/"volume_by_author_sample.csv").read_bytes(), file_name="volume_by_author_sample.csv")
