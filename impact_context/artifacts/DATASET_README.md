# Data Source Setup

The framework attempted to initialize DuckDB using:
`/home/sandbox/data/customer_support_on_twitter/Tweets.csv`

The file was not found. Please download the Kaggle dataset and place the CSV here:

```
pip install kagglehub
python -c "import kagglehub, pathlib; p=kagglehub.dataset_download('thoughtvector/customer-support-on-twitter'); print(p)"
```
Then copy the relevant CSV (Tweets.csv) to:
`/home/sandbox/data/customer_support_on_twitter/Tweets.csv`

After copying, re-run the framework to execute the pending DDL:
```
streamlit run /home/sandbox/impact_context/artifacts/interactive_dashboard.py
```
Or re-trigger the SQL runner step.