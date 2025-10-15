"""
Real-Time Data Manager module for customer support analytics.
Coordinates multiple data sources and provides unified real-time data access.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
import logging
from datetime import datetime, timedelta
import threading
import time
import queue
from dataclasses import dataclass
from enum import Enum
import json

# Import our data source managers
try:
    from database_connector import db_connector
    from api_manager import api_manager, APIConfig, APIType
    from websocket_manager import ws_manager, WebSocketConfig, WebSocketType
    DATA_SOURCES_AVAILABLE = True
except ImportError:
    DATA_SOURCES_AVAILABLE = False
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Data source managers not available")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSourceType(Enum):
    """Data source types."""
    DATABASE = "database"
    API = "api"
    WEBSOCKET = "websocket"
    CSV = "csv"
    TWITTER = "twitter"

@dataclass
class DataSourceConfig:
    """Data source configuration."""
    source_type: DataSourceType
    source_id: str
    config: Dict[str, Any]
    refresh_interval: int = 60
    enabled: bool = True
    priority: int = 1  # Higher number = higher priority

class RealTimeDataManager:
    """Manages multiple data sources and provides unified real-time data access."""
    
    def __init__(self):
        """Initialize the real-time data manager."""
        self.data_sources = {}
        self.data_cache = {}
        self.update_callbacks = {}
        self.monitoring_threads = {}
        self.alert_queue = queue.Queue()
        self.last_update = {}
        self.running = False
        
        # Data aggregation settings
        self.aggregation_window = 300  # 5 minutes
        self.max_cache_size = 10000  # Maximum records per source
        
        # Alert thresholds
        self.alert_thresholds = {
            'response_time_high': 60,  # minutes
            'sla_breach_rate': 0.1,   # 10%
            'sentiment_low': -0.2,    # negative sentiment threshold
            'volume_spike': 2.0,       # 2x normal volume
            'error_rate': 0.05         # 5% error rate
        }
        
        logger.info("Real-Time Data Manager initialized")
    
    def add_data_source(self, config: DataSourceConfig) -> Dict:
        """
        Add a new data source.
        
        Args:
            config: Data source configuration
            
        Returns:
            Dict with addition status
        """
        try:
            if not DATA_SOURCES_AVAILABLE:
                return {
                    'success': False,
                    'message': "Data source managers not available"
                }
            
            source_id = config.source_id
            
            # Validate configuration
            validation_result = self._validate_config(config)
            if not validation_result['success']:
                return validation_result
            
            # Add to data sources
            self.data_sources[source_id] = config
            
            # Initialize cache
            self.data_cache[source_id] = {
                'data': pd.DataFrame(),
                'timestamp': None,
                'count': 0,
                'errors': 0
            }
            
            # Connect to data source
            connection_result = self._connect_data_source(config)
            
            if connection_result['success']:
                logger.info(f"Added data source: {source_id} ({config.source_type.value})")
                
                return {
                    'success': True,
                    'source_id': source_id,
                    'message': f"Successfully added {config.source_type.value} data source"
                }
            else:
                # Remove from data sources if connection failed
                del self.data_sources[source_id]
                del self.data_cache[source_id]
                
                return connection_result
                
        except Exception as e:
            logger.error(f"Error adding data source: {e}")
            return {
                'success': False,
                'message': f"Failed to add data source: {str(e)}"
            }
    
    def remove_data_source(self, source_id: str) -> Dict:
        """
        Remove a data source.
        
        Args:
            source_id: ID of the data source to remove
            
        Returns:
            Dict with removal status
        """
        try:
            if source_id not in self.data_sources:
                return {
                    'success': False,
                    'message': f"Data source not found: {source_id}"
                }
            
            config = self.data_sources[source_id]
            
            # Disconnect from data source
            disconnect_result = self._disconnect_data_source(config)
            
            # Stop monitoring if active
            if source_id in self.monitoring_threads:
                self.stop_monitoring(source_id)
            
            # Remove from collections
            del self.data_sources[source_id]
            if source_id in self.data_cache:
                del self.data_cache[source_id]
            if source_id in self.update_callbacks:
                del self.update_callbacks[source_id]
            if source_id in self.last_update:
                del self.last_update[source_id]
            
            logger.info(f"Removed data source: {source_id}")
            
            return {
                'success': True,
                'message': f"Successfully removed data source: {source_id}"
            }
            
        except Exception as e:
            logger.error(f"Error removing data source: {e}")
            return {
                'success': False,
                'message': f"Failed to remove data source: {str(e)}"
            }
    
    def start_monitoring(self, source_id: str = None, callback: Optional[Callable] = None) -> Dict:
        """
        Start monitoring data sources.
        
        Args:
            source_id: Specific source to monitor (None for all)
            callback: Callback function for data updates
            
        Returns:
            Dict with monitoring status
        """
        try:
            if not DATA_SOURCES_AVAILABLE:
                return {
                    'success': False,
                    'message': "Data source managers not available"
                }
            
            sources_to_monitor = []
            
            if source_id:
                if source_id in self.data_sources:
                    sources_to_monitor = [source_id]
                else:
                    return {
                        'success': False,
                        'message': f"Data source not found: {source_id}"
                    }
            else:
                sources_to_monitor = list(self.data_sources.keys())
            
            if not sources_to_monitor:
                return {
                    'success': False,
                    'message': "No data sources to monitor"
                }
            
            # Start monitoring for each source
            for src_id in sources_to_monitor:
                if src_id not in self.monitoring_threads:
                    config = self.data_sources[src_id]
                    
                    # Set callback
                    if callback:
                        self.update_callbacks[src_id] = callback
                    
                    # Start monitoring thread
                    stop_event = threading.Event()
                    monitor_thread = threading.Thread(
                        target=self._monitoring_loop,
                        args=(src_id, stop_event),
                        daemon=True
                    )
                    
                    self.monitoring_threads[src_id] = {
                        'thread': monitor_thread,
                        'stop': stop_event,
                        'config': config
                    }
                    
                    monitor_thread.start()
            
            self.running = True
            
            logger.info(f"Started monitoring {len(sources_to_monitor)} data sources")
            
            return {
                'success': True,
                'message': f"Started monitoring {len(sources_to_monitor)} data sources",
                'sources': sources_to_monitor
            }
            
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            return {
                'success': False,
                'message': f"Failed to start monitoring: {str(e)}"
            }
    
    def stop_monitoring(self, source_id: str = None) -> Dict:
        """
        Stop monitoring data sources.
        
        Args:
            source_id: Specific source to stop (None for all)
            
        Returns:
            Dict with stop status
        """
        try:
            sources_to_stop = []
            
            if source_id:
                if source_id in self.monitoring_threads:
                    sources_to_stop = [source_id]
                else:
                    return {
                        'success': False,
                        'message': f"No active monitoring found for {source_id}"
                    }
            else:
                sources_to_stop = list(self.monitoring_threads.keys())
            
            # Stop monitoring for each source
            for src_id in sources_to_stop:
                if src_id in self.monitoring_threads:
                    self.monitoring_threads[src_id]['stop'].set()
                    del self.monitoring_threads[src_id]
            
            if not self.monitoring_threads:
                self.running = False
            
            logger.info(f"Stopped monitoring {len(sources_to_stop)} data sources")
            
            return {
                'success': True,
                'message': f"Stopped monitoring {len(sources_to_stop)} data sources",
                'sources': sources_to_stop
            }
            
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
            return {
                'success': False,
                'message': f"Failed to stop monitoring: {str(e)}"
            }
    
    def get_latest_data(self, source_id: str = None) -> Dict:
        """
        Get latest data from data sources.
        
        Args:
            source_id: Specific source to get data from (None for all)
            
        Returns:
            Dict with data
        """
        try:
            if source_id:
                if source_id not in self.data_cache:
                    return {
                        'success': False,
                        'message': f"Data source not found: {source_id}"
                    }
                
                cache_info = self.data_cache[source_id]
                
                return {
                    'success': True,
                    'data': cache_info['data'],
                    'timestamp': cache_info['timestamp'],
                    'count': cache_info['count'],
                    'source_id': source_id
                }
            else:
                # Get data from all sources
                all_data = {}
                
                for src_id, cache_info in self.data_cache.items():
                    all_data[src_id] = {
                        'data': cache_info['data'],
                        'timestamp': cache_info['timestamp'],
                        'count': cache_info['count']
                    }
                
                return {
                    'success': True,
                    'data': all_data,
                    'sources': list(all_data.keys())
                }
                
        except Exception as e:
            logger.error(f"Error getting latest data: {e}")
            return {
                'success': False,
                'message': f"Failed to get latest data: {str(e)}"
            }
    
    def get_aggregated_data(self, time_window: int = None) -> Dict:
        """
        Get aggregated data from all sources.
        
        Args:
            time_window: Time window in seconds for aggregation
            
        Returns:
            Dict with aggregated data
        """
        try:
            if not time_window:
                time_window = self.aggregation_window
            
            cutoff_time = datetime.now() - timedelta(seconds=time_window)
            aggregated_data = []
            
            for src_id, cache_info in self.data_cache.items():
                if cache_info['timestamp'] and cache_info['timestamp'] >= cutoff_time:
                    data = cache_info['data']
                    if not data.empty:
                        # Add source identifier
                        data_copy = data.copy()
                        data_copy['data_source'] = src_id
                        aggregated_data.append(data_copy)
            
            if aggregated_data:
                # Combine all data
                combined_data = pd.concat(aggregated_data, ignore_index=True)
                
                # Remove duplicates based on ticket_id and timestamp
                if 'ticket_id' in combined_data.columns and 'created_at' in combined_data.columns:
                    combined_data = combined_data.drop_duplicates(
                        subset=['ticket_id', 'created_at'], 
                        keep='last'
                    )
                
                logger.info(f"Aggregated {len(combined_data)} records from {len(aggregated_data)} sources")
                
                return {
                    'success': True,
                    'data': combined_data,
                    'row_count': len(combined_data),
                    'sources': len(aggregated_data),
                    'time_window': time_window
                }
            else:
                return {
                    'success': True,
                    'data': pd.DataFrame(),
                    'row_count': 0,
                    'sources': 0,
                    'time_window': time_window
                }
                
        except Exception as e:
            logger.error(f"Error getting aggregated data: {e}")
            return {
                'success': False,
                'message': f"Failed to get aggregated data: {str(e)}"
            }
    
    def _validate_config(self, config: DataSourceConfig) -> Dict:
        """Validate data source configuration."""
        try:
            if not config.source_id:
                return {
                    'success': False,
                    'message': "Source ID is required"
                }
            
            if config.source_type not in DataSourceType:
                return {
                    'success': False,
                    'message': f"Unsupported source type: {config.source_type}"
                }
            
            if not config.config:
                return {
                    'success': False,
                    'message': "Source configuration is required"
                }
            
            return {'success': True}
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Configuration validation failed: {str(e)}"
            }
    
    def _connect_data_source(self, config: DataSourceConfig) -> Dict:
        """Connect to a data source."""
        try:
            source_id = config.source_id
            source_type = config.source_type
            
            if source_type == DataSourceType.DATABASE:
                return self._connect_database(config)
            elif source_type == DataSourceType.API:
                return self._connect_api(config)
            elif source_type == DataSourceType.WEBSOCKET:
                return self._connect_websocket(config)
            else:
                return {
                    'success': False,
                    'message': f"Connection not implemented for {source_type.value}"
                }
                
        except Exception as e:
            logger.error(f"Error connecting data source: {e}")
            return {
                'success': False,
                'message': f"Connection failed: {str(e)}"
            }
    
    def _connect_database(self, config: DataSourceConfig) -> Dict:
        """Connect to database."""
        try:
            db_config = config.config
            connection_result = db_connector.connect(
                db_config['type'],
                db_config['params']
            )
            
            if connection_result['success']:
                # Store connection ID
                config.config['connection_id'] = connection_result['connection_id']
                
                return {
                    'success': True,
                    'message': "Database connected successfully"
                }
            else:
                return connection_result
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Database connection failed: {str(e)}"
            }
    
    def _connect_api(self, config: DataSourceConfig) -> Dict:
        """Connect to API."""
        try:
            api_config = config.config
            
            # Create API configuration
            api_config_obj = APIConfig(
                api_type=APIType(api_config['type']),
                base_url=api_config['base_url'],
                credentials=api_config['credentials'],
                headers=api_config.get('headers', {}),
                rate_limit=api_config.get('rate_limit', 100),
                timeout=api_config.get('timeout', 30),
                refresh_interval=config.refresh_interval
            )
            
            add_result = api_manager.add_api_source(config.source_id, api_config_obj)
            
            return add_result
            
        except Exception as e:
            return {
                'success': False,
                'message': f"API connection failed: {str(e)}"
            }
    
    def _connect_websocket(self, config: DataSourceConfig) -> Dict:
        """Connect to WebSocket."""
        try:
            ws_config = config.config
            
            # Create WebSocket configuration
            ws_config_obj = WebSocketConfig(
                ws_type=WebSocketType(ws_config['type']),
                url=ws_config['url'],
                headers=ws_config.get('headers'),
                auth_token=ws_config.get('auth_token'),
                heartbeat_interval=ws_config.get('heartbeat_interval', 30),
                reconnect_interval=ws_config.get('reconnect_interval', 5)
            )
            
            connect_result = ws_manager.connect(config.source_id, ws_config_obj)
            
            if connect_result['success']:
                # Subscribe to messages
                subscribe_result = ws_manager.subscribe(
                    config.source_id,
                    self._websocket_callback
                )
                
                return subscribe_result
            else:
                return connect_result
                
        except Exception as e:
            return {
                'success': False,
                'message': f"WebSocket connection failed: {str(e)}"
            }
    
    def _disconnect_data_source(self, config: DataSourceConfig) -> Dict:
        """Disconnect from a data source."""
        try:
            source_type = config.source_type
            source_id = config.source_id
            
            if source_type == DataSourceType.DATABASE:
                if 'connection_id' in config.config:
                    return db_connector.disconnect(config.config['connection_id'])
            elif source_type == DataSourceType.API:
                return api_manager.remove_api_source(source_id)
            elif source_type == DataSourceType.WEBSOCKET:
                return ws_manager.disconnect(source_id)
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error disconnecting data source: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def _monitoring_loop(self, source_id: str, stop_event: threading.Event):
        """Monitoring loop for a data source."""
        try:
            config = self.data_sources[source_id]
            source_type = config.source_type
            
            while not stop_event.is_set():
                try:
                    # Get data based on source type
                    if source_type == DataSourceType.DATABASE:
                        data_result = self._get_database_data(source_id)
                    elif source_type == DataSourceType.API:
                        data_result = self._get_api_data(source_id)
                    elif source_type == DataSourceType.WEBSOCKET:
                        data_result = self._get_websocket_data(source_id)
                    else:
                        data_result = {'success': False, 'message': 'Unsupported source type'}
                    
                    if data_result['success']:
                        # Update cache
                        self._update_cache(source_id, data_result['data'])
                        
                        # Check for alerts
                        self._check_alerts(source_id, data_result['data'])
                        
                        # Call callback if set
                        if source_id in self.update_callbacks:
                            try:
                                self.update_callbacks[source_id](source_id, data_result['data'])
                            except Exception as e:
                                logger.error(f"Error in update callback: {e}")
                    
                    # Wait for next update
                    stop_event.wait(config.refresh_interval)
                    
                except Exception as e:
                    logger.error(f"Error in monitoring loop for {source_id}: {e}")
                    self.data_cache[source_id]['errors'] += 1
                    stop_event.wait(60)  # Wait longer on error
                    
        except Exception as e:
            logger.error(f"Monitoring loop error for {source_id}: {e}")
    
    def _get_database_data(self, source_id: str) -> Dict:
        """Get data from database."""
        try:
            config = self.data_sources[source_id]
            connection_id = config.config['connection_id']
            
            data_result = db_connector.get_support_data(
                connection_id,
                config.config.get('table_name', 'support_tickets'),
                limit=config.config.get('limit', 1000)
            )
            
            return data_result
            
        except Exception as e:
            logger.error(f"Error getting database data: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def _get_api_data(self, source_id: str) -> Dict:
        """Get data from API."""
        try:
            data_result = api_manager.get_real_time_data(source_id)
            return data_result
            
        except Exception as e:
            logger.error(f"Error getting API data: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def _get_websocket_data(self, source_id: str) -> Dict:
        """Get data from WebSocket."""
        try:
            messages_result = ws_manager.get_latest_messages(source_id, limit=100)
            
            if messages_result['success'] and messages_result['messages']:
                # Convert messages to DataFrame
                messages = messages_result['messages']
                df = pd.DataFrame(messages)
                
                return {
                    'success': True,
                    'data': df,
                    'row_count': len(df)
                }
            else:
                return {
                    'success': True,
                    'data': pd.DataFrame(),
                    'row_count': 0
                }
                
        except Exception as e:
            logger.error(f"Error getting WebSocket data: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def _websocket_callback(self, connection_id: str, data: Dict):
        """Callback for WebSocket messages."""
        try:
            # Convert to DataFrame
            df = pd.DataFrame([data])
            
            # Update cache immediately
            self._update_cache(connection_id, df)
            
            # Check for alerts
            self._check_alerts(connection_id, df)
            
            # Call update callback if set
            if connection_id in self.update_callbacks:
                try:
                    self.update_callbacks[connection_id](connection_id, df)
                except Exception as e:
                    logger.error(f"Error in WebSocket callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error in WebSocket callback: {e}")
    
    def _update_cache(self, source_id: str, data: pd.DataFrame):
        """Update data cache."""
        try:
            if source_id not in self.data_cache:
                return
            
            cache_info = self.data_cache[source_id]
            
            # Limit cache size
            if len(data) > self.max_cache_size:
                data = data.tail(self.max_cache_size)
            
            # Update cache
            cache_info['data'] = data
            cache_info['timestamp'] = datetime.now()
            cache_info['count'] = len(data)
            
            self.last_update[source_id] = datetime.now()
            
            logger.debug(f"Updated cache for {source_id}: {len(data)} records")
            
        except Exception as e:
            logger.error(f"Error updating cache: {e}")
    
    def _check_alerts(self, source_id: str, data: pd.DataFrame):
        """Check for alert conditions."""
        try:
            if data.empty:
                return
            
            alerts = []
            
            # Check response time alerts
            if 'response_time_minutes' in data.columns:
                high_response_times = data[data['response_time_minutes'] > self.alert_thresholds['response_time_high']]
                if len(high_response_times) > 0:
                    alerts.append({
                        'type': 'warning',
                        'message': f"High response times detected: {len(high_response_times)} tickets",
                        'source_id': source_id,
                        'timestamp': datetime.now()
                    })
            
            # Check sentiment alerts
            if 'combined_score' in data.columns:
                negative_sentiment = data[data['combined_score'] < self.alert_thresholds['sentiment_low']]
                if len(negative_sentiment) > 0:
                    alerts.append({
                        'type': 'warning',
                        'message': f"Negative sentiment detected: {len(negative_sentiment)} messages",
                        'source_id': source_id,
                        'timestamp': datetime.now()
                    })
            
            # Add alerts to queue
            for alert in alerts:
                self.alert_queue.put(alert)
                logger.warning(f"ALERT: {alert['message']}")
                
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    def get_pending_alerts(self) -> List[Dict]:
        """Get pending alerts."""
        try:
            alerts = []
            
            while not self.alert_queue.empty():
                try:
                    alert = self.alert_queue.get_nowait()
                    alerts.append(alert)
                except queue.Empty:
                    break
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting pending alerts: {e}")
            return []
    
    def get_manager_status(self) -> Dict:
        """Get real-time data manager status."""
        try:
            status = {
                'running': self.running,
                'data_sources': len(self.data_sources),
                'monitoring_active': len(self.monitoring_threads),
                'total_records': sum(cache['count'] for cache in self.data_cache.values()),
                'total_errors': sum(cache['errors'] for cache in self.data_cache.values()),
                'pending_alerts': self.alert_queue.qsize(),
                'last_update': max(self.last_update.values()) if self.last_update else None
            }
            
            return {
                'success': True,
                'status': status
            }
            
        except Exception as e:
            logger.error(f"Error getting manager status: {e}")
            return {
                'success': False,
                'message': str(e)
            }

# Global instance
realtime_manager = RealTimeDataManager()
