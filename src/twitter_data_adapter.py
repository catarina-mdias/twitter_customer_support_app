"""
Twitter Data Adapter for Customer Support Analytics App
Converts Twitter customer support data to the app's expected format.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwitterDataAdapter:
    """Handles conversion of Twitter customer support data to app format."""
    
    def __init__(self):
        """Initialize the Twitter data adapter."""
        self.twitter_columns = [
            'tweet_id', 'author_id', 'inbound', 'created_at', 'text', 
            'response_tweet_id', 'in_response_to_tweet_id'
        ]
        
        self.app_columns = [
            'ticket_id', 'team', 'created_at', 'responded_at', 
            'customer_message', 'priority', 'category'
        ]
        
        logger.info("Twitter data adapter initialized")
    
    def convert_twitter_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert Twitter dataset to app format.
        
        Args:
            df: DataFrame with Twitter customer support data
            
        Returns:
            pd.DataFrame: Converted data in app format
        """
        try:
            logger.info(f"Converting Twitter data with {len(df)} rows")
            
            # Create conversation pairs
            conversations = self._create_conversation_pairs(df)
            
            # Convert to app format
            app_data = self._convert_to_app_format(conversations)
            
            logger.info(f"Conversion completed. Created {len(app_data)} conversation pairs")
            return app_data
            
        except Exception as e:
            logger.error(f"Error converting Twitter data: {str(e)}")
            raise
    
    def _create_conversation_pairs(self, df: pd.DataFrame) -> List[Dict]:
        """
        Create conversation pairs from Twitter data.
        
        Args:
            df: Twitter DataFrame
            
        Returns:
            List[Dict]: List of conversation pairs
        """
        conversations = []
        
        # Sort by timestamp to process chronologically
        df_sorted = df.sort_values('created_at')
        
        # Group by conversation threads
        conversation_groups = self._group_conversations(df_sorted)
        
        for conv_id, conv_tweets in conversation_groups.items():
            # Separate customer and support messages
            customer_tweets = conv_tweets[conv_tweets['inbound'] == True]
            support_tweets = conv_tweets[conv_tweets['inbound'] == False]
            
            if len(customer_tweets) > 0 and len(support_tweets) > 0:
                # Find the first customer message and first support response
                first_customer = customer_tweets.iloc[0]
                first_support = support_tweets.iloc[0]
                
                # Only include if support response comes after customer message
                if first_support['created_at'] > first_customer['created_at']:
                    conversations.append({
                        'tweet_id': first_customer['tweet_id'],
                        'author_id': first_support['author_id'],
                        'customer_tweet_id': first_customer['tweet_id'],
                        'support_tweet_id': first_support['tweet_id'],
                        'customer_message': first_customer['text'],
                        'support_response': first_support['text'],
                        'customer_created_at': first_customer['created_at'],
                        'support_created_at': first_support['created_at'],
                        'conversation_length': len(conv_tweets)
                    })
        
        return conversations
    
    def _group_conversations(self, df: pd.DataFrame) -> Dict[int, pd.DataFrame]:
        """
        Group tweets into conversation threads.
        
        Args:
            df: Sorted Twitter DataFrame
            
        Returns:
            Dict[int, pd.DataFrame]: Conversation groups
        """
        conversation_groups = {}
        conversation_id = 0
        
        for idx, tweet in df.iterrows():
            # Check if this tweet is part of an existing conversation
            assigned_to_conversation = False
            
            for conv_id, conv_tweets in conversation_groups.items():
                # Check if tweet is responding to any tweet in this conversation
                if (tweet['in_response_to_tweet_id'] in conv_tweets['tweet_id'].values or
                    tweet['response_tweet_id'] in conv_tweets['tweet_id'].values):
                    conversation_groups[conv_id] = pd.concat([conv_tweets, tweet.to_frame().T], ignore_index=True)
                    assigned_to_conversation = True
                    break
            
            if not assigned_to_conversation:
                # Start new conversation
                conversation_groups[conversation_id] = tweet.to_frame().T
                conversation_id += 1
        
        return conversation_groups
    
    def _convert_to_app_format(self, conversations: List[Dict]) -> pd.DataFrame:
        """
        Convert conversation pairs to app format.
        
        Args:
            conversations: List of conversation pairs
            
        Returns:
            pd.DataFrame: Data in app format
        """
        app_data = []
        
        for i, conv in enumerate(conversations):
            # Parse timestamps
            customer_time = self._parse_twitter_timestamp(conv['customer_created_at'])
            support_time = self._parse_twitter_timestamp(conv['support_created_at'])
            
            # Clean customer message
            customer_message = self._clean_twitter_text(conv['customer_message'])
            
            # Determine priority based on conversation characteristics
            priority = self._determine_priority(customer_message, conv['conversation_length'])
            
            # Determine category based on message content
            category = self._determine_category(customer_message)
            
            app_data.append({
                'ticket_id': f"TWITTER_{conv['customer_tweet_id']}",
                'team': conv['author_id'],
                'created_at': customer_time,
                'responded_at': support_time,
                'customer_message': customer_message,
                'priority': priority,
                'category': category,
                'conversation_length': conv['conversation_length'],
                'support_response': conv['support_response']
            })
        
        return pd.DataFrame(app_data)
    
    def _parse_twitter_timestamp(self, timestamp_str: str) -> datetime:
        """
        Parse Twitter timestamp format.
        
        Args:
            timestamp_str: Twitter timestamp string
            
        Returns:
            datetime: Parsed datetime object
        """
        try:
            # Twitter format: "Tue Oct 31 22:10:47 +0000 2017"
            return datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S %z %Y")
        except Exception as e:
            logger.warning(f"Error parsing timestamp '{timestamp_str}': {str(e)}")
            return datetime.now()
    
    def _clean_twitter_text(self, text: str) -> str:
        """
        Clean Twitter text for analysis.
        
        Args:
            text: Raw Twitter text
            
        Returns:
            str: Cleaned text
        """
        if pd.isna(text) or text == '':
            return ''
        
        # Remove @mentions
        text = re.sub(r'@\w+', '', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _determine_priority(self, message: str, conversation_length: int) -> str:
        """
        Determine ticket priority based on message content and conversation length.
        
        Args:
            message: Customer message
            conversation_length: Number of tweets in conversation
            
        Returns:
            str: Priority level
        """
        message_lower = message.lower()
        
        # High priority indicators
        high_priority_words = ['urgent', 'emergency', 'critical', 'asap', 'immediately', 'broken', 'down']
        if any(word in message_lower for word in high_priority_words):
            return 'High'
        
        # Medium priority indicators
        medium_priority_words = ['problem', 'issue', 'help', 'support', 'service']
        if any(word in message_lower for word in medium_priority_words):
            return 'Medium'
        
        # Long conversations might indicate complex issues
        if conversation_length > 5:
            return 'Medium'
        
        return 'Low'
    
    def _determine_category(self, message: str) -> str:
        """
        Determine ticket category based on message content.
        
        Args:
            message: Customer message
            
        Returns:
            str: Category
        """
        message_lower = message.lower()
        
        # Technical issues
        tech_words = ['internet', 'wifi', 'connection', 'service', 'network', 'app', 'website', 'login']
        if any(word in message_lower for word in tech_words):
            return 'Technical'
        
        # Billing issues
        billing_words = ['bill', 'payment', 'charge', 'refund', 'money', 'cost', 'price']
        if any(word in message_lower for word in billing_words):
            return 'Billing'
        
        # Account issues
        account_words = ['account', 'password', 'username', 'profile', 'settings']
        if any(word in message_lower for word in account_words):
            return 'Account'
        
        # General support
        return 'General'
    
    def validate_twitter_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate Twitter dataset structure.
        
        Args:
            df: Twitter DataFrame
            
        Returns:
            Dict[str, Any]: Validation results
        """
        validation_results = {
            'is_valid': True,
            'missing_columns': [],
            'data_quality': {},
            'conversion_ready': True
        }
        
        # Check required columns
        missing_cols = [col for col in self.twitter_columns if col not in df.columns]
        if missing_cols:
            validation_results['missing_columns'] = missing_cols
            validation_results['is_valid'] = False
            validation_results['conversion_ready'] = False
        
        # Data quality checks
        validation_results['data_quality'] = {
            'total_tweets': len(df),
            'customer_tweets': len(df[df['inbound'] == True]) if 'inbound' in df.columns else 0,
            'support_tweets': len(df[df['inbound'] == False]) if 'inbound' in df.columns else 0,
            'unique_authors': df['author_id'].nunique() if 'author_id' in df.columns else 0,
            'date_range': {
                'earliest': df['created_at'].min() if 'created_at' in df.columns else None,
                'latest': df['created_at'].max() if 'created_at' in df.columns else None
            }
        }
        
        return validation_results

def create_sample_twitter_data() -> pd.DataFrame:
    """
    Create a sample dataset in Twitter format for testing.
    
    Returns:
        pd.DataFrame: Sample Twitter data
    """
    sample_data = [
        {
            'tweet_id': 1,
            'author_id': 'sprintcare',
            'inbound': False,
            'created_at': 'Tue Oct 31 22:10:47 +0000 2017',
            'text': '@115712 I understand. I would like to assist you. We would need to get you into a private secured link to further assist.',
            'response_tweet_id': 2,
            'in_response_to_tweet_id': 3.0
        },
        {
            'tweet_id': 2,
            'author_id': '115712',
            'inbound': True,
            'created_at': 'Tue Oct 31 22:11:45 +0000 2017',
            'text': '@sprintcare and how do you propose we do that',
            'response_tweet_id': '',
            'in_response_to_tweet_id': 1.0
        },
        {
            'tweet_id': 3,
            'author_id': '115712',
            'inbound': True,
            'created_at': 'Tue Oct 31 22:08:27 +0000 2017',
            'text': '@sprintcare I have sent several private messages and no one is responding as usual',
            'response_tweet_id': 1,
            'in_response_to_tweet_id': 4.0
        }
    ]
    
    return pd.DataFrame(sample_data)
