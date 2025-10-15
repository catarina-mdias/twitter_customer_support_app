"""
Twitter-specific visualizations for customer support analytics.
Creates charts and graphs specific to Twitter customer support data.
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

class TwitterVisualizations:
    """Handles creation of Twitter-specific visualizations."""
    
    def __init__(self):
        """Initialize the Twitter visualizations with color schemes."""
        self.twitter_colors = {
            'sprintcare': '#FF6B35',      # Sprint Orange
            'verizonsupport': '#CD040B',  # Verizon Red
            'ask_spectrum': '#00A651',     # Spectrum Green
            'chipotletweets': '#FFC72C',  # Chipotle Yellow
            'askplaystation': '#003791',  # PlayStation Blue
            'default': '#1f77b4'          # Default Blue
        }
        
        self.layout_config = {
            'font': {'family': 'Arial, sans-serif', 'size': 12},
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'margin': {'l': 50, 'r': 50, 't': 50, 'b': 50}
        }
    
    def create_twitter_team_performance(self, df: pd.DataFrame) -> go.Figure:
        """
        Create Twitter team performance comparison chart.
        
        Args:
            df: DataFrame with Twitter team data
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            if df.empty or 'team' not in df.columns:
                return self._create_error_chart("No team data available")
            
            # Calculate team metrics
            team_metrics = df.groupby('team').agg({
                'response_time_minutes': ['count', 'median', 'mean'],
                'customer_message': 'count'
            }).round(2)
            
            team_metrics.columns = ['ticket_count', 'median_response_time', 'avg_response_time', 'message_count']
            team_metrics = team_metrics.reset_index()
            
            # Create subplot
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    'Tickets per Team',
                    'Median Response Time by Team',
                    'Average Response Time by Team',
                    'Team Performance Score'
                ),
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "bar"}]]
            )
            
            # Tickets per team
            fig.add_trace(
                go.Bar(
                    x=team_metrics['team'],
                    y=team_metrics['ticket_count'],
                    name="Tickets",
                    marker_color=[self.twitter_colors.get(team.lower(), self.twitter_colors['default']) 
                                 for team in team_metrics['team']]
                ),
                row=1, col=1
            )
            
            # Median response time
            fig.add_trace(
                go.Bar(
                    x=team_metrics['team'],
                    y=team_metrics['median_response_time'],
                    name="Median RT",
                    marker_color=[self.twitter_colors.get(team.lower(), self.twitter_colors['default']) 
                                 for team in team_metrics['team']]
                ),
                row=1, col=2
            )
            
            # Average response time
            fig.add_trace(
                go.Bar(
                    x=team_metrics['team'],
                    y=team_metrics['avg_response_time'],
                    name="Avg RT",
                    marker_color=[self.twitter_colors.get(team.lower(), self.twitter_colors['default']) 
                                 for team in team_metrics['team']]
                ),
                row=2, col=1
            )
            
            # Performance score (inverse of response time)
            team_metrics['performance_score'] = 100 - (team_metrics['median_response_time'] / 60) * 100
            team_metrics['performance_score'] = team_metrics['performance_score'].clip(0, 100)
            
            fig.add_trace(
                go.Bar(
                    x=team_metrics['team'],
                    y=team_metrics['performance_score'],
                    name="Performance",
                    marker_color=[self.twitter_colors.get(team.lower(), self.twitter_colors['default']) 
                                 for team in team_metrics['team']]
                ),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                title="Twitter Customer Support Team Performance",
                height=600,
                showlegend=False,
                **self.layout_config
            )
            
            # Update axes
            fig.update_xaxes(title_text="Team", row=2, col=1)
            fig.update_xaxes(title_text="Team", row=2, col=2)
            fig.update_yaxes(title_text="Count", row=1, col=1)
            fig.update_yaxes(title_text="Minutes", row=1, col=2)
            fig.update_yaxes(title_text="Minutes", row=2, col=1)
            fig.update_yaxes(title_text="Score", row=2, col=2)
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating Twitter team performance chart: {str(e)}")
            return self._create_error_chart("Error creating team performance chart")
    
    def create_twitter_response_time_trend(self, df: pd.DataFrame) -> go.Figure:
        """
        Create Twitter response time trend chart.
        
        Args:
            df: DataFrame with Twitter data
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            if df.empty or 'created_at' not in df.columns or 'response_time_minutes' not in df.columns:
                return self._create_error_chart("No response time data available")
            
            # Create hourly aggregation
            df['hour'] = df['created_at'].dt.hour
            hourly_metrics = df.groupby('hour')['response_time_minutes'].agg(['count', 'median', 'mean']).reset_index()
            
            fig = go.Figure()
            
            # Add median response time line
            fig.add_trace(
                go.Scatter(
                    x=hourly_metrics['hour'],
                    y=hourly_metrics['median'],
                    mode='lines+markers',
                    name='Median Response Time',
                    line=dict(color='#FF6B35', width=3),
                    marker=dict(size=8)
                )
            )
            
            # Add average response time line
            fig.add_trace(
                go.Scatter(
                    x=hourly_metrics['hour'],
                    y=hourly_metrics['mean'],
                    mode='lines+markers',
                    name='Average Response Time',
                    line=dict(color='#CD040B', width=2),
                    marker=dict(size=6)
                )
            )
            
            # Add volume as background bars
            fig.add_trace(
                go.Bar(
                    x=hourly_metrics['hour'],
                    y=hourly_metrics['count'],
                    name='Ticket Volume',
                    opacity=0.3,
                    marker_color='#1f77b4',
                    yaxis='y2'
                )
            )
            
            # Update layout
            fig.update_layout(
                title="Twitter Response Time Trends by Hour",
                xaxis_title="Hour of Day",
                yaxis_title="Response Time (minutes)",
                yaxis2=dict(
                    title="Ticket Volume",
                    overlaying='y',
                    side='right'
                ),
                height=400,
                **self.layout_config
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating Twitter response time trend: {str(e)}")
            return self._create_error_chart("Error creating response time trend")
    
    def create_twitter_sentiment_by_team(self, df: pd.DataFrame) -> go.Figure:
        """
        Create Twitter sentiment analysis by team.
        
        Args:
            df: DataFrame with Twitter sentiment data
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            if df.empty or 'team' not in df.columns or 'category' not in df.columns:
                return self._create_error_chart("No sentiment data available")
            
            # Create sentiment distribution by team
            sentiment_by_team = df.groupby(['team', 'category']).size().reset_index(name='count')
            
            fig = px.bar(
                sentiment_by_team,
                x='team',
                y='count',
                color='category',
                title="Twitter Sentiment Distribution by Team",
                color_discrete_map={
                    'positive': '#2E8B57',
                    'negative': '#DC143C',
                    'neutral': '#4682B4'
                }
            )
            
            fig.update_layout(
                xaxis_title="Team",
                yaxis_title="Number of Messages",
                height=400,
                **self.layout_config
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating Twitter sentiment by team: {str(e)}")
            return self._create_error_chart("Error creating sentiment chart")
    
    def create_twitter_conversation_length_analysis(self, df: pd.DataFrame) -> go.Figure:
        """
        Create conversation length analysis chart.
        
        Args:
            df: DataFrame with Twitter conversation data
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            if df.empty or 'conversation_length' not in df.columns:
                return self._create_error_chart("No conversation length data available")
            
            # Create conversation length distribution
            fig = go.Figure()
            
            # Histogram of conversation lengths
            fig.add_trace(
                go.Histogram(
                    x=df['conversation_length'],
                    nbinsx=20,
                    name='Conversation Length Distribution',
                    marker_color='#1f77b4',
                    opacity=0.7
                )
            )
            
            # Add mean line
            mean_length = df['conversation_length'].mean()
            fig.add_vline(
                x=mean_length,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Mean: {mean_length:.1f}"
            )
            
            fig.update_layout(
                title="Twitter Conversation Length Distribution",
                xaxis_title="Conversation Length (number of tweets)",
                yaxis_title="Frequency",
                height=400,
                **self.layout_config
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating conversation length analysis: {str(e)}")
            return self._create_error_chart("Error creating conversation analysis")
    
    def create_twitter_insights_dashboard(self, df: pd.DataFrame) -> go.Figure:
        """
        Create comprehensive Twitter insights dashboard.
        
        Args:
            df: DataFrame with Twitter data
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            if df.empty:
                return self._create_error_chart("No data available for insights")
            
            # Create subplot with multiple insights
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    'Top Teams by Volume',
                    'Response Time Distribution',
                    'Sentiment by Team',
                    'Conversation Length vs Response Time'
                ),
                specs=[[{"type": "bar"}, {"type": "histogram"}],
                       [{"type": "bar"}, {"type": "scatter"}]]
            )
            
            # Top teams by volume
            team_counts = df['team'].value_counts().head(5)
            fig.add_trace(
                go.Bar(
                    x=team_counts.index,
                    y=team_counts.values,
                    name="Team Volume",
                    marker_color=[self.twitter_colors.get(team.lower(), self.twitter_colors['default']) 
                                 for team in team_counts.index]
                ),
                row=1, col=1
            )
            
            # Response time distribution
            if 'response_time_minutes' in df.columns:
                fig.add_trace(
                    go.Histogram(
                        x=df['response_time_minutes'],
                        nbinsx=20,
                        name="Response Time",
                        marker_color='#4682B4'
                    ),
                    row=1, col=2
                )
            
            # Sentiment by team
            if 'category' in df.columns:
                sentiment_counts = df['category'].value_counts()
                fig.add_trace(
                    go.Bar(
                        x=sentiment_counts.index,
                        y=sentiment_counts.values,
                        name="Sentiment",
                        marker_color=['#2E8B57', '#DC143C', '#4682B4'][:len(sentiment_counts)]
                    ),
                    row=2, col=1
                )
            
            # Conversation length vs response time
            if 'conversation_length' in df.columns and 'response_time_minutes' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['conversation_length'],
                        y=df['response_time_minutes'],
                        mode='markers',
                        name="Length vs RT",
                        marker=dict(color='#FF6B35', size=8, opacity=0.6)
                    ),
                    row=2, col=2
                )
            
            # Update layout
            fig.update_layout(
                title="Twitter Customer Support Insights Dashboard",
                height=600,
                showlegend=False,
                **self.layout_config
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating Twitter insights dashboard: {str(e)}")
            return self._create_error_chart("Error creating insights dashboard")
    
    def _create_error_chart(self, error_message: str) -> go.Figure:
        """
        Create an error chart with message.
        
        Args:
            error_message: Error message to display
            
        Returns:
            go.Figure: Error chart
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
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=300,
            **self.layout_config
        )
        return fig
