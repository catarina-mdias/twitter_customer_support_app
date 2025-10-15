"""
Sentiment analysis module for customer support analytics.
Handles sentiment analysis using VADER and TextBlob for customer messages.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import re
import string

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Handles sentiment analysis operations for customer support messages."""
    
    def __init__(self):
        """Initialize the sentiment analyzer with VADER and TextBlob."""
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.sentiment_thresholds = {
            'positive': 0.05,
            'negative': -0.05,
            'neutral_min': -0.05,
            'neutral_max': 0.05
        }
        logger.info("Sentiment analyzer initialized")
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze single text for sentiment using both VADER and TextBlob.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict: Sentiment analysis results
        """
        if not text or pd.isna(text) or text.strip() == '':
            return {
                'vader_score': 0.0,
                'textblob_score': 0.0,
                'combined_score': 0.0,
                'category': 'neutral',
                'confidence': 0.0,
                'vader_compound': 0.0,
                'vader_positive': 0.0,
                'vader_negative': 0.0,
                'vader_neutral': 1.0
            }
        
        try:
            # Clean text before analysis
            cleaned_text = self._clean_text(text)
            
            # VADER analysis
            vader_scores = self.vader_analyzer.polarity_scores(cleaned_text)
            
            # TextBlob analysis
            blob = TextBlob(cleaned_text)
            textblob_score = blob.sentiment.polarity
            
            # Combined score (weighted average)
            combined_score = (vader_scores['compound'] * 0.7) + (textblob_score * 0.3)
            
            # Categorize sentiment
            category = self.categorize_sentiment(combined_score)
            
            # Calculate confidence based on score magnitude
            confidence = min(abs(combined_score) * 2, 1.0)
            
            return {
                'vader_score': vader_scores['compound'],
                'textblob_score': textblob_score,
                'combined_score': combined_score,
                'category': category,
                'confidence': confidence,
                'vader_compound': vader_scores['compound'],
                'vader_positive': vader_scores['pos'],
                'vader_negative': vader_scores['neg'],
                'vader_neutral': vader_scores['neu']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing text: {str(e)}")
            return {
                'vader_score': 0.0,
                'textblob_score': 0.0,
                'combined_score': 0.0,
                'category': 'neutral',
                'confidence': 0.0,
                'vader_compound': 0.0,
                'vader_positive': 0.0,
                'vader_negative': 0.0,
                'vader_neutral': 1.0
            }
    
    def analyze_batch(self, texts: List[str]) -> pd.DataFrame:
        """
        Analyze multiple texts efficiently.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            pd.DataFrame: DataFrame with sentiment analysis results
        """
        logger.info(f"Analyzing {len(texts)} texts for sentiment")
        
        results = []
        for i, text in enumerate(texts):
            if i % 100 == 0:
                logger.info(f"Processed {i}/{len(texts)} texts")
            
            result = self.analyze_text(text)
            results.append(result)
        
        df_results = pd.DataFrame(results)
        logger.info(f"Sentiment analysis completed for {len(texts)} texts")
        
        return df_results
    
    def categorize_sentiment(self, score: float) -> str:
        """
        Categorize sentiment score into positive, negative, or neutral.
        
        Args:
            score: Sentiment score (-1 to 1)
            
        Returns:
            str: Sentiment category
        """
        if score > self.sentiment_thresholds['positive']:
            return 'positive'
        elif score < self.sentiment_thresholds['negative']:
            return 'negative'
        else:
            return 'neutral'
    
    def get_sentiment_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate sentiment statistics from DataFrame.
        
        Args:
            df: DataFrame with sentiment analysis results
            
        Returns:
            Dict: Sentiment metrics
        """
        if df.empty or 'combined_score' not in df.columns:
            return {
                'total_messages': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'positive_percentage': 0.0,
                'negative_percentage': 0.0,
                'neutral_percentage': 0.0,
                'average_score': 0.0,
                'sentiment_distribution': {}
            }
        
        total_messages = len(df)
        positive_count = (df['category'] == 'positive').sum()
        negative_count = (df['category'] == 'negative').sum()
        neutral_count = (df['category'] == 'neutral').sum()
        
        positive_percentage = (positive_count / total_messages) * 100
        negative_percentage = (negative_count / total_messages) * 100
        neutral_percentage = (neutral_count / total_messages) * 100
        
        average_score = df['combined_score'].mean()
        
        sentiment_distribution = {
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count
        }
        
        return {
            'total_messages': total_messages,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_percentage': positive_percentage,
            'negative_percentage': negative_percentage,
            'neutral_percentage': neutral_percentage,
            'average_score': average_score,
            'sentiment_distribution': sentiment_distribution
        }
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and preprocess text for sentiment analysis.
        
        Args:
            text: Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        if not text or pd.isna(text):
            return ""
        
        # Convert to string and lowercase
        text = str(text).lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # Remove phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?]', '', text)
        
        # Remove extra punctuation
        text = re.sub(r'[.]{2,}', '.', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        return text.strip()
    
    def analyze_sentiment_trends(self, df: pd.DataFrame, date_col: str = 'created_at') -> pd.DataFrame:
        """
        Analyze sentiment trends over time.
        
        Args:
            df: DataFrame with sentiment data and date column
            date_col: Name of the date column
            
        Returns:
            pd.DataFrame: Daily sentiment trends
        """
        if df.empty or date_col not in df.columns:
            return pd.DataFrame()
        
        # Ensure date column is datetime
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Group by date and calculate sentiment metrics
        daily_trends = df.groupby(df[date_col].dt.date).agg({
            'combined_score': ['mean', 'count'],
            'category': lambda x: (x == 'positive').sum(),
            'vader_positive': 'mean',
            'vader_negative': 'mean',
            'vader_neutral': 'mean'
        }).round(3)
        
        # Flatten column names
        daily_trends.columns = [
            'avg_sentiment_score', 'message_count', 'positive_count',
            'avg_positive_score', 'avg_negative_score', 'avg_neutral_score'
        ]
        
        # Calculate percentages
        daily_trends['positive_percentage'] = (daily_trends['positive_count'] / daily_trends['message_count'] * 100).round(1)
        
        return daily_trends.reset_index()
    
    def get_sentiment_correlation(self, df: pd.DataFrame) -> Dict:
        """
        Calculate correlation between sentiment and other metrics.
        
        Args:
            df: DataFrame with sentiment and other metrics
            
        Returns:
            Dict: Correlation results
        """
        if df.empty or 'combined_score' not in df.columns:
            return {}
        
        correlations = {}
        
        # Sentiment vs response time correlation
        if 'response_time_minutes' in df.columns:
            corr = df['combined_score'].corr(df['response_time_minutes'])
            correlations['sentiment_vs_response_time'] = corr
        
        # Sentiment vs team correlation (if team is categorical)
        if 'team' in df.columns:
            # Convert team to numeric for correlation
            team_numeric = pd.Categorical(df['team']).codes
            corr = df['combined_score'].corr(team_numeric)
            correlations['sentiment_vs_team'] = corr
        
        return correlations
