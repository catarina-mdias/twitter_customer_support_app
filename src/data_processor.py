"""
Data processing module for customer support analytics.
Handles data loading, validation, and response time calculations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import sentiment analysis modules
try:
    from sentiment_analyzer import SentimentAnalyzer
    from text_processor import TextProcessor
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    logger.warning("Sentiment analysis modules not available")

# Import team analysis modules
try:
    from team_analyzer import TeamAnalyzer
    from performance_metrics import PerformanceMetrics
    from insights_generator import InsightsGenerator
    TEAM_ANALYSIS_AVAILABLE = True
except ImportError:
    TEAM_ANALYSIS_AVAILABLE = False
    logger.warning("Team analysis modules not available")

# Import Twitter data adapter
try:
    from twitter_data_adapter import TwitterDataAdapter
    TWITTER_ADAPTER_AVAILABLE = True
except ImportError:
    TWITTER_ADAPTER_AVAILABLE = False
    logger.warning("Twitter data adapter not available")

class DataProcessor:
    """Handles data processing operations for customer support analytics."""
    
    def __init__(self):
        """Initialize the data processor."""
        self.required_columns = ['ticket_id', 'created_at', 'responded_at']
        self.optional_columns = ['team', 'customer_message', 'priority', 'category']
        
        # Initialize sentiment analysis components if available
        if SENTIMENT_AVAILABLE:
            self.sentiment_analyzer = SentimentAnalyzer()
            self.text_processor = TextProcessor()
            logger.info("Sentiment analysis components initialized")
        else:
            self.sentiment_analyzer = None
            self.text_processor = None
        
        # Initialize team analysis components if available
        if TEAM_ANALYSIS_AVAILABLE:
            self.team_analyzer = TeamAnalyzer()
            self.performance_metrics = PerformanceMetrics()
            self.insights_generator = InsightsGenerator()
            logger.info("Team analysis components initialized")
        else:
            self.team_analyzer = None
            self.performance_metrics = None
            self.insights_generator = None
        
        # Initialize Twitter data adapter if available
        if TWITTER_ADAPTER_AVAILABLE:
            self.twitter_adapter = TwitterDataAdapter()
            logger.info("Twitter data adapter initialized")
        else:
            self.twitter_adapter = None
    
    def load_data(self, uploaded_file) -> pd.DataFrame:
        """
        Load and validate CSV data from uploaded file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            pd.DataFrame: Processed and validated data
        """
        try:
            # Read CSV file
            df = pd.read_csv(uploaded_file)
            logger.info(f"Loaded {len(df)} rows from CSV file")
            
            # Check if this is Twitter data
            if self._is_twitter_data(df):
                logger.info("Detected Twitter data format, converting...")
                df = self._convert_twitter_data(df)
            
            # Validate required columns
            missing_columns = [col for col in self.required_columns if col not in df.columns]
            if missing_columns:
                logger.warning(f"Missing required columns: {missing_columns}")
                # Try to find similar column names
                df = self._fix_column_names(df)
            
            # Convert date columns
            df = self._convert_date_columns(df)
            
            # Basic data cleaning
            df = self._clean_data(df)
            
            logger.info(f"Data processing completed. Final shape: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def _fix_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Attempt to fix column names by finding similar names.
        
        Args:
            df: DataFrame with potentially incorrect column names
            
        Returns:
            pd.DataFrame: DataFrame with corrected column names
        """
        column_mapping = {}
        
        # Common variations for required columns
        variations = {
            'ticket_id': ['id', 'ticket', 'ticket_number', 'case_id'],
            'created_at': ['created', 'timestamp', 'date_created', 'open_time'],
            'responded_at': ['responded', 'response_time', 'closed_time', 'resolved_at']
        }
        
        for required_col, variations_list in variations.items():
            if required_col not in df.columns:
                for variation in variations_list:
                    if variation in df.columns:
                        column_mapping[variation] = required_col
                        break
        
        # Apply column mapping
        df = df.rename(columns=column_mapping)
        logger.info(f"Applied column mapping: {column_mapping}")
        
        return df
    
    def _is_twitter_data(self, df: pd.DataFrame) -> bool:
        """
        Check if the data is in Twitter format.
        
        Args:
            df: DataFrame to check
            
        Returns:
            bool: True if Twitter data format detected
        """
        twitter_columns = ['tweet_id', 'author_id', 'inbound', 'created_at', 'text']
        return all(col in df.columns for col in twitter_columns)
    
    def _convert_twitter_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert Twitter data to app format.
        
        Args:
            df: Twitter DataFrame
            
        Returns:
            pd.DataFrame: Converted data in app format (with original columns preserved)
        """
        if not TWITTER_ADAPTER_AVAILABLE or self.twitter_adapter is None:
            logger.error("Twitter adapter not available")
            return df
        
        try:
            # Store original Twitter columns before conversion
            original_cols = {}
            twitter_specific_cols = ['conversation_id', 'text', 'tweet_id', 'author_id', 'inbound']
            for col in twitter_specific_cols:
                if col in df.columns:
                    original_cols[col] = df[col].copy()
            
            # Convert to standard format
            converted_df = self.twitter_adapter.convert_twitter_data(df)
            
            # Preserve original Twitter columns for RAG and other features
            for col, data in original_cols.items():
                if col not in converted_df.columns:
                    converted_df[col] = data
            
            logger.info(f"Converted Twitter data and preserved original columns: {list(original_cols.keys())}")
            return converted_df
            
        except Exception as e:
            logger.error(f"Error converting Twitter data: {str(e)}")
            return df
    
    def _convert_date_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert date columns to datetime format.
        
        Args:
            df: DataFrame with date columns
            
        Returns:
            pd.DataFrame: DataFrame with converted date columns
        """
        date_columns = ['created_at', 'responded_at']
        
        for col in date_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    logger.info(f"Converted {col} to datetime format")
                except Exception as e:
                    logger.warning(f"Could not convert {col} to datetime: {str(e)}")
        
        return df
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform basic data cleaning operations.
        
        Args:
            df: DataFrame to clean
            
        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Remove duplicate rows
        initial_count = len(df)
        df = df.drop_duplicates()
        if len(df) < initial_count:
            logger.info(f"Removed {initial_count - len(df)} duplicate rows")
        
        # Clean text columns
        text_columns = ['customer_message', 'team']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace('nan', np.nan)
        
        return df
    
    def calculate_response_times(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate response times for each ticket.
        
        Args:
            df: DataFrame with created_at and responded_at columns
            
        Returns:
            pd.DataFrame: DataFrame with response_time_minutes column
        """
        if 'created_at' not in df.columns or 'responded_at' not in df.columns:
            logger.warning("Required date columns not found for response time calculation")
            return df
        
        # Create a copy to avoid modifying original
        df_rt = df.copy()
        
        # Calculate response time in minutes
        df_rt['response_time_minutes'] = (
            df_rt['responded_at'] - df_rt['created_at']
        ).dt.total_seconds() / 60
        
        # Handle negative response times (data quality issues)
        negative_count = (df_rt['response_time_minutes'] < 0).sum()
        if negative_count > 0:
            logger.warning(f"Found {negative_count} tickets with negative response times")
            df_rt = df_rt[df_rt['response_time_minutes'] >= 0]
        
        # Handle extremely long response times (likely data errors)
        max_reasonable_hours = 24 * 30  # 30 days
        max_reasonable_minutes = max_reasonable_hours * 60
        extreme_count = (df_rt['response_time_minutes'] > max_reasonable_minutes).sum()
        if extreme_count > 0:
            logger.warning(f"Found {extreme_count} tickets with extremely long response times")
            df_rt = df_rt[df_rt['response_time_minutes'] <= max_reasonable_minutes]
        
        logger.info(f"Calculated response times for {len(df_rt)} tickets")
        return df_rt
    
    def calculate_team_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate performance metrics for each team.
        
        Args:
            df: DataFrame with team and response_time_minutes columns
            
        Returns:
            pd.DataFrame: Team performance metrics
        """
        if 'team' not in df.columns or 'response_time_minutes' not in df.columns:
            logger.warning("Required columns not found for team metrics calculation")
            return pd.DataFrame()
        
        # Group by team and calculate metrics
        team_metrics = df.groupby('team')['response_time_minutes'].agg([
            'count',  # Number of tickets
            'mean',   # Average response time
            'median', # Median response time
            'std',    # Standard deviation
            lambda x: x.quantile(0.9),  # P90 response time
            lambda x: (x <= 60).mean() * 100,  # SLA compliance rate
            lambda x: (x > 60).mean() * 100,   # SLA breach rate
        ]).round(2)
        
        # Rename columns
        team_metrics.columns = [
            'Total Tickets',
            'Avg Response Time (min)',
            'Median Response Time (min)',
            'Std Dev (min)',
            'P90 Response Time (min)',
            'SLA Compliance Rate (%)',
            'SLA Breach Rate (%)'
        ]
        
        # Sort by median response time (best performers first)
        team_metrics = team_metrics.sort_values('Median Response Time (min)')
        
        logger.info(f"Calculated metrics for {len(team_metrics)} teams")
        return team_metrics
    
    def get_data_quality_report(self, df: pd.DataFrame) -> Dict:
        """
        Generate a data quality report.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dict: Data quality metrics
        """
        report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_data': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'data_types': df.dtypes.to_dict()
        }
        
        # Calculate completeness for each column
        report['completeness'] = {
            col: (1 - df[col].isnull().sum() / len(df)) * 100 
            for col in df.columns
        }
        
        return report
    
    def analyze_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze sentiment for customer messages in the dataset.
        
        Args:
            df: DataFrame with customer_message column
            
        Returns:
            pd.DataFrame: DataFrame with sentiment analysis results
        """
        if not SENTIMENT_AVAILABLE or self.sentiment_analyzer is None:
            logger.warning("Sentiment analysis not available")
            return df
        
        if 'customer_message' not in df.columns:
            logger.warning("No customer_message column found for sentiment analysis")
            return df
        
        try:
            logger.info("Starting sentiment analysis...")
            
            # Get customer messages
            messages = df['customer_message'].fillna('').astype(str).tolist()
            
            # Analyze sentiment in batches for efficiency
            batch_size = 100
            sentiment_results = []
            
            for i in range(0, len(messages), batch_size):
                batch_messages = messages[i:i + batch_size]
                batch_results = self.sentiment_analyzer.analyze_batch(batch_messages)
                sentiment_results.append(batch_results)
                
                if i % 500 == 0:
                    logger.info(f"Processed {i}/{len(messages)} messages for sentiment")
            
            # Combine all results
            all_sentiment_results = pd.concat(sentiment_results, ignore_index=True)
            
            # Add sentiment columns to original dataframe
            df_with_sentiment = df.copy()
            for col in all_sentiment_results.columns:
                df_with_sentiment[col] = all_sentiment_results[col]
            
            logger.info(f"Sentiment analysis completed for {len(messages)} messages")
            return df_with_sentiment
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return df
    
    def get_sentiment_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate sentiment metrics from the dataset.
        
        Args:
            df: DataFrame with sentiment analysis results
            
        Returns:
            Dict: Sentiment metrics
        """
        if not SENTIMENT_AVAILABLE or self.sentiment_analyzer is None:
            return {'error': 'Sentiment analysis not available'}
        
        if 'combined_score' not in df.columns:
            return {'error': 'No sentiment data found'}
        
        try:
            return self.sentiment_analyzer.get_sentiment_metrics(df)
        except Exception as e:
            logger.error(f"Error calculating sentiment metrics: {str(e)}")
            return {'error': str(e)}
    
    def get_sentiment_trends(self, df: pd.DataFrame, date_col: str = 'created_at') -> pd.DataFrame:
        """
        Calculate sentiment trends over time.
        
        Args:
            df: DataFrame with sentiment data and date column
            date_col: Name of the date column
            
        Returns:
            pd.DataFrame: Daily sentiment trends
        """
        if not SENTIMENT_AVAILABLE or self.sentiment_analyzer is None:
            return pd.DataFrame()
        
        try:
            return self.sentiment_analyzer.analyze_sentiment_trends(df, date_col)
        except Exception as e:
            logger.error(f"Error calculating sentiment trends: {str(e)}")
            return pd.DataFrame()
    
    def get_sentiment_correlation(self, df: pd.DataFrame) -> Dict:
        """
        Calculate correlation between sentiment and other metrics.
        
        Args:
            df: DataFrame with sentiment and other metrics
            
        Returns:
            Dict: Correlation results
        """
        if not SENTIMENT_AVAILABLE or self.sentiment_analyzer is None:
            return {}
        
        try:
            return self.sentiment_analyzer.get_sentiment_correlation(df)
        except Exception as e:
            logger.error(f"Error calculating sentiment correlation: {str(e)}")
            return {}
    
    def process_text_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process text statistics for customer messages.
        
        Args:
            df: DataFrame with customer_message column
            
        Returns:
            pd.DataFrame: DataFrame with text statistics
        """
        if not SENTIMENT_AVAILABLE or self.text_processor is None:
            return df
        
        if 'customer_message' not in df.columns:
            return df
        
        try:
            logger.info("Processing text statistics...")
            
            # Get customer messages
            messages = df['customer_message'].fillna('').astype(str).tolist()
            
            # Process text statistics
            text_stats = self.text_processor.process_batch_texts(messages)
            
            # Add text statistics to original dataframe
            df_with_text_stats = df.copy()
            for col in text_stats.columns:
                if col not in df_with_text_stats.columns:
                    df_with_text_stats[col] = text_stats[col]
            
            logger.info("Text statistics processing completed")
            return df_with_text_stats
            
        except Exception as e:
            logger.error(f"Error processing text statistics: {str(e)}")
            return df
    
    def get_team_sentiment_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate sentiment metrics by team.
        
        Args:
            df: DataFrame with team and sentiment data
            
        Returns:
            pd.DataFrame: Team sentiment metrics
        """
        if not SENTIMENT_AVAILABLE or self.sentiment_analyzer is None:
            return pd.DataFrame()
        
        if 'team' not in df.columns or 'combined_score' not in df.columns:
            return pd.DataFrame()
        
        try:
            # Group by team and calculate sentiment metrics
            team_sentiment = df.groupby('team').agg({
                'combined_score': ['mean', 'std', 'count'],
                'category': lambda x: (x == 'positive').sum() / len(x) * 100,
                'vader_positive': 'mean',
                'vader_negative': 'mean',
                'vader_neutral': 'mean'
            }).round(3)
            
            # Flatten column names
            team_sentiment.columns = [
                'avg_sentiment_score', 'sentiment_std', 'message_count',
                'positive_percentage', 'avg_positive_score', 'avg_negative_score', 'avg_neutral_score'
            ]
            
            # Sort by average sentiment score (best performers first)
            team_sentiment = team_sentiment.sort_values('avg_sentiment_score', ascending=False)
            
            logger.info(f"Calculated sentiment metrics for {len(team_sentiment)} teams")
            return team_sentiment
            
        except Exception as e:
            logger.error(f"Error calculating team sentiment metrics: {str(e)}")
            return pd.DataFrame()
    
    def filter_by_sentiment(self, df: pd.DataFrame, sentiment_filter: str = 'all') -> pd.DataFrame:
        """
        Filter data by sentiment category.
        
        Args:
            df: DataFrame with sentiment data
            sentiment_filter: Sentiment filter ('all', 'positive', 'negative', 'neutral')
            
        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        if sentiment_filter == 'all' or 'category' not in df.columns:
            return df
        
        try:
            filtered_df = df[df['category'] == sentiment_filter].copy()
            logger.info(f"Filtered data by sentiment: {sentiment_filter}, {len(filtered_df)} records")
            return filtered_df
        except Exception as e:
            logger.error(f"Error filtering by sentiment: {str(e)}")
            return df
    
    # Team Analysis Methods
    
    def get_team_performance_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive team performance analysis.
        
        Args:
            df: DataFrame with team performance data
            
        Returns:
            Dict[str, Any]: Team performance analysis
        """
        if not TEAM_ANALYSIS_AVAILABLE or 'team' not in df.columns:
            return {'error': 'Team analysis not available or team column missing'}
        
        try:
            # Group data by team
            teams_data = {}
            for team in df['team'].unique():
                team_df = df[df['team'] == team]
                teams_data[team] = team_df
            
            # Calculate team performance metrics
            team_analysis = {}
            for team_name, team_df in teams_data.items():
                if team_df.empty:
                    continue
                
                # Calculate performance metrics
                performance_metrics = self.performance_metrics.calculate_overall_performance(team_df)
                
                # Get team insights
                team_insights = self.team_analyzer.get_team_insights(team_df, team_name)
                
                team_analysis[team_name] = {
                    'performance_metrics': performance_metrics,
                    'team_insights': team_insights,
                    'data_summary': {
                        'total_tickets': len(team_df),
                        'avg_response_time': team_df['response_time_minutes'].mean() if 'response_time_minutes' in team_df.columns else 0,
                        'sla_compliance': (team_df['response_time_minutes'] <= 60).mean() if 'response_time_minutes' in team_df.columns else 0
                    }
                }
            
            logger.info(f"Generated team performance analysis for {len(team_analysis)} teams")
            return team_analysis
            
        except Exception as e:
            logger.error(f"Error generating team performance analysis: {str(e)}")
            return {'error': str(e)}
    
    def get_team_comparison(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get team comparison metrics.
        
        Args:
            df: DataFrame with team performance data
            
        Returns:
            pd.DataFrame: Team comparison data
        """
        if not TEAM_ANALYSIS_AVAILABLE or 'team' not in df.columns:
            return pd.DataFrame()
        
        try:
            # Calculate response times if not already present
            if 'response_time_minutes' not in df.columns:
                if 'created_at' in df.columns and 'responded_at' in df.columns:
                    df = self.calculate_response_times(df)
            
            # Analyze sentiment if not already present and text column exists
            text_column = None
            if 'text' in df.columns:
                text_column = 'text'
            elif 'customer_message' in df.columns:
                text_column = 'customer_message'
            
            if text_column and 'combined_score' not in df.columns:
                df = self.analyze_sentiment(df)
            
            # Group data by team
            teams_data = {}
            for team in df['team'].unique():
                team_df = df[df['team'] == team].copy()
                teams_data[team] = team_df
            
            # Get team comparison
            comparison_df = self.team_analyzer.compare_teams(teams_data)
            
            logger.info(f"Generated team comparison for {len(comparison_df)} teams")
            return comparison_df
            
        except Exception as e:
            logger.error(f"Error generating team comparison: {str(e)}")
            return pd.DataFrame()
    
    def get_team_rankings(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get team performance rankings.
        
        Args:
            df: DataFrame with team performance data
            
        Returns:
            pd.DataFrame: Team rankings
        """
        if not TEAM_ANALYSIS_AVAILABLE or 'team' not in df.columns:
            return pd.DataFrame()
        
        try:
            # Calculate response times if not already present
            if 'response_time_minutes' not in df.columns:
                if 'created_at' in df.columns and 'responded_at' in df.columns:
                    df = self.calculate_response_times(df)
            
            # Analyze sentiment if not already present and text column exists
            text_column = None
            if 'text' in df.columns:
                text_column = 'text'
            elif 'customer_message' in df.columns:
                text_column = 'customer_message'
            
            if text_column and 'combined_score' not in df.columns:
                df = self.analyze_sentiment(df)
            
            # Group data by team
            teams_data = {}
            for team in df['team'].unique():
                team_df = df[df['team'] == team].copy()
                teams_data[team] = team_df
            
            # Get team rankings
            rankings_df = self.team_analyzer.get_team_rankings(teams_data)
            
            logger.info(f"Generated team rankings for {len(rankings_df)} teams")
            return rankings_df
            
        except Exception as e:
            logger.error(f"Error generating team rankings: {str(e)}")
            return pd.DataFrame()
    
    def get_team_insights(self, df: pd.DataFrame, team_name: str) -> Dict[str, Any]:
        """
        Get insights for a specific team.
        
        Args:
            df: DataFrame with team performance data
            team_name: Name of the team
            
        Returns:
            Dict[str, Any]: Team insights
        """
        if not TEAM_ANALYSIS_AVAILABLE or 'team' not in df.columns:
            return {'error': 'Team analysis not available or team column missing'}
        
        try:
            # Filter data for specific team
            team_df = df[df['team'] == team_name]
            
            if team_df.empty:
                return {'error': f'No data found for team: {team_name}'}
            
            # Calculate performance metrics
            performance_metrics = self.performance_metrics.calculate_overall_performance(team_df)
            
            # Generate insights
            insights = self.insights_generator.generate_team_insights(team_df, team_name, performance_metrics)
            
            logger.info(f"Generated insights for team: {team_name}")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating team insights: {str(e)}")
            return {'error': str(e)}
    
    def get_team_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get team performance trends over time.
        
        Args:
            df: DataFrame with historical team performance data
            
        Returns:
            Dict[str, Any]: Team trend analysis
        """
        if not TEAM_ANALYSIS_AVAILABLE or 'team' not in df.columns:
            return {'error': 'Team analysis not available or team column missing'}
        
        try:
            # Group data by team
            teams_data = {}
            for team in df['team'].unique():
                team_df = df[df['team'] == team]
                teams_data[team] = team_df
            
            # Get team trends
            trends = self.team_analyzer.track_performance_trends(df)
            
            logger.info(f"Generated team trends for {len(trends)} teams")
            return trends
            
        except Exception as e:
            logger.error(f"Error generating team trends: {str(e)}")
            return {'error': str(e)}
    
    def get_performance_benchmarks(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get performance benchmarks across all teams.
        
        Args:
            df: DataFrame with team performance data
            
        Returns:
            Dict[str, Any]: Performance benchmarks
        """
        if not TEAM_ANALYSIS_AVAILABLE or 'team' not in df.columns:
            return {'error': 'Team analysis not available or team column missing'}
        
        try:
            # Group data by team
            teams_data = {}
            for team in df['team'].unique():
                team_df = df[df['team'] == team]
                teams_data[team] = team_df
            
            # Get performance benchmarks
            benchmarks = self.performance_metrics.get_performance_benchmarks(teams_data)
            
            logger.info(f"Generated performance benchmarks for {len(teams_data)} teams")
            return benchmarks
            
        except Exception as e:
            logger.error(f"Error generating performance benchmarks: {str(e)}")
            return {'error': str(e)}
    
    def get_comparative_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comparative insights across all teams.
        
        Args:
            df: DataFrame with team performance data
            
        Returns:
            Dict[str, Any]: Comparative insights
        """
        if not TEAM_ANALYSIS_AVAILABLE or 'team' not in df.columns:
            return {'error': 'Team analysis not available or team column missing'}
        
        try:
            # Group data by team
            teams_data = {}
            for team in df['team'].unique():
                team_df = df[df['team'] == team]
                teams_data[team] = team_df
            
            # Get comparative insights
            insights = self.insights_generator.generate_comparative_insights(teams_data)
            
            logger.info(f"Generated comparative insights for {len(teams_data)} teams")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating comparative insights: {str(e)}")
            return {'error': str(e)}
