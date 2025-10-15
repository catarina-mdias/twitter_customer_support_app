"""
Twitter API Integration Module
Handles connection to Twitter API and data fetching for customer support analysis.
"""

import tweepy
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import time

logger = logging.getLogger(__name__)

class TwitterAPIConnector:
    """Handles Twitter API connection and data fetching."""
    
    def __init__(self):
        """Initialize Twitter API connector."""
        self.api = None
        self.client = None
        self.is_connected = False
        
    def connect(self, bearer_token: str) -> Dict[str, any]:
        """
        Connect to Twitter API using Bearer Token.
        
        Args:
            bearer_token: Twitter API Bearer Token
            
        Returns:
            Dict with connection status and message
        """
        try:
            if not bearer_token or bearer_token.strip() == "":
                return {
                    'success': False,
                    'message': 'Bearer token is required',
                    'error': 'Missing credentials'
                }
            
            # Initialize Twitter API v2 client
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                wait_on_rate_limit=True
            )
            
            # Test connection by getting user info
            try:
                # Try to get a public user to test connection
                user = self.client.get_user(username='twitter')
                if user.data:
                    self.is_connected = True
                    return {
                        'success': True,
                        'message': 'Successfully connected to Twitter API',
                        'user_info': user.data
                    }
            except Exception as e:
                logger.error(f"Twitter API connection test failed: {str(e)}")
                return {
                    'success': False,
                    'message': f'Failed to connect to Twitter API: {str(e)}',
                    'error': str(e)
                }
                
        except Exception as e:
            logger.error(f"Twitter API connection error: {str(e)}")
            return {
                'success': False,
                'message': f'Connection error: {str(e)}',
                'error': str(e)
            }
    
    def fetch_account_tweets(self, username: str, days_back: int = 30, max_tweets: int = 100) -> Dict[str, any]:
        """
        Fetch tweets from a specific Twitter account.
        
        Args:
            username: Twitter username (without @)
            days_back: Number of days to look back
            max_tweets: Maximum number of tweets to fetch
            
        Returns:
            Dict with tweets data and metadata
        """
        if not self.is_connected:
            return {
                'success': False,
                'message': 'Not connected to Twitter API',
                'error': 'No connection'
            }
        
        try:
            # Get user ID
            user = self.client.get_user(username=username)
            if not user.data:
                return {
                    'success': False,
                    'message': f'User @{username} not found',
                    'error': 'User not found'
                }
            
            user_id = user.data.id
            
            # Calculate start time
            start_time = datetime.utcnow() - timedelta(days=days_back)
            
            # Fetch tweets
            tweets = []
            tweet_count = 0
            
            try:
                # Get user's tweets
                for tweet in tweepy.Paginator(
                    self.client.get_users_tweets,
                    id=user_id,
                    max_results=min(100, max_tweets),
                    start_time=start_time,
                    tweet_fields=['created_at', 'public_metrics', 'context_annotations', 'lang']
                ).flatten(limit=max_tweets):
                    
                    tweets.append({
                        'tweet_id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'retweet_count': tweet.public_metrics['retweet_count'],
                        'like_count': tweet.public_metrics['like_count'],
                        'reply_count': tweet.public_metrics['reply_count'],
                        'quote_count': tweet.public_metrics['quote_count'],
                        'lang': tweet.lang
                    })
                    tweet_count += 1
                    
                    # Add small delay to respect rate limits
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error fetching tweets: {str(e)}")
                return {
                    'success': False,
                    'message': f'Error fetching tweets: {str(e)}',
                    'error': str(e)
                }
            
            if not tweets:
                return {
                    'success': False,
                    'message': f'No tweets found for @{username} in the last {days_back} days',
                    'error': 'No tweets found'
                }
            
            # Convert to DataFrame
            df = pd.DataFrame(tweets)
            
            # Convert to app format
            df_converted = self._convert_to_app_format(df, username)
            
            return {
                'success': True,
                'message': f'Successfully fetched {len(tweets)} tweets from @{username}',
                'data': df_converted,
                'raw_data': df,
                'user_info': user.data,
                'tweet_count': len(tweets)
            }
            
        except Exception as e:
            logger.error(f"Error fetching account tweets: {str(e)}")
            return {
                'success': False,
                'message': f'Error fetching tweets: {str(e)}',
                'error': str(e)
            }
    
    def search_tweets(self, query: str, days_back: int = 7, max_tweets: int = 100) -> Dict[str, any]:
        """
        Search for tweets using a query.
        
        Args:
            query: Search query
            days_back: Number of days to look back
            max_tweets: Maximum number of tweets to fetch
            
        Returns:
            Dict with tweets data and metadata
        """
        if not self.is_connected:
            return {
                'success': False,
                'message': 'Not connected to Twitter API',
                'error': 'No connection'
            }
        
        try:
            # Calculate start time
            start_time = datetime.utcnow() - timedelta(days=days_back)
            
            # Search tweets
            tweets = []
            tweet_count = 0
            
            try:
                for tweet in tweepy.Paginator(
                    self.client.search_recent_tweets,
                    query=query,
                    max_results=min(100, max_tweets),
                    start_time=start_time,
                    tweet_fields=['created_at', 'public_metrics', 'author_id', 'lang']
                ).flatten(limit=max_tweets):
                    
                    tweets.append({
                        'tweet_id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'author_id': tweet.author_id,
                        'retweet_count': tweet.public_metrics['retweet_count'],
                        'like_count': tweet.public_metrics['like_count'],
                        'reply_count': tweet.public_metrics['reply_count'],
                        'quote_count': tweet.public_metrics['quote_count'],
                        'lang': tweet.lang
                    })
                    tweet_count += 1
                    
                    # Add small delay to respect rate limits
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error searching tweets: {str(e)}")
                return {
                    'success': False,
                    'message': f'Error searching tweets: {str(e)}',
                    'error': str(e)
                }
            
            if not tweets:
                return {
                    'success': False,
                    'message': f'No tweets found for query "{query}" in the last {days_back} days',
                    'error': 'No tweets found'
                }
            
            # Convert to DataFrame
            df = pd.DataFrame(tweets)
            
            # Convert to app format
            df_converted = self._convert_to_app_format(df, "Search Results")
            
            return {
                'success': True,
                'message': f'Successfully found {len(tweets)} tweets for query "{query}"',
                'data': df_converted,
                'raw_data': df,
                'query': query,
                'tweet_count': len(tweets)
            }
            
        except Exception as e:
            logger.error(f"Error searching tweets: {str(e)}")
            return {
                'success': False,
                'message': f'Error searching tweets: {str(e)}',
                'error': str(e)
            }
    
    def _convert_to_app_format(self, df: pd.DataFrame, source: str) -> pd.DataFrame:
        """
        Convert Twitter data to app's expected format.
        
        Args:
            df: Twitter DataFrame
            source: Source identifier
            
        Returns:
            DataFrame in app format
        """
        try:
            # Create app format DataFrame
            app_df = pd.DataFrame({
                'ticket_id': df['tweet_id'].astype(str),
                'created_at': pd.to_datetime(df['created_at']),
                'responded_at': pd.to_datetime(df['created_at']) + pd.Timedelta(minutes=15),  # Simulate response time
                'customer_message': df['text'],
                'team': f'Twitter - {source}',
                'source': 'Twitter',
                'retweet_count': df.get('retweet_count', 0),
                'like_count': df.get('like_count', 0),
                'reply_count': df.get('reply_count', 0),
                'quote_count': df.get('quote_count', 0),
                'lang': df.get('lang', 'en')
            })
            
            return app_df
            
        except Exception as e:
            logger.error(f"Error converting Twitter data: {str(e)}")
            return df
    
    def disconnect(self):
        """Disconnect from Twitter API."""
        self.api = None
        self.client = None
        self.is_connected = False
        logger.info("Disconnected from Twitter API")

# Global instance
twitter_connector = TwitterAPIConnector()
