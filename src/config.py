"""
Configuration module for customer support analytics app.
Contains app settings, constants, and configuration parameters.
"""

import os
from typing import Dict, List, Any
from datetime import timedelta

class AppConfig:
    """Configuration class for the customer support analytics app."""
    
    def __init__(self):
        """Initialize configuration with default values."""
        self.app_name = "Customer Support Analytics"
        self.version = "1.0.0"
        
        # Data processing settings
        self.max_file_size_mb = 100
        self.max_rows_preview = 1000
        self.max_rows_processing = 100000
        
        # Response time settings
        self.sla_threshold_minutes = 60
        self.max_reasonable_response_hours = 24 * 30  # 30 days
        
        # Team performance settings
        self.min_tickets_per_team = 5  # Minimum tickets for team analysis
        self.sla_compliance_target = 80  # Target SLA compliance percentage
        
        # Team analysis configuration
        self.team_performance_weights = {
            'response_time': 0.30,
            'quality': 0.25,
            'efficiency': 0.25,
            'capacity': 0.20
        }
        
        self.team_scoring_thresholds = {
            'excellent': 90,
            'good': 75,
            'average': 60,
            'poor': 45,
            'critical': 30
        }
        
        self.team_analysis_settings = {
            'min_data_points': 5,
            'trend_analysis_days': 30,
            'benchmark_calculation': True,
            'insight_generation': True,
            'comparative_analysis': True
        }
        
        # Team visualization settings
        self.team_chart_colors = {
            'excellent': '#2E8B57',  # Sea Green
            'good': '#4682B4',       # Steel Blue
            'average': '#FF8C00',    # Dark Orange
            'poor': '#DC143C',       # Crimson
            'critical': '#8B0000',   # Dark Red
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd'
        }
        
        # Performance metrics configuration
        self.performance_metrics = {
            'efficiency_target': 80,
            'quality_target': 80,
            'consistency_target': 80,
            'capacity_target': 80,
            'response_time_target': 30,  # minutes
            'sentiment_target': 0.2
        }
        
        # Team insights configuration
        self.insights_settings = {
            'auto_generate': True,
            'include_recommendations': True,
            'include_action_items': True,
            'include_trends': True,
            'include_benchmarks': True,
            'max_recommendations': 5,
            'max_action_items': 3
        }
        
        # Visualization settings
        self.chart_height = 400
        self.chart_width = None  # Use container width
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd',
            'light': '#8c564b',
            'dark': '#e377c2'
        }
        
        # Data validation settings
        self.required_columns = [
            'ticket_id',
            'created_at', 
            'responded_at'
        ]
        
        self.optional_columns = [
            'team',
            'customer_message',
            'priority',
            'category',
            'resolution_time',
            'customer_satisfaction'
        ]
        
        # Column name variations for auto-detection
        self.column_variations = {
            'ticket_id': ['id', 'ticket', 'ticket_number', 'case_id', 'ticket_id'],
            'created_at': ['created', 'timestamp', 'date_created', 'open_time', 'created_at'],
            'responded_at': ['responded', 'response_time', 'closed_time', 'resolved_at', 'responded_at'],
            'team': ['team', 'group', 'department', 'assigned_team', 'support_team'],
            'customer_message': ['message', 'description', 'content', 'customer_message', 'ticket_content'],
            'priority': ['priority', 'urgency', 'severity', 'ticket_priority'],
            'category': ['category', 'type', 'classification', 'ticket_category']
        }
        
        # Performance thresholds
        self.performance_thresholds = {
            'excellent_response_time': 15,  # minutes
            'good_response_time': 30,      # minutes
            'acceptable_response_time': 60, # minutes
            'poor_response_time': 120      # minutes
        }
        
        # Sentiment analysis settings
        self.sentiment_thresholds = {
            'positive': 0.05,
            'negative': -0.05,
            'neutral_min': -0.05,
            'neutral_max': 0.05
        }
        
        # Sentiment analysis configuration
        self.sentiment_config = {
            'vader_weight': 0.7,  # Weight for VADER scores in combined analysis
            'textblob_weight': 0.3,  # Weight for TextBlob scores in combined analysis
            'batch_size': 100,  # Batch size for processing messages
            'min_confidence': 0.1,  # Minimum confidence threshold
            'max_text_length': 10000,  # Maximum text length to process
            'enable_text_preprocessing': True,  # Enable text cleaning
            'enable_keyword_extraction': True,  # Enable keyword extraction
            'enable_language_detection': True,  # Enable language detection
            'enable_text_statistics': True  # Enable text statistics
        }
        
        # Sentiment color schemes
        self.sentiment_colors = {
            'positive': '#2E8B57',  # Sea Green
            'negative': '#DC143C',  # Crimson
            'neutral': '#4682B4',   # Steel Blue
            'positive_light': '#90EE90',  # Light Green
            'negative_light': '#FFB6C1',  # Light Pink
            'neutral_light': '#B0C4DE',   # Light Steel Blue
            'positive_dark': '#006400',   # Dark Green
            'negative_dark': '#8B0000',   # Dark Red
            'neutral_dark': '#2F4F4F'     # Dark Slate Gray
        }
        
        # Text processing settings
        self.text_processing = {
            'max_keywords': 10,  # Maximum keywords to extract
            'min_word_length': 3,  # Minimum word length for keywords
            'remove_stop_words': True,  # Remove common stop words
            'enable_lemmatization': True,  # Enable word lemmatization
            'custom_stop_words': [
                'ticket', 'support', 'customer', 'service', 'help', 'issue',
                'problem', 'please', 'thank', 'thanks', 'hello', 'hi',
                'regards', 'best', 'sincerely', 'dear', 'sir', 'madam'
            ]
        }
        
        # Sentiment analysis performance settings
        self.sentiment_performance = {
            'max_messages_per_batch': 1000,  # Maximum messages per batch
            'progress_update_interval': 100,  # Progress update interval
            'memory_limit_mb': 500,  # Memory limit for processing
            'timeout_seconds': 300,  # Timeout for analysis
            'enable_caching': True,  # Enable result caching
            'cache_expiry_hours': 24  # Cache expiry time
        }
        
        # Export settings
        self.export_formats = ['csv', 'xlsx', 'json']
        self.export_filename_prefix = 'support_analytics'
        
        # Logging settings
        self.log_level = 'INFO'
        self.log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # UI settings
        self.sidebar_width = 300
        self.main_content_padding = 20
        self.chart_margin = {'l': 50, 'r': 50, 't': 50, 'b': 50}
        
        # Error messages
        self.error_messages = {
            'file_upload_error': 'Error uploading file. Please check the file format and try again.',
            'data_processing_error': 'Error processing data. Please check your data format.',
            'visualization_error': 'Error creating visualization. Please try again.',
            'missing_columns': 'Required columns are missing from the uploaded data.',
            'invalid_data': 'Invalid data detected. Please check your data quality.',
            'file_too_large': f'File is too large. Maximum size allowed: {self.max_file_size_mb}MB',
            'no_data': 'No data found in the uploaded file.'
        }
        
        # Success messages
        self.success_messages = {
            'file_uploaded': 'File uploaded successfully!',
            'data_processed': 'Data processed successfully!',
            'analysis_complete': 'Analysis completed successfully!'
        }
        
        # Help text
        self.help_text = {
            'file_upload': 'Upload a CSV file containing customer support data. Required columns: ticket_id, created_at, responded_at',
            'data_format': 'Data should be in CSV format with proper date formatting (YYYY-MM-DD HH:MM:SS)',
            'team_analysis': 'Team analysis requires a "team" column in your data',
            'sentiment_analysis': 'Sentiment analysis requires a "customer_message" column in your data'
        }
    
    def get_column_variations(self, column_name: str) -> List[str]:
        """
        Get possible variations for a column name.
        
        Args:
            column_name: The standard column name
            
        Returns:
            List[str]: List of possible variations
        """
        return self.column_variations.get(column_name, [column_name])
    
    def get_performance_category(self, response_time_minutes: float) -> str:
        """
        Categorize response time performance.
        
        Args:
            response_time_minutes: Response time in minutes
            
        Returns:
            str: Performance category
        """
        if response_time_minutes <= self.performance_thresholds['excellent_response_time']:
            return 'Excellent'
        elif response_time_minutes <= self.performance_thresholds['good_response_time']:
            return 'Good'
        elif response_time_minutes <= self.performance_thresholds['acceptable_response_time']:
            return 'Acceptable'
        else:
            return 'Poor'
    
    def get_sla_status(self, response_time_minutes: float) -> str:
        """
        Determine SLA compliance status.
        
        Args:
            response_time_minutes: Response time in minutes
            
        Returns:
            str: SLA status ('Compliant' or 'Breach')
        """
        return 'Compliant' if response_time_minutes <= self.sla_threshold_minutes else 'Breach'
    
    def validate_file_size(self, file_size_bytes: int) -> bool:
        """
        Validate if file size is within limits.
        
        Args:
            file_size_bytes: File size in bytes
            
        Returns:
            bool: True if file size is acceptable
        """
        max_size_bytes = self.max_file_size_mb * 1024 * 1024
        return file_size_bytes <= max_size_bytes
    
    def get_export_filename(self, data_type: str, format: str) -> str:
        """
        Generate export filename.
        
        Args:
            data_type: Type of data being exported
            format: Export format (csv, xlsx, json)
            
        Returns:
            str: Generated filename
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{self.export_filename_prefix}_{data_type}_{timestamp}.{format}"
    
    def get_sentiment_category(self, score: float) -> str:
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
    
    def get_sentiment_color(self, category: str, intensity: str = 'normal') -> str:
        """
        Get color for sentiment category.
        
        Args:
            category: Sentiment category ('positive', 'negative', 'neutral')
            intensity: Color intensity ('light', 'normal', 'dark')
            
        Returns:
            str: Hex color code
        """
        color_key = f"{category}_{intensity}" if intensity != 'normal' else category
        return self.sentiment_colors.get(color_key, self.sentiment_colors[category])
    
    def get_sentiment_config(self, key: str, default=None):
        """
        Get sentiment configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        return self.sentiment_config.get(key, default)
    
    def get_text_processing_config(self, key: str, default=None):
        """
        Get text processing configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        return self.text_processing.get(key, default)
    
    def get_sentiment_performance_config(self, key: str, default=None):
        """
        Get sentiment performance configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        return self.sentiment_performance.get(key, default)
    
    def is_sentiment_analysis_enabled(self) -> bool:
        """
        Check if sentiment analysis is enabled.
        
        Returns:
            bool: True if sentiment analysis is enabled
        """
        return self.sentiment_config.get('enable_text_preprocessing', True)
    
    def get_sentiment_batch_size(self) -> int:
        """
        Get the batch size for sentiment analysis.
        
        Returns:
            int: Batch size
        """
        return self.sentiment_config.get('batch_size', 100)
    
    def get_sentiment_threshold(self, category: str) -> float:
        """
        Get sentiment threshold for a category.
        
        Args:
            category: Sentiment category ('positive', 'negative', 'neutral_min', 'neutral_max')
            
        Returns:
            float: Threshold value
        """
        return self.sentiment_thresholds.get(category, 0.0)
    
    # Team Analysis Configuration Methods
    
    def get_team_performance_weights(self) -> Dict[str, float]:
        """
        Get team performance weights.
        
        Returns:
            Dict[str, float]: Performance weights
        """
        return self.team_performance_weights.copy()
    
    def get_team_scoring_thresholds(self) -> Dict[str, int]:
        """
        Get team scoring thresholds.
        
        Returns:
            Dict[str, int]: Scoring thresholds
        """
        return self.team_scoring_thresholds.copy()
    
    def get_team_analysis_settings(self) -> Dict[str, Any]:
        """
        Get team analysis settings.
        
        Returns:
            Dict[str, Any]: Analysis settings
        """
        return self.team_analysis_settings.copy()
    
    def get_team_chart_colors(self) -> Dict[str, str]:
        """
        Get team chart colors.
        
        Returns:
            Dict[str, str]: Chart colors
        """
        return self.team_chart_colors.copy()
    
    def get_performance_metrics_config(self) -> Dict[str, Any]:
        """
        Get performance metrics configuration.
        
        Returns:
            Dict[str, Any]: Performance metrics config
        """
        return self.performance_metrics.copy()
    
    def get_insights_settings(self) -> Dict[str, Any]:
        """
        Get insights generation settings.
        
        Returns:
            Dict[str, Any]: Insights settings
        """
        return self.insights_settings.copy()
    
    def get_team_performance_level(self, score: float) -> str:
        """
        Get team performance level based on score.
        
        Args:
            score: Performance score (0-100)
            
        Returns:
            str: Performance level
        """
        if score >= self.team_scoring_thresholds['excellent']:
            return 'excellent'
        elif score >= self.team_scoring_thresholds['good']:
            return 'good'
        elif score >= self.team_scoring_thresholds['average']:
            return 'average'
        elif score >= self.team_scoring_thresholds['poor']:
            return 'poor'
        else:
            return 'critical'
    
    def get_team_color(self, performance_level: str) -> str:
        """
        Get color for team performance level.
        
        Args:
            performance_level: Performance level ('excellent', 'good', 'average', 'poor', 'critical')
            
        Returns:
            str: Hex color code
        """
        return self.team_chart_colors.get(performance_level, self.team_chart_colors['primary'])
    
    def is_team_analysis_enabled(self) -> bool:
        """
        Check if team analysis is enabled.
        
        Returns:
            bool: True if team analysis is enabled
        """
        return self.team_analysis_settings.get('benchmark_calculation', True)
    
    def get_min_team_data_points(self) -> int:
        """
        Get minimum data points required for team analysis.
        
        Returns:
            int: Minimum data points
        """
        return self.team_analysis_settings.get('min_data_points', 5)
    
    def get_trend_analysis_days(self) -> int:
        """
        Get number of days for trend analysis.
        
        Returns:
            int: Number of days
        """
        return self.team_analysis_settings.get('trend_analysis_days', 30)
    
    def should_generate_insights(self) -> bool:
        """
        Check if insights should be auto-generated.
        
        Returns:
            bool: True if insights should be generated
        """
        return self.insights_settings.get('auto_generate', True)
    
    def get_max_recommendations(self) -> int:
        """
        Get maximum number of recommendations to generate.
        
        Returns:
            int: Maximum recommendations
        """
        return self.insights_settings.get('max_recommendations', 5)
    
    def get_max_action_items(self) -> int:
        """
        Get maximum number of action items to generate.
        
        Returns:
            int: Maximum action items
        """
        return self.insights_settings.get('max_action_items', 3)
