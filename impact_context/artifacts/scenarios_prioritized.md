# Prioritized Scenarios & MVP
_Generated: 2025-10-17_

> Alignment: Applied directives from `impact_framework.yaml` keys: project, version, framework, globals, required_artifacts, tools, session_documentation, cursor_integration...

## Executive Summary
We prioritize scenarios that maximize **impact on latency reduction** with **feasible data engineering** using Twitter/X public data. The MVP centers on a **Latency Benchmark & Telemetry** that operationalizes p50/p90 KPIs with alerting.

## Scenario Catalog
1. **S1 — Latency Benchmark Dashboard**
   - **Outcome**: Brands see their p50/p90 by day and vs peer group.
   - **Users**: CX Lead, Support Ops.
   - **Data**: Thread‑safe pairs, canonical_brand map, winsorized latencies.
2. **S2 — Intraday Early‑Warning Alerts**
   - **Outcome**: Notify when p90 exceeds baseline by +25% in a 2‑h window.
   - **Users**: Support Ops Manager.
   - **Data**: Rolling time‑bucket metrics; thresholds by brand/daypart.
3. **S3 — Topic‑Stratified Insights**
   - **Outcome**: Identify topics driving long waits and target automation.
   - **Users**: Automation PO, CX Lead.
   - **Data**: Sentiment, topic tags from NLP enrichment.

## Feasibility vs Impact Matrix
| Scenario | Tech Feasibility | Business Impact | Priority |
|---|---|---|---|
| S1 | High | High | P1 |
| S2 | Medium | High | P1 |
| S3 | Medium | Medium | P2 |

## MVP Definition (Scope & Criteria)
**Scope (v1):**
- Data pairing & winsorization pipeline
- KPI service for p50/p90 per brand/day
- Dashboard with trend + peer ranking
- Alert engine (static thresholds)

**Acceptance Criteria:**
- ≥ 95% of valid pairs classified correctly (`pair_status=valid`).
- KPI freshness ≤ 4 hours.
- Alert precision ≥ 80% (manual review).

## Sprint Plan (Indicative)
- **Sprint 1 (2 weeks)**: Pairing logic, canonical_brand map, KPI calc (p50/p90).
- **Sprint 2 (2 weeks)**: Dashboard (brand trends, peer rank), alert MVP.
- **Sprint 3 (2 weeks)**: NLP enrichment (topic/sentiment), topic views.

## Risks & Mitigations
- **R1 Data Ambiguity**: ambiguous threads → flag & exclude from KPI; aim < 5%.
- **R2 Outliers Skew**: winsorize at p99 and monitor tail share.
- **R3 Topic Drift**: retrain NLP quarterly; add human‑in‑the‑loop tags.
- **R4 Platform Changes**: isolate adapters; contract on stable fields.

## Roadmap (Next 3 months)
- v1.0 Benchmark + Alerts → v1.1 Topic Views → v1.2 Staffing Recs (daypart) → v1.3 API Export.
