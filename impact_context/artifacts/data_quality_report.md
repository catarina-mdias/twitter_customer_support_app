# Data Quality Report

_Generated: 2025-09-30_00-03-32_

## Executive Summary
- Dataset file: `/home/sandbox/data/customer_support_on_twitter/Tweets.csv`
- Response pairs analyzed (sample): **44,488**  
- Response time (seconds): mean **17180.8**, median **1140.5**, p90 **30222.2**

## Schema Overview (sample)
See `table_schema_overview.csv` for full details.

## Quality Metrics (sample)
See `table_quality_summary.csv`. Key issues:
- **response_tweet_id**: 32.8% nulls (dtype: object)
- **in_response_to_tweet_id**: 26.0% nulls (dtype: float64)
- **tweet_id**: 0.0% nulls (dtype: int64)
- **author_id**: 0.0% nulls (dtype: object)
- **inbound**: 0.0% nulls (dtype: bool)
- **created_at**: 0.0% nulls (dtype: object)
- **text**: 0.0% nulls (dtype: object)

## Recommendations
- Normalize timestamps → UTC, and validate monotonicity in threads.
- Index keys: `tweet_id`, `in_response_to_tweet_id`, `author_id` for faster joins.
- Consider deduplication rules for retweets/duplicates.
- Add sentiment & topic columns (next step) to strengthen product insights.
