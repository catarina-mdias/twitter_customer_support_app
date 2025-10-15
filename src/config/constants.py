"""
Application Constants for Customer Support Analytics App
Stores application-wide constants and static values
"""

class AppConstants:
    """Stores application-wide constants."""

    # Custom CSS for enhanced styling
    CUSTOM_CSS: str = """
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .subtitle {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0 0;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    </style>
    """

    # Color schemes
    COLOR_SCHEMES: dict = {
        'primary': {
            'main': '#667eea',
            'light': '#8fa4f3',
            'dark': '#4c63d2'
        },
        'secondary': {
            'main': '#764ba2',
            'light': '#9a6bb8',
            'dark': '#5a3a7a'
        },
        'success': {
            'main': '#28a745',
            'light': '#5cb85c',
            'dark': '#1e7e34'
        },
        'warning': {
            'main': '#ffc107',
            'light': '#ffcd39',
            'dark': '#e0a800'
        },
        'error': {
            'main': '#dc3545',
            'light': '#e85d75',
            'dark': '#c82333'
        },
        'info': {
            'main': '#17a2b8',
            'light': '#5bc0de',
            'dark': '#138496'
        }
    }

    # Chart configurations
    CHART_CONFIGS: dict = {
        'response_time': {
            'color': '#667eea',
            'title': 'Response Time Analysis',
            'x_axis': 'Date',
            'y_axis': 'Response Time (minutes)'
        },
        'sentiment': {
            'color': '#28a745',
            'title': 'Sentiment Analysis',
            'x_axis': 'Date',
            'y_axis': 'Sentiment Score'
        },
        'team_performance': {
            'color': '#764ba2',
            'title': 'Team Performance',
            'x_axis': 'Team',
            'y_axis': 'Performance Score'
        }
    }

    # Animation durations (in milliseconds)
    ANIMATION_DURATIONS: dict = {
        'fast': 150,
        'normal': 300,
        'slow': 500
    }

    # Breakpoints for responsive design
    BREAKPOINTS: dict = {
        'mobile': 768,
        'tablet': 1024,
        'desktop': 1200
    }

    # Default values
    DEFAULTS: dict = {
        'chart_height': 400,
        'max_chart_points': 1000,
        'cache_ttl': 300,
        'page_size': 20
    }

    # File extensions
    SUPPORTED_FILE_EXTENSIONS: list = ['.csv', '.xlsx', '.json']

    # Date formats
    DATE_FORMATS: list = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
        '%m/%d/%Y %H:%M:%S',
        '%m/%d/%Y %H:%M',
        '%m/%d/%Y',
        '%d/%m/%Y %H:%M:%S',
        '%d/%m/%Y %H:%M',
        '%d/%m/%Y'
    ]

    # Regular expressions for data validation
    REGEX_PATTERNS: dict = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'phone': r'^\+?[\d\s\-\(\)]{10,}$',
        'url': r'^https?://[^\s/$.?#].[^\s]*$'
    }

    # Performance thresholds
    PERFORMANCE_THRESHOLDS: dict = {
        'excellent_response_time': 15,  # minutes
        'good_response_time': 30,
        'acceptable_response_time': 60,
        'excellent_sla_compliance': 0.95,  # 95%
        'good_sla_compliance': 0.85,       # 85%
        'acceptable_sla_compliance': 0.75,  # 75%
        'excellent_sentiment': 0.5,        # 0.5
        'good_sentiment': 0.2,             # 0.2
        'acceptable_sentiment': 0.0        # 0.0
    }

    # Team performance weights
    TEAM_PERFORMANCE_WEIGHTS: dict = {
        'response_time': 0.30,
        'quality': 0.25,
        'efficiency': 0.25,
        'capacity': 0.20
    }

    # Sentiment analysis weights
    SENTIMENT_WEIGHTS: dict = {
        'vader': 0.7,
        'textblob': 0.3
    }

    # Export formats and their MIME types
    EXPORT_MIME_TYPES: dict = {
        'csv': 'text/csv',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'json': 'application/json',
        'html': 'text/html',
        'pdf': 'application/pdf'
    }

    # Notification types
    NOTIFICATION_TYPES: list = ['success', 'error', 'warning', 'info']

    # Loading states
    LOADING_STATES: dict = {
        'skeleton': 'skeleton',
        'spinner': 'spinner',
        'progress': 'progress'
    }

    # Theme options
    THEMES: list = ['light', 'dark', 'auto']

    # Accessibility settings
    ACCESSIBILITY: dict = {
        'min_contrast_ratio': 4.5,
        'focus_outline_width': '2px',
        'focus_outline_color': '#667eea',
        'reduced_motion_duration': '0s'
    }