"""
Forecasting module for customer support analytics.
Handles predictive analytics for response times, sentiment trends, and capacity planning.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import forecasting libraries
try:
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    import statsmodels.api as sm
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    FORECASTING_AVAILABLE = True
except ImportError:
    FORECASTING_AVAILABLE = False
    logging.warning("Forecasting libraries not available. Install scikit-learn and statsmodels.")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ForecastingEngine:
    """Handles predictive analytics and forecasting for customer support metrics."""
    
    def __init__(self):
        """Initialize the forecasting engine."""
        self.models = {}
        self.scalers = {}
        self.forecast_horizon = 30  # days
        self.confidence_level = 0.95
        
        if not FORECASTING_AVAILABLE:
            logger.warning("Forecasting capabilities limited due to missing dependencies")
        
        logger.info("Forecasting engine initialized")
    
    def predict_response_times(self, historical_data: pd.DataFrame) -> Dict:
        """
        Predict future response times using time series analysis.
        
        Args:
            historical_data: DataFrame with historical response time data
            
        Returns:
            Dict: Prediction results with confidence intervals
        """
        try:
            if not FORECASTING_AVAILABLE:
                return self._simple_trend_prediction(historical_data)
            
            # Prepare time series data
            df_ts = self._prepare_time_series_data(historical_data, 'response_time_minutes')
            
            if df_ts.empty or len(df_ts) < 10:
                return self._simple_trend_prediction(historical_data)
            
            # Try multiple forecasting methods
            predictions = {}
            
            # Method 1: Linear trend
            linear_pred = self._linear_trend_forecast(df_ts)
            predictions['linear_trend'] = linear_pred
            
            # Method 2: Exponential smoothing
            exp_pred = self._exponential_smoothing_forecast(df_ts)
            predictions['exponential_smoothing'] = exp_pred
            
            # Method 3: Seasonal decomposition
            seasonal_pred = self._seasonal_decomposition_forecast(df_ts)
            predictions['seasonal'] = seasonal_pred
            
            # Combine predictions
            combined_pred = self._combine_predictions(predictions)
            
            return {
                'predictions': combined_pred,
                'method': 'combined',
                'confidence_interval': self._calculate_confidence_interval(combined_pred),
                'trend_direction': self._analyze_trend_direction(df_ts),
                'seasonality': self._detect_seasonality(df_ts),
                'accuracy_metrics': self._calculate_accuracy_metrics(df_ts, predictions)
            }
            
        except Exception as e:
            logger.error(f"Error in response time prediction: {e}")
            return self._simple_trend_prediction(historical_data)
    
    def forecast_sentiment_trends(self, sentiment_data: pd.DataFrame) -> Dict:
        """
        Forecast sentiment trends over time.
        
        Args:
            sentiment_data: DataFrame with sentiment analysis data
            
        Returns:
            Dict: Sentiment trend predictions
        """
        try:
            if not FORECASTING_AVAILABLE:
                return self._simple_sentiment_trend(sentiment_data)
            
            # Prepare sentiment time series
            df_sentiment = self._prepare_sentiment_time_series(sentiment_data)
            
            if df_sentiment.empty or len(df_sentiment) < 7:
                return self._simple_sentiment_trend(sentiment_data)
            
            # Predict sentiment trends by category
            predictions = {}
            
            for sentiment in ['positive', 'negative', 'neutral']:
                if sentiment in df_sentiment.columns:
                    sentiment_ts = df_sentiment[sentiment].dropna()
                    if len(sentiment_ts) >= 7:
                        pred = self._exponential_smoothing_forecast(sentiment_ts)
                        predictions[sentiment] = pred
            
            # Overall sentiment score prediction
            if 'sentiment_score' in df_sentiment.columns:
                score_ts = df_sentiment['sentiment_score'].dropna()
                if len(score_ts) >= 7:
                    score_pred = self._linear_trend_forecast(score_ts)
                    predictions['overall_score'] = score_pred
            
            return {
                'sentiment_predictions': predictions,
                'trend_analysis': self._analyze_sentiment_trends(df_sentiment),
                'recommendations': self._generate_sentiment_recommendations(predictions),
                'confidence_level': self.confidence_level
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment trend forecasting: {e}")
            return self._simple_sentiment_trend(sentiment_data)
    
    def predict_team_performance(self, team_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Predict team performance based on historical data.
        
        Args:
            team_data: Dictionary with team names as keys and DataFrames as values
            
        Returns:
            Dict: Team performance predictions
        """
        try:
            predictions = {}
            
            for team_name, team_df in team_data.items():
                if team_df.empty or len(team_df) < 5:
                    continue
                
                # Calculate historical performance metrics
                historical_metrics = self._calculate_team_metrics_history(team_df)
                
                # Predict future performance
                team_prediction = self._predict_team_metrics(historical_metrics)
                
                predictions[team_name] = {
                    'predicted_performance': team_prediction,
                    'trend_direction': self._analyze_team_trend(historical_metrics),
                    'risk_factors': self._identify_risk_factors(historical_metrics),
                    'improvement_potential': self._assess_improvement_potential(historical_metrics)
                }
            
            return {
                'team_predictions': predictions,
                'overall_insights': self._generate_team_insights(predictions),
                'recommendations': self._generate_team_recommendations(predictions)
            }
            
        except Exception as e:
            logger.error(f"Error in team performance prediction: {e}")
            return {'error': str(e)}
    
    def capacity_planning(self, workload_data: pd.DataFrame) -> Dict:
        """
        Perform capacity planning analysis.
        
        Args:
            workload_data: DataFrame with workload and capacity data
            
        Returns:
            Dict: Capacity planning recommendations
        """
        try:
            # Analyze current capacity utilization
            capacity_analysis = self._analyze_capacity_utilization(workload_data)
            
            # Predict future workload
            workload_prediction = self._predict_future_workload(workload_data)
            
            # Calculate capacity requirements
            capacity_requirements = self._calculate_capacity_requirements(
                capacity_analysis, workload_prediction
            )
            
            return {
                'current_capacity': capacity_analysis,
                'workload_prediction': workload_prediction,
                'capacity_requirements': capacity_requirements,
                'recommendations': self._generate_capacity_recommendations(
                    capacity_analysis, capacity_requirements
                ),
                'risk_assessment': self._assess_capacity_risks(capacity_requirements)
            }
            
        except Exception as e:
            logger.error(f"Error in capacity planning: {e}")
            return {'error': str(e)}
    
    def _prepare_time_series_data(self, df: pd.DataFrame, metric_column: str) -> pd.Series:
        """Prepare time series data for forecasting."""
        try:
            # Ensure we have datetime index
            if 'created_at' in df.columns:
                df['date'] = pd.to_datetime(df['created_at']).dt.date
                ts_data = df.groupby('date')[metric_column].mean()
            else:
                # Create synthetic time series if no date column
                ts_data = pd.Series(df[metric_column].values)
            
            return ts_data.dropna()
        except Exception as e:
            logger.error(f"Error preparing time series data: {e}")
            return pd.Series()
    
    def _prepare_sentiment_time_series(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare sentiment data for time series analysis."""
        try:
            if 'created_at' not in df.columns:
                return pd.DataFrame()
            
            df['date'] = pd.to_datetime(df['created_at']).dt.date
            
            # Group by date and calculate sentiment metrics
            sentiment_ts = df.groupby('date').agg({
                'combined_score': 'mean',
                'category': lambda x: x.value_counts().to_dict()
            }).reset_index()
            
            # Expand sentiment categories
            sentiment_expanded = pd.DataFrame()
            sentiment_expanded['date'] = sentiment_ts['date']
            sentiment_expanded['sentiment_score'] = sentiment_ts['combined_score']
            
            for sentiment in ['positive', 'negative', 'neutral']:
                sentiment_expanded[sentiment] = sentiment_ts['category'].apply(
                    lambda x: x.get(sentiment, 0) if isinstance(x, dict) else 0
                )
            
            return sentiment_expanded.set_index('date')
            
        except Exception as e:
            logger.error(f"Error preparing sentiment time series: {e}")
            return pd.DataFrame()
    
    def _linear_trend_forecast(self, ts_data: pd.Series) -> Dict:
        """Perform linear trend forecasting."""
        try:
            if len(ts_data) < 3:
                return {'forecast': [], 'trend': 'insufficient_data'}
            
            # Create time index
            X = np.arange(len(ts_data)).reshape(-1, 1)
            y = ts_data.values
            
            # Fit linear regression
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict future values
            future_X = np.arange(len(ts_data), len(ts_data) + self.forecast_horizon).reshape(-1, 1)
            forecast = model.predict(future_X)
            
            # Calculate trend direction
            trend_slope = model.coef_[0]
            trend_direction = 'increasing' if trend_slope > 0 else 'decreasing' if trend_slope < 0 else 'stable'
            
            return {
                'forecast': forecast.tolist(),
                'trend': trend_direction,
                'slope': trend_slope,
                'r_squared': model.score(X, y)
            }
            
        except Exception as e:
            logger.error(f"Error in linear trend forecast: {e}")
            return {'forecast': [], 'trend': 'error'}
    
    def _exponential_smoothing_forecast(self, ts_data: pd.Series) -> Dict:
        """Perform exponential smoothing forecasting."""
        try:
            if len(ts_data) < 3:
                return {'forecast': [], 'trend': 'insufficient_data'}
            
            # Simple exponential smoothing
            alpha = 0.3  # Smoothing parameter
            forecast_values = []
            
            # Calculate initial forecast
            forecast = ts_data.iloc[0]
            
            # Generate forecasts
            for i in range(self.forecast_horizon):
                forecast = alpha * ts_data.iloc[-1] + (1 - alpha) * forecast
                forecast_values.append(forecast)
            
            return {
                'forecast': forecast_values,
                'trend': 'exponential_smoothing',
                'alpha': alpha
            }
            
        except Exception as e:
            logger.error(f"Error in exponential smoothing forecast: {e}")
            return {'forecast': [], 'trend': 'error'}
    
    def _seasonal_decomposition_forecast(self, ts_data: pd.Series) -> Dict:
        """Perform seasonal decomposition forecasting."""
        try:
            if len(ts_data) < 12:  # Need at least 12 data points for seasonal analysis
                return {'forecast': [], 'trend': 'insufficient_data'}
            
            # Simple seasonal pattern detection
            if len(ts_data) >= 7:  # Weekly pattern
                weekly_pattern = ts_data.groupby(ts_data.index.dayofweek).mean()
                forecast_values = []
                
                for i in range(self.forecast_horizon):
                    day_of_week = (len(ts_data) + i) % 7
                    forecast_values.append(weekly_pattern.iloc[day_of_week])
                
                return {
                    'forecast': forecast_values,
                    'trend': 'seasonal',
                    'pattern': 'weekly'
                }
            
            return {'forecast': [], 'trend': 'no_seasonality'}
            
        except Exception as e:
            logger.error(f"Error in seasonal decomposition forecast: {e}")
            return {'forecast': [], 'trend': 'error'}
    
    def _combine_predictions(self, predictions: Dict) -> List[float]:
        """Combine multiple prediction methods."""
        try:
            all_forecasts = []
            weights = {'linear_trend': 0.4, 'exponential_smoothing': 0.4, 'seasonal': 0.2}
            
            for method, pred_data in predictions.items():
                if 'forecast' in pred_data and pred_data['forecast']:
                    all_forecasts.append(pred_data['forecast'])
            
            if not all_forecasts:
                return []
            
            # Weighted average of forecasts
            combined_forecast = []
            for i in range(self.forecast_horizon):
                weighted_sum = 0
                total_weight = 0
                
                for j, forecast in enumerate(all_forecasts):
                    if i < len(forecast):
                        weight = list(weights.values())[j] if j < len(weights) else 1.0
                        weighted_sum += forecast[i] * weight
                        total_weight += weight
                
                if total_weight > 0:
                    combined_forecast.append(weighted_sum / total_weight)
                else:
                    combined_forecast.append(0)
            
            return combined_forecast
            
        except Exception as e:
            logger.error(f"Error combining predictions: {e}")
            return []
    
    def _simple_trend_prediction(self, df: pd.DataFrame) -> Dict:
        """Simple trend prediction when advanced methods are not available."""
        try:
            if 'response_time_minutes' not in df.columns:
                return {'error': 'No response time data available'}
            
            # Calculate simple trend
            response_times = df['response_time_minutes'].dropna()
            if len(response_times) < 2:
                return {'error': 'Insufficient data for prediction'}
            
            # Simple moving average trend
            recent_avg = response_times.tail(7).mean() if len(response_times) >= 7 else response_times.mean()
            overall_avg = response_times.mean()
            
            trend_direction = 'improving' if recent_avg < overall_avg else 'declining'
            
            # Simple forecast (assume trend continues)
            trend_factor = recent_avg / overall_avg if overall_avg > 0 else 1.0
            forecast_values = [recent_avg * (trend_factor ** i) for i in range(1, self.forecast_horizon + 1)]
            
            # Generate recommendations
            recommendations = []
            if trend_direction == 'improving':
                recommendations.append(f"Response times are improving (current avg: {recent_avg:.1f} min)")
                recommendations.append("Continue current practices to maintain improvement")
            else:
                recommendations.append(f"Response times are declining (current avg: {recent_avg:.1f} min)")
                recommendations.append("Consider reviewing team workload and processes")
            
            return {
                'predictions': forecast_values,  # Return as list, not nested dict
                'method': 'simple_trend',
                'confidence_interval': {
                    'lower': [f * 0.8 for f in forecast_values],
                    'upper': [f * 1.2 for f in forecast_values]
                },
                'trend_direction': trend_direction,
                'seasonality': {'has_seasonality': False, 'pattern': 'none'},
                'accuracy_metrics': {'method': 'simple_trend', 'confidence': 'low'},
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error in simple trend prediction: {e}")
            return {'error': str(e)}
    
    def _simple_sentiment_trend(self, df: pd.DataFrame) -> Dict:
        """Simple sentiment trend analysis when advanced methods are not available."""
        try:
            if 'combined_score' not in df.columns:
                return {'error': 'No sentiment data available'}
            
            sentiment_scores = df['combined_score'].dropna()
            if len(sentiment_scores) < 2:
                return {'error': 'Insufficient sentiment data'}
            
            # Calculate trend
            recent_sentiment = sentiment_scores.tail(7).mean() if len(sentiment_scores) >= 7 else sentiment_scores.mean()
            overall_sentiment = sentiment_scores.mean()
            
            trend_direction = 'improving' if recent_sentiment > overall_sentiment else 'declining'
            
            return {
                'sentiment_predictions': {
                    'overall_score': [recent_sentiment] * self.forecast_horizon,
                    'trend': trend_direction
                },
                'trend_analysis': {
                    'current_sentiment': recent_sentiment,
                    'trend_direction': trend_direction,
                    'volatility': sentiment_scores.std()
                },
                'recommendations': [
                    f"Sentiment trend is {trend_direction}",
                    f"Current sentiment score: {recent_sentiment:.3f}",
                    "Monitor customer feedback closely"
                ],
                'confidence_level': 0.7
            }
            
        except Exception as e:
            logger.error(f"Error in simple sentiment trend: {e}")
            return {'error': str(e)}
    
    def _calculate_confidence_interval(self, forecast: List[float]) -> Dict:
        """Calculate confidence intervals for forecasts."""
        try:
            if not forecast:
                return {'lower': [], 'upper': []}
            
            # Simple confidence interval calculation
            std_dev = np.std(forecast) if len(forecast) > 1 else forecast[0] * 0.1
            confidence_factor = 1.96  # 95% confidence
            
            lower_bound = [f - confidence_factor * std_dev for f in forecast]
            upper_bound = [f + confidence_factor * std_dev for f in forecast]
            
            return {
                'lower': lower_bound,
                'upper': upper_bound,
                'confidence_level': self.confidence_level
            }
            
        except Exception as e:
            logger.error(f"Error calculating confidence interval: {e}")
            return {'lower': [], 'upper': []}
    
    def _analyze_trend_direction(self, ts_data: pd.Series) -> str:
        """Analyze the direction of the trend."""
        try:
            if len(ts_data) < 2:
                return 'insufficient_data'
            
            # Calculate trend using linear regression
            X = np.arange(len(ts_data)).reshape(-1, 1)
            y = ts_data.values
            
            model = LinearRegression()
            model.fit(X, y)
            
            slope = model.coef_[0]
            
            if slope > 0.01:
                return 'increasing'
            elif slope < -0.01:
                return 'decreasing'
            else:
                return 'stable'
                
        except Exception as e:
            logger.error(f"Error analyzing trend direction: {e}")
            return 'unknown'
    
    def _detect_seasonality(self, ts_data: pd.Series) -> Dict:
        """Detect seasonal patterns in the data."""
        try:
            if len(ts_data) < 7:
                return {'has_seasonality': False, 'pattern': 'none'}
            
            # Check for weekly patterns
            if len(ts_data) >= 7:
                weekly_variance = ts_data.groupby(ts_data.index.dayofweek).var().mean()
                overall_variance = ts_data.var()
                
                if weekly_variance > overall_variance * 0.1:
                    return {'has_seasonality': True, 'pattern': 'weekly'}
            
            return {'has_seasonality': False, 'pattern': 'none'}
            
        except Exception as e:
            logger.error(f"Error detecting seasonality: {e}")
            return {'has_seasonality': False, 'pattern': 'error'}
    
    def _calculate_accuracy_metrics(self, ts_data: pd.Series, predictions: Dict) -> Dict:
        """Calculate accuracy metrics for predictions."""
        try:
            if len(ts_data) < 5:
                return {'method': 'insufficient_data', 'confidence': 'low'}
            
            # Use last few points for validation
            validation_size = min(3, len(ts_data) // 3)
            actual = ts_data.tail(validation_size).values
            
            # Calculate metrics for each method
            metrics = {}
            for method, pred_data in predictions.items():
                if 'forecast' in pred_data and len(pred_data['forecast']) >= validation_size:
                    predicted = pred_data['forecast'][:validation_size]
                    
                    mae = np.mean(np.abs(actual - predicted))
                    mse = np.mean((actual - predicted) ** 2)
                    
                    metrics[method] = {
                        'mae': mae,
                        'mse': mse,
                        'rmse': np.sqrt(mse)
                    }
            
            # Determine best method
            if metrics:
                best_method = min(metrics.keys(), key=lambda x: metrics[x]['mae'])
                return {
                    'best_method': best_method,
                    'metrics': metrics,
                    'confidence': 'medium' if metrics[best_method]['mae'] < ts_data.std() else 'low'
                }
            
            return {'method': 'no_validation', 'confidence': 'low'}
            
        except Exception as e:
            logger.error(f"Error calculating accuracy metrics: {e}")
            return {'method': 'error', 'confidence': 'low'}
    
    def _analyze_sentiment_trends(self, df_sentiment: pd.DataFrame) -> Dict:
        """Analyze sentiment trends in detail."""
        try:
            if df_sentiment.empty:
                return {'trend': 'no_data'}
            
            trends = {}
            
            for column in df_sentiment.columns:
                if column != 'date':
                    series = df_sentiment[column].dropna()
                    if len(series) >= 2:
                        trend = self._analyze_trend_direction(series)
                        trends[column] = {
                            'direction': trend,
                            'current_value': series.iloc[-1],
                            'average': series.mean(),
                            'volatility': series.std()
                        }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment trends: {e}")
            return {'trend': 'error'}
    
    def _generate_sentiment_recommendations(self, predictions: Dict) -> List[str]:
        """Generate recommendations based on sentiment predictions."""
        recommendations = []
        
        try:
            if 'overall_score' in predictions:
                score_pred = predictions['overall_score']
                if 'forecast' in score_pred:
                    future_scores = score_pred['forecast']
                    avg_future_score = np.mean(future_scores)
                    
                    if avg_future_score > 0.1:
                        recommendations.append("Positive sentiment trend predicted - maintain current service quality")
                    elif avg_future_score < -0.1:
                        recommendations.append("Negative sentiment trend predicted - implement customer satisfaction improvements")
                    else:
                        recommendations.append("Stable sentiment trend - monitor for changes")
            
            # Category-specific recommendations
            for sentiment, pred_data in predictions.items():
                if sentiment in ['positive', 'negative', 'neutral'] and 'forecast' in pred_data:
                    trend = pred_data.get('trend', 'stable')
                    if sentiment == 'negative' and trend == 'increasing':
                        recommendations.append("Negative sentiment increasing - review customer feedback processes")
                    elif sentiment == 'positive' and trend == 'decreasing':
                        recommendations.append("Positive sentiment decreasing - investigate service quality issues")
            
            return recommendations[:5]  # Limit to top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error generating sentiment recommendations: {e}")
            return ["Unable to generate recommendations due to data limitations"]
    
    def _calculate_team_metrics_history(self, team_df: pd.DataFrame) -> Dict:
        """Calculate historical team performance metrics."""
        try:
            metrics = {}
            
            if 'response_time_minutes' in team_df.columns:
                response_times = team_df['response_time_minutes'].dropna()
                metrics['response_time'] = {
                    'mean': response_times.mean(),
                    'median': response_times.median(),
                    'std': response_times.std(),
                    'trend': self._analyze_trend_direction(response_times)
                }
            
            if 'combined_score' in team_df.columns:
                sentiment_scores = team_df['combined_score'].dropna()
                metrics['sentiment'] = {
                    'mean': sentiment_scores.mean(),
                    'std': sentiment_scores.std(),
                    'trend': self._analyze_trend_direction(sentiment_scores)
                }
            
            # Volume metrics
            metrics['volume'] = {
                'total_tickets': len(team_df),
                'daily_average': len(team_df) / max(1, (team_df['created_at'].max() - team_df['created_at'].min()).days)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating team metrics history: {e}")
            return {}
    
    def _predict_team_metrics(self, historical_metrics: Dict) -> Dict:
        """Predict future team performance metrics."""
        try:
            predictions = {}
            
            for metric, data in historical_metrics.items():
                if isinstance(data, dict) and 'trend' in data:
                    trend = data['trend']
                    current_value = data.get('mean', 0)
                    
                    # Simple trend-based prediction
                    if trend == 'increasing':
                        predicted_value = current_value * 1.1
                    elif trend == 'decreasing':
                        predicted_value = current_value * 0.9
                    else:
                        predicted_value = current_value
                    
                    predictions[metric] = {
                        'predicted_value': predicted_value,
                        'trend': trend,
                        'confidence': 'medium'
                    }
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting team metrics: {e}")
            return {}
    
    def _analyze_team_trend(self, historical_metrics: Dict) -> str:
        """Analyze overall team trend."""
        try:
            trends = []
            for metric, data in historical_metrics.items():
                if isinstance(data, dict) and 'trend' in data:
                    trends.append(data['trend'])
            
            if not trends:
                return 'unknown'
            
            # Majority trend
            trend_counts = {}
            for trend in trends:
                trend_counts[trend] = trend_counts.get(trend, 0) + 1
            
            return max(trend_counts.keys(), key=trend_counts.get)
            
        except Exception as e:
            logger.error(f"Error analyzing team trend: {e}")
            return 'unknown'
    
    def _identify_risk_factors(self, historical_metrics: Dict) -> List[str]:
        """Identify risk factors for team performance."""
        try:
            risks = []
            
            for metric, data in historical_metrics.items():
                if isinstance(data, dict):
                    trend = data.get('trend', 'stable')
                    value = data.get('mean', 0)
                    
                    if metric == 'response_time' and trend == 'increasing' and value > 60:
                        risks.append("Response times increasing and exceeding SLA")
                    elif metric == 'sentiment' and trend == 'decreasing' and value < 0:
                        risks.append("Customer sentiment declining")
                    elif metric == 'volume' and data.get('daily_average', 0) > 50:
                        risks.append("High ticket volume may impact quality")
            
            return risks
            
        except Exception as e:
            logger.error(f"Error identifying risk factors: {e}")
            return []
    
    def _assess_improvement_potential(self, historical_metrics: Dict) -> str:
        """Assess team improvement potential."""
        try:
            improvement_score = 0
            
            for metric, data in historical_metrics.items():
                if isinstance(data, dict):
                    trend = data.get('trend', 'stable')
                    value = data.get('mean', 0)
                    
                    if metric == 'response_time' and trend == 'increasing':
                        improvement_score += 2
                    elif metric == 'sentiment' and trend == 'decreasing':
                        improvement_score += 2
                    elif metric == 'response_time' and value > 30:
                        improvement_score += 1
                    elif metric == 'sentiment' and value < 0.1:
                        improvement_score += 1
            
            if improvement_score >= 4:
                return 'high'
            elif improvement_score >= 2:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            logger.error(f"Error assessing improvement potential: {e}")
            return 'unknown'
    
    def _generate_team_insights(self, predictions: Dict) -> List[str]:
        """Generate overall team insights."""
        try:
            insights = []
            
            # Analyze overall trends
            improving_teams = []
            declining_teams = []
            
            for team, data in predictions.items():
                if isinstance(data, dict) and 'trend_direction' in data:
                    trend = data['trend_direction']
                    if trend == 'improving':
                        improving_teams.append(team)
                    elif trend == 'declining':
                        declining_teams.append(team)
            
            if improving_teams:
                insights.append(f"Teams showing improvement: {', '.join(improving_teams)}")
            if declining_teams:
                insights.append(f"Teams needing attention: {', '.join(declining_teams)}")
            
            # Risk analysis
            high_risk_teams = []
            for team, data in predictions.items():
                if isinstance(data, dict) and 'risk_factors' in data:
                    if len(data['risk_factors']) >= 2:
                        high_risk_teams.append(team)
            
            if high_risk_teams:
                insights.append(f"High-risk teams requiring immediate attention: {', '.join(high_risk_teams)}")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating team insights: {e}")
            return ["Unable to generate team insights"]
    
    def _generate_team_recommendations(self, predictions: Dict) -> List[str]:
        """Generate team-specific recommendations."""
        try:
            recommendations = []
            
            for team, data in predictions.items():
                if isinstance(data, dict):
                    risk_factors = data.get('risk_factors', [])
                    improvement_potential = data.get('improvement_potential', 'unknown')
                    
                    if risk_factors:
                        recommendations.append(f"{team}: Address {len(risk_factors)} identified risk factors")
                    
                    if improvement_potential == 'high':
                        recommendations.append(f"{team}: High improvement potential - prioritize training and process optimization")
            
            return recommendations[:10]  # Limit to top 10 recommendations
            
        except Exception as e:
            logger.error(f"Error generating team recommendations: {e}")
            return ["Unable to generate team recommendations"]
    
    def _analyze_capacity_utilization(self, workload_data: pd.DataFrame) -> Dict:
        """Analyze current capacity utilization."""
        try:
            if workload_data.empty:
                return {'utilization': 0, 'status': 'no_data'}
            
            # Calculate basic capacity metrics
            total_tickets = len(workload_data)
            
            if 'created_at' in workload_data.columns:
                date_range = (workload_data['created_at'].max() - workload_data['created_at'].min()).days
                daily_average = total_tickets / max(1, date_range)
            else:
                daily_average = total_tickets
            
            # Estimate capacity (assuming 8-hour workday, 1 ticket per hour per agent)
            estimated_capacity = daily_average * 8  # Simplified capacity calculation
            
            utilization = min(100, (daily_average / max(1, estimated_capacity)) * 100)
            
            if utilization > 90:
                status = 'overloaded'
            elif utilization > 70:
                status = 'high'
            elif utilization > 50:
                status = 'moderate'
            else:
                status = 'low'
            
            return {
                'utilization': utilization,
                'status': status,
                'daily_average': daily_average,
                'estimated_capacity': estimated_capacity
            }
            
        except Exception as e:
            logger.error(f"Error analyzing capacity utilization: {e}")
            return {'utilization': 0, 'status': 'error'}
    
    def _predict_future_workload(self, workload_data: pd.DataFrame) -> Dict:
        """Predict future workload."""
        try:
            if workload_data.empty or 'created_at' not in workload_data.columns:
                return {'predicted_workload': 0, 'trend': 'no_data'}
            
            # Calculate historical workload trend
            workload_data['date'] = pd.to_datetime(workload_data['created_at']).dt.date
            daily_workload = workload_data.groupby('date').size()
            
            if len(daily_workload) < 2:
                return {'predicted_workload': daily_workload.mean(), 'trend': 'stable'}
            
            # Simple trend analysis
            trend = self._analyze_trend_direction(daily_workload)
            current_workload = daily_workload.tail(7).mean() if len(daily_workload) >= 7 else daily_workload.mean()
            
            # Predict future workload
            if trend == 'increasing':
                predicted_workload = current_workload * 1.1
            elif trend == 'decreasing':
                predicted_workload = current_workload * 0.9
            else:
                predicted_workload = current_workload
            
            return {
                'predicted_workload': predicted_workload,
                'trend': trend,
                'current_workload': current_workload,
                'confidence': 'medium'
            }
            
        except Exception as e:
            logger.error(f"Error predicting future workload: {e}")
            return {'predicted_workload': 0, 'trend': 'error'}
    
    def _calculate_capacity_requirements(self, capacity_analysis: Dict, workload_prediction: Dict) -> Dict:
        """Calculate capacity requirements based on predictions."""
        try:
            current_utilization = capacity_analysis.get('utilization', 0)
            predicted_workload = workload_prediction.get('predicted_workload', 0)
            current_capacity = capacity_analysis.get('estimated_capacity', 1)
            
            # Calculate required capacity
            if predicted_workload > 0:
                required_capacity = predicted_workload * 8  # 8 hours per day
                capacity_gap = required_capacity - current_capacity
                
                if capacity_gap > 0:
                    status = 'insufficient'
                    recommendation = 'increase_capacity'
                elif capacity_gap < -current_capacity * 0.2:
                    status = 'excess'
                    recommendation = 'reduce_capacity'
                else:
                    status = 'adequate'
                    recommendation = 'maintain'
            else:
                status = 'unknown'
                recommendation = 'monitor'
                capacity_gap = 0
            
            return {
                'required_capacity': required_capacity,
                'current_capacity': current_capacity,
                'capacity_gap': capacity_gap,
                'status': status,
                'recommendation': recommendation
            }
            
        except Exception as e:
            logger.error(f"Error calculating capacity requirements: {e}")
            return {'status': 'error', 'recommendation': 'monitor'}
    
    def _generate_capacity_recommendations(self, capacity_analysis: Dict, capacity_requirements: Dict) -> List[str]:
        """Generate capacity planning recommendations."""
        try:
            recommendations = []
            
            utilization = capacity_analysis.get('utilization', 0)
            status = capacity_analysis.get('status', 'unknown')
            capacity_gap = capacity_requirements.get('capacity_gap', 0)
            
            if status == 'overloaded':
                recommendations.append("Immediate capacity increase required - consider hiring additional staff")
            elif status == 'high':
                recommendations.append("High utilization detected - plan for capacity expansion")
            elif status == 'low':
                recommendations.append("Low utilization - consider optimizing resource allocation")
            
            if capacity_gap > 0:
                recommendations.append(f"Capacity gap of {capacity_gap:.1f} hours/day - plan for expansion")
            elif capacity_gap < -10:
                recommendations.append("Excess capacity available - consider resource reallocation")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating capacity recommendations: {e}")
            return ["Unable to generate capacity recommendations"]
    
    def _assess_capacity_risks(self, capacity_requirements: Dict) -> List[str]:
        """Assess capacity-related risks."""
        try:
            risks = []
            
            status = capacity_requirements.get('status', 'unknown')
            capacity_gap = capacity_requirements.get('capacity_gap', 0)
            
            if status == 'insufficient':
                risks.append("Insufficient capacity may lead to service degradation")
            elif status == 'excess':
                risks.append("Excess capacity may indicate inefficient resource allocation")
            
            if capacity_gap > 20:
                risks.append("Large capacity gap poses operational risk")
            elif capacity_gap < -20:
                risks.append("Significant excess capacity may impact cost efficiency")
            
            return risks
            
        except Exception as e:
            logger.error(f"Error assessing capacity risks: {e}")
            return ["Unable to assess capacity risks"]
