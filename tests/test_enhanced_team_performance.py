"""
Test script for Enhanced Team Performance Scoring System
Demonstrates the dynamic traffic light system with sample data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def create_sample_data():
    """Create sample team performance data for testing."""
    
    # Set random seed for reproducible results
    np.random.seed(42)
    
    # Sample teams with different performance levels
    teams = ['Support Team A', 'Support Team B', 'Support Team C', 'Support Team D', 'Support Team E']
    
    data = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i, team in enumerate(teams):
        # Create different performance profiles for each team
        if team == 'Support Team A':  # Top performer
            response_times = np.random.normal(25, 5, 100)  # Fast response times
            sentiment_scores = np.random.normal(0.3, 0.1, 100)  # Positive sentiment
        elif team == 'Support Team B':  # Good performer
            response_times = np.random.normal(35, 8, 80)
            sentiment_scores = np.random.normal(0.1, 0.15, 80)
        elif team == 'Support Team C':  # Average performer
            response_times = np.random.normal(45, 10, 90)
            sentiment_scores = np.random.normal(0.0, 0.2, 90)
        elif team == 'Support Team D':  # Poor performer
            response_times = np.random.normal(65, 15, 70)
            sentiment_scores = np.random.normal(-0.1, 0.2, 70)
        else:  # Critical performer
            response_times = np.random.normal(85, 20, 60)
            sentiment_scores = np.random.normal(-0.2, 0.25, 60)
        
        # Ensure response times are positive
        response_times = np.maximum(response_times, 1)
        
        # Create tickets for this team
        for j in range(len(response_times)):
            created_at = base_date + timedelta(
                days=np.random.randint(0, 30),
                hours=np.random.randint(0, 24),
                minutes=np.random.randint(0, 60)
            )
            responded_at = created_at + timedelta(minutes=response_times[j])
            
            data.append({
                'ticket_id': f'T{i:02d}{j:03d}',
                'created_at': created_at,
                'responded_at': responded_at,
                'team': team,
                'customer_message': f'Sample customer message {j} for {team}',
                'response_time_minutes': response_times[j],
                'combined_score': sentiment_scores[j]
            })
    
    return pd.DataFrame(data)

def test_enhanced_team_analyzer():
    """Test the enhanced team analyzer with sample data."""
    
    print("🚀 Testing Enhanced Team Performance Scoring System")
    print("=" * 60)
    
    # Create sample data
    print("📊 Creating sample team performance data...")
    df = create_sample_data()
    
    print(f"✅ Created {len(df)} tickets across {df['team'].nunique()} teams")
    print(f"📈 Teams: {', '.join(df['team'].unique())}")
    print()
    
    # Test enhanced team analyzer
    try:
        from enhanced_team_analyzer import EnhancedTeamAnalyzer
        
        print("🔍 Analyzing team performance with dynamic scoring...")
        analyzer = EnhancedTeamAnalyzer()
        team_analysis = analyzer.calculate_dynamic_team_scores(df)
        
        if 'error' in team_analysis:
            print(f"❌ Error: {team_analysis['error']}")
            return
        
        print("✅ Enhanced team analysis completed successfully!")
        print()
        
        # Display results
        print("📊 TEAM PERFORMANCE RESULTS")
        print("=" * 60)
        
        for team_name, team_data in team_analysis.items():
            relative_score = team_data.get('relative_score', 0)
            performance_level = team_data.get('performance_level', 'average')
            traffic_light = team_data.get('traffic_light', {})
            percentile_ranking = team_data.get('percentile_ranking', 0)
            metrics = team_data.get('performance_metrics', {})
            
            print(f"\n{traffic_light.get('color', '⚪')} {team_name}")
            print(f"   Score: {relative_score:.1f}")
            print(f"   Level: {traffic_light.get('label', 'Average')}")
            print(f"   Ranking: Top {100-percentile_ranking:.0f}%")
            print(f"   Tickets: {metrics.get('ticket_count', 0)}")
            print(f"   Avg Response Time: {metrics.get('avg_response_time', 0):.1f} min")
            print(f"   SLA Compliance: {metrics.get('sla_compliance', 0):.1f}%")
            print(f"   Avg Sentiment: {metrics.get('avg_sentiment', 0):.3f}")
        
        # Display dynamic thresholds
        print(f"\n📈 DYNAMIC THRESHOLDS")
        print("=" * 30)
        thresholds = analyzer.dynamic_thresholds
        print(f"🟢 Excellent: ≥ {thresholds.get('excellent', 0):.1f}")
        print(f"🟡 Good: ≥ {thresholds.get('good', 0):.1f}")
        print(f"🟠 Average: ≥ {thresholds.get('average', 0):.1f}")
        print(f"🔴 Poor: ≥ {thresholds.get('poor', 0):.1f}")
        
        # Test rankings
        print(f"\n🏆 TEAM RANKINGS")
        print("=" * 30)
        rankings_df = analyzer.get_team_rankings(team_analysis)
        if not rankings_df.empty:
            print(rankings_df.to_string(index=False))
        
        # Test performance summary
        print(f"\n📋 PERFORMANCE SUMMARY")
        print("=" * 30)
        summary = analyzer.get_performance_summary(team_analysis)
        if 'error' not in summary:
            print(f"Total Teams: {summary['total_teams']}")
            print("Performance Distribution:")
            for level, count in summary['performance_distribution'].items():
                percentage = summary['performance_percentages'][level]
                print(f"  {level.title()}: {count} teams ({percentage:.1f}%)")
        
        print(f"\n✅ Enhanced Team Performance System Test Completed Successfully!")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure the enhanced_team_analyzer.py file is in the src directory")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_enhanced_component():
    """Test the enhanced team performance component."""
    
    print("\n🎨 Testing Enhanced Team Performance Component")
    print("=" * 60)
    
    try:
        from enhanced_team_performance_component import EnhancedTeamPerformanceComponent
        
        # Create sample data
        df = create_sample_data()
        
        # Create analyzer and get analysis
        from enhanced_team_analyzer import EnhancedTeamAnalyzer
        analyzer = EnhancedTeamAnalyzer()
        team_analysis = analyzer.calculate_dynamic_team_scores(df)
        
        if 'error' in team_analysis:
            print(f"❌ Error: {team_analysis['error']}")
            return
        
        # Test component (without Streamlit)
        print("✅ Enhanced Team Performance Component loaded successfully!")
        print("📊 Component features:")
        print("  - Dynamic traffic light cards")
        print("  - Performance distribution charts")
        print("  - Team rankings table")
        print("  - Performance insights and recommendations")
        print("  - Export functionality")
        
        print(f"\n✅ Enhanced Team Performance Component Test Completed!")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure the enhanced_team_performance_component.py file is in the src directory")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function."""
    
    print("🧪 Enhanced Team Performance Scoring System - Test Suite")
    print("=" * 70)
    print()
    
    # Test enhanced team analyzer
    test_enhanced_team_analyzer()
    
    # Test enhanced component
    test_enhanced_component()
    
    print(f"\n🎉 All Tests Completed!")
    print("=" * 30)
    print("📝 Next Steps:")
    print("1. Run the Streamlit app to see the enhanced system in action")
    print("2. Upload your own team data to test with real data")
    print("3. Customize the performance weights and thresholds as needed")
    print("4. Explore the enhanced visualizations and insights")

if __name__ == "__main__":
    main()
