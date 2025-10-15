"""
Configuration Loader for Support Analytics App
Loads configuration from JSON files and environment variables.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigLoader:
    """Loads and manages application configuration."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from files and environment variables."""
        # Determine environment
        environment = os.getenv('ENVIRONMENT', 'development')
        
        # Load base configuration
        config_file = self.config_dir / f"{environment}.json"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        else:
            # Fallback to development config
            dev_config_file = self.config_dir / "development.json"
            if dev_config_file.exists():
                with open(dev_config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = self._get_default_config()
        
        # Override with environment variables
        self._override_with_env()
    
    def _override_with_env(self):
        """Override configuration with environment variables."""
        # Database configuration
        if os.getenv('DB_HOST'):
            self.config['database']['params']['host'] = os.getenv('DB_HOST')
        if os.getenv('DB_PORT'):
            self.config['database']['params']['port'] = int(os.getenv('DB_PORT'))
        if os.getenv('DB_NAME'):
            self.config['database']['params']['database'] = os.getenv('DB_NAME')
        if os.getenv('DB_USER'):
            self.config['database']['params']['user'] = os.getenv('DB_USER')
        if os.getenv('DB_PASSWORD'):
            self.config['database']['params']['password'] = os.getenv('DB_PASSWORD')
        
        # Redis configuration
        if os.getenv('REDIS_HOST'):
            self.config['cache']['redis']['host'] = os.getenv('REDIS_HOST')
        if os.getenv('REDIS_PORT'):
            self.config['cache']['redis']['port'] = int(os.getenv('REDIS_PORT'))
        if os.getenv('REDIS_PASSWORD'):
            self.config['cache']['redis']['password'] = os.getenv('REDIS_PASSWORD')
        
        # API credentials
        if os.getenv('ZENDESK_EMAIL'):
            self.config['apis']['zendesk']['credentials']['email'] = os.getenv('ZENDESK_EMAIL')
        if os.getenv('ZENDESK_TOKEN'):
            self.config['apis']['zendesk']['credentials']['token'] = os.getenv('ZENDESK_TOKEN')
        
        if os.getenv('FRESHDESK_API_KEY'):
            self.config['apis']['freshdesk']['credentials']['api_key'] = os.getenv('FRESHDESK_API_KEY')
        
        if os.getenv('INTERCOM_TOKEN'):
            self.config['apis']['intercom']['credentials']['token'] = os.getenv('INTERCOM_TOKEN')
        
        if os.getenv('SLACK_BOT_TOKEN'):
            self.config['apis']['slack']['credentials']['token'] = os.getenv('SLACK_BOT_TOKEN')
            self.config['websockets']['slack_rtm']['auth_token'] = os.getenv('SLACK_BOT_TOKEN')
        
        if os.getenv('DISCORD_BOT_TOKEN'):
            self.config['websockets']['discord_gateway']['auth_token'] = os.getenv('DISCORD_BOT_TOKEN')
        
        # Cloud storage
        if os.getenv('AWS_ACCESS_KEY_ID'):
            self.config['cloud_storage']['aws_s3']['credentials']['access_key_id'] = os.getenv('AWS_ACCESS_KEY_ID')
        if os.getenv('AWS_SECRET_ACCESS_KEY'):
            self.config['cloud_storage']['aws_s3']['credentials']['secret_access_key'] = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        # Monitoring
        if os.getenv('SLACK_WEBHOOK_URL'):
            self.config['monitoring']['notifications']['slack']['webhook_url'] = os.getenv('SLACK_WEBHOOK_URL')
        
        # Logging
        if os.getenv('LOG_LEVEL'):
            self.config['logging']['level'] = os.getenv('LOG_LEVEL')
        if os.getenv('LOG_FILE'):
            self.config['logging']['file'] = os.getenv('LOG_FILE')
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "environment": "development",
            "database": {
                "type": "sqlite",
                "params": {"database": ":memory:"}
            },
            "apis": {},
            "websockets": {},
            "cloud_storage": {},
            "monitoring": {
                "refresh_interval": 30,
                "alert_thresholds": {
                    "response_time_high": 60,
                    "sla_breach_rate": 0.1,
                    "sentiment_low": -0.2
                }
            },
            "cache": {
                "redis": {
                    "host": "localhost",
                    "port": 6379,
                    "db": 0,
                    "password": None,
                    "ttl": 300
                }
            },
            "logging": {
                "level": "INFO",
                "file": "logs/support_analytics.log",
                "max_size": "10MB",
                "backup_count": 5
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return self.get('database', {})
    
    def get_api_config(self, api_name: str) -> Dict[str, Any]:
        """Get API configuration by name."""
        return self.get(f'apis.{api_name}', {})
    
    def get_websocket_config(self, ws_name: str) -> Dict[str, Any]:
        """Get WebSocket configuration by name."""
        return self.get(f'websockets.{ws_name}', {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return self.get('monitoring', {})
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration."""
        return self.get('cache', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get('logging', {})
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.get('environment') == 'production'
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.get('environment') == 'development'
    
    def get_all_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get all API configurations."""
        return self.get('apis', {})
    
    def get_all_websockets(self) -> Dict[str, Dict[str, Any]]:
        """Get all WebSocket configurations."""
        return self.get('websockets', {})
    
    def get_all_cloud_storage(self) -> Dict[str, Dict[str, Any]]:
        """Get all cloud storage configurations."""
        return self.get('cloud_storage', {})

# Global configuration instance
config = ConfigLoader()

def get_config() -> ConfigLoader:
    """Get the global configuration instance."""
    return config
