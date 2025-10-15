"""
Simple test for Enhanced Team Performance Scoring System
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_simple_test_data():
    """Create simple test data for team performance."""
    
    # Create sample data for 3 teams with different performance levels
    data = []
    
    # Team A - Top performer
    for i in range(50):
        data.append({
            'ticket_id': f'TA{i:03d}',
            'created_at': datetime.now() - timedelta(days=np.random.randint(1, 30)),
            'responded_at': datetime.now() - timedelta(days=np.random.randint(1, 30), minutes=np.random.randint(10, 30)),
            'team': 'Team A',
            'customer_message': f'Customer message {i}',
            'response_time_minutes': np.random.randint(15, 35),
            'combined_score': np.random.uniform(0.1, 0.4)
        })
    
    # Team B - Average performer
    for i in range(50):
        data.append({
            'ticket_id': f'TB{i:03d}',
            'created_at': datetime.now() - timedelta(days=np.random.randint(1, 30)),
            'responded_at': datetime.now() - timedelta(days=np.random.randint(1, 30), minutes=np.random.randint(30, 60)),
            'team': 'Team B',
            'customer_message': f'Customer message {i}',
            'response_time_minutes': np.random.randint(35, 65),
            'combined_score': np.random.uniform(-0.1, 0.2)
        })
    
    # Team C - Poor performer
    for i in range(50):
        data.append({
            'ticket_id': f'TC{i:03d}',
            'created_at': datetime.now() - timedelta(days=np.random.randint(1, 30)),
            'responded_at': datetime.now() - timedelta(days=np.random.randint(1, 30), minutes=np.random.randint(60, 120)),
            'team': 'Team C',
            'customer_message': f'Customer message {i}',
            'response_time_minutes': np.random.randint(65, 120),
            'combined_score': np.random.uniform(-0.3, 0.0)
        })
    
    return pd.DataFrame(data)

def test_enhanced_system():
    """Test the enhanced team performance system."""
    
    print("🚀 Testing Enhanced Team Performance System")
    print("=" * 50)
    
    # Create test data
    df = create_simple_test_data()
    print(f"✅ Created test data: {len(df)} tickets across {df['team'].nunique()} teams")
    
    # Test enhanced analyzer
    try:
        import sys
        import os
        sys.path.append('src')
        
        from enhanced_team_analyzer import EnhancedTeamAnalyzer
        
        analyzer = EnhancedTeamAnalyzer()
        team_analysis = analyzer.calculate_dynamic_team_scores(df)
        
        if 'error' in team_analysis:
            print(f"❌ Error: {team_analysis['error']}")
            return
        
        print("\n📊 TEAM PERFORMANCE RESULTS")
        print("=" * 40)
        
        for team_name, team_data in team_analysis.items():
            relative_score = team_data.get('relative_score', 0)
            performance_level = team_data.get('performance_level', 'average')
            traffic_light = team_data.get('traffic_light', {})
            percentile_ranking = team_data.get('percentile_ranking', 0)
            
            print(f"\n{traffic_light.get('color', '⚪')} {team_name}")
            print(f"   Score: {relative_score:.1f}")
            print(f"   Level: {traffic_light.get('label', 'Average')}")
            print(f"   Ranking: Top {100-percentile_ranking:.0f}%")
        
        print(f"\n✅ Enhanced Team Performance System Test Successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_system()
