# Customer Support Analytics App

A streamlined analytics dashboard for evaluating **customer support performance**, **sentiment trends**, and **team efficiency** — with integrated **AI-powered RAG insights**.

---

## 🚀 Key Features

### 📊 Core Analytics
- Response Time Metrics (Median, P90, SLA compliance)
- Team Performance Comparison
- Trend and Distribution Analysis
- Automatic Data Cleaning and Validation

### 😊 Sentiment Insights
- Sentiment Scoring (VADER/TextBlob)
- Trend Correlation with Response Metrics
- Team Sentiment Comparison
- Message Statistics (word count, readability)

### 👥 Team Analytics
- Performance Rankings and Scores
- Team Comparisons
- Automated Recommendations

### 🔮 Advanced Analytics
- Predictive Forecasting and Anomaly Detection
- Comprehensive Reporting (PDF, Excel, CSV, HTML)

### 🏠 Modern UI
- Streamlit-based tabbed dashboard
- Responsive layout with fast loading
- Clean and intuitive navigation

---

## ⚙️ Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Steps
```bash
# 1. Clone repository
git clone https://github.com/your-username/customer_support_app.git
cd customer_support_app

# 2. Install dependencies
pip install -r src/requirements.txt

# 3. (Optional) Additional dependencies
pip install psycopg2-binary pymysql redis websockets aiohttp boto3 google-cloud-storage azure-storage-blob
```

### Run the App
```bash
streamlit run src/app.py
```
Then open [http://localhost:8501](http://localhost:8501)

---

## 📁 Data Sources

### 📄 CSV Upload (✅ Currently Active)
Upload customer support data in CSV format with the following columns:

**Required:**
- `ticket_id`: Unique ticket identifier
- `created_at`: Ticket creation datetime
- `responded_at`: Response datetime

**Optional:**
- `team`, `customer_message`, `priority`, `category`

---

## 🤖 RAG-Powered Insights

Ask natural-language questions about your data with **Retrieval Augmented Generation (RAG)**.

### Setup
```bash
pip install langchain langchain-openai langchain-community chromadb openai tiktoken
export OPENAI_API_KEY=your-api-key
```
Activate via **Advanced Analytics → RAG Insights** in the app.

Example queries:
- “Why was sentiment negative last week?”
- “What topics are customers most concerned about?”

---

## 🎯 Key Achievements

- **Production-Ready:** End-to-end Streamlit app with modular design
- **Comprehensive Analytics:** Covers 6 development phases (analytics, sentiment, teams, AI)
- **Modern UI:** Clean, responsive, and performance-optimized
- **Multi-Source Ready:** CSV, Twitter, API, Database, Cloud
- **AI Integration:** GPT‑4‑mini powered insights via LangChain and Chroma
- **Reporting:** Multi-format exports and executive summaries

---

**License:** MIT License  
**Version:** Short README v1.0
