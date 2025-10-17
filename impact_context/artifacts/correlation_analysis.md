# Correlation & Pattern Analysis — Latency Drivers
_Generated: 2025-10-17_

> Alignment: Applied directives from `impact_framework.yaml` keys: project, version, framework, globals, required_artifacts, tools, session_documentation, cursor_integration...

## Key Latency Distribution
- **Mean:** 17180.8s | **Median:** 1140.5s | **p90:** 30222.2s  
Distribution is **heavy‑tailed**: p90 ≫ median. For operations, median and percentiles are the reliable KPIs.

## Volume vs Latency (per Author)
Observed correlation between inbound volume and mean response time was inconclusive (**NaN** in sample), hinting at **data gaps** or the need for **time‑bucketed analysis** (e.g., hourly/daypart). Action: compute correlation per period and apply mixed‑effects modeling to separate brand effects and workload effects.

### Example Brand Snapshots (sample)
- **TMobileHelp** — mean ≈ **500s**: a fast responder archetype (likely strong routing/playbooks).
- **VirginTrains** — mean ≈ **771s**: consistently fast.
- **Delta** — mean ≈ **1536s**: moderate response speed.
- **AppleSupport** — mean ≈ **5914s**: slower; potential queueing/triage complexity.
- **British_Airways** — mean ≈ **12631s**: long waits; likely operational bottlenecks.
- **hulu_support** — mean ≈ **70091s**: extreme tail behavior; probably pairing/outlier artifacts.

> See `response_time_by_author_sample.csv` for full author stats and `volume_by_author_sample.csv` for inbound/outbound volumes.

## Patterns & Hypotheses
1. **Queueing Pressure**: Latency rises during spikes; requires intraday staffing alignment.
2. **Case Complexity**: Technical/transactional topics might inflate handling/triage time.
3. **Channel Friction**: Public → DM handoff and re‑open patterns can elongate measured latency.
4. **Policy/Governance**: Legal reviews for airlines/finance could add systemic delays.

## What to Measure Next
- **Time‑bucketed correlation**: volume vs p50/p90 by hour/day to isolate staffing effects.
- **Topic‑stratified latency**: p50/p90 by `topic_tag` to pinpoint complex intents.
- **Sentiment‑stratified latency**: does negative sentiment accelerate triage?
- **First Reply vs Resolution**: split KPIs to avoid confounding first‑touch with full resolution.

## Actionable Signals
- Adopt **p50/p90 Latency by Brand** as the core benchmark.
- Create **Latency SLA tiers** (Gold/Silver/Bronze) for brands with peer‑group comparisons.
- Build **Early‑Warning Alerts** when p90 exceeds baseline by +25% within any 2‑hour window.
