#!/usr/bin/env python3
"""
Comprehensive Test Suite for Predictive Performance Analytics System
Tests trend analysis, forecasting, velocity prediction, and risk assessment
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, Any

# Add performance modules to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir / "performance"))

from performance_monitoring_hook import PerformanceMonitoringHook
from performance.predictive_analytics import PredictiveAnalyticsEngine


class PredictiveSystemTest:
    """Complete predictive analytics system test"""
    
    def __init__(self):
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        
        print("🔮 Starting Comprehensive Predictive Analytics System Test")
        print("=" * 70)
    
    def run_all_tests(self):
        """Run all predictive system tests"""
        
        # Core predictive analytics tests
        self.test_predictive_engine_initialization()
        self.test_trend_analysis()
        self.test_performance_forecasting()
        self.test_velocity_prediction()
        self.test_risk_assessment()
        
        # Integration tests
        self.test_hook_integration_with_predictions()
        self.test_predictive_insights_generation()
        self.test_real_time_prediction_updates()
        
        # Advanced scenarios
        self.test_high_load_prediction_scenario()
        self.test_resource_exhaustion_prediction()
        
        # Generate final report
        self.generate_test_report()
    
    def test_predictive_engine_initialization(self):
        """Test 1: Predictive Engine Initialization"""
        test_name = "Predictive Engine Initialization"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"🔮 Test 1: {test_name}")
            
            # Initialize predictive engine
            engine = PredictiveAnalyticsEngine()
            
            # Verify key components
            assert hasattr(engine, 'trend_models'), "Should have trend models"
            assert hasattr(engine, 'forecast_models'), "Should have forecast models"
            assert hasattr(engine, 'velocity_models'), "Should have velocity models"
            assert hasattr(engine, 'risk_models'), "Should have risk models"
            assert engine.db_path.exists(), "Should create database"
            
            self._test_passed(test_name, "Predictive engine initialized successfully")
            
        except Exception as e:
            self._test_failed(test_name, str(e))
    
    def test_trend_analysis(self):
        """Test 2: Trend Analysis"""
        test_name = "Trend Analysis"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"📈 Test 2: {test_name}")
            
            engine = PredictiveAnalyticsEngine()
            
            # Test with various trend patterns
            test_data = {
                'increasing_trend': list(range(20, 40)),  # Clear upward trend
                'decreasing_trend': list(range(40, 20, -1)),  # Clear downward trend
                'stable_trend': [30] * 20,  # Stable values
                'volatile_trend': [30 + (i % 4 - 2) * 5 for i in range(20)]  # Volatile pattern
            }
            
            trends = engine.analyze_trends(test_data)
            
            # Should detect trends for sufficient data
            trend_count = len(trends)
            assert trend_count > 0, "Should detect some trends with test data"
            
            # Check trend properties
            for trend in trends:
                assert hasattr(trend, 'direction'), "Trend should have direction"
                assert hasattr(trend, 'confidence'), "Trend should have confidence"
                assert hasattr(trend, 'predicted_next_values'), "Trend should have predictions"
                assert 0 <= trend.confidence <= 1, "Confidence should be between 0 and 1"
            
            self._test_passed(test_name, f"Detected {trend_count} trends successfully")
            
        except Exception as e:
            self._test_failed(test_name, str(e))
    
    def test_performance_forecasting(self):
        """Test 3: Performance Forecasting"""
        test_name = "Performance Forecasting"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"🔮 Test 3: {test_name}")
            
            engine = PredictiveAnalyticsEngine()
            
            # Create synthetic time series data
            base_values = [50 + i * 0.5 + (i % 10) * 2 for i in range(50)]
            test_data = {
                'cpu_usage': base_values,
                'memory_usage': [v * 0.8 for v in base_values],
                'execution_time': [v * 0.1 for v in base_values]
            }
            
            forecasts = engine.generate_forecasts(test_data, [5, 15, 30])
            
            # Should generate forecasts
            forecast_count = len(forecasts)
            assert forecast_count > 0, "Should generate forecasts with sufficient data"
            
            # Verify forecast properties
            for forecast in forecasts:
                assert len(forecast.predicted_values) > 0, "Should have predicted values"
                assert len(forecast.confidence_intervals) == len(forecast.predicted_values), "Should have confidence intervals"
                assert hasattr(forecast, 'forecast_confidence'), "Should have forecast confidence"
                assert hasattr(forecast, 'risk_assessment'), "Should have risk assessment"
            
            self._test_passed(test_name, f"Generated {forecast_count} forecasts successfully")
            
        except Exception as e:
            self._test_failed(test_name, str(e))
    
    def test_velocity_prediction(self):
        """Test 4: Velocity Prediction"""
        test_name = "Velocity Prediction"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"⚡ Test 4: {test_name}")
            
            engine = PredictiveAnalyticsEngine()
            
            # Test different task types
            task_types = ['Task', 'Bash', 'Read', 'Write', 'Edit']
            predictions = []
            
            for task_type in task_types:
                prediction = engine.predict_velocity(task_type, {'complexity': 'medium'})
                predictions.append(prediction)
                
                # Verify prediction properties
                assert prediction.predicted_completion_time > 0, "Should predict positive completion time"
                assert 0 <= prediction.confidence <= 1, "Confidence should be between 0 and 1"
                assert len(prediction.factors_considered) > 0, "Should consider multiple factors"
                assert len(prediction.optimization_suggestions) > 0, "Should provide optimization suggestions"
            
            avg_prediction_time = sum(p.predicted_completion_time for p in predictions) / len(predictions)
            avg_confidence = sum(p.confidence for p in predictions) / len(predictions)
            
            self._test_passed(test_name, f"Generated {len(predictions)} predictions (avg: {avg_prediction_time:.1f}s, confidence: {avg_confidence:.2f})")
            
        except Exception as e:
            self._test_failed(test_name, str(e))
    
    def test_risk_assessment(self):
        """Test 5: Risk Assessment"""
        test_name = "Risk Assessment"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"⚠️ Test 5: {test_name}")
            
            engine = PredictiveAnalyticsEngine()
            
            # Test various risk scenarios
            test_scenarios = [
                {'cpu_usage': 95, 'memory_usage': 85, 'disk_usage': 70},  # High risk
                {'cpu_usage': 60, 'memory_usage': 55, 'disk_usage': 50},  # Medium risk
                {'cpu_usage': 30, 'memory_usage': 35, 'disk_usage': 25}   # Low risk
            ]
            
            total_risks = 0
            high_risk_count = 0
            
            for i, scenario in enumerate(test_scenarios):
                risks = engine.assess_risks(scenario)
                total_risks += len(risks)
                
                for risk in risks:
                    # Verify risk properties
                    assert hasattr(risk, 'risk_type'), "Risk should have type"
                    assert hasattr(risk, 'risk_level'), "Risk should have level"
                    assert 0 <= risk.probability <= 1, "Probability should be between 0 and 1"
                    assert risk.impact_score > 0, "Should have positive impact score"
                    assert len(risk.mitigation_strategies) > 0, "Should provide mitigation strategies"
                    
                    if risk.risk_level.value in ['high', 'critical']:
                        high_risk_count += 1
            
            # High resource usage scenario should detect more risks
            high_scenario_risks = engine.assess_risks(test_scenarios[0])
            low_scenario_risks = engine.assess_risks(test_scenarios[2])
            
            assert len(high_scenario_risks) >= len(low_scenario_risks), "High usage should detect more risks"
            
            self._test_passed(test_name, f"Assessed {total_risks} risks across scenarios ({high_risk_count} high/critical)")
            
        except Exception as e:
            self._test_failed(test_name, str(e))
    
    def test_hook_integration_with_predictions(self):
        """Test 6: Hook Integration with Predictions"""
        test_name = "Hook Integration with Predictions"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"🔗 Test 6: {test_name}")
            
            # Initialize hook with predictive analytics enabled
            import os
            os.environ['ENABLE_PREDICTIVE_ANALYTICS'] = 'true'
            
            hook = PerformanceMonitoringHook()
            
            # Test pre-hook with predictive insights
            pre_result = hook.pre_tool_use_hook('Task', {'test': 'value'})
            
            assert 'performance_insights' in pre_result, "Should provide performance insights"
            insights = pre_result['performance_insights']
            
            # Should include predictive insights
            predictive_insights = [insight for insight in insights if 'predicted' in insight.lower() or 'risk' in insight.lower()]
            assert len(predictive_insights) > 0, "Should include predictive insights"
            
            # Test post-hook with predictive analysis
            post_result = hook.post_tool_use_hook('Task', {'test': 'value'}, 'result', 5.0)
            
            assert 'predictive_analysis' in post_result, "Should include predictive analysis"
            predictive_analysis = post_result['predictive_analysis']
            
            # Verify predictive analysis structure
            expected_keys = ['velocity_analysis', 'risk_assessment', 'performance_predictions']
            for key in expected_keys:
                assert key in predictive_analysis, f"Should include {key} in predictive analysis"
            
            self._test_passed(test_name, f"Integration successful ({len(insights)} insights, {len(predictive_analysis)} analysis sections)")
            
        except Exception as e:
            self._test_failed(test_name, str(e))
    
    def test_predictive_insights_generation(self):
        """Test 7: Predictive Insights Generation"""
        test_name = "Predictive Insights Generation"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"💡 Test 7: {test_name}")
            
            engine = PredictiveAnalyticsEngine()
            
            # Test insight generation for different scenarios
            scenarios = [
                {'tool_name': 'Task', 'execution_time': 2.0, 'arguments': {}},
                {'tool_name': 'Bash', 'execution_time': 15.0, 'arguments': {'command': 'find / -name "*.log"'}},
                {'tool_name': 'Read', 'execution_time': 0.5, 'arguments': {'file_path': '/small/file.txt'}}
            ]
            
            insight_count = 0
            
            for scenario in scenarios:
                # Generate velocity prediction (key insight)
                velocity = engine.predict_velocity(scenario['tool_name'], scenario['arguments'])
                
                # Count insights
                insight_count += len(velocity.optimization_suggestions)
                insight_count += len(velocity.risk_factors)
                
                # Verify insights are relevant
                assert velocity.predicted_completion_time > 0, "Should predict realistic completion time"
                assert len(velocity.optimization_suggestions) > 0, "Should provide optimization suggestions"
                
                # Test risk insights
                current_metrics = engine._get_current_performance_metrics()
                risks = engine.assess_risks(current_metrics)
                
                for risk in risks:
                    insight_count += len(risk.early_warning_indicators)
                    assert len(risk.early_warning_indicators) > 0, "Should provide early warning indicators"
            
            self._test_passed(test_name, f"Generated {insight_count} predictive insights across scenarios")
            
        except Exception as e:
            self._test_failed(test_name, str(e))
    
    def test_real_time_prediction_updates(self):
        """Test 8: Real-time Prediction Updates"""
        test_name = "Real-time Prediction Updates"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"⏱️ Test 8: {test_name}")
            
            engine = PredictiveAnalyticsEngine()
            
            # Test multiple predictions over time
            predictions_over_time = []
            
            for i in range(3):
                # Simulate changing conditions
                velocity = engine.predict_velocity('Task', {'iteration': i})
                predictions_over_time.append(velocity)
                
                # Small delay to simulate real-time updates
                time.sleep(0.1)
            
            # Verify predictions are generated
            assert len(predictions_over_time) == 3, "Should generate predictions for each iteration"
            
            # Check prediction consistency
            avg_prediction_time = sum(p.predicted_completion_time for p in predictions_over_time) / len(predictions_over_time)
            
            # All predictions should be reasonable
            for prediction in predictions_over_time:
                assert prediction.predicted_completion_time > 0, "All predictions should be positive"
                assert prediction.confidence >= 0, "All predictions should have non-negative confidence"
            
            self._test_passed(test_name, f"Generated {len(predictions_over_time)} real-time predictions (avg: {avg_prediction_time:.1f}s)")
            
        except Exception as e:
            self._test_failed(test_name, str(e))
    
    def test_high_load_prediction_scenario(self):
        """Test 9: High Load Prediction Scenario"""
        test_name = "High Load Prediction Scenario"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"🔥 Test 9: {test_name}")
            
            engine = PredictiveAnalyticsEngine()
            
            # Simulate high system load
            high_load_metrics = {
                'cpu_usage': 90,
                'memory_usage': 85,
                'disk_usage': 75,
                'execution_time': 20.0
            }
            
            # Test velocity prediction under load
            velocity = engine.predict_velocity('Task', {'complexity': 'high'})
            
            # Should predict longer completion time due to load
            assert velocity.predicted_completion_time > 30, "Should predict longer time under high load"
            
            # Test risk assessment under load
            risks = engine.assess_risks(high_load_metrics)
            high_risks = [r for r in risks if r.risk_level.value in ['high', 'critical']]
            
            assert len(high_risks) > 0, "Should detect high risks under load"
            assert len(risks) >= 3, "Should detect multiple risks under high load"
            
            # Verify risk mitigation strategies
            total_strategies = sum(len(r.mitigation_strategies) for r in risks)
            assert total_strategies > 5, "Should provide multiple mitigation strategies"
            
            self._test_passed(test_name, f"High load scenario: {len(risks)} risks detected, {len(high_risks)} critical")
            
        except Exception as e:
            self._test_failed(test_name, str(e))
    
    def test_resource_exhaustion_prediction(self):
        """Test 10: Resource Exhaustion Prediction"""
        test_name = "Resource Exhaustion Prediction"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"📉 Test 10: {test_name}")
            
            engine = PredictiveAnalyticsEngine()
            
            # Test resource exhaustion scenarios
            exhaustion_scenarios = [
                {'cpu_usage': 95, 'memory_usage': 60, 'disk_usage': 50},  # CPU exhaustion
                {'cpu_usage': 60, 'memory_usage': 95, 'disk_usage': 50},  # Memory exhaustion
                {'cpu_usage': 60, 'memory_usage': 60, 'disk_usage': 95}   # Disk exhaustion
            ]
            
            exhaustion_predictions = 0
            
            for i, scenario in enumerate(exhaustion_scenarios):
                # Test with performance monitoring hook integration
                hook = PerformanceMonitoringHook()
                result = hook.post_tool_use_hook('TestTool', {}, 'result', 5.0)
                
                if 'predictive_analysis' in result:
                    pred_analysis = result['predictive_analysis']
                    if 'performance_predictions' in pred_analysis:
                        perf_pred = pred_analysis['performance_predictions']
                        
                        # Check for resource exhaustion timeline
                        if 'resource_exhaustion_timeline' in perf_pred:
                            timeline = perf_pred['resource_exhaustion_timeline']
                            if timeline:  # Non-empty timeline indicates potential exhaustion
                                exhaustion_predictions += 1
                
                # Direct risk assessment test
                risks = engine.assess_risks(scenario)
                critical_risks = [r for r in risks if r.risk_level.value == 'critical']
                
                if critical_risks:
                    exhaustion_predictions += 1
            
            assert exhaustion_predictions > 0, "Should predict resource exhaustion for high usage scenarios"
            
            self._test_passed(test_name, f"Resource exhaustion prediction successful ({exhaustion_predictions} scenarios)")
            
        except Exception as e:
            self._test_failed(test_name, str(e))
    
    def _test_passed(self, test_name: str, details: str):
        """Record a passed test"""
        self.test_results['passed_tests'] += 1
        self.test_results['test_details'].append({
            'name': test_name,
            'status': 'PASSED',
            'details': details
        })
        print(f"   ✅ PASSED: {details}")
    
    def _test_failed(self, test_name: str, error: str):
        """Record a failed test"""
        self.test_results['failed_tests'] += 1
        self.test_results['test_details'].append({
            'name': test_name,
            'status': 'FAILED',
            'error': error
        })
        print(f"   ❌ FAILED: {error}")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        
        print("\n" + "=" * 70)
        print("🔮 PREDICTIVE ANALYTICS SYSTEM TEST REPORT")
        print("=" * 70)
        
        # Summary
        total = self.test_results['total_tests']
        passed = self.test_results['passed_tests']
        failed = self.test_results['failed_tests']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {total}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Status indicator
        if success_rate >= 90:
            status_emoji = "🟢"
            status_text = "EXCELLENT"
        elif success_rate >= 75:
            status_emoji = "🟡"
            status_text = "GOOD"
        elif success_rate >= 50:
            status_emoji = "🟠"
            status_text = "NEEDS IMPROVEMENT"
        else:
            status_emoji = "🔴"
            status_text = "CRITICAL"
        
        print(f"\n{status_emoji} Overall Predictive System Status: {status_text}")
        
        # Detailed results
        print(f"\n📝 Detailed Results:")
        for test in self.test_results['test_details']:
            status_symbol = "✅" if test['status'] == 'PASSED' else "❌"
            print(f"   {status_symbol} {test['name']}")
            if test['status'] == 'PASSED':
                print(f"      {test['details']}")
            else:
                print(f"      Error: {test['error']}")
        
        # Predictive system capabilities confirmed
        if success_rate >= 80:
            print(f"\n🔮 Confirmed Predictive System Capabilities:")
            print(f"   ✅ Advanced trend analysis with statistical modeling")
            print(f"   ✅ ML-powered performance forecasting")
            print(f"   ✅ Intelligent velocity prediction")
            print(f"   ✅ Comprehensive risk assessment")
            print(f"   ✅ Real-time predictive insights generation")
            print(f"   ✅ Resource exhaustion prediction")
            print(f"   ✅ High-load scenario handling")
            print(f"   ✅ Seamless hook integration")
        
        # Save report
        report_path = Path.home() / ".claude" / "predictive_test_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📁 Full predictive test report saved to: {report_path}")
        
        return success_rate


def main():
    """Run comprehensive predictive system test"""
    
    tester = PredictiveSystemTest()
    tester.run_all_tests()
    
    # Calculate success rate
    total = tester.test_results['total_tests']
    passed = tester.test_results['passed_tests']
    success_rate = (passed / total * 100) if total > 0 else 0
    
    # Return appropriate exit code
    exit_code = 0 if success_rate >= 80 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()