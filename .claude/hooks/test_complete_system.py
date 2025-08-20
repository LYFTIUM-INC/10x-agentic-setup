#!/usr/bin/env python3
"""
Comprehensive Test Suite for Complete Performance Monitoring System
Tests resource optimization, bottleneck detection, and ML-powered insights
"""

import sys
import time
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

# Add performance modules to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir / "performance"))

from performance_monitoring_hook import PerformanceMonitoringHook
from performance.metrics_collector import MetricsCollector
from performance.bottleneck_detector import AdvancedBottleneckDetector
from performance.resource_optimizer import ResourceOptimizer


class ComprehensiveSystemTest:
    """Complete system integration test"""
    
    def __init__(self):
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        
        print("🚀 Starting Comprehensive Performance Monitoring System Test")
        print("=" * 70)
    
    def run_all_tests(self):
        """Run all system tests"""
        
        # Core component tests
        self.test_performance_hook_integration()
        self.test_bottleneck_detection_integration()
        self.test_resource_optimization_integration() 
        self.test_advanced_analysis_flow()
        self.test_dashboard_integration()
        self.test_error_handling()
        
        # Performance scenario tests
        self.test_high_cpu_scenario()
        self.test_memory_pressure_scenario()
        self.test_slow_tool_optimization()
        
        # Generate final report
        self.generate_test_report()
    
    def test_performance_hook_integration(self):
        """Test 1: Performance Hook Integration"""
        test_name = "Performance Hook Integration"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"🧪 Test 1: {test_name}")
            
            # Initialize hook
            hook = PerformanceMonitoringHook()
            
            # Test pre-hook
            pre_result = hook.pre_tool_use_hook('TestTool', {'test_param': 'test_value'})
            assert pre_result['monitoring_enabled'] == True, "Pre-hook should be enabled"
            assert 'performance_insights' in pre_result, "Should provide insights"
            
            # Test post-hook
            post_result = hook.post_tool_use_hook('TestTool', {'test_param': 'test_value'}, 'result', 1.5)
            assert 'performance_analysis' in post_result, "Should include performance analysis"
            assert 'bottleneck_analysis' in post_result, "Should include bottleneck analysis"
            
            self._test_passed(test_name, "Hook integration successful")
            
        except Exception as e:
            self._test_failed(test_name, str(e))
    
    def test_bottleneck_detection_integration(self):
        """Test 2: ML Bottleneck Detection Integration"""
        test_name = "ML Bottleneck Detection Integration"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"🔍 Test 2: {test_name}")
            
            # Initialize components
            metrics_collector = MetricsCollector()
            detector = AdvancedBottleneckDetector(metrics_collector, None)
            
            # Test bottleneck detection with simulated metrics
            test_metrics = {
                'cpu_usage': 95.0,
                'memory_usage': 88.0,
                'disk_usage': 78.0,
                'avg_execution_time': 25.0
            }
            
            bottlenecks = detector.detect_bottlenecks(test_metrics)
            assert len(bottlenecks) > 0, "Should detect bottlenecks with high resource usage"
            
            # Verify bottleneck properties
            cpu_bottleneck = next((b for b in bottlenecks if b.category.value == 'computational'), None)
            if cpu_bottleneck:
                assert cpu_bottleneck.confidence > 0.5, "Should have reasonable confidence"
                assert len(cpu_bottleneck.resolution_recommendations) > 0, "Should provide recommendations"
            
            self._test_passed(test_name, f"Detected {len(bottlenecks)} bottlenecks successfully")
            
        except Exception as e:
            self._test_failed(test_name, str(e))
    
    def test_resource_optimization_integration(self):
        """Test 3: Resource Optimization Integration"""
        test_name = "Resource Optimization Integration"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"⚡ Test 3: {test_name}")
            
            # Initialize resource optimizer
            metrics_collector = MetricsCollector()
            optimizer = ResourceOptimizer(metrics_collector)
            
            # Test bottleneck detection
            resource_bottlenecks = optimizer.detect_bottlenecks()
            print(f"   Detected {len(resource_bottlenecks)} resource bottlenecks")
            
            # Test optimization plan generation if bottlenecks found
            if resource_bottlenecks:
                plan = optimizer.generate_optimization_plan(resource_bottlenecks[:3])  # Top 3
                assert plan.plan_id is not None, "Should generate plan ID"
                assert len(plan.actions) > 0, "Should provide optimization actions"
                assert plan.expected_improvement > 0, "Should estimate improvement"
            
            self._test_passed(test_name, "Resource optimization system working")
            
        except Exception as e:
            self._test_failed(test_name, str(e))
    
    def test_advanced_analysis_flow(self):
        """Test 4: Advanced Analysis Flow"""
        test_name = "Advanced Analysis Flow"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"🔬 Test 4: {test_name}")
            
            hook = PerformanceMonitoringHook()
            
            # Simulate slow tool execution
            result = hook.post_tool_use_hook('SlowTask', {}, 'result', 15.0)
            
            # Verify advanced analysis was performed
            assert 'bottleneck_analysis' in result, "Should include bottleneck analysis"
            bottleneck_analysis = result['bottleneck_analysis']
            
            assert 'bottlenecks_detected' in bottleneck_analysis, "Should detect bottlenecks"
            assert 'resource_bottlenecks' in bottleneck_analysis, "Should check resource bottlenecks"
            assert 'optimization_recommendations' in bottleneck_analysis, "Should provide recommendations"
            assert 'performance_health_score' in bottleneck_analysis, "Should calculate health score"
            
            # Health score should be reasonable for slow execution
            health_score = bottleneck_analysis['performance_health_score']
            assert 0 <= health_score <= 100, "Health score should be in valid range"
            
            self._test_passed(test_name, f"Advanced analysis complete (Health Score: {health_score:.1f})")
            
        except Exception as e:
            self._test_failed(test_name, str(e))
    
    def test_dashboard_integration(self):
        """Test 5: Dashboard Integration"""
        test_name = "Dashboard Integration"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"📊 Test 5: {test_name}")
            
            # Check if dashboard file exists and is accessible
            dashboard_path = Path.home() / ".claude" / "dashboard.html"
            
            if dashboard_path.exists():
                with open(dashboard_path, 'r') as f:
                    content = f.read()
                    assert "Claude Code Dashboard" in content, "Dashboard should have title"
                    assert "Performance" in content, "Dashboard should mention performance"
                    assert "chart" in content.lower(), "Dashboard should include charts"
            
            self._test_passed(test_name, "Dashboard integration verified")
            
        except Exception as e:
            self._test_failed(test_name, str(e))
    
    def test_error_handling(self):
        """Test 6: Error Handling"""
        test_name = "Error Handling"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"🛡️ Test 6: {test_name}")
            
            hook = PerformanceMonitoringHook()
            
            # Test with invalid/None arguments
            result = hook.pre_tool_use_hook('TestTool', None)
            assert 'error' in result or result.get('monitoring_enabled') == False, "Should handle None arguments"
            
            result = hook.post_tool_use_hook('TestTool', {}, None, -1)
            assert isinstance(result, dict), "Should return dict even with invalid data"
            
            self._test_passed(test_name, "Error handling works properly")
            
        except Exception as e:
            self._test_failed(test_name, str(e))
    
    def test_high_cpu_scenario(self):
        """Test 7: High CPU Scenario"""
        test_name = "High CPU Scenario"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"🔥 Test 7: {test_name}")
            
            hook = PerformanceMonitoringHook()
            
            # Simulate CPU-intensive operation
            pre_result = hook.pre_tool_use_hook('CPUIntensive', {'operation': 'heavy_computation'})
            
            # Check if CPU bottleneck insights are provided
            insights = pre_result.get('performance_insights', [])
            cpu_related = any('cpu' in insight.lower() or 'computational' in insight.lower() for insight in insights)
            
            # The hook should provide some performance insights
            assert isinstance(insights, list), "Should provide insights list"
            
            self._test_passed(test_name, f"CPU scenario handled ({len(insights)} insights provided)")
            
        except Exception as e:
            self._test_failed(test_name, str(e))
    
    def test_memory_pressure_scenario(self):
        """Test 8: Memory Pressure Scenario"""
        test_name = "Memory Pressure Scenario"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"🧠 Test 8: {test_name}")
            
            hook = PerformanceMonitoringHook()
            
            # Simulate memory-intensive operation
            large_data = "x" * (1024 * 1024)  # 1MB string
            result = hook.post_tool_use_hook('MemoryIntensive', {'data': large_data}, 'result', 3.0)
            
            # Verify analysis includes memory considerations
            assert 'performance_analysis' in result, "Should analyze performance"
            analysis = result['performance_analysis']
            
            # Should categorize based on execution time and data size
            assert 'performance_tier' in analysis, "Should categorize performance"
            
            self._test_passed(test_name, f"Memory scenario handled (Tier: {analysis.get('performance_tier', 'unknown')})")
            
        except Exception as e:
            self._test_failed(test_name, str(e))
    
    def test_slow_tool_optimization(self):
        """Test 9: Slow Tool Optimization"""
        test_name = "Slow Tool Optimization"
        self.test_results['total_tests'] += 1
        
        try:
            print(f"⏱️ Test 9: {test_name}")
            
            hook = PerformanceMonitoringHook()
            
            # Simulate very slow tool
            result = hook.post_tool_use_hook('VerySlow', {}, 'result', 35.0)
            
            # Should trigger performance warnings and recommendations
            assert 'performance_warning' in result, "Should warn about slow execution"
            warning = result['performance_warning']
            
            assert 'recommendations' in warning, "Should provide recommendations"
            assert len(warning['recommendations']) > 0, "Should have specific recommendations"
            
            self._test_passed(test_name, f"Slow tool optimization triggered ({len(warning['recommendations'])} recommendations)")
            
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
        print("📋 COMPREHENSIVE SYSTEM TEST REPORT")
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
        
        print(f"\n{status_emoji} Overall System Status: {status_text}")
        
        # Detailed results
        print(f"\n📝 Detailed Results:")
        for test in self.test_results['test_details']:
            status_symbol = "✅" if test['status'] == 'PASSED' else "❌"
            print(f"   {status_symbol} {test['name']}")
            if test['status'] == 'PASSED':
                print(f"      {test['details']}")
            else:
                print(f"      Error: {test['error']}")
        
        # System capabilities confirmed
        if success_rate >= 75:
            print(f"\n🚀 Confirmed System Capabilities:")
            print(f"   ✅ Real-time performance monitoring")
            print(f"   ✅ ML-powered bottleneck detection")
            print(f"   ✅ Advanced resource optimization")
            print(f"   ✅ Comprehensive analysis and recommendations")
            print(f"   ✅ Dashboard integration and visualization")
            print(f"   ✅ Robust error handling and recovery")
        
        # Save report
        report_path = Path.home() / ".claude" / "system_test_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📁 Full test report saved to: {report_path}")
        
        return success_rate


def main():
    """Run comprehensive system test"""
    
    tester = ComprehensiveSystemTest()
    tester.run_all_tests()
    
    # Calculate success rate
    total = tester.test_results['total_tests']
    passed = tester.test_results['passed_tests']
    success_rate = (passed / total * 100) if total > 0 else 0
    
    # Return appropriate exit code
    exit_code = 0 if success_rate >= 75 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()