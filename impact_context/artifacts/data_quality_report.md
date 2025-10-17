# Data Quality Report — Customer Support on Twitter
_Generated: 2025-10-17_

> Alignment: Applied directives from `impact_framework.yaml` keys: project, version, framework, globals, required_artifacts, tools, session_documentation, cursor_integration...

## Executive Summary
We assessed a large, multi-brand Twitter customer-support dataset to validate suitability for latency analytics, agent benchmarking, and CX insights. Key takeaway: **timestamps and thread-linkage are reliable enough for MVP analytics**, but **reply-link columns carry notable sparsity** that must be handled explicitly in the pipeline.

**Response time (sec):** mean **17180.8**, median **1140.5**, p90 **30222.2**.  
These heavy-tailed latencies indicate the need for robust percentile-based KPIs (p50/p90) over simple means.

### Data Scope
- Source file: `/home/sandbox/data/customer_support_on_twitter/Tweets.csv`
- Sample size used in diagnostics: **44,488** response pairs
- Entities: Tweets, Authors (brand & user), Parent–child relationships (reply links)

## Schema Overview (abridged)
- **tweet_id** (int64): unique identifier. **0% nulls**.
- **author_id** (str): brand/user handle. **0% nulls**.
- **created_at** (str/datetime): tweet timestamp (assumed UTC). **0% nulls**.
- **text** (str): tweet content. **0% nulls**.
- **inbound** (bool): whether inbound from user. **0% nulls**.
- **in_response_to_tweet_id** (float/str): parent tweet id. **~26% nulls**.
- **response_tweet_id** (str): agent reply id. **~33% nulls**.

> See `table_schema_overview.csv` for complete column profiling and `table_quality_summary.csv` for column-level metrics.

## Key Quality Findings
1. **Thread linkage sparsity**: Missing values in `in_response_to_tweet_id` and `response_tweet_id` can break naive response-pair joins.  
2. **Timestamp normalization**: Mixed string formats—ensure parsing to timezone-aware UTC.  
3. **Duplication risk**: Retweets/quotes may inflate volumes and distort SLA latency.  
4. **Author identity**: Multiple support handles per brand; standardize to a canonical brand id.  
5. **Outliers & truncation**: Extremely high latencies (10M+ seconds) likely due to cross-thread jumps or stale re-opens.

## Readiness Assessment (for MVP)
- **Latency KPIs (p50/p90)**: ✅ feasible with winsorization and thread-aware pairing.  
- **Per-brand benchmarking**: ✅ feasible after canonical brand mapping.  
- **Sentiment/topic stratification**: ⚠️ requires new NLP enrichment columns.  
- **Causal diagnostics** (workload → latency): ⚠️ requires stable inbound/outbound pairing and time-bucketing.

## Recommendations (Prioritized)
**P0 — Must do for MVP**
- Normalize all timestamps to UTC (`created_at_tz`), validate non-negative reply deltas.
- Build **thread-safe pairing**: map user inbound → first agent reply; drop or flag ambiguous pairs.
- Implement **winsorization** at p99 and cap negative/zero latencies to a floor of 1s.
- Create **canonical_brand** dimension and reference table (merge AppleSupport, AppleCare, etc.).

**P1 — Should do**
- Deduplicate retweets/quotes; mark with `tweet_type` to filter in analytics.
- Add **NLP enrichment**: sentiment (polarity), topic labels, intent; store as `sentiment_polarity`, `topic_tag`.
- Establish **data contracts** for required fields (`tweet_id`, `author_id`, `created_at`, `inbound`).

**P2 — Could do**
- Language detection & translation pipelines for non‑EN tweets.
- Spam/bot detection to remove noise.

## Data Quality Rules (for Telemetry)
- **DQ-001**: `created_at_tz` must parse and be within [2010-01-01, now].
- **DQ-002**: `response_latency_s` ≥ 1 and ≤ p99.9 cap.
- **DQ-003**: `canonical_brand` present for all agent tweets.
- **DQ-004**: `pair_status` in {valid, ambiguous, missing_parent}; ambiguous < 5% of pairs.

## Ownership & Ops
- **Data Engineering**: timestamp parsing, pairing logic, canonical brand map.
- **Data Science**: winsorization thresholds, sentiment/topic models.
- **Analytics**: KPI spec, dashboard QA, stakeholder education.

## Artifacts
- `table_schema_overview.csv` — profiling snapshot
- `table_quality_summary.csv` — quality metrics
- `inspect_profile.csv` — per-column stats
