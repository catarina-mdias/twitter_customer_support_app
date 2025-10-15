"""
Sentiment visualization module for customer support analytics.
Creates interactive charts and graphs for sentiment analysis data.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentVisualizations:
    """Handles creation of sentiment-specific visualizations."""
    
    def __init__(self):
        """Initialize the sentiment visualizations with color schemes."""
        self.sentiment_colors = {
            'positive': '#2E8B57',  # Sea Green
            'negative': '#DC143C',  # Crimson
            'neutral': '#4682B4',   # Steel Blue
            'positive_light': '#90EE90',  # Light Green
            'negative_light': '#FFB6C1',  # Light Pink
            'neutral_light': '#B0C4DE'    # Light Steel Blue
        }
        
        self.layout_config = {
            'font': {'family': 'Arial, sans-serif', 'size': 12},
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'margin': {'l': 50, 'r': 50, 't': 50, 'b': 50}
        }
    
    def create_sentiment_distribution(self, df: pd.DataFrame) -> go.Figure:
        """
        Create a pie chart showing sentiment distribution.
        
        Args:
            df: DataFrame with sentiment data
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            if df.empty or 'category' not in df.columns:
                return self._create_error_chart("No sentiment data available")
            
            # Count sentiment categories
            sentiment_counts = df['category'].value_counts()
            
            # Create pie chart
            fig = go.Figure(data=[go.Pie(
                labels=sentiment_counts.index,
                values=sentiment_counts.values,
                marker_colors=[self.sentiment_colors.get(cat, '#808080') for cat in sentiment_counts.index],
                textinfo='label+percent+value',
                textposition='auto',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            )])
            
            fig.update_layout(
                title="Sentiment Distribution",
                height=400,
                showlegend=True,
                **self.layout_config
            )
            
            logger.info("Created sentiment distribution chart")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating sentiment distribution chart: {str(e)}")
            return self._create_error_chart("Error creating sentiment distribution")
    
    def create_sentiment_trends(self, df: pd.DataFrame, date_col: str = 'created_at') -> go.Figure:
        """
        Create a line chart showing sentiment trends over time.
        
        Args:
            df: DataFrame with sentiment data and date column
            date_col: Name of the date column
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            if df.empty or date_col not in df.columns or 'category' not in df.columns:
                return self._create_error_chart("No sentiment trend data available")
            
            # Ensure date column is datetime
            df[date_col] = pd.to_datetime(df[date_col])
            
            # Group by date and calculate sentiment metrics
            daily_sentiment = df.groupby(df[date_col].dt.date).agg({
                'category': lambda x: (x == 'positive').sum(),
                'combined_score': 'mean'
            }).reset_index()
            
            daily_sentiment.columns = ['date', 'positive_count', 'avg_sentiment_score']
            
            # Create subplot with secondary y-axis
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Sentiment Score Trends', 'Positive Messages Count'),
                vertical_spacing=0.1,
                specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
            )
            
            # Add sentiment score line
            fig.add_trace(
                go.Scatter(
                    x=daily_sentiment['date'],
                    y=daily_sentiment['avg_sentiment_score'],
                    mode='lines+markers',
                    name='Average Sentiment Score',
                    line=dict(color=self.sentiment_colors['neutral'], width=3),
                    marker=dict(size=6)
                ),
                row=1, col=1
            )
            
            # Add positive messages bar chart
            fig.add_trace(
                go.Bar(
                    x=daily_sentiment['date'],
                    y=daily_sentiment['positive_count'],
                    name='Positive Messages',
                    marker_color=self.sentiment_colors['positive'],
                    opacity=0.7
                ),
                row=2, col=1
            )
            
            # Update layout
            fig.update_layout(
                title="Sentiment Trends Over Time",
                height=600,
                showlegend=True,
                **self.layout_config
            )
            
            # Update axes
            fig.update_xaxes(title_text="Date", row=2, col=1)
            fig.update_yaxes(title_text="Sentiment Score", row=1, col=1)
            fig.update_yaxes(title_text="Positive Messages Count", row=2, col=1)
            
            logger.info("Created sentiment trends chart")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating sentiment trends chart: {str(e)}")
            return self._create_error_chart("Error creating sentiment trends")
    
    def create_sentiment_vs_response_time(self, df: pd.DataFrame) -> go.Figure:
        """
        Create a scatter plot showing sentiment vs response time correlation.
        
        Args:
            df: DataFrame with sentiment and response time data
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            if (df.empty or 'combined_score' not in df.columns or 
                'response_time_minutes' not in df.columns):
                return self._create_error_chart("No correlation data available")
            
            # Filter out rows with NaN values in critical columns
            df_clean = df.dropna(subset=['response_time_minutes', 'combined_score'])
            
            # Remove outliers: cap at 1000 minutes max
            df_clean = df_clean[df_clean['response_time_minutes'] <= 1000]
            
            if len(df_clean) == 0:
                return self._create_error_chart("No valid correlation data available")
            
            # Create scatter plot
            fig = go.Figure()
            
            # Add scatter points colored by sentiment category
            if 'category' in df_clean.columns:
                # Group by category if available
                for category in df_clean['category'].unique():
                    category_data = df_clean[df_clean['category'] == category]
                    
                    fig.add_trace(go.Scatter(
                        x=category_data['response_time_minutes'],
                        y=category_data['combined_score'],
                        mode='markers',
                        name=category.title(),
                        marker=dict(
                            color=self.sentiment_colors.get(category, '#808080'),
                            size=8,
                            opacity=0.6
                        ),
                        text=category_data.get('customer_message', '').str[:100] if 'customer_message' in category_data.columns else '',
                        hovertemplate='<b>%{text}</b><br>Response Time: %{x:.1f} min<br>Sentiment: %{y:.3f}<extra></extra>'
                    ))
            else:
                # No category column, create single trace
                fig.add_trace(go.Scatter(
                    x=df_clean['response_time_minutes'],
                    y=df_clean['combined_score'],
                    mode='markers',
                    name='All Messages',
                    marker=dict(
                        color='#3498db',
                        size=8,
                        opacity=0.6
                    ),
                    text=df_clean.get('customer_message', '').str[:100] if 'customer_message' in df_clean.columns else '',
                    hovertemplate='<b>%{text}</b><br>Response Time: %{x:.1f} min<br>Sentiment: %{y:.3f}<extra></extra>'
                ))
            
            # Add trend line
            if len(df_clean) > 1:
                z = np.polyfit(df_clean['response_time_minutes'], df_clean['combined_score'], 1)
                p = np.poly1d(z)
                trend_x = np.linspace(df_clean['response_time_minutes'].min(), df_clean['response_time_minutes'].max(), 100)
                trend_y = p(trend_x)
                
                fig.add_trace(go.Scatter(
                    x=trend_x,
                    y=trend_y,
                    mode='lines',
                    name='Trend Line',
                    line=dict(color='red', width=2, dash='dash')
                ))
            
            # Update layout
            fig.update_layout(
                title="Sentiment vs Response Time Correlation (≤1000 min)",
                xaxis_title="Response Time (minutes)",
                yaxis_title="Sentiment Score",
                height=500,
                showlegend=True,
                **self.layout_config
            )
            
            logger.info("Created sentiment vs response time chart")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating sentiment vs response time chart: {str(e)}")
            return self._create_error_chart("Error creating correlation chart")
    
    def create_team_sentiment_comparison(self, df: pd.DataFrame) -> go.Figure:
        """
        Create a bar chart comparing sentiment performance by team.
        
        Args:
            df: DataFrame with team and sentiment data
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            if df.empty or 'team' not in df.columns or 'category' not in df.columns:
                return self._create_error_chart("No team sentiment data available")
            
            # Calculate team sentiment metrics
            team_sentiment = df.groupby('team').agg({
                'category': lambda x: (x == 'positive').sum() / len(x) * 100,  # Positive percentage
                'combined_score': 'mean',
                'ticket_id': 'count'  # Total tickets
            }).round(2)
            
            team_sentiment.columns = ['positive_percentage', 'avg_sentiment_score', 'total_tickets']
            team_sentiment = team_sentiment.sort_values('positive_percentage', ascending=True)
            
            # Create subplot with two metrics
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Positive Sentiment Percentage by Team', 'Average Sentiment Score by Team'),
                horizontal_spacing=0.1
            )
            
            # Positive percentage chart
            fig.add_trace(
                go.Bar(
                    x=team_sentiment.index,
                    y=team_sentiment['positive_percentage'],
                    name='Positive %',
                    marker_color=self.sentiment_colors['positive'],
                    text=team_sentiment['positive_percentage'].round(1),
                    textposition='auto'
                ),
                row=1, col=1
            )
            
            # Average sentiment score chart
            fig.add_trace(
                go.Bar(
                    x=team_sentiment.index,
                    y=team_sentiment['avg_sentiment_score'],
                    name='Avg Sentiment Score',
                    marker_color=self.sentiment_colors['neutral'],
                    text=team_sentiment['avg_sentiment_score'].round(3),
                    textposition='auto'
                ),
                row=1, col=2
            )
            
            # Update layout
            fig.update_layout(
                title="Team Sentiment Performance Comparison",
                height=500,
                showlegend=False,
                **self.layout_config
            )
            
            # Update axes
            fig.update_xaxes(title_text="Team", row=1, col=1)
            fig.update_xaxes(title_text="Team", row=1, col=2)
            fig.update_yaxes(title_text="Positive %", row=1, col=1)
            fig.update_yaxes(title_text="Sentiment Score", row=1, col=2)
            
            logger.info("Created team sentiment comparison chart")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating team sentiment comparison chart: {str(e)}")
            return self._create_error_chart("Error creating team comparison")
    
    def create_sentiment_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """
        Create a heatmap showing sentiment patterns.
        
        Args:
            df: DataFrame with sentiment data
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            if df.empty or 'category' not in df.columns:
                return self._create_error_chart("No sentiment data available for heatmap")
            
            # Create sentiment vs time heatmap
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at'])
                df['hour'] = df['created_at'].dt.hour
                df['day_of_week'] = df['created_at'].dt.day_name()
                
                # Create pivot table for heatmap
                heatmap_data = df.groupby(['day_of_week', 'hour'])['category'].apply(
                    lambda x: (x == 'positive').sum() / len(x) * 100
                ).unstack(fill_value=0)
                
                # Reorder days
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                heatmap_data = heatmap_data.reindex(day_order)
                
                fig = go.Figure(data=go.Heatmap(
                    z=heatmap_data.values,
                    x=heatmap_data.columns,
                    y=heatmap_data.index,
                    colorscale='RdYlGn',
                    zmin=0,
                    zmax=100,
                    hovertemplate='<b>%{y}</b><br>Hour: %{x}<br>Positive %: %{z:.1f}%<extra></extra>'
                ))
                
                fig.update_layout(
                    title="Sentiment Heatmap by Day and Hour",
                    xaxis_title="Hour of Day",
                    yaxis_title="Day of Week",
                    height=500,
                    **self.layout_config
                )
            else:
                # Simple sentiment distribution heatmap
                sentiment_counts = df['category'].value_counts()
                
                fig = go.Figure(data=go.Heatmap(
                    z=[sentiment_counts.values],
                    x=sentiment_counts.index,
                    y=['Sentiment Distribution'],
                    colorscale='RdYlGn',
                    hovertemplate='<b>%{x}</b><br>Count: %{z}<extra></extra>'
                ))
                
                fig.update_layout(
                    title="Sentiment Distribution Heatmap",
                    height=300,
                    **self.layout_config
                )
            
            logger.info("Created sentiment heatmap")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating sentiment heatmap: {str(e)}")
            return self._create_error_chart("Error creating heatmap")
    
    def create_sentiment_insights(self, df: pd.DataFrame) -> go.Figure:
        """
        Create a comprehensive sentiment insights dashboard.
        
        Args:
            df: DataFrame with sentiment data
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            if df.empty or 'category' not in df.columns:
                return self._create_error_chart("No sentiment data available for insights")
            
            # Create subplot with multiple insights
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    'Sentiment Distribution',
                    'Sentiment Score Distribution',
                    'Top Positive Messages',
                    'Top Negative Messages'
                ),
                specs=[[{"type": "pie"}, {"type": "histogram"}],
                       [{"type": "bar"}, {"type": "bar"}]]
            )
            
            # Sentiment distribution pie chart
            sentiment_counts = df['category'].value_counts()
            fig.add_trace(
                go.Pie(
                    labels=sentiment_counts.index,
                    values=sentiment_counts.values,
                    marker_colors=[self.sentiment_colors.get(cat, '#808080') for cat in sentiment_counts.index],
                    name="Sentiment Distribution"
                ),
                row=1, col=1
            )
            
            # Sentiment score histogram
            fig.add_trace(
                go.Histogram(
                    x=df['combined_score'],
                    nbinsx=20,
                    marker_color=self.sentiment_colors['neutral'],
                    name="Score Distribution"
                ),
                row=1, col=2
            )
            
            # Top positive messages (if customer_message column exists)
            if 'customer_message' in df.columns:
                positive_messages = df[df['category'] == 'positive'].nlargest(5, 'combined_score')
                if not positive_messages.empty:
                    fig.add_trace(
                        go.Bar(
                            x=positive_messages['combined_score'],
                            y=[f"Msg {i+1}" for i in range(len(positive_messages))],
                            orientation='h',
                            marker_color=self.sentiment_colors['positive'],
                            name="Top Positive"
                        ),
                        row=2, col=1
                    )
                
                # Top negative messages
                negative_messages = df[df['category'] == 'negative'].nsmallest(5, 'combined_score')
                if not negative_messages.empty:
                    fig.add_trace(
                        go.Bar(
                            x=negative_messages['combined_score'],
                            y=[f"Msg {i+1}" for i in range(len(negative_messages))],
                            orientation='h',
                            marker_color=self.sentiment_colors['negative'],
                            name="Top Negative"
                        ),
                        row=2, col=2
                    )
            
            # Update layout
            fig.update_layout(
                title="Sentiment Analysis Insights Dashboard",
                height=800,
                showlegend=False,
                **self.layout_config
            )
            
            logger.info("Created sentiment insights dashboard")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating sentiment insights: {str(e)}")
            return self._create_error_chart("Error creating insights dashboard")
    
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
