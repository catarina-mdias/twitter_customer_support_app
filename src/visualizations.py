"""
Visualization module for customer support analytics.
Creates interactive charts and graphs using Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChartGenerator:
    """Handles creation of interactive visualizations for customer support analytics."""
    
    def __init__(self):
        """Initialize the chart generator with default styling."""
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd',
            'light': '#8c564b',
            'dark': '#e377c2'
        }
        
        self.layout_config = {
            'font': {'family': 'Arial, sans-serif', 'size': 12},
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'margin': {'l': 50, 'r': 50, 't': 50, 'b': 50}
        }
    
    def create_response_time_trend(self, df: pd.DataFrame) -> go.Figure:
        """
        Create a time series chart showing response time trends.
        
        Args:
            df: DataFrame with response_time_minutes and created_at columns
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            # Group by date and calculate daily metrics
            daily_metrics = df.groupby(df['created_at'].dt.date)['response_time_minutes'].agg([
                'count', 'mean', 'median', lambda x: x.quantile(0.9)
            ]).reset_index()
            
            daily_metrics.columns = ['date', 'ticket_count', 'avg_response_time', 'median_response_time', 'p90_response_time']
            
            # Create subplot with secondary y-axis
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Response Time Trends', 'Ticket Volume'),
                vertical_spacing=0.1,
                specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
            )
            
            # Add response time lines
            fig.add_trace(
                go.Scatter(
                    x=daily_metrics['date'],
                    y=daily_metrics['median_response_time'],
                    mode='lines+markers',
                    name='Median Response Time',
                    line=dict(color=self.color_scheme['primary'], width=3),
                    marker=dict(size=6)
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=daily_metrics['date'],
                    y=daily_metrics['p90_response_time'],
                    mode='lines+markers',
                    name='P90 Response Time',
                    line=dict(color=self.color_scheme['warning'], width=2),
                    marker=dict(size=4)
                ),
                row=1, col=1
            )
            
            # Add SLA threshold line
            fig.add_hline(
                y=60, 
                line_dash="dash", 
                line_color="red",
                annotation_text="SLA Threshold (60 min)",
                row=1, col=1
            )
            
            # Add ticket volume bar chart
            fig.add_trace(
                go.Bar(
                    x=daily_metrics['date'],
                    y=daily_metrics['ticket_count'],
                    name='Ticket Count',
                    marker_color=self.color_scheme['info'],
                    opacity=0.7
                ),
                row=2, col=1
            )
            
            # Update layout
            fig.update_layout(
                title="Response Time Trends Over Time",
                xaxis_title="Date",
                yaxis_title="Response Time (minutes)",
                yaxis2_title="Number of Tickets",
                height=600,
                showlegend=True,
                **self.layout_config
            )
            
            # Update x-axis for both subplots
            fig.update_xaxes(title_text="Date", row=2, col=1)
            
            logger.info("Created response time trend chart")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating response time trend chart: {str(e)}")
            return self._create_error_chart("Error creating trend chart")
    
    def create_response_time_distribution(self, df: pd.DataFrame) -> go.Figure:
        """
        Create a histogram showing response time distribution.
        
        Args:
            df: DataFrame with response_time_minutes column
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            # Create histogram
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=df['response_time_minutes'],
                nbinsx=50,
                name='Response Time Distribution',
                marker_color=self.color_scheme['primary'],
                opacity=0.7
            ))
            
            # Add vertical lines for key metrics
            median_rt = df['response_time_minutes'].median()
            p90_rt = df['response_time_minutes'].quantile(0.9)
            
            fig.add_vline(
                x=median_rt,
                line_dash="dash",
                line_color="green",
                annotation_text=f"Median: {median_rt:.1f} min"
            )
            
            fig.add_vline(
                x=p90_rt,
                line_dash="dash",
                line_color="orange",
                annotation_text=f"P90: {p90_rt:.1f} min"
            )
            
            fig.add_vline(
                x=60,
                line_dash="dash",
                line_color="red",
                annotation_text="SLA: 60 min"
            )
            
            # Update layout
            fig.update_layout(
                title="Response Time Distribution",
                xaxis_title="Response Time (minutes)",
                yaxis_title="Number of Tickets",
                height=400,
                **self.layout_config
            )
            
            logger.info("Created response time distribution chart")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating response time distribution chart: {str(e)}")
            return self._create_error_chart("Error creating distribution chart")
    
    def create_team_comparison(self, team_metrics: pd.DataFrame) -> go.Figure:
        """
        Create a bar chart comparing team performance.
        
        Args:
            team_metrics: DataFrame with team performance metrics
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            # Create subplot with two metrics
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Median Response Time by Team', 'SLA Compliance Rate by Team'),
                horizontal_spacing=0.1
            )
            
            # Sort teams by median response time
            team_metrics_sorted = team_metrics.sort_values('Median Response Time (min)')
            
            # Median response time chart
            fig.add_trace(
                go.Bar(
                    x=team_metrics_sorted.index,
                    y=team_metrics_sorted['Median Response Time (min)'],
                    name='Median Response Time',
                    marker_color=self.color_scheme['primary'],
                    text=team_metrics_sorted['Median Response Time (min)'].round(1),
                    textposition='auto'
                ),
                row=1, col=1
            )
            
            # SLA compliance rate chart
            fig.add_trace(
                go.Bar(
                    x=team_metrics_sorted.index,
                    y=team_metrics_sorted['SLA Compliance Rate (%)'],
                    name='SLA Compliance Rate',
                    marker_color=self.color_scheme['success'],
                    text=team_metrics_sorted['SLA Compliance Rate (%)'].round(1),
                    textposition='auto'
                ),
                row=1, col=2
            )
            
            # Add SLA threshold line
            fig.add_hline(
                y=80,  # 80% SLA compliance threshold
                line_dash="dash",
                line_color="red",
                annotation_text="Target: 80%",
                row=1, col=2
            )
            
            # Update layout
            fig.update_layout(
                title="Team Performance Comparison",
                height=500,
                showlegend=False,
                **self.layout_config
            )
            
            # Update axes
            fig.update_xaxes(title_text="Team", row=1, col=1)
            fig.update_xaxes(title_text="Team", row=1, col=2)
            fig.update_yaxes(title_text="Response Time (min)", row=1, col=1)
            fig.update_yaxes(title_text="Compliance Rate (%)", row=1, col=2)
            
            logger.info("Created team comparison chart")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating team comparison chart: {str(e)}")
            return self._create_error_chart("Error creating team comparison chart")
    
    def create_sla_breach_analysis(self, df: pd.DataFrame) -> go.Figure:
        """
        Create a chart analyzing SLA breaches.
        
        Args:
            df: DataFrame with response_time_minutes column
            
        Returns:
            go.Figure: Plotly figure object
        """
        try:
            # Calculate SLA breach data
            total_tickets = len(df)
            sla_breaches = (df['response_time_minutes'] > 60).sum()
            sla_compliance = total_tickets - sla_breaches
            
            # Create pie chart
            fig = go.Figure(data=[go.Pie(
                labels=['SLA Compliant', 'SLA Breach'],
                values=[sla_compliance, sla_breaches],
                marker_colors=[self.color_scheme['success'], self.color_scheme['warning']],
                textinfo='label+percent+value',
                textposition='auto'
            )])
            
            fig.update_layout(
                title=f"SLA Compliance Overview<br><sub>Total Tickets: {total_tickets}</sub>",
                height=400,
                **self.layout_config
            )
            
            logger.info("Created SLA breach analysis chart")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating SLA breach analysis chart: {str(e)}")
            return self._create_error_chart("Error creating SLA breach analysis")
    
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
