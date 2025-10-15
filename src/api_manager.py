"""
API Manager module for real-time customer support analytics.
Handles multiple API data sources and real-time data access.
"""

import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
from datetime import datetime, timedelta
import threading
import time
import json
import asyncio
import aiohttp
from dataclasses import dataclass
from enum import Enum

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIType(Enum):
    """Supported API types."""
    ZENDESK = "zendesk"
    FRESHDESK = "freshdesk"
    INTERCOM = "intercom"
    SLACK = "slack"
    TEAMS = "teams"
    DISCORD = "discord"
    CUSTOM = "custom"

@dataclass
class APIConfig:
    """API configuration data class."""
    api_type: APIType
    base_url: str
    credentials: Dict[str, str]
    headers: Dict[str, str]
    rate_limit: int = 100  # requests per minute
    timeout: int = 30
    retry_attempts: int = 3
    refresh_interval: int = 60  # seconds

class APIManager:
    """Manages multiple API data sources for real-time customer support analytics."""
    
    def __init__(self):
        """Initialize the API manager."""
        self.active_connections = {}
        self.refresh_intervals = {}
        self.monitoring_threads = {}
        self.data_cache = {}
        self.last_update = {}
        self.rate_limiters = {}
        
        # API endpoints for different services
        self.api_endpoints = {
            APIType.ZENDESK: {
                'tickets': '/api/v2/tickets.json',
                'users': '/api/v2/users.json',
                'organizations': '/api/v2/organizations.json'
            },
            APIType.FRESHDESK: {
                'tickets': '/api/v2/tickets',
                'contacts': '/api/v2/contacts',
                'agents': '/api/v2/agents'
            },
            APIType.INTERCOM: {
                'conversations': '/conversations',
                'users': '/users',
                'teams': '/teams'
            },
            APIType.SLACK: {
                'messages': '/api/conversations.history',
                'channels': '/api/conversations.list',
                'users': '/api/users.list'
            }
        }
        
        logger.info("API Manager initialized")
    
    def add_api_source(self, source_id: str, api_config: APIConfig) -> Dict:
        """
        Add a new API data source.
        
        Args:
            source_id: Unique identifier for the API source
            api_config: API configuration
            
        Returns:
            Dict with connection status
        """
        try:
            # Validate API configuration
            validation_result = self._validate_api_config(api_config)
            if not validation_result['success']:
                return validation_result
            
            # Test connection
            test_result = self._test_api_connection(api_config)
            if not test_result['success']:
                return test_result
            
            # Store configuration
            self.active_connections[source_id] = {
                'config': api_config,
                'created_at': datetime.now(),
                'last_successful_request': datetime.now(),
                'request_count': 0,
                'error_count': 0
            }
            
            # Initialize rate limiter
            self.rate_limiters[source_id] = {
                'last_request': datetime.now(),
                'request_count': 0,
                'window_start': datetime.now()
            }
            
            logger.info(f"Added API source: {source_id} ({api_config.api_type.value})")
            
            return {
                'success': True,
                'source_id': source_id,
                'message': f"Successfully added {api_config.api_type.value} API source"
            }
            
        except Exception as e:
            logger.error(f"Error adding API source: {e}")
            return {
                'success': False,
                'message': f"Failed to add API source: {str(e)}"
            }
    
    def remove_api_source(self, source_id: str) -> Dict:
        """
        Remove an API data source.
        
        Args:
            source_id: ID of the API source to remove
            
        Returns:
            Dict with removal status
        """
        try:
            if source_id in self.active_connections:
                # Stop monitoring if active
                if source_id in self.monitoring_threads:
                    self.stop_auto_refresh(source_id)
                
                # Remove from all collections
                del self.active_connections[source_id]
                if source_id in self.refresh_intervals:
                    del self.refresh_intervals[source_id]
                if source_id in self.data_cache:
                    del self.data_cache[source_id]
                if source_id in self.last_update:
                    del self.last_update[source_id]
                if source_id in self.rate_limiters:
                    del self.rate_limiters[source_id]
                
                logger.info(f"Removed API source: {source_id}")
                
                return {
                    'success': True,
                    'message': f"Successfully removed API source: {source_id}"
                }
            else:
                return {
                    'success': False,
                    'message': f"API source not found: {source_id}"
                }
                
        except Exception as e:
            logger.error(f"Error removing API source: {e}")
            return {
                'success': False,
                'message': f"Failed to remove API source: {str(e)}"
            }
    
    def start_auto_refresh(self, source_id: str, interval: int = 60, callback: Optional[callable] = None) -> Dict:
        """
        Start automatic data refresh for an API source.
        
        Args:
            source_id: ID of the API source
            interval: Refresh interval in seconds
            callback: Callback function for data updates
            
        Returns:
            Dict with refresh status
        """
        try:
            if source_id not in self.active_connections:
                return {
                    'success': False,
                    'message': f"API source not found: {source_id}"
                }
            
            # Stop existing refresh if any
            if source_id in self.monitoring_threads:
                self.stop_auto_refresh(source_id)
            
            # Start refresh thread
            stop_event = threading.Event()
            refresh_thread = threading.Thread(
                target=self._refresh_loop,
                args=(source_id, interval, callback, stop_event),
                daemon=True
            )
            
            self.monitoring_threads[source_id] = {
                'thread': refresh_thread,
                'stop': stop_event,
                'interval': interval,
                'callback': callback
            }
            
            self.refresh_intervals[source_id] = interval
            refresh_thread.start()
            
            logger.info(f"Started auto-refresh for {source_id} (interval: {interval}s)")
            
            return {
                'success': True,
                'message': f"Auto-refresh started for {source_id}",
                'interval': interval
            }
            
        except Exception as e:
            logger.error(f"Error starting auto-refresh: {e}")
            return {
                'success': False,
                'message': f"Failed to start auto-refresh: {str(e)}"
            }
    
    def stop_auto_refresh(self, source_id: str) -> Dict:
        """
        Stop automatic data refresh for an API source.
        
        Args:
            source_id: ID of the API source
            
        Returns:
            Dict with stop status
        """
        try:
            if source_id in self.monitoring_threads:
                self.monitoring_threads[source_id]['stop'].set()
                del self.monitoring_threads[source_id]
                
                if source_id in self.refresh_intervals:
                    del self.refresh_intervals[source_id]
                
                logger.info(f"Stopped auto-refresh for {source_id}")
                
                return {
                    'success': True,
                    'message': f"Auto-refresh stopped for {source_id}"
                }
            else:
                return {
                    'success': False,
                    'message': f"No active refresh found for {source_id}"
                }
                
        except Exception as e:
            logger.error(f"Error stopping auto-refresh: {e}")
            return {
                'success': False,
                'message': f"Failed to stop auto-refresh: {str(e)}"
            }
    
    def get_real_time_data(self, source_id: str, endpoint: str = None) -> Dict:
        """
        Get real-time data from an API source.
        
        Args:
            source_id: ID of the API source
            endpoint: Specific endpoint to query
            
        Returns:
            Dict with data and status
        """
        try:
            if source_id not in self.active_connections:
                return {
                    'success': False,
                    'message': f"API source not found: {source_id}"
                }
            
            # Check rate limiting
            if not self._check_rate_limit(source_id):
                return {
                    'success': False,
                    'message': "Rate limit exceeded, please wait"
                }
            
            connection_info = self.active_connections[source_id]
            api_config = connection_info['config']
            
            # Determine endpoint
            if not endpoint:
                endpoint = self._get_default_endpoint(api_config.api_type)
            
            # Make API request
            data = self._make_api_request(api_config, endpoint)
            
            if data['success']:
                # Process and standardize data
                processed_data = self._process_api_data(data['data'], api_config.api_type)
                
                # Update cache
                self.data_cache[source_id] = {
                    'data': processed_data,
                    'timestamp': datetime.now(),
                    'endpoint': endpoint
                }
                
                self.last_update[source_id] = datetime.now()
                connection_info['last_successful_request'] = datetime.now()
                connection_info['request_count'] += 1
                
                logger.info(f"Retrieved data from {source_id}: {len(processed_data)} records")
                
                return {
                    'success': True,
                    'data': processed_data,
                    'row_count': len(processed_data),
                    'timestamp': datetime.now(),
                    'source_id': source_id
                }
            else:
                connection_info['error_count'] += 1
                return data
                
        except Exception as e:
            logger.error(f"Error getting real-time data: {e}")
            if source_id in self.active_connections:
                self.active_connections[source_id]['error_count'] += 1
            
            return {
                'success': False,
                'message': f"Failed to get real-time data: {str(e)}"
            }
    
    def _validate_api_config(self, api_config: APIConfig) -> Dict:
        """Validate API configuration."""
        try:
            if not api_config.base_url:
                return {
                    'success': False,
                    'message': "Base URL is required"
                }
            
            if not api_config.credentials:
                return {
                    'success': False,
                    'message': "API credentials are required"
                }
            
            return {'success': True}
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Configuration validation failed: {str(e)}"
            }
    
    def _test_api_connection(self, api_config: APIConfig) -> Dict:
        """Test API connection."""
        try:
            # Make a simple test request
            test_url = f"{api_config.base_url}/test" if api_config.api_type == APIType.CUSTOM else f"{api_config.base_url}/"
            
            response = requests.get(
                test_url,
                headers=api_config.headers,
                auth=self._get_auth(api_config),
                timeout=api_config.timeout
            )
            
            if response.status_code in [200, 401, 403]:  # 401/403 means API is reachable but auth might be needed
                return {'success': True}
            else:
                return {
                    'success': False,
                    'message': f"API test failed with status {response.status_code}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"API connection test failed: {str(e)}"
            }
    
    def _make_api_request(self, api_config: APIConfig, endpoint: str) -> Dict:
        """Make API request."""
        try:
            url = f"{api_config.base_url}{endpoint}"
            
            response = requests.get(
                url,
                headers=api_config.headers,
                auth=self._get_auth(api_config),
                timeout=api_config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'data': data
                }
            else:
                return {
                    'success': False,
                    'message': f"API request failed with status {response.status_code}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"API request failed: {str(e)}"
            }
    
    def _get_auth(self, api_config: APIConfig):
        """Get authentication for API request."""
        credentials = api_config.credentials
        
        if api_config.api_type == APIType.ZENDESK:
            return (credentials.get('email'), credentials.get('token'))
        elif api_config.api_type == APIType.FRESHDESK:
            return (credentials.get('api_key'), 'X')
        elif api_config.api_type == APIType.INTERCOM:
            return None  # Uses Bearer token in headers
        else:
            return None
    
    def _get_default_endpoint(self, api_type: APIType) -> str:
        """Get default endpoint for API type."""
        endpoints = self.api_endpoints.get(api_type, {})
        return endpoints.get('tickets', '/')
    
    def _process_api_data(self, data: Dict, api_type: APIType) -> pd.DataFrame:
        """Process API data into standardized format."""
        try:
            # Extract records from API response
            if api_type == APIType.ZENDESK:
                records = data.get('tickets', [])
            elif api_type == APIType.FRESHDESK:
                records = data if isinstance(data, list) else data.get('results', [])
            elif api_type == APIType.INTERCOM:
                records = data.get('conversations', [])
            else:
                records = data if isinstance(data, list) else [data]
            
            if not records:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            # Standardize columns based on API type
            df = self._standardize_api_columns(df, api_type)
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing API data: {e}")
            return pd.DataFrame()
    
    def _standardize_api_columns(self, df: pd.DataFrame, api_type: APIType) -> pd.DataFrame:
        """Standardize columns based on API type."""
        try:
            column_mapping = {}
            
            if api_type == APIType.ZENDESK:
                column_mapping = {
                    'id': 'ticket_id',
                    'created_at': 'created_at',
                    'updated_at': 'responded_at',
                    'description': 'customer_message',
                    'assignee_id': 'team',
                    'status': 'status',
                    'priority': 'priority'
                }
            elif api_type == APIType.FRESHDESK:
                column_mapping = {
                    'id': 'ticket_id',
                    'created_at': 'created_at',
                    'updated_at': 'responded_at',
                    'description': 'customer_message',
                    'responder_id': 'team',
                    'status': 'status',
                    'priority': 'priority'
                }
            elif api_type == APIType.INTERCOM:
                column_mapping = {
                    'id': 'ticket_id',
                    'created_at': 'created_at',
                    'updated_at': 'responded_at',
                    'source': 'customer_message',
                    'assignee': 'team'
                }
            
            # Rename columns
            df = df.rename(columns=column_mapping)
            
            # Convert datetime columns
            datetime_columns = ['created_at', 'responded_at']
            for col in datetime_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            logger.error(f"Error standardizing API columns: {e}")
            return df
    
    def _check_rate_limit(self, source_id: str) -> bool:
        """Check if request is within rate limit."""
        try:
            if source_id not in self.rate_limiters:
                return True
            
            limiter = self.rate_limiters[source_id]
            connection_info = self.active_connections[source_id]
            api_config = connection_info['config']
            
            now = datetime.now()
            window_start = limiter['window_start']
            
            # Reset window if needed
            if (now - window_start).seconds >= 60:
                limiter['window_start'] = now
                limiter['request_count'] = 0
            
            # Check if within limit
            if limiter['request_count'] < api_config.rate_limit:
                limiter['request_count'] += 1
                limiter['last_request'] = now
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True
    
    def _refresh_loop(self, source_id: str, interval: int, callback: callable, stop_event: threading.Event):
        """Internal refresh loop."""
        try:
            while not stop_event.is_set():
                try:
                    # Get latest data
                    data_result = self.get_real_time_data(source_id)
                    
                    if data_result['success'] and callback:
                        callback(source_id, data_result['data'])
                    
                    # Wait for next refresh
                    stop_event.wait(interval)
                    
                except Exception as e:
                    logger.error(f"Error in refresh loop: {e}")
                    stop_event.wait(60)  # Wait longer on error
                    
        except Exception as e:
            logger.error(f"Refresh loop error: {e}")
    
    def get_source_status(self, source_id: str) -> Dict:
        """Get API source status."""
        try:
            if source_id not in self.active_connections:
                return {
                    'success': False,
                    'status': 'not_found',
                    'message': 'Source not found'
                }
            
            connection_info = self.active_connections[source_id]
            api_config = connection_info['config']
            
            # Test connection
            test_result = self._test_api_connection(api_config)
            status = 'connected' if test_result['success'] else 'error'
            
            return {
                'success': True,
                'status': status,
                'api_type': api_config.api_type.value,
                'created_at': connection_info['created_at'],
                'last_successful_request': connection_info['last_successful_request'],
                'request_count': connection_info['request_count'],
                'error_count': connection_info['error_count'],
                'monitoring_active': source_id in self.monitoring_threads,
                'last_update': self.last_update.get(source_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting source status: {e}")
            return {
                'success': False,
                'status': 'error',
                'message': str(e)
            }
    
    def get_all_sources(self) -> Dict:
        """Get all active API sources."""
        try:
            sources = {}
            
            for source_id, connection_info in self.active_connections.items():
                status = self.get_source_status(source_id)
                sources[source_id] = {
                    'api_type': connection_info['config'].api_type.value,
                    'created_at': connection_info['created_at'],
                    'status': status.get('status', 'unknown'),
                    'monitoring_active': source_id in self.monitoring_threads
                }
            
            return {
                'success': True,
                'sources': sources,
                'count': len(sources)
            }
            
        except Exception as e:
            logger.error(f"Error getting all sources: {e}")
            return {
                'success': False,
                'message': str(e)
            }

# Global instance
api_manager = APIManager()
