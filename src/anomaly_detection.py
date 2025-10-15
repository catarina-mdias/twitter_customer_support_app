"""
Anomaly detection module for customer support analytics.
Handles detection of unusual patterns and outliers in support data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import anomaly detection libraries
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import DBSCAN
    from scipy import stats
    from scipy.signal import find_peaks
    ANOMALY_DETECTION_AVAILABLE = True
except ImportError:
    ANOMALY_DETECTION_AVAILABLE = False
    logging.warning("Anomaly detection libraries not available. Install scikit-learn and scipy.")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Handles anomaly detection and outlier identification in customer support data."""
    
    def __init__(self):
        """Initialize the anomaly detector."""
        self.anomaly_threshold = 0.1  # 10% of data points can be anomalies
        self.z_score_threshold = 2.5  # Z-score threshold for statistical anomalies
        self.isolation_contamination = 0.1  # Expected proportion of anomalies
        
        if not ANOMALY_DETECTION_AVAILABLE:
            logger.warning("Anomaly detection capabilities limited due to missing dependencies")
        
        logger.info("Anomaly detector initialized")
    
    def detect_anomalies(self, df: pd.DataFrame) -> Dict:
        """
        Detect anomalies in customer support data.
        
        Args:
            df: DataFrame with customer support data
            
        Returns:
            Dict: Anomaly detection results
        """
        try:
            anomalies = {}
            
            # Detect response time anomalies
            if 'response_time_minutes' in df.columns:
                rt_anomalies = self._detect_response_time_anomalies(df)
                anomalies['response_time'] = rt_anomalies
            
            # Detect sentiment anomalies
            if 'combined_score' in df.columns:
                sentiment_anomalies = self._detect_sentiment_anomalies(df)
                anomalies['sentiment'] = sentiment_anomalies
            
            # Detect volume anomalies
            if 'created_at' in df.columns:
                volume_anomalies = self._detect_volume_anomalies(df)
                anomalies['volume'] = volume_anomalies
            
            # Detect team performance anomalies
            if 'team' in df.columns:
                team_anomalies = self._detect_team_anomalies(df)
                anomalies['team_performance'] = team_anomalies
            
            # Detect temporal anomalies
            if 'created_at' in df.columns:
                temporal_anomalies = self._detect_temporal_anomalies(df)
                anomalies['temporal'] = temporal_anomalies
            
            # Generate overall anomaly summary
            summary = self._generate_anomaly_summary(anomalies)
            anomalies['summary'] = summary
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return {'error': str(e)}
    
    def _detect_response_time_anomalies(self, df: pd.DataFrame) -> Dict:
        """Detect anomalies in response times."""
        try:
            response_times = df['response_time_minutes'].dropna()
            
            if len(response_times) < 5:
                return {'anomalies': [], 'method': 'insufficient_data'}
            
            anomalies = []
            
            # Method 1: Statistical outliers (Z-score)
            z_scores = np.abs(stats.zscore(response_times))
            statistical_outliers = df[z_scores > self.z_score_threshold].index.tolist()
            
            # Method 2: Isolation Forest (if available)
            isolation_outliers = []
            if ANOMALY_DETECTION_AVAILABLE and len(response_times) >= 10:
                isolation_outliers = self._isolation_forest_detection(response_times)
            
            # Method 3: Percentile-based outliers
            percentile_outliers = self._percentile_based_detection(response_times)
            
            # Combine methods
            all_outliers = list(set(statistical_outliers + isolation_outliers + percentile_outliers))
            
            # Analyze anomaly characteristics
            anomaly_analysis = self._analyze_response_time_anomalies(df, all_outliers)
            
            return {
                'anomalies': all_outliers,
                'count': len(all_outliers),
                'percentage': len(all_outliers) / len(df) * 100,
                'methods': {
                    'statistical': len(statistical_outliers),
                    'isolation_forest': len(isolation_outliers),
                    'percentile': len(percentile_outliers)
                },
                'analysis': anomaly_analysis,
                'severity': self._assess_anomaly_severity(len(all_outliers), len(df))
            }
            
        except Exception as e:
            logger.error(f"Error detecting response time anomalies: {e}")
            return {'anomalies': [], 'method': 'error'}
    
    def _detect_sentiment_anomalies(self, df: pd.DataFrame) -> Dict:
        """Detect anomalies in sentiment scores."""
        try:
            sentiment_scores = df['combined_score'].dropna()
            
            if len(sentiment_scores) < 5:
                return {'anomalies': [], 'method': 'insufficient_data'}
            
            anomalies = []
            
            # Method 1: Extreme sentiment values
            extreme_positive = df[sentiment_scores > 0.8].index.tolist()
            extreme_negative = df[sentiment_scores < -0.8].index.tolist()
            
            # Method 2: Statistical outliers
            z_scores = np.abs(stats.zscore(sentiment_scores))
            statistical_outliers = df[z_scores > self.z_score_threshold].index.tolist()
            
            # Method 3: Sentiment volatility
            if len(sentiment_scores) >= 10:
                volatility_outliers = self._detect_sentiment_volatility(df)
            else:
                volatility_outliers = []
            
            # Combine methods
            all_outliers = list(set(extreme_positive + extreme_negative + statistical_outliers + volatility_outliers))
            
            # Analyze sentiment anomaly patterns
            anomaly_analysis = self._analyze_sentiment_anomalies(df, all_outliers)
            
            return {
                'anomalies': all_outliers,
                'count': len(all_outliers),
                'percentage': len(all_outliers) / len(df) * 100,
                'types': {
                    'extreme_positive': len(extreme_positive),
                    'extreme_negative': len(extreme_negative),
                    'statistical': len(statistical_outliers),
                    'volatility': len(volatility_outliers)
                },
                'analysis': anomaly_analysis,
                'severity': self._assess_anomaly_severity(len(all_outliers), len(df))
            }
            
        except Exception as e:
            logger.error(f"Error detecting sentiment anomalies: {e}")
            return {'anomalies': [], 'method': 'error'}
    
    def _detect_volume_anomalies(self, df: pd.DataFrame) -> Dict:
        """Detect anomalies in ticket volume."""
        try:
            if 'created_at' not in df.columns:
                return {'anomalies': [], 'method': 'no_date_column'}
            
            # Group by date to get daily volumes
            df['date'] = pd.to_datetime(df['created_at']).dt.date
            daily_volumes = df.groupby('date').size()
            
            if len(daily_volumes) < 5:
                return {'anomalies': [], 'method': 'insufficient_data'}
            
            anomalies = []
            
            # Method 1: Statistical outliers in daily volume
            z_scores = np.abs(stats.zscore(daily_volumes))
            volume_outliers = daily_volumes[z_scores > self.z_score_threshold].index.tolist()
            
            # Method 2: Peak detection
            if len(daily_volumes) >= 7:
                peaks = self._detect_volume_peaks(daily_volumes)
                valleys = self._detect_volume_valleys(daily_volumes)
            else:
                peaks = []
                valleys = []
            
            # Method 3: Trend anomalies
            trend_anomalies = self._detect_volume_trend_anomalies(daily_volumes)
            
            # Convert date anomalies back to original indices
            anomaly_indices = []
            for anomaly_date in volume_outliers + peaks + valleys + trend_anomalies:
                date_indices = df[df['date'] == anomaly_date].index.tolist()
                anomaly_indices.extend(date_indices)
            
            # Analyze volume anomaly patterns
            anomaly_analysis = self._analyze_volume_anomalies(daily_volumes, volume_outliers)
            
            return {
                'anomalies': anomaly_indices,
                'count': len(anomaly_indices),
                'percentage': len(anomaly_indices) / len(df) * 100,
                'daily_anomalies': {
                    'statistical': len(volume_outliers),
                    'peaks': len(peaks),
                    'valleys': len(valleys),
                    'trend': len(trend_anomalies)
                },
                'analysis': anomaly_analysis,
                'severity': self._assess_anomaly_severity(len(anomaly_indices), len(df))
            }
            
        except Exception as e:
            logger.error(f"Error detecting volume anomalies: {e}")
            return {'anomalies': [], 'method': 'error'}
    
    def _detect_team_anomalies(self, df: pd.DataFrame) -> Dict:
        """Detect anomalies in team performance."""
        try:
            if 'team' not in df.columns:
                return {'anomalies': [], 'method': 'no_team_column'}
            
            team_anomalies = {}
            
            for team in df['team'].unique():
                team_df = df[df['team'] == team]
                
                if len(team_df) < 5:
                    continue
                
                # Detect team-specific anomalies
                team_anomaly_indices = []
                
                # Response time anomalies for this team
                if 'response_time_minutes' in team_df.columns:
                    rt_anomalies = self._detect_response_time_anomalies(team_df)
                    team_anomaly_indices.extend(rt_anomalies.get('anomalies', []))
                
                # Sentiment anomalies for this team
                if 'combined_score' in team_df.columns:
                    sentiment_anomalies = self._detect_sentiment_anomalies(team_df)
                    team_anomaly_indices.extend(sentiment_anomalies.get('anomalies', []))
                
                # Volume anomalies for this team
                if 'created_at' in team_df.columns:
                    volume_anomalies = self._detect_volume_anomalies(team_df)
                    team_anomaly_indices.extend(volume_anomalies.get('anomalies', []))
                
                if team_anomaly_indices:
                    team_anomalies[team] = {
                        'anomalies': list(set(team_anomaly_indices)),
                        'count': len(set(team_anomaly_indices)),
                        'percentage': len(set(team_anomaly_indices)) / len(team_df) * 100
                    }
            
            # Overall team anomaly analysis
            analysis = self._analyze_team_anomalies(df, team_anomalies)
            
            return {
                'team_anomalies': team_anomalies,
                'analysis': analysis,
                'severity': self._assess_team_anomaly_severity(team_anomalies)
            }
            
        except Exception as e:
            logger.error(f"Error detecting team anomalies: {e}")
            return {'anomalies': [], 'method': 'error'}
    
    def _detect_temporal_anomalies(self, df: pd.DataFrame) -> Dict:
        """Detect temporal anomalies in the data."""
        try:
            if 'created_at' not in df.columns:
                return {'anomalies': [], 'method': 'no_date_column'}
            
            df['datetime'] = pd.to_datetime(df['created_at'])
            df['hour'] = df['datetime'].dt.hour
            df['day_of_week'] = df['datetime'].dt.dayofweek
            
            anomalies = []
            
            # Detect unusual time patterns
            # 1. Unusual hours (outside business hours)
            business_hours = df[(df['hour'] >= 9) & (df['hour'] <= 17)]
            non_business_hours = df[(df['hour'] < 9) | (df['hour'] > 17)]
            
            if len(non_business_hours) > len(df) * 0.3:  # More than 30% outside business hours
                anomalies.extend(non_business_hours.index.tolist())
            
            # 2. Weekend patterns
            weekend_tickets = df[df['day_of_week'].isin([5, 6])]  # Saturday, Sunday
            if len(weekend_tickets) > len(df) * 0.2:  # More than 20% on weekends
                anomalies.extend(weekend_tickets.index.tolist())
            
            # 3. Time clustering anomalies
            clustering_anomalies = self._detect_time_clustering_anomalies(df)
            anomalies.extend(clustering_anomalies)
            
            # Analyze temporal patterns
            analysis = self._analyze_temporal_patterns(df)
            
            return {
                'anomalies': list(set(anomalies)),
                'count': len(set(anomalies)),
                'percentage': len(set(anomalies)) / len(df) * 100,
                'patterns': {
                    'non_business_hours': len(non_business_hours),
                    'weekend_tickets': len(weekend_tickets),
                    'clustering': len(clustering_anomalies)
                },
                'analysis': analysis,
                'severity': self._assess_anomaly_severity(len(set(anomalies)), len(df))
            }
            
        except Exception as e:
            logger.error(f"Error detecting temporal anomalies: {e}")
            return {'anomalies': [], 'method': 'error'}
    
    def _isolation_forest_detection(self, data: pd.Series) -> List[int]:
        """Use Isolation Forest for anomaly detection."""
        try:
            if not ANOMALY_DETECTION_AVAILABLE:
                return []
            
            # Reshape data for sklearn
            X = data.values.reshape(-1, 1)
            
            # Apply Isolation Forest
            iso_forest = IsolationForest(contamination=self.isolation_contamination, random_state=42)
            anomaly_labels = iso_forest.fit_predict(X)
            
            # Get indices of anomalies (-1 indicates anomaly)
            anomaly_indices = data[anomaly_labels == -1].index.tolist()
            
            return anomaly_indices
            
        except Exception as e:
            logger.error(f"Error in Isolation Forest detection: {e}")
            return []
    
    def _percentile_based_detection(self, data: pd.Series) -> List[int]:
        """Detect anomalies using percentile-based method."""
        try:
            # Define percentile thresholds
            lower_threshold = data.quantile(0.05)  # Bottom 5%
            upper_threshold = data.quantile(0.95)  # Top 5%
            
            # Find outliers
            outliers = data[(data < lower_threshold) | (data > upper_threshold)]
            
            return outliers.index.tolist()
            
        except Exception as e:
            logger.error(f"Error in percentile-based detection: {e}")
            return []
    
    def _detect_sentiment_volatility(self, df: pd.DataFrame) -> List[int]:
        """Detect high sentiment volatility."""
        try:
            if 'created_at' not in df.columns or 'combined_score' not in df.columns:
                return []
            
            # Group by date and calculate daily sentiment volatility
            df['date'] = pd.to_datetime(df['created_at']).dt.date
            daily_sentiment = df.groupby('date')['combined_score'].agg(['mean', 'std']).reset_index()
            
            # Find days with high volatility
            high_volatility_days = daily_sentiment[
                daily_sentiment['std'] > daily_sentiment['std'].quantile(0.9)
            ]['date'].tolist()
            
            # Get indices for high volatility days
            volatility_indices = []
            for date in high_volatility_days:
                date_indices = df[df['date'] == date].index.tolist()
                volatility_indices.extend(date_indices)
            
            return volatility_indices
            
        except Exception as e:
            logger.error(f"Error detecting sentiment volatility: {e}")
            return []
    
    def _detect_volume_peaks(self, daily_volumes: pd.Series) -> List:
        """Detect volume peaks using signal processing."""
        try:
            if not ANOMALY_DETECTION_AVAILABLE or len(daily_volumes) < 7:
                return []
            
            # Find peaks in volume data
            volumes_array = daily_volumes.values
            peaks, _ = find_peaks(volumes_array, height=np.mean(volumes_array) + np.std(volumes_array))
            
            # Convert peak indices to dates
            peak_dates = daily_volumes.index[peaks].tolist()
            
            return peak_dates
            
        except Exception as e:
            logger.error(f"Error detecting volume peaks: {e}")
            return []
    
    def _detect_volume_valleys(self, daily_volumes: pd.Series) -> List:
        """Detect volume valleys using signal processing."""
        try:
            if not ANOMALY_DETECTION_AVAILABLE or len(daily_volumes) < 7:
                return []
            
            # Find valleys in volume data (negative peaks)
            volumes_array = -daily_volumes.values  # Invert to find valleys
            valleys, _ = find_peaks(volumes_array, height=np.mean(volumes_array) + np.std(volumes_array))
            
            # Convert valley indices to dates
            valley_dates = daily_volumes.index[valleys].tolist()
            
            return valley_dates
            
        except Exception as e:
            logger.error(f"Error detecting volume valleys: {e}")
            return []
    
    def _detect_volume_trend_anomalies(self, daily_volumes: pd.Series) -> List:
        """Detect anomalies in volume trends."""
        try:
            if len(daily_volumes) < 7:
                return []
            
            # Calculate rolling mean and standard deviation
            rolling_mean = daily_volumes.rolling(window=7, center=True).mean()
            rolling_std = daily_volumes.rolling(window=7, center=True).std()
            
            # Find days where volume deviates significantly from trend
            threshold = rolling_std.mean() * 2
            anomalies = daily_volumes[
                np.abs(daily_volumes - rolling_mean) > threshold
            ].index.tolist()
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting volume trend anomalies: {e}")
            return []
    
    def _detect_time_clustering_anomalies(self, df: pd.DataFrame) -> List[int]:
        """Detect unusual time clustering patterns."""
        try:
            if 'created_at' not in df.columns:
                return []
            
            # Group tickets by hour and detect unusual clustering
            hourly_counts = df.groupby(df['created_at'].dt.hour).size()
            
            # Find hours with unusually high activity
            mean_hourly = hourly_counts.mean()
            std_hourly = hourly_counts.std()
            threshold = mean_hourly + 2 * std_hourly
            
            unusual_hours = hourly_counts[hourly_counts > threshold].index.tolist()
            
            # Get indices for unusual hours
            clustering_indices = []
            for hour in unusual_hours:
                hour_indices = df[df['created_at'].dt.hour == hour].index.tolist()
                clustering_indices.extend(hour_indices)
            
            return clustering_indices
            
        except Exception as e:
            logger.error(f"Error detecting time clustering anomalies: {e}")
            return []
    
    def _analyze_response_time_anomalies(self, df: pd.DataFrame, anomalies: List[int]) -> Dict:
        """Analyze characteristics of response time anomalies."""
        try:
            if not anomalies:
                return {'pattern': 'none', 'severity': 'low'}
            
            anomaly_df = df.loc[anomalies]
            
            analysis = {
                'pattern': 'detected',
                'severity': 'medium',
                'characteristics': {}
            }
            
            if 'team' in anomaly_df.columns:
                team_distribution = anomaly_df['team'].value_counts()
                analysis['characteristics']['team_distribution'] = team_distribution.to_dict()
            
            if 'priority' in anomaly_df.columns:
                priority_distribution = anomaly_df['priority'].value_counts()
                analysis['characteristics']['priority_distribution'] = priority_distribution.to_dict()
            
            # Calculate anomaly severity
            avg_response_time = df['response_time_minutes'].mean()
            avg_anomaly_time = anomaly_df['response_time_minutes'].mean()
            
            if avg_anomaly_time > avg_response_time * 2:
                analysis['severity'] = 'high'
            elif avg_anomaly_time > avg_response_time * 1.5:
                analysis['severity'] = 'medium'
            else:
                analysis['severity'] = 'low'
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing response time anomalies: {e}")
            return {'pattern': 'error', 'severity': 'unknown'}
    
    def _analyze_sentiment_anomalies(self, df: pd.DataFrame, anomalies: List[int]) -> Dict:
        """Analyze characteristics of sentiment anomalies."""
        try:
            if not anomalies:
                return {'pattern': 'none', 'severity': 'low'}
            
            anomaly_df = df.loc[anomalies]
            
            analysis = {
                'pattern': 'detected',
                'severity': 'medium',
                'characteristics': {}
            }
            
            # Analyze sentiment distribution
            sentiment_distribution = anomaly_df['combined_score'].describe()
            analysis['characteristics']['sentiment_stats'] = sentiment_distribution.to_dict()
            
            # Check for extreme values
            extreme_positive = len(anomaly_df[anomaly_df['combined_score'] > 0.8])
            extreme_negative = len(anomaly_df[anomaly_df['combined_score'] < -0.8])
            
            analysis['characteristics']['extreme_values'] = {
                'positive': extreme_positive,
                'negative': extreme_negative
            }
            
            # Determine severity
            if extreme_negative > len(anomalies) * 0.5:
                analysis['severity'] = 'high'
            elif extreme_positive > len(anomalies) * 0.7:
                analysis['severity'] = 'medium'
            else:
                analysis['severity'] = 'low'
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment anomalies: {e}")
            return {'pattern': 'error', 'severity': 'unknown'}
    
    def _analyze_volume_anomalies(self, daily_volumes: pd.Series, anomalies: List) -> Dict:
        """Analyze characteristics of volume anomalies."""
        try:
            if not anomalies:
                return {'pattern': 'none', 'severity': 'low'}
            
            analysis = {
                'pattern': 'detected',
                'severity': 'medium',
                'characteristics': {}
            }
            
            # Analyze anomaly volumes
            anomaly_volumes = daily_volumes.loc[anomalies]
            normal_volumes = daily_volumes.drop(anomalies)
            
            analysis['characteristics']['volume_stats'] = {
                'anomaly_mean': anomaly_volumes.mean(),
                'normal_mean': normal_volumes.mean(),
                'volume_ratio': anomaly_volumes.mean() / normal_volumes.mean() if normal_volumes.mean() > 0 else 1
            }
            
            # Determine severity
            volume_ratio = analysis['characteristics']['volume_stats']['volume_ratio']
            if volume_ratio > 3:
                analysis['severity'] = 'high'
            elif volume_ratio > 2:
                analysis['severity'] = 'medium'
            else:
                analysis['severity'] = 'low'
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing volume anomalies: {e}")
            return {'pattern': 'error', 'severity': 'unknown'}
    
    def _analyze_team_anomalies(self, df: pd.DataFrame, team_anomalies: Dict) -> Dict:
        """Analyze team-specific anomaly patterns."""
        try:
            if not team_anomalies:
                return {'pattern': 'none', 'severity': 'low'}
            
            analysis = {
                'pattern': 'detected',
                'severity': 'medium',
                'team_analysis': {}
            }
            
            # Analyze each team's anomaly patterns
            for team, data in team_anomalies.items():
                team_df = df[df['team'] == team]
                anomaly_count = data['count']
                total_count = len(team_df)
                
                analysis['team_analysis'][team] = {
                    'anomaly_rate': anomaly_count / total_count,
                    'severity': 'high' if anomaly_count / total_count > 0.2 else 'medium' if anomaly_count / total_count > 0.1 else 'low'
                }
            
            # Overall severity
            high_severity_teams = sum(1 for team_data in analysis['team_analysis'].values() 
                                    if team_data['severity'] == 'high')
            
            if high_severity_teams > len(team_anomalies) * 0.5:
                analysis['severity'] = 'high'
            elif high_severity_teams > 0:
                analysis['severity'] = 'medium'
            else:
                analysis['severity'] = 'low'
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing team anomalies: {e}")
            return {'pattern': 'error', 'severity': 'unknown'}
    
    def _analyze_temporal_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze temporal patterns in the data."""
        try:
            analysis = {
                'business_hours_distribution': {},
                'weekend_activity': 0,
                'peak_hours': []
            }
            
            # Analyze business hours distribution
            hourly_counts = df.groupby(df['created_at'].dt.hour).size()
            analysis['business_hours_distribution'] = hourly_counts.to_dict()
            
            # Weekend activity
            weekend_count = len(df[df['created_at'].dt.dayofweek.isin([5, 6])])
            analysis['weekend_activity'] = weekend_count / len(df) * 100
            
            # Peak hours
            peak_hours = hourly_counts.nlargest(3).index.tolist()
            analysis['peak_hours'] = peak_hours
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing temporal patterns: {e}")
            return {'pattern': 'error'}
    
    def _assess_anomaly_severity(self, anomaly_count: int, total_count: int) -> str:
        """Assess the severity of anomalies."""
        try:
            anomaly_rate = anomaly_count / total_count if total_count > 0 else 0
            
            if anomaly_rate > 0.2:
                return 'high'
            elif anomaly_rate > 0.1:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            logger.error(f"Error assessing anomaly severity: {e}")
            return 'unknown'
    
    def _assess_team_anomaly_severity(self, team_anomalies: Dict) -> str:
        """Assess overall team anomaly severity."""
        try:
            if not team_anomalies:
                return 'low'
            
            # Calculate average anomaly rate across teams
            total_anomalies = sum(data['count'] for data in team_anomalies.values())
            total_tickets = sum(data['count'] / (data['percentage'] / 100) for data in team_anomalies.values())
            
            if total_tickets > 0:
                overall_rate = total_anomalies / total_tickets
                return self._assess_anomaly_severity(int(total_anomalies), int(total_tickets))
            
            return 'medium'
            
        except Exception as e:
            logger.error(f"Error assessing team anomaly severity: {e}")
            return 'unknown'
    
    def _generate_anomaly_summary(self, anomalies: Dict) -> Dict:
        """Generate overall anomaly summary."""
        try:
            summary = {
                'total_anomalies': 0,
                'anomaly_types': [],
                'overall_severity': 'low',
                'recommendations': []
            }
            
            # Count total anomalies
            for anomaly_type, data in anomalies.items():
                if isinstance(data, dict) and 'count' in data:
                    summary['total_anomalies'] += data['count']
                    summary['anomaly_types'].append(anomaly_type)
            
            # Determine overall severity
            severity_scores = []
            for anomaly_type, data in anomalies.items():
                if isinstance(data, dict) and 'severity' in data:
                    severity = data['severity']
                    if severity == 'high':
                        severity_scores.append(3)
                    elif severity == 'medium':
                        severity_scores.append(2)
                    else:
                        severity_scores.append(1)
            
            if severity_scores:
                avg_severity = np.mean(severity_scores)
                if avg_severity >= 2.5:
                    summary['overall_severity'] = 'high'
                elif avg_severity >= 1.5:
                    summary['overall_severity'] = 'medium'
                else:
                    summary['overall_severity'] = 'low'
            
            # Generate recommendations
            summary['recommendations'] = self._generate_anomaly_recommendations(anomalies)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating anomaly summary: {e}")
            return {'total_anomalies': 0, 'overall_severity': 'unknown'}
    
    def _generate_anomaly_recommendations(self, anomalies: Dict) -> List[str]:
        """Generate recommendations based on detected anomalies."""
        try:
            recommendations = []
            
            # Response time anomalies
            if 'response_time' in anomalies and anomalies['response_time'].get('count', 0) > 0:
                recommendations.append("Review response time anomalies - consider process optimization")
            
            # Sentiment anomalies
            if 'sentiment' in anomalies and anomalies['sentiment'].get('count', 0) > 0:
                recommendations.append("Investigate sentiment anomalies - review customer feedback processes")
            
            # Volume anomalies
            if 'volume' in anomalies and anomalies['volume'].get('count', 0) > 0:
                recommendations.append("Analyze volume anomalies - consider capacity planning")
            
            # Team anomalies
            if 'team_performance' in anomalies and anomalies['team_performance'].get('team_anomalies'):
                recommendations.append("Address team performance anomalies - provide targeted training")
            
            # Temporal anomalies
            if 'temporal' in anomalies and anomalies['temporal'].get('count', 0) > 0:
                recommendations.append("Review temporal patterns - optimize scheduling and resource allocation")
            
            # General recommendations
            if len(recommendations) == 0:
                recommendations.append("No significant anomalies detected - maintain current monitoring")
            else:
                recommendations.append("Implement continuous anomaly monitoring system")
            
            return recommendations[:5]  # Limit to top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error generating anomaly recommendations: {e}")
            return ["Unable to generate recommendations"]
