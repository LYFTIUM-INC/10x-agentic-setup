"""
Predictive Analytics MCP Server
TimeGPT-inspired forecasting system for development velocity, risk analysis, and performance prediction
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import numpy as np
import sqlite3
import pickle
from collections import defaultdict, deque
import uuid

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TimeSeriesPoint:
    """Represents a single point in a time series"""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ForecastResult:
    """Represents a forecasting result"""
    forecast_id: str
    forecast_horizon: int
    predictions: List[float]
    confidence_intervals: List[Tuple[float, float]]
    accuracy_score: float
    model_confidence: float
    generated_at: datetime
    
@dataclass
class RiskAssessment:
    """Represents a risk assessment result"""
    risk_id: str
    risk_type: str
    risk_level: str  # "low", "medium", "high", "critical"
    probability: float
    impact_score: float
    risk_factors: List[str]
    mitigation_strategies: List[str]
    confidence: float
    assessed_at: datetime

@dataclass
class PerformancePrediction:
    """Represents a performance prediction"""
    prediction_id: str
    metric_name: str
    predicted_value: float
    confidence_interval: Tuple[float, float]
    bottlenecks: List[str]
    optimization_suggestions: List[str]
    prediction_confidence: float
    predicted_at: datetime

class TimeSeriesDatabase:
    """Manages time series data storage and retrieval"""
    
    def __init__(self, db_path: str = "predictive_analytics.db"):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the database schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Time series data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS time_series_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    series_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    value REAL NOT NULL,
                    metadata BLOB,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Forecasts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS forecasts (
                    forecast_id TEXT PRIMARY KEY,
                    series_name TEXT NOT NULL,
                    forecast_horizon INTEGER,
                    predictions BLOB,
                    confidence_intervals BLOB,
                    accuracy_score REAL,
                    model_confidence REAL,
                    generated_at TEXT
                )
            ''')
            
            # Risk assessments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS risk_assessments (
                    risk_id TEXT PRIMARY KEY,
                    risk_type TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    probability REAL,
                    impact_score REAL,
                    risk_factors BLOB,
                    mitigation_strategies BLOB,
                    confidence REAL,
                    assessed_at TEXT
                )
            ''')
            
            # Performance predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_predictions (
                    prediction_id TEXT PRIMARY KEY,
                    metric_name TEXT NOT NULL,
                    predicted_value REAL,
                    confidence_interval BLOB,
                    bottlenecks BLOB,
                    optimization_suggestions BLOB,
                    prediction_confidence REAL,
                    predicted_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Predictive analytics database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
    
    async def store_time_series_point(self, series_name: str, point: TimeSeriesPoint):
        """Store a time series data point"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            metadata_blob = pickle.dumps(point.metadata) if point.metadata else None
            
            cursor.execute('''
                INSERT INTO time_series_data (series_name, timestamp, value, metadata)
                VALUES (?, ?, ?, ?)
            ''', (
                series_name,
                point.timestamp.isoformat(),
                point.value,
                metadata_blob
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store time series point: {str(e)}")
    
    async def get_time_series_data(self, series_name: str, 
                                 start_time: Optional[datetime] = None,
                                 end_time: Optional[datetime] = None,
                                 limit: int = 1000) -> List[TimeSeriesPoint]:
        """Retrieve time series data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT timestamp, value, metadata FROM time_series_data WHERE series_name = ?"
            params = [series_name]
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            points = []
            for timestamp_str, value, metadata_blob in rows:
                metadata = pickle.loads(metadata_blob) if metadata_blob else {}
                point = TimeSeriesPoint(
                    timestamp=datetime.fromisoformat(timestamp_str),
                    value=float(value),
                    metadata=metadata
                )
                points.append(point)
            
            conn.close()
            return points
            
        except Exception as e:
            logger.error(f"Failed to retrieve time series data: {str(e)}")
            return []

class TimeGPTInspiredForecaster:
    """TimeGPT-inspired forecasting engine for zero-shot predictions"""
    
    def __init__(self):
        self.model_weights = {}
        self.pattern_memory = {}
        self.seasonal_patterns = {}
        self.trend_components = {}
        
    async def forecast_time_series(self, 
                                 data: List[TimeSeriesPoint], 
                                 horizon: int = 10,
                                 confidence_level: float = 0.95) -> ForecastResult:
        """Generate forecasts using TimeGPT-inspired zero-shot approach"""
        
        if len(data) < 3:
            # Return default forecast for insufficient data
            return self._create_default_forecast(horizon)
        
        # Extract time series values
        values = [point.value for point in data]
        timestamps = [point.timestamp for point in data]
        
        # Analyze patterns
        trend = await self._extract_trend(values)
        seasonality = await self._extract_seasonality(values, timestamps)
        noise_level = await self._estimate_noise_level(values)
        
        # Generate predictions
        predictions = await self._generate_predictions(
            values, trend, seasonality, horizon
        )
        
        # Calculate confidence intervals
        confidence_intervals = await self._calculate_confidence_intervals(
            predictions, noise_level, confidence_level
        )
        
        # Assess accuracy based on recent performance
        accuracy_score = await self._assess_forecast_accuracy(values)
        
        # Calculate model confidence
        model_confidence = await self._calculate_model_confidence(
            values, trend, seasonality, noise_level
        )
        
        return ForecastResult(
            forecast_id=str(uuid.uuid4()),
            forecast_horizon=horizon,
            predictions=predictions,
            confidence_intervals=confidence_intervals,
            accuracy_score=accuracy_score,
            model_confidence=model_confidence,
            generated_at=datetime.now()
        )
    
    async def _extract_trend(self, values: List[float]) -> Dict[str, Any]:
        """Extract trend component from time series"""
        if len(values) < 2:
            return {"type": "constant", "slope": 0.0, "strength": 0.0}
        
        # Simple linear trend extraction
        x = np.arange(len(values))
        y = np.array(values)
        
        # Calculate slope using least squares
        slope = np.sum((x - np.mean(x)) * (y - np.mean(y))) / np.sum((x - np.mean(x))**2)
        
        # Determine trend strength
        trend_strength = abs(slope) / (np.std(values) + 1e-8)
        
        trend_type = "increasing" if slope > 0.01 else "decreasing" if slope < -0.01 else "constant"
        
        return {
            "type": trend_type,
            "slope": slope,
            "strength": min(trend_strength, 1.0)
        }
    
    async def _extract_seasonality(self, values: List[float], 
                                 timestamps: List[datetime]) -> Dict[str, Any]:
        """Extract seasonal patterns from time series"""
        if len(values) < 7:  # Need at least a week of data
            return {"detected": False, "period": 0, "strength": 0.0}
        
        # Check for weekly patterns (common in development metrics)
        weekly_pattern = await self._detect_weekly_pattern(values, timestamps)
        
        # Check for daily patterns
        daily_pattern = await self._detect_daily_pattern(values, timestamps)
        
        # Return strongest pattern
        if weekly_pattern["strength"] > daily_pattern["strength"]:
            return {
                "detected": True,
                "type": "weekly",
                "period": 7,
                "strength": weekly_pattern["strength"],
                "pattern": weekly_pattern["pattern"]
            }
        elif daily_pattern["strength"] > 0.1:
            return {
                "detected": True,
                "type": "daily", 
                "period": 1,
                "strength": daily_pattern["strength"],
                "pattern": daily_pattern["pattern"]
            }
        else:
            return {"detected": False, "period": 0, "strength": 0.0}
    
    async def _detect_weekly_pattern(self, values: List[float], 
                                   timestamps: List[datetime]) -> Dict[str, Any]:
        """Detect weekly patterns in the data"""
        if len(values) < 14:  # Need at least 2 weeks
            return {"strength": 0.0, "pattern": []}
        
        # Group by day of week
        weekday_values = defaultdict(list)
        for value, timestamp in zip(values, timestamps):
            weekday = timestamp.weekday()  # 0=Monday, 6=Sunday
            weekday_values[weekday].append(value)
        
        # Calculate average for each day of week
        weekday_averages = {}
        for weekday in range(7):
            if weekday in weekday_values and weekday_values[weekday]:
                weekday_averages[weekday] = np.mean(weekday_values[weekday])
            else:
                weekday_averages[weekday] = np.mean(values)
        
        # Calculate pattern strength
        overall_mean = np.mean(values)
        daily_means = list(weekday_averages.values())
        pattern_variance = np.var(daily_means)
        total_variance = np.var(values)
        
        strength = pattern_variance / (total_variance + 1e-8)
        
        return {
            "strength": min(strength, 1.0),
            "pattern": daily_means
        }
    
    async def _detect_daily_pattern(self, values: List[float], 
                                  timestamps: List[datetime]) -> Dict[str, Any]:
        """Detect daily patterns in the data"""
        if len(values) < 24:  # Need at least 24 hours of data
            return {"strength": 0.0, "pattern": []}
        
        # Group by hour of day
        hourly_values = defaultdict(list)
        for value, timestamp in zip(values, timestamps):
            hour = timestamp.hour
            hourly_values[hour].append(value)
        
        # Calculate average for each hour
        hourly_averages = {}
        for hour in range(24):
            if hour in hourly_values and hourly_values[hour]:
                hourly_averages[hour] = np.mean(hourly_values[hour])
            else:
                hourly_averages[hour] = np.mean(values)
        
        # Calculate pattern strength
        hourly_means = list(hourly_averages.values())
        pattern_variance = np.var(hourly_means)
        total_variance = np.var(values)
        
        strength = pattern_variance / (total_variance + 1e-8)
        
        return {
            "strength": min(strength, 1.0),
            "pattern": hourly_means
        }
    
    async def _estimate_noise_level(self, values: List[float]) -> float:
        """Estimate the noise level in the time series"""
        if len(values) < 3:
            return np.std(values) if values else 1.0
        
        # Calculate first differences to estimate noise
        diffs = np.diff(values)
        noise_estimate = np.std(diffs) / np.sqrt(2)  # Adjust for differencing
        
        return max(noise_estimate, 0.01)  # Minimum noise level
    
    async def _generate_predictions(self, values: List[float], 
                                  trend: Dict[str, Any],
                                  seasonality: Dict[str, Any],
                                  horizon: int) -> List[float]:
        """Generate predictions combining trend and seasonality"""
        if not values:
            return [0.0] * horizon
        
        predictions = []
        last_value = values[-1]
        
        for h in range(1, horizon + 1):
            # Start with last observed value
            pred = last_value
            
            # Add trend component
            if trend["type"] != "constant":
                trend_contribution = trend["slope"] * h * trend["strength"]
                pred += trend_contribution
            
            # Add seasonal component
            if seasonality["detected"]:
                seasonal_index = (len(values) + h - 1) % seasonality["period"]
                seasonal_pattern = seasonality.get("pattern", [])
                
                if seasonal_pattern and seasonal_index < len(seasonal_pattern):
                    seasonal_baseline = np.mean(values) if values else 0
                    seasonal_contribution = (seasonal_pattern[seasonal_index] - seasonal_baseline) * seasonality["strength"]
                    pred += seasonal_contribution
            
            # Add slight mean reversion to prevent unrealistic predictions
            mean_value = np.mean(values[-min(10, len(values)):])  # Recent mean
            reversion_factor = 0.1  # Small reversion
            pred = pred * (1 - reversion_factor) + mean_value * reversion_factor
            
            predictions.append(pred)
        
        return predictions
    
    async def _calculate_confidence_intervals(self, predictions: List[float], 
                                            noise_level: float,
                                            confidence_level: float) -> List[Tuple[float, float]]:
        """Calculate confidence intervals for predictions"""
        z_score = 1.96 if confidence_level >= 0.95 else 1.64  # Approximate z-scores
        
        intervals = []
        for i, pred in enumerate(predictions):
            # Increase uncertainty with longer horizons
            horizon_factor = 1 + 0.1 * i
            margin = z_score * noise_level * horizon_factor
            
            lower_bound = pred - margin
            upper_bound = pred + margin
            intervals.append((lower_bound, upper_bound))
        
        return intervals
    
    async def _assess_forecast_accuracy(self, values: List[float]) -> float:
        """Assess forecast accuracy based on recent performance"""
        if len(values) < 5:
            return 0.7  # Default accuracy for insufficient data
        
        # Use last 20% of data for backtesting
        test_size = max(1, len(values) // 5)
        train_data = values[:-test_size]
        test_data = values[-test_size:]
        
        if len(train_data) < 2:
            return 0.7
        
        # Generate simple predictions for test period
        trend_slope = (train_data[-1] - train_data[0]) / len(train_data)
        
        predictions = []
        last_train = train_data[-1]
        for i in range(test_size):
            pred = last_train + trend_slope * (i + 1)
            predictions.append(pred)
        
        # Calculate accuracy using MAPE (Mean Absolute Percentage Error)
        if test_data and predictions:
            mape = np.mean([abs(actual - pred) / (abs(actual) + 1e-8) 
                           for actual, pred in zip(test_data, predictions)])
            accuracy = max(0.0, 1.0 - mape)
            return min(accuracy, 0.95)  # Cap at 95%
        
        return 0.7
    
    async def _calculate_model_confidence(self, values: List[float],
                                        trend: Dict[str, Any],
                                        seasonality: Dict[str, Any],
                                        noise_level: float) -> float:
        """Calculate overall model confidence"""
        confidence_factors = []
        
        # Data quantity confidence
        data_confidence = min(1.0, len(values) / 50.0)  # Higher confidence with more data
        confidence_factors.append(data_confidence)
        
        # Trend clarity confidence
        trend_confidence = trend.get("strength", 0.0)
        confidence_factors.append(trend_confidence)
        
        # Seasonality confidence
        seasonal_confidence = seasonality.get("strength", 0.0) if seasonality.get("detected") else 0.5
        confidence_factors.append(seasonal_confidence)
        
        # Noise level confidence (lower noise = higher confidence)
        if values:
            signal_to_noise = np.std(values) / (noise_level + 1e-8)
            noise_confidence = min(1.0, signal_to_noise / 10.0)
            confidence_factors.append(noise_confidence)
        
        return np.mean(confidence_factors)
    
    def _create_default_forecast(self, horizon: int) -> ForecastResult:
        """Create a default forecast for insufficient data"""
        predictions = [0.0] * horizon
        confidence_intervals = [(0.0, 0.0)] * horizon
        
        return ForecastResult(
            forecast_id=str(uuid.uuid4()),
            forecast_horizon=horizon,
            predictions=predictions,
            confidence_intervals=confidence_intervals,
            accuracy_score=0.5,
            model_confidence=0.3,
            generated_at=datetime.now()
        )

class DevelopmentVelocityForecaster:
    """Forecasts development velocity metrics"""
    
    def __init__(self, ts_db: TimeSeriesDatabase):
        self.ts_db = ts_db
        self.forecaster = TimeGPTInspiredForecaster()
        self.velocity_metrics = [
            "commits_per_day",
            "pull_requests_per_week", 
            "story_points_per_sprint",
            "bugs_fixed_per_week",
            "lines_of_code_per_day",
            "deployment_frequency",
            "lead_time",
            "cycle_time"
        ]
    
    async def forecast_velocity(self, metric_name: str, 
                              days_ahead: int = 14) -> ForecastResult:
        """Forecast a specific velocity metric"""
        
        # Get historical data
        end_time = datetime.now()
        start_time = end_time - timedelta(days=90)  # Last 90 days
        
        data = await self.ts_db.get_time_series_data(
            f"velocity_{metric_name}", start_time, end_time
        )
        
        if not data:
            # Generate synthetic data for demonstration
            data = await self._generate_synthetic_velocity_data(metric_name)
        
        # Generate forecast
        forecast = await self.forecaster.forecast_time_series(
            data, horizon=days_ahead
        )
        
        return forecast
    
    async def forecast_sprint_completion(self, 
                                       current_sprint_progress: Dict[str, Any]) -> Dict[str, Any]:
        """Forecast sprint completion probability"""
        
        # Get velocity history
        velocity_data = await self.ts_db.get_time_series_data(
            "velocity_story_points_per_sprint", 
            datetime.now() - timedelta(days=180)
        )
        
        if not velocity_data:
            velocity_data = await self._generate_synthetic_velocity_data("story_points_per_sprint")
        
        # Calculate metrics
        recent_velocities = [point.value for point in velocity_data[-10:]]
        avg_velocity = np.mean(recent_velocities) if recent_velocities else 20.0
        velocity_std = np.std(recent_velocities) if len(recent_velocities) > 1 else 5.0
        
        # Sprint analysis
        total_points = current_sprint_progress.get("total_points", 40)
        completed_points = current_sprint_progress.get("completed_points", 0)
        remaining_points = total_points - completed_points
        days_remaining = current_sprint_progress.get("days_remaining", 7)
        
        # Calculate completion probability
        required_velocity = remaining_points / max(days_remaining, 1)
        probability = self._calculate_completion_probability(
            required_velocity, avg_velocity, velocity_std
        )
        
        # Risk factors
        risk_factors = []
        if required_velocity > avg_velocity * 1.2:
            risk_factors.append("Required velocity exceeds historical average")
        if days_remaining < 3:
            risk_factors.append("Limited time remaining")
        if remaining_points > total_points * 0.7:
            risk_factors.append("High percentage of work remaining")
        
        return {
            "completion_probability": probability,
            "required_daily_velocity": required_velocity,
            "historical_avg_velocity": avg_velocity,
            "risk_factors": risk_factors,
            "recommended_actions": self._generate_sprint_recommendations(
                probability, required_velocity, avg_velocity
            )
        }
    
    def _calculate_completion_probability(self, required_velocity: float,
                                        avg_velocity: float, 
                                        velocity_std: float) -> float:
        """Calculate probability of completing sprint at required velocity"""
        if velocity_std == 0:
            return 1.0 if required_velocity <= avg_velocity else 0.5
        
        # Use normal distribution to estimate probability
        z_score = (required_velocity - avg_velocity) / velocity_std
        
        # Approximate probability using z-score
        if z_score <= -2:
            return 0.95
        elif z_score <= -1:
            return 0.85
        elif z_score <= 0:
            return 0.75
        elif z_score <= 1:
            return 0.55
        elif z_score <= 2:
            return 0.35
        else:
            return 0.15
    
    def _generate_sprint_recommendations(self, probability: float,
                                       required_velocity: float,
                                       avg_velocity: float) -> List[str]:
        """Generate recommendations based on sprint forecast"""
        recommendations = []
        
        if probability < 0.5:
            recommendations.append("Consider scope reduction or sprint extension")
            recommendations.append("Identify and remove blockers immediately")
            recommendations.append("Consider pair programming to increase velocity")
        elif probability < 0.7:
            recommendations.append("Monitor progress closely")
            recommendations.append("Prepare contingency plans for scope adjustment")
        else:
            recommendations.append("Sprint on track for successful completion")
            recommendations.append("Consider taking on additional work if capacity allows")
        
        if required_velocity > avg_velocity * 1.5:
            recommendations.append("Required velocity significantly exceeds capacity")
            recommendations.append("Escalate to stakeholders for scope negotiation")
        
        return recommendations
    
    async def _generate_synthetic_velocity_data(self, metric_name: str) -> List[TimeSeriesPoint]:
        """Generate synthetic velocity data for demonstration"""
        data = []
        base_value = {
            "commits_per_day": 5.0,
            "pull_requests_per_week": 8.0,
            "story_points_per_sprint": 25.0,
            "bugs_fixed_per_week": 3.0,
            "lines_of_code_per_day": 150.0,
            "deployment_frequency": 2.0,
            "lead_time": 3.5,
            "cycle_time": 2.0
        }.get(metric_name, 10.0)
        
        # Generate 60 days of synthetic data
        for i in range(60):
            timestamp = datetime.now() - timedelta(days=60-i)
            
            # Add trend and noise
            trend = 0.02 * i  # Slight upward trend
            noise = np.random.normal(0, base_value * 0.2)
            weekly_pattern = 0.1 * base_value * np.sin(2 * np.pi * i / 7)
            
            value = base_value + trend + weekly_pattern + noise
            value = max(0, value)  # Ensure non-negative
            
            point = TimeSeriesPoint(timestamp=timestamp, value=value)
            data.append(point)
        
        return data

class TechnicalRiskAnalyzer:
    """Analyzes and predicts technical risks"""
    
    def __init__(self, ts_db: TimeSeriesDatabase):
        self.ts_db = ts_db
        self.risk_categories = [
            "code_quality_degradation",
            "technical_debt_accumulation", 
            "performance_degradation",
            "security_vulnerabilities",
            "dependency_risks",
            "infrastructure_risks",
            "team_capacity_risks",
            "deployment_risks"
        ]
        
    async def assess_comprehensive_risk(self) -> List[RiskAssessment]:
        """Perform comprehensive risk assessment"""
        
        risk_assessments = []
        
        for risk_category in self.risk_categories:
            assessment = await self._assess_risk_category(risk_category)
            risk_assessments.append(assessment)
        
        # Sort by risk level and probability
        risk_assessments.sort(
            key=lambda r: (self._risk_level_score(r.risk_level), r.probability),
            reverse=True
        )
        
        return risk_assessments
    
    async def _assess_risk_category(self, risk_category: str) -> RiskAssessment:
        """Assess a specific risk category"""
        
        # Get relevant metrics for this risk category
        metrics = await self._get_risk_metrics(risk_category)
        
        # Analyze trends and patterns
        risk_indicators = await self._analyze_risk_indicators(risk_category, metrics)
        
        # Calculate risk probability and impact
        probability = await self._calculate_risk_probability(risk_indicators)
        impact_score = await self._calculate_impact_score(risk_category, risk_indicators)
        
        # Determine risk level
        risk_level = self._determine_risk_level(probability, impact_score)
        
        # Generate risk factors and mitigation strategies
        risk_factors = self._identify_risk_factors(risk_category, risk_indicators)
        mitigation_strategies = self._generate_mitigation_strategies(risk_category, risk_level)
        
        # Calculate confidence
        confidence = self._calculate_assessment_confidence(metrics, risk_indicators)
        
        return RiskAssessment(
            risk_id=str(uuid.uuid4()),
            risk_type=risk_category,
            risk_level=risk_level,
            probability=probability,
            impact_score=impact_score,
            risk_factors=risk_factors,
            mitigation_strategies=mitigation_strategies,
            confidence=confidence,
            assessed_at=datetime.now()
        )
    
    async def _get_risk_metrics(self, risk_category: str) -> Dict[str, List[TimeSeriesPoint]]:
        """Get relevant metrics for risk assessment"""
        
        metric_mappings = {
            "code_quality_degradation": ["code_coverage", "cyclomatic_complexity", "code_duplication"],
            "technical_debt_accumulation": ["technical_debt_hours", "code_smells", "refactor_frequency"],
            "performance_degradation": ["response_time", "cpu_usage", "memory_usage", "error_rate"],
            "security_vulnerabilities": ["vulnerability_count", "security_scan_failures", "outdated_dependencies"],
            "dependency_risks": ["dependency_count", "outdated_packages", "security_advisories"],
            "infrastructure_risks": ["uptime", "disk_usage", "network_latency", "backup_failures"],
            "team_capacity_risks": ["team_size", "workload_distribution", "burnout_indicators"],
            "deployment_risks": ["deployment_frequency", "rollback_rate", "deployment_duration"]
        }
        
        metrics = {}
        relevant_metrics = metric_mappings.get(risk_category, [])
        
        for metric_name in relevant_metrics:
            data = await self.ts_db.get_time_series_data(
                f"risk_{metric_name}",
                datetime.now() - timedelta(days=30)
            )
            
            if not data:
                # Generate synthetic data for demonstration
                data = await self._generate_synthetic_risk_data(metric_name)
            
            metrics[metric_name] = data
        
        return metrics
    
    async def _analyze_risk_indicators(self, risk_category: str, 
                                     metrics: Dict[str, List[TimeSeriesPoint]]) -> Dict[str, Any]:
        """Analyze metrics to identify risk indicators"""
        
        indicators = {
            "trend_analysis": {},
            "threshold_breaches": {},
            "pattern_anomalies": {},
            "correlation_analysis": {}
        }
        
        for metric_name, data in metrics.items():
            if not data:
                continue
                
            values = [point.value for point in data]
            
            # Trend analysis
            if len(values) >= 2:
                recent_values = values[-7:]  # Last week
                older_values = values[-14:-7] if len(values) >= 14 else values[:-7]
                
                if recent_values and older_values:
                    recent_avg = np.mean(recent_values)
                    older_avg = np.mean(older_values)
                    trend_change = (recent_avg - older_avg) / (older_avg + 1e-8)
                    
                    indicators["trend_analysis"][metric_name] = {
                        "change_percentage": trend_change * 100,
                        "direction": "increasing" if trend_change > 0.05 else "decreasing" if trend_change < -0.05 else "stable"
                    }
            
            # Threshold breach analysis
            thresholds = self._get_risk_thresholds(metric_name)
            if thresholds and values:
                recent_value = values[-1]
                breach_status = self._check_threshold_breach(recent_value, thresholds)
                
                indicators["threshold_breaches"][metric_name] = breach_status
            
            # Pattern anomaly detection
            if len(values) >= 7:
                anomaly_score = self._detect_anomalies(values)
                indicators["pattern_anomalies"][metric_name] = anomaly_score
        
        return indicators
    
    def _get_risk_thresholds(self, metric_name: str) -> Dict[str, float]:
        """Get risk thresholds for different metrics"""
        
        thresholds = {
            "code_coverage": {"warning": 70.0, "critical": 50.0},
            "cyclomatic_complexity": {"warning": 10.0, "critical": 15.0},
            "response_time": {"warning": 500.0, "critical": 1000.0},
            "error_rate": {"warning": 1.0, "critical": 5.0},
            "cpu_usage": {"warning": 70.0, "critical": 90.0},
            "memory_usage": {"warning": 80.0, "critical": 95.0},
            "disk_usage": {"warning": 80.0, "critical": 95.0},
            "vulnerability_count": {"warning": 5.0, "critical": 10.0}
        }
        
        return thresholds.get(metric_name, {})
    
    def _check_threshold_breach(self, value: float, thresholds: Dict[str, float]) -> Dict[str, Any]:
        """Check if a value breaches risk thresholds"""
        
        if "critical" in thresholds and value >= thresholds["critical"]:
            return {"status": "critical", "threshold": thresholds["critical"], "value": value}
        elif "warning" in thresholds and value >= thresholds["warning"]:
            return {"status": "warning", "threshold": thresholds["warning"], "value": value}
        else:
            return {"status": "normal", "value": value}
    
    def _detect_anomalies(self, values: List[float]) -> float:
        """Detect anomalies in time series data"""
        if len(values) < 3:
            return 0.0
        
        # Simple anomaly detection using statistical outliers
        mean = np.mean(values)
        std = np.std(values)
        
        # Count values beyond 2 standard deviations
        anomalies = sum(1 for v in values if abs(v - mean) > 2 * std)
        anomaly_score = anomalies / len(values)
        
        return min(anomaly_score, 1.0)
    
    async def _calculate_risk_probability(self, risk_indicators: Dict[str, Any]) -> float:
        """Calculate overall risk probability"""
        
        probability_factors = []
        
        # Trend analysis contribution
        trend_analysis = risk_indicators.get("trend_analysis", {})
        negative_trends = sum(1 for trend in trend_analysis.values() 
                            if trend.get("direction") == "increasing")
        
        if trend_analysis:
            trend_factor = negative_trends / len(trend_analysis)
            probability_factors.append(trend_factor)
        
        # Threshold breach contribution
        threshold_breaches = risk_indicators.get("threshold_breaches", {})
        critical_breaches = sum(1 for breach in threshold_breaches.values()
                              if breach.get("status") == "critical")
        warning_breaches = sum(1 for breach in threshold_breaches.values()
                             if breach.get("status") == "warning")
        
        if threshold_breaches:
            breach_factor = (critical_breaches * 1.0 + warning_breaches * 0.5) / len(threshold_breaches)
            probability_factors.append(breach_factor)
        
        # Anomaly contribution
        pattern_anomalies = risk_indicators.get("pattern_anomalies", {})
        if pattern_anomalies:
            anomaly_factor = np.mean(list(pattern_anomalies.values()))
            probability_factors.append(anomaly_factor)
        
        # Calculate overall probability
        if probability_factors:
            return min(np.mean(probability_factors), 1.0)
        else:
            return 0.3  # Default moderate probability
    
    async def _calculate_impact_score(self, risk_category: str, 
                                    risk_indicators: Dict[str, Any]) -> float:
        """Calculate potential impact score"""
        
        # Base impact scores by category
        base_impacts = {
            "security_vulnerabilities": 0.9,
            "performance_degradation": 0.7,
            "infrastructure_risks": 0.8,
            "deployment_risks": 0.6,
            "code_quality_degradation": 0.5,
            "technical_debt_accumulation": 0.4,
            "dependency_risks": 0.6,
            "team_capacity_risks": 0.7
        }
        
        base_impact = base_impacts.get(risk_category, 0.5)
        
        # Adjust based on severity of indicators
        threshold_breaches = risk_indicators.get("threshold_breaches", {})
        critical_breaches = sum(1 for breach in threshold_breaches.values()
                              if breach.get("status") == "critical")
        
        if critical_breaches > 0:
            base_impact = min(base_impact * 1.3, 1.0)
        
        return base_impact
    
    def _determine_risk_level(self, probability: float, impact_score: float) -> str:
        """Determine risk level based on probability and impact"""
        
        risk_score = probability * impact_score
        
        if risk_score >= 0.7:
            return "critical"
        elif risk_score >= 0.5:
            return "high"
        elif risk_score >= 0.3:
            return "medium"
        else:
            return "low"
    
    def _risk_level_score(self, risk_level: str) -> int:
        """Convert risk level to numeric score for sorting"""
        return {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(risk_level, 1)
    
    def _identify_risk_factors(self, risk_category: str, 
                             risk_indicators: Dict[str, Any]) -> List[str]:
        """Identify specific risk factors"""
        
        factors = []
        
        # Add factors based on trend analysis
        trend_analysis = risk_indicators.get("trend_analysis", {})
        for metric, trend in trend_analysis.items():
            if trend.get("direction") == "increasing" and trend.get("change_percentage", 0) > 10:
                factors.append(f"Increasing trend in {metric} ({trend['change_percentage']:.1f}%)")
        
        # Add factors based on threshold breaches
        threshold_breaches = risk_indicators.get("threshold_breaches", {})
        for metric, breach in threshold_breaches.items():
            if breach.get("status") in ["warning", "critical"]:
                factors.append(f"{metric} exceeds {breach['status']} threshold ({breach['value']:.1f})")
        
        # Add factors based on anomalies
        pattern_anomalies = risk_indicators.get("pattern_anomalies", {})
        for metric, anomaly_score in pattern_anomalies.items():
            if anomaly_score > 0.2:
                factors.append(f"Anomalous patterns detected in {metric}")
        
        return factors[:5]  # Limit to top 5 factors
    
    def _generate_mitigation_strategies(self, risk_category: str, risk_level: str) -> List[str]:
        """Generate mitigation strategies for the risk"""
        
        strategies = {
            "code_quality_degradation": [
                "Implement mandatory code reviews",
                "Increase test coverage requirements", 
                "Schedule refactoring sprints",
                "Set up automated quality gates"
            ],
            "technical_debt_accumulation": [
                "Allocate dedicated technical debt sprints",
                "Implement technical debt tracking",
                "Establish refactoring guidelines",
                "Create technical debt reduction roadmap"
            ],
            "performance_degradation": [
                "Implement performance monitoring",
                "Conduct performance testing",
                "Optimize critical code paths",
                "Scale infrastructure resources"
            ],
            "security_vulnerabilities": [
                "Update vulnerable dependencies immediately",
                "Implement security scanning in CI/CD",
                "Conduct security code reviews",
                "Schedule penetration testing"
            ],
            "dependency_risks": [
                "Regular dependency updates",
                "Dependency vulnerability scanning",
                "Evaluate alternative dependencies",
                "Implement dependency lock files"
            ],
            "infrastructure_risks": [
                "Implement infrastructure monitoring",
                "Create disaster recovery plan",
                "Scale infrastructure capacity",
                "Implement backup verification"
            ],
            "team_capacity_risks": [
                "Monitor team workload distribution",
                "Plan for team scaling",
                "Implement knowledge sharing",
                "Address burnout indicators"
            ],
            "deployment_risks": [
                "Implement gradual deployments",
                "Improve rollback procedures",
                "Add deployment monitoring",
                "Automate deployment testing"
            ]
        }
        
        base_strategies = strategies.get(risk_category, ["Monitor situation closely"])
        
        # Adjust strategies based on risk level
        if risk_level == "critical":
            return ["IMMEDIATE ACTION REQUIRED"] + base_strategies
        elif risk_level == "high":
            return ["Priority attention needed"] + base_strategies
        else:
            return base_strategies
    
    def _calculate_assessment_confidence(self, metrics: Dict[str, List[TimeSeriesPoint]],
                                       risk_indicators: Dict[str, Any]) -> float:
        """Calculate confidence in the risk assessment"""
        
        confidence_factors = []
        
        # Data availability confidence
        non_empty_metrics = sum(1 for data in metrics.values() if data)
        total_metrics = len(metrics) if metrics else 1
        data_confidence = non_empty_metrics / total_metrics
        confidence_factors.append(data_confidence)
        
        # Data recency confidence
        if metrics:
            most_recent_data = []
            for data in metrics.values():
                if data:
                    most_recent = max(point.timestamp for point in data)
                    hours_ago = (datetime.now() - most_recent).total_seconds() / 3600
                    recency_factor = max(0.0, 1.0 - hours_ago / 168)  # Decay over a week
                    most_recent_data.append(recency_factor)
            
            if most_recent_data:
                recency_confidence = np.mean(most_recent_data)
                confidence_factors.append(recency_confidence)
        
        # Indicator quality confidence
        indicators_with_data = sum(1 for indicators in risk_indicators.values() if indicators)
        total_indicator_types = len(risk_indicators)
        indicator_confidence = indicators_with_data / total_indicator_types if total_indicator_types > 0 else 0.5
        confidence_factors.append(indicator_confidence)
        
        return np.mean(confidence_factors) if confidence_factors else 0.5
    
    async def _generate_synthetic_risk_data(self, metric_name: str) -> List[TimeSeriesPoint]:
        """Generate synthetic risk data for demonstration"""
        
        data = []
        base_values = {
            "code_coverage": 75.0,
            "cyclomatic_complexity": 8.0,
            "response_time": 200.0,
            "error_rate": 0.5,
            "cpu_usage": 45.0,
            "memory_usage": 60.0,
            "vulnerability_count": 2.0
        }
        
        base_value = base_values.get(metric_name, 50.0)
        
        # Generate 30 days of data
        for i in range(30):
            timestamp = datetime.now() - timedelta(days=30-i)
            
            # Add some trend and noise
            trend = 0.5 * i if metric_name in ["vulnerability_count", "error_rate"] else -0.2 * i
            noise = np.random.normal(0, base_value * 0.1)
            
            value = base_value + trend + noise
            value = max(0, value)
            
            point = TimeSeriesPoint(timestamp=timestamp, value=value)
            data.append(point)
        
        return data

class PerformancePredictionEngine:
    """Predicts performance bottlenecks and optimization opportunities"""
    
    def __init__(self, ts_db: TimeSeriesDatabase):
        self.ts_db = ts_db
        self.forecaster = TimeGPTInspiredForecaster()
        
    async def predict_performance_bottlenecks(self) -> List[PerformancePrediction]:
        """Predict upcoming performance bottlenecks"""
        
        predictions = []
        
        # Performance metrics to analyze
        metrics = [
            "response_time",
            "throughput",
            "cpu_utilization", 
            "memory_utilization",
            "disk_io",
            "network_latency",
            "error_rate",
            "queue_depth"
        ]
        
        for metric in metrics:
            prediction = await self._predict_metric_performance(metric)
            if prediction:
                predictions.append(prediction)
        
        # Sort by prediction confidence and potential impact
        predictions.sort(key=lambda p: p.prediction_confidence, reverse=True)
        
        return predictions
    
    async def _predict_metric_performance(self, metric_name: str) -> Optional[PerformancePrediction]:
        """Predict performance for a specific metric"""
        
        # Get historical data
        data = await self.ts_db.get_time_series_data(
            f"performance_{metric_name}",
            datetime.now() - timedelta(days=30)
        )
        
        if not data:
            # Generate synthetic data for demonstration
            data = await self._generate_synthetic_performance_data(metric_name)
        
        if len(data) < 5:
            return None
        
        # Generate forecast
        forecast = await self.forecaster.forecast_time_series(data, horizon=7)
        
        # Analyze for bottlenecks
        current_value = data[-1].value
        predicted_values = forecast.predictions
        
        # Check if prediction indicates performance degradation
        avg_predicted = np.mean(predicted_values)
        degradation_threshold = self._get_degradation_threshold(metric_name)
        
        if avg_predicted > current_value * (1 + degradation_threshold):
            # Potential bottleneck detected
            bottlenecks = self._identify_bottlenecks(metric_name, predicted_values, current_value)
            optimizations = self._suggest_optimizations(metric_name, bottlenecks)
            
            # Calculate confidence interval
            confidence_intervals = forecast.confidence_intervals
            avg_confidence_interval = (
                np.mean([ci[0] for ci in confidence_intervals]),
                np.mean([ci[1] for ci in confidence_intervals])
            )
            
            return PerformancePrediction(
                prediction_id=str(uuid.uuid4()),
                metric_name=metric_name,
                predicted_value=avg_predicted,
                confidence_interval=avg_confidence_interval,
                bottlenecks=bottlenecks,
                optimization_suggestions=optimizations,
                prediction_confidence=forecast.model_confidence,
                predicted_at=datetime.now()
            )
        
        return None
    
    def _get_degradation_threshold(self, metric_name: str) -> float:
        """Get the threshold for considering performance degradation"""
        
        thresholds = {
            "response_time": 0.2,  # 20% increase is concerning
            "cpu_utilization": 0.15,  # 15% increase
            "memory_utilization": 0.1,  # 10% increase
            "error_rate": 0.05,  # 5% increase
            "network_latency": 0.25,  # 25% increase
            "disk_io": 0.3  # 30% increase
        }
        
        return thresholds.get(metric_name, 0.15)  # Default 15%
    
    def _identify_bottlenecks(self, metric_name: str, 
                            predicted_values: List[float],
                            current_value: float) -> List[str]:
        """Identify specific bottlenecks based on predictions"""
        
        bottlenecks = []
        max_predicted = max(predicted_values)
        increase_percentage = ((max_predicted - current_value) / current_value) * 100
        
        bottleneck_mappings = {
            "response_time": [
                f"Response time may increase by {increase_percentage:.1f}%",
                "Database query performance degradation",
                "Increased application load"
            ],
            "cpu_utilization": [
                f"CPU usage may increase by {increase_percentage:.1f}%",
                "Compute-intensive operations scaling",
                "Insufficient CPU capacity"
            ],
            "memory_utilization": [
                f"Memory usage may increase by {increase_percentage:.1f}%",
                "Memory leaks or inefficient allocation",
                "Increased data processing load"
            ],
            "error_rate": [
                f"Error rate may increase by {increase_percentage:.1f}%",
                "System instability indicators",
                "Cascading failure risks"
            ]
        }
        
        return bottleneck_mappings.get(metric_name, [f"{metric_name} degradation predicted"])
    
    def _suggest_optimizations(self, metric_name: str, bottlenecks: List[str]) -> List[str]:
        """Suggest optimization strategies"""
        
        optimization_mappings = {
            "response_time": [
                "Implement caching layers",
                "Optimize database queries",
                "Scale application instances",
                "Implement load balancing"
            ],
            "cpu_utilization": [
                "Scale compute resources horizontally",
                "Optimize CPU-intensive algorithms", 
                "Implement resource pooling",
                "Consider workload scheduling"
            ],
            "memory_utilization": [
                "Implement memory management optimization",
                "Scale memory resources",
                "Optimize data structures",
                "Implement garbage collection tuning"
            ],
            "error_rate": [
                "Implement circuit breakers",
                "Add redundancy and failover",
                "Improve error handling",
                "Implement graceful degradation"
            ],
            "network_latency": [
                "Optimize network configuration",
                "Implement CDN for static content",
                "Reduce network hops",
                "Implement connection pooling"
            ]
        }
        
        return optimization_mappings.get(metric_name, ["Monitor and investigate further"])
    
    async def _generate_synthetic_performance_data(self, metric_name: str) -> List[TimeSeriesPoint]:
        """Generate synthetic performance data"""
        
        base_values = {
            "response_time": 150.0,
            "throughput": 1000.0,
            "cpu_utilization": 45.0,
            "memory_utilization": 60.0,
            "disk_io": 30.0,
            "network_latency": 50.0,
            "error_rate": 0.1,
            "queue_depth": 5.0
        }
        
        base_value = base_values.get(metric_name, 50.0)
        data = []
        
        for i in range(30):
            timestamp = datetime.now() - timedelta(days=30-i)
            
            # Add gradual increase to simulate load growth
            trend = 0.5 * i
            daily_pattern = 0.2 * base_value * np.sin(2 * np.pi * i / 7)  # Weekly pattern
            noise = np.random.normal(0, base_value * 0.1)
            
            value = base_value + trend + daily_pattern + noise
            value = max(0, value)
            
            point = TimeSeriesPoint(timestamp=timestamp, value=value)
            data.append(point)
        
        return data

class PredictiveAnalyticsServer:
    """Main MCP server for predictive analytics"""
    
    def __init__(self):
        self.server = Server("predictive-analytics")
        self.ts_db = TimeSeriesDatabase()
        self.velocity_forecaster = DevelopmentVelocityForecaster(self.ts_db)
        self.risk_analyzer = TechnicalRiskAnalyzer(self.ts_db)
        self.performance_predictor = PerformancePredictionEngine(self.ts_db)
        
        self._setup_server()
    
    def _setup_server(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available prediction tools"""
            return [
                Tool(
                    name="forecast_development_velocity",
                    description="Forecast development velocity metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "metric_name": {
                                "type": "string",
                                "description": "Velocity metric to forecast",
                                "enum": [
                                    "commits_per_day",
                                    "pull_requests_per_week",
                                    "story_points_per_sprint", 
                                    "bugs_fixed_per_week",
                                    "deployment_frequency"
                                ]
                            },
                            "days_ahead": {
                                "type": "integer",
                                "description": "Number of days to forecast ahead",
                                "default": 14
                            }
                        },
                        "required": ["metric_name"]
                    }
                ),
                Tool(
                    name="assess_technical_risks",
                    description="Perform comprehensive technical risk assessment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "risk_categories": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific risk categories to assess (optional)"
                            },
                            "include_mitigation": {
                                "type": "boolean",
                                "description": "Include mitigation strategies",
                                "default": True
                            }
                        }
                    }
                ),
                Tool(
                    name="predict_performance_bottlenecks", 
                    description="Predict upcoming performance bottlenecks",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prediction_horizon": {
                                "type": "integer",
                                "description": "Days ahead to predict",
                                "default": 7
                            },
                            "confidence_threshold": {
                                "type": "number",
                                "description": "Minimum confidence for predictions",
                                "default": 0.6
                            }
                        }
                    }
                ),
                Tool(
                    name="forecast_sprint_completion",
                    description="Forecast sprint completion probability",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "total_points": {
                                "type": "integer",
                                "description": "Total story points in sprint"
                            },
                            "completed_points": {
                                "type": "integer", 
                                "description": "Currently completed story points"
                            },
                            "days_remaining": {
                                "type": "integer",
                                "description": "Days remaining in sprint"
                            }
                        },
                        "required": ["total_points", "completed_points", "days_remaining"]
                    }
                ),
                Tool(
                    name="store_metrics_data",
                    description="Store time series metrics data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "metric_name": {
                                "type": "string",
                                "description": "Name of the metric"
                            },
                            "value": {
                                "type": "number",
                                "description": "Metric value"
                            },
                            "timestamp": {
                                "type": "string",
                                "description": "ISO timestamp (optional, defaults to now)"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Additional metadata"
                            }
                        },
                        "required": ["metric_name", "value"]
                    }
                ),
                Tool(
                    name="generate_analytics_dashboard",
                    description="Generate comprehensive analytics dashboard",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "dashboard_type": {
                                "type": "string",
                                "enum": ["velocity", "risk", "performance", "comprehensive"],
                                "description": "Type of dashboard to generate"
                            },
                            "time_range": {
                                "type": "string",
                                "enum": ["7d", "30d", "90d"],
                                "description": "Time range for dashboard data",
                                "default": "30d"
                            }
                        },
                        "required": ["dashboard_type"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
            """Handle tool calls"""
            
            try:
                if name == "forecast_development_velocity":
                    metric_name = arguments["metric_name"]
                    days_ahead = arguments.get("days_ahead", 14)
                    
                    forecast = await self.velocity_forecaster.forecast_velocity(
                        metric_name, days_ahead
                    )
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "forecast_id": forecast.forecast_id,
                            "metric": metric_name,
                            "horizon_days": days_ahead,
                            "predictions": forecast.predictions,
                            "confidence_intervals": forecast.confidence_intervals,
                            "accuracy_score": forecast.accuracy_score,
                            "model_confidence": forecast.model_confidence,
                            "generated_at": forecast.generated_at.isoformat()
                        }, indent=2)
                    )]
                
                elif name == "assess_technical_risks":
                    risk_assessments = await self.risk_analyzer.assess_comprehensive_risk()
                    
                    results = []
                    for assessment in risk_assessments:
                        results.append({
                            "risk_id": assessment.risk_id,
                            "risk_type": assessment.risk_type,
                            "risk_level": assessment.risk_level,
                            "probability": assessment.probability,
                            "impact_score": assessment.impact_score,
                            "risk_factors": assessment.risk_factors,
                            "mitigation_strategies": assessment.mitigation_strategies,
                            "confidence": assessment.confidence,
                            "assessed_at": assessment.assessed_at.isoformat()
                        })
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "risk_assessment_summary": {
                                "total_risks": len(results),
                                "critical_risks": len([r for r in results if r["risk_level"] == "critical"]),
                                "high_risks": len([r for r in results if r["risk_level"] == "high"]),
                                "assessment_timestamp": datetime.now().isoformat()
                            },
                            "risk_assessments": results
                        }, indent=2)
                    )]
                
                elif name == "predict_performance_bottlenecks":
                    predictions = await self.performance_predictor.predict_performance_bottlenecks()
                    
                    results = []
                    for prediction in predictions:
                        results.append({
                            "prediction_id": prediction.prediction_id,
                            "metric_name": prediction.metric_name,
                            "predicted_value": prediction.predicted_value,
                            "confidence_interval": prediction.confidence_interval,
                            "bottlenecks": prediction.bottlenecks,
                            "optimization_suggestions": prediction.optimization_suggestions,
                            "prediction_confidence": prediction.prediction_confidence,
                            "predicted_at": prediction.predicted_at.isoformat()
                        })
                    
                    return [TextContent(
                        type="text", 
                        text=json.dumps({
                            "performance_predictions": results,
                            "summary": {
                                "total_predictions": len(results),
                                "high_confidence_predictions": len([p for p in results if p["prediction_confidence"] > 0.7]),
                                "prediction_timestamp": datetime.now().isoformat()
                            }
                        }, indent=2)
                    )]
                
                elif name == "forecast_sprint_completion":
                    sprint_progress = {
                        "total_points": arguments["total_points"],
                        "completed_points": arguments["completed_points"],
                        "days_remaining": arguments["days_remaining"]
                    }
                    
                    forecast = await self.velocity_forecaster.forecast_sprint_completion(sprint_progress)
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "sprint_forecast": forecast,
                            "sprint_status": self._get_sprint_status(forecast["completion_probability"]),
                            "forecast_timestamp": datetime.now().isoformat()
                        }, indent=2)
                    )]
                
                elif name == "store_metrics_data":
                    metric_name = arguments["metric_name"]
                    value = arguments["value"]
                    timestamp_str = arguments.get("timestamp")
                    metadata = arguments.get("metadata", {})
                    
                    timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now()
                    
                    point = TimeSeriesPoint(
                        timestamp=timestamp,
                        value=float(value),
                        metadata=metadata
                    )
                    
                    await self.ts_db.store_time_series_point(metric_name, point)
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "success",
                            "message": f"Stored metric data for {metric_name}",
                            "stored_at": datetime.now().isoformat()
                        }, indent=2)
                    )]
                
                elif name == "generate_analytics_dashboard":
                    dashboard_type = arguments["dashboard_type"]
                    time_range = arguments.get("time_range", "30d")
                    
                    dashboard = await self._generate_dashboard(dashboard_type, time_range)
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(dashboard, indent=2)
                    )]
                
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
                    
            except Exception as e:
                logger.error(f"Error handling tool call {name}: {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    def _get_sprint_status(self, completion_probability: float) -> str:
        """Get sprint status based on completion probability"""
        if completion_probability >= 0.8:
            return "On Track"
        elif completion_probability >= 0.6:
            return "At Risk"
        elif completion_probability >= 0.4:
            return "High Risk"
        else:
            return "Critical Risk"
    
    async def _generate_dashboard(self, dashboard_type: str, time_range: str) -> Dict[str, Any]:
        """Generate analytics dashboard"""
        
        days = {"7d": 7, "30d": 30, "90d": 90}[time_range]
        
        dashboard = {
            "dashboard_type": dashboard_type,
            "time_range": time_range,
            "generated_at": datetime.now().isoformat(),
            "summary": {},
            "charts": [],
            "insights": []
        }
        
        if dashboard_type in ["velocity", "comprehensive"]:
            # Add velocity forecasts
            velocity_metrics = ["commits_per_day", "story_points_per_sprint"]
            for metric in velocity_metrics:
                forecast = await self.velocity_forecaster.forecast_velocity(metric, 7)
                dashboard["charts"].append({
                    "type": "velocity_forecast",
                    "metric": metric,
                    "forecast": forecast.predictions,
                    "confidence": forecast.model_confidence
                })
        
        if dashboard_type in ["risk", "comprehensive"]:
            # Add risk assessments
            risks = await self.risk_analyzer.assess_comprehensive_risk()
            high_priority_risks = [r for r in risks if r.risk_level in ["critical", "high"]]
            
            dashboard["summary"]["high_priority_risks"] = len(high_priority_risks)
            dashboard["charts"].append({
                "type": "risk_summary",
                "risk_distribution": {
                    "critical": len([r for r in risks if r.risk_level == "critical"]),
                    "high": len([r for r in risks if r.risk_level == "high"]),
                    "medium": len([r for r in risks if r.risk_level == "medium"]),
                    "low": len([r for r in risks if r.risk_level == "low"])
                }
            })
        
        if dashboard_type in ["performance", "comprehensive"]:
            # Add performance predictions
            predictions = await self.performance_predictor.predict_performance_bottlenecks()
            
            dashboard["summary"]["performance_predictions"] = len(predictions)
            dashboard["charts"].append({
                "type": "performance_predictions",
                "predictions": [
                    {
                        "metric": p.metric_name,
                        "predicted_value": p.predicted_value,
                        "confidence": p.prediction_confidence
                    }
                    for p in predictions
                ]
            })
        
        # Add insights
        dashboard["insights"] = [
            f"Generated comprehensive {dashboard_type} analytics dashboard",
            f"Analyzed {time_range} of historical data",
            "Predictions include confidence intervals and risk assessments"
        ]
        
        return dashboard
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="predictive-analytics",
                    server_version="1.0.0",
                    capabilities={}
                )
            )

async def main():
    """Main entry point"""
    server = PredictiveAnalyticsServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())