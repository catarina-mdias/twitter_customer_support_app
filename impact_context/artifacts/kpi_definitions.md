# KPI Definitions & Measurement Framework
_Generated: 2025-10-17_

> Alignment: Applied directives from `impact_framework.yaml` keys: project, version, framework, globals, required_artifacts, tools, session_documentation, cursor_integration...

## Executive Summary
KPIs focus on **first‑reply latency** robustness: use **percentiles (p50/p90)** over means, by brand and time. Success = **reduced p90**, improved consistency (lower IQR), and faster anomaly detection.

## KPI Hierarchy
**Business (CX Outcomes)**
- **B1: p90 First‑Reply Latency (sec)** — lower is better
- **B2: p50 First‑Reply Latency (sec)**
- **B3: Consistency Index** (IQR / median)

**Product (Adoption & Utility)**
- **P1: Alert Acceptance Rate** (% alerts acknowledged)
- **P2: Action Rate** (% alerts followed by playbook action)
- **P3: Dashboard Active Users / wk**

**Technical (Reliability & Data Quality)**
- **T1: Pair Validity Rate** (% pairs with `pair_status=valid`)
- **T2: KPI Freshness** (age of latest metric)
- **T3: Tail Winsorization Coverage** (% rows capped above p99)

## Baselines (from sample)
- Median (p50) ≈ **1140.5s**
- p90 ≈ **30222.2s**
> Baselines will be recomputed per brand and daypart once the pairing pipeline is finalized.

## Targets (Quarter 1)
- **B1 p90**: −20% vs baseline for pilot brands
- **B2 p50**: −10% vs baseline
- **B3 Consistency**: −15% IQR/median
- **T1 Pair Validity**: ≥ 95%
- **T2 Freshness**: ≤ 4h
- **P1 Acceptance**: ≥ 75%; **P2 Action**: ≥ 40%

## Measurement & Data Collection
- Compute latency from `created_at_tz` parent → first agent reply.
- Bucket by brand/daypart; winsorize above p99.
- Log alerts, acknowledgments, and actions to `alert_events` table.

## Success Criteria & Failure Thresholds
- **Success**: B1/B2 met for ≥ 2 of 3 pilot brands; T1/T2 met consistently 4 weeks.
- **Failure**: p90 increases > +10% over baseline for two consecutive weeks without exogenous event.

## Monitoring & Alerting
- Real‑time checks: DQ‑001..004 (see Data Quality Report).
- KPI monitors: p90 drift > +25% (2‑h window), freshness breach (>4h).

## Reporting Cadence
- **Weekly** ops review: brand trends, incident retros.
- **Monthly** CX review: benchmark pack, peer rank, playbook updates.
