"""
Team analysis module for customer support analytics.
Handles advanced team performance analysis, scoring, and comparison.
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

class TeamAnalyzer:
    """Handles advanced team performance analysis and comparison."""
    
    def __init__(self):
        """Initialize the team analyzer with performance parameters."""
        self.performance_weights = {
            'response_time': 0.30,
            'quality': 0.25,
            'efficiency': 0.25,
            'capacity': 0.20
        }
        
        self.scoring_thresholds = {
            'excellent': 90,
            'good': 75,
            'average': 60,
            'poor': 45
        }
        
        logger.info("Team analyzer initialized")
    
    def calculate_team_score(self, team_data: pd.DataFrame) -> float:
        """
        Calculate overall team performance score (0-100).
        
        Args:
            team_data: DataFrame with team performance metrics
            
        Returns:
            float: Overall team performance score
        """
        try:
            if team_data.empty:
                return 0.0
            
            # Calculate individual component scores
            response_time_score = self._calculate_response_time_score(team_data)
            quality_score = self._calculate_quality_score(team_data)
            efficiency_score = self._calculate_efficiency_score(team_data)
            capacity_score = self._calculate_capacity_score(team_data)
            
            # Calculate weighted overall score
            overall_score = (
                response_time_score * self.performance_weights['response_time'] +
                quality_score * self.performance_weights['quality'] +
                efficiency_score * self.performance_weights['efficiency'] +
                capacity_score * self.performance_weights['capacity']
            )
            
            # Ensure score is between 0 and 100
            overall_score = min(100, max(0, overall_score))
            
            logger.info(f"Calculated team score: {overall_score:.2f}")
            return overall_score
            
        except Exception as e:
            logger.error(f"Error calculating team score: {str(e)}")
            return 0.0
    
    def identify_improvement_areas(self, team_data: pd.DataFrame) -> List[str]:
        """
        Identify specific areas for improvement.
        
        Args:
            team_data: DataFrame with team performance metrics
            
        Returns:
            List[str]: List of improvement areas
        """
        try:
            improvement_areas = []
            
            # Check response time performance
            if 'response_time_minutes' in team_data.columns:
                median_rt = team_data['response_time_minutes'].median()
                sla_compliance = (team_data['response_time_minutes'] <= 60).mean()
                
                if median_rt > 45:  # More than 45 minutes median
                    improvement_areas.append("Response Time - Median response time is too high")
                if sla_compliance < 0.8:  # Less than 80% SLA compliance
                    improvement_areas.append("SLA Compliance - Below 80% compliance rate")
            
            # Check quality metrics
            if 'combined_score' in team_data.columns:
                avg_sentiment = team_data['combined_score'].mean()
                positive_rate = (team_data['category'] == 'positive').mean()
                
                if avg_sentiment < 0.1:  # Low sentiment score
                    improvement_areas.append("Customer Satisfaction - Low sentiment scores")
                if positive_rate < 0.4:  # Less than 40% positive
                    improvement_areas.append("Customer Experience - Low positive feedback rate")
            
            # Check efficiency metrics
            if 'ticket_id' in team_data.columns:
                total_tickets = len(team_data)
                if total_tickets < 10:  # Low ticket volume
                    improvement_areas.append("Ticket Volume - Low ticket processing volume")
            
            # Check consistency
            if 'response_time_minutes' in team_data.columns:
                rt_std = team_data['response_time_minutes'].std()
                rt_mean = team_data['response_time_minutes'].mean()
                cv = rt_std / rt_mean if rt_mean > 0 else 0
                
                if cv > 1.0:  # High coefficient of variation
                    improvement_areas.append("Consistency - High variability in response times")
            
            logger.info(f"Identified {len(improvement_areas)} improvement areas")
            return improvement_areas
            
        except Exception as e:
            logger.error(f"Error identifying improvement areas: {str(e)}")
            return []
    
    def compare_teams(self, teams_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Compare multiple teams and return comparison metrics.
        
        Args:
            teams_data: Dictionary with team names as keys and DataFrames as values
            
        Returns:
            pd.DataFrame: Team comparison metrics
        """
        try:
            comparison_data = []
            
            for team_name, team_df in teams_data.items():
                if team_df.empty:
                    continue
                
                # Calculate team metrics
                team_score = self.calculate_team_score(team_df)
                improvement_areas = self.identify_improvement_areas(team_df)
                
                # Basic metrics
                total_tickets = len(team_df)
                avg_response_time = team_df['response_time_minutes'].mean() if 'response_time_minutes' in team_df.columns else 0
                sla_compliance = (team_df['response_time_minutes'] <= 60).mean() if 'response_time_minutes' in team_df.columns else 0
                
                # Quality metrics
                avg_sentiment = team_df['combined_score'].mean() if 'combined_score' in team_df.columns else 0
                positive_rate = (team_df['category'] == 'positive').mean() if 'category' in team_df.columns else 0
                
                # Efficiency metrics
                tickets_per_day = total_tickets / 30 if total_tickets > 0 else 0  # Assuming 30-day period
                
                comparison_data.append({
                    'Team': team_name,
                    'Overall Score': round(team_score, 2),
                    'Total Tickets': total_tickets,
                    'Avg Response Time (min)': round(avg_response_time, 2),
                    'SLA Compliance (%)': round(sla_compliance * 100, 1),
                    'Avg Sentiment Score': round(avg_sentiment, 3),
                    'Positive Rate (%)': round(positive_rate * 100, 1),
                    'Tickets per Day': round(tickets_per_day, 1),
                    'Improvement Areas': len(improvement_areas),
                    'Performance Level': self._get_performance_level(team_score)
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            
            # Sort by overall score (best performers first)
            comparison_df = comparison_df.sort_values('Overall Score', ascending=False)
            
            logger.info(f"Compared {len(teams_data)} teams")
            return comparison_df
            
        except Exception as e:
            logger.error(f"Error comparing teams: {str(e)}")
            return pd.DataFrame()
    
    def track_performance_trends(self, historical_data: pd.DataFrame) -> Dict:
        """
        Track performance changes over time.
        
        Args:
            historical_data: DataFrame with historical team performance data
            
        Returns:
            Dict: Performance trend analysis
        """
        try:
            if historical_data.empty or 'created_at' not in historical_data.columns:
                return {}
            
            # Ensure date column is datetime
            historical_data['created_at'] = pd.to_datetime(historical_data['created_at'])
            
            # Group by team and date
            daily_metrics = historical_data.groupby(['team', historical_data['created_at'].dt.date]).agg({
                'response_time_minutes': ['mean', 'count'],
                'combined_score': 'mean' if 'combined_score' in historical_data.columns else lambda x: 0
            }).round(3)
            
            # Flatten column names
            daily_metrics.columns = ['avg_response_time', 'ticket_count', 'avg_sentiment']
            daily_metrics = daily_metrics.reset_index()
            
            trends = {}
            
            # Calculate trends for each team
            for team in daily_metrics['team'].unique():
                team_data = daily_metrics[daily_metrics['team'] == team].sort_values('created_at')
                
                if len(team_data) < 2:
                    continue
                
                # Calculate trend slopes
                x = np.arange(len(team_data))
                
                # Response time trend
                rt_trend = np.polyfit(x, team_data['avg_response_time'], 1)[0] if len(team_data) > 1 else 0
                
                # Sentiment trend
                sentiment_trend = np.polyfit(x, team_data['avg_sentiment'], 1)[0] if len(team_data) > 1 else 0
                
                # Ticket volume trend
                volume_trend = np.polyfit(x, team_data['ticket_count'], 1)[0] if len(team_data) > 1 else 0
                
                trends[team] = {
                    'response_time_trend': rt_trend,
                    'sentiment_trend': sentiment_trend,
                    'volume_trend': volume_trend,
                    'data_points': len(team_data),
                    'improving_response_time': rt_trend < 0,  # Negative trend is good
                    'improving_sentiment': sentiment_trend > 0,  # Positive trend is good
                    'increasing_volume': volume_trend > 0
                }
            
            logger.info(f"Calculated trends for {len(trends)} teams")
            return trends
            
        except Exception as e:
            logger.error(f"Error tracking performance trends: {str(e)}")
            return {}
    
    def get_team_rankings(self, teams_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Get team performance rankings.
        
        Args:
            teams_data: Dictionary with team names as keys and DataFrames as values
            
        Returns:
            pd.DataFrame: Team rankings
        """
        try:
            rankings_data = []
            
            for team_name, team_df in teams_data.items():
                if team_df.empty:
                    continue
                
                team_score = self.calculate_team_score(team_df)
                improvement_areas = self.identify_improvement_areas(team_df)
                
                rankings_data.append({
                    'Team': team_name,
                    'Score': team_score,
                    'Performance Level': self._get_performance_level(team_score),
                    'Improvement Areas': len(improvement_areas),
                    'Priority': 'High' if len(improvement_areas) > 3 else 'Medium' if len(improvement_areas) > 1 else 'Low'
                })
            
            rankings_df = pd.DataFrame(rankings_data)
            rankings_df = rankings_df.sort_values('Score', ascending=False)
            rankings_df['Rank'] = range(1, len(rankings_df) + 1)
            
            logger.info(f"Generated rankings for {len(rankings_df)} teams")
            return rankings_df
            
        except Exception as e:
            logger.error(f"Error generating team rankings: {str(e)}")
            return pd.DataFrame()
    
    def _calculate_response_time_score(self, team_data: pd.DataFrame) -> float:
        """Calculate response time performance score."""
        if 'response_time_minutes' not in team_data.columns:
            return 50.0  # Return neutral score instead of 0
        
        median_rt = team_data['response_time_minutes'].median()
        sla_compliance = (team_data['response_time_minutes'] <= 60).mean()
        
        # Score based on median response time (lower is better)
        # More gradual scoring: excellent (<15 min), good (<30 min), average (<60 min), poor (>60 min)
        if median_rt <= 15:
            rt_score = 100
        elif median_rt <= 30:
            rt_score = 90 - ((median_rt - 15) / 15) * 10  # 90-80
        elif median_rt <= 60:
            rt_score = 80 - ((median_rt - 30) / 30) * 20  # 80-60
        else:
            rt_score = max(40, 60 - ((median_rt - 60) / 60) * 20)  # 60-40
        
        # Adjust based on SLA compliance
        sla_score = sla_compliance * 100
        
        # Weighted average: 60% response time, 40% SLA compliance
        final_score = (rt_score * 0.6) + (sla_score * 0.4)
        
        return min(100, max(0, final_score))
    
    def _calculate_quality_score(self, team_data: pd.DataFrame) -> float:
        """Calculate quality performance score."""
        if 'combined_score' not in team_data.columns:
            return 50.0  # Neutral score if no sentiment data
        
        avg_sentiment = team_data['combined_score'].mean()
        positive_rate = (team_data['category'] == 'positive').mean()
        
        # Convert sentiment score to 0-100 scale
        sentiment_score = (avg_sentiment + 1) * 50  # -1 to 1 becomes 0 to 100
        
        # Adjust based on positive rate
        positive_factor = positive_rate * 0.2 + 0.8  # 0.8 to 1.0 multiplier
        
        return min(100, sentiment_score * positive_factor)
    
    def _calculate_efficiency_score(self, team_data: pd.DataFrame) -> float:
        """Calculate efficiency performance score."""
        if 'ticket_id' not in team_data.columns:
            return 50.0
        
        total_tickets = len(team_data)
        
        # Score based on ticket volume (more tickets processed = higher efficiency)
        # More reasonable thresholds: 10+ tickets/day = excellent, 5+ = good, 2+ = average
        tickets_per_day = total_tickets / 30  # Assuming 30-day period
        
        if tickets_per_day >= 10:
            efficiency_score = 100
        elif tickets_per_day >= 5:
            efficiency_score = 80 + ((tickets_per_day - 5) / 5) * 20  # 80-100
        elif tickets_per_day >= 2:
            efficiency_score = 60 + ((tickets_per_day - 2) / 3) * 20  # 60-80
        elif tickets_per_day >= 1:
            efficiency_score = 40 + ((tickets_per_day - 1) / 1) * 20  # 40-60
        else:
            efficiency_score = max(20, tickets_per_day * 40)  # 0-40
        
        return min(100, efficiency_score)
    
    def _calculate_capacity_score(self, team_data: pd.DataFrame) -> float:
        """Calculate capacity utilization score based on consistency."""
        if 'response_time_minutes' not in team_data.columns:
            return 50.0
        
        # Calculate capacity based on response time consistency
        rt_std = team_data['response_time_minutes'].std()
        rt_mean = team_data['response_time_minutes'].mean()
        
        if rt_mean == 0 or pd.isna(rt_std):
            return 50.0
        
        # Lower coefficient of variation = better consistency/capacity management
        cv = rt_std / rt_mean
        
        # More gradual scoring: excellent (CV<0.5), good (CV<1.0), average (CV<1.5), poor (CV>=1.5)
        if cv <= 0.5:
            capacity_score = 90 + (0.5 - cv) * 20  # 90-100
        elif cv <= 1.0:
            capacity_score = 75 + (1.0 - cv) * 30  # 75-90
        elif cv <= 1.5:
            capacity_score = 60 + (1.5 - cv) * 30  # 60-75
        else:
            capacity_score = max(40, 60 - (cv - 1.5) * 20)  # 40-60
        
        return min(100, max(0, capacity_score))
    
    def _get_performance_level(self, score: float) -> str:
        """Get performance level based on score."""
        if score >= self.scoring_thresholds['excellent']:
            return 'Excellent'
        elif score >= self.scoring_thresholds['good']:
            return 'Good'
        elif score >= self.scoring_thresholds['average']:
            return 'Average'
        elif score >= self.scoring_thresholds['poor']:
            return 'Poor'
        else:
            return 'Critical'
    
    def get_team_insights(self, team_data: pd.DataFrame, team_name: str) -> Dict:
        """
        Get comprehensive insights for a specific team.
        
        Args:
            team_data: DataFrame with team performance data
            team_name: Name of the team
            
        Returns:
            Dict: Team insights
        """
        try:
            if team_data.empty:
                return {'error': 'No data available for team analysis'}
            
            # Calculate basic metrics
            team_score = self.calculate_team_score(team_data)
            improvement_areas = self.identify_improvement_areas(team_data)
            
            # Performance level
            performance_level = self._get_performance_level(team_score)
            
            # Key metrics
            total_tickets = len(team_data)
            avg_response_time = team_data['response_time_minutes'].mean() if 'response_time_minutes' in team_data.columns else 0
            sla_compliance = (team_data['response_time_minutes'] <= 60).mean() if 'response_time_minutes' in team_data.columns else 0
            
            # Quality metrics
            avg_sentiment = team_data['combined_score'].mean() if 'combined_score' in team_data.columns else 0
            positive_rate = (team_data['category'] == 'positive').mean() if 'category' in team_data.columns else 0
            
            insights = {
                'team_name': team_name,
                'overall_score': round(team_score, 2),
                'performance_level': performance_level,
                'total_tickets': total_tickets,
                'avg_response_time': round(avg_response_time, 2),
                'sla_compliance': round(sla_compliance * 100, 1),
                'avg_sentiment': round(avg_sentiment, 3),
                'positive_rate': round(positive_rate * 100, 1),
                'improvement_areas': improvement_areas,
                'improvement_count': len(improvement_areas),
                'priority_level': 'High' if len(improvement_areas) > 3 else 'Medium' if len(improvement_areas) > 1 else 'Low'
            }
            
            logger.info(f"Generated insights for team: {team_name}")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating team insights: {str(e)}")
            return {'error': str(e)}
