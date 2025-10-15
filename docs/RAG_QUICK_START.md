# RAG Insights - Quick Start Guide

Get started with AI-powered insights in under 5 minutes!

## 🚀 Quick Setup

### Step 1: Install Dependencies

```bash
pip install langchain langchain-openai langchain-community chromadb openai tiktoken
```

### Step 2: Get OpenAI API Key

1. Visit [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign up or log in
3. Click "Create new secret key"
4. Copy your API key

### Step 3: Configure API Key

**Option A: Environment Variable (Recommended for local dev)**
```bash
export OPENAI_API_KEY=your-key-here
```

**Option B: Streamlit Secrets (Recommended for deployment)**
```bash
# Create .streamlit/secrets.toml
echo 'OPENAI_API_KEY = "your-key-here"' > .streamlit/secrets.toml
```

### Step 4: Run the App

```bash
streamlit run src/app.py
```

## 📖 How to Use

### 1. Load Twitter Data

- Click "📁 Upload CSV" in the sidebar
- Select `data/tweets_100.csv` or your own Twitter data
- Wait for data to load

### 2. Enable RAG Insights

- In the sidebar, scroll to "🤖 AI-Powered Insights"
- Check the box: "Insights Explanation (RAG)"
- Go to the "🔮 Advanced Analytics" tab

### 3. Wait for Initialization

- The system will:
  - Load conversations from your data
  - Create embeddings (takes ~15-30 seconds)
  - Build the vector store
- You'll see stats when ready:
  - Total conversations
  - Total messages
  - Date range
  - Dominant sentiment

### 4. Ask Questions

Try these example questions:

```
Why was sentiment negative on Oct 31?
What caused a spike in complaints?
Why are customers frustrated with response times?
What topics are customers most concerned about?
What are the main pain points?
```

### 5. Review Results

You'll see:
- **AI Explanation**: A comprehensive answer to your question
- **Supporting Evidence**: 3-5 actual conversation excerpts that justify the answer
- **Metadata**: Date, sentiment, and message count for each conversation

## 💡 Tips for Best Results

### Write Good Questions

✅ **Good**:
- "Why was sentiment negative on Oct 31?"
- "What caused response times to increase in November?"
- "What are customers complaining about most?"

❌ **Avoid**:
- Single words: "Complaints"
- Too vague: "Tell me something"
- Multiple questions: "What happened and why and how to fix it?"

### Data Requirements

Your CSV must have:
- `conversation_id`: Groups related messages
- `text`: The message content
- `created_at`: Timestamp (recommended)
- `author_id`: Author identifier (optional)

## 🔧 Troubleshooting

### "No API key found"

**Solution**: Make sure you've set `OPENAI_API_KEY` as environment variable or in `.streamlit/secrets.toml`

### "No conversations found"

**Cause**: Data doesn't have required columns or conversation_ids are missing

**Solution**: Ensure your CSV has `conversation_id` and `text` columns with valid data

### "Vector store build failed"

**Causes**:
- Invalid API key
- Network issues
- Out of memory

**Solutions**:
- Verify API key at [platform.openai.com](https://platform.openai.com)
- Check internet connection
- Try smaller dataset

### Slow initialization

**Normal**: First-time setup takes 15-30 seconds for 100 conversations

**If very slow** (>1 minute):
- Check internet speed
- Reduce dataset size
- Verify API key limits

## 💰 Cost Estimate

For typical usage (100 conversations, 20 queries/day):

- **Embeddings**: ~$0.10 per session (one-time)
- **Queries**: ~$0.002 per query
- **Daily**: ~$0.05
- **Monthly**: ~$2-3

Very affordable for most use cases!

## 📊 What to Expect

### First Query

- Takes 5-8 seconds
- Includes retrieval + generation time
- Shows 3-5 relevant conversations

### Answer Quality

- Evidence-based (not made up)
- References specific conversations
- Explains patterns and trends
- Admits uncertainty when appropriate

### Limitations

- Only analyzes uploaded data
- Limited to conversation text
- May miss very subtle patterns
- Depends on data quality

## 🎯 Example Workflow

1. **Morning**: Upload yesterday's support data
2. **Wait 30 seconds**: RAG system initializes
3. **Ask**: "What issues are customers reporting most?"
4. **Review**: AI answer + evidence
5. **Ask**: "Why are customers frustrated?"
6. **Review**: Specific pain points identified
7. **Act**: Use insights to improve support

## 🔗 Additional Resources

- **Complete Technical Guide**: See `RAG_INSIGHTS_GUIDE.md`
- **Implementation Details**: See `RAG_IMPLEMENTATION_SUMMARY.md`
- **General User Guide**: See `README.md`

## ❓ FAQ

**Q: How much does it cost?**  
A: ~$2-3/month for typical usage (100 queries)

**Q: Can I use my own data?**  
A: Yes! Just ensure it has `conversation_id` and `text` columns

**Q: Is my data private?**  
A: Data is sent to OpenAI for embedding/generation. Check their privacy policy.

**Q: Can I use a different LLM?**  
A: Currently GPT-4-mini only. Local LLM support planned for future.

**Q: How accurate are the answers?**  
A: Very high when evidence exists in data. Always shows sources.

**Q: Can I export the insights?**  
A: Currently view-only. Export feature planned for future.

## 🆘 Need Help?

1. Check the troubleshooting section above
2. Review `RAG_INSIGHTS_GUIDE.md` for technical details
3. Ensure all dependencies are installed
4. Verify your data format matches requirements

## 🎉 You're Ready!

That's it! Start asking questions and discovering insights in your support data.

**Happy analyzing!** 🚀

---

**Last Updated**: October 12, 2025  
**Version**: 1.0  
**Feature Status**: Production Ready

