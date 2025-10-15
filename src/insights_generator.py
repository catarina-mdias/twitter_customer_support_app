"""
Insights generator module for customer support analytics.
Handles automated generation of insights and recommendations for team performance.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InsightsGenerator:
    """Handles automated generation of insights and recommendations."""
    
    def __init__(self):
        """Initialize the insights generator."""
        self.insight_templates = {
            'response_time': {
                'excellent': "Outstanding response time performance! Keep up the great work.",
                'good': "Good response time performance with room for minor improvements.",
                'average': "Response times are acceptable but could be improved with process optimization.",
                'poor': "Response times need significant improvement. Consider implementing prioritization systems.",
                'critical': "Response times are critically high. Immediate action required."
            },
            'quality': {
                'excellent': "Exceptional customer satisfaction! Your team is delivering outstanding service.",
                'good': "Good customer satisfaction levels. Continue focusing on quality service.",
                'average': "Customer satisfaction is acceptable but could be enhanced with better communication.",
                'poor': "Customer satisfaction needs improvement. Consider additional training and process review.",
                'critical': "Customer satisfaction is critically low. Immediate intervention required."
            },
            'efficiency': {
                'excellent': "Excellent efficiency! Your team is processing tickets at an optimal rate.",
                'good': "Good efficiency levels. Minor optimizations could further improve performance.",
                'average': "Efficiency is acceptable but could be improved with better resource allocation.",
                'poor': "Efficiency needs improvement. Consider process automation and workflow optimization.",
                'critical': "Efficiency is critically low. Immediate process review and optimization required."
            },
            'consistency': {
                'excellent': "Outstanding consistency! Your team maintains stable performance across all metrics.",
                'good': "Good consistency levels. Minor standardization could further improve stability.",
                'average': "Consistency is acceptable but could be improved with better process standardization.",
                'poor': "Consistency needs improvement. Consider implementing standardized procedures.",
                'critical': "Consistency is critically low. Immediate standardization and training required."
            }
        }
        
        self.recommendation_templates = {
            'response_time': [
                "Implement ticket prioritization system based on urgency and impact",
                "Set up automated routing to appropriate team members",
                "Create response time alerts and monitoring dashboard",
                "Provide additional training on quick resolution techniques",
                "Review and optimize current processes for faster resolution"
            ],
            'quality': [
                "Conduct customer service training sessions",
                "Implement customer feedback collection and analysis",
                "Create knowledge base for common issues and solutions",
                "Establish quality assurance processes and reviews",
                "Improve communication templates and response guidelines"
            ],
            'efficiency': [
                "Automate repetitive tasks and processes",
                "Implement workflow management tools",
                "Optimize resource allocation and workload distribution",
                "Create performance dashboards for real-time monitoring",
                "Establish clear escalation procedures and guidelines"
            ],
            'consistency': [
                "Standardize response procedures and templates",
                "Implement regular training and knowledge sharing sessions",
                "Create detailed process documentation and guidelines",
                "Establish quality control checkpoints and reviews",
                "Implement performance monitoring and feedback systems"
            ]
        }
        
        logger.info("Insights generator initialized")
    
    def generate_team_insights(self, team_data: pd.DataFrame, team_name: str, 
                             performance_metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate comprehensive insights for a team.
        
        Args:
            team_data: DataFrame with team performance data
            team_name: Name of the team
            performance_metrics: Dictionary with performance metrics
            
        Returns:
            Dict[str, Any]: Generated insights
        """
        try:
            if team_data.empty:
                return {'error': 'No data available for insights generation'}
            
            insights = {
                'team_name': team_name,
                'generated_at': datetime.now().isoformat(),
                'overall_assessment': {},
                'detailed_insights': {},
                'recommendations': [],
                'action_items': [],
                'priority_level': 'Medium',
                'key_metrics': performance_metrics
            }
            
            # Generate overall assessment
            overall_score = performance_metrics.get('overall_score', 0)
            insights['overall_assessment'] = self._assess_overall_performance(overall_score)
            
            # Generate detailed insights for each metric
            insights['detailed_insights'] = self._generate_detailed_insights(performance_metrics)
            
            # Generate recommendations
            insights['recommendations'] = self._generate_recommendations(performance_metrics, team_data)
            
            # Generate action items
            insights['action_items'] = self._generate_action_items(performance_metrics, team_data)
            
            # Determine priority level
            insights['priority_level'] = self._determine_priority_level(performance_metrics)
            
            # Generate specific insights based on data patterns
            insights['data_insights'] = self._analyze_data_patterns(team_data)
            
            logger.info(f"Generated insights for team: {team_name}")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating team insights: {str(e)}")
            return {'error': str(e)}
    
    def generate_comparative_insights(self, teams_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Generate comparative insights across multiple teams.
        
        Args:
            teams_data: Dictionary with team data
            
        Returns:
            Dict[str, Any]: Comparative insights
        """
        try:
            if not teams_data:
                return {'error': 'No team data available for comparative analysis'}
            
            comparative_insights = {
                'generated_at': datetime.now().isoformat(),
                'team_rankings': {},
                'best_practices': [],
                'improvement_opportunities': [],
                'benchmark_analysis': {},
                'recommendations': []
            }
            
            # Calculate team rankings
            team_scores = {}
            for team_name, team_df in teams_data.items():
                if team_df.empty:
                    continue
                
                # Calculate basic metrics
                if 'response_time_minutes' in team_df.columns:
                    avg_rt = team_df['response_time_minutes'].mean()
                    sla_compliance = (team_df['response_time_minutes'] <= 60).mean()
                else:
                    avg_rt = 0
                    sla_compliance = 0
                
                if 'combined_score' in team_df.columns:
                    avg_sentiment = team_df['combined_score'].mean()
                else:
                    avg_sentiment = 0
                
                team_scores[team_name] = {
                    'avg_response_time': avg_rt,
                    'sla_compliance': sla_compliance,
                    'avg_sentiment': avg_sentiment,
                    'ticket_count': len(team_df)
                }
            
            # Generate rankings
            comparative_insights['team_rankings'] = self._generate_team_rankings(team_scores)
            
            # Identify best practices
            comparative_insights['best_practices'] = self._identify_best_practices(team_scores)
            
            # Identify improvement opportunities
            comparative_insights['improvement_opportunities'] = self._identify_improvement_opportunities(team_scores)
            
            # Generate benchmark analysis
            comparative_insights['benchmark_analysis'] = self._generate_benchmark_analysis(team_scores)
            
            # Generate recommendations
            comparative_insights['recommendations'] = self._generate_comparative_recommendations(team_scores)
            
            logger.info(f"Generated comparative insights for {len(teams_data)} teams")
            return comparative_insights
            
        except Exception as e:
            logger.error(f"Error generating comparative insights: {str(e)}")
            return {'error': str(e)}
    
    def generate_trend_insights(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate insights based on performance trends.
        
        Args:
            historical_data: DataFrame with historical performance data
            
        Returns:
            Dict[str, Any]: Trend insights
        """
        try:
            if historical_data.empty or 'created_at' not in historical_data.columns:
                return {'error': 'No historical data available for trend analysis'}
            
            # Ensure date column is datetime
            historical_data['created_at'] = pd.to_datetime(historical_data['created_at'])
            
            trend_insights = {
                'generated_at': datetime.now().isoformat(),
                'trend_analysis': {},
                'forecast_insights': [],
                'seasonal_patterns': {},
                'recommendations': []
            }
            
            # Analyze trends by team
            for team in historical_data['team'].unique():
                team_data = historical_data[historical_data['team'] == team]
                
                if len(team_data) < 2:
                    continue
                
                # Calculate trend metrics
                team_trends = self._calculate_team_trends(team_data)
                trend_insights['trend_analysis'][team] = team_trends
            
            # Generate forecast insights
            trend_insights['forecast_insights'] = self._generate_forecast_insights(trend_insights['trend_analysis'])
            
            # Identify seasonal patterns
            trend_insights['seasonal_patterns'] = self._identify_seasonal_patterns(historical_data)
            
            # Generate trend-based recommendations
            trend_insights['recommendations'] = self._generate_trend_recommendations(trend_insights['trend_analysis'])
            
            logger.info("Generated trend insights")
            return trend_insights
            
        except Exception as e:
            logger.error(f"Error generating trend insights: {str(e)}")
            return {'error': str(e)}
    
    def _assess_overall_performance(self, overall_score: float) -> Dict[str, Any]:
        """Assess overall performance level."""
        if overall_score >= 90:
            level = 'excellent'
            description = "Outstanding performance across all metrics"
        elif overall_score >= 75:
            level = 'good'
            description = "Good performance with minor areas for improvement"
        elif overall_score >= 60:
            level = 'average'
            description = "Average performance with several improvement opportunities"
        elif overall_score >= 45:
            level = 'poor'
            description = "Below average performance requiring attention"
        else:
            level = 'critical'
            description = "Critical performance issues requiring immediate intervention"
        
        return {
            'level': level,
            'score': overall_score,
            'description': description
        }
    
    def _generate_detailed_insights(self, performance_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Generate detailed insights for each performance metric."""
        insights = {}
        
        # Response time insights
        if 'avg_response_time' in performance_metrics:
            rt_score = performance_metrics['avg_response_time']
            if rt_score <= 15:
                level = 'excellent'
            elif rt_score <= 30:
                level = 'good'
            elif rt_score <= 60:
                level = 'average'
            elif rt_score <= 120:
                level = 'poor'
            else:
                level = 'critical'
            
            insights['response_time'] = {
                'level': level,
                'message': self.insight_templates['response_time'][level],
                'score': rt_score
            }
        
        # Quality insights
        if 'avg_sentiment' in performance_metrics:
            sentiment_score = performance_metrics['avg_sentiment']
            if sentiment_score >= 0.5:
                level = 'excellent'
            elif sentiment_score >= 0.2:
                level = 'good'
            elif sentiment_score >= 0.0:
                level = 'average'
            elif sentiment_score >= -0.2:
                level = 'poor'
            else:
                level = 'critical'
            
            insights['quality'] = {
                'level': level,
                'message': self.insight_templates['quality'][level],
                'score': sentiment_score
            }
        
        # Efficiency insights
        if 'efficiency_score' in performance_metrics:
            eff_score = performance_metrics['efficiency_score']
            if eff_score >= 90:
                level = 'excellent'
            elif eff_score >= 75:
                level = 'good'
            elif eff_score >= 60:
                level = 'average'
            elif eff_score >= 45:
                level = 'poor'
            else:
                level = 'critical'
            
            insights['efficiency'] = {
                'level': level,
                'message': self.insight_templates['efficiency'][level],
                'score': eff_score
            }
        
        # Consistency insights
        if 'consistency_score' in performance_metrics:
            cons_score = performance_metrics['consistency_score']
            if cons_score >= 90:
                level = 'excellent'
            elif cons_score >= 75:
                level = 'good'
            elif cons_score >= 60:
                level = 'average'
            elif cons_score >= 45:
                level = 'poor'
            else:
                level = 'critical'
            
            insights['consistency'] = {
                'level': level,
                'message': self.insight_templates['consistency'][level],
                'score': cons_score
            }
        
        return insights
    
    def _generate_recommendations(self, performance_metrics: Dict[str, float], 
                                team_data: pd.DataFrame) -> List[str]:
        """Generate recommendations based on performance metrics."""
        recommendations = []
        
        # Response time recommendations
        if 'avg_response_time' in performance_metrics and performance_metrics['avg_response_time'] > 30:
            recommendations.extend(self.recommendation_templates['response_time'][:2])
        
        # Quality recommendations
        if 'avg_sentiment' in performance_metrics and performance_metrics['avg_sentiment'] < 0.2:
            recommendations.extend(self.recommendation_templates['quality'][:2])
        
        # Efficiency recommendations
        if 'efficiency_score' in performance_metrics and performance_metrics['efficiency_score'] < 70:
            recommendations.extend(self.recommendation_templates['efficiency'][:2])
        
        # Consistency recommendations
        if 'consistency_score' in performance_metrics and performance_metrics['consistency_score'] < 70:
            recommendations.extend(self.recommendation_templates['consistency'][:2])
        
        # Remove duplicates and limit to top 5
        recommendations = list(dict.fromkeys(recommendations))[:5]
        
        return recommendations
    
    def _generate_action_items(self, performance_metrics: Dict[str, float], 
                             team_data: pd.DataFrame) -> List[Dict[str, str]]:
        """Generate specific action items based on performance metrics."""
        action_items = []
        
        # Response time action items
        if 'avg_response_time' in performance_metrics and performance_metrics['avg_response_time'] > 45:
            action_items.append({
                'category': 'Response Time',
                'action': 'Implement ticket prioritization system',
                'priority': 'High',
                'timeline': '1-2 weeks'
            })
        
        # Quality action items
        if 'avg_sentiment' in performance_metrics and performance_metrics['avg_sentiment'] < 0.0:
            action_items.append({
                'category': 'Quality',
                'action': 'Conduct customer service training',
                'priority': 'High',
                'timeline': '2-3 weeks'
            })
        
        # Efficiency action items
        if 'efficiency_score' in performance_metrics and performance_metrics['efficiency_score'] < 60:
            action_items.append({
                'category': 'Efficiency',
                'action': 'Review and optimize current processes',
                'priority': 'Medium',
                'timeline': '3-4 weeks'
            })
        
        # Consistency action items
        if 'consistency_score' in performance_metrics and performance_metrics['consistency_score'] < 60:
            action_items.append({
                'category': 'Consistency',
                'action': 'Standardize response procedures',
                'priority': 'Medium',
                'timeline': '2-3 weeks'
            })
        
        return action_items
    
    def _determine_priority_level(self, performance_metrics: Dict[str, float]) -> str:
        """Determine priority level based on performance metrics."""
        critical_count = 0
        poor_count = 0
        
        # Count critical and poor performance areas
        for metric, score in performance_metrics.items():
            if 'response_time' in metric and score > 60:
                critical_count += 1
            elif 'sentiment' in metric and score < -0.2:
                critical_count += 1
            elif 'score' in metric and score < 45:
                critical_count += 1
            elif 'score' in metric and score < 60:
                poor_count += 1
        
        if critical_count >= 2:
            return 'Critical'
        elif critical_count >= 1 or poor_count >= 3:
            return 'High'
        elif poor_count >= 1:
            return 'Medium'
        else:
            return 'Low'
    
    def _analyze_data_patterns(self, team_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data patterns to generate additional insights."""
        patterns = {}
        
        # Response time patterns
        if 'response_time_minutes' in team_data.columns:
            rt_std = team_data['response_time_minutes'].std()
            rt_mean = team_data['response_time_minutes'].mean()
            
            if rt_std / rt_mean > 1.0:  # High coefficient of variation
                patterns['response_time_consistency'] = 'High variability in response times'
            else:
                patterns['response_time_consistency'] = 'Consistent response times'
        
        # Sentiment patterns
        if 'combined_score' in team_data.columns:
            sentiment_std = team_data['combined_score'].std()
            if sentiment_std > 0.5:
                patterns['sentiment_consistency'] = 'High variability in customer sentiment'
            else:
                patterns['sentiment_consistency'] = 'Consistent customer sentiment'
        
        # Volume patterns
        if 'created_at' in team_data.columns:
            team_data['created_at'] = pd.to_datetime(team_data['created_at'])
            daily_volume = team_data.groupby(team_data['created_at'].dt.date).size()
            
            if daily_volume.std() > daily_volume.mean() * 0.5:
                patterns['volume_consistency'] = 'High variability in daily ticket volume'
            else:
                patterns['volume_consistency'] = 'Consistent daily ticket volume'
        
        return patterns
    
    def _generate_team_rankings(self, team_scores: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
        """Generate team rankings based on performance scores."""
        rankings = []
        
        for team_name, scores in team_scores.items():
            # Calculate overall score (weighted average)
            overall_score = (
                scores.get('sla_compliance', 0) * 0.4 +
                (1 - scores.get('avg_response_time', 60) / 60) * 0.3 +
                (scores.get('avg_sentiment', 0) + 1) * 25 * 0.3
            )
            
            rankings.append({
                'team': team_name,
                'overall_score': round(overall_score, 2),
                'sla_compliance': scores.get('sla_compliance', 0),
                'avg_response_time': scores.get('avg_response_time', 0),
                'avg_sentiment': scores.get('avg_sentiment', 0),
                'ticket_count': scores.get('ticket_count', 0)
            })
        
        # Sort by overall score
        rankings.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # Add rank
        for i, ranking in enumerate(rankings):
            ranking['rank'] = i + 1
        
        return rankings
    
    def _identify_best_practices(self, team_scores: Dict[str, Dict[str, float]]) -> List[str]:
        """Identify best practices from top-performing teams."""
        best_practices = []
        
        # Find top performers
        top_teams = sorted(team_scores.items(), 
                          key=lambda x: x[1].get('sla_compliance', 0), reverse=True)[:2]
        
        for team_name, scores in top_teams:
            if scores.get('sla_compliance', 0) > 0.9:
                best_practices.append(f"{team_name} maintains excellent SLA compliance (>90%)")
            
            if scores.get('avg_response_time', 60) < 20:
                best_practices.append(f"{team_name} achieves fast response times (<20 min)")
            
            if scores.get('avg_sentiment', 0) > 0.3:
                best_practices.append(f"{team_name} maintains high customer satisfaction")
        
        return best_practices
    
    def _identify_improvement_opportunities(self, team_scores: Dict[str, Dict[str, float]]) -> List[str]:
        """Identify improvement opportunities from underperforming teams."""
        opportunities = []
        
        # Find underperformers
        bottom_teams = sorted(team_scores.items(), 
                             key=lambda x: x[1].get('sla_compliance', 0))[:2]
        
        for team_name, scores in bottom_teams:
            if scores.get('sla_compliance', 0) < 0.7:
                opportunities.append(f"{team_name} needs SLA compliance improvement (<70%)")
            
            if scores.get('avg_response_time', 60) > 45:
                opportunities.append(f"{team_name} needs response time improvement (>45 min)")
            
            if scores.get('avg_sentiment', 0) < -0.1:
                opportunities.append(f"{team_name} needs customer satisfaction improvement")
        
        return opportunities
    
    def _generate_benchmark_analysis(self, team_scores: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Generate benchmark analysis across teams."""
        if not team_scores:
            return {}
        
        # Calculate benchmarks
        sla_values = [scores.get('sla_compliance', 0) for scores in team_scores.values()]
        rt_values = [scores.get('avg_response_time', 60) for scores in team_scores.values()]
        sentiment_values = [scores.get('avg_sentiment', 0) for scores in team_scores.values()]
        
        return {
            'sla_compliance': {
                'mean': np.mean(sla_values),
                'median': np.median(sla_values),
                'std': np.std(sla_values),
                'min': np.min(sla_values),
                'max': np.max(sla_values)
            },
            'response_time': {
                'mean': np.mean(rt_values),
                'median': np.median(rt_values),
                'std': np.std(rt_values),
                'min': np.min(rt_values),
                'max': np.max(rt_values)
            },
            'sentiment': {
                'mean': np.mean(sentiment_values),
                'median': np.median(sentiment_values),
                'std': np.std(sentiment_values),
                'min': np.min(sentiment_values),
                'max': np.max(sentiment_values)
            }
        }
    
    def _generate_comparative_recommendations(self, team_scores: Dict[str, Dict[str, float]]) -> List[str]:
        """Generate recommendations based on comparative analysis."""
        recommendations = []
        
        # Find performance gaps
        sla_values = [scores.get('sla_compliance', 0) for scores in team_scores.values()]
        rt_values = [scores.get('avg_response_time', 60) for scores in team_scores.values()]
        
        if max(sla_values) - min(sla_values) > 0.3:
            recommendations.append("Significant SLA compliance gap between teams - implement knowledge sharing")
        
        if max(rt_values) - min(rt_values) > 30:
            recommendations.append("Large response time variation between teams - standardize processes")
        
        return recommendations
    
    def _calculate_team_trends(self, team_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate trend metrics for a team."""
        if len(team_data) < 2:
            return {}
        
        # Sort by date
        team_data = team_data.sort_values('created_at')
        
        # Calculate trend slopes
        x = np.arange(len(team_data))
        
        trends = {}
        
        if 'response_time_minutes' in team_data.columns:
            rt_trend = np.polyfit(x, team_data['response_time_minutes'], 1)[0]
            trends['response_time_trend'] = rt_trend
            trends['response_time_improving'] = rt_trend < 0
        
        if 'combined_score' in team_data.columns:
            sentiment_trend = np.polyfit(x, team_data['combined_score'], 1)[0]
            trends['sentiment_trend'] = sentiment_trend
            trends['sentiment_improving'] = sentiment_trend > 0
        
        return trends
    
    def _generate_forecast_insights(self, trend_analysis: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate forecast insights based on trend analysis."""
        insights = []
        
        for team, trends in trend_analysis.items():
            if trends.get('response_time_improving', False):
                insights.append(f"{team} is improving response times - continue current practices")
            elif trends.get('response_time_trend', 0) > 5:
                insights.append(f"{team} response times are deteriorating - immediate action needed")
            
            if trends.get('sentiment_improving', False):
                insights.append(f"{team} customer satisfaction is improving - maintain quality focus")
            elif trends.get('sentiment_trend', 0) < -0.1:
                insights.append(f"{team} customer satisfaction is declining - review service quality")
        
        return insights
    
    def _identify_seasonal_patterns(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Identify seasonal patterns in the data."""
        patterns = {}
        
        if 'created_at' not in historical_data.columns:
            return patterns
        
        # Analyze by day of week
        historical_data['day_of_week'] = historical_data['created_at'].dt.day_name()
        daily_patterns = historical_data.groupby('day_of_week').size()
        
        if not daily_patterns.empty:
            patterns['day_of_week'] = daily_patterns.to_dict()
        
        # Analyze by hour
        historical_data['hour'] = historical_data['created_at'].dt.hour
        hourly_patterns = historical_data.groupby('hour').size()
        
        if not hourly_patterns.empty:
            patterns['hourly'] = hourly_patterns.to_dict()
        
        return patterns
    
    def _generate_trend_recommendations(self, trend_analysis: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on trend analysis."""
        recommendations = []
        
        declining_teams = []
        improving_teams = []
        
        for team, trends in trend_analysis.items():
            if trends.get('response_time_trend', 0) > 5:
                declining_teams.append(team)
            elif trends.get('response_time_improving', False):
                improving_teams.append(team)
        
        if declining_teams:
            recommendations.append(f"Teams {', '.join(declining_teams)} need immediate attention for response time issues")
        
        if improving_teams:
            recommendations.append(f"Teams {', '.join(improving_teams)} are performing well - share their best practices")
        
        return recommendations
