"""
Real-time monitoring module for customer support analytics.
Handles live data updates, performance monitoring, and alert system.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta
import time
import threading
import queue
import warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTimeMonitor:
    """Handles real-time monitoring and live updates for customer support analytics."""
    
    def __init__(self):
        """Initialize the real-time monitor."""
        self.monitoring_active = False
        self.update_interval = 30  # seconds
        self.alert_queue = queue.Queue()
        self.metrics_cache = {}
        self.last_update = None
        
        # Alert thresholds
        self.alert_thresholds = {
            'response_time_high': 60,  # minutes
            'sla_breach_rate': 0.1,   # 10%
            'sentiment_low': -0.2,    # negative sentiment threshold
            'volume_spike': 2.0        # 2x normal volume
        }
        
        logger.info("Real-time monitor initialized")
    
    def start_monitoring(self, data_source=None):
        """Start real-time monitoring."""
        try:
            self.monitoring_active = True
            self.data_source = data_source
            
            # Start monitoring thread
            monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            monitor_thread.start()
            
            logger.info("Real-time monitoring started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            return False
    
    def stop_monitoring(self):
        """Stop real-time monitoring."""
        self.monitoring_active = False
        logger.info("Real-time monitoring stopped")
    
    def update_metrics(self, new_data: pd.DataFrame):
        """Update metrics with new data."""
        try:
            current_time = datetime.now()
            
            # Calculate current metrics
            metrics = self._calculate_current_metrics(new_data)
            
            # Update cache
            self.metrics_cache[current_time] = metrics
            self.last_update = current_time
            
            # Check for alerts
            self._check_alerts(metrics)
            
            # Clean old cache entries (keep last hour)
            self._clean_cache()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
            return {}
    
    def get_live_dashboard_data(self) -> Dict:
        """Get current dashboard data for live updates."""
        try:
            if not self.metrics_cache:
                return {'status': 'no_data', 'message': 'No metrics available'}
            
            # Get latest metrics
            latest_time = max(self.metrics_cache.keys())
            latest_metrics = self.metrics_cache[latest_time]
            
            # Calculate trends
            trends = self._calculate_trends()
            
            # Get pending alerts
            alerts = self._get_pending_alerts()
            
            return {
                'status': 'active',
                'last_update': latest_time.isoformat(),
                'metrics': latest_metrics,
                'trends': trends,
                'alerts': alerts,
                'monitoring_active': self.monitoring_active
            }
            
        except Exception as e:
            logger.error(f"Error getting live dashboard data: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def check_alerts(self, metrics: Dict):
        """Check for alert conditions."""
        try:
            alerts = []
            
            # Response time alerts
            if 'median_response_time' in metrics:
                rt = metrics['median_response_time']
                if rt > self.alert_thresholds['response_time_high']:
                    alerts.append({
                        'type': 'response_time_high',
                        'severity': 'high',
                        'message': f'Response time ({rt:.1f} min) exceeds threshold ({self.alert_thresholds["response_time_high"]} min)',
                        'timestamp': datetime.now().isoformat()
                    })
            
            # SLA breach alerts
            if 'sla_breach_rate' in metrics:
                breach_rate = metrics['sla_breach_rate']
                if breach_rate > self.alert_thresholds['sla_breach_rate']:
                    alerts.append({
                        'type': 'sla_breach',
                        'severity': 'high',
                        'message': f'SLA breach rate ({breach_rate:.1%}) exceeds threshold ({self.alert_thresholds["sla_breach_rate"]:.1%})',
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Sentiment alerts
            if 'average_sentiment' in metrics:
                sentiment = metrics['average_sentiment']
                if sentiment < self.alert_thresholds['sentiment_low']:
                    alerts.append({
                        'type': 'sentiment_low',
                        'severity': 'medium',
                        'message': f'Customer sentiment ({sentiment:.3f}) is below threshold ({self.alert_thresholds["sentiment_low"]})',
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Volume spike alerts
            if 'current_volume' in metrics and 'normal_volume' in metrics:
                volume_ratio = metrics['current_volume'] / metrics['normal_volume']
                if volume_ratio > self.alert_thresholds['volume_spike']:
                    alerts.append({
                        'type': 'volume_spike',
                        'severity': 'medium',
                        'message': f'Ticket volume spike detected ({volume_ratio:.1f}x normal)',
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Add alerts to queue
            for alert in alerts:
                self.alert_queue.put(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
            return []
    
    def get_alert_history(self, limit: int = 50) -> List[Dict]:
        """Get recent alert history."""
        try:
            alerts = []
            temp_queue = queue.Queue()
            
            # Extract alerts from queue
            while not self.alert_queue.empty():
                alert = self.alert_queue.get()
                alerts.append(alert)
                temp_queue.put(alert)
            
            # Put alerts back in queue
            while not temp_queue.empty():
                self.alert_queue.put(temp_queue.get())
            
            # Sort by timestamp and limit
            alerts.sort(key=lambda x: x['timestamp'], reverse=True)
            return alerts[:limit]
            
        except Exception as e:
            logger.error(f"Error getting alert history: {e}")
            return []
    
    def set_alert_threshold(self, alert_type: str, threshold: float):
        """Set alert threshold for a specific metric."""
        try:
            if alert_type in self.alert_thresholds:
                self.alert_thresholds[alert_type] = threshold
                logger.info(f"Alert threshold for {alert_type} set to {threshold}")
                return True
            else:
                logger.warning(f"Unknown alert type: {alert_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting alert threshold: {e}")
            return False
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Update metrics if data source is available
                if hasattr(self, 'data_source') and self.data_source is not None:
                    current_data = self._get_current_data()
                    if not current_data.empty:
                        self.update_metrics(current_data)
                
                # Sleep for update interval
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.update_interval)
    
    def _calculate_current_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate current metrics from data."""
        try:
            metrics = {}
            
            # Response time metrics
            if 'response_time_minutes' in data.columns:
                rt_data = data['response_time_minutes'].dropna()
                if len(rt_data) > 0:
                    metrics['median_response_time'] = rt_data.median()
                    metrics['average_response_time'] = rt_data.mean()
                    metrics['sla_breach_rate'] = (rt_data > 60).mean()
                    metrics['response_time_count'] = len(rt_data)
            
            # Sentiment metrics
            if 'combined_score' in data.columns:
                sentiment_data = data['combined_score'].dropna()
                if len(sentiment_data) > 0:
                    metrics['average_sentiment'] = sentiment_data.mean()
                    metrics['positive_rate'] = (sentiment_data > 0.05).mean()
                    metrics['negative_rate'] = (sentiment_data < -0.05).mean()
                    metrics['sentiment_count'] = len(sentiment_data)
            
            # Volume metrics
            if 'created_at' in data.columns:
                current_time = datetime.now()
                last_hour = current_time - timedelta(hours=1)
                
                # Filter data from last hour
                data['created_at'] = pd.to_datetime(data['created_at'])
                recent_data = data[data['created_at'] >= last_hour]
                
                metrics['current_volume'] = len(recent_data)
                metrics['normal_volume'] = len(data) / max(1, (data['created_at'].max() - data['created_at'].min()).total_seconds() / 3600)
            
            # Team metrics
            if 'team' in data.columns:
                team_counts = data['team'].value_counts()
                metrics['team_distribution'] = team_counts.to_dict()
                metrics['active_teams'] = len(team_counts)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating current metrics: {e}")
            return {}
    
    def _calculate_trends(self) -> Dict:
        """Calculate trends from cached metrics."""
        try:
            if len(self.metrics_cache) < 2:
                return {'status': 'insufficient_data'}
            
            # Get recent metrics (last 5 data points)
            recent_times = sorted(self.metrics_cache.keys())[-5:]
            recent_metrics = [self.metrics_cache[time] for time in recent_times]
            
            trends = {}
            
            # Calculate trends for key metrics
            for metric in ['median_response_time', 'average_sentiment', 'current_volume']:
                values = []
                for metrics in recent_metrics:
                    if metric in metrics:
                        values.append(metrics[metric])
                
                if len(values) >= 2:
                    # Simple trend calculation
                    if values[-1] > values[0]:
                        trends[metric] = 'increasing'
                    elif values[-1] < values[0]:
                        trends[metric] = 'decreasing'
                    else:
                        trends[metric] = 'stable'
            
            return trends
            
        except Exception as e:
            logger.error(f"Error calculating trends: {e}")
            return {'status': 'error'}
    
    def _check_alerts(self, metrics: Dict):
        """Check for alert conditions."""
        try:
            alerts = self.check_alerts(metrics)
            
            # Log alerts
            for alert in alerts:
                logger.warning(f"ALERT: {alert['message']}")
                
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    def _get_pending_alerts(self) -> List[Dict]:
        """Get pending alerts from queue."""
        try:
            alerts = []
            temp_queue = queue.Queue()
            
            # Extract alerts from queue
            while not self.alert_queue.empty():
                alert = self.alert_queue.get()
                alerts.append(alert)
                temp_queue.put(alert)
            
            # Put alerts back in queue
            while not temp_queue.empty():
                self.alert_queue.put(temp_queue.get())
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting pending alerts: {e}")
            return []
    
    def _get_current_data(self) -> pd.DataFrame:
        """Get current data from data source."""
        try:
            if hasattr(self.data_source, 'get_current_data'):
                return self.data_source.get_current_data()
            else:
                # Return empty DataFrame if no data source
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error getting current data: {e}")
            return pd.DataFrame()
    
    def _clean_cache(self):
        """Clean old entries from metrics cache."""
        try:
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(hours=1)
            
            # Remove old entries
            old_keys = [key for key in self.metrics_cache.keys() if key < cutoff_time]
            for key in old_keys:
                del self.metrics_cache[key]
                
        except Exception as e:
            logger.error(f"Error cleaning cache: {e}")


class AlertSystem:
    """Handles alert management and notification system."""
    
    def __init__(self):
        """Initialize the alert system."""
        self.alert_rules = {}
        self.notification_channels = []
        self.alert_history = []
        
        logger.info("Alert system initialized")
    
    def create_alert_rule(self, rule: Dict):
        """Create a new alert rule."""
        try:
            rule_id = rule.get('id', f"rule_{len(self.alert_rules)}")
            self.alert_rules[rule_id] = rule
            logger.info(f"Alert rule created: {rule_id}")
            return rule_id
            
        except Exception as e:
            logger.error(f"Error creating alert rule: {e}")
            return None
    
    def check_sla_alerts(self, response_times: pd.Series):
        """Check for SLA breach alerts."""
        try:
            alerts = []
            
            # Calculate SLA breach rate
            breach_rate = (response_times > 60).mean()
            
            if breach_rate > 0.1:  # 10% threshold
                alert = {
                    'type': 'sla_breach',
                    'severity': 'high',
                    'message': f'SLA breach rate: {breach_rate:.1%}',
                    'timestamp': datetime.now().isoformat(),
                    'metric_value': breach_rate,
                    'threshold': 0.1
                }
                alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking SLA alerts: {e}")
            return []
    
    def check_performance_alerts(self, metrics: Dict):
        """Check for performance threshold alerts."""
        try:
            alerts = []
            
            # Response time alerts
            if 'median_response_time' in metrics:
                rt = metrics['median_response_time']
                if rt > 60:  # 60 minutes threshold
                    alert = {
                        'type': 'response_time_high',
                        'severity': 'high',
                        'message': f'High response time: {rt:.1f} minutes',
                        'timestamp': datetime.now().isoformat(),
                        'metric_value': rt,
                        'threshold': 60
                    }
                    alerts.append(alert)
            
            # Sentiment alerts
            if 'average_sentiment' in metrics:
                sentiment = metrics['average_sentiment']
                if sentiment < -0.2:  # Negative sentiment threshold
                    alert = {
                        'type': 'sentiment_low',
                        'severity': 'medium',
                        'message': f'Low customer sentiment: {sentiment:.3f}',
                        'timestamp': datetime.now().isoformat(),
                        'metric_value': sentiment,
                        'threshold': -0.2
                    }
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking performance alerts: {e}")
            return []
    
    def send_alert(self, alert: Dict):
        """Send alert notification."""
        try:
            # Add to alert history
            self.alert_history.append(alert)
            
            # Log alert
            logger.warning(f"ALERT SENT: {alert['message']}")
            
            # Send to notification channels
            for channel in self.notification_channels:
                try:
                    channel.send_alert(alert)
                except Exception as e:
                    logger.error(f"Error sending alert to channel: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
            return False
    
    def add_notification_channel(self, channel):
        """Add a notification channel."""
        try:
            self.notification_channels.append(channel)
            logger.info(f"Notification channel added: {type(channel).__name__}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding notification channel: {e}")
            return False
    
    def get_alert_statistics(self) -> Dict:
        """Get alert statistics."""
        try:
            if not self.alert_history:
                return {'total_alerts': 0}
            
            # Calculate statistics
            total_alerts = len(self.alert_history)
            alert_types = {}
            severity_counts = {}
            
            for alert in self.alert_history:
                alert_type = alert.get('type', 'unknown')
                severity = alert.get('severity', 'unknown')
                
                alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            return {
                'total_alerts': total_alerts,
                'alert_types': alert_types,
                'severity_distribution': severity_counts,
                'last_alert': self.alert_history[-1]['timestamp'] if self.alert_history else None
            }
            
        except Exception as e:
            logger.error(f"Error getting alert statistics: {e}")
            return {'error': str(e)}


class PerformanceMonitor:
    """Handles application performance monitoring."""
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.metrics = {}
        self.start_time = datetime.now()
        
        logger.info("Performance monitor initialized")
    
    def record_metric(self, metric_name: str, value: float, timestamp: datetime = None):
        """Record a performance metric."""
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            if metric_name not in self.metrics:
                self.metrics[metric_name] = []
            
            self.metrics[metric_name].append({
                'value': value,
                'timestamp': timestamp
            })
            
        except Exception as e:
            logger.error(f"Error recording metric: {e}")
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary."""
        try:
            summary = {
                'uptime': (datetime.now() - self.start_time).total_seconds(),
                'metrics': {}
            }
            
            for metric_name, values in self.metrics.items():
                if values:
                    metric_values = [v['value'] for v in values]
                    summary['metrics'][metric_name] = {
                        'count': len(metric_values),
                        'average': np.mean(metric_values),
                        'min': np.min(metric_values),
                        'max': np.max(metric_values),
                        'latest': metric_values[-1] if metric_values else None
                    }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {'error': str(e)}
    
    def get_system_health(self) -> Dict:
        """Get system health status."""
        try:
            health = {
                'status': 'healthy',
                'uptime': (datetime.now() - self.start_time).total_seconds(),
                'checks': {}
            }
            
            # Check if metrics are being recorded
            if self.metrics:
                health['checks']['metrics_recording'] = 'healthy'
            else:
                health['checks']['metrics_recording'] = 'warning'
                health['status'] = 'degraded'
            
            # Check for recent activity
            recent_activity = False
            for metric_values in self.metrics.values():
                if metric_values:
                    latest_time = max(v['timestamp'] for v in metric_values)
                    if (datetime.now() - latest_time).total_seconds() < 300:  # 5 minutes
                        recent_activity = True
                        break
            
            if recent_activity:
                health['checks']['recent_activity'] = 'healthy'
            else:
                health['checks']['recent_activity'] = 'warning'
                health['status'] = 'degraded'
            
            return health
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {'status': 'error', 'message': str(e)}
