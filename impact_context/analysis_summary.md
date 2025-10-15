# IMPACT Analysis Summary
Generated: 2025-09-26T15:02:34.416797Z
Dataset: twcs.csv (sample 250,000)

Artifacts created under: /mnt/data/impact_context/artifacts

Steps:
- I_inspect → data_quality_report.md, inspect_profile.csv
- M_map → correlation_analysis.md, data_dictionary.csv, charts/correlation_matrix.png
- P_position → market_analysis.md + position charts
- A_act → scenarios_prioritized.md + scenarios_prioritized_table.csv
- C_calibrate → kpi_definitions.md
- T_telemetry → interactive_dashboard.py

How to run the dashboard:
```
pip install streamlit pandas
streamlit run interactive_dashboard.py
```
