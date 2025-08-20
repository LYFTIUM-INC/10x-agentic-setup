#!/usr/bin/env python3
"""
Performance Monitoring Hook for Claude Code
Integrates metrics collection, analysis, optimization, and dashboard updates
"""

import sys
import json
import time
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add performance modules to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir / "performance"))

from performance.metrics_collector import MetricsCollector, ToolExecutionTracker, HookExecutionTracker
from performance.performance_analyzer import PerformanceAnalyzer
from performance.optimization_engine import OptimizationEngine
from performance.dashboard_generator import DashboardGenerator
from performance.resource_optimizer import ResourceOptimizer
from performance.bottleneck_detector import AdvancedBottleneckDetector
from performance.predictive_analytics import PredictiveAnalyticsEngine

class PerformanceMonitoringHook:
    """Comprehensive performance monitoring hook for Claude Code"""
    
    def __init__(self):
        # Initialize components
        self.metrics_collector = MetricsCollector()
        self.analyzer = PerformanceAnalyzer()
        self.optimizer = OptimizationEngine(self.metrics_collector, self.analyzer)
        self.dashboard = DashboardGenerator()
        self.resource_optimizer = ResourceOptimizer(self.metrics_collector)
        self.bottleneck_detector = AdvancedBottleneckDetector(self.metrics_collector, self.analyzer)
        self.predictive_engine = PredictiveAnalyticsEngine(self.metrics_collector)
        
        # Configuration
        self.enable_auto_optimization = os.getenv('PERFORMANCE_AUTO_OPTIMIZE', 'false').lower() == 'true'
        self.enable_predictive_scaling = os.getenv('PERFORMANCE_PREDICTIVE_SCALING', 'false').lower() == 'true'
        self.enable_bottleneck_detection = os.getenv('ENABLE_BOTTLENECK_DETECTION', 'true').lower() == 'true'
        self.enable_resource_optimization = os.getenv('ENABLE_RESOURCE_OPTIMIZATION', 'true').lower() == 'true'
        self.enable_predictive_analytics = os.getenv('ENABLE_PREDICTIVE_ANALYTICS', 'true').lower() == 'true'
        self.performance_threshold = float(os.getenv('PERFORMANCE_THRESHOLD', '5.0'))  # seconds
        
        # Session tracking
        self.session_id = self._generate_session_id()
        self.active_trackers = {}
        
        # Start dashboard if not already running
        if not os.getenv('DASHBOARD_DISABLED', 'false').lower() == 'true':
            try:
                self.dashboard.start_dashboard()
            except Exception as e:
                print(f"Dashboard startup failed: {e}")
    
    def pre_tool_use_hook(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-tool monitoring hook"""
        
        start_time = time.time()
        
        try:
            # Start tool execution tracking
            tracker = self.metrics_collector.track_tool_execution(tool_name, start_time)
            
            # Estimate input size
            input_size = self._estimate_input_size(arguments)
            tracker.set_input_size(input_size)
            
            # Store tracker for post-hook use
            self.active_trackers[f"{tool_name}_{start_time}"] = tracker
            
            # Check for performance optimization opportunities
            insights = []
            
            # Run bottleneck detection
            if self.enable_bottleneck_detection:
                try:
                    bottlenecks = self.bottleneck_detector.detect_bottlenecks()
                    for bottleneck in bottlenecks[:2]:  # Top 2 bottlenecks
                        if bottleneck.severity in ['high', 'critical']:
                            insights.append(f"Bottleneck detected: {bottleneck.category.value} - {bottleneck.severity}")
                except Exception as e:
                    insights.append(f"Bottleneck detection warning: {str(e)}")
            
            # Resource optimization opportunities
            if self.enable_resource_optimization:
                try:
                    resource_bottlenecks = self.resource_optimizer.detect_bottlenecks()
                    for bottleneck in resource_bottlenecks[:2]:  # Top 2 resource issues
                        if bottleneck.severity in ['high', 'critical']:
                            insights.append(f"Resource bottleneck: {bottleneck.resource_type.value} - {bottleneck.root_cause}")
                except Exception as e:
                    insights.append(f"Resource analysis warning: {str(e)}")
            
            # Predictive analytics insights
            if self.enable_predictive_analytics:
                try:
                    # Velocity prediction for this tool
                    velocity_prediction = self.predictive_engine.predict_velocity(tool_name, arguments)
                    insights.append(f"Predicted completion: {velocity_prediction.predicted_completion_time:.1f}s ({velocity_prediction.confidence:.2f} confidence)")
                    
                    # Risk assessment
                    current_metrics = self.predictive_engine._get_current_performance_metrics()
                    risk_assessments = self.predictive_engine.assess_risks(current_metrics)
                    high_risks = [r for r in risk_assessments if r.risk_level.value in ['high', 'critical']]
                    if high_risks:
                        insights.append(f"Performance risks detected: {len(high_risks)} high/critical risks")
                        
                except Exception as e:
                    insights.append(f"Predictive analytics warning: {str(e)}")
            
            # Traditional optimization opportunities
            if self.enable_auto_optimization:
                opportunities = self.optimizer.analyze_optimization_opportunities()
                for opp in opportunities[:3]:  # Top 3 opportunities
                    if opp.get('priority') == 'high':
                        insights.append(f"Optimization opportunity: {opp.get('description', 'Unknown')}")
            
            return {
                'monitoring_enabled': True,
                'tool_name': tool_name,
                'start_time': start_time,
                'input_size': input_size,
                'session_id': self.session_id,
                'performance_insights': insights,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'monitoring_enabled': False,
                'error': str(e),
                'tool_name': tool_name,
                'timestamp': time.time()
            }
    
    def post_tool_use_hook(self, tool_name: str, arguments: Dict[str, Any], 
                          result: Any, execution_time: float) -> Dict[str, Any]:
        """Post-tool monitoring and analysis hook"""
        
        analysis_results = {
            'tool_name': tool_name,
            'execution_time': execution_time,
            'timestamp': time.time(),
            'session_id': self.session_id,
            'performance_analysis': {}
        }
        
        try:
            # Find and finalize tool execution tracker
            tracker_key = None
            for key in self.active_trackers.keys():
                if key.startswith(tool_name):
                    tracker_key = key
                    break
            
            if tracker_key:
                tracker = self.active_trackers.pop(tracker_key)
                
                # Set output size
                output_size = self._estimate_output_size(result)
                tracker.set_output_size(output_size)
                
                # Finalize tracking (this will store metrics)
                tracker.__exit__(None, None, None)
                
                analysis_results['output_size'] = output_size
            
            # Performance analysis
            performance_analysis = self._analyze_tool_performance(tool_name, execution_time, arguments, result)
            analysis_results['performance_analysis'] = performance_analysis
            
            # Check for performance issues
            if execution_time > self.performance_threshold:
                analysis_results['performance_warning'] = {
                    'message': f"Slow execution detected: {tool_name} took {execution_time:.2f}s",
                    'threshold': self.performance_threshold,
                    'recommendations': self._get_performance_recommendations(tool_name, execution_time)
                }
                
                # Trigger auto-optimization if enabled
                if self.enable_auto_optimization and execution_time > self.performance_threshold * 2:
                    optimization_results = self._trigger_auto_optimization(tool_name, execution_time)
                    analysis_results['auto_optimization'] = optimization_results
            
            # Update dashboard data
            self._update_dashboard()
            
            # Advanced bottleneck detection and resource optimization
            if self.enable_bottleneck_detection or self.enable_resource_optimization:
                bottleneck_analysis = self._perform_advanced_bottleneck_analysis(tool_name, execution_time)
                analysis_results['bottleneck_analysis'] = bottleneck_analysis
            
            # Predictive analytics
            if self.enable_predictive_analytics:
                predictive_analysis = self._perform_predictive_analysis(tool_name, execution_time, arguments, result)
                analysis_results['predictive_analysis'] = predictive_analysis
            
            # Predictive scaling
            if self.enable_predictive_scaling:
                scaling_insights = self._analyze_scaling_needs(tool_name, execution_time)
                analysis_results['scaling_insights'] = scaling_insights
            
        except Exception as e:
            analysis_results['error'] = str(e)
        
        return analysis_results
    
    def hook_execution_monitor(self, hook_name: str, hook_type: str, tool_name: str = None):
        """Context manager for monitoring hook execution"""
        return self.metrics_collector.track_hook_execution(hook_name, hook_type, tool_name)
    
    def _analyze_tool_performance(self, tool_name: str, execution_time: float, 
                                arguments: Dict[str, Any], result: Any) -> Dict[str, Any]:
        """Analyze individual tool performance"""
        
        analysis = {
            'execution_time': execution_time,
            'performance_tier': self._categorize_performance(execution_time),
            'resource_usage': 'normal',  # Would be enhanced with actual resource monitoring
            'optimization_potential': 'low'
        }
        
        # Categorize performance
        if execution_time > 30:
            analysis['performance_tier'] = 'critical'
            analysis['optimization_potential'] = 'high'
        elif execution_time > 10:
            analysis['performance_tier'] = 'slow'
            analysis['optimization_potential'] = 'medium'
        elif execution_time > 2:
            analysis['performance_tier'] = 'acceptable'
            analysis['optimization_potential'] = 'low'
        else:
            analysis['performance_tier'] = 'fast'
            analysis['optimization_potential'] = 'none'
        
        # Tool-specific analysis
        if tool_name == 'Bash':
            command = arguments.get('command', '')
            analysis['command_complexity'] = self._analyze_command_complexity(command)
        elif tool_name in ['Read', 'Write', 'Edit']:
            file_path = arguments.get('file_path', '')
            analysis['file_operation_type'] = self._analyze_file_operation(file_path, arguments)
        elif tool_name == 'Task':
            analysis['subtask_complexity'] = 'high'  # Task operations are typically complex
        
        return analysis
    
    def _categorize_performance(self, execution_time: float) -> str:
        """Categorize performance based on execution time"""
        
        if execution_time < 0.5:
            return 'excellent'
        elif execution_time < 2.0:
            return 'good'
        elif execution_time < 5.0:
            return 'acceptable'
        elif execution_time < 15.0:
            return 'slow'
        else:
            return 'critical'
    
    def _analyze_command_complexity(self, command: str) -> str:
        """Analyze bash command complexity"""
        
        complexity_indicators = [
            ('|', 'pipe'),
            ('&&', 'chaining'),
            ('for ', 'loop'),
            ('while ', 'loop'),
            ('find ', 'search'),
            ('grep -r', 'recursive_search'),
            ('sort', 'sorting'),
            ('awk', 'processing')
        ]
        
        found_indicators = []
        for indicator, category in complexity_indicators:
            if indicator in command:
                found_indicators.append(category)
        
        if len(found_indicators) > 2:
            return 'complex'
        elif len(found_indicators) > 0:
            return 'moderate'
        else:
            return 'simple'
    
    def _analyze_file_operation(self, file_path: str, arguments: Dict[str, Any]) -> str:
        """Analyze file operation type and complexity"""
        
        if 'content' in arguments:
            content_size = len(str(arguments['content']))
            if content_size > 50000:
                return 'large_file_write'
            elif content_size > 5000:
                return 'medium_file_write'
            else:
                return 'small_file_write'
        
        if file_path:
            if file_path.endswith(('.json', '.yaml', '.yml')):
                return 'structured_data'
            elif file_path.endswith(('.py', '.js', '.ts', '.java')):
                return 'source_code'
            elif file_path.endswith(('.md', '.txt')):
                return 'text_document'
            elif file_path.endswith(('.log')):
                return 'log_file'
        
        return 'generic_file_operation'
    
    def _get_performance_recommendations(self, tool_name: str, execution_time: float) -> List[str]:
        """Get performance recommendations for slow tools"""
        
        recommendations = []
        
        if tool_name == 'Bash':
            recommendations.extend([
                "Consider optimizing the command for better performance",
                "Use more efficient commands or flags where possible",
                "Break complex operations into smaller steps"
            ])
        
        elif tool_name in ['Read', 'Write', 'Edit']:
            recommendations.extend([
                "Consider file size and optimize for large files",
                "Use streaming operations for very large files",
                "Check if file caching could improve performance"
            ])
        
        elif tool_name == 'Task':
            recommendations.extend([
                "Consider breaking complex tasks into simpler subtasks",
                "Use parallel execution where possible",
                "Optimize the prompt for more focused analysis"
            ])
        
        # General recommendations
        if execution_time > 30:
            recommendations.append("Consider implementing timeout handling")
        
        if execution_time > 60:
            recommendations.append("This operation may benefit from asynchronous execution")
        
        return recommendations
    
    def _trigger_auto_optimization(self, tool_name: str, execution_time: float) -> Dict[str, Any]:
        """Trigger automatic optimization for slow tools"""
        
        try:
            # Find applicable optimizations
            opportunities = self.optimizer.analyze_optimization_opportunities()
            applicable_opts = []
            
            for opp in opportunities:
                if (opp.get('priority') in ['high', 'medium'] and 
                    opp.get('confidence', 0) > 0.7):
                    applicable_opts.append(opp)
            
            results = []
            for opp in applicable_opts[:2]:  # Apply top 2 optimizations
                rule_id = opp.get('rule_id')
                if rule_id:
                    try:
                        result = self.optimizer.apply_optimization(rule_id, override_approval=True)
                        results.append({
                            'rule_id': rule_id,
                            'optimization_id': result.optimization_id,
                            'status': result.status.value
                        })
                    except Exception as e:
                        results.append({
                            'rule_id': rule_id,
                            'status': 'failed',
                            'error': str(e)
                        })
            
            return {
                'triggered': True,
                'tool_name': tool_name,
                'execution_time': execution_time,
                'optimizations_applied': results
            }
            
        except Exception as e:
            return {
                'triggered': False,
                'error': str(e)
            }
    
    def _analyze_scaling_needs(self, tool_name: str, execution_time: float) -> Dict[str, Any]:
        """Analyze if scaling is needed based on performance trends"""
        
        try:
            trends = self.analyzer.analyze_performance_trends('short')
            bottlenecks = self.analyzer.identify_bottlenecks()
            
            scaling_needed = False
            scaling_type = None
            
            # Check for consistent performance degradation
            degrading_trends = [t for t in trends if t.direction.value == 'degrading']
            if len(degrading_trends) > 1:
                scaling_needed = True
                scaling_type = 'horizontal'
            
            # Check for resource bottlenecks
            critical_bottlenecks = [b for b in bottlenecks if b.severity == 'critical']
            if critical_bottlenecks:
                scaling_needed = True
                scaling_type = 'vertical'
            
            return {
                'scaling_needed': scaling_needed,
                'scaling_type': scaling_type,
                'degrading_trends': len(degrading_trends),
                'critical_bottlenecks': len(critical_bottlenecks),
                'recommendation': self._get_scaling_recommendation(scaling_needed, scaling_type)
            }
            
        except Exception as e:
            return {
                'scaling_analysis_error': str(e)
            }
    
    def _get_scaling_recommendation(self, scaling_needed: bool, scaling_type: str) -> str:
        """Get scaling recommendation"""
        
        if not scaling_needed:
            return "No scaling needed - performance is stable"
        
        if scaling_type == 'vertical':
            return "Consider vertical scaling - increase CPU/memory resources"
        elif scaling_type == 'horizontal':
            return "Consider horizontal scaling - distribute workload across multiple instances"
        else:
            return "Performance monitoring suggests considering scaling options"
    
    def _estimate_input_size(self, arguments: Dict[str, Any]) -> int:
        """Estimate input data size"""
        
        total_size = 0
        
        for key, value in arguments.items():
            if isinstance(value, str):
                total_size += len(value.encode('utf-8'))
            elif isinstance(value, (dict, list)):
                total_size += len(json.dumps(value).encode('utf-8'))
            else:
                total_size += len(str(value).encode('utf-8'))
        
        return total_size
    
    def _estimate_output_size(self, result: Any) -> int:
        """Estimate output data size"""
        
        if result is None:
            return 0
        
        try:
            if isinstance(result, str):
                return len(result.encode('utf-8'))
            elif isinstance(result, (dict, list)):
                return len(json.dumps(result).encode('utf-8'))
            else:
                return len(str(result).encode('utf-8'))
        except:
            return 0
    
    def _update_dashboard(self):
        """Update dashboard with latest data"""
        
        try:
            self.dashboard.update_dashboard_data()
        except Exception as e:
            # Dashboard update failures shouldn't break the hook
            pass
    
    def _perform_advanced_bottleneck_analysis(self, tool_name: str, execution_time: float) -> Dict[str, Any]:
        """Perform advanced bottleneck detection and resource optimization analysis"""
        
        analysis = {
            'tool_name': tool_name,
            'execution_time': execution_time,
            'bottlenecks_detected': [],
            'resource_bottlenecks': [],
            'optimization_recommendations': [],
            'timestamp': time.time()
        }
        
        try:
            # ML-powered bottleneck detection
            if self.enable_bottleneck_detection:
                bottlenecks = self.bottleneck_detector.detect_bottlenecks()
                
                for bottleneck in bottlenecks:
                    bottleneck_info = {
                        'bottleneck_id': bottleneck.bottleneck_id,
                        'category': bottleneck.category.value,
                        'detection_method': bottleneck.detection_method.value,
                        'confidence': bottleneck.confidence,
                        'severity': bottleneck.severity,
                        'symptoms': bottleneck.symptoms_observed,
                        'root_cause': bottleneck.root_cause_analysis.get('primary_factors', []),
                        'recommendations': [rec.get('strategy', 'Unknown') for rec in bottleneck.resolution_recommendations[:3]],
                        'estimated_duration': bottleneck.duration_estimated
                    }
                    analysis['bottlenecks_detected'].append(bottleneck_info)
            
            # Resource-specific bottleneck detection
            if self.enable_resource_optimization:
                resource_bottlenecks = self.resource_optimizer.detect_bottlenecks()
                
                for bottleneck in resource_bottlenecks:
                    resource_info = {
                        'resource_type': bottleneck.resource_type.value,
                        'severity': bottleneck.severity,
                        'current_usage': bottleneck.current_usage,
                        'threshold': bottleneck.threshold,
                        'impact_score': bottleneck.impact_score,
                        'duration_minutes': bottleneck.duration_minutes,
                        'affected_processes': bottleneck.affected_processes[:5],  # Limit processes
                        'root_cause': bottleneck.root_cause,
                        'recommendations': [rec.get('description', 'Unknown') for rec in bottleneck.recommendations[:3]],
                        'detected_at': bottleneck.detected_at
                    }
                    analysis['resource_bottlenecks'].append(resource_info)
            
            # Generate comprehensive optimization recommendations
            analysis['optimization_recommendations'] = self._generate_optimization_recommendations(
                analysis['bottlenecks_detected'], 
                analysis['resource_bottlenecks'],
                tool_name,
                execution_time
            )
            
            # Calculate overall performance health score
            analysis['performance_health_score'] = self._calculate_performance_health_score(
                analysis['bottlenecks_detected'],
                analysis['resource_bottlenecks'],
                execution_time
            )
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _generate_optimization_recommendations(self, bottlenecks: List[Dict], 
                                             resource_bottlenecks: List[Dict],
                                             tool_name: str, execution_time: float) -> List[str]:
        """Generate comprehensive optimization recommendations"""
        
        recommendations = []
        
        # Bottleneck-based recommendations
        for bottleneck in bottlenecks:
            if bottleneck['severity'] in ['high', 'critical']:
                category = bottleneck['category']
                if category == 'computational':
                    recommendations.extend([
                        "Consider parallel processing for CPU-intensive operations",
                        "Optimize algorithm complexity and data structures",
                        "Implement CPU-specific optimizations"
                    ])
                elif category == 'memory':
                    recommendations.extend([
                        "Implement memory pooling and efficient garbage collection",
                        "Optimize data structures for memory efficiency",
                        "Consider memory-mapped files for large data processing"
                    ])
                elif category == 'storage':
                    recommendations.extend([
                        "Implement asynchronous I/O operations",
                        "Use SSD-optimized access patterns",
                        "Consider data compression and caching strategies"
                    ])
        
        # Resource bottleneck recommendations
        for resource in resource_bottlenecks:
            if resource['severity'] in ['high', 'critical']:
                resource_type = resource['resource_type']
                if resource_type == 'cpu':
                    recommendations.append(f"CPU utilization at {resource['current_usage']:.1f}% - consider load balancing")
                elif resource_type == 'memory':
                    recommendations.append(f"Memory usage at {resource['current_usage']:.1f}% - optimize memory allocation")
                elif resource_type == 'disk':
                    recommendations.append(f"Disk usage at {resource['current_usage']:.1f}% - cleanup or expand storage")
        
        # Tool-specific recommendations
        if execution_time > 10:
            if tool_name == 'Task':
                recommendations.append("Break complex tasks into smaller, parallelizable subtasks")
            elif tool_name == 'Bash':
                recommendations.append("Optimize shell commands and consider alternative implementations")
            elif tool_name in ['Read', 'Write', 'Edit']:
                recommendations.append("Consider streaming operations for large files")
        
        # Remove duplicates and limit
        unique_recommendations = list(set(recommendations))
        return unique_recommendations[:5]  # Top 5 recommendations
    
    def _calculate_performance_health_score(self, bottlenecks: List[Dict], 
                                          resource_bottlenecks: List[Dict],
                                          execution_time: float) -> float:
        """Calculate overall performance health score (0-100)"""
        
        score = 100.0
        
        # Deduct points for bottlenecks
        for bottleneck in bottlenecks:
            severity = bottleneck['severity']
            if severity == 'critical':
                score -= 20
            elif severity == 'high':
                score -= 15
            elif severity == 'medium':
                score -= 10
            elif severity == 'low':
                score -= 5
        
        # Deduct points for resource bottlenecks
        for resource in resource_bottlenecks:
            severity = resource['severity']
            if severity == 'critical':
                score -= 15
            elif severity == 'high':
                score -= 10
            elif severity == 'medium':
                score -= 7
            elif severity == 'low':
                score -= 3
        
        # Deduct points based on execution time
        if execution_time > 30:
            score -= 20
        elif execution_time > 15:
            score -= 15
        elif execution_time > 5:
            score -= 10
        
        # Ensure score is within bounds
        return max(0.0, min(100.0, score))
    
    def _perform_predictive_analysis(self, tool_name: str, execution_time: float, 
                                   arguments: Dict[str, Any], result: Any) -> Dict[str, Any]:
        """Perform comprehensive predictive analytics"""
        
        analysis = {
            'tool_name': tool_name,
            'execution_time': execution_time,
            'trends': [],
            'forecasts': [],
            'velocity_analysis': {},
            'risk_assessment': [],
            'performance_predictions': {},
            'timestamp': time.time()
        }
        
        try:
            # Get current performance metrics for analysis
            current_metrics = self.predictive_engine._get_current_performance_metrics()
            
            # Trend Analysis
            if hasattr(self.metrics_collector, 'get_metric_history'):
                try:
                    metric_history = self.metrics_collector.get_metric_history(['cpu_usage', 'memory_usage', 'execution_time'])
                    trends = self.predictive_engine.analyze_trends(metric_history)
                    
                    analysis['trends'] = [
                        {
                            'metric': trend.metric_name,
                            'direction': trend.direction.value,
                            'confidence': trend.confidence,
                            'strength': trend.trend_strength,
                            'predicted_next': trend.predicted_next_values[:3]
                        }
                        for trend in trends
                    ]
                except Exception as e:
                    analysis['trend_analysis_error'] = str(e)
            
            # Performance Forecasting
            try:
                # Create mock historical data for forecasting
                mock_history = {
                    'cpu_usage': [current_metrics['cpu_usage']] * 20,
                    'memory_usage': [current_metrics['memory_usage']] * 20,
                    'execution_time': [execution_time] * 10
                }
                
                forecasts = self.predictive_engine.generate_forecasts(mock_history, [5, 15])
                
                analysis['forecasts'] = [
                    {
                        'metric': forecast.metric_name,
                        'horizon_minutes': forecast.forecast_horizon,
                        'predicted_values': forecast.predicted_values[:3],
                        'confidence': forecast.forecast_confidence.value,
                        'risk_level': forecast.risk_assessment.value,
                        'anomaly_probability': forecast.anomaly_probability
                    }
                    for forecast in forecasts
                ]
            except Exception as e:
                analysis['forecast_error'] = str(e)
            
            # Velocity Analysis
            try:
                velocity_prediction = self.predictive_engine.predict_velocity(tool_name, arguments)
                
                analysis['velocity_analysis'] = {
                    'predicted_completion_time': velocity_prediction.predicted_completion_time,
                    'confidence': velocity_prediction.confidence,
                    'accuracy_score': velocity_prediction.prediction_accuracy_score,
                    'factors_considered': velocity_prediction.factors_considered,
                    'risk_factors': velocity_prediction.risk_factors[:3],  # Top 3
                    'optimization_suggestions': velocity_prediction.optimization_suggestions[:3],
                    'historical_performance': velocity_prediction.historical_performance
                }
            except Exception as e:
                analysis['velocity_error'] = str(e)
            
            # Risk Assessment
            try:
                risk_assessments = self.predictive_engine.assess_risks(current_metrics)
                
                analysis['risk_assessment'] = [
                    {
                        'risk_type': risk.risk_type,
                        'risk_level': risk.risk_level.value,
                        'probability': risk.probability,
                        'impact_score': risk.impact_score,
                        'time_to_materialization_minutes': risk.time_to_materialization,
                        'confidence': risk.confidence,
                        'mitigation_strategies': risk.mitigation_strategies[:3],
                        'early_warning_indicators': risk.early_warning_indicators[:3]
                    }
                    for risk in risk_assessments
                ]
            except Exception as e:
                analysis['risk_assessment_error'] = str(e)
            
            # Performance Predictions for next operations
            try:
                analysis['performance_predictions'] = {
                    'next_operation_estimated_time': self._predict_next_operation_time(tool_name, execution_time, current_metrics),
                    'system_stability_forecast': self._forecast_system_stability(current_metrics),
                    'resource_exhaustion_timeline': self._predict_resource_exhaustion(current_metrics),
                    'performance_improvement_opportunities': self._identify_improvement_opportunities(current_metrics, execution_time)
                }
            except Exception as e:
                analysis['prediction_error'] = str(e)
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _predict_next_operation_time(self, tool_name: str, current_execution_time: float, 
                                   metrics: Dict[str, float]) -> Dict[str, Any]:
        """Predict execution time for next operation of same type"""
        
        # Simple prediction based on current performance and trends
        base_time = current_execution_time
        
        # Adjust based on current system load
        load_factor = 1.0
        if metrics.get('cpu_usage', 50) > 70:
            load_factor *= 1.2
        if metrics.get('memory_usage', 50) > 80:
            load_factor *= 1.3
        
        predicted_time = base_time * load_factor
        
        # Confidence based on system stability
        cpu_stability = 1.0 - abs(metrics.get('cpu_usage', 50) - 50) / 50
        memory_stability = 1.0 - abs(metrics.get('memory_usage', 50) - 50) / 50
        confidence = (cpu_stability + memory_stability) / 2
        
        return {
            'predicted_seconds': predicted_time,
            'confidence': confidence,
            'factors': {
                'base_execution_time': base_time,
                'load_factor': load_factor,
                'cpu_impact': (metrics.get('cpu_usage', 50) - 50) / 50,
                'memory_impact': (metrics.get('memory_usage', 50) - 50) / 50
            }
        }
    
    def _forecast_system_stability(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Forecast system stability over next period"""
        
        # Calculate stability score
        cpu_score = 100 - metrics.get('cpu_usage', 50)
        memory_score = 100 - metrics.get('memory_usage', 50)
        disk_score = 100 - metrics.get('disk_usage', 50)
        
        current_stability = (cpu_score + memory_score + disk_score) / 3
        
        # Simple trend projection
        projected_stability_5min = max(0, current_stability - 5)
        projected_stability_15min = max(0, current_stability - 10)
        projected_stability_30min = max(0, current_stability - 15)
        
        return {
            'current_stability_score': current_stability,
            'projected_5min': projected_stability_5min,
            'projected_15min': projected_stability_15min,
            'projected_30min': projected_stability_30min,
            'stability_trend': 'declining' if current_stability < 70 else 'stable'
        }
    
    def _predict_resource_exhaustion(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Predict when resources might be exhausted"""
        
        predictions = {}
        
        # CPU exhaustion
        cpu_usage = metrics.get('cpu_usage', 50)
        if cpu_usage > 60:
            time_to_cpu_exhaustion = max(10, (100 - cpu_usage) * 2)  # Simple linear projection
            predictions['cpu'] = {
                'time_to_exhaustion_minutes': time_to_cpu_exhaustion,
                'current_usage': cpu_usage,
                'risk_level': 'high' if time_to_cpu_exhaustion < 30 else 'medium'
            }
        
        # Memory exhaustion
        memory_usage = metrics.get('memory_usage', 50)
        if memory_usage > 70:
            time_to_memory_exhaustion = max(15, (100 - memory_usage) * 3)
            predictions['memory'] = {
                'time_to_exhaustion_minutes': time_to_memory_exhaustion,
                'current_usage': memory_usage,
                'risk_level': 'high' if time_to_memory_exhaustion < 20 else 'medium'
            }
        
        # Disk exhaustion
        disk_usage = metrics.get('disk_usage', 50)
        if disk_usage > 80:
            time_to_disk_exhaustion = max(60, (100 - disk_usage) * 10)
            predictions['disk'] = {
                'time_to_exhaustion_minutes': time_to_disk_exhaustion,
                'current_usage': disk_usage,
                'risk_level': 'high' if time_to_disk_exhaustion < 120 else 'medium'
            }
        
        return predictions
    
    def _identify_improvement_opportunities(self, metrics: Dict[str, float], 
                                         execution_time: float) -> List[str]:
        """Identify opportunities for performance improvement"""
        
        opportunities = []
        
        # Resource-based opportunities
        if metrics.get('cpu_usage', 50) > 75:
            opportunities.append("CPU optimization: Consider algorithm improvements or parallel processing")
        
        if metrics.get('memory_usage', 50) > 80:
            opportunities.append("Memory optimization: Implement memory pooling or streaming processing")
        
        if metrics.get('disk_usage', 50) > 85:
            opportunities.append("Storage optimization: Clean up temporary files or implement compression")
        
        # Execution time opportunities
        if execution_time > 10:
            opportunities.append("Execution time optimization: Break down complex operations or add caching")
        
        if execution_time > 30:
            opportunities.append("Async processing: Consider asynchronous execution for long-running operations")
        
        # System-wide opportunities
        overall_usage = (metrics.get('cpu_usage', 50) + metrics.get('memory_usage', 50)) / 2
        if overall_usage > 70:
            opportunities.append("System scaling: Consider horizontal or vertical scaling options")
        
        return opportunities[:5]  # Return top 5 opportunities
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid
        return str(uuid.uuid4())

# Hook integration functions for Claude Code
def pre_tool_use(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Pre-tool use hook entry point"""
    
    try:
        hook = PerformanceMonitoringHook()
        return hook.pre_tool_use_hook(tool_name, arguments)
    except Exception as e:
        return {
            'monitoring_enabled': False,
            'error': str(e),
            'hook_name': 'performance_monitoring',
            'timestamp': time.time()
        }

def post_tool_use(tool_name: str, arguments: Dict[str, Any], 
                 result: Any, execution_time: float) -> Dict[str, Any]:
    """Post-tool use hook entry point"""
    
    try:
        hook = PerformanceMonitoringHook()
        return hook.post_tool_use_hook(tool_name, arguments, result, execution_time)
    except Exception as e:
        return {
            'monitoring_enabled': False,
            'error': str(e),
            'hook_name': 'performance_monitoring',
            'timestamp': time.time()
        }

# Example usage and testing
def test_performance_monitoring_hook():
    """Test the performance monitoring hook"""
    
    print("🧪 Testing Performance Monitoring Hook...")
    
    hook = PerformanceMonitoringHook()
    
    # Test pre-tool hook
    print("🚀 Testing pre-tool monitoring...")
    pre_result = hook.pre_tool_use_hook('Test', {'test_arg': 'test_value'})
    print(f"   Pre-hook result: {pre_result.get('monitoring_enabled', False)}")
    
    # Simulate tool execution
    time.sleep(0.1)
    
    # Test post-tool hook
    print("📊 Testing post-tool monitoring...")
    post_result = hook.post_tool_use_hook('Test', {'test_arg': 'test_value'}, 'test_result', 0.1)
    print(f"   Post-hook analysis: {post_result.get('performance_analysis', {}).get('performance_tier', 'unknown')}")
    
    # Test slow tool simulation
    print("⏱️ Testing slow tool detection...")
    slow_result = hook.post_tool_use_hook('SlowTool', {}, 'result', 12.0)
    if 'performance_warning' in slow_result:
        print(f"   Slow tool detected: {slow_result['performance_warning']['message']}")
    
    print("✅ Performance monitoring hook test completed!")

if __name__ == "__main__":
    test_performance_monitoring_hook()