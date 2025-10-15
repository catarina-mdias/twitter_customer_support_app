"""
Team visualization module for customer support analytics.
Creates interactive charts and graphs for team performance analysis.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TeamVisualizations:
    """Handles creation of team-specific visualizations."""
    
    def __init__(self):
        """Initialize the team visualizations with color schemes."""
        self.team_colors = {
            'excellent': '#2E8B57',  # Sea Green
            'good': '#4682B4',       # Steel Blue
            'average': '#FF8C00',    # Dark Orange
            'poor': '#DC143C',       # Crimson
            'critical': '#8B0000',   # Dark Red
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd'
        }
        
        self.layout_config = {
            'font': {'family': 'Arial, sans-serif', 'size': 12},
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'margin': {'l': 50, 'r': 50, 't': 50, 'b': 50}
        }
    
    def create_team_performance_radar(self, team_metrics: Dict[str, float], team_name: str) -> go.Figure:
        """
        Create a radar chart showing team performance across multiple dimensions.
        
        Args:
            team_metrics: Dictionary with performance metrics
            team_name: Name of the team
            
        Returns:
            go.Figure: Plotly radar chart
        """
        try:
            # Define performance dimensions
            dimensions = [
                'Efficiency',
                'Quality',
                'Consistency',
                'Capacity',
                'Response Time',
                'SLA Compliance'
            ]
            
            # Extract values for radar chart
            values = [
                team_metrics.get('efficiency_score', 0),
                team_metrics.get('quality_score', 0),
                team_metrics.get('consistency_score', 0),
                team_metrics.get('capacity_utilization', 0),
                100 - (team_metrics.get('avg_response_time', 0) / 60) * 100,  # Invert response time
                team_metrics.get('sla_compliance', 0) * 100
            ]
            
            # Ensure values are within 0-100 range
            values = [max(0, min(100, v)) for v in values]
            
            # Create radar chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=dimensions,
                fill='toself',
                name=team_name,
                line_color=self.team_colors['primary'],
                fillcolor=f"rgba(31, 119, 180, 0.3)"
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        tickfont=dict(size=10)
                    )
                ),
                title=f"Team Performance Radar - {team_name}",
                height=500,
                showlegend=True,
                **self.layout_config
            )
            
            logger.info(f"Created team performance radar for {team_name}")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating team performance radar: {str(e)}")
            return self._create_error_chart("Error creating radar chart")
    
    def create_team_comparison_chart(self, comparison_data: pd.DataFrame) -> go.Figure:
        """
        Create a bar chart comparing teams across multiple metrics.
        
        Args:
            comparison_data: DataFrame with team comparison metrics
            
        Returns:
            go.Figure: Plotly bar chart
        """
        try:
            if comparison_data.empty:
                return self._create_error_chart("No team comparison data available")
            
            # Create subplot with multiple metrics
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Overall Score', 'SLA Compliance', 'Avg Response Time', 'Positive Rate'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Overall Score
            fig.add_trace(
                go.Bar(
                    x=comparison_data['Team'],
                    y=comparison_data['Overall Score'],
                    name='Overall Score',
                    marker_color=self.team_colors['primary'],
                    text=comparison_data['Overall Score'].round(1),
                    textposition='auto'
                ),
                row=1, col=1
            )
            
            # SLA Compliance
            fig.add_trace(
                go.Bar(
                    x=comparison_data['Team'],
                    y=comparison_data['SLA Compliance (%)'],
                    name='SLA Compliance',
                    marker_color=self.team_colors['success'],
                    text=comparison_data['SLA Compliance (%)'].round(1),
                    textposition='auto'
                ),
                row=1, col=2
            )
            
            # Average Response Time
            fig.add_trace(
                go.Bar(
                    x=comparison_data['Team'],
                    y=comparison_data['Avg Response Time (min)'],
                    name='Avg Response Time',
                    marker_color=self.team_colors['warning'],
                    text=comparison_data['Avg Response Time (min)'].round(1),
                    textposition='auto'
                ),
                row=2, col=1
            )
            
            # Positive Rate
            fig.add_trace(
                go.Bar(
                    x=comparison_data['Team'],
                    y=comparison_data['Positive Rate (%)'],
                    name='Positive Rate',
                    marker_color=self.team_colors['info'],
                    text=comparison_data['Positive Rate (%)'].round(1),
                    textposition='auto'
                ),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                title="Team Performance Comparison",
                height=600,
                showlegend=False,
                **self.layout_config
            )
            
            # Update axes
            fig.update_xaxes(title_text="Team", row=2, col=1)
            fig.update_xaxes(title_text="Team", row=2, col=2)
            fig.update_yaxes(title_text="Score", row=1, col=1)
            fig.update_yaxes(title_text="Compliance %", row=1, col=2)
            fig.update_yaxes(title_text="Minutes", row=2, col=1)
            fig.update_yaxes(title_text="Positive %", row=2, col=2)
            
            logger.info("Created team comparison chart")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating team comparison chart: {str(e)}")
            return self._create_error_chart("Error creating comparison chart")
    
    def create_team_rankings_chart(self, rankings_data: pd.DataFrame) -> go.Figure:
        """
        Create a horizontal bar chart showing team rankings.
        
        Args:
            rankings_data: DataFrame with team rankings
            
        Returns:
            go.Figure: Plotly bar chart
        """
        try:
            if rankings_data.empty:
                return self._create_error_chart("No ranking data available")
            
            # Sort by score (highest first)
            rankings_data = rankings_data.sort_values('Score', ascending=True)
            
            # Create color mapping based on performance level
            color_map = {
                'Excellent': self.team_colors['excellent'],
                'Good': self.team_colors['good'],
                'Average': self.team_colors['average'],
                'Poor': self.team_colors['poor'],
                'Critical': self.team_colors['critical']
            }
            
            colors = [color_map.get(level, self.team_colors['primary']) 
                     for level in rankings_data['Performance Level']]
            
            # Create horizontal bar chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                y=rankings_data['Team'],
                x=rankings_data['Score'],
                orientation='h',
                marker_color=colors,
                text=rankings_data['Score'].round(1),
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}<br>Rank: %{customdata}<extra></extra>',
                customdata=rankings_data['Rank']
            ))
            
            # Add rank annotations
            for i, (idx, row) in enumerate(rankings_data.iterrows()):
                fig.add_annotation(
                    x=row['Score'] + 1,
                    y=i,
                    text=f"#{row['Rank']}",
                    showarrow=False,
                    font=dict(size=12, color="gray")
                )
            
            fig.update_layout(
                title="Team Performance Rankings",
                xaxis_title="Performance Score",
                yaxis_title="Team",
                height=max(400, len(rankings_data) * 40),
                showlegend=False,
                **self.layout_config
            )
            
            logger.info("Created team rankings chart")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating team rankings chart: {str(e)}")
            return self._create_error_chart("Error creating rankings chart")
    
    def create_team_trends_chart(self, trends_data: Dict[str, Any]) -> go.Figure:
        """
        Create a line chart showing team performance trends over time.
        
        Args:
            trends_data: Dictionary with team trend data
            
        Returns:
            go.Figure: Plotly line chart
        """
        try:
            if not trends_data:
                return self._create_error_chart("No trend data available")
            
            fig = go.Figure()
            
            # Add trend lines for each team
            for team_name, team_trends in trends_data.items():
                if 'data_points' not in team_trends or team_trends['data_points'] < 2:
                    continue
                
                # Create trend line data
                x_values = list(range(team_trends['data_points']))
                y_values = [50 + team_trends['response_time_trend'] * i for i in x_values]  # Simulated trend
                
                fig.add_trace(go.Scatter(
                    x=x_values,
                    y=y_values,
                    mode='lines+markers',
                    name=team_name,
                    line=dict(width=3),
                    marker=dict(size=6)
                ))
            
            fig.update_layout(
                title="Team Performance Trends Over Time",
                xaxis_title="Time Period",
                yaxis_title="Performance Score",
                height=500,
                showlegend=True,
                **self.layout_config
            )
            
            logger.info("Created team trends chart")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating team trends chart: {str(e)}")
            return self._create_error_chart("Error creating trends chart")
    
    def create_team_heatmap(self, teams_data: Dict[str, pd.DataFrame]) -> go.Figure:
        """
        Create a heatmap showing team performance across different metrics.
        
        Args:
            teams_data: Dictionary with team data
            
        Returns:
            go.Figure: Plotly heatmap
        """
        try:
            if not teams_data:
                return self._create_error_chart("No team data available for heatmap")
            
            # Prepare heatmap data
            teams = list(teams_data.keys())
            metrics = ['Response Time', 'SLA Compliance', 'Sentiment', 'Efficiency', 'Volume']
            
            # Calculate metric scores for each team
            heatmap_data = []
            for team_name, team_df in teams_data.items():
                if team_df.empty:
                    continue
                
                team_scores = []
                
                # Response Time Score (inverted - lower is better)
                if 'response_time_minutes' in team_df.columns:
                    avg_rt = team_df['response_time_minutes'].mean()
                    rt_score = max(0, 100 - (avg_rt / 60) * 100)
                else:
                    rt_score = 50
                team_scores.append(rt_score)
                
                # SLA Compliance Score
                if 'response_time_minutes' in team_df.columns:
                    sla_score = (team_df['response_time_minutes'] <= 60).mean() * 100
                else:
                    sla_score = 50
                team_scores.append(sla_score)
                
                # Sentiment Score
                if 'combined_score' in team_df.columns:
                    sentiment_score = (team_df['combined_score'].mean() + 1) * 50
                else:
                    sentiment_score = 50
                team_scores.append(sentiment_score)
                
                # Efficiency Score (based on ticket count)
                efficiency_score = min(100, (len(team_df) / 30) * 100)  # Scale based on 30-day period
                team_scores.append(efficiency_score)
                
                # Volume Score (based on ticket count)
                volume_score = min(100, (len(team_df) / 20) * 100)  # Scale based on 20 tickets target
                team_scores.append(volume_score)
                
                heatmap_data.append(team_scores)
            
            if not heatmap_data:
                return self._create_error_chart("No valid team data for heatmap")
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data,
                x=metrics,
                y=teams,
                colorscale='RdYlGn',
                zmin=0,
                zmax=100,
                hovertemplate='<b>%{y}</b><br>%{x}: %{z:.1f}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Team Performance Heatmap",
                xaxis_title="Performance Metrics",
                yaxis_title="Teams",
                height=max(400, len(teams) * 50),
                **self.layout_config
            )
            
            logger.info("Created team performance heatmap")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating team heatmap: {str(e)}")
            return self._create_error_chart("Error creating heatmap")
    
    def create_team_insights_dashboard(self, insights_data: Dict[str, Any]) -> go.Figure:
        """
        Create a comprehensive team insights dashboard.
        
        Args:
            insights_data: Dictionary with team insights data
            
        Returns:
            go.Figure: Plotly dashboard
        """
        try:
            if not insights_data:
                return self._create_error_chart("No insights data available")
            
            # Create subplot with multiple insights
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    'Performance Distribution',
                    'Improvement Areas',
                    'Strengths vs Weaknesses',
                    'Performance Level Distribution'
                ),
                specs=[[{"type": "histogram"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "pie"}]]
            )
            
            # Performance Distribution (simulated data)
            performance_scores = [insights_data.get('overall_score', 0)]
            fig.add_trace(
                go.Histogram(
                    x=performance_scores,
                    nbinsx=10,
                    marker_color=self.team_colors['primary'],
                    name="Performance Score"
                ),
                row=1, col=1
            )
            
            # Improvement Areas
            improvement_areas = insights_data.get('improvement_areas', [])
            if improvement_areas:
                area_counts = pd.Series(improvement_areas).value_counts()
                fig.add_trace(
                    go.Bar(
                        x=area_counts.index,
                        y=area_counts.values,
                        marker_color=self.team_colors['warning'],
                        name="Improvement Areas"
                    ),
                    row=1, col=2
                )
            
            # Strengths vs Weaknesses
            strengths = insights_data.get('strengths', [])
            weaknesses = insights_data.get('weaknesses', [])
            
            fig.add_trace(
                go.Bar(
                    x=['Strengths', 'Weaknesses'],
                    y=[len(strengths), len(weaknesses)],
                    marker_color=[self.team_colors['success'], self.team_colors['warning']],
                    name="Strengths vs Weaknesses"
                ),
                row=2, col=1
            )
            
            # Performance Level Distribution
            performance_level = insights_data.get('performance_level', 'Average')
            level_counts = {performance_level: 1}
            
            fig.add_trace(
                go.Pie(
                    labels=list(level_counts.keys()),
                    values=list(level_counts.values()),
                    marker_colors=[self.team_colors.get(performance_level.lower(), self.team_colors['primary'])],
                    name="Performance Level"
                ),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                title="Team Performance Insights Dashboard",
                height=600,
                showlegend=False,
                **self.layout_config
            )
            
            logger.info("Created team insights dashboard")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating team insights dashboard: {str(e)}")
            return self._create_error_chart("Error creating insights dashboard")
    
    def create_team_benchmarks_chart(self, benchmarks_data: Dict[str, Any]) -> go.Figure:
        """
        Create a chart showing team performance benchmarks.
        
        Args:
            benchmarks_data: Dictionary with benchmark data
            
        Returns:
            go.Figure: Plotly chart
        """
        try:
            if not benchmarks_data or 'overall_score' not in benchmarks_data:
                return self._create_error_chart("No benchmark data available")
            
            # Extract benchmark data
            overall_benchmarks = benchmarks_data['overall_score']
            
            # Create benchmark indicators
            fig = go.Figure()
            
            # Add benchmark lines
            benchmark_values = [
                overall_benchmarks['min'],
                overall_benchmarks['median'],
                overall_benchmarks['mean'],
                overall_benchmarks['max']
            ]
            
            benchmark_labels = ['Minimum', 'Median', 'Mean', 'Maximum']
            colors = [self.team_colors['critical'], self.team_colors['average'], 
                     self.team_colors['good'], self.team_colors['excellent']]
            
            for value, label, color in zip(benchmark_values, benchmark_labels, colors):
                fig.add_trace(go.Scatter(
                    x=[0, 1],
                    y=[value, value],
                    mode='lines',
                    name=label,
                    line=dict(color=color, width=3, dash='dash'),
                    hovertemplate=f'{label}: {value:.1f}<extra></extra>'
                ))
            
            # Add standard deviation range
            mean_val = overall_benchmarks['mean']
            std_val = overall_benchmarks['std']
            
            fig.add_trace(go.Scatter(
                x=[0, 1, 1, 0, 0],
                y=[mean_val - std_val, mean_val - std_val, mean_val + std_val, mean_val + std_val, mean_val - std_val],
                fill='toself',
                fillcolor='rgba(0,100,80,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Standard Deviation Range',
                hoverinfo='skip'
            ))
            
            fig.update_layout(
                title="Team Performance Benchmarks",
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis_title="Performance Score",
                height=400,
                showlegend=True,
                **self.layout_config
            )
            
            logger.info("Created team benchmarks chart")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating team benchmarks chart: {str(e)}")
            return self._create_error_chart("Error creating benchmarks chart")
    
    def _create_error_chart(self, error_message: str) -> go.Figure:
        """
        Create a simple error chart when visualization fails.
        
        Args:
            error_message: Error message to display
            
        Returns:
            go.Figure: Simple error chart
        """
        fig = go.Figure()
        fig.add_annotation(
            text=error_message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="red")
        )
        fig.update_layout(
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            height=300
        )
        return fig
