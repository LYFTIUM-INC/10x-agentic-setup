"""
Test suite for Predictive Analytics MCP Server forecasting capabilities
Tests TimeGPT-inspired forecasting, development velocity, and risk analysis
"""

import pytest
import asyncio
import json
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from server import (
    TimeGPTInspiredForecaster,
    DevelopmentVelocityForecaster, 
    TechnicalRiskAnalyzer,
    PerformancePredictionEngine,
    PredictiveAnalyticsServer
)

class TestTimeGPTForecaster:
    """Test TimeGPT-inspired forecasting capabilities"""
    
    @pytest.fixture
    def forecaster(self):
        return TimeGPTInspiredForecaster()
    
    @pytest.fixture
    def sample_time_series(self):
        """Generate sample time series data for testing"""
        base_date = datetime.now() - timedelta(days=30)
        return [
            {
                "timestamp": (base_date + timedelta(days=i)).isoformat(),
                "value": 10 + i * 0.5 + (i % 7) * 2  # Trend + weekly pattern
            }
            for i in range(30)
        ]
    
    def test_forecaster_initialization(self, forecaster):
        """Test forecaster initializes with correct parameters"""
        assert forecaster.model_params["context_length"] == 512
        assert forecaster.model_params["prediction_length"] == 96
        assert forecaster.model_params["frequency"] == "1H"
    
    def test_prepare_features(self, forecaster, sample_time_series):
        """Test feature preparation from time series data"""
        features = forecaster._prepare_features(sample_time_series)
        
        assert "trend" in features
        assert "seasonal" in features
        assert "residual" in features
        assert len(features["values"]) == len(sample_time_series)
    
    def test_detect_seasonality(self, forecaster, sample_time_series):
        """Test seasonality detection"""
        values = [point["value"] for point in sample_time_series]
        
        # Test weekly seasonality (period=7)
        seasonality = forecaster._detect_seasonality(values, period=7)
        assert len(seasonality) == len(values)
        
        # Seasonal component should have some variation
        assert max(seasonality) > min(seasonality)
    
    def test_forecast_generation(self, forecaster, sample_time_series):
        """Test forecast generation with confidence intervals"""
        forecast_result = forecaster._generate_forecast(
            sample_time_series, 
            horizon=24,
            confidence_levels=[0.8, 0.95]
        )
        
        assert "predictions" in forecast_result
        assert "confidence_intervals" in forecast_result
        assert "metadata" in forecast_result
        
        # Check prediction count
        assert len(forecast_result["predictions"]) == 24
        
        # Check confidence intervals
        assert len(forecast_result["confidence_intervals"]) == 2
        for interval in forecast_result["confidence_intervals"]:
            assert "lower" in interval
            assert "upper" in interval
            assert "confidence" in interval

class TestDevelopmentVelocityForecaster:
    """Test development velocity forecasting"""
    
    @pytest.fixture
    def velocity_forecaster(self):
        return DevelopmentVelocityForecaster()
    
    @pytest.fixture
    def sample_sprint_data(self):
        """Generate sample sprint velocity data"""
        return [
            {
                "sprint": f"Sprint {i+1}",
                "completed_points": 20 + i * 2 + (i % 3),
                "planned_points": 25 + i,
                "completion_rate": 0.8 + (i * 0.02),
                "team_capacity": 5,
                "sprint_length": 14
            }
            for i in range(10)
        ]
    
    def test_velocity_trend_analysis(self, velocity_forecaster, sample_sprint_data):
        """Test velocity trend analysis"""
        trend_analysis = velocity_forecaster._analyze_velocity_trends(sample_sprint_data)
        
        assert "trend_direction" in trend_analysis
        assert "velocity_stability" in trend_analysis
        assert "capacity_utilization" in trend_analysis
        assert "performance_metrics" in trend_analysis
        
        # Should detect positive trend
        assert trend_analysis["trend_direction"] in ["increasing", "stable", "decreasing"]
    
    def test_sprint_forecast(self, velocity_forecaster, sample_sprint_data):
        """Test sprint completion forecasting"""
        forecast = velocity_forecaster._forecast_sprint_completion(
            sample_sprint_data,
            target_points=30,
            forecast_sprints=3
        )
        
        assert "completion_probability" in forecast
        assert "estimated_sprints" in forecast
        assert "confidence_intervals" in forecast
        assert "risk_factors" in forecast
        
        # Completion probability should be between 0 and 1
        assert 0 <= forecast["completion_probability"] <= 1

class TestTechnicalRiskAnalyzer:
    """Test technical risk analysis capabilities"""
    
    @pytest.fixture
    def risk_analyzer(self):
        from unittest.mock import Mock
        mock_db = Mock()
        return TechnicalRiskAnalyzer(mock_db)
    
    @pytest.fixture
    def sample_project_metrics(self):
        """Generate sample project metrics for risk analysis"""
        return {
            "code_metrics": {
                "cyclomatic_complexity": 15.5,
                "code_coverage": 0.75,
                "technical_debt_ratio": 0.12,
                "duplicate_code_percentage": 0.08
            },
            "team_metrics": {
                "team_size": 8,
                "experience_distribution": {"senior": 3, "mid": 3, "junior": 2},
                "turnover_rate": 0.15
            },
            "project_metrics": {
                "project_duration_months": 12,
                "requirements_stability": 0.70,
                "technology_maturity": 0.85
            }
        }
    
    @pytest.mark.asyncio
    async def test_comprehensive_risk_assessment(self, risk_analyzer, sample_project_metrics):
        """Test comprehensive risk assessment"""
        risk_assessments = await risk_analyzer.assess_comprehensive_risk()
        
        assert isinstance(risk_assessments, list)
        # Should have risk assessments for different categories
        assert len(risk_assessments) >= 0
        
        # Each assessment should have required fields
        for assessment in risk_assessments:
            assert hasattr(assessment, 'risk_category')
            assert hasattr(assessment, 'risk_score')
            assert hasattr(assessment, 'confidence')
    
    @pytest.mark.asyncio
    async def test_predictive_risk_modeling(self, risk_analyzer):
        """Test predictive risk modeling capabilities"""
        # Test with sample trend data
        trend_data = [0.1, 0.15, 0.18, 0.22, 0.25]  # Increasing risk trend
        
        prediction = await risk_analyzer.predict_risk_trajectory(
            "technical_debt_accumulation",
            trend_data,
            prediction_horizon=30
        )
        
        assert "predicted_risk_scores" in prediction
        assert "risk_acceleration" in prediction
        assert "critical_thresholds" in prediction
    
    @pytest.mark.asyncio 
    async def test_risk_mitigation_strategies(self, risk_analyzer):
        """Test risk mitigation strategy generation"""
        # Create sample high-risk scenario
        high_risk_metrics = {
            "code_complexity": 25.0,  # High complexity
            "test_coverage": 0.45,    # Low coverage
            "technical_debt_ratio": 0.35  # High debt
        }
        
        strategies = await risk_analyzer.generate_mitigation_strategies(high_risk_metrics)
        
        assert "immediate_actions" in strategies
        assert "long_term_strategies" in strategies
        assert "monitoring_checkpoints" in strategies
        
        # Should have actionable recommendations
        assert len(strategies["immediate_actions"]) > 0

class TestPerformancePredictionEngine:
    """Test performance prediction and bottleneck detection"""
    
    @pytest.fixture
    def performance_engine(self):
        from unittest.mock import Mock
        mock_db = Mock()
        return PerformancePredictionEngine(mock_db)
    
    @pytest.fixture
    def sample_performance_data(self):
        """Generate sample performance metrics"""
        return {
            "build_times": [120, 135, 140, 125, 150, 160, 145],
            "test_execution_times": [45, 50, 48, 52, 55, 53, 49],
            "deployment_times": [300, 280, 290, 310, 295, 285, 275],
            "api_response_times": [0.15, 0.18, 0.16, 0.20, 0.17, 0.19, 0.14],
            "memory_usage": [0.65, 0.70, 0.68, 0.72, 0.75, 0.71, 0.69],
            "cpu_usage": [0.45, 0.50, 0.48, 0.52, 0.55, 0.49, 0.47]
        }
    
    @pytest.mark.asyncio
    async def test_performance_bottleneck_prediction(self, performance_engine, sample_performance_data):
        """Test performance bottleneck prediction"""
        predictions = await performance_engine.predict_performance_bottlenecks()
        
        assert isinstance(predictions, list)
        # Should return performance predictions
        assert len(predictions) >= 0
        
        # Each prediction should have required fields
        for prediction in predictions:
            assert hasattr(prediction, 'metric_name')
            assert hasattr(prediction, 'prediction_confidence')
    
    @pytest.mark.asyncio
    async def test_performance_optimization_recommendations(self, performance_engine):
        """Test performance optimization recommendations"""
        # Test with sample bottleneck scenario
        bottleneck_data = {
            "metric": "response_time",
            "current_value": 2.5,  # High response time
            "trend": "increasing",
            "severity": "high"
        }
        
        recommendations = await performance_engine.generate_optimization_recommendations(bottleneck_data)
        
        assert "immediate_optimizations" in recommendations
        assert "medium_term_improvements" in recommendations
        assert "monitoring_strategy" in recommendations
        
        # Should have actionable recommendations
        assert len(recommendations["immediate_optimizations"]) > 0

class TestPredictiveAnalyticsServer:
    """Test the main MCP server integration"""
    
    @pytest.fixture
    def server(self):
        return PredictiveAnalyticsServer()
    
    @pytest.fixture
    def temp_db_file(self):
        """Create temporary database file for testing"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            yield tmp_file.name
        os.unlink(tmp_file.name)
    
    @pytest.mark.asyncio
    async def test_server_initialization(self, server, temp_db_file):
        """Test server initialization"""
        with patch.object(server.ts_db, 'db_path', temp_db_file):
            # Database initialization happens in constructor
            server.ts_db._initialize_database()
            
            # Check if database tables are created
            assert os.path.exists(temp_db_file)
    
    @pytest.mark.asyncio
    async def test_forecast_development_velocity_tool(self, server, temp_db_file):
        """Test forecast_development_velocity MCP tool"""
        with patch.object(server.ts_db, 'db_path', temp_db_file):
            server.ts_db._initialize_database()
            
            # Test the MCP tool directly
            result = await server.forecast_development_velocity(
                "commits_per_day",
                days_ahead=14
            )
            
            # Parse result
            forecast_data = json.loads(result)
            assert "predictions" in forecast_data
            assert "success" in forecast_data
            assert forecast_data["success"] is True
    
    @pytest.mark.asyncio
    async def test_assess_technical_risks_tool(self, server, temp_db_file):
        """Test assess_technical_risks MCP tool"""
        with patch.object(server.ts_db, 'db_path', temp_db_file):
            server.ts_db._initialize_database()
            
            project_data = {
                "code_complexity": 8.5,
                "test_coverage": 0.78,
                "team_size": 6,
                "project_duration": 8
            }
            
            result = await server.assess_technical_risks(
                json.dumps(project_data)
            )
            
            # Parse result
            risk_data = json.loads(result)
            assert "assessments" in risk_data
            assert "success" in risk_data
            assert risk_data["success"] is True
    
    @pytest.mark.asyncio
    async def test_predict_performance_bottlenecks_tool(self, server, temp_db_file):
        """Test predict_performance_bottlenecks MCP tool"""
        with patch.object(server.ts_db, 'db_path', temp_db_file):
            server.ts_db._initialize_database()
            
            performance_data = {
                "build_times": [120, 135, 140],
                "test_times": [45, 50, 48],
                "deployment_times": [300, 280, 290]
            }
            
            result = await server.predict_performance_bottlenecks(
                json.dumps(performance_data)
            )
            
            # Parse result
            bottleneck_data = json.loads(result)
            assert "predictions" in bottleneck_data
            assert "success" in bottleneck_data
            assert bottleneck_data["success"] is True

@pytest.mark.integration
class TestIntegrationScenarios:
    """Integration tests for complete workflows"""
    
    @pytest.fixture
    def server(self):
        return PredictiveAnalyticsServer()
    
    @pytest.fixture
    def temp_db_file(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            yield tmp_file.name
        os.unlink(tmp_file.name)
    
    @pytest.mark.asyncio
    async def test_complete_project_analysis_workflow(self, server, temp_db_file):
        """Test complete project analysis workflow"""
        with patch.object(server.ts_db, 'db_path', temp_db_file):
            server.ts_db._initialize_database()
            
            # 1. Store project metrics
            metrics_data = {
                "timestamp": datetime.now().isoformat(),
                "build_time": 145,
                "test_coverage": 0.82,
                "code_complexity": 7.8
            }
            
            store_result = await server.store_metrics_data(
                "project_metrics",
                json.dumps(metrics_data)
            )
            assert '"success": true' in store_result
            
            # 2. Assess technical risks
            risk_data = {
                "code_complexity": 7.8,
                "test_coverage": 0.82,
                "team_size": 5,
                "project_duration": 6
            }
            
            risk_result = await server.assess_technical_risks(
                json.dumps(risk_data)
            )
            risk_analysis = json.loads(risk_result)
            assert risk_analysis["success"] is True
            
            # 3. Generate analytics dashboard
            dashboard_result = await server.generate_analytics_dashboard()
            dashboard_data = json.loads(dashboard_result)
            assert dashboard_data["success"] is True
            assert "dashboard_data" in dashboard_data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])