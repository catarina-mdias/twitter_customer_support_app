"""
Performance metrics module for customer support analytics.
Handles calculation of various performance metrics for teams and individuals.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceMetrics:
    """Handles calculation of performance metrics for teams and individuals."""
    
    def __init__(self):
        """Initialize the performance metrics calculator."""
        self.metric_weights = {
            'response_time': 0.25,
            'quality': 0.25,
            'efficiency': 0.25,
            'consistency': 0.25
        }
        
        self.thresholds = {
            'excellent_response_time': 15,  # minutes
            'good_response_time': 30,
            'acceptable_response_time': 60,
            'poor_response_time': 120,
            'excellent_sla_compliance': 0.95,  # 95%
            'good_sla_compliance': 0.85,       # 85%
            'acceptable_sla_compliance': 0.75,  # 75%
            'excellent_sentiment': 0.5,        # 0.5
            'good_sentiment': 0.2,             # 0.2
            'acceptable_sentiment': 0.0,       # 0.0
            'excellent_positive_rate': 0.7,    # 70%
            'good_positive_rate': 0.5,         # 50%
            'acceptable_positive_rate': 0.3    # 30%
        }
        
        logger.info("Performance metrics calculator initialized")
    
    def calculate_efficiency_score(self, team_data: pd.DataFrame) -> float:
        """
        Calculate team efficiency score based on various metrics.
        
        Args:
            team_data: DataFrame with team performance data
            
        Returns:
            float: Efficiency score (0-100)
        """
        try:
            if team_data.empty:
                return 0.0
            
            efficiency_components = []
            
            # Ticket processing rate
            if 'ticket_id' in team_data.columns:
                total_tickets = len(team_data)
                # Assuming 30-day period for calculation
                tickets_per_day = total_tickets / 30
                ticket_score = min(100, (tickets_per_day / 10) * 100)  # Scale based on 10 tickets/day target
                efficiency_components.append(ticket_score)
            
            # Response time efficiency
            if 'response_time_minutes' in team_data.columns:
                median_rt = team_data['response_time_minutes'].median()
                rt_efficiency = max(0, 100 - (median_rt / 60) * 100)  # Scale to 100
                efficiency_components.append(rt_efficiency)
            
            # SLA compliance efficiency
            if 'response_time_minutes' in team_data.columns:
                sla_compliance = (team_data['response_time_minutes'] <= 60).mean()
                sla_efficiency = sla_compliance * 100
                efficiency_components.append(sla_efficiency)
            
            # First-call resolution (if available)
            if 'first_call_resolution' in team_data.columns:
                fcr_rate = team_data['first_call_resolution'].mean()
                fcr_efficiency = fcr_rate * 100
                efficiency_components.append(fcr_efficiency)
            
            # Calculate weighted average
            if efficiency_components:
                efficiency_score = np.mean(efficiency_components)
            else:
                efficiency_score = 50.0  # Neutral score
            
            logger.info(f"Calculated efficiency score: {efficiency_score:.2f}")
            return min(100, max(0, efficiency_score))
            
        except Exception as e:
            logger.error(f"Error calculating efficiency score: {str(e)}")
            return 0.0
    
    def calculate_quality_score(self, team_data: pd.DataFrame) -> float:
        """
        Calculate response quality score based on customer feedback.
        
        Args:
            team_data: DataFrame with team performance data
            
        Returns:
            float: Quality score (0-100)
        """
        try:
            if team_data.empty:
                return 50.0  # Neutral score
            
            quality_components = []
            
            # Sentiment-based quality
            if 'combined_score' in team_data.columns:
                avg_sentiment = team_data['combined_score'].mean()
                # Convert sentiment score (-1 to 1) to quality score (0 to 100)
                sentiment_quality = (avg_sentiment + 1) * 50
                quality_components.append(sentiment_quality)
            
            # Positive feedback rate
            if 'category' in team_data.columns:
                positive_rate = (team_data['category'] == 'positive').mean()
                positive_quality = positive_rate * 100
                quality_components.append(positive_quality)
            
            # Resolution quality (based on sentiment improvement)
            if 'combined_score' in team_data.columns and 'response_time_minutes' in team_data.columns:
                # Check if better response times correlate with better sentiment
                correlation = team_data['response_time_minutes'].corr(team_data['combined_score'])
                if not pd.isna(correlation):
                    # Negative correlation is good (faster response = better sentiment)
                    resolution_quality = max(0, 50 - correlation * 25)  # Scale correlation
                    quality_components.append(resolution_quality)
            
            # Calculate weighted average
            if quality_components:
                quality_score = np.mean(quality_components)
            else:
                quality_score = 50.0  # Neutral score
            
            logger.info(f"Calculated quality score: {quality_score:.2f}")
            return min(100, max(0, quality_score))
            
        except Exception as e:
            logger.error(f"Error calculating quality score: {str(e)}")
            return 50.0
    
    def calculate_consistency_score(self, team_data: pd.DataFrame) -> float:
        """
        Calculate performance consistency score.
        
        Args:
            team_data: DataFrame with team performance data
            
        Returns:
            float: Consistency score (0-100)
        """
        try:
            if team_data.empty:
                return 0.0
            
            consistency_components = []
            
            # Response time consistency
            if 'response_time_minutes' in team_data.columns:
                rt_std = team_data['response_time_minutes'].std()
                rt_mean = team_data['response_time_minutes'].mean()
                
                if rt_mean > 0:
                    # Lower coefficient of variation = more consistent
                    cv = rt_std / rt_mean
                    rt_consistency = max(0, 100 - cv * 50)  # Scale CV to 0-100
                    consistency_components.append(rt_consistency)
            
            # Sentiment consistency
            if 'combined_score' in team_data.columns:
                sentiment_std = team_data['combined_score'].std()
                # Lower standard deviation = more consistent sentiment
                sentiment_consistency = max(0, 100 - sentiment_std * 100)
                consistency_components.append(sentiment_consistency)
            
            # Daily ticket volume consistency
            if 'created_at' in team_data.columns and 'ticket_id' in team_data.columns:
                team_data['created_at'] = pd.to_datetime(team_data['created_at'])
                daily_tickets = team_data.groupby(team_data['created_at'].dt.date).size()
                
                if len(daily_tickets) > 1:
                    volume_std = daily_tickets.std()
                    volume_mean = daily_tickets.mean()
                    
                    if volume_mean > 0:
                        volume_cv = volume_std / volume_mean
                        volume_consistency = max(0, 100 - volume_cv * 50)
                        consistency_components.append(volume_consistency)
            
            # Calculate weighted average
            if consistency_components:
                consistency_score = np.mean(consistency_components)
            else:
                consistency_score = 50.0  # Neutral score
            
            logger.info(f"Calculated consistency score: {consistency_score:.2f}")
            return min(100, max(0, consistency_score))
            
        except Exception as e:
            logger.error(f"Error calculating consistency score: {str(e)}")
            return 0.0
    
    def calculate_capacity_utilization(self, team_data: pd.DataFrame) -> float:
        """
        Calculate team capacity utilization score.
        
        Args:
            team_data: DataFrame with team performance data
            
        Returns:
            float: Capacity utilization score (0-100)
        """
        try:
            if team_data.empty:
                return 0.0
            
            capacity_components = []
            
            # Ticket processing capacity
            if 'ticket_id' in team_data.columns:
                total_tickets = len(team_data)
                # Assuming 30-day period and target of 10 tickets/day per team
                target_tickets = 10 * 30
                capacity_utilization = min(100, (total_tickets / target_tickets) * 100)
                capacity_components.append(capacity_utilization)
            
            # Response time capacity (ability to handle load)
            if 'response_time_minutes' in team_data.columns:
                median_rt = team_data['response_time_minutes'].median()
                # Lower response time = better capacity utilization
                rt_capacity = max(0, 100 - (median_rt / 60) * 100)
                capacity_components.append(rt_capacity)
            
            # Peak performance analysis
            if 'created_at' in team_data.columns and 'response_time_minutes' in team_data.columns:
                team_data['created_at'] = pd.to_datetime(team_data['created_at'])
                team_data['hour'] = team_data['created_at'].dt.hour
                
                # Calculate hourly performance
                hourly_performance = team_data.groupby('hour')['response_time_minutes'].agg(['mean', 'count'])
                hourly_performance = hourly_performance[hourly_performance['count'] > 0]
                
                if not hourly_performance.empty:
                    # Find peak hours (most tickets)
                    peak_hours = hourly_performance.nlargest(3, 'count')
                    peak_avg_rt = peak_hours['mean'].mean()
                    
                    # Better performance during peak hours = better capacity
                    peak_capacity = max(0, 100 - (peak_avg_rt / 60) * 100)
                    capacity_components.append(peak_capacity)
            
            # Calculate weighted average
            if capacity_components:
                capacity_score = np.mean(capacity_components)
            else:
                capacity_score = 50.0  # Neutral score
            
            logger.info(f"Calculated capacity utilization: {capacity_score:.2f}")
            return min(100, max(0, capacity_score))
            
        except Exception as e:
            logger.error(f"Error calculating capacity utilization: {str(e)}")
            return 0.0
    
    def calculate_overall_performance(self, team_data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate overall performance metrics for a team.
        
        Args:
            team_data: DataFrame with team performance data
            
        Returns:
            Dict[str, float]: Dictionary of performance metrics
        """
        try:
            if team_data.empty:
                return {
                    'efficiency_score': 0.0,
                    'quality_score': 0.0,
                    'consistency_score': 0.0,
                    'capacity_utilization': 0.0,
                    'overall_score': 0.0
                }
            
            # Calculate individual component scores
            efficiency_score = self.calculate_efficiency_score(team_data)
            quality_score = self.calculate_quality_score(team_data)
            consistency_score = self.calculate_consistency_score(team_data)
            capacity_utilization = self.calculate_capacity_utilization(team_data)
            
            # Calculate weighted overall score
            overall_score = (
                efficiency_score * self.metric_weights['efficiency'] +
                quality_score * self.metric_weights['quality'] +
                consistency_score * self.metric_weights['consistency'] +
                capacity_utilization * self.metric_weights['response_time']  # Using response_time weight for capacity
            )
            
            performance_metrics = {
                'efficiency_score': round(efficiency_score, 2),
                'quality_score': round(quality_score, 2),
                'consistency_score': round(consistency_score, 2),
                'capacity_utilization': round(capacity_utilization, 2),
                'overall_score': round(overall_score, 2)
            }
            
            logger.info(f"Calculated overall performance: {overall_score:.2f}")
            return performance_metrics
            
        except Exception as e:
            logger.error(f"Error calculating overall performance: {str(e)}")
            return {
                'efficiency_score': 0.0,
                'quality_score': 0.0,
                'consistency_score': 0.0,
                'capacity_utilization': 0.0,
                'overall_score': 0.0
            }
    
    def get_performance_benchmarks(self, teams_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Calculate performance benchmarks across all teams.
        
        Args:
            teams_data: Dictionary with team names as keys and DataFrames as values
            
        Returns:
            Dict[str, Any]: Performance benchmarks
        """
        try:
            if not teams_data:
                return {}
            
            all_metrics = []
            
            # Calculate metrics for each team
            for team_name, team_data in teams_data.items():
                if team_data.empty:
                    continue
                
                team_metrics = self.calculate_overall_performance(team_data)
                team_metrics['team'] = team_name
                all_metrics.append(team_metrics)
            
            if not all_metrics:
                return {}
            
            metrics_df = pd.DataFrame(all_metrics)
            
            # Calculate benchmarks
            benchmarks = {
                'overall_score': {
                    'mean': metrics_df['overall_score'].mean(),
                    'median': metrics_df['overall_score'].median(),
                    'std': metrics_df['overall_score'].std(),
                    'min': metrics_df['overall_score'].min(),
                    'max': metrics_df['overall_score'].max()
                },
                'efficiency_score': {
                    'mean': metrics_df['efficiency_score'].mean(),
                    'median': metrics_df['efficiency_score'].median(),
                    'std': metrics_df['efficiency_score'].std()
                },
                'quality_score': {
                    'mean': metrics_df['quality_score'].mean(),
                    'median': metrics_df['quality_score'].median(),
                    'std': metrics_df['quality_score'].std()
                },
                'consistency_score': {
                    'mean': metrics_df['consistency_score'].mean(),
                    'median': metrics_df['consistency_score'].median(),
                    'std': metrics_df['consistency_score'].std()
                },
                'capacity_utilization': {
                    'mean': metrics_df['capacity_utilization'].mean(),
                    'median': metrics_df['capacity_utilization'].median(),
                    'std': metrics_df['capacity_utilization'].std()
                },
                'team_count': len(metrics_df),
                'top_performer': metrics_df.loc[metrics_df['overall_score'].idxmax(), 'team'],
                'needs_improvement': metrics_df.loc[metrics_df['overall_score'].idxmin(), 'team']
            }
            
            logger.info(f"Calculated benchmarks for {len(metrics_df)} teams")
            return benchmarks
            
        except Exception as e:
            logger.error(f"Error calculating performance benchmarks: {str(e)}")
            return {}
    
    def get_performance_trends(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate performance trends over time.
        
        Args:
            historical_data: DataFrame with historical performance data
            
        Returns:
            Dict[str, Any]: Performance trend analysis
        """
        try:
            if historical_data.empty or 'created_at' not in historical_data.columns:
                return {}
            
            # Ensure date column is datetime
            historical_data['created_at'] = pd.to_datetime(historical_data['created_at'])
            
            # Group by team and date
            daily_metrics = historical_data.groupby(['team', historical_data['created_at'].dt.date]).agg({
                'response_time_minutes': 'mean',
                'combined_score': 'mean' if 'combined_score' in historical_data.columns else lambda x: 0,
                'ticket_id': 'count'
            }).reset_index()
            
            daily_metrics.columns = ['team', 'date', 'avg_response_time', 'avg_sentiment', 'ticket_count']
            
            trends = {}
            
            # Calculate trends for each team
            for team in daily_metrics['team'].unique():
                team_data = daily_metrics[daily_metrics['team'] == team].sort_values('date')
                
                if len(team_data) < 2:
                    continue
                
                # Calculate trend slopes
                x = np.arange(len(team_data))
                
                # Response time trend (negative is good)
                rt_trend = np.polyfit(x, team_data['avg_response_time'], 1)[0] if len(team_data) > 1 else 0
                
                # Sentiment trend (positive is good)
                sentiment_trend = np.polyfit(x, team_data['avg_sentiment'], 1)[0] if len(team_data) > 1 else 0
                
                # Volume trend
                volume_trend = np.polyfit(x, team_data['ticket_count'], 1)[0] if len(team_data) > 1 else 0
                
                trends[team] = {
                    'response_time_trend': rt_trend,
                    'sentiment_trend': sentiment_trend,
                    'volume_trend': volume_trend,
                    'data_points': len(team_data),
                    'improving_response_time': rt_trend < 0,
                    'improving_sentiment': sentiment_trend > 0,
                    'increasing_volume': volume_trend > 0,
                    'trend_strength': abs(rt_trend) + abs(sentiment_trend) + abs(volume_trend)
                }
            
            logger.info(f"Calculated trends for {len(trends)} teams")
            return trends
            
        except Exception as e:
            logger.error(f"Error calculating performance trends: {str(e)}")
            return {}
    
    def get_performance_insights(self, team_data: pd.DataFrame, team_name: str) -> Dict[str, Any]:
        """
        Get performance insights and recommendations for a team.
        
        Args:
            team_data: DataFrame with team performance data
            team_name: Name of the team
            
        Returns:
            Dict[str, Any]: Performance insights
        """
        try:
            if team_data.empty:
                return {'error': 'No data available for performance analysis'}
            
            # Calculate performance metrics
            performance_metrics = self.calculate_overall_performance(team_data)
            
            # Generate insights
            insights = {
                'team_name': team_name,
                'performance_metrics': performance_metrics,
                'insights': [],
                'recommendations': [],
                'strengths': [],
                'weaknesses': []
            }
            
            # Analyze strengths and weaknesses
            if performance_metrics['efficiency_score'] >= 80:
                insights['strengths'].append("High efficiency in ticket processing")
            elif performance_metrics['efficiency_score'] <= 40:
                insights['weaknesses'].append("Low efficiency - consider process optimization")
            
            if performance_metrics['quality_score'] >= 80:
                insights['strengths'].append("Excellent customer satisfaction")
            elif performance_metrics['quality_score'] <= 40:
                insights['weaknesses'].append("Low customer satisfaction - focus on service quality")
            
            if performance_metrics['consistency_score'] >= 80:
                insights['strengths'].append("Consistent performance across all metrics")
            elif performance_metrics['consistency_score'] <= 40:
                insights['weaknesses'].append("Inconsistent performance - standardize processes")
            
            if performance_metrics['capacity_utilization'] >= 80:
                insights['strengths'].append("Good capacity utilization")
            elif performance_metrics['capacity_utilization'] <= 40:
                insights['weaknesses'].append("Low capacity utilization - optimize resource allocation")
            
            # Generate recommendations
            if performance_metrics['efficiency_score'] < 60:
                insights['recommendations'].append("Implement ticket prioritization system")
            
            if performance_metrics['quality_score'] < 60:
                insights['recommendations'].append("Provide additional customer service training")
            
            if performance_metrics['consistency_score'] < 60:
                insights['recommendations'].append("Standardize response procedures")
            
            if performance_metrics['capacity_utilization'] < 60:
                insights['recommendations'].append("Review workload distribution and capacity planning")
            
            # Overall performance level
            overall_score = performance_metrics['overall_score']
            if overall_score >= 90:
                insights['performance_level'] = 'Excellent'
            elif overall_score >= 75:
                insights['performance_level'] = 'Good'
            elif overall_score >= 60:
                insights['performance_level'] = 'Average'
            elif overall_score >= 45:
                insights['performance_level'] = 'Poor'
            else:
                insights['performance_level'] = 'Critical'
            
            logger.info(f"Generated performance insights for team: {team_name}")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating performance insights: {str(e)}")
            return {'error': str(e)}
