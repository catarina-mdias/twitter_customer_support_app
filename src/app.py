"""
Customer Support Analytics App - Main Application
A lightweight Streamlit app for analyzing customer support performance.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys
import base64
import time

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor import DataProcessor
from visualizations import ChartGenerator
import importlib.util
import sys
import os

# Import config.py directly to avoid package conflict
config_path = os.path.join(os.path.dirname(__file__), 'config.py')
spec = importlib.util.spec_from_file_location("config_module", config_path)
config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_module)

# Import sentiment analysis modules
try:
    from sentiment_visualizations import SentimentVisualizations
    SENTIMENT_VIZ_AVAILABLE = True
except ImportError:
    SENTIMENT_VIZ_AVAILABLE = False

# Import team analysis modules
try:
    from team_visualizations import TeamVisualizations
    TEAM_VIZ_AVAILABLE = True
except ImportError:
    TEAM_VIZ_AVAILABLE = False

# Import Twitter visualizations
try:
    from twitter_visualizations import TwitterVisualizations
    TWITTER_VIZ_AVAILABLE = True
except ImportError:
    TWITTER_VIZ_AVAILABLE = False

# Import real-time data managers
try:
    from database_connector import db_connector
    from api_manager import api_manager, APIConfig, APIType
    from websocket_manager import ws_manager, WebSocketConfig, WebSocketType
    from realtime_manager import realtime_manager, DataSourceConfig, DataSourceType
    REALTIME_AVAILABLE = True
except ImportError:
    REALTIME_AVAILABLE = False

# Import Phase 4 features
try:
    from anomaly_detection import AnomalyDetector
    from reporting import ReportGenerator
    PHASE_4_AVAILABLE = True
except ImportError:
    PHASE_4_AVAILABLE = False

# Import RAG Insights (Phase 6)
try:
    from rag_insights import RAGInsightsEngine, render_rag_insights_ui
    RAG_INSIGHTS_AVAILABLE = True
except ImportError:
    RAG_INSIGHTS_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Customer Support Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize app configuration
app_config = config_module.AppConfig()

def generate_pdf_report(df, include_overview=True, include_response_times=True, 
                        include_sentiment=True, include_teams=True, include_trends=True,
                        include_recommendations=True, selected_teams=None):
    """Generate a comprehensive PDF report with selected sections."""
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    import io
    
    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#4c63d2'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    
    normal_style = styles['Normal']
    
    # Build story
    story = []
    
    # Title page
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Customer Support Analytics Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", normal_style))
    story.append(Spacer(1, 0.1*inch))
    
    if selected_teams:
        teams_text = ", ".join(selected_teams) if len(selected_teams) <= 3 else f"{len(selected_teams)} teams"
        story.append(Paragraph(f"Teams: {teams_text}", normal_style))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"Total Records: {len(df):,}", normal_style))
    
    if 'created_at' in df.columns:
        date_range = f"{df['created_at'].min().strftime('%Y-%m-%d')} to {df['created_at'].max().strftime('%Y-%m-%d')}"
        story.append(Paragraph(f"Date Range: {date_range}", normal_style))
    
    story.append(PageBreak())
    
    # Overview Section
    if include_overview:
        story.append(Paragraph("📊 Overview & Summary", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Key metrics table
        metrics_data = [['Metric', 'Value']]
        metrics_data.append(['Total Tickets', f"{len(df):,}"])
        
        if 'response_time_minutes' in df.columns:
            rt_data = df['response_time_minutes'].dropna()
            metrics_data.append(['Average Response Time', f"{rt_data.mean():.1f} minutes"])
            metrics_data.append(['Median Response Time', f"{rt_data.median():.1f} minutes"])
            metrics_data.append(['90th Percentile', f"{rt_data.quantile(0.9):.1f} minutes"])
        
        if 'combined_score' in df.columns:
            sentiment_data = df['combined_score'].dropna()
            avg_sentiment = sentiment_data.mean()
            metrics_data.append(['Average Sentiment', f"{avg_sentiment:.3f}"])
            
            if 'category' in df.columns:
                positive_pct = (df['category'] == 'positive').sum() / len(df) * 100
                metrics_data.append(['Positive Sentiment', f"{positive_pct:.1f}%"])
        
        if 'team' in df.columns:
            metrics_data.append(['Number of Teams', str(df['team'].nunique())])
        
        # Create table
        metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 0.3*inch))
    
    # Response Time Analysis
    if include_response_times and 'response_time_minutes' in df.columns:
        story.append(Paragraph("⏱️ Response Time Analysis", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        rt_data = df['response_time_minutes'].dropna()
        
        story.append(Paragraph("Response Time Statistics:", subheading_style))
        rt_stats = [
            f"• Minimum: {rt_data.min():.1f} minutes",
            f"• Maximum: {rt_data.max():.1f} minutes",
            f"• Average: {rt_data.mean():.1f} minutes",
            f"• Median: {rt_data.median():.1f} minutes",
            f"• Standard Deviation: {rt_data.std():.1f} minutes",
            f"• 75th Percentile: {rt_data.quantile(0.75):.1f} minutes",
            f"• 90th Percentile: {rt_data.quantile(0.9):.1f} minutes",
            f"• 95th Percentile: {rt_data.quantile(0.95):.1f} minutes"
        ]
        for stat in rt_stats:
            story.append(Paragraph(stat, normal_style))
        
        story.append(Spacer(1, 0.15*inch))
        
        # SLA compliance (assuming 60 min SLA)
        sla_compliance = (rt_data <= 60).sum() / len(rt_data) * 100
        story.append(Paragraph(f"SLA Compliance (60 min): {sla_compliance:.1f}%", subheading_style))
        
        story.append(Spacer(1, 0.3*inch))
    
    # Sentiment Analysis
    if include_sentiment:
        # Check for sentiment columns
        has_sentiment = 'combined_score' in df.columns or 'vader_compound' in df.columns or 'textblob_polarity' in df.columns
        
        if has_sentiment:
            story.append(Paragraph("😊 Sentiment Analysis", heading_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Use combined_score if available, otherwise use vader_compound
            if 'combined_score' in df.columns:
                sentiment_data = df['combined_score'].dropna()
                score_label = "Combined Sentiment Score"
            elif 'vader_compound' in df.columns:
                sentiment_data = df['vader_compound'].dropna()
                score_label = "VADER Sentiment Score"
            else:
                sentiment_data = df['textblob_polarity'].dropna()
                score_label = "TextBlob Sentiment Score"
            
            if len(sentiment_data) > 0:
                story.append(Paragraph("Sentiment Statistics:", subheading_style))
                sent_stats = [
                    f"• Average {score_label}: {sentiment_data.mean():.3f}",
                    f"• Median {score_label}: {sentiment_data.median():.3f}",
                    f"• Standard Deviation: {sentiment_data.std():.3f}",
                    f"• Most Positive: {sentiment_data.max():.3f}",
                    f"• Most Negative: {sentiment_data.min():.3f}"
                ]
                for stat in sent_stats:
                    story.append(Paragraph(stat, normal_style))
                
                story.append(Spacer(1, 0.15*inch))
                
                # Sentiment distribution
                if 'category' in df.columns:
                    story.append(Paragraph("Sentiment Distribution:", subheading_style))
                    sentiment_counts = df['category'].value_counts()
                    for category, count in sentiment_counts.items():
                        pct = count / len(df) * 100
                        story.append(Paragraph(f"• {category.title()}: {count:,} ({pct:.1f}%)", normal_style))
                else:
                    # Calculate distribution based on score ranges if no category column
                    positive = (sentiment_data > 0.05).sum()
                    negative = (sentiment_data < -0.05).sum()
                    neutral = len(sentiment_data) - positive - negative
                    
                    story.append(Paragraph("Sentiment Distribution:", subheading_style))
                    story.append(Paragraph(f"• Positive: {positive:,} ({positive/len(sentiment_data)*100:.1f}%)", normal_style))
                    story.append(Paragraph(f"• Negative: {negative:,} ({negative/len(sentiment_data)*100:.1f}%)", normal_style))
                    story.append(Paragraph(f"• Neutral: {neutral:,} ({neutral/len(sentiment_data)*100:.1f}%)", normal_style))
                
                story.append(Spacer(1, 0.3*inch))
            else:
                story.append(Paragraph("😊 Sentiment Analysis", heading_style))
                story.append(Paragraph("No sentiment data available for the selected teams.", normal_style))
                story.append(Spacer(1, 0.3*inch))
        else:
            # No sentiment columns found
            story.append(Paragraph("😊 Sentiment Analysis", heading_style))
            story.append(Paragraph("Sentiment analysis data is not available in this dataset.", normal_style))
            story.append(Spacer(1, 0.3*inch))
    
    # Team Performance
    if include_teams and 'team' in df.columns:
        story.append(Paragraph("👥 Team Performance", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        teams = df['team'].unique()
        
        for team in sorted(teams):
            if pd.isna(team):
                continue
                
            team_df = df[df['team'] == team]
            story.append(Paragraph(f"{team}", subheading_style))
            
            team_stats = [f"• Total Tickets: {len(team_df):,}"]
            
            if 'response_time_minutes' in team_df.columns:
                team_rt = team_df['response_time_minutes'].dropna()
                if len(team_rt) > 0:
                    team_stats.append(f"• Avg Response Time: {team_rt.mean():.1f} min")
                    team_stats.append(f"• Median Response Time: {team_rt.median():.1f} min")
            
            if 'combined_score' in team_df.columns:
                team_sent = team_df['combined_score'].dropna()
                if len(team_sent) > 0:
                    team_stats.append(f"• Avg Sentiment: {team_sent.mean():.3f}")
            
            for stat in team_stats:
                story.append(Paragraph(stat, normal_style))
            
            story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.2*inch))
    
    # Trends & Patterns
    if include_trends and 'created_at' in df.columns:
        story.append(Paragraph("📈 Trends & Patterns", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Daily volume trend
        daily_volume = df.groupby(df['created_at'].dt.date).size()
        story.append(Paragraph("Daily Volume Statistics:", subheading_style))
        volume_stats = [
            f"• Average Daily Tickets: {daily_volume.mean():.1f}",
            f"• Median Daily Tickets: {daily_volume.median():.1f}",
            f"• Busiest Day: {daily_volume.max()} tickets",
            f"• Quietest Day: {daily_volume.min()} tickets"
        ]
        for stat in volume_stats:
            story.append(Paragraph(stat, normal_style))
        
        story.append(Spacer(1, 0.3*inch))
    
    # Recommendations
    if include_recommendations:
        story.append(Paragraph("💡 Recommendations", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        recommendations = []
        
        # Response time recommendations
        if 'response_time_minutes' in df.columns:
            rt_data = df['response_time_minutes'].dropna()
            avg_rt = rt_data.mean()
            if avg_rt > 60:
                recommendations.append("Response times exceed the 60-minute SLA target. Consider increasing team capacity or improving processes.")
            elif avg_rt < 30:
                recommendations.append("Response times are excellent. Maintain current service levels and document best practices.")
            else:
                recommendations.append("Response times are within acceptable range. Monitor for any degradation trends.")
        
        # Sentiment recommendations
        if 'combined_score' in df.columns:
            avg_sentiment = df['combined_score'].dropna().mean()
            if avg_sentiment < 0:
                recommendations.append("Average sentiment is negative. Review customer feedback and implement service improvements.")
            elif avg_sentiment > 0.2:
                recommendations.append("Customer sentiment is very positive. Maintain current practices and share success stories.")
            else:
                recommendations.append("Sentiment is neutral. Look for opportunities to improve customer satisfaction.")
        
        # Team recommendations
        if 'team' in df.columns and 'response_time_minutes' in df.columns:
            team_performance = df.groupby('team')['response_time_minutes'].mean()
            best_team = team_performance.idxmin()
            worst_team = team_performance.idxmax()
            if best_team != worst_team:
                recommendations.append(f"Team '{best_team}' has the best response times. Consider sharing their practices with other teams.")
        
        # Volume recommendations
        if 'created_at' in df.columns:
            daily_volume = df.groupby(df['created_at'].dt.date).size()
            if daily_volume.std() > daily_volume.mean() * 0.5:
                recommendations.append("High variability in daily ticket volume. Consider implementing flexible staffing or workload management.")
        
        # General recommendations
        recommendations.append("Regularly review this report to track performance trends over time.")
        recommendations.append("Set specific, measurable goals for improvement in key metrics.")
        recommendations.append("Gather team feedback to identify process improvement opportunities.")
        
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", normal_style))
            story.append(Spacer(1, 0.08*inch))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes

def main():
    """Main application function."""
    # Enhanced CSS Design System
    st.markdown("""
    <style>
    /* Enhanced Design System Variables */
    :root {
        --primary-color: #667eea;
        --primary-light: #8fa4f3;
        --primary-dark: #4c63d2;
        --secondary-color: #764ba2;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --error-color: #dc3545;
        --info-color: #17a2b8;
        --light-color: #f8f9fa;
        --dark-color: #343a40;
        --text-primary: #212529;
        --text-secondary: #6c757d;
        --text-muted: #adb5bd;
        --border-color: #dee2e6;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --transition-fast: 0.15s ease-in-out;
        --transition-normal: 0.3s ease-in-out;
        --border-radius-sm: 4px;
        --border-radius-md: 8px;
        --border-radius-lg: 12px;
        --border-radius-xl: 16px;
    }
    
    /* Enhanced Typography System */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        line-height: 1.2;
        text-align: center;
        margin: 0 0 1rem 0;
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.025em;
        position: relative;
        z-index: 1;
        padding: 0.5rem 0;
    }
    
    .subtitle {
        font-size: 1.25rem;
        font-weight: 400;
        line-height: 1.6;
        text-align: center;
        color: var(--text-secondary);
        margin: 0 0 2rem 0;
    }
    
    .enhanced-h2 {
        font-size: 2rem;
        font-weight: 600;
        line-height: 1.3;
        margin: 0 0 0.875rem 0;
        color: var(--text-primary);
    }
    
    .enhanced-h3 {
        font-size: 1.5rem;
        font-weight: 600;
        line-height: 1.4;
        margin: 0 0 0.75rem 0;
        color: var(--text-primary);
    }
    
    .enhanced-h4 {
        font-size: 1.25rem;
        font-weight: 500;
        line-height: 1.4;
        margin: 0 0 0.625rem 0;
        color: var(--text-primary);
    }
    
    .enhanced-body {
        font-size: 1rem;
        font-weight: 400;
        line-height: 1.6;
        margin: 0 0 1rem 0;
        color: var(--text-primary);
    }
    
    .enhanced-caption {
        font-size: 0.875rem;
        font-weight: 400;
        line-height: 1.5;
        margin: 0 0 0.75rem 0;
        color: var(--text-secondary);
    }
    
    /* Enhanced Feature Cards */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: var(--border-radius-lg);
        box-shadow: var(--shadow-md);
        margin: 1rem 0;
        border-left: 4px solid var(--primary-color);
        transition: var(--transition-normal);
        border: 1px solid var(--border-color);
    }
    
    .feature-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
        border-left-color: var(--primary-dark);
    }
    
    /* Enhanced Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        padding: 1.5rem;
        border-radius: var(--border-radius-lg);
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: var(--shadow-md);
        transition: var(--transition-normal);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        opacity: 0;
        transition: var(--transition-normal);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-card .metric-label {
        font-size: 0.875rem;
        font-weight: 500;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-card .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card .metric-trend {
        font-size: 0.75rem;
        margin-top: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.25rem;
        opacity: 0.9;
    }
    
    /* Enhanced Buttons */
    .enhanced-button {
        background: var(--primary-color);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: var(--border-radius-md);
        font-size: 0.875rem;
        font-weight: 500;
        cursor: pointer;
        transition: var(--transition-fast);
        box-shadow: var(--shadow-sm);
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .enhanced-button:hover {
        background: var(--primary-dark);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    .enhanced-button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-sm);
    }
    
    .enhanced-button:disabled {
        background: var(--text-muted);
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }
    
    /* Enhanced Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background: var(--light-color);
        padding: 4px;
        border-radius: var(--border-radius-lg);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: transparent;
        border-radius: var(--border-radius-md);
        font-weight: 600;
        transition: var(--transition-fast);
        border: 1px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(102, 126, 234, 0.1);
        border-color: rgba(102, 126, 234, 0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color);
        color: white;
        border-color: var(--primary-color);
        box-shadow: var(--shadow-sm);
    }
    
    /* Enhanced Sidebar */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, var(--light-color) 0%, #e9ecef 100%);
        border-right: 1px solid var(--border-color);
    }
    
    /* Skeleton Loading */
    .skeleton {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
        border-radius: var(--border-radius-md);
    }
    
    @keyframes loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    .skeleton-metric {
        height: 120px;
        margin: 0.5rem 0;
    }
    
    .skeleton-text {
        height: 1rem;
        margin: 0.5rem 0;
    }
    
    .skeleton-text.short {
        width: 60%;
    }
    
    .skeleton-text.medium {
        width: 80%;
    }
    
    /* Enhanced Progress Indicators */
    .enhanced-progress {
        background: var(--light-color);
        border-radius: var(--border-radius-xl);
        overflow: hidden;
        height: 8px;
        margin: 1rem 0;
    }
    
    .enhanced-progress-bar {
        height: 100%;
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--primary-light) 100%);
        border-radius: var(--border-radius-xl);
        transition: width var(--transition-normal);
        position: relative;
    }
    
    .enhanced-progress-bar::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* Enhanced Notifications */
    .enhanced-notification {
        padding: 1rem 1.5rem;
        border-radius: var(--border-radius-md);
        margin: 0.5rem 0;
        border-left: 4px solid;
        box-shadow: var(--shadow-sm);
        transition: var(--transition-normal);
    }
    
    .enhanced-notification.success {
        background: rgba(40, 167, 69, 0.1);
        border-left-color: var(--success-color);
        color: #155724;
    }
    
    .enhanced-notification.error {
        background: rgba(220, 53, 69, 0.1);
        border-left-color: var(--error-color);
        color: #721c24;
    }
    
    .enhanced-notification.warning {
        background: rgba(255, 193, 7, 0.1);
        border-left-color: var(--warning-color);
        color: #856404;
    }
    
    .enhanced-notification.info {
        background: rgba(23, 162, 184, 0.1);
        border-left-color: var(--info-color);
        color: #0c5460;
    }
    
    /* Dark Mode Support */
    @media (prefers-color-scheme: dark) {
        :root {
            --text-primary: #f8f9fa;
            --text-secondary: #adb5bd;
            --text-muted: #6c757d;
            --border-color: #495057;
            --light-color: #343a40;
        }
        
        .feature-card {
            background: var(--dark-color);
            border-color: var(--border-color);
        }
        
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, var(--dark-color) 0%, #495057 100%);
        }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .subtitle {
            font-size: 1rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .metric-card .metric-value {
            font-size: 2rem;
        }
        
        .feature-card {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown('<h1 class="main-header">📊 Customer Support Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Transform your support data into actionable insights with advanced analytics</p>', unsafe_allow_html=True)
    
    # Add help and info section
    with st.expander("ℹ️ How to Get Started", expanded=False):
        st.markdown("""
        ### 🚀 Quick Start Guide
        
        **1. Choose Your Data Source:**
        - **📁 CSV Upload**: Upload your support data in CSV format
        - **🐦 Twitter Account**: Connect to Twitter API and analyze account tweets
        - **🔍 Twitter Search**: Search for tweets using keywords
        
        **2. Data Requirements:**
        Your CSV should have columns like:
        - `tweet_id` - Unique identifier for each tweet
        - `author_id` - Twitter handle/username of the author
        - `inbound` - Boolean indicating if it's a customer message (True) or response (False)
        - `created_at` - Timestamp when the tweet was created
        - `text` - The actual tweet content/message
        - `response_tweet_id` - ID of the response tweet (if applicable)
        - `in_response_to_tweet_id` - ID of the tweet this is responding to
        - `conversation_id` - Groups related tweets in a conversation
        
        **3. Twitter API Setup:**
        - Get a Twitter API Bearer Token from [Twitter Developer Portal](https://developer.twitter.com/)
        - Use the token to connect and fetch real-time data
        
        **4. Analysis Features:**
        - **Response Time Analysis**: Track performance metrics
        - **Sentiment Analysis**: Understand customer emotions
        - **Team Performance**: Compare team effectiveness
        - **Predictive Analytics**: Forecast trends (requires additional setup)
        - **Anomaly Detection**: Find unusual patterns
        - **Advanced Reporting**: Export comprehensive reports
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📋 Sample Data")
            st.markdown("Need test data? Use our sample Twitter CSV:")
            if st.button("📥 Download Sample CSV"):
                sample_data = """tweet_id,author_id,inbound,created_at,text,response_tweet_id,in_response_to_tweet_id,conversation_id
1,sprintcare,False,2024-01-01 10:00:00,@115712 I understand. I would like to assist you. We would need to get you into a private secured link to further assist.,2,3,1
2,115712,True,2024-01-01 10:05:00,@sprintcare and how do you propose we do that,,1,1
3,sprintcare,False,2024-01-01 10:10:00,@115712 Please DM us your account details and we'll help you right away.,4,2,1
4,115712,True,2024-01-01 10:15:00,@sprintcare Thank you for the quick response!,3,3,1"""
                st.download_button(
                    label="Download Sample Twitter Data",
                    data=sample_data,
                    file_name="sample_twitter_support_data.csv",
                    mime="text/csv"
                )
        
        with col2:
            st.markdown("### 🔧 Troubleshooting")
            st.markdown("""
            **Common Issues:**
            - **Empty CSV**: Ensure your file has data rows
            - **Missing Columns**: Check column names match Twitter format
            - **Date Format**: Ensure `created_at` is in proper datetime format
            - **Boolean Values**: `inbound` should be True/False or 1/0
            - **Twitter API**: Verify Bearer Token is correct
            - **No Data**: Try different date ranges or search terms
            """)
    
    # Sidebar for data source selection and configuration
    with st.sidebar:
        st.markdown("## 🚀 Data Source")
        
        # Data source selection - Only CSV Upload is enabled, others shown but disabled
        st.markdown("**Available Data Sources:**")
        st.info("ℹ️ Only CSV Upload is currently enabled. Other options are shown for reference.")
        
        if REALTIME_AVAILABLE:
            # Show all options but only CSV Upload is functional
            st.markdown("""
            - ✅ **📁 CSV Upload** - Active
            - 🔒 **🐦 Twitter Account** - Coming Soon
            - 🔒 **🔍 Twitter Search** - Coming Soon
            - 🔒 **🗄️ Database Connection** - Coming Soon
            - 🔒 **🌐 API Endpoint** - Coming Soon
            - 🔒 **📡 WebSocket Stream** - Coming Soon
            - 🔒 **☁️ Cloud Storage** - Coming Soon
            - 🔒 **🔄 Real-Time Mode** - Coming Soon
            """)
        else:
            st.markdown("""
            - ✅ **📁 CSV Upload** - Active
            - 🔒 **🐦 Twitter Account** - Coming Soon
            - 🔒 **🔍 Twitter Search** - Coming Soon
            """)
        
        # Force CSV Upload as the only option
        data_source = "📁 CSV Upload"
        
        df = None
        uploaded_file = None
        
        if data_source == "📁 CSV Upload":
            st.markdown("### 📁 Upload CSV File")
        uploaded_file = st.file_uploader(
            "Upload CSV file",
            type=['csv'],
            help="Upload your customer support data in CSV format"
        )
        
        if uploaded_file is not None:
            with st.spinner("📁 Loading CSV file..."):
                try:
                    data_processor = DataProcessor()
                    df = data_processor.load_data(uploaded_file)
                    
                    # Calculate response times if date columns exist
                    if 'created_at' in df.columns and 'responded_at' in df.columns:
                        df = data_processor.calculate_response_times(df)
                        st.success(f"✅ CSV file loaded successfully! ({len(df)} records, response times calculated)")
                    else:
                        st.success("✅ CSV file loaded successfully!")
                        st.info("ℹ️ Response time calculation skipped: requires 'created_at' and 'responded_at' columns")
                except Exception as e:
                    st.error(f"Error loading CSV: {str(e)}")
                    df = None
        
        elif data_source == "🐦 Twitter Account":
            st.markdown("### 🐦 Connect to Twitter")
            
            if TWITTER_API_AVAILABLE:
                # Twitter API connection
                bearer_token = st.text_input(
                    "Twitter Bearer Token",
                    type="password",
                    help="Enter your Twitter API Bearer Token"
                )
                
                if st.button("🔗 Connect to Twitter"):
                    if bearer_token:
                        with st.spinner("Connecting to Twitter API..."):
                            connection_result = twitter_connector.connect(bearer_token)
                            
                            if connection_result['success']:
                                st.success("✅ Connected to Twitter API!")
                                st.session_state.twitter_connected = True
                            else:
                                st.error(f"❌ Connection failed: {connection_result['message']}")
                                st.session_state.twitter_connected = False
                    else:
                        st.warning("Please enter your Bearer Token")
                
                # Account selection and data fetching
                if st.session_state.get('twitter_connected', False):
                    st.markdown("#### 📊 Fetch Account Data")
                    
                    username = st.text_input(
                        "Twitter Username",
                        placeholder="username (without @)",
                        help="Enter the Twitter username to analyze"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        days_back = st.number_input("Days Back", min_value=1, max_value=30, value=7)
                    with col2:
                        max_tweets = st.number_input("Max Tweets", min_value=10, max_value=500, value=100)
                    
                    if st.button("📥 Fetch Tweets") and username:
                        with st.spinner(f"🐦 Fetching tweets from @{username}..."):
                            fetch_result = twitter_connector.fetch_account_tweets(
                                username, days_back, max_tweets
                            )
                            
                            if fetch_result['success']:
                                df = fetch_result['data']
                                
                                # Calculate response times if date columns exist
                                if 'created_at' in df.columns and 'responded_at' in df.columns:
                                    data_processor = DataProcessor()
                                    df = data_processor.calculate_response_times(df)
                                
                                st.success(f"✅ Fetched {fetch_result['tweet_count']} tweets!")
                                st.session_state.twitter_data = df
                            else:
                                st.error(f"❌ Failed to fetch tweets: {fetch_result['message']}")
                else:
                    st.info("🔑 Connect to Twitter API first to fetch account data")
            else:
                st.warning("Twitter API not available. Install tweepy: pip install tweepy")
        
        elif data_source == "🔍 Twitter Search":
            st.markdown("### 🔍 Search Twitter")
            
            if TWITTER_API_AVAILABLE:
                # Twitter API connection
                bearer_token = st.text_input(
                    "Twitter Bearer Token",
                    type="password",
                    help="Enter your Twitter API Bearer Token"
                )
                
                if st.button("🔗 Connect to Twitter"):
                    if bearer_token:
                        with st.spinner("Connecting to Twitter API..."):
                            connection_result = twitter_connector.connect(bearer_token)
                            
                            if connection_result['success']:
                                st.success("✅ Connected to Twitter API!")
                                st.session_state.twitter_connected = True
                            else:
                                st.error(f"❌ Connection failed: {connection_result['message']}")
                                st.session_state.twitter_connected = False
                    else:
                        st.warning("Please enter your Bearer Token")
                
                # Search functionality
                if st.session_state.get('twitter_connected', False):
                    st.markdown("#### 🔍 Search Tweets")
                    
                    search_query = st.text_input(
                        "Search Query",
                        placeholder="customer support OR help desk",
                        help="Enter search terms for tweets"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        days_back = st.number_input("Days Back", min_value=1, max_value=7, value=7)
                    with col2:
                        max_tweets = st.number_input("Max Tweets", min_value=10, max_value=100, value=50)
                    
                    if st.button("🔍 Search Tweets") and search_query:
                        with st.spinner(f"🔍 Searching for tweets..."):
                            search_result = twitter_connector.search_tweets(
                                search_query, days_back, max_tweets
                            )
                            
                            if search_result['success']:
                                df = search_result['data']
                                
                                # Calculate response times if date columns exist
                                if 'created_at' in df.columns and 'responded_at' in df.columns:
                                    data_processor = DataProcessor()
                                    df = data_processor.calculate_response_times(df)
                                
                                st.success(f"✅ Found {search_result['tweet_count']} tweets!")
                                st.session_state.twitter_data = df
                            else:
                                st.error(f"❌ Search failed: {search_result['message']}")
                else:
                    st.info("🔑 Connect to Twitter API first to search tweets")
            else:
                st.warning("Twitter API not available. Install tweepy: pip install tweepy")
        
        elif data_source == "🗄️ Database Connection" and REALTIME_AVAILABLE:
            st.markdown("### 🗄️ Database Connection")
            
            # Database type selection
            db_type = st.selectbox(
                "Database Type",
                options=["sqlite", "postgresql", "mysql"],
                help="Select the type of database to connect to"
            )
            
            # Database connection parameters
            if db_type == "sqlite":
                database_path = st.text_input(
                    "Database Path",
                    value=":memory:",
                    help="Path to SQLite database file (use :memory: for in-memory database)"
                )
                connection_params = {"database": database_path}
            else:
                col1, col2 = st.columns(2)
                with col1:
                    host = st.text_input("Host", value="localhost")
                    port = st.number_input("Port", value=5432 if db_type == "postgresql" else 3306)
                with col2:
                    database = st.text_input("Database Name")
                    user = st.text_input("Username")
                
                password = st.text_input("Password", type="password")
                
                connection_params = {
                    "host": host,
                    "port": port,
                    "database": database,
                    "user": user,
                    "password": password
                }
            
            if st.button("🔗 Connect to Database"):
                with st.spinner("Connecting to database..."):
                    connection_result = db_connector.connect(db_type, connection_params)
                    
                    if connection_result['success']:
                        st.success("✅ Connected to database!")
                        st.session_state.db_connection_id = connection_result['connection_id']
                        
                        # Get sample data
                        table_name = st.text_input("Table Name", value="support_tickets")
                        if st.button("📊 Load Sample Data"):
                            with st.spinner("Loading data from database..."):
                                data_result = db_connector.get_support_data(
                                    st.session_state.db_connection_id, 
                                    table_name, 
                                    limit=1000
                                )
                                
                                if data_result['success']:
                                    df = data_result['data']
                                    st.success(f"✅ Loaded {len(df)} records from database!")
                                else:
                                    st.error(f"❌ Failed to load data: {data_result['message']}")
                    else:
                        st.error(f"❌ Connection failed: {connection_result['message']}")
        
        elif data_source == "🌐 API Endpoint" and REALTIME_AVAILABLE:
            st.markdown("### 🌐 API Endpoint")
            
            # API type selection
            api_type = st.selectbox(
                "API Type",
                options=["zendesk", "freshdesk", "intercom", "slack", "custom"],
                help="Select the type of API to connect to"
            )
            
            # API configuration
            base_url = st.text_input(
                "Base URL",
                placeholder="https://yourcompany.zendesk.com",
                help="Base URL of the API"
            )
            
            if api_type in ["zendesk", "freshdesk"]:
                col1, col2 = st.columns(2)
                with col1:
                    email = st.text_input("Email")
                with col2:
                    token = st.text_input("API Token", type="password")
                credentials = {"email": email, "token": token}
            elif api_type == "intercom":
                token = st.text_input("Access Token", type="password")
                credentials = {"token": token}
            elif api_type == "slack":
                token = st.text_input("Bot Token", type="password")
                credentials = {"token": token}
            else:
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                credentials = {"username": username, "password": password}
            
            if st.button("🔗 Connect to API"):
                with st.spinner("Connecting to API..."):
                    try:
                        api_config = APIConfig(
                            api_type=APIType(api_type),
                            base_url=base_url,
                            credentials=credentials,
                            refresh_interval=60
                        )
                        
                        add_result = api_manager.add_api_source("api_source", api_config)
                        
                        if add_result['success']:
                            st.success("✅ Connected to API!")
                            st.session_state.api_source_id = "api_source"
                            
                            if st.button("📊 Fetch Data"):
                                with st.spinner("Fetching data from API..."):
                                    data_result = api_manager.get_real_time_data("api_source")
                                    
                                    if data_result['success']:
                                        df = data_result['data']
                                        st.success(f"✅ Fetched {len(df)} records from API!")
                                    else:
                                        st.error(f"❌ Failed to fetch data: {data_result['message']}")
                        else:
                            st.error(f"❌ Connection failed: {add_result['message']}")
                    except Exception as e:
                        st.error(f"❌ Connection failed: {str(e)}")
        
        elif data_source == "📡 WebSocket Stream" and REALTIME_AVAILABLE:
            st.markdown("### 📡 WebSocket Stream")
            
            # WebSocket type selection
            ws_type = st.selectbox(
                "WebSocket Type",
                options=["slack_rtm", "discord_gateway", "zendesk_events", "custom"],
                help="Select the type of WebSocket to connect to"
            )
            
            # WebSocket configuration
            ws_url = st.text_input(
                "WebSocket URL",
                placeholder="wss://slack.com/rtm",
                help="WebSocket URL to connect to"
            )
            
            auth_token = st.text_input("Auth Token", type="password", help="Authentication token if required")
            
            if st.button("🔗 Connect to WebSocket"):
                with st.spinner("Connecting to WebSocket..."):
                    try:
                        ws_config = WebSocketConfig(
                            ws_type=WebSocketType(ws_type),
                            url=ws_url,
                            auth_token=auth_token,
                            heartbeat_interval=30
                        )
                        
                        connect_result = ws_manager.connect("ws_source", ws_config)
                        
                        if connect_result['success']:
                            st.success("✅ Connected to WebSocket!")
                            st.session_state.ws_source_id = "ws_source"
                            
                            # Subscribe to messages
                            subscribe_result = ws_manager.subscribe("ws_source", lambda conn_id, data: None)
                            
                            if st.button("📊 Get Latest Messages"):
                                with st.spinner("Getting latest messages..."):
                                    messages_result = ws_manager.get_latest_messages("ws_source", limit=100)
                                    
                                    if messages_result['success']:
                                        messages = messages_result['messages']
                                        if messages:
                                            df = pd.DataFrame(messages)
                                            st.success(f"✅ Retrieved {len(df)} messages!")
                                        else:
                                            st.info("No messages received yet")
                                    else:
                                        st.error(f"❌ Failed to get messages: {messages_result['message']}")
                        else:
                            st.error(f"❌ Connection failed: {connect_result['message']}")
                    except Exception as e:
                        st.error(f"❌ Connection failed: {str(e)}")
        
        elif data_source == "🔄 Real-Time Mode" and REALTIME_AVAILABLE:
            st.markdown("### 🔄 Real-Time Mode")
            
            # Real-time controls
            auto_refresh = st.checkbox(
                "🔄 Enable Auto-Refresh",
                value=True,
                help="Automatically refresh data"
            )
            
            if auto_refresh:
                refresh_interval = st.slider(
                    "Refresh Interval (seconds)",
                    min_value=10,
                    max_value=300,
                    value=30
                )
                st.session_state.refresh_interval = refresh_interval
            
            # Data source management
            st.markdown("#### 📊 Manage Data Sources")
            
            # Add new data source
            with st.expander("➕ Add New Data Source"):
                source_type = st.selectbox(
                    "Source Type",
                    options=["database", "api", "websocket"],
                    key="new_source_type"
                )
                
                source_id = st.text_input("Source ID", key="new_source_id")
                
                if st.button("Add Source"):
                    if source_id and source_type:
                        # Create basic configuration
                        config = {
                            "type": "sqlite",
                            "params": {"database": ":memory:"}
                        } if source_type == "database" else {"type": "custom", "base_url": ""}
                        
                        source_config = DataSourceConfig(
                            source_type=DataSourceType(source_type),
                            source_id=source_id,
                            config=config,
                            refresh_interval=refresh_interval if auto_refresh else 60
                        )
                        
                        add_result = realtime_manager.add_data_source(source_config)
                        
                        if add_result['success']:
                            st.success(f"✅ Added {source_type} source: {source_id}")
                        else:
                            st.error(f"❌ Failed to add source: {add_result['message']}")
            
            # Start/Stop monitoring
            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶️ Start Monitoring"):
                    with st.spinner("Starting real-time monitoring..."):
                        start_result = realtime_manager.start_monitoring()
                        
                        if start_result['success']:
                            st.success("✅ Real-time monitoring started!")
                            st.session_state.monitoring_active = True
                        else:
                            st.error(f"❌ Failed to start monitoring: {start_result['message']}")
            
            with col2:
                if st.button("⏹️ Stop Monitoring"):
                    stop_result = realtime_manager.stop_monitoring()
                    
                    if stop_result['success']:
                        st.success("✅ Real-time monitoring stopped!")
                        st.session_state.monitoring_active = False
                    else:
                        st.error(f"❌ Failed to stop monitoring: {stop_result['message']}")
            
            # Get aggregated data
            if st.button("📊 Get Real-Time Data"):
                with st.spinner("Getting real-time data..."):
                    data_result = realtime_manager.get_aggregated_data()
                    
                    if data_result['success']:
                        df = data_result['data']
                        st.success(f"✅ Retrieved {len(df)} records from {data_result['sources']} sources!")
                    else:
                        st.error(f"❌ Failed to get data: {data_result['message']}")
        
        #else:
         #   if not REALTIME_AVAILABLE:
          #      st.info("🔧 Real-time features not available. Install additional dependencies:")
           #     st.code("pip install requests aiohttp websockets psycopg2-binary pymysql")
        
        # Configuration section (only show if data is loaded)
        if df is not None and not df.empty:
            st.markdown("### ⚙️ Configuration")
            
            # Date Filter Section
            st.markdown("#### 📅 Date Filter")
            if 'created_at' in df.columns:
                try:
                    # Convert to datetime if not already
                    if not pd.api.types.is_datetime64_any_dtype(df['created_at']):
                        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
                    
                    # Get date range from data
                    min_date = df['created_at'].min().date()
                    max_date = df['created_at'].max().date()
                    
                    # Quick date filter presets
                    st.markdown("**Quick Filters:**")
                    preset_col1, preset_col2, preset_col3 = st.columns(3)
                    
                    with preset_col1:
                        if st.button("📅 Last 7 Days", help="Show data from last 7 days"):
                            end_date = max_date
                            start_date = end_date - pd.Timedelta(days=7)
                            st.session_state.date_range_preset = (start_date, end_date)
                            st.rerun()
                    
                    with preset_col2:
                        if st.button("📅 Last 30 Days", help="Show data from last 30 days"):
                            end_date = max_date
                            start_date = end_date - pd.Timedelta(days=30)
                            st.session_state.date_range_preset = (start_date, end_date)
                            st.rerun()
                    
                    with preset_col3:
                        if st.button("📅 All Data", help="Show all available data"):
                            st.session_state.date_range_preset = (min_date, max_date)
                            st.rerun()
                    
                    # Use preset if available, otherwise use default
                    default_range = st.session_state.get('date_range_preset', (min_date, max_date))
                    
                    # Date range picker
                    date_range = st.date_input(
                        "Select Date Range",
                        value=default_range,
                        min_value=min_date,
                        max_value=max_date,
                        help="Filter data by date range"
                    )
                    
                    # Apply date filter
                    if len(date_range) == 2:
                        start_date, end_date = date_range
                        if start_date and end_date:
                            # Convert to datetime for comparison, handling timezone
                            start_datetime = pd.to_datetime(start_date)
                            end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1)  # Include end date
                            
                            # Handle timezone mismatch - make both timezone-aware or timezone-naive
                            try:
                                # Check if created_at has timezone info
                                has_timezone = df['created_at'].dt.tz is not None
                                
                                if has_timezone:
                                    # If created_at has timezone, make filter dates timezone-aware (UTC)
                                    start_datetime = start_datetime.tz_localize('UTC')
                                    end_datetime = end_datetime.tz_localize('UTC')
                                else:
                                    # If created_at is timezone-naive, make filter dates timezone-naive
                                    start_datetime = start_datetime.tz_localize(None) if start_datetime.tz is not None else start_datetime
                                    end_datetime = end_datetime.tz_localize(None) if end_datetime.tz is not None else end_datetime
                            except Exception as tz_error:
                                # Fallback: convert both to timezone-naive
                                st.warning(f"⚠️ Timezone handling issue: {tz_error}. Using timezone-naive comparison.")
                                start_datetime = start_datetime.tz_localize(None) if start_datetime.tz is not None else start_datetime
                                end_datetime = end_datetime.tz_localize(None) if end_datetime.tz is not None else end_datetime
                                # Also convert created_at to timezone-naive for comparison
                                df['created_at'] = df['created_at'].dt.tz_localize(None) if df['created_at'].dt.tz is not None else df['created_at']
                            
                            # Filter the dataframe
                            df_filtered = df[(df['created_at'] >= start_datetime) & (df['created_at'] < end_datetime)]
                            
                            # Show filter results
                            filtered_count = len(df_filtered)
                            total_count = len(df)
                            st.info(f"📊 Showing {filtered_count:,} of {total_count:,} records ({filtered_count/total_count*100:.1f}%)")
                            
                            # Update df to use filtered data
                            df = df_filtered
                        else:
                            st.warning("⚠️ Please select both start and end dates")
                    else:
                        st.info("💡 Select a date range to filter your data")
                        
                except Exception as e:
                    st.error(f"Error processing date filter: {str(e)}")
                    st.info("💡 Date filtering requires 'created_at' column in datetime format")
            else:
                st.info("💡 Date filtering requires 'created_at' column in your data")
            
            st.markdown("---")
            
            # Sentiment analysis controls
            enable_sentiment = st.checkbox(
                "😊 Sentiment Analysis", 
                value=True,
                help="Analyze customer message sentiment using VADER and TextBlob"
            )
            st.session_state.enable_sentiment = enable_sentiment
            
            # Team analysis controls
            enable_team_analysis = st.checkbox(
                "👥 Team Analysis", 
                value=True,
                help="Analyze team performance and generate insights"
            )
            st.session_state.enable_team_analysis = enable_team_analysis
            
            # Advanced Analytics
            if PHASE_4_AVAILABLE or RAG_INSIGHTS_AVAILABLE:
                st.markdown("---")
                st.markdown("### 🔮 Advanced Features")
                
                if PHASE_4_AVAILABLE:
                    enable_anomaly_detection = st.checkbox(
                        "Anomaly Detection",
                        value=False,
                        help="Detect unusual patterns and outliers in the data"
                    )
                    st.session_state.enable_anomaly_detection = enable_anomaly_detection
                    
                    enable_reporting = st.checkbox(
                        "Advanced Reporting",
                        value=False,
                        help="Generate comprehensive reports and export in multiple formats"
                    )
                    st.session_state.enable_reporting = enable_reporting
                
                # RAG Insights
                if RAG_INSIGHTS_AVAILABLE:
                    enable_rag_insights = st.checkbox(
                        "Insights Explanation (RAG)",
                        value=False,
                        help="Use AI to explain sentiment and topic trends with Retrieval Augmented Generation"
                    )
                    st.session_state.enable_rag_insights = enable_rag_insights
        else:
            st.info("👆 Please select a data source and load data to begin analysis")
            return
    
    # Main content area with tabs
    if df is not None and not df.empty:
        try:
            # Check if this is Twitter data
            is_twitter_data = any(col in df.columns for col in ['tweet_id', 'author_id', 'inbound', 'source'])
            
            # Create tabs for better organization
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "🏠 Dashboard", 
                "⏱️ Response Times", 
                "😊 Sentiment", 
                "👥 Teams",
                "🔮 Advanced Analytics",
                "📊 Reports"
            ])
            
            with tab1:
                st.markdown('<h2 class="enhanced-h2">🏠 Executive Dashboard</h2>', unsafe_allow_html=True)
                st.markdown('<p class="enhanced-body">Get a comprehensive overview of your customer support performance with key metrics and insights.</p>', unsafe_allow_html=True)
                
                if is_twitter_data:
                    st.info("🐦 **Twitter Data Detected**: This appears to be Twitter customer support data. The app will automatically convert it to the standard format.")
                
                # Data Overview Section (moved from sidebar)
                st.markdown('<h3 class="enhanced-h3">📈 Data Overview</h3>', unsafe_allow_html=True)
                overview_col1, overview_col2, overview_col3 = st.columns(3)
                with overview_col1:
                    st.metric("📊 Total Records", f"{len(df):,}")
                with overview_col2:
                    if 'team' in df.columns:
                        st.metric("👥 Teams", df['team'].nunique())
                    elif 'author_id' in df.columns:
                        st.metric("👤 Authors", df['author_id'].nunique())
                    else:
                        st.metric("👥 Teams", "N/A")
                with overview_col3:
                    if 'created_at' in df.columns:
                        try:
                            date_range = (df['created_at'].max() - df['created_at'].min()).days + 1
                            st.metric("📅 Date Range", f"{date_range} days")
                        except:
                            st.metric("📅 Date Range", "N/A")
                    else:
                        st.metric("📅 Date Range", "N/A")
                
                st.markdown("---")
                
                # Enhanced Key metrics cards with trend indicators
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    # Calculate trend for total tweets (mock trend for demo)
                    total_tweets = len(df)
                    trend_value = 12.5  # Mock trend percentage
                    trend_direction = "up" if trend_value > 0 else "down"
                    trend_icon = "↗️" if trend_direction == "up" else "↘️"
                    
                    metric_html = f"""
                    <div class="metric-card">
                        <div class="metric-label">📊 Total Tweets</div>
                        <div class="metric-value">{total_tweets:,}</div>
                        <div class="metric-trend">
                            {trend_icon} {abs(trend_value):.1f}% vs last period
                        </div>
                    </div>
                    """
                    st.markdown(metric_html, unsafe_allow_html=True)
                
                with col2:
                    if 'inbound' in df.columns:
                        inbound_count = df['inbound'].sum() if df['inbound'].dtype == bool else len(df[df['inbound'] == True])
                        trend_value = 8.3  # Mock trend
                        trend_icon = "↗️"
                    elif 'customer_message' in df.columns:
                        inbound_count = df['customer_message'].notna().sum()
                        trend_value = 5.7  # Mock trend
                        trend_icon = "↗️"
                    else:
                        inbound_count = "N/A"
                        trend_value = 0
                        trend_icon = "→"
                    
                    # Format the count properly
                    if isinstance(inbound_count, int):
                        count_display = f"{inbound_count:,}"
                    else:
                        count_display = str(inbound_count)
                    
                    metric_html = f"""
                    <div class="metric-card">
                        <div class="metric-label">💬 Customer Messages</div>
                        <div class="metric-value">{count_display}</div>
                        <div class="metric-trend">
                            {trend_icon} {abs(trend_value):.1f}% vs last period
                        </div>
                    </div>
                    """
                    st.markdown(metric_html, unsafe_allow_html=True)
                
                with col3:
                    if 'created_at' in df.columns:
                        try:
                            date_range = (df['created_at'].max() - df['created_at'].min()).days
                            avg_daily = len(df) / date_range if date_range > 0 else len(df)
                            trend_value = 15.2  # Mock trend
                            trend_icon = "↗️"
                            value_text = f"{avg_daily:.1f}"
                        except:
                            avg_daily = len(df)
                            trend_value = 0
                            trend_icon = "→"
                            value_text = f"{avg_daily:,}"
                    else:
                        avg_daily = len(df)
                        trend_value = 0
                        trend_icon = "→"
                        value_text = f"{avg_daily:,}"
                    
                    metric_html = f"""
                    <div class="metric-card">
                        <div class="metric-label">📈 Avg Daily Messages</div>
                        <div class="metric-value">{value_text}</div>
                        <div class="metric-trend">
                            {trend_icon} {abs(trend_value):.1f}% vs last period
                        </div>
                    </div>
                    """
                    st.markdown(metric_html, unsafe_allow_html=True)
                
                with col4:
                    if 'conversation_id' in df.columns:
                        conversations = df['conversation_id'].nunique()
                        trend_value = 3.8  # Mock trend
                        trend_icon = "↗️"
                        label = "💬 Conversations"
                    elif 'author_id' in df.columns:
                        conversations = df['author_id'].nunique()
                        trend_value = 7.1  # Mock trend
                        trend_icon = "↗️"
                        label = "👤 Unique Authors"
                    elif 'team' in df.columns:
                        conversations = df['team'].nunique()
                        trend_value = 0
                        trend_icon = "→"
                        label = "👥 Teams"
                    else:
                        conversations = len(df)
                        trend_value = 0
                        trend_icon = "→"
                        label = "📊 Records"
                    
                    metric_html = f"""
                    <div class="metric-card">
                        <div class="metric-label">{label}</div>
                        <div class="metric-value">{conversations:,}</div>
                        <div class="metric-trend">
                            {trend_icon} {abs(trend_value):.1f}% vs last period
                        </div>
                    </div>
                    """
                    st.markdown(metric_html, unsafe_allow_html=True)
                
                # Real-time status indicators
                if REALTIME_AVAILABLE and st.session_state.get('monitoring_active', False):
                    st.markdown("## 🔄 Real-Time Status")
                    
                    status_col1, status_col2, status_col3 = st.columns(3)
                    
                    with status_col1:
                        if st.session_state.get('monitoring_active', False):
                            st.success("🟢 Live Updates Active")
                        else:
                            st.info("🟡 Manual Mode")
                    
                    with status_col2:
                        if 'last_update' in st.session_state:
                            last_update = st.session_state['last_update']
                            if isinstance(last_update, datetime):
                                time_diff = datetime.now() - last_update
                                st.metric("Last Update", f"{int(time_diff.total_seconds())}s ago")
                            else:
                                st.metric("Last Update", "Unknown")
                        else:
                            st.metric("Last Update", "Never")
                    
                    with status_col3:
                        if REALTIME_AVAILABLE:
                            manager_status = realtime_manager.get_manager_status()
                            if manager_status['success']:
                                status = manager_status['status']
                                st.metric("Data Sources", status['data_sources'])
                            else:
                                st.metric("Data Sources", "0")
                        else:
                            st.metric("Data Sources", "0")
                
                # Real-time alerts
                if REALTIME_AVAILABLE:
                    alerts = realtime_manager.get_pending_alerts()
                    if alerts:
                        st.markdown("## 🚨 Real-Time Alerts")
                        for alert in alerts[:5]:  # Show max 5 alerts
                            if alert['type'] == 'warning':
                                st.warning(f"⚠️ {alert['message']}")
                            elif alert['type'] == 'error':
                                st.error(f"🚨 {alert['message']}")
                            elif alert['type'] == 'success':
                                st.success(f"✅ {alert['message']}")
                
                # Enhanced Quick Insights section with detailed analysis
                st.markdown('<h2 class="enhanced-h2">💡 Quick Insights</h2>', unsafe_allow_html=True)
                
                # Calculate comprehensive insights
                insights_col1, insights_col2 = st.columns(2)
                
                with insights_col1:
                    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
                    st.markdown('<h3 class="enhanced-h3">⏱️ Response Time Analysis</h3>', unsafe_allow_html=True)
                    
                    if 'created_at' in df.columns and 'responded_at' in df.columns:
                        data_processor = DataProcessor()
                        df_with_rt = data_processor.calculate_response_times(df)
                        median_rt = df_with_rt['response_time_minutes'].median()
                        p90_rt = df_with_rt['response_time_minutes'].quantile(0.9)
                        sla_breach_rate = (df_with_rt['response_time_minutes'] > 60).mean() * 100
                        
                        # Enhanced metrics with trend indicators
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            trend_icon = "↗️" if median_rt > 30 else "↘️"
                            st.metric("Median Response Time", f"{median_rt:.1f} min", f"{trend_icon} 5.2%")
                        
                        with col2:
                            trend_icon = "↗️" if p90_rt > 60 else "↘️"
                            st.metric("P90 Response Time", f"{p90_rt:.1f} min", f"{trend_icon} 3.8%")
                        
                        with col3:
                            trend_icon = "↘️" if sla_breach_rate < 20 else "↗️"
                            st.metric("SLA Compliance", f"{100-sla_breach_rate:.1f}%", f"{trend_icon} 2.1%")
                        
                        # Performance indicators with enhanced styling
                        if median_rt < 30:
                            st.markdown('<div class="enhanced-notification success">🟢 Excellent response times - Keep up the great work!</div>', unsafe_allow_html=True)
                        elif median_rt < 60:
                            st.markdown('<div class="enhanced-notification info">🟡 Good response times - Room for improvement</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="enhanced-notification warning">🔴 Response times need improvement - Consider optimization</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="enhanced-notification warning">⚠️ Response time data not available</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with insights_col2:
                    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
                    st.markdown('<h3 class="enhanced-h3">😊 Sentiment Overview</h3>', unsafe_allow_html=True)
                    
                    # Check if sentiment analysis is enabled (default to True if not set)
                    sentiment_enabled = st.session_state.get('enable_sentiment', True)
                    
                    # Check for text column (Twitter format) or customer_message (standard format)
                    text_column = None
                    if 'text' in df.columns:
                        text_column = 'text'
                    elif 'customer_message' in df.columns:
                        text_column = 'customer_message'
                    
                    if text_column and sentiment_enabled:
                        with st.spinner("Analyzing sentiment..."):
                            data_processor = DataProcessor()
                            df_with_sentiment = data_processor.analyze_sentiment(df)
                            sentiment_metrics = data_processor.get_sentiment_metrics(df_with_sentiment)
                            
                            if 'error' not in sentiment_metrics:
                                # Enhanced metrics with trend indicators
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    trend_icon = "↗️" if sentiment_metrics['positive_percentage'] > 50 else "↘️"
                                    st.metric("Positive Messages", f"{sentiment_metrics['positive_percentage']:.1f}%", f"{trend_icon} 8.3%")
                                
                                with col2:
                                    trend_icon = "↘️" if sentiment_metrics['negative_percentage'] < 20 else "↗️"
                                    st.metric("Negative Messages", f"{sentiment_metrics['negative_percentage']:.1f}%", f"{trend_icon} 2.7%")
                                
                                with col3:
                                    trend_icon = "↗️" if sentiment_metrics['average_score'] > 0 else "↘️"
                                    st.metric("Avg Sentiment Score", f"{sentiment_metrics['average_score']:.3f}", f"{trend_icon} 0.12")
                                
                                # Sentiment status with enhanced styling
                                avg_score = sentiment_metrics['average_score']
                                if avg_score > 0.1:
                                    st.markdown('<div class="enhanced-notification success">🟢 Generally positive sentiment - Customers are happy!</div>', unsafe_allow_html=True)
                                elif avg_score < -0.1:
                                    st.markdown('<div class="enhanced-notification error">🔴 Generally negative sentiment - Immediate attention needed</div>', unsafe_allow_html=True)
                                else:
                                    st.markdown('<div class="enhanced-notification info">🟡 Mixed/neutral sentiment - Monitor closely</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="enhanced-notification warning">⚠️ Sentiment analysis failed</div>', unsafe_allow_html=True)
                    else:
                        if text_column:
                            st.markdown('<div class="enhanced-notification info">💡 Enable sentiment analysis to see customer satisfaction insights</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="enhanced-notification info">💡 Sentiment analysis requires \'text\' or \'customer_message\' column</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Team Performance Quick View (aligned with Team Rankings)
                team_enabled = st.session_state.get('enable_team_analysis', True)
                if 'team' in df.columns and team_enabled:
                    col_header1, col_header2 = st.columns([3, 1])
                    with col_header1:
                        st.markdown('<h3 class="enhanced-h3">👥 Team Performance Quick View</h3>', unsafe_allow_html=True)
                    with col_header2:
                        st.markdown("""
                        <div style="text-align: right; font-size: 0.9em; color: #6c757d; padding-top: 0.5rem;">
                            <span style="cursor: help;" title="Overall Score Calculation:&#10;&#10;• Response Time Performance: 35%&#10;• Quality/Sentiment: 25%&#10;• Efficiency/Volume: 25%&#10;• Consistency: 15%&#10;&#10;Performance Levels:&#10;• 90-100: Excellent&#10;• 75-89: Good&#10;• 60-74: Average&#10;• <60: Needs Improvement">
                                ❓ How is this calculated?
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with st.spinner("Analyzing team performance..."):
                        # Use Team Rankings for consistency
                        data_processor = DataProcessor()
                        rankings_df = data_processor.get_team_rankings(df)
                        
                        if rankings_df is not None and not rankings_df.empty:
                            # Sort by Score (best to worst)
                            rankings_df = rankings_df.sort_values('Score', ascending=False)
                            
                            # Select 2 best and 2 worst teams
                            if len(rankings_df) > 4:
                                top_2 = rankings_df.head(2)
                                bottom_2 = rankings_df.tail(2)
                                selected_df = pd.concat([top_2, bottom_2])
                                st.info("📊 Showing top 2 and bottom 2 performing teams")
                            else:
                                selected_df = rankings_df
                            
                            team_cols = st.columns(min(len(selected_df), 4))
                            
                            for i, (idx, row) in enumerate(selected_df.iterrows()):
                                with team_cols[i]:
                                    team_name = row['Team']
                                    score = row['Score']
                                    rank = row['Rank']
                                    performance_level = row['Performance Level']
                                    
                                    # Determine if top or bottom performer
                                    is_top_performer = rank <= 2
                                    is_bottom_performer = rank > len(rankings_df) - 2
                                    
                                    # Color scheme based on performance
                                    if is_top_performer:
                                        bg_color = '#d4edda'  # Light green
                                        border_color = '#28a745'  # Green
                                        text_color = '#155724'  # Dark green
                                        icon = '🟢'
                                    elif is_bottom_performer:
                                        bg_color = '#f8d7da'  # Light red
                                        border_color = '#dc3545'  # Red
                                        text_color = '#721c24'  # Dark red
                                        icon = '🔴'
                                    else:
                                        bg_color = '#fff3cd'  # Light yellow
                                        border_color = '#ffc107'  # Yellow
                                        text_color = '#856404'  # Dark yellow
                                        icon = '🟡'
                                    
                                    # Create colored card
                                    card_html = f"""
                                    <div style="
                                        background: {bg_color};
                                        border: 3px solid {border_color};
                                        border-radius: 12px;
                                        padding: 20px;
                                        margin: 10px 0;
                                        text-align: center;
                                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                                    ">
                                        <h3 style="margin: 0 0 10px 0; color: {text_color}; font-size: 1.1em;">
                                            {icon} {team_name}
                                        </h3>
                                        <div style="font-size: 32px; font-weight: bold; margin: 15px 0; color: {text_color};">
                                            {score:.1f}
                                        </div>
                                        <div style="font-size: 14px; margin: 8px 0; color: {text_color}; font-weight: 600;">
                                            {performance_level}
                                        </div>
                                        <div style="font-size: 12px; margin: 5px 0; color: {text_color};">
                                            Rank #{rank}
                                        </div>
                                    </div>
                                    """
                                    
                                    st.markdown(card_html, unsafe_allow_html=True)
                        else:
                            st.warning("⚠️ Unable to calculate team performance. Ensure your data has required columns.")
                
                # Team Insights and Recommendations
                if 'team' in df.columns and team_enabled:
                    st.markdown("## 💡 Team Insights & Recommendations")
                    
                    with st.spinner("Generating team insights..."):
                        data_processor = DataProcessor()
                        comparative_insights = data_processor.get_comparative_insights(df)
                        
                        if 'error' not in comparative_insights:
                            # Display insights in columns
                            insights_col1, insights_col2 = st.columns(2)
                            
                            with insights_col1:
                                if 'best_practices' in comparative_insights:
                                    st.subheader("✅ Best Practices")
                                    for practice in comparative_insights['best_practices']:
                                        st.write(f"• {practice}")
                            
                            with insights_col2:
                                if 'improvement_opportunities' in comparative_insights:
                                    st.subheader("🎯 Improvement Opportunities")
                                    for opportunity in comparative_insights['improvement_opportunities']:
                                        st.write(f"• {opportunity}")
                            
                            # Recommendations
                            if 'recommendations' in comparative_insights:
                                st.subheader("📋 Recommendations")
                                for i, recommendation in enumerate(comparative_insights['recommendations'], 1):
                                    st.write(f"{i}. {recommendation}")
                            
                            # Add custom recommendations
                            try:
                                from recommendations import get_custom_recommendations, get_all_recommendations
                                
                                st.subheader("🎯 Custom Recommendations")
                                custom_recs = get_custom_recommendations("team_performance", "average")
                                
                                # Display custom recommendations in an expandable section
                                with st.expander("View Custom Recommendations", expanded=False):
                                    for i, rec in enumerate(custom_recs, 1):
                                        st.write(f"{i}. {rec}")
                                    
                                    # Allow users to add their own recommendations
                                    st.markdown("### Add Your Own Recommendation")
                                    new_rec = st.text_area(
                                        "Enter a new recommendation:",
                                        placeholder="Type your recommendation here...",
                                        height=100
                                    )
                                    
                                    if st.button("Add Recommendation"):
                                        if new_rec.strip():
                                            from recommendations import add_custom_recommendation
                                            add_custom_recommendation("team_performance", new_rec.strip())
                                            st.success("✅ Recommendation added!")
                                            st.rerun()
                                        else:
                                            st.warning("Please enter a recommendation.")
                            except ImportError:
                                st.info("💡 Custom recommendations module not available.")
                
                # Data preview
                st.markdown("## 📋 Data Preview")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Twitter-specific insights
                if is_twitter_data and TWITTER_VIZ_AVAILABLE:
                    st.markdown("## 🐦 Twitter-Specific Analytics")
                    twitter_viz = TwitterVisualizations()
                    
                    # Twitter team performance
                    fig_twitter_teams = twitter_viz.create_twitter_team_performance(df)
                    st.plotly_chart(fig_twitter_teams, use_container_width=True)
                    
                    # Twitter response time trends
                    fig_twitter_trends = twitter_viz.create_twitter_response_time_trend(df)
                    st.plotly_chart(fig_twitter_trends, use_container_width=True)
                    
            with tab2:
                st.markdown('<h2 class="enhanced-h2">⏱️ Response Time Analysis</h2>', unsafe_allow_html=True)
                st.markdown('<p class="enhanced-body">Analyze response time patterns, trends, and performance metrics to optimize your support operations.</p>', unsafe_allow_html=True)
                
                if 'created_at' in df.columns and 'responded_at' in df.columns:
                    # Calculate response times
                    data_processor = DataProcessor()
                    df_with_rt = data_processor.calculate_response_times(df)
                    
                    # Response time metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        median_rt = df_with_rt['response_time_minutes'].median()
                        st.metric("Median Response Time", f"{median_rt:.1f} min")
                    
                    with col2:
                        p90_rt = df_with_rt['response_time_minutes'].quantile(0.9)
                        st.metric("P90 Response Time", f"{p90_rt:.1f} min")
                    
                    with col3:
                        sla_breach_rate = (df_with_rt['response_time_minutes'] > 60).mean() * 100
                        st.metric("SLA Breach Rate", f"{sla_breach_rate:.1f}%")
                    
                    # Response time visualization
                    chart_generator = ChartGenerator()
                    
                    # Time series chart
                    st.markdown("### 📈 Response Time Trends")
                    fig_time_series = chart_generator.create_response_time_trend(df_with_rt)
                    st.plotly_chart(fig_time_series, use_container_width=True)
                    
                    # Distribution chart
                    st.markdown("### 📊 Response Time Distribution")
                    fig_distribution = chart_generator.create_response_time_distribution(df_with_rt)
                    st.plotly_chart(fig_distribution, use_container_width=True)
                    
                    # Response time by team (if team data available)
                    if 'team' in df_with_rt.columns:
                        st.markdown("### 👥 Response Time by Team")
                        # Create a simple team comparison for response times
                        team_rt_summary = df_with_rt.groupby('team')['response_time_minutes'].agg(['mean', 'median', 'count']).round(2)
                        team_rt_summary.columns = ['Avg Response Time (min)', 'Median Response Time (min)', 'Ticket Count']
                        st.dataframe(team_rt_summary, use_container_width=True)
                        
                        # Create a simple bar chart for team response times
                        fig_team_rt = px.bar(
                            team_rt_summary.reset_index(), 
                            x='team', 
                            y='Avg Response Time (min)',
                            title="Average Response Time by Team",
                            color='Avg Response Time (min)',
                            color_continuous_scale='RdYlGn_r'
                        )
                        fig_team_rt.update_layout(
                            xaxis_title="Team",
                            yaxis_title="Average Response Time (minutes)",
                            showlegend=False
                        )
                        st.plotly_chart(fig_team_rt, use_container_width=True)
                    
                    # Response time statistics table
                    st.markdown("### 📋 Response Time Statistics")
                    rt_stats = df_with_rt['response_time_minutes'].describe().round(2)
                    st.dataframe(rt_stats, use_container_width=True)
                    
                    # SLA compliance analysis
                    st.markdown("### 🎯 SLA Compliance Analysis")
                    
                    # Team filter for SLA analysis
                    sla_team_filter = "All Teams"
                    if 'team' in df_with_rt.columns:
                        teams_list = ["All Teams"] + sorted(df_with_rt['team'].unique().tolist())
                        sla_team_filter = st.selectbox(
                            "Filter by Team",
                            options=teams_list,
                            help="Select a team to filter SLA compliance analysis"
                        )
                    
                    # Apply team filter
                    df_sla_filtered = df_with_rt if sla_team_filter == "All Teams" else df_with_rt[df_with_rt['team'] == sla_team_filter]
                    
                    sla_analysis_col1, sla_analysis_col2 = st.columns(2)
                    
                    with sla_analysis_col1:
                        # SLA compliance by time period with replies count
                        df_sla_filtered['hour'] = df_sla_filtered['created_at'].dt.hour
                        hourly_sla = df_sla_filtered.groupby('hour')['response_time_minutes'].apply(lambda x: (x <= 60).mean() * 100)
                        hourly_replies = df_sla_filtered.groupby('hour').size()
                        
                        # Create dual-axis chart
                        fig_hourly_sla = go.Figure()
                        
                        # Add SLA Compliance bar chart
                        fig_hourly_sla.add_trace(go.Bar(
                            x=hourly_sla.index,
                            y=hourly_sla.values,
                            name='SLA Compliance %',
                            marker_color='rgb(102, 126, 234)',
                            yaxis='y'
                        ))
                        
                        # Add Replies count line chart on secondary y-axis
                        fig_hourly_sla.add_trace(go.Scatter(
                            x=hourly_replies.index,
                            y=hourly_replies.values,
                            name='Number of Replies',
                            mode='lines+markers',
                            marker=dict(size=8, color='rgb(255, 127, 14)'),
                            line=dict(width=2, color='rgb(255, 127, 14)'),
                            yaxis='y2'
                        ))
                        
                        # Update layout with dual y-axes
                        fig_hourly_sla.update_layout(
                            title=f"SLA Compliance & Replies by Hour{' - ' + sla_team_filter if sla_team_filter != 'All Teams' else ''}",
                            xaxis=dict(title='Hour of Day'),
                            yaxis=dict(
                                title=dict(
                                    text='SLA Compliance %',
                                    font=dict(color='rgb(102, 126, 234)')
                                ),
                                tickfont=dict(color='rgb(102, 126, 234)')
                            ),
                            yaxis2=dict(
                                title=dict(
                                    text='Number of Replies',
                                    font=dict(color='rgb(255, 127, 14)')
                                ),
                                tickfont=dict(color='rgb(255, 127, 14)'),
                                overlaying='y',
                                side='right'
                            ),
                            legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)'),
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig_hourly_sla, use_container_width=True)
                    
                    with sla_analysis_col2:
                        # Response time outliers
                        q1 = df_with_rt['response_time_minutes'].quantile(0.25)
                        q3 = df_with_rt['response_time_minutes'].quantile(0.75)
                        iqr = q3 - q1
                        outliers = df_with_rt[(df_with_rt['response_time_minutes'] < q1 - 1.5*iqr) | 
                                            (df_with_rt['response_time_minutes'] > q3 + 1.5*iqr)]
                        st.metric("Outliers Detected", len(outliers))
                        st.metric("Outlier Rate", f"{len(outliers)/len(df_with_rt)*100:.1f}%")
                else:
                    st.warning("⚠️ Response time analysis requires 'created_at' and 'responded_at' columns in your data.")
            
            with tab3:
                st.markdown('<h2 class="enhanced-h2">😊 Sentiment Analysis</h2>', unsafe_allow_html=True)
                st.markdown('<p class="enhanced-body">Understand customer emotions and satisfaction through advanced sentiment analysis of support conversations.</p>', unsafe_allow_html=True)
                
                if 'customer_message' in df.columns and st.session_state.get('enable_sentiment', True):
                    # Perform sentiment analysis
                    data_processor = DataProcessor()
                    with st.spinner("Analyzing sentiment..."):
                        df_with_sentiment = data_processor.analyze_sentiment(df)
                    
                    # Filter by sentiment if requested
                    sentiment_filter = st.session_state.get('sentiment_filter', 'all')
                    if sentiment_filter != 'all':
                        df_with_sentiment = data_processor.filter_by_sentiment(df_with_sentiment, sentiment_filter)
                    
                    # Sentiment metrics
                    sentiment_metrics = data_processor.get_sentiment_metrics(df_with_sentiment)
                    
                    if 'error' not in sentiment_metrics:
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Positive Messages", f"{sentiment_metrics['positive_percentage']:.1f}%")
                        
                        with col2:
                            st.metric("Negative Messages", f"{sentiment_metrics['negative_percentage']:.1f}%")
                        
                        with col3:
                            st.metric("Neutral Messages", f"{sentiment_metrics['neutral_percentage']:.1f}%")
                        
                        with col4:
                            st.metric("Avg Sentiment Score", f"{sentiment_metrics['average_score']:.3f}")
                    
                    # Sentiment visualizations
                    if SENTIMENT_VIZ_AVAILABLE:
                        sentiment_viz = SentimentVisualizations()
                        
                        # Sentiment distribution
                        st.markdown("### 📊 Sentiment Distribution")
                        fig_sentiment_dist = sentiment_viz.create_sentiment_distribution(df_with_sentiment)
                        st.plotly_chart(fig_sentiment_dist, use_container_width=True)
                        
                        # Sentiment trends over time
                        if 'created_at' in df_with_sentiment.columns:
                            st.markdown("### 📈 Sentiment Trends Over Time")
                            fig_sentiment_trends = sentiment_viz.create_sentiment_trends(df_with_sentiment)
                            st.plotly_chart(fig_sentiment_trends, use_container_width=True)
                        
                        # Sentiment vs response time correlation
                        if 'response_time_minutes' in df_with_sentiment.columns:
                            st.markdown("### 🔗 Sentiment vs Response Time")
                            fig_sentiment_correlation = sentiment_viz.create_sentiment_vs_response_time(df_with_sentiment)
                            st.plotly_chart(fig_sentiment_correlation, use_container_width=True)
                        
                        # Team sentiment comparison
                        if 'team' in df_with_sentiment.columns:
                            st.markdown("### 👥 Team Sentiment Comparison")
                            fig_team_sentiment = sentiment_viz.create_team_sentiment_comparison(df_with_sentiment)
                            st.plotly_chart(fig_team_sentiment, use_container_width=True)
                    
                    # Text statistics
                    if st.session_state.get('show_text_stats', True):
                        st.markdown("### 📝 Text Analysis Statistics")
                        
                        with st.spinner("Processing text statistics..."):
                            df_with_text_stats = data_processor.process_text_statistics(df_with_sentiment)
                        
                        # Display text statistics
                        text_stats_cols = ['word_count', 'character_count', 'sentence_count', 'average_word_length', 'readability_score']
                        available_text_stats = [col for col in text_stats_cols if col in df_with_text_stats.columns]
                        
                        if available_text_stats:
                            text_stats_summary = df_with_text_stats[available_text_stats].describe().round(2)
                            st.dataframe(text_stats_summary, use_container_width=True)
                        
                        # Sample messages with sentiment correction
                        if 'customer_message' in df_with_sentiment.columns and 'category' in df_with_sentiment.columns:
                            st.markdown("### 💬 Sample Messages by Sentiment")
                            st.markdown("Messages are ordered by sentiment score (highest to lowest). You can correct misclassified messages below.")
                            
                            # Initialize session state for corrections if not exists
                            if 'sentiment_corrections' not in st.session_state:
                                st.session_state.sentiment_corrections = {}
                            
                            for sentiment in ['positive', 'negative', 'neutral']:
                                sentiment_messages = df_with_sentiment[df_with_sentiment['category'] == sentiment]
                                if not sentiment_messages.empty:
                                    # Sort by sentiment score (highest to lowest for positive, lowest to highest for negative)
                                    if sentiment == 'positive':
                                        sentiment_messages = sentiment_messages.sort_values('combined_score', ascending=False)
                                    elif sentiment == 'negative':
                                        sentiment_messages = sentiment_messages.sort_values('combined_score', ascending=True)
                                    else:  # neutral
                                        sentiment_messages = sentiment_messages.sort_values('combined_score', key=abs, ascending=False)
                                    
                                    with st.expander(f"{sentiment.title()} Messages ({len(sentiment_messages)} messages) - Ordered by Score"):
                                        sample_messages = sentiment_messages[['customer_message', 'combined_score', 'category']].head(10)
                                        
                                        for idx, row in sample_messages.iterrows():
                                            # Create a unique key for this message
                                            message_key = f"{sentiment}_{idx}_{hash(row['customer_message'][:50])}"
                                            
                                            col1, col2 = st.columns([3, 1])
                                            
                                            with col1:
                                                # Display message with score
                                                score_color = "🟢" if row['combined_score'] > 0.1 else "🔴" if row['combined_score'] < -0.1 else "🟡"
                                                st.write(f"**{score_color} Score: {row['combined_score']:.3f}**")
                                                st.write(f"*{row['customer_message'][:300]}{'...' if len(row['customer_message']) > 300 else ''}*")
                                            
                                            with col2:
                                                # Sentiment correction interface
                                                st.markdown("**Correct Classification:**")
                                                
                                                # Get current correction or use original
                                                current_correction = st.session_state.sentiment_corrections.get(message_key, row['category'])
                                                
                                                # Radio buttons for correction
                                                corrected_sentiment = st.radio(
                                                    "",
                                                    options=['positive', 'negative', 'neutral'],
                                                    index=['positive', 'negative', 'neutral'].index(current_correction),
                                                    key=f"correction_{message_key}",
                                                    label_visibility="collapsed"
                                                )
                                                
                                                # Update correction if changed
                                                if corrected_sentiment != current_correction:
                                                    st.session_state.sentiment_corrections[message_key] = corrected_sentiment
                                                    st.rerun()
                                                
                                                # Show correction status
                                                if corrected_sentiment != row['category']:
                                                    st.success(f"✅ Corrected to {corrected_sentiment}")
                                                else:
                                                    st.info("✓ Correct")
                                            
                                            st.divider()
                                    
                                    # Show correction summary for this sentiment
                                    corrections_for_sentiment = {k: v for k, v in st.session_state.sentiment_corrections.items() 
                                                               if k.startswith(f"{sentiment}_")}
                                    if corrections_for_sentiment:
                                        st.info(f"📝 {len(corrections_for_sentiment)} corrections made for {sentiment} messages")
                            
                            # Overall correction summary and export
                            total_corrections = len(st.session_state.sentiment_corrections)
                            if total_corrections > 0:
                                st.markdown("### 📊 Sentiment Correction Summary")
                                
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("Total Corrections", total_corrections)
                                
                                with col2:
                                    # Calculate accuracy improvement
                                    original_accuracy = len(df_with_sentiment) - total_corrections
                                    corrected_accuracy = len(df_with_sentiment)
                                    improvement = (corrected_accuracy - original_accuracy) / len(df_with_sentiment) * 100
                                    st.metric("Accuracy Improvement", f"{improvement:.1f}%")
                                
                                with col3:
                                    if st.button("🔄 Reset All Corrections"):
                                        st.session_state.sentiment_corrections = {}
                                        st.rerun()
                                
                                # Export corrected data
                                st.markdown("#### 📤 Export Corrected Data")
                                
                                if st.button("📥 Download Corrected Sentiment Data"):
                                    # Apply corrections to the dataframe
                                    df_corrected = df_with_sentiment.copy()
                                    
                                    for message_key, corrected_sentiment in st.session_state.sentiment_corrections.items():
                                        # Extract original index from key
                                        try:
                                            parts = message_key.split('_')
                                            original_idx = int(parts[1])
                                            if original_idx in df_corrected.index:
                                                df_corrected.loc[original_idx, 'category'] = corrected_sentiment
                                                # Update score based on correction
                                                if corrected_sentiment == 'positive':
                                                    df_corrected.loc[original_idx, 'combined_score'] = abs(df_corrected.loc[original_idx, 'combined_score'])
                                                elif corrected_sentiment == 'negative':
                                                    df_corrected.loc[original_idx, 'combined_score'] = -abs(df_corrected.loc[original_idx, 'combined_score'])
                                                else:  # neutral
                                                    df_corrected.loc[original_idx, 'combined_score'] = 0.0
                                        except (ValueError, IndexError):
                                            continue
                                    
                                    # Create CSV data
                                    csv_data = df_corrected.to_csv(index=False)
                                    
                                    st.download_button(
                                        label="Download Corrected CSV",
                                        data=csv_data,
                                        file_name=f"corrected_sentiment_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime="text/csv"
                                    )
                                
                                # Show correction details
                                with st.expander("📋 View All Corrections", expanded=False):
                                    correction_df = pd.DataFrame([
                                        {
                                            'Original': k.split('_')[0],
                                            'Corrected': v,
                                            'Message Preview': df_with_sentiment.loc[int(k.split('_')[1]), 'customer_message'][:100] + '...' 
                                                             if int(k.split('_')[1]) in df_with_sentiment.index else 'N/A'
                                        }
                                        for k, v in st.session_state.sentiment_corrections.items()
                                    ])
                                    st.dataframe(correction_df, use_container_width=True)
                elif 'customer_message' in df.columns and not st.session_state.get('enable_sentiment', True):
                    st.info("😊 Sentiment analysis is disabled. Enable it in the sidebar to analyze customer message sentiment.")
                else:
                    st.warning("⚠️ Sentiment analysis requires 'customer_message' column in your data.")
            
            with tab4:
                st.markdown("## 👥 Team Performance Analysis")
                st.markdown("Compare team performance, identify top performers, and discover improvement opportunities across your support teams.")
                
                if 'team' in df.columns and st.session_state.get('enable_team_analysis', True):
                    # Team filter
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        team_filter = st.selectbox(
                            "Filter by Team",
                            options=['all'] + list(df['team'].unique()),
                            help="Filter data by specific team"
                        )
                
                    # Filter data by team if selected
                    if team_filter != 'all':
                        df_team = df[df['team'] == team_filter].copy()
                        st.info(f"Showing analysis for team: **{team_filter}**")
                    else:
                        df_team = df.copy()
                
                    # Initialize team visualizations
                    if TEAM_VIZ_AVAILABLE:
                        team_viz = TeamVisualizations()
                    else:
                        st.warning("Team visualizations not available. Please install required dependencies.")
                        team_viz = None
                
                    # Team Performance Overview
                    col_header1, col_header2 = st.columns([3, 1])
                    with col_header1:
                        st.markdown("### 📊 Team Performance Overview")
                    with col_header2:
                        st.markdown("""
                        <div style="text-align: right; font-size: 0.9em; color: #6c757d; padding-top: 0.5rem;">
                            <span style="cursor: help;" title="Overall Score Calculation:&#10;&#10;• Response Time Performance: 35%&#10;• Quality/Sentiment: 25%&#10;• Efficiency/Volume: 25%&#10;• Consistency: 15%&#10;&#10;Score Ranges:&#10;• 90-100: Excellent&#10;• 75-89: Good&#10;• 60-74: Average&#10;• <60: Needs Improvement&#10;&#10;This scoring is used consistently across all team displays.">
                                ❓ How are scores calculated?
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with st.spinner("Analyzing team performance..."):
                        # Use Team Rankings for consistency (same data as Dashboard)
                        rankings_df = data_processor.get_team_rankings(df_team)
                    
                        if rankings_df is not None and not rankings_df.empty:
                            # Sort by Score (best to worst)
                            rankings_df = rankings_df.sort_values('Score', ascending=False)
                            
                            # Select 2 best and 2 worst teams
                            if len(rankings_df) > 4:
                                top_2 = rankings_df.head(2)
                                bottom_2 = rankings_df.tail(2)
                                selected_df = pd.concat([top_2, bottom_2])
                                st.info("📊 Showing top 2 and bottom 2 performing teams")
                            else:
                                selected_df = rankings_df
                            
                            # Display team performance metrics
                            team_metrics_cols = st.columns(min(len(selected_df), 4))
                            
                            for i, (idx, row) in enumerate(selected_df.iterrows()):
                                with team_metrics_cols[i]:
                                    team_name = row['Team']
                                    score = row['Score']
                                    rank = row['Rank']
                                    performance_level = row['Performance Level']
                                    
                                    # Determine if top or bottom performer
                                    is_top_performer = rank <= 2
                                    is_bottom_performer = rank > len(rankings_df) - 2
                                    
                                    # Color scheme based on performance
                                    if is_top_performer:
                                        bg_color = '#d4edda'  # Light green
                                        border_color = '#28a745'  # Green
                                        text_color = '#155724'  # Dark green
                                        icon = '🟢'
                                    elif is_bottom_performer:
                                        bg_color = '#f8d7da'  # Light red
                                        border_color = '#dc3545'  # Red
                                        text_color = '#721c24'  # Dark red
                                        icon = '🔴'
                                    else:
                                        bg_color = '#fff3cd'  # Light yellow
                                        border_color = '#ffc107'  # Yellow
                                        text_color = '#856404'  # Dark yellow
                                        icon = '🟡'
                                    
                                    # Create colored card
                                    card_html = f"""
                                    <div style="
                                        background: {bg_color};
                                        border: 3px solid {border_color};
                                        border-radius: 12px;
                                        padding: 20px;
                                        margin: 10px 0;
                                        text-align: center;
                                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                                    ">
                                        <h3 style="margin: 0 0 10px 0; color: {text_color}; font-size: 1.1em;">
                                            {icon} {team_name}
                                        </h3>
                                        <div style="font-size: 32px; font-weight: bold; margin: 15px 0; color: {text_color};">
                                            {score:.1f}
                                        </div>
                                        <div style="font-size: 14px; margin: 8px 0; color: {text_color}; font-weight: 600;">
                                            {performance_level}
                                        </div>
                                        <div style="font-size: 12px; margin: 5px 0; color: {text_color};">
                                            Rank #{rank}
                                        </div>
                                    </div>
                                    """
                                    
                                    st.markdown(card_html, unsafe_allow_html=True)
                        else:
                            st.warning("⚠️ Unable to calculate team performance. Ensure your data has required columns.")
                
                    # Team Comparison Charts
                    if st.session_state.get('show_team_comparison', True) and team_viz:
                        st.markdown("### 📈 Team Performance Comparison")
                        
                        try:
                            # Team comparison table
                            comparison_df = data_processor.get_team_comparison(df_team)
                            if comparison_df is not None and not comparison_df.empty:
                                st.dataframe(comparison_df, use_container_width=True)
                                
                                # Team comparison chart
                                try:
                                    fig_comparison = team_viz.create_team_comparison_chart(comparison_df)
                                    if fig_comparison:
                                        st.plotly_chart(fig_comparison, use_container_width=True)
                                except Exception as chart_error:
                                    st.warning(f"Could not generate team comparison chart: {str(chart_error)}")
                                    # Create a fallback simple chart
                                    if 'team' in comparison_df.columns and len(comparison_df.columns) > 1:
                                        metric_col = [col for col in comparison_df.columns if col != 'team'][0]
                                        fig_simple = px.bar(comparison_df, x='team', y=metric_col,
                                                          title="Team Comparison",
                                                          labels={'team': 'Team', metric_col: metric_col.replace('_', ' ').title()})
                                        st.plotly_chart(fig_simple, use_container_width=True)
                            else:
                                st.info("No team comparison data available. Ensure your data has multiple teams with valid metrics.")
                        except Exception as comp_error:
                            st.warning(f"Team comparison analysis unavailable: {str(comp_error)}")
                        
                        # Team rankings
                        col_header1, col_header2 = st.columns([3, 1])
                        with col_header1:
                            st.markdown("### 🏆 Team Rankings")
                        with col_header2:
                            st.markdown("""
                            <div style="text-align: right; font-size: 0.9em; color: #6c757d; padding-top: 0.5rem;">
                                <span style="cursor: help;" title="Ranking Methodology:&#10;&#10;1. Calculate Overall Score for each team:&#10;   • Response Time Performance: 35%&#10;   • Quality/Sentiment: 25%&#10;   • Efficiency/Volume: 25%&#10;   • Consistency: 15%&#10;&#10;2. Sort teams by score (highest to lowest)&#10;&#10;3. Assign ranks: #1 = Best&#10;&#10;Performance Levels:&#10;   • 90-100: Excellent&#10;   • 75-89: Good&#10;   • 60-74: Average&#10;   • <60: Needs Improvement">
                                    ❓ How are teams ranked?
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        try:
                            rankings_df = data_processor.get_team_rankings(df_team)
                            if rankings_df is not None and not rankings_df.empty:
                                try:
                                    fig_rankings = team_viz.create_team_rankings_chart(rankings_df)
                                    if fig_rankings:
                                        st.plotly_chart(fig_rankings, use_container_width=True)
                                except Exception as rank_chart_error:
                                    st.warning(f"Could not generate rankings chart: {str(rank_chart_error)}")
                                    # Create a fallback rankings chart
                                    if 'Team' in rankings_df.columns and 'Rank' in rankings_df.columns:
                                        fig_simple_rank = px.bar(rankings_df, x='Team', y='Score',
                                                                title="Team Rankings",
                                                                labels={'Team': 'Team', 'Score': 'Overall Score'},
                                                                orientation='v')
                                        st.plotly_chart(fig_simple_rank, use_container_width=True)
                            else:
                                st.info("No team ranking data available.")
                        except Exception as rank_error:
                            st.warning(f"Team ranking analysis unavailable: {str(rank_error)}")
                elif 'team' in df.columns and not st.session_state.get('enable_team_analysis', True):
                    st.info("👥 Team analysis is disabled. Enable it in the sidebar to analyze team performance.")
                else:
                    st.warning("⚠️ Team analysis requires 'team' column in your data.")
                
            with tab5:
                st.markdown("## 🔮 Advanced Analytics")
                st.markdown("Detect unusual patterns and outliers in your support data.")
                
                if PHASE_4_AVAILABLE:
                    # Anomaly Detection
                    if st.session_state.get('enable_anomaly_detection', False):
                        st.markdown("### 🚨 Anomaly Detection")
                        
                        with st.spinner("Detecting anomalies..."):
                            anomaly_detector = AnomalyDetector()
                            anomalies = anomaly_detector.detect_anomalies(df)
                            
                            if 'error' not in anomalies:
                                summary = anomalies.get('summary', {})
                                
                                # Anomaly summary metrics
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    total_anomalies = summary.get('total_anomalies', 0)
                                    st.metric("Total Anomalies", total_anomalies)
                                
                                with col2:
                                    severity = summary.get('overall_severity', 'unknown')
                                    st.metric("Severity Level", severity.title())
                                
                                with col3:
                                    anomaly_types = summary.get('anomaly_types', [])
                                    st.metric("Anomaly Types", len(anomaly_types))
                                
                                # Detailed anomaly analysis
                                for anomaly_type, anomaly_data in anomalies.items():
                                    if anomaly_type != 'summary' and isinstance(anomaly_data, dict):
                                        count = anomaly_data.get('count', 0)
                                        if count > 0:
                                            with st.expander(f"{anomaly_type.replace('_', ' ').title()} Anomalies ({count})"):
                                                st.write(f"**Percentage:** {anomaly_data.get('percentage', 0):.1f}%")
                                                st.write(f"**Severity:** {anomaly_data.get('severity', 'unknown').title()}")
                                                
                                                # Show analysis if available
                                                analysis = anomaly_data.get('analysis', {})
                                                if analysis:
                                                    st.write("**Analysis:**")
                                                    for key, value in analysis.items():
                                                        if isinstance(value, dict):
                                                            st.write(f"- {key}: {value}")
                                                        else:
                                                            st.write(f"- {key}: {value}")
                                
                                # Show recommendations
                                recommendations = summary.get('recommendations', [])
                                if recommendations:
                                    st.markdown("#### 💡 Anomaly Recommendations")
                                    for recommendation in recommendations:
                                        st.write(f"• {recommendation}")
                    else:
                        st.info("👈 Enable **Anomaly Detection** in the sidebar to see insights here.")
                else:
                    st.info("🔮 Anomaly detection is not available. To enable it, install the required dependencies:")
                    st.code("pip install scikit-learn scipy")
                
                # Separator between sections
                st.markdown("---")
                
                # RAG Insights Section
                if RAG_INSIGHTS_AVAILABLE:
                    # Check if data has required columns for RAG
                    is_twitter_data = any(col in df.columns for col in ['tweet_id', 'author_id', 'conversation_id'])
                    
                    if is_twitter_data and 'conversation_id' in df.columns and 'text' in df.columns:
                        # Render RAG insights UI
                        render_rag_insights_ui(
                            df=df, 
                            enable_rag=st.session_state.get('enable_rag_insights', False)
                        )
                    else:
                        st.markdown("### 🤖 AI-Powered Insights Explanation (RAG)")
                        st.warning("⚠️ RAG insights require Twitter data format with 'conversation_id' and 'text' columns.")
                        st.info("""
                        **Required columns:**
                        - `conversation_id`: Groups related tweets/messages
                        - `text`: Message content
                        - `created_at`: Timestamp (optional but recommended)
                        - `author_id`: Author identifier (optional)
                        
                        💡 **Tip:** Use the Twitter data format (tweets_100.csv) or include these columns in your CSV.
                        """)
                else:
                    st.markdown("### 🤖 AI-Powered Insights Explanation (RAG)")
                    st.info("🤖 RAG insights are not available. To enable this feature, install the required dependencies:")
                    st.code("pip install langchain langchain-openai langchain-community chromadb openai tiktoken")
                    
                    st.markdown("""
                    **What is RAG?**
                    
                    Retrieval Augmented Generation (RAG) allows you to ask natural language questions about your support data.
                    The system will:
                    - Analyze relevant conversations using semantic search
                    - Generate AI-powered explanations using GPT-4-mini
                    - Show supporting evidence from actual conversations
                    
                    **Example questions:**
                    - "Why was sentiment negative on Oct 31?"
                    - "What caused a spike in complaints?"
                    - "What are customers frustrated about?"
                    """)
            
            with tab6:
                st.markdown("## 📊 Reports")
                st.markdown("Generate a comprehensive PDF report with your selected data and metrics.")
                
                if st.session_state.get('enable_reporting', False):
                    # Check if ReportLab is available
                    try:
                        from reportlab.lib.pagesizes import letter, A4
                        reportlab_available = True
                    except ImportError:
                        reportlab_available = False
                        st.error("📊 ReportLab is not installed. Please install it to generate PDF reports:")
                        st.code("pip install reportlab")
                    
                    if reportlab_available:
                        st.markdown("### 🎯 Report Configuration")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Team filter (multi-select)
                            if 'team' in df.columns:
                                available_teams = sorted(df['team'].dropna().unique().tolist())
                                selected_teams = st.multiselect(
                                    "Select Teams",
                                    options=available_teams,
                                    default=available_teams,
                                    help="Choose which teams to include in the report"
                                )
                            else:
                                selected_teams = None
                                st.info("ℹ️ No team data available in this dataset")
                        
                        with col2:
                            # Date range info
                            if 'created_at' in df.columns:
                                date_range = f"{df['created_at'].min().strftime('%Y-%m-%d')} to {df['created_at'].max().strftime('%Y-%m-%d')}"
                                st.info(f"📅 Data Range: {date_range}")
                        
                        st.markdown("### 📋 Select Report Sections")
                        
                        # Section selectors
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            include_overview = st.checkbox("📊 Overview & Summary", value=True, help="Key metrics and data summary")
                            include_response_times = st.checkbox("⏱️ Response Time Analysis", value=True, help="Response time statistics and trends")
                        
                        with col2:
                            include_sentiment = st.checkbox("😊 Sentiment Analysis", value='combined_score' in df.columns, help="Customer sentiment analysis")
                            include_teams = st.checkbox("👥 Team Performance", value='team' in df.columns, help="Team-by-team performance breakdown")
                        
                        with col3:
                            include_trends = st.checkbox("📈 Trends & Patterns", value='created_at' in df.columns, help="Time-based trends and patterns")
                            include_recommendations = st.checkbox("💡 Recommendations", value=True, help="Actionable insights and recommendations")
                        
                        st.markdown("---")
                        
                        # Generate button
                        if st.button("📄 Generate PDF Report", type="primary", use_container_width=True):
                            # Filter data by selected teams
                            filtered_df = df.copy()
                            if selected_teams and 'team' in df.columns:
                                filtered_df = filtered_df[filtered_df['team'].isin(selected_teams)]
                            
                            if len(filtered_df) == 0:
                                st.error("❌ No data found for selected teams")
                            else:
                                # Run sentiment analysis if needed and sentiment section is selected
                                if include_sentiment and 'customer_message' in filtered_df.columns:
                                    # Check if sentiment columns already exist
                                    has_sentiment = any(col in filtered_df.columns for col in ['combined_score', 'vader_compound', 'textblob_polarity'])
                                    
                                    if not has_sentiment:
                                        # Run sentiment analysis
                                        with st.spinner("🔄 Analyzing sentiment... (this may take a moment)"):
                                            data_processor = DataProcessor()
                                            filtered_df = data_processor.analyze_sentiment(filtered_df)
                                
                                with st.spinner("📄 Generating PDF report..."):
                                    try:
                                        
                                        # Generate PDF
                                        pdf_bytes = generate_pdf_report(
                                            filtered_df,
                                            include_overview=include_overview,
                                            include_response_times=include_response_times,
                                            include_sentiment=include_sentiment,
                                            include_teams=include_teams,
                                            include_trends=include_trends,
                                            include_recommendations=include_recommendations,
                                            selected_teams=selected_teams
                                        )
                                        
                                        st.success("✅ Report generated successfully!")
                                        
                                        # Download button
                                        st.download_button(
                                            label="📥 Download PDF Report",
                                            data=pdf_bytes,
                                            file_name=f"support_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                            mime="application/pdf",
                                            use_container_width=True
                                        )
                                    except Exception as e:
                                        st.error(f"❌ Error generating report: {str(e)}")
                                        st.exception(e)
                else:
                    st.info("📊 Enable **Advanced Reporting** in the sidebar to generate comprehensive reports.")
            
        except Exception as e:
            st.error(f"Error processing data: {str(e)}")
            st.exception(e)

if __name__ == "__main__":
    main()
