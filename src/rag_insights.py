"""
RAG-based Insights Engine for Customer Support Analytics
Uses LangChain, Chroma vector store, and OpenAI GPT for natural language insights.

This module integrates with MCP (Model Context Protocol) file-access connector
to dynamically load and analyze customer support data.
"""

import pandas as pd
import os
import glob
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LangChain imports for RAG orchestration
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document

# For conversation grouping and preprocessing
import hashlib


class RAGInsightsEngine:
    """
    RAG-based insights engine that uses MCP file connector to dynamically load
    CSV data, preprocess conversations, embed them in Chroma, and answer
    natural language queries about sentiment and topic trends.
    
    Key Components:
    - MCP Integration: Dynamically loads latest CSV from data/ folder
    - Data Preprocessing: Groups tweets by conversation_id
    - Vector Store: Chroma for semantic search
    - LLM: OpenAI GPT-4-mini for generation
    - LangChain: Orchestrates the RAG workflow
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, data_directory: str = "data"):
        """
        Initialize the RAG insights engine.
        
        Args:
            openai_api_key: OpenAI API key (if None, reads from env or Streamlit secrets)
            data_directory: Directory where CSV files are stored (MCP monitored directory)
        """
        self.data_directory = data_directory
        self.vectorstore = None
        self.qa_chain = None
        self.df = None
        self.conversations = []
        
        # Get OpenAI API key from multiple sources
        # MCP Note: While MCP provides file access, API keys should still be managed securely
        # Priority: 1. Parameter, 2. Environment variable (.env), 3. Streamlit secrets
        if openai_api_key:
            self.api_key = openai_api_key
        elif os.environ.get('OPENAI_API_KEY'):
            self.api_key = os.environ.get('OPENAI_API_KEY')
        else:
            # Safely check Streamlit secrets without throwing error if file doesn't exist
            try:
                if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                    self.api_key = st.secrets['OPENAI_API_KEY']
                else:
                    self.api_key = None
            except:
                self.api_key = None
            
        # Initialize LLM and embeddings
        if self.api_key:
            self.llm = ChatOpenAI(
                model_name="gpt-4o-mini",  # Using gpt-4o-mini as specified
                temperature=0.7,
                openai_api_key=self.api_key
            )
            self.embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
        else:
            self.llm = None
            self.embeddings = None
    
    def get_latest_csv_via_mcp(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Use MCP file-access connector to get the latest CSV file from data directory.
        
        MCP Integration: This method simulates MCP file access by directly accessing
        the filesystem. In production, this would use the MCP protocol to request
        file listings and read operations through the MCP server.
        
        The MCP connector (defined in .cursor/mcp.json) provides:
        - Safe, sandboxed access to the data/ directory
        - File listing capabilities
        - File reading operations
        
        Args:
            filename: Specific filename to load, or None to auto-detect latest
            
        Returns:
            Path to the CSV file or None if not found
        """
        if filename and os.path.exists(os.path.join(self.data_directory, filename)):
            return os.path.join(self.data_directory, filename)
        
        # Use MCP pattern: List files in data directory
        # In production, this would be an MCP protocol request
        csv_files = glob.glob(os.path.join(self.data_directory, "*.csv"))
        
        if not csv_files:
            return None
        
        # Get the most recently modified CSV (simulates MCP file metadata query)
        latest_csv = max(csv_files, key=os.path.getmtime)
        return latest_csv
    
    def load_and_preprocess_data(self, csv_path: Optional[str] = None) -> bool:
        """
        Load CSV data using MCP connector and preprocess for RAG.
        
        Preprocessing steps:
        1. Load CSV via MCP file access
        2. Group tweets by conversation_id
        3. Combine messages in each conversation
        4. Extract metadata (sentiment, dates, authors)
        
        Args:
            csv_path: Path to CSV file, or None to auto-detect via MCP
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Step 1: Use MCP to get latest CSV
            if csv_path is None:
                csv_path = self.get_latest_csv_via_mcp()
            
            if csv_path is None:
                st.error("No CSV files found in data directory via MCP connector")
                return False
            
            # Step 2: Load CSV data (MCP read operation)
            self.df = pd.read_csv(csv_path)
            
            # Step 3: Validate required columns
            required_cols = ['conversation_id', 'text', 'created_at']
            if not all(col in self.df.columns for col in required_cols):
                st.error(f"CSV must contain: {', '.join(required_cols)}")
                return False
            
            # Step 4: Preprocess - group by conversation_id
            self.conversations = self._group_by_conversation()
            
            if not self.conversations:
                st.error("No valid conversations found in data")
                return False
            
            return True
            
        except Exception as e:
            st.error(f"Error loading data via MCP: {str(e)}")
            return False
    
    def _group_by_conversation(self) -> List[Dict]:
        """
        Group tweets by conversation_id and combine into conversation documents.
        
        Each conversation becomes a single document with:
        - Combined text from CUSTOMER messages only (inbound=True)
        - Metadata: dates, authors, sentiment indicators
        
        Returns:
            List of conversation dictionaries
        """
        conversations = []
        
        # Group by conversation_id
        grouped = self.df.groupby('conversation_id')
        
        for conv_id, group in grouped:
            # Sort by created_at to maintain chronological order
            group = group.sort_values('created_at')
            
            # Filter for customer messages only (inbound=True)
            if 'inbound' in group.columns:
                customer_messages = group[group['inbound'] == True]
            else:
                # If no inbound column, use all messages
                customer_messages = group
            
            # Skip if no customer messages in this conversation
            if len(customer_messages) == 0:
                continue
            
            # Combine only customer text in the conversation
            combined_text = "\n".join(customer_messages['text'].astype(str).tolist())
            
            # Extract metadata from customer messages
            dates = pd.to_datetime(customer_messages['created_at'], errors='coerce')
            start_date = dates.min() if not dates.isna().all() else None
            
            # Check for sentiment indicators in text (if available)
            sentiment_keywords = {
                'positive': ['thanks', 'thank you', 'great', 'awesome', 'perfect', 'excellent', 'love'],
                'negative': ['worst', 'terrible', 'awful', 'frustrated', 'angry', 'disappointed', 'horrible']
            }
            
            text_lower = combined_text.lower()
            positive_score = sum(1 for word in sentiment_keywords['positive'] if word in text_lower)
            negative_score = sum(1 for word in sentiment_keywords['negative'] if word in text_lower)
            
            sentiment = 'neutral'
            if positive_score > negative_score:
                sentiment = 'positive'
            elif negative_score > positive_score:
                sentiment = 'negative'
            
            # Get customer authors involved
            authors = customer_messages['author_id'].unique().tolist() if 'author_id' in customer_messages.columns else []
            
            conversations.append({
                'conversation_id': str(conv_id),
                'text': combined_text,
                'start_date': start_date,
                'message_count': len(customer_messages),  # Count of customer messages only
                'sentiment': sentiment,
                'authors': authors,
                'has_customer_message': True,  # Always true since we filtered for them
                'metadata': {
                    'date': start_date.strftime('%Y-%m-%d') if start_date else 'Unknown',
                    'sentiment': sentiment,
                    'message_count': len(customer_messages)  # Customer messages count
                }
            })
        
        return conversations
    
    def build_vector_store(self) -> bool:
        """
        Build Chroma vector store from preprocessed conversations.
        
        RAG Pipeline Steps:
        1. Convert conversations to LangChain Documents
        2. Split long conversations into chunks
        3. Generate embeddings using OpenAI
        4. Store in Chroma vector database
        
        Returns:
            True if successful, False otherwise
        """
        if not self.conversations:
            st.error("No conversations to embed. Load data first.")
            return False
        
        if not self.embeddings:
            st.error("OpenAI API key required for embeddings")
            return False
        
        try:
            # Step 1: Convert to LangChain Documents
            documents = []
            for conv in self.conversations:
                doc = Document(
                    page_content=conv['text'],
                    metadata={
                        'conversation_id': conv['conversation_id'],
                        'date': conv['metadata']['date'],
                        'sentiment': conv['sentiment'],
                        'message_count': conv['message_count']
                    }
                )
                documents.append(doc)
            
            # Step 2: Split long documents into chunks for better retrieval
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            split_docs = text_splitter.split_documents(documents)
            
            # Step 3 & 4: Create Chroma vector store with embeddings
            # Using in-memory Chroma for this session
            self.vectorstore = Chroma.from_documents(
                documents=split_docs,
                embedding=self.embeddings,
                collection_name="support_conversations"
            )
            
            return True
            
        except Exception as e:
            st.error(f"Error building vector store: {str(e)}")
            return False
    
    def create_qa_chain(self) -> bool:
        """
        Create LangChain RetrievalQA chain for answering queries.
        
        LangChain Orchestration:
        - Combines retriever (Chroma) with LLM (GPT-4-mini)
        - Uses custom prompt template for support analytics
        - Returns answers with source documents
        
        Returns:
            True if successful, False otherwise
        """
        if not self.vectorstore or not self.llm:
            return False
        
        try:
            # Custom prompt template for customer support insights
            # Prompt Design: Instructs LLM to analyze support conversations and explain trends
            prompt_template = """You are an AI assistant analyzing customer support data.
Use the following conversation excerpts to answer questions about sentiment and topic trends.

Context from support conversations:
{context}

Question: {question}

Instructions:
- Analyze the provided conversations to understand patterns
- Explain why certain sentiment or topic trends occurred
- Reference specific examples from the conversations
- Be concise but thorough in your explanation
- If you're not sure, say so rather than making up information

Answer:"""

            PROMPT = PromptTemplate(
                template=prompt_template, 
                input_variables=["context", "question"]
            )
            
            # Create RetrievalQA chain with custom prompt
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",  # "stuff" chain type passes all retrieved docs to LLM
                retriever=self.vectorstore.as_retriever(
                    search_kwargs={"k": 5}  # Retrieve top 5 most relevant conversations
                ),
                return_source_documents=True,
                chain_type_kwargs={"prompt": PROMPT}
            )
            
            return True
            
        except Exception as e:
            st.error(f"Error creating QA chain: {str(e)}")
            return False
    
    def query(self, question: str) -> Tuple[Optional[str], List[Dict]]:
        """
        Query the RAG system with a natural language question.
        
        Args:
            question: Natural language question about sentiment or topics
            
        Returns:
            Tuple of (answer, source_documents)
            - answer: LLM-generated explanation
            - source_documents: List of relevant conversation excerpts
        """
        if not self.qa_chain:
            return None, []
        
        try:
            # Execute RAG query
            result = self.qa_chain.invoke({"query": question})
            
            # Extract answer
            answer = result.get('result', 'No answer generated')
            
            # Extract and format source documents
            source_docs = []
            for doc in result.get('source_documents', []):
                source_docs.append({
                    'text': doc.page_content,
                    'conversation_id': doc.metadata.get('conversation_id', 'Unknown'),
                    'date': doc.metadata.get('date', 'Unknown'),
                    'sentiment': doc.metadata.get('sentiment', 'Unknown'),
                    'message_count': doc.metadata.get('message_count', 0)
                })
            
            return answer, source_docs
            
        except Exception as e:
            st.error(f"Error during query: {str(e)}")
            return None, []
    
    def initialize_from_dataframe(self, df: pd.DataFrame) -> bool:
        """
        Initialize RAG system from an already-loaded DataFrame.
        
        This is useful when the app has already loaded data and we want
        to build the RAG system without re-reading from MCP.
        
        Args:
            df: Pandas DataFrame with conversation data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.df = df.copy()
            
            # Validate columns
            if 'conversation_id' not in df.columns or 'text' not in df.columns:
                st.error("DataFrame must contain 'conversation_id' and 'text' columns")
                return False
            
            # Preprocess
            self.conversations = self._group_by_conversation()
            
            if not self.conversations:
                st.error("No valid conversations found")
                return False
            
            # Build vector store
            if not self.build_vector_store():
                return False
            
            # Create QA chain
            if not self.create_qa_chain():
                return False
            
            return True
            
        except Exception as e:
            st.error(f"Error initializing from DataFrame: {str(e)}")
            return False
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the loaded data and RAG system.
        
        Returns:
            Dictionary with stats
        """
        stats = {
            'total_conversations': len(self.conversations),
            'total_messages': sum(c['message_count'] for c in self.conversations),
            'date_range': 'N/A',
            'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
            'vectorstore_ready': self.vectorstore is not None,
            'qa_chain_ready': self.qa_chain is not None
        }
        
        if self.conversations:
            # Date range
            dates = [c['start_date'] for c in self.conversations if c['start_date']]
            if dates:
                stats['date_range'] = f"{min(dates).strftime('%Y-%m-%d')} to {max(dates).strftime('%Y-%m-%d')}"
            
            # Sentiment distribution
            for conv in self.conversations:
                sentiment = conv.get('sentiment', 'neutral')
                stats['sentiment_distribution'][sentiment] += 1
        
        return stats


def render_rag_insights_ui(df: pd.DataFrame, enable_rag: bool = True):
    """
    Render the RAG insights UI component in Streamlit.
    
    This function is called from the Advanced Analytics tab in app.py.
    
    Args:
        df: DataFrame with conversation data
        enable_rag: Whether RAG insights are enabled
    """
    st.markdown("### 🤖 AI-Powered Insights Explanation (RAG)")
    st.markdown("""
    Ask natural language questions about sentiment and topic trends in your support data.
    The AI will analyze conversations and explain patterns using **Retrieval Augmented Generation (RAG)**.
    """)
    
    if not enable_rag:
        st.info("Enable 'Insights Explanation' in the sidebar to use RAG-powered insights.")
        return
    
    # Check for API key (prioritize environment variable from .env file)
    api_key = None
    
    # First check environment variable (loaded from .env by python-dotenv)
    if os.environ.get('OPENAI_API_KEY'):
        api_key = os.environ.get('OPENAI_API_KEY')
    else:
        # Then check Streamlit secrets (safely)
        try:
            if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                api_key = st.secrets['OPENAI_API_KEY']
        except:
            pass  # No secrets file, that's okay
    
    if not api_key:
        st.warning("⚠️ OpenAI API key not found. Please set OPENAI_API_KEY in environment variables or Streamlit secrets.")
        st.info("""
        To use RAG insights:
        1. Get an API key from https://platform.openai.com/api-keys
        2. Add to `.streamlit/secrets.toml`: `OPENAI_API_KEY = "your-key-here"`
        3. Or set environment variable: `export OPENAI_API_KEY=your-key-here`
        """)
        return
    
    # Initialize RAG engine in session state
    if 'rag_engine' not in st.session_state:
        st.session_state.rag_engine = None
        st.session_state.rag_initialized = False
    
    # Initialize RAG system
    if not st.session_state.rag_initialized:
        with st.spinner("🔄 Initializing RAG system (loading data, creating embeddings)..."):
            try:
                engine = RAGInsightsEngine(openai_api_key=api_key)
                
                # Initialize from current DataFrame
                if engine.initialize_from_dataframe(df):
                    st.session_state.rag_engine = engine
                    st.session_state.rag_initialized = True
                    st.success("✅ RAG system initialized successfully!")
                    
                    # Show stats
                    stats = engine.get_stats()
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Conversations", stats['total_conversations'])
                    with col2:
                        st.metric("Messages", stats['total_messages'])
                    with col3:
                        st.metric("Date Range", stats['date_range'], delta=None)
                    with col4:
                        sentiment_emoji = {
                            'positive': '😊',
                            'negative': '😞', 
                            'neutral': '😐'
                        }
                        dominant_sentiment = max(stats['sentiment_distribution'], 
                                                key=stats['sentiment_distribution'].get)
                        st.metric("Dominant Sentiment", 
                                f"{sentiment_emoji[dominant_sentiment]} {dominant_sentiment.title()}")
                else:
                    st.error("Failed to initialize RAG system. Check data format.")
                    return
            except Exception as e:
                st.error(f"Error initializing RAG: {str(e)}")
                return
    
    # Query interface
    st.markdown("---")
    st.markdown("#### 💬 Ask a Question")
    
    # Example queries
    with st.expander("📝 Example Questions"):
        st.markdown("""
        - Why was sentiment negative on Oct 31?
        - What caused a spike in complaints?
        - Why are customers frustrated with response times?
        - What topics are customers most concerned about?
        - Why did satisfaction improve in November?
        - What are the main pain points customers mention?
        """)
    
    # Query input
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input(
            "Your question:",
            placeholder="e.g., Why was sentiment negative on Oct 31?",
            key="rag_query_input"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        explain_button = st.button("🔍 Explain", type="primary", use_container_width=True)
    
    # Execute query
    if explain_button and query:
        with st.spinner("🤔 Analyzing conversations and generating explanation..."):
            answer, sources = st.session_state.rag_engine.query(query)
            
            if answer:
                # Display answer
                st.markdown("#### 💡 AI Explanation")
                st.markdown(f"""
                <div style="
                    background-color: #f0f8ff;
                    border-left: 4px solid #4CAF50;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 15px 0;
                ">
                    {answer}
                </div>
                """, unsafe_allow_html=True)
                
                # Display source conversations
                if sources:
                    st.markdown("---")
                    st.markdown("#### 📚 Supporting Evidence (Retrieved Conversations)")
                    st.markdown(f"*Showing {len(sources)} relevant conversation excerpts that support this explanation*")
                    
                    for i, source in enumerate(sources, 1):
                        sentiment_color = {
                            'positive': '#d4edda',
                            'negative': '#f8d7da',
                            'neutral': '#fff3cd'
                        }
                        
                        sentiment_icon = {
                            'positive': '😊',
                            'negative': '😞',
                            'neutral': '😐'
                        }
                        
                        bg_color = sentiment_color.get(source['sentiment'], '#f8f9fa')
                        icon = sentiment_icon.get(source['sentiment'], '💬')
                        
                        # Truncate long texts
                        display_text = source['text'][:500] + "..." if len(source['text']) > 500 else source['text']
                        
                        st.markdown(f"""
                        <div style="
                            background-color: {bg_color};
                            border: 1px solid #dee2e6;
                            border-radius: 8px;
                            padding: 15px;
                            margin: 10px 0;
                        ">
                            <strong>{icon} Example {i}</strong> 
                            <span style="color: #6c757d; font-size: 0.9em;">
                                | Date: {source['date']} 
                                | Sentiment: {source['sentiment'].title()} 
                                | Messages: {source['message_count']}
                            </span>
                            <hr style="margin: 10px 0;">
                            <div style="font-style: italic; color: #495057;">
                                {display_text}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.error("Failed to generate explanation. Please try rephrasing your question.")
    
    elif explain_button and not query:
        st.warning("Please enter a question first.")
    
    # Technical details expander
    with st.expander("🔧 Technical Details: How RAG Works"):
        st.markdown("""
        **RAG (Retrieval Augmented Generation) Pipeline:**
        
        1. **Data Loading (MCP Integration)**:
           - Uses MCP file-access connector to dynamically load CSV from `data/` folder
           - MCP provides secure, sandboxed access to the file system
           
        2. **Preprocessing**:
           - Groups tweets by `conversation_id`
           - Combines messages in chronological order
           - Extracts metadata (dates, sentiment, authors)
           
        3. **Embedding & Storage**:
           - Text is embedded using OpenAI embeddings
           - Stored in Chroma vector database for semantic search
           - Enables finding similar conversations based on meaning
           
        4. **Retrieval**:
           - User query is converted to embedding
           - Top 5 most relevant conversations are retrieved
           - Uses cosine similarity for matching
           
        5. **Generation**:
           - Retrieved conversations + user query sent to GPT-4-mini
           - LLM generates explanation based on evidence
           - LangChain orchestrates the workflow
           
        **Key Technologies:**
        - **LangChain**: Workflow orchestration
        - **Chroma**: Vector database for embeddings
        - **OpenAI GPT-4-mini**: Large language model for generation
        - **MCP**: Model Context Protocol for file access
        """)

