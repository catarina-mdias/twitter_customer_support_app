
import streamlit as st
import pandas as pd
import numpy as np
import pathlib
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

ART_DIR = pathlib.Path(__file__).resolve().parent

# Page configuration
st.set_page_config(
    page_title="IMPACT Framework Dashboard", 
    layout="wide",
    page_icon="📊"
)

# Header
st.title("📊 IMPACT Framework Interactive Dashboard")
st.markdown("---")

# Utility loaders
@st.cache_data(show_spinner=False)
def load_csv(name):
    """Load CSV file with error handling"""
    p = ART_DIR / name
    if not p.exists():
        st.warning(f"File {name} not found")
        return pd.DataFrame()
    try:
        return pd.read_csv(p)
    except Exception as e:
        st.error(f"Error loading {name}: {e}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_markdown(name):
    """Load markdown file content"""
    p = ART_DIR / name
    if not p.exists():
        return ""
    try:
        return p.read_text(encoding='utf-8')
    except Exception as e:
        st.error(f"Error loading {name}: {e}")
        return ""

def normalize_datetime_column(df, column_name):
    """Normalize datetime column to timezone-naive for consistent comparisons"""
    if column_name in df.columns:
        df[column_name] = pd.to_datetime(df[column_name], errors="coerce")
        # Convert to timezone-naive if timezone-aware
        if hasattr(df[column_name].dtype, 'tz') and df[column_name].dtype.tz is not None:
            df[column_name] = df[column_name].dt.tz_localize(None)
    return df


# Load all datasets (with progress indicator)
with st.spinner("🔄 Loading datasets..."):
    pairs = load_csv("response_pairs_sample.csv")
    resp_by_author = load_csv("response_time_by_author_sample.csv")
    vol_by_author = load_csv("volume_by_author_sample.csv")
    schema_df = load_csv("table_schema_overview.csv")
    quality_df = load_csv("table_quality_summary.csv")
    scenarios_df = load_csv("scenarios_prioritized_table.csv")
    correlation_df = load_csv("correlation_matrix.csv")
    brand_counts = load_csv("brand_counts.csv")

    # Normalize datetime columns to prevent comparison issues
    pairs = normalize_datetime_column(pairs, "created_at_customer")
    pairs = normalize_datetime_column(pairs, "created_at_agent")

# Load IMPACT framework artifacts
correlation_analysis = load_markdown("correlation_analysis.md")
market_analysis = load_markdown("market_analysis.md")
scenarios_prioritized = load_markdown("scenarios_prioritized.md")
kpi_definitions = load_markdown("kpi_definitions.md")
data_quality_report = load_markdown("data_quality_report.md")

# Sidebar with project overview
with st.sidebar:
    st.header("📋 Project Overview")
    st.markdown("""
    **IMPACT Framework Implementation**
    
    This dashboard integrates all outputs from the IMPACT framework analysis for Twitter Customer Support Analytics.
    """)
    
    st.header("📊 Dataset Summary")
    if not pairs.empty:
        st.metric("Response Pairs", f"{len(pairs):,}")
    if not resp_by_author.empty:
        st.metric("Authors Analyzed", f"{len(resp_by_author):,}")
    if not vol_by_author.empty:
        st.metric("Volume Records", f"{len(vol_by_author):,}")
    
    st.header("🎯 Key Metrics")
    if not pairs.empty and "response_time_seconds" in pairs.columns:
        median_latency = pairs["response_time_seconds"].median() / 60  # Convert to minutes
        p90_latency = pairs["response_time_seconds"].quantile(0.9) / 60
        st.metric("Median Response Time", f"{median_latency:.1f} min")
        st.metric("P90 Response Time", f"{p90_latency:.1f} min")
    
    st.markdown("---")
    
    # Quick Actions
    st.header("🚀 Quick Actions")
    if st.button("📥 Download All Data"):
        st.session_state.show_downloads = True
    
    if st.button("📊 View Framework Summary"):
        st.session_state.show_summary = True

# Main content area with tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Overview", 
    "🔍 I - Inspect", 
    "🔗 M - Map", 
    "🎯 P - Position", 
    "⚡ A - Act", 
    "📈 C - Calibrate", 
    "👥 Brand Performance"
])

# Overview Tab
with tab1:
    st.header("📊 Project Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Response Pairs", f"{len(pairs):,}" if not pairs.empty else "0")
        st.metric("Authors Analyzed", f"{len(resp_by_author):,}" if not resp_by_author.empty else "0")
    
    with col2:
        if not pairs.empty and "response_time_seconds" in pairs.columns:
            median_latency = pairs["response_time_seconds"].median() / 60
            p90_latency = pairs["response_time_seconds"].quantile(0.9) / 60
            st.metric("Median Response Time", f"{median_latency:.1f} min")
            st.metric("P90 Response Time", f"{p90_latency:.1f} min")
    
    with col3:
        if not brand_counts.empty:
            top_brands = brand_counts.head(5)
            st.metric("Top Brands", len(brand_counts))
            st.dataframe(top_brands[['brand', 'count']] if 'brand' in top_brands.columns else top_brands.head())
    
    st.markdown("---")
    
    # Dataset summary
    st.subheader("📋 Dataset Summary")
    if not pairs.empty:
        st.write(f"**Response Pairs Dataset**: {pairs.shape[0]:,} rows × {pairs.shape[1]} columns")
        st.write(f"**Columns**: {', '.join(pairs.columns.tolist())}")
    
    if not resp_by_author.empty:
        st.write(f"**Author Response Times**: {resp_by_author.shape[0]:,} rows × {resp_by_author.shape[1]} columns")
    
    if not vol_by_author.empty:
        st.write(f"**Volume by Author**: {vol_by_author.shape[0]:,} rows × {vol_by_author.shape[1]} columns")

# Data Quality Tab (I - Inspect)
with tab2:
    st.header("🔍 Data Quality Assessment")
    
    if data_quality_report:
        st.markdown(data_quality_report)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not quality_df.empty:
            st.subheader("📊 Quality Metrics")
            st.dataframe(quality_df, use_container_width=True)
    
    with col2:
        if not schema_df.empty:
            st.subheader("🗂️ Schema Overview")
            st.dataframe(schema_df, use_container_width=True)
    
    # Data quality visualizations
    if not pairs.empty:
        st.subheader("📈 Data Quality Visualizations")
        
        # Missing data heatmap
        missing_data = pairs.isnull().sum()
        if missing_data.sum() > 0:
            fig_missing = px.bar(
                x=missing_data.index, 
                y=missing_data.values,
                title="Missing Data by Column",
                labels={'x': 'Column', 'y': 'Missing Count'}
            )
            st.plotly_chart(fig_missing, use_container_width=True)
        
        # Response time distribution
        if "response_time_seconds" in pairs.columns:
            response_times = pairs["response_time_seconds"].dropna() / 60  # Convert to minutes
            response_times = response_times[response_times <= response_times.quantile(0.95)]  # Remove outliers
            
            fig_dist = px.histogram(
                response_times, 
                nbins=50,
                title="Response Time Distribution (minutes)",
                labels={'x': 'Response Time (minutes)', 'y': 'Frequency'}
            )
            st.plotly_chart(fig_dist, use_container_width=True)

# Correlation Analysis Tab (M - Map)
with tab3:
    st.header("🔗 Correlation & Pattern Analysis")
    
    if correlation_analysis:
        st.markdown(correlation_analysis)
    
    if not correlation_df.empty:
        st.subheader("📊 Correlation Matrix")
        
        # Create correlation heatmap
        corr_matrix = correlation_df.set_index(correlation_df.columns[0])
        fig_corr = px.imshow(
            corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            color_continuous_scale='RdBu',
            title="Feature Correlation Matrix"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    
    # Brand performance analysis
    if not resp_by_author.empty and not brand_counts.empty:
        st.subheader("🏢 Brand Performance Analysis")
        
        # Merge brand data with response times
        brand_performance = resp_by_author.copy()
        if 'author_id' in brand_performance.columns and 'brand' in brand_counts.columns:
            # Ensure compatible data types for merge
            brand_perf_copy = brand_performance.copy()
            brand_counts_copy = brand_counts.copy()
            
            # Convert both columns to string to ensure compatibility
            brand_perf_copy['author_id'] = brand_perf_copy['author_id'].astype(str)
            brand_counts_copy['brand'] = brand_counts_copy['brand'].astype(str)
            
            brand_performance = brand_perf_copy.merge(
                brand_counts_copy, 
                left_on='author_id', 
                right_on='brand', 
                how='left'
            )
            
            # Top performing brands by response time
            if 'mean_response_time' in brand_performance.columns:
                top_brands = brand_performance.nsmallest(10, 'mean_response_time')
                
                fig_brands = px.bar(
                    top_brands,
                    x='author_id',
                    y='mean_response_time',
                    title="Top 10 Fastest Responding Brands",
                    labels={'mean_response_time': 'Mean Response Time (seconds)', 'author_id': 'Brand'}
                )
                st.plotly_chart(fig_brands, use_container_width=True)

# Market Analysis Tab (P - Position)
with tab4:
    st.header("🎯 Market Analysis & Opportunities")
    
    if market_analysis:
        st.markdown(market_analysis)
    
    # Market opportunity sizing
    st.subheader("💰 Market Opportunity Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Addressable Market", "€18-45M", "Benchmark/Telemetry Niche")
        st.metric("Target Brands", "~3,000", "Mid-to-large active brands")
    
    with col2:
        st.metric("Pricing Tier 1", "€5-8k/year", "Benchmark Reports")
        st.metric("Pricing Tier 2", "€12-18k/year", "Telemetry Pro")
    
    # Competitive positioning
    st.subheader("🏆 Competitive Positioning")
    
    competitors = {
        'Platform': ['Native Platform Analytics', 'Social Listening Suites', 'BPO/Workforce Tools'],
        'Strengths': ['Basic averages', 'Strong sentiment/mentions', 'Staffing models'],
        'Weaknesses': ['Limited pairing logic', 'Weaker SLA pairing', 'Lack neutral benchmarking'],
        'Our Advantage': ['Thread-safe latency science', 'Open KPIs (p50/p90)', 'Brand-level benchmark']
    }
    
    comp_df = pd.DataFrame(competitors)
    st.dataframe(comp_df, use_container_width=True)
    
    # Stakeholder personas
    st.subheader("👥 Key Stakeholders")
    
    personas = {
        'Role': ['Support Operations Manager', 'Head of CX', 'Product Owner (Automation)'],
        'Key Needs': ['Intraday early-warning', 'Brand-level positioning', 'Topic and triage insights'],
        'Success Metrics': ['SLA compliance', 'Peer benchmarking', 'Automation targeting']
    }
    
    persona_df = pd.DataFrame(personas)
    st.dataframe(persona_df, use_container_width=True)

# Scenarios & MVP Tab (A - Act)
with tab5:
    st.header("⚡ Scenario Evaluation & MVP Definition")
    
    if scenarios_prioritized:
        st.markdown(scenarios_prioritized)
    
    if not scenarios_df.empty:
        st.subheader("📊 Scenario Prioritization Matrix")
        
        # Create impact vs effort scatter plot
        fig_scenarios = px.scatter(
            scenarios_df,
            x='effort',
            y='impact',
            size='priority_score',
            hover_data=['name', 'notes'],
            title="Scenario Impact vs Effort Matrix",
            labels={'effort': 'Implementation Effort', 'impact': 'Business Impact'}
        )
        st.plotly_chart(fig_scenarios, use_container_width=True)
        
        # Top scenarios table
        st.subheader("🎯 Top Priority Scenarios")
        top_scenarios = scenarios_df.nlargest(5, 'priority_score')
        st.dataframe(top_scenarios, use_container_width=True)
    
    # MVP Definition
    st.subheader("🚀 MVP Definition")
    
    mvp_features = {
        'Feature': [
            'Data pairing & winsorization pipeline',
            'KPI service for p50/p90 per brand/day',
            'Dashboard with trend + peer ranking',
            'Alert engine (static thresholds)',
            'NLP enrichment (topic/sentiment)'
        ],
        'Sprint': ['Sprint 1', 'Sprint 1', 'Sprint 2', 'Sprint 2', 'Sprint 3'],
        'Acceptance Criteria': [
            '≥95% valid pairs classified',
            'KPI freshness ≤4 hours',
            'Peer ranking functional',
            'Alert precision ≥80%',
            'Topic views operational'
        ]
    }
    
    mvp_df = pd.DataFrame(mvp_features)
    st.dataframe(mvp_df, use_container_width=True)

# KPI Dashboard Tab (C - Calibrate)
with tab6:
    st.header("📈 KPI Dashboard & Measurement Framework")
    
    if kpi_definitions:
        st.markdown(kpi_definitions)
    
    # KPI Metrics
    st.subheader("🎯 Key Performance Indicators")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("P90 First-Reply Latency", "30222.2s", "Target: -20%")
        st.metric("P50 First-Reply Latency", "1140.5s", "Target: -10%")
    
    with col2:
        st.metric("Pair Validity Rate", "95%", "Target: ≥95%")
        st.metric("KPI Freshness", "4h", "Target: ≤4h")
    
    with col3:
        st.metric("Alert Acceptance Rate", "75%", "Target: ≥75%")
        st.metric("Action Rate", "40%", "Target: ≥40%")
    
    # KPI Hierarchy Visualization
    st.subheader("📊 KPI Hierarchy")
    
    kpi_hierarchy = {
        'Level': ['Business (CX Outcomes)', 'Product (Adoption & Utility)', 'Technical (Reliability & Data Quality)'],
        'Primary KPIs': [
            'P90 First-Reply Latency, P50 First-Reply Latency, Consistency Index',
            'Alert Acceptance Rate, Action Rate, Dashboard Active Users',
            'Pair Validity Rate, KPI Freshness, Tail Winsorization Coverage'
        ]
    }
    
    kpi_hierarchy_df = pd.DataFrame(kpi_hierarchy)
    st.dataframe(kpi_hierarchy_df, use_container_width=True)
    
    # Performance tracking
    if not pairs.empty and "response_time_seconds" in pairs.columns:
        st.subheader("📈 Performance Tracking")
        
        # Response time trends
        response_times = pairs["response_time_seconds"].dropna() / 60  # Convert to minutes
        
        # Create performance metrics
        p50_current = response_times.quantile(0.5)
        p90_current = response_times.quantile(0.9)
        
        # Target calculations (assuming baseline from sample)
        p50_target = p50_current * 0.9  # -10% target
        p90_target = p90_current * 0.8  # -20% target
        
        # Performance vs targets
        perf_data = {
            'Metric': ['P50 Response Time', 'P90 Response Time'],
            'Current (min)': [p50_current, p90_current],
            'Target (min)': [p50_target, p90_target],
            'Progress': [f"{((p50_target - p50_current) / p50_current * 100):.1f}%", 
                        f"{((p90_target - p90_current) / p90_current * 100):.1f}%"]
        }
        
        perf_df = pd.DataFrame(perf_data)
        st.dataframe(perf_df, use_container_width=True)

# Brand Performance Tab
with tab7:
    st.header("👥 Brand Performance Analysis")

    if pairs.empty:
        st.info("No response pairs data available.")
    else:

        # Filters
        col1, col2 = st.columns(2)

        # Date range filter
        if "created_at_customer" in pairs.columns and not pairs["created_at_customer"].isna().all():
            min_dt = pairs["created_at_customer"].min()
            max_dt = pairs["created_at_customer"].max()
            start, end = col1.date_input(
            "Date range (by customer tweet)",
            (min_dt.date() if pd.notna(min_dt) else None,
             max_dt.date() if pd.notna(max_dt) else None)
        )

        # Agent filter
        if "agent_id" in pairs.columns:
            agent_options = ["All"] + sorted(pairs["agent_id"].dropna().astype(str).unique().tolist())
            selected_agent = col2.selectbox("Filter by Agent ID", agent_options)

        # Apply filters
        df = pairs.copy()

        if "created_at_customer" in df.columns and start and end:
            # Create timezone-naive timestamps for comparison
            start_ts = pd.Timestamp(start)
            end_ts = pd.Timestamp(end) + pd.Timedelta(days=1)
            
            # Filter by date range
            df = df[(df["created_at_customer"] >= start_ts) & (df["created_at_customer"] <= end_ts)]

        if "agent_id" in df.columns and selected_agent != "All":
            df = df[df["agent_id"].astype(str) == selected_agent]

        st.write(f"**Filtered pairs**: {df.shape[0]:,}")

        # Response time analysis
        if not df.empty and "response_time_seconds" in df.columns:
            st.subheader("📊 Response Time Analysis")
            
            # Response time distribution
            response_times = df["response_time_seconds"].dropna() / 60  # Convert to minutes
            response_times = response_times[response_times <= response_times.quantile(0.99)]  # Remove extreme outliers
            
            fig_dist = px.histogram(
                response_times, 
                nbins=50,
                title="Response Time Distribution (minutes)",
                labels={'x': 'Response Time (minutes)', 'y': 'Frequency'}
            )
            st.plotly_chart(fig_dist, use_container_width=True)
            
            # Brand-level performance
            if "customer_id" in df.columns:
                st.subheader("🏢 Brand-Level Performance")
                
                brand_performance = (
                    df.groupby("customer_id")["response_time_seconds"]
                    .agg([
                        ('count', 'count'),
                        ('mean_minutes', lambda x: x.mean() / 60),
                        ('median_minutes', lambda x: x.median() / 60),
                        ('p90_minutes', lambda x: x.quantile(0.9) / 60)
                    ])
                    .reset_index()
                    .sort_values('median_minutes')
                )
                
                # Top 20 brands by median response time
                top_brands = brand_performance.head(20)
                
                fig_brands = px.bar(
                    top_brands,
                    x='customer_id',
                    y='median_minutes',
                    title="Top 20 Brands by Median Response Time",
                    labels={'median_minutes': 'Median Response Time (minutes)', 'customer_id': 'Brand'}
                )
                fig_brands.update_layout(xaxis=dict(tickangle=45))
                st.plotly_chart(fig_brands, use_container_width=True)
                
                # Volume vs Response Time correlation
                if not vol_by_author.empty:
                    st.subheader("📈 Volume vs Response Time Correlation")
                    
                    # Merge volume data - ensure compatible data types
                    brand_perf_copy = brand_performance.copy()
                    vol_by_author_copy = vol_by_author.copy()
                    
                    # Convert both columns to string to ensure compatibility
                    brand_perf_copy['customer_id'] = brand_perf_copy['customer_id'].astype(str)
                    vol_by_author_copy['author_id'] = vol_by_author_copy['author_id'].astype(str)
                    
                    merged_performance = brand_perf_copy.merge(
                        vol_by_author_copy, 
                        left_on='customer_id', 
                        right_on='author_id', 
                        how='left'
                    )
                    
                    if 'inbound_msgs' in merged_performance.columns:
                        valid_data = merged_performance[['inbound_msgs', 'median_minutes']].dropna()
                        
                        if not valid_data.empty:
                            fig_corr = px.scatter(
                                valid_data,
                                x='inbound_msgs',
                                y='median_minutes',
                                title="Inbound Volume vs Median Response Time",
                                labels={'inbound_msgs': 'Inbound Messages', 'median_minutes': 'Median Response Time (minutes)'}
                            )
                            st.plotly_chart(fig_corr, use_container_width=True)

# Download Section (triggered from sidebar)
if st.session_state.get('show_downloads', False):
    st.markdown("---")
    st.header("📥 Data Export & Downloads")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📊 Download Datasets")
        if (ART_DIR/"response_pairs_sample.csv").exists():
            st.download_button(
                "Download Response Pairs", 
                (ART_DIR/"response_pairs_sample.csv").read_bytes(), 
                file_name="response_pairs_sample.csv",
                mime="text/csv"
            )
        
        if (ART_DIR/"response_time_by_author_sample.csv").exists():
            st.download_button(
                "Download Author Response Times", 
                (ART_DIR/"response_time_by_author_sample.csv").read_bytes(), 
                file_name="response_time_by_author_sample.csv",
                mime="text/csv"
            )
        
        if (ART_DIR/"volume_by_author_sample.csv").exists():
            st.download_button(
                "Download Volume by Author", 
                (ART_DIR/"volume_by_author_sample.csv").read_bytes(), 
                file_name="volume_by_author_sample.csv",
                mime="text/csv"
            )
    
    with col2:
        st.subheader("📋 Download IMPACT Artifacts")
        if (ART_DIR/"data_quality_report.md").exists():
            st.download_button(
                "Download Data Quality Report", 
                (ART_DIR/"data_quality_report.md").read_bytes(), 
                file_name="data_quality_report.md",
                mime="text/markdown"
            )
        
        if (ART_DIR/"correlation_analysis.md").exists():
            st.download_button(
                "Download Correlation Analysis", 
                (ART_DIR/"correlation_analysis.md").read_bytes(), 
                file_name="correlation_analysis.md",
                mime="text/markdown"
            )
        
        if (ART_DIR/"market_analysis.md").exists():
            st.download_button(
                "Download Market Analysis", 
                (ART_DIR/"market_analysis.md").read_bytes(), 
                file_name="market_analysis.md",
                mime="text/markdown"
            )
    
    with col3:
        st.subheader("🚀 How to Run Locally")
        st.markdown("""
        **Prerequisites:**
        - Python 3.8+
        - pip install streamlit plotly pandas numpy
        
        **Run Command:**
        ```bash
        streamlit run interactive_dashboard.py
        ```
        
        **Access:** http://localhost:8501
        """)
    
    # Reset the flag
    if st.button("Close Downloads"):
        st.session_state.show_downloads = False

# Framework Summary Section (triggered from sidebar)
if st.session_state.get('show_summary', False):
    st.markdown("---")
    st.header("🎯 IMPACT Framework Summary")
    
    impact_summary = {
        'Step': ['I - Inspect', 'M - Map', 'P - Position', 'A - Act', 'C - Calibrate', 'T - Telemetry'],
        'Focus': [
            'Data Quality Assessment',
            'Correlation & Pattern Analysis',
            'Market Analysis & Opportunities', 
            'Scenario Evaluation & MVP',
            'KPI Definitions & Measurement',
            'Interactive Dashboard (this)'
        ],
        'Key Outputs': [
            'Data quality scores, schema validation',
            'Correlation matrix, brand performance',
            'Market sizing, competitive analysis',
            'Scenario prioritization, MVP definition',
            'KPI hierarchy, measurement framework',
            'Interactive exploration dashboard'
        ],
        'Status': ['✅ Complete', '✅ Complete', '✅ Complete', '✅ Complete', '✅ Complete', '✅ Complete']
    }
    
    impact_df = pd.DataFrame(impact_summary)
    st.dataframe(impact_df, use_container_width=True)
    
    st.success("🎉 **IMPACT Framework Implementation Complete!**")
    st.markdown("""
    This dashboard integrates all outputs from the IMPACT framework analysis, providing:
    - **Comprehensive data quality assessment** with visual insights
    - **Correlation analysis** revealing patterns and relationships  
    - **Market analysis** with opportunity sizing and competitive positioning
    - **Scenario evaluation** with MVP definition and sprint planning
    - **KPI framework** with measurement and monitoring strategies
    - **Interactive exploration** of all findings and datasets
    
    **Next Steps:** Use this dashboard to guide development decisions and validate the MVP approach outlined in the framework analysis.
    """)
    
    # Reset the flag
    if st.button("Close Summary"):
        st.session_state.show_summary = False
