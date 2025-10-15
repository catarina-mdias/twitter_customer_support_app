"""
Application Settings for Customer Support Analytics App
Centralized configuration settings and constants
"""

from typing import Dict, List, Any
from datetime import timedelta

class AppSettings:
    """Centralized application settings and configurations."""

    # App Information
    APP_NAME: str = "Customer Support Analytics"
    VERSION: str = "2.0.0"
    APP_SUBTITLE: str = "Transform your support data into actionable insights with advanced analytics"
    PAGE_ICON: str = "📊"
    LAYOUT: str = "wide"
    INITIAL_SIDEBAR_STATE: str = "expanded"

    # Data processing settings
    MAX_FILE_SIZE_MB: int = 100
    MAX_ROWS_PREVIEW: int = 1000
    MAX_ROWS_PROCESSING: int = 100000

    # Column names (standardized)
    TICKET_ID_COL: str = 'ticket_id'
    CREATED_AT_COL: str = 'created_at'
    RESPONDED_AT_COL: str = 'responded_at'
    CUSTOMER_MESSAGE_COL: str = 'customer_message'
    TEAM_COL: str = 'team'
    RESPONSE_TIME_COL: str = 'response_time_minutes'
    SENTIMENT_SCORE_COL: str = 'combined_score'
    SENTIMENT_CATEGORY_COL: str = 'category'

    # Response time settings
    SLA_THRESHOLD_MINUTES: int = 60
    MAX_REASONABLE_RESPONSE_HOURS: int = 24 * 30  # 30 days

    # Team performance settings
    MIN_TICKETS_PER_TEAM: int = 5
    SLA_COMPLIANCE_TARGET: int = 80

    # Sentiment analysis settings
    SENTIMENT_THRESHOLDS: Dict[str, float] = {
        'positive': 0.05,
        'negative': -0.05,
        'neutral_min': -0.05,
        'neutral_max': 0.05
    }
    VADER_WEIGHT: float = 0.7
    TEXTBLOB_WEIGHT: float = 0.3

    # Caching settings
    CACHE_TTL_SECONDS: int = 300  # 5 minutes

    # Error messages
    ERROR_MESSAGES: Dict[str, str] = {
        'file_upload_error': 'Error uploading file. Please check the file format and try again.',
        'data_processing_error': 'Error processing data. Please check your data format.',
        'visualization_error': 'Error creating visualization. Please try again.',
        'missing_columns': 'Required columns are missing from the uploaded data.',
        'invalid_data': 'Invalid data detected. Please check your data quality.',
        'file_too_large': 'File is too large. Maximum size allowed: {max_size}MB',
        'no_data': 'No data found in the uploaded file or after filtering.'
    }

    # Success messages
    SUCCESS_MESSAGES: Dict[str, str] = {
        'file_uploaded': 'File uploaded successfully!',
        'data_processed': 'Data processed successfully!',
        'analysis_complete': 'Analysis completed successfully!'
    }

    # Help text
    HELP_TEXT: Dict[str, str] = {
        'file_upload': 'Upload a CSV file containing customer support data. Required columns: ticket_id, created_at, responded_at',
        'data_format': 'Data should be in CSV format with proper date formatting (YYYY-MM-DD HH:MM:SS)',
        'team_analysis': 'Team analysis requires a "team" column in your data',
        'sentiment_analysis': 'Sentiment analysis requires a "customer_message" column in your data'
    }

    # Required and optional columns for data validation
    REQUIRED_COLUMNS: List[str] = [TICKET_ID_COL, CREATED_AT_COL, RESPONDED_AT_COL]
    OPTIONAL_COLUMNS: List[str] = [TEAM_COL, CUSTOMER_MESSAGE_COL, 'priority', 'category']

    # Column name variations for auto-detection
    COLUMN_VARIATIONS: Dict[str, List[str]] = {
        TICKET_ID_COL: ['id', 'ticket', 'ticket_number', 'case_id', TICKET_ID_COL],
        CREATED_AT_COL: ['created', 'timestamp', 'date_created', 'open_time', CREATED_AT_COL],
        RESPONDED_AT_COL: ['responded', 'response_time', 'closed_time', 'resolved_at', RESPONDED_AT_COL],
        TEAM_COL: ['team', 'group', 'department', 'assigned_team', 'support_team'],
        CUSTOMER_MESSAGE_COL: ['message', 'description', 'content', CUSTOMER_MESSAGE_COL, 'ticket_content'],
        'priority': ['priority', 'urgency', 'severity', 'ticket_priority'],
        'category': ['category', 'type', 'classification', 'ticket_category']
    }

    # Performance settings
    CHART_HEIGHT: int = 400
    MAX_CHART_POINTS: int = 1000

    # UI Settings
    SIDEBAR_WIDTH: int = 300
    MAIN_CONTENT_PADDING: int = 20
    CHART_MARGIN: Dict[str, int] = {'l': 50, 'r': 50, 't': 50, 'b': 50}

    # Export settings
    EXPORT_FORMATS: List[str] = ['csv', 'xlsx', 'json']
    EXPORT_FILENAME_PREFIX: str = 'support_analytics'

    # Logging settings
    LOG_LEVEL: str = 'INFO'
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    def get_column_variations(self, column_name: str) -> List[str]:
        """Get column name variations for a given column."""
        return self.COLUMN_VARIATIONS.get(column_name, [column_name])

    def get_performance_category(self, response_time: float) -> str:
        """Get performance category based on response time."""
        if response_time <= 15:
            return 'excellent'
        elif response_time <= 30:
            return 'good'
        elif response_time <= 60:
            return 'average'
        else:
            return 'poor'

    def get_sla_status(self, response_time: float) -> str:
        """Get SLA status based on response time."""
        if response_time <= self.SLA_THRESHOLD_MINUTES:
            return 'compliant'
        else:
            return 'breached'

    def validate_file_size(self, file_size_bytes: int) -> bool:
        """Validate if file size is within limits."""
        max_size_bytes = self.MAX_FILE_SIZE_MB * 1024 * 1024
        return file_size_bytes <= max_size_bytes

    def get_export_filename(self, report_type: str, format: str) -> str:
        """Generate export filename."""
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{self.EXPORT_FILENAME_PREFIX}_{report_type}_{timestamp}.{format}"

    def get_sentiment_category(self, score: float) -> str:
        """Get sentiment category based on score."""
        if score > self.SENTIMENT_THRESHOLDS['positive']:
            return 'positive'
        elif score < self.SENTIMENT_THRESHOLDS['negative']:
            return 'negative'
        else:
            return 'neutral'

    def get_sentiment_color(self, category: str) -> str:
        """Get color for sentiment category."""
        colors = {
            'positive': '#28a745',
            'negative': '#dc3545',
            'neutral': '#6c757d'
        }
        return colors.get(category, '#6c757d')

    def get_team_performance_level(self, score: float) -> str:
        """Get team performance level based on score."""
        if score >= 90:
            return 'excellent'
        elif score >= 75:
            return 'good'
        elif score >= 60:
            return 'average'
        else:
            return 'poor'

    def get_team_color(self, level: str) -> str:
        """Get color for team performance level."""
        colors = {
            'excellent': '#28a745',
            'good': '#17a2b8',
            'average': '#ffc107',
            'poor': '#dc3545'
        }
        return colors.get(level, '#6c757d')