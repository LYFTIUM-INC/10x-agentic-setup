#!/usr/bin/env python3
"""
Predictive Performance Analytics Engine
ML-powered performance forecasting, trend analysis, and risk assessment
Inspired by TimeGPT and modern forecasting techniques
"""

import time
import json
import logging
import sqlite3
import statistics
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrendDirection(Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"
    VOLATILE = "volatile"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ForecastConfidence(Enum):
    VERY_LOW = "very_low"  # 0-20%
    LOW = "low"           # 20-40%
    MEDIUM = "medium"     # 40-70%
    HIGH = "high"         # 70-90%
    VERY_HIGH = "very_high" # 90-100%

@dataclass
class PerformanceTrend:
    metric_name: str
    direction: TrendDirection
    confidence: float
    slope: float
    r_squared: float
    recent_values: List[float]
    predicted_next_values: List[float]
    trend_strength: str
    detected_at: float

@dataclass
class PerformanceForecast:
    metric_name: str
    forecast_horizon: int  # minutes
    predicted_values: List[float]
    confidence_intervals: List[Tuple[float, float]]
    forecast_confidence: ForecastConfidence
    seasonal_patterns: Dict[str, Any]
    anomaly_probability: float
    risk_assessment: RiskLevel
    generated_at: float

@dataclass
class VelocityPrediction:
    task_type: str
    predicted_completion_time: float
    confidence: float
    factors_considered: List[str]
    historical_performance: Dict[str, float]
    risk_factors: List[str]
    optimization_suggestions: List[str]
    prediction_accuracy_score: float

@dataclass
class RiskAssessment:
    risk_type: str
    risk_level: RiskLevel
    probability: float
    impact_score: float
    time_to_materialization: float  # minutes
    mitigation_strategies: List[str]
    early_warning_indicators: List[str]
    confidence: float

class PredictiveAnalyticsEngine:
    """Advanced predictive analytics for performance forecasting"""
    
    def __init__(self, metrics_collector=None):
        self.metrics_collector = metrics_collector
        
        # Database for prediction storage
        self.db_path = Path.home() / ".claude" / "predictive_analytics.db"
        self.init_database()
        
        # Prediction models and state
        self.trend_models = {}
        self.forecast_models = {}
        self.velocity_models = {}
        self.risk_models = {}
        
        # Configuration
        self.max_history_points = 1000
        self.min_data_points = 20
        self.forecast_horizons = [5, 15, 30, 60]  # minutes
        self.trend_window = 100  # data points
        
        # ML parameters
        self.seasonal_periods = [24, 168]  # hours, weekly patterns
        self.confidence_threshold = 0.6
        self.volatility_threshold = 0.3
        
        # Performance baselines
        self.performance_baselines = {}
        self.update_baselines()
        
        logger.info("Predictive analytics engine initialized")
    
    def init_database(self):
        """Initialize prediction database"""
        
        self.db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT,
                    direction TEXT,
                    confidence REAL,
                    slope REAL,
                    r_squared REAL,
                    trend_strength TEXT,
                    detected_at REAL,
                    data TEXT
                );
                
                CREATE TABLE IF NOT EXISTS forecasts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT,
                    forecast_horizon INTEGER,
                    predicted_values TEXT,
                    confidence_intervals TEXT,
                    forecast_confidence TEXT,
                    anomaly_probability REAL,
                    risk_level TEXT,
                    generated_at REAL
                );
                
                CREATE TABLE IF NOT EXISTS velocity_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_type TEXT,
                    predicted_time REAL,
                    confidence REAL,
                    factors TEXT,
                    historical_data TEXT,
                    risk_factors TEXT,
                    suggestions TEXT,
                    accuracy_score REAL,
                    predicted_at REAL
                );
                
                CREATE TABLE IF NOT EXISTS risk_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    risk_type TEXT,
                    risk_level TEXT,
                    probability REAL,
                    impact_score REAL,
                    time_to_materialization REAL,
                    mitigation_strategies TEXT,
                    warning_indicators TEXT,
                    confidence REAL,
                    assessed_at REAL
                );
                
                CREATE INDEX IF NOT EXISTS idx_trends_metric ON trends(metric_name);
                CREATE INDEX IF NOT EXISTS idx_forecasts_metric ON forecasts(metric_name);
                CREATE INDEX IF NOT EXISTS idx_velocity_task ON velocity_predictions(task_type);
                CREATE INDEX IF NOT EXISTS idx_risk_type ON risk_assessments(risk_type);
            """)
    
    def analyze_trends(self, metrics_data: Dict[str, List[float]], window_size: int = None) -> List[PerformanceTrend]:
        """Analyze performance trends using advanced statistical methods"""
        
        if window_size is None:
            window_size = self.trend_window
        
        trends = []
        
        for metric_name, values in metrics_data.items():
            if len(values) < self.min_data_points:
                continue
            
            # Use recent window for trend analysis
            recent_values = values[-window_size:]
            
            # Calculate trend using multiple methods
            trend = self._calculate_trend(metric_name, recent_values)
            if trend:
                trends.append(trend)
                self._store_trend(trend)
        
        return trends
    
    def generate_forecasts(self, metrics_data: Dict[str, List[float]], 
                         horizons: List[int] = None) -> List[PerformanceForecast]:
        """Generate ML-powered performance forecasts"""
        
        if horizons is None:
            horizons = self.forecast_horizons
        
        forecasts = []
        
        for metric_name, values in metrics_data.items():
            if len(values) < self.min_data_points * 2:  # Need more data for forecasting
                continue
            
            for horizon in horizons:
                forecast = self._generate_forecast(metric_name, values, horizon)
                if forecast:
                    forecasts.append(forecast)
                    self._store_forecast(forecast)
        
        return forecasts
    
    def predict_velocity(self, task_type: str, task_context: Dict[str, Any] = None) -> VelocityPrediction:
        """Predict task completion velocity based on historical patterns"""
        
        # Get historical performance for similar tasks
        historical_data = self._get_historical_velocity(task_type)
        
        # Analyze current system state
        current_metrics = self._get_current_performance_metrics()
        
        # Generate velocity prediction
        prediction = self._calculate_velocity_prediction(
            task_type, historical_data, current_metrics, task_context or {}
        )
        
        self._store_velocity_prediction(prediction)
        return prediction
    
    def assess_risks(self, current_metrics: Dict[str, float] = None) -> List[RiskAssessment]:
        """Comprehensive risk assessment for performance issues"""
        
        if current_metrics is None:
            current_metrics = self._get_current_performance_metrics()
        
        risk_assessments = []
        
        # Performance degradation risks
        perf_risks = self._assess_performance_risks(current_metrics)
        risk_assessments.extend(perf_risks)
        
        # Resource exhaustion risks
        resource_risks = self._assess_resource_risks(current_metrics)
        risk_assessments.extend(resource_risks)
        
        # System stability risks
        stability_risks = self._assess_stability_risks(current_metrics)
        risk_assessments.extend(stability_risks)
        
        # Capacity planning risks
        capacity_risks = self._assess_capacity_risks(current_metrics)
        risk_assessments.extend(capacity_risks)
        
        # Store all risk assessments
        for risk in risk_assessments:
            self._store_risk_assessment(risk)
        
        return risk_assessments
    
    def _calculate_trend(self, metric_name: str, values: List[float]) -> Optional[PerformanceTrend]:
        """Calculate trend using linear regression and statistical analysis"""
        
        if len(values) < 5:
            return None
        
        # Linear regression
        n = len(values)
        x = list(range(n))
        y = values
        
        # Calculate slope and correlation
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return None
        
        slope = numerator / denominator
        
        # Calculate R-squared
        y_pred = [slope * (x[i] - x_mean) + y_mean for i in range(n)]
        ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Determine trend direction and strength
        direction, confidence, trend_strength = self._classify_trend(slope, r_squared, values)
        
        # Predict next few values
        predicted_values = []
        for i in range(5):  # Predict next 5 points
            next_x = n + i
            next_y = slope * (next_x - x_mean) + y_mean
            predicted_values.append(max(0, next_y))  # Ensure non-negative
        
        return PerformanceTrend(
            metric_name=metric_name,
            direction=direction,
            confidence=confidence,
            slope=slope,
            r_squared=r_squared,
            recent_values=values[-10:],  # Last 10 values
            predicted_next_values=predicted_values,
            trend_strength=trend_strength,
            detected_at=time.time()
        )
    
    def _classify_trend(self, slope: float, r_squared: float, values: List[float]) -> Tuple[TrendDirection, float, str]:
        """Classify trend direction, confidence, and strength"""
        
        # Calculate volatility
        volatility = statistics.stdev(values) / statistics.mean(values) if statistics.mean(values) != 0 else 0
        
        # Base confidence on R-squared and volatility
        confidence = r_squared * (1 - min(volatility, 1.0))
        
        # Trend strength
        abs_slope = abs(slope)
        if abs_slope < 0.01:
            strength = "weak"
        elif abs_slope < 0.1:
            strength = "moderate"
        else:
            strength = "strong"
        
        # Direction classification
        if volatility > self.volatility_threshold and r_squared < 0.3:
            direction = TrendDirection.VOLATILE
        elif abs(slope) < 0.001:  # Very small slope
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.IMPROVING if metric_name in ['success_rate', 'efficiency'] else TrendDirection.DEGRADING
        else:
            direction = TrendDirection.DEGRADING if metric_name in ['success_rate', 'efficiency'] else TrendDirection.IMPROVING
        
        return direction, confidence, strength
    
    def _generate_forecast(self, metric_name: str, values: List[float], horizon: int) -> Optional[PerformanceForecast]:
        """Generate forecast using exponential smoothing and seasonal decomposition"""
        
        if len(values) < 10:
            return None
        
        # Simple exponential smoothing with trend (Holt's method)
        alpha = 0.3  # Level smoothing parameter
        beta = 0.1   # Trend smoothing parameter
        
        # Initialize
        level = values[0]
        trend = (values[1] - values[0])
        
        smoothed_values = [level]
        
        # Apply Holt's exponential smoothing
        for i in range(1, len(values)):
            prev_level = level
            level = alpha * values[i] + (1 - alpha) * (level + trend)
            trend = beta * (level - prev_level) + (1 - beta) * trend
            smoothed_values.append(level)
        
        # Generate forecast
        predicted_values = []
        confidence_intervals = []
        
        for h in range(1, horizon + 1):
            # Point forecast
            forecast_value = level + h * trend
            predicted_values.append(max(0, forecast_value))
            
            # Confidence interval (simple approach)
            residuals = [values[i] - smoothed_values[i] for i in range(len(values))]
            residual_std = statistics.stdev(residuals) if len(residuals) > 1 else 0
            
            margin = 1.96 * residual_std * math.sqrt(h)  # 95% confidence interval
            lower_bound = max(0, forecast_value - margin)
            upper_bound = forecast_value + margin
            confidence_intervals.append((lower_bound, upper_bound))
        
        # Assess forecast quality
        forecast_confidence = self._assess_forecast_confidence(values, smoothed_values, horizon)
        anomaly_probability = self._calculate_anomaly_probability(values, predicted_values[0])
        risk_level = self._assess_forecast_risk(metric_name, predicted_values, values)
        
        # Detect seasonal patterns (simplified)
        seasonal_patterns = self._detect_seasonal_patterns(values)
        
        return PerformanceForecast(
            metric_name=metric_name,
            forecast_horizon=horizon,
            predicted_values=predicted_values,
            confidence_intervals=confidence_intervals,
            forecast_confidence=forecast_confidence,
            seasonal_patterns=seasonal_patterns,
            anomaly_probability=anomaly_probability,
            risk_assessment=risk_level,
            generated_at=time.time()
        )
    
    def _assess_forecast_confidence(self, historical: List[float], smoothed: List[float], horizon: int) -> ForecastConfidence:
        """Assess forecast confidence based on historical accuracy"""
        
        if len(historical) != len(smoothed):
            return ForecastConfidence.LOW
        
        # Calculate MAPE (Mean Absolute Percentage Error)
        mape_values = []
        for i in range(len(historical)):
            if historical[i] != 0:
                mape = abs((historical[i] - smoothed[i]) / historical[i])
                mape_values.append(mape)
        
        if not mape_values:
            return ForecastConfidence.LOW
        
        avg_mape = statistics.mean(mape_values)
        
        # Adjust confidence based on forecast horizon
        horizon_penalty = min(0.1 * horizon, 0.5)
        adjusted_accuracy = (1 - avg_mape) * (1 - horizon_penalty)
        
        if adjusted_accuracy > 0.9:
            return ForecastConfidence.VERY_HIGH
        elif adjusted_accuracy > 0.7:
            return ForecastConfidence.HIGH
        elif adjusted_accuracy > 0.4:
            return ForecastConfidence.MEDIUM
        elif adjusted_accuracy > 0.2:
            return ForecastConfidence.LOW
        else:
            return ForecastConfidence.VERY_LOW
    
    def _calculate_anomaly_probability(self, historical: List[float], predicted_value: float) -> float:
        """Calculate probability that predicted value is anomalous"""
        
        if len(historical) < 10:
            return 0.5
        
        mean_val = statistics.mean(historical)
        std_val = statistics.stdev(historical)
        
        if std_val == 0:
            return 0.0 if predicted_value == mean_val else 1.0
        
        # Z-score based anomaly probability
        z_score = abs(predicted_value - mean_val) / std_val
        
        # Convert z-score to probability (simplified)
        if z_score > 3:
            return 0.9
        elif z_score > 2:
            return 0.7
        elif z_score > 1:
            return 0.3
        else:
            return 0.1
    
    def _assess_forecast_risk(self, metric_name: str, predicted_values: List[float], 
                           historical: List[float]) -> RiskLevel:
        """Assess risk level based on forecast"""
        
        if not predicted_values:
            return RiskLevel.MEDIUM
        
        # Risk thresholds by metric type
        risk_thresholds = {
            'cpu_usage': [50, 70, 85, 95],
            'memory_usage': [60, 75, 90, 98],
            'disk_usage': [70, 80, 90, 95],
            'execution_time': [5, 10, 20, 30],
            'error_rate': [0.01, 0.05, 0.1, 0.2]
        }
        
        thresholds = risk_thresholds.get(metric_name, [25, 50, 75, 90])
        max_predicted = max(predicted_values)
        
        if max_predicted >= thresholds[3]:
            return RiskLevel.CRITICAL
        elif max_predicted >= thresholds[2]:
            return RiskLevel.HIGH
        elif max_predicted >= thresholds[1]:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _detect_seasonal_patterns(self, values: List[float]) -> Dict[str, Any]:
        """Detect seasonal patterns in the data"""
        
        patterns = {
            'has_seasonality': False,
            'period': None,
            'amplitude': 0,
            'strength': 0
        }
        
        if len(values) < 50:  # Need sufficient data
            return patterns
        
        # Simple autocorrelation approach
        max_lag = min(50, len(values) // 4)
        best_correlation = 0
        best_period = None
        
        for lag in range(2, max_lag):
            if lag >= len(values):
                break
            
            # Calculate autocorrelation at this lag
            correlation = self._calculate_autocorrelation(values, lag)
            
            if correlation > best_correlation:
                best_correlation = correlation
                best_period = lag
        
        if best_correlation > 0.3:  # Threshold for significant seasonality
            patterns['has_seasonality'] = True
            patterns['period'] = best_period
            patterns['amplitude'] = self._calculate_seasonal_amplitude(values, best_period)
            patterns['strength'] = best_correlation
        
        return patterns
    
    def _calculate_autocorrelation(self, values: List[float], lag: int) -> float:
        """Calculate autocorrelation at given lag"""
        
        if lag >= len(values):
            return 0
        
        n = len(values) - lag
        if n <= 1:
            return 0
        
        mean_val = statistics.mean(values)
        
        numerator = sum((values[i] - mean_val) * (values[i + lag] - mean_val) for i in range(n))
        denominator = sum((values[i] - mean_val) ** 2 for i in range(len(values)))
        
        return numerator / denominator if denominator != 0 else 0
    
    def _calculate_seasonal_amplitude(self, values: List[float], period: int) -> float:
        """Calculate amplitude of seasonal pattern"""
        
        if period >= len(values):
            return 0
        
        # Group values by seasonal position
        seasonal_groups = [[] for _ in range(period)]
        
        for i, value in enumerate(values):
            seasonal_groups[i % period].append(value)
        
        # Calculate seasonal means
        seasonal_means = []
        for group in seasonal_groups:
            if group:
                seasonal_means.append(statistics.mean(group))
        
        if not seasonal_means:
            return 0
        
        # Amplitude is range of seasonal means
        return max(seasonal_means) - min(seasonal_means)
    
    def _calculate_velocity_prediction(self, task_type: str, historical_data: Dict[str, Any],
                                    current_metrics: Dict[str, float], context: Dict[str, Any]) -> VelocityPrediction:
        """Calculate velocity prediction for task completion"""
        
        # Base prediction on historical performance
        historical_times = historical_data.get('completion_times', [])
        baseline_time = statistics.mean(historical_times) if historical_times else 60.0
        
        # Adjust for current system performance
        performance_factor = self._calculate_performance_factor(current_metrics)
        
        # Adjust for task complexity
        complexity_factor = self._estimate_task_complexity(task_type, context)
        
        # Calculate predicted time
        predicted_time = baseline_time * performance_factor * complexity_factor
        
        # Calculate confidence based on data quality
        confidence = self._calculate_prediction_confidence(historical_data, current_metrics)
        
        # Identify risk factors
        risk_factors = self._identify_velocity_risks(current_metrics, context)
        
        # Generate optimization suggestions
        suggestions = self._generate_velocity_optimizations(task_type, current_metrics, risk_factors)
        
        # Calculate prediction accuracy score
        accuracy_score = self._estimate_prediction_accuracy(historical_data, current_metrics)
        
        return VelocityPrediction(
            task_type=task_type,
            predicted_completion_time=predicted_time,
            confidence=confidence,
            factors_considered=[
                'historical_performance',
                'current_system_metrics',
                'task_complexity',
                'resource_availability'
            ],
            historical_performance={
                'avg_completion_time': baseline_time,
                'success_rate': historical_data.get('success_rate', 0.9),
                'sample_size': len(historical_times)
            },
            risk_factors=risk_factors,
            optimization_suggestions=suggestions,
            prediction_accuracy_score=accuracy_score
        )
    
    def _calculate_performance_factor(self, metrics: Dict[str, float]) -> float:
        """Calculate how current performance affects task completion time"""
        
        cpu_usage = metrics.get('cpu_usage', 50)
        memory_usage = metrics.get('memory_usage', 50)
        
        # Higher usage = slower performance
        cpu_factor = 1 + (cpu_usage - 50) / 200  # Normalize around 50%
        memory_factor = 1 + (memory_usage - 50) / 200
        
        # Combine factors (weighted average)
        overall_factor = (cpu_factor * 0.6) + (memory_factor * 0.4)
        
        return max(0.1, min(3.0, overall_factor))  # Clamp between 0.1x and 3x
    
    def _estimate_task_complexity(self, task_type: str, context: Dict[str, Any]) -> float:
        """Estimate task complexity multiplier"""
        
        # Base complexity by task type
        complexity_map = {
            'Bash': 1.2,
            'Task': 2.0,
            'Read': 0.8,
            'Write': 1.0,
            'Edit': 1.1,
            'Grep': 1.3,
            'WebFetch': 1.5
        }
        
        base_complexity = complexity_map.get(task_type, 1.0)
        
        # Adjust based on context
        if 'file_size' in context and context['file_size'] > 100000:
            base_complexity *= 1.5
        
        if 'parallel_operations' in context and context['parallel_operations'] > 1:
            base_complexity *= 0.8  # Parallel processing is faster
        
        return base_complexity
    
    def _calculate_prediction_confidence(self, historical_data: Dict[str, Any], 
                                       current_metrics: Dict[str, float]) -> float:
        """Calculate confidence in velocity prediction"""
        
        # Base confidence on historical data quality
        sample_size = len(historical_data.get('completion_times', []))
        variance = statistics.variance(historical_data.get('completion_times', [0])) if sample_size > 1 else 0
        
        # Confidence factors
        sample_confidence = min(1.0, sample_size / 50)  # More samples = higher confidence
        variance_confidence = max(0.1, 1 - (variance / 100))  # Lower variance = higher confidence
        
        # Current system stability
        cpu_stability = 1 - abs(current_metrics.get('cpu_usage', 50) - 50) / 50
        memory_stability = 1 - abs(current_metrics.get('memory_usage', 50) - 50) / 50
        system_confidence = (cpu_stability + memory_stability) / 2
        
        # Overall confidence
        overall_confidence = (sample_confidence * 0.4) + (variance_confidence * 0.3) + (system_confidence * 0.3)
        
        return max(0.1, min(1.0, overall_confidence))
    
    def _identify_velocity_risks(self, metrics: Dict[str, float], context: Dict[str, Any]) -> List[str]:
        """Identify risk factors that could affect task velocity"""
        
        risks = []
        
        # Resource risks
        if metrics.get('cpu_usage', 0) > 80:
            risks.append("High CPU utilization may slow task execution")
        
        if metrics.get('memory_usage', 0) > 85:
            risks.append("High memory usage may cause slowdowns or failures")
        
        if metrics.get('disk_usage', 0) > 90:
            risks.append("Low disk space may impact task performance")
        
        # Context-based risks
        if context.get('file_size', 0) > 1000000:
            risks.append("Large file size may require additional processing time")
        
        if context.get('network_dependent', False):
            risks.append("Network latency may affect task completion time")
        
        if context.get('external_dependencies', 0) > 0:
            risks.append("External dependencies may introduce unpredictable delays")
        
        return risks
    
    def _generate_velocity_optimizations(self, task_type: str, metrics: Dict[str, float], 
                                       risks: List[str]) -> List[str]:
        """Generate optimization suggestions for improved velocity"""
        
        suggestions = []
        
        # Resource-based optimizations
        if metrics.get('cpu_usage', 0) > 70:
            suggestions.append("Consider parallel processing to distribute CPU load")
            suggestions.append("Optimize algorithms to reduce computational complexity")
        
        if metrics.get('memory_usage', 0) > 75:
            suggestions.append("Implement memory-efficient data structures")
            suggestions.append("Use streaming processing for large datasets")
        
        # Task-specific optimizations
        if task_type == 'Task':
            suggestions.append("Break complex tasks into smaller, focused subtasks")
            suggestions.append("Use specific prompts to reduce processing overhead")
        elif task_type == 'Bash':
            suggestions.append("Use built-in commands instead of external utilities")
            suggestions.append("Minimize file I/O operations")
        elif task_type in ['Read', 'Write', 'Edit']:
            suggestions.append("Process files in chunks for better memory usage")
            suggestions.append("Use efficient file formats when possible")
        
        # Risk-specific optimizations
        if any('network' in risk.lower() for risk in risks):
            suggestions.append("Implement retry mechanisms for network operations")
            suggestions.append("Cache frequently accessed network resources")
        
        if any('disk' in risk.lower() for risk in risks):
            suggestions.append("Clean up temporary files before task execution")
            suggestions.append("Use compression for large file operations")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def _estimate_prediction_accuracy(self, historical_data: Dict[str, Any], 
                                    current_metrics: Dict[str, float]) -> float:
        """Estimate the accuracy score of the prediction"""
        
        # Base accuracy on historical consistency
        completion_times = historical_data.get('completion_times', [])
        if len(completion_times) < 2:
            return 0.5  # Medium accuracy for limited data
        
        # Calculate coefficient of variation
        mean_time = statistics.mean(completion_times)
        std_time = statistics.stdev(completion_times)
        cv = std_time / mean_time if mean_time > 0 else 1
        
        # Lower variation = higher accuracy
        variation_score = max(0.1, 1 - cv)
        
        # System stability affects accuracy
        cpu_stability = 1 - abs(current_metrics.get('cpu_usage', 50) - 50) / 50
        memory_stability = 1 - abs(current_metrics.get('memory_usage', 50) - 50) / 50
        stability_score = (cpu_stability + memory_stability) / 2
        
        # Sample size affects accuracy
        sample_score = min(1.0, len(completion_times) / 20)
        
        # Combined accuracy score
        accuracy = (variation_score * 0.5) + (stability_score * 0.3) + (sample_score * 0.2)
        
        return max(0.1, min(1.0, accuracy))
    
    def _assess_performance_risks(self, metrics: Dict[str, float]) -> List[RiskAssessment]:
        """Assess risks related to performance degradation"""
        
        risks = []
        
        # CPU performance risk
        cpu_usage = metrics.get('cpu_usage', 0)
        if cpu_usage > 60:
            risk_level = RiskLevel.CRITICAL if cpu_usage > 90 else \
                        RiskLevel.HIGH if cpu_usage > 80 else RiskLevel.MEDIUM
            
            risks.append(RiskAssessment(
                risk_type="cpu_performance_degradation",
                risk_level=risk_level,
                probability=min(1.0, (cpu_usage - 60) / 40),
                impact_score=8.0,
                time_to_materialization=max(5, 60 - cpu_usage),
                mitigation_strategies=[
                    "Implement CPU throttling",
                    "Distribute workload across multiple cores",
                    "Optimize CPU-intensive algorithms"
                ],
                early_warning_indicators=[
                    "CPU usage trending upward",
                    "Increased task execution times",
                    "System responsiveness degradation"
                ],
                confidence=0.8
            ))
        
        # Memory performance risk
        memory_usage = metrics.get('memory_usage', 0)
        if memory_usage > 70:
            risk_level = RiskLevel.CRITICAL if memory_usage > 95 else \
                        RiskLevel.HIGH if memory_usage > 85 else RiskLevel.MEDIUM
            
            risks.append(RiskAssessment(
                risk_type="memory_exhaustion",
                risk_level=risk_level,
                probability=min(1.0, (memory_usage - 70) / 30),
                impact_score=9.0,
                time_to_materialization=max(10, 120 - memory_usage),
                mitigation_strategies=[
                    "Implement memory cleanup routines",
                    "Use memory-efficient data structures",
                    "Enable memory compression"
                ],
                early_warning_indicators=[
                    "Memory usage steadily increasing",
                    "Increased garbage collection frequency",
                    "Application slowdowns"
                ],
                confidence=0.85
            ))
        
        return risks
    
    def _assess_resource_risks(self, metrics: Dict[str, float]) -> List[RiskAssessment]:
        """Assess risks related to resource exhaustion"""
        
        risks = []
        
        # Disk space risk
        disk_usage = metrics.get('disk_usage', 0)
        if disk_usage > 80:
            risk_level = RiskLevel.CRITICAL if disk_usage > 95 else \
                        RiskLevel.HIGH if disk_usage > 90 else RiskLevel.MEDIUM
            
            risks.append(RiskAssessment(
                risk_type="disk_space_exhaustion",
                risk_level=risk_level,
                probability=min(1.0, (disk_usage - 80) / 20),
                impact_score=7.5,
                time_to_materialization=max(30, 200 - disk_usage * 2),
                mitigation_strategies=[
                    "Clean up temporary files",
                    "Archive old log files",
                    "Implement disk space monitoring"
                ],
                early_warning_indicators=[
                    "Disk usage above 80%",
                    "Temporary file accumulation",
                    "Log file growth"
                ],
                confidence=0.9
            ))
        
        return risks
    
    def _assess_stability_risks(self, metrics: Dict[str, float]) -> List[RiskAssessment]:
        """Assess risks related to system stability"""
        
        risks = []
        
        # Overall system stability risk based on multiple metrics
        cpu_usage = metrics.get('cpu_usage', 0)
        memory_usage = metrics.get('memory_usage', 0)
        
        stability_score = (cpu_usage + memory_usage) / 2
        
        if stability_score > 75:
            risks.append(RiskAssessment(
                risk_type="system_instability",
                risk_level=RiskLevel.HIGH if stability_score > 90 else RiskLevel.MEDIUM,
                probability=min(1.0, (stability_score - 75) / 25),
                impact_score=8.5,
                time_to_materialization=max(15, 150 - stability_score),
                mitigation_strategies=[
                    "Implement graceful degradation",
                    "Add system health monitoring",
                    "Create automatic failover mechanisms"
                ],
                early_warning_indicators=[
                    "Multiple resource metrics trending high",
                    "Increased error rates",
                    "Response time degradation"
                ],
                confidence=0.75
            ))
        
        return risks
    
    def _assess_capacity_risks(self, metrics: Dict[str, float]) -> List[RiskAssessment]:
        """Assess risks related to capacity planning"""
        
        risks = []
        
        # Analyze growth trends if we have historical data
        # For now, implement a simple capacity risk based on current utilization
        
        avg_usage = (
            metrics.get('cpu_usage', 0) + 
            metrics.get('memory_usage', 0) + 
            metrics.get('disk_usage', 0)
        ) / 3
        
        if avg_usage > 70:
            risks.append(RiskAssessment(
                risk_type="capacity_planning",
                risk_level=RiskLevel.MEDIUM if avg_usage < 85 else RiskLevel.HIGH,
                probability=0.6,
                impact_score=6.0,
                time_to_materialization=720,  # 12 hours
                mitigation_strategies=[
                    "Plan for capacity expansion",
                    "Implement auto-scaling",
                    "Optimize resource utilization"
                ],
                early_warning_indicators=[
                    "Sustained high resource utilization",
                    "Performance degradation during peak times",
                    "Limited headroom for growth"
                ],
                confidence=0.7
            ))
        
        return risks
    
    def _get_historical_velocity(self, task_type: str) -> Dict[str, Any]:
        """Get historical velocity data for task type"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT predicted_time, accuracy_score FROM velocity_predictions WHERE task_type = ? ORDER BY predicted_at DESC LIMIT 50",
                    (task_type,)
                )
                
                results = cursor.fetchall()
                
                if results:
                    times = [r[0] for r in results]
                    accuracies = [r[1] for r in results if r[1] is not None]
                    
                    return {
                        'completion_times': times,
                        'success_rate': statistics.mean(accuracies) if accuracies else 0.8,
                        'sample_size': len(times)
                    }
        
        except Exception as e:
            logger.warning(f"Failed to get historical velocity data: {e}")
        
        # Default fallback data
        return {
            'completion_times': [30.0, 45.0, 60.0],  # Default estimates
            'success_rate': 0.85,
            'sample_size': 3
        }
    
    def _get_current_performance_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""
        
        if self.metrics_collector:
            try:
                summary = self.metrics_collector.get_performance_summary(window_seconds=300)
                return {
                    'cpu_usage': summary.get('system_metrics', {}).get('avg_cpu_usage', 50),
                    'memory_usage': summary.get('system_metrics', {}).get('avg_memory_usage', 50),
                    'disk_usage': summary.get('system_metrics', {}).get('avg_disk_usage', 50),
                    'execution_time': summary.get('tool_execution', {}).get('avg_execution_time', 5),
                    'success_rate': summary.get('tool_execution', {}).get('success_rate', 90)
                }
            except:
                pass
        
        # Fallback to system metrics
        try:
            import psutil
            return {
                'cpu_usage': psutil.cpu_percent(interval=1),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'execution_time': 5.0,
                'success_rate': 90.0
            }
        except:
            return {
                'cpu_usage': 50.0,
                'memory_usage': 50.0,
                'disk_usage': 50.0,
                'execution_time': 5.0,
                'success_rate': 90.0
            }
    
    def update_baselines(self):
        """Update performance baselines"""
        
        current_time = time.time()
        self.performance_baselines = {
            'cpu_usage': {'baseline': 25.0, 'updated_at': current_time},
            'memory_usage': {'baseline': 40.0, 'updated_at': current_time},
            'disk_usage': {'baseline': 30.0, 'updated_at': current_time},
            'execution_time': {'baseline': 2.0, 'updated_at': current_time}
        }
        
        logger.info("Performance baselines updated")
    
    def _store_trend(self, trend: PerformanceTrend):
        """Store trend analysis in database"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO trends (metric_name, direction, confidence, slope, r_squared, 
                                      trend_strength, detected_at, data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trend.metric_name,
                    trend.direction.value,
                    trend.confidence,
                    trend.slope,
                    trend.r_squared,
                    trend.trend_strength,
                    trend.detected_at,
                    json.dumps({
                        'recent_values': trend.recent_values,
                        'predicted_values': trend.predicted_next_values
                    })
                ))
        except Exception as e:
            logger.error(f"Failed to store trend: {e}")
    
    def _store_forecast(self, forecast: PerformanceForecast):
        """Store forecast in database"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO forecasts (metric_name, forecast_horizon, predicted_values,
                                         confidence_intervals, forecast_confidence, anomaly_probability,
                                         risk_level, generated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    forecast.metric_name,
                    forecast.forecast_horizon,
                    json.dumps(forecast.predicted_values),
                    json.dumps(forecast.confidence_intervals),
                    forecast.forecast_confidence.value,
                    forecast.anomaly_probability,
                    forecast.risk_assessment.value,
                    forecast.generated_at
                ))
        except Exception as e:
            logger.error(f"Failed to store forecast: {e}")
    
    def _store_velocity_prediction(self, prediction: VelocityPrediction):
        """Store velocity prediction in database"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO velocity_predictions (task_type, predicted_time, confidence,
                                                    factors, historical_data, risk_factors,
                                                    suggestions, accuracy_score, predicted_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    prediction.task_type,
                    prediction.predicted_completion_time,
                    prediction.confidence,
                    json.dumps(prediction.factors_considered),
                    json.dumps(prediction.historical_performance),
                    json.dumps(prediction.risk_factors),
                    json.dumps(prediction.optimization_suggestions),
                    prediction.prediction_accuracy_score,
                    time.time()
                ))
        except Exception as e:
            logger.error(f"Failed to store velocity prediction: {e}")
    
    def _store_risk_assessment(self, risk: RiskAssessment):
        """Store risk assessment in database"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO risk_assessments (risk_type, risk_level, probability, impact_score,
                                                time_to_materialization, mitigation_strategies,
                                                warning_indicators, confidence, assessed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    risk.risk_type,
                    risk.risk_level.value,
                    risk.probability,
                    risk.impact_score,
                    risk.time_to_materialization,
                    json.dumps(risk.mitigation_strategies),
                    json.dumps(risk.early_warning_indicators),
                    risk.confidence,
                    time.time()
                ))
        except Exception as e:
            logger.error(f"Failed to store risk assessment: {e}")

# Example usage and testing
def test_predictive_analytics():
    """Test predictive analytics functionality"""
    
    print("🧪 Testing Predictive Analytics Engine...")
    
    engine = PredictiveAnalyticsEngine()
    
    # Test trend analysis
    print("📈 Testing trend analysis...")
    metrics_data = {
        'cpu_usage': [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70],
        'memory_usage': [30, 32, 28, 35, 33, 40, 38, 45, 42, 48, 50],
        'execution_time': [2.0, 2.2, 2.1, 2.5, 2.3, 2.8, 2.6, 3.0, 2.9, 3.2, 3.1]
    }
    
    trends = engine.analyze_trends(metrics_data)
    print(f"   Detected {len(trends)} trends")
    for trend in trends:
        print(f"   {trend.metric_name}: {trend.direction.value} ({trend.confidence:.2f} confidence)")
    
    # Test forecasting
    print("\n🔮 Testing forecasting...")
    forecasts = engine.generate_forecasts(metrics_data, [5, 15])
    print(f"   Generated {len(forecasts)} forecasts")
    for forecast in forecasts:
        print(f"   {forecast.metric_name} ({forecast.forecast_horizon}min): {forecast.forecast_confidence.value}")
    
    # Test velocity prediction
    print("\n⚡ Testing velocity prediction...")
    velocity = engine.predict_velocity('Task', {'complexity': 'medium'})
    print(f"   Predicted Task completion: {velocity.predicted_completion_time:.1f}s ({velocity.confidence:.2f} confidence)")
    print(f"   Risk factors: {len(velocity.risk_factors)}")
    print(f"   Optimization suggestions: {len(velocity.optimization_suggestions)}")
    
    # Test risk assessment
    print("\n⚠️ Testing risk assessment...")
    current_metrics = {'cpu_usage': 85, 'memory_usage': 75, 'disk_usage': 65}
    risks = engine.assess_risks(current_metrics)
    print(f"   Identified {len(risks)} risks")
    for risk in risks:
        print(f"   {risk.risk_type}: {risk.risk_level.value} ({risk.probability:.2f} probability)")
    
    print("\n✅ Predictive analytics engine test completed!")

if __name__ == "__main__":
    test_predictive_analytics()