"""
Custom Recommendations Module
This file contains custom recommendations that can be added to the Team Insights & Recommendations section.
"""

# Custom recommendations dictionary
CUSTOM_RECOMMENDATIONS = {
    "response_time": [
        "Consider implementing automated responses for common queries to reduce response times",
        "Set up priority queues to handle urgent tickets faster",
        "Implement SLA monitoring alerts to catch delays early",
        "Train agents on time management techniques for faster ticket resolution",
        "Use templates for common responses to speed up replies"
    ],
    
    "sentiment": [
        "Implement proactive outreach for customers showing negative sentiment",
        "Create escalation procedures for highly negative sentiment cases",
        "Develop empathy training programs for support agents",
        "Set up sentiment monitoring dashboards for real-time awareness",
        "Create customer satisfaction follow-up processes"
    ],
    
    "team_performance": [
        "Implement peer mentoring programs between high and low performers",
        "Create knowledge sharing sessions for best practices",
        "Set up regular team performance reviews and feedback sessions",
        "Implement gamification elements to boost team engagement",
        "Create cross-training programs to improve team flexibility"
    ],
    
    "general": [
        "Implement customer feedback collection at the end of each interaction",
        "Create knowledge base articles for common issues",
        "Set up regular team meetings to discuss challenges and solutions",
        "Implement quality assurance processes for ticket handling",
        "Create customer journey mapping to identify pain points"
    ]
}

# Function to get recommendations based on analysis results
def get_custom_recommendations(analysis_type="general", performance_level="average"):
    """
    Get custom recommendations based on analysis type and performance level.
    
    Args:
        analysis_type (str): Type of analysis (response_time, sentiment, team_performance, general)
        performance_level (str): Performance level (excellent, good, average, poor)
    
    Returns:
        list: List of relevant recommendations
    """
    recommendations = CUSTOM_RECOMMENDATIONS.get(analysis_type, CUSTOM_RECOMMENDATIONS["general"])
    
    # Add performance-specific recommendations
    if performance_level == "poor":
        recommendations.extend([
            f"🚨 Immediate action required for {analysis_type} performance",
            f"Consider additional training and support for {analysis_type} improvement",
            f"Implement daily monitoring and feedback for {analysis_type} metrics"
        ])
    elif performance_level == "excellent":
        recommendations.extend([
            f"🌟 Maintain current excellent {analysis_type} performance",
            f"Share best practices from {analysis_type} success with other teams",
            f"Consider advanced optimization strategies for {analysis_type}"
        ])
    
    return recommendations

# Function to add new recommendations
def add_custom_recommendation(analysis_type, recommendation):
    """
    Add a new custom recommendation to the recommendations dictionary.
    
    Args:
        analysis_type (str): Type of analysis
        recommendation (str): New recommendation to add
    """
    if analysis_type not in CUSTOM_RECOMMENDATIONS:
        CUSTOM_RECOMMENDATIONS[analysis_type] = []
    
    CUSTOM_RECOMMENDATIONS[analysis_type].append(recommendation)

# Function to get all recommendations
def get_all_recommendations():
    """
    Get all custom recommendations organized by type.
    
    Returns:
        dict: All recommendations organized by analysis type
    """
    return CUSTOM_RECOMMENDATIONS
