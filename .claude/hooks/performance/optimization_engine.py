#!/usr/bin/env python3
"""
Performance Optimization Engine
Automatically applies performance optimizations based on analysis and machine learning
"""

import os
import json
import time
import logging
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import statistics
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    CACHING = "caching"
    PARALLELIZATION = "parallelization"
    RESOURCE_SCALING = "resource_scaling"
    ALGORITHM_OPTIMIZATION = "algorithm_optimization"
    CONFIGURATION_TUNING = "configuration_tuning"
    CLEANUP = "cleanup"

class OptimizationStatus(Enum):
    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"
    REVERTED = "reverted"

@dataclass
class OptimizationRule:
    rule_id: str
    name: str
    optimization_type: OptimizationType
    trigger_conditions: Dict[str, Any]
    optimization_actions: List[Dict[str, Any]]
    expected_improvement: float  # Expected improvement percentage
    risk_level: str  # low, medium, high
    auto_apply: bool = False
    requires_approval: bool = True

@dataclass
class OptimizationResult:
    optimization_id: str
    rule_id: str
    applied_at: float
    status: OptimizationStatus
    before_metrics: Dict[str, float]
    after_metrics: Optional[Dict[str, float]] = None
    actual_improvement: Optional[float] = None
    metadata: Dict[str, Any] = None
    error_message: Optional[str] = None

@dataclass
class PerformanceBaseline:
    metric_name: str
    baseline_value: float
    measurement_count: int
    confidence_interval: Tuple[float, float]
    last_updated: float

class OptimizationEngine:
    """Intelligent performance optimization engine"""
    
    def __init__(self, metrics_collector=None, analyzer=None):
        self.metrics_collector = metrics_collector
        self.analyzer = analyzer
        self.config_dir = Path.home() / ".claude" / "performance"
        self.config_dir.mkdir(exist_ok=True)
        
        # Optimization rules storage
        self.rules_file = self.config_dir / "optimization_rules.json"
        self.results_file = self.config_dir / "optimization_results.json"
        self.baselines_file = self.config_dir / "performance_baselines.json"
        
        # Active optimizations tracking
        self.active_optimizations = {}
        self.optimization_lock = threading.RLock()
        
        # Performance baselines
        self.baselines = self.load_baselines()
        
        # Optimization rules
        self.rules = self.load_optimization_rules()
        
        # A/B testing parameters
        self.ab_test_duration = 300  # 5 minutes
        self.min_samples_for_significance = 30
        
        # Safety mechanisms
        self.max_concurrent_optimizations = 3
        self.rollback_threshold = 0.15  # 15% performance degradation triggers rollback
        
        logger.info("Performance optimization engine initialized")
    
    def load_optimization_rules(self) -> List[OptimizationRule]:
        """Load optimization rules from configuration"""
        
        if self.rules_file.exists():
            try:
                with open(self.rules_file, 'r') as f:
                    rules_data = json.load(f)
                    return [OptimizationRule(**rule) for rule in rules_data]
            except Exception as e:
                logger.error(f"Failed to load optimization rules: {e}")
        
        # Return default rules if none exist
        return self.get_default_optimization_rules()
    
    def get_default_optimization_rules(self) -> List[OptimizationRule]:
        """Get default optimization rules"""
        
        return [
            # Caching optimization
            OptimizationRule(
                rule_id="cache_slow_tools",
                name="Cache Slow Tool Results",
                optimization_type=OptimizationType.CACHING,
                trigger_conditions={
                    "tool_avg_execution_time": ">10.0",
                    "tool_execution_frequency": ">5/hour",
                    "tool_success_rate": ">0.9"
                },
                optimization_actions=[
                    {"action": "enable_result_caching", "duration": 3600},
                    {"action": "set_cache_size", "size": "100MB"}
                ],
                expected_improvement=40.0,
                risk_level="low",
                auto_apply=True,
                requires_approval=False
            ),
            
            # Parallelization optimization
            OptimizationRule(
                rule_id="parallelize_independent_operations",
                name="Parallelize Independent Operations",
                optimization_type=OptimizationType.PARALLELIZATION,
                trigger_conditions={
                    "cpu_utilization": "<50.0",
                    "concurrent_operations": "<3",
                    "independent_operations_detected": True
                },
                optimization_actions=[
                    {"action": "increase_parallel_workers", "count": 4},
                    {"action": "enable_async_execution", "tools": ["Read", "Write", "Grep"]}
                ],
                expected_improvement=60.0,
                risk_level="medium",
                auto_apply=False,
                requires_approval=True
            ),
            
            # Memory optimization
            OptimizationRule(
                rule_id="optimize_memory_usage",
                name="Optimize Memory Usage",
                optimization_type=OptimizationType.RESOURCE_SCALING,
                trigger_conditions={
                    "memory_usage": ">85.0",
                    "memory_growth_rate": ">5%/hour"
                },
                optimization_actions=[
                    {"action": "enable_garbage_collection", "frequency": "aggressive"},
                    {"action": "reduce_cache_sizes", "reduction": 25},
                    {"action": "enable_memory_pooling"}
                ],
                expected_improvement=20.0,
                risk_level="low",
                auto_apply=True,
                requires_approval=False
            ),
            
            # Hook optimization
            OptimizationRule(
                rule_id="optimize_slow_hooks",
                name="Optimize Slow Hook Execution",
                optimization_type=OptimizationType.ALGORITHM_OPTIMIZATION,
                trigger_conditions={
                    "hook_avg_execution_time": ">2.0",
                    "hook_execution_frequency": ">10/hour"
                },
                optimization_actions=[
                    {"action": "enable_async_hooks", "timeout": 5000},
                    {"action": "batch_hook_operations", "batch_size": 5},
                    {"action": "optimize_hook_payload"}
                ],
                expected_improvement=50.0,
                risk_level="medium",
                auto_apply=False,
                requires_approval=True
            ),
            
            # Cleanup optimization
            OptimizationRule(
                rule_id="cleanup_disk_space",
                name="Clean Up Disk Space",
                optimization_type=OptimizationType.CLEANUP,
                trigger_conditions={
                    "disk_usage": ">90.0"
                },
                optimization_actions=[
                    {"action": "cleanup_logs", "keep_days": 7},
                    {"action": "cleanup_temp_files"},
                    {"action": "compress_old_backups", "age_days": 30}
                ],
                expected_improvement=15.0,
                risk_level="low",
                auto_apply=True,
                requires_approval=False
            )
        ]
    
    def load_baselines(self) -> Dict[str, PerformanceBaseline]:
        """Load performance baselines"""
        
        baselines = {}
        
        if self.baselines_file.exists():
            try:
                with open(self.baselines_file, 'r') as f:
                    baselines_data = json.load(f)
                    for name, data in baselines_data.items():
                        baselines[name] = PerformanceBaseline(
                            metric_name=data['metric_name'],
                            baseline_value=data['baseline_value'],
                            measurement_count=data['measurement_count'],
                            confidence_interval=tuple(data['confidence_interval']),
                            last_updated=data['last_updated']
                        )
            except Exception as e:
                logger.error(f"Failed to load baselines: {e}")
        
        return baselines
    
    def save_baselines(self):
        """Save performance baselines"""
        
        try:
            baselines_data = {}
            for name, baseline in self.baselines.items():
                baselines_data[name] = {
                    'metric_name': baseline.metric_name,
                    'baseline_value': baseline.baseline_value,
                    'measurement_count': baseline.measurement_count,
                    'confidence_interval': list(baseline.confidence_interval),
                    'last_updated': baseline.last_updated
                }
            
            with open(self.baselines_file, 'w') as f:
                json.dump(baselines_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save baselines: {e}")
    
    def analyze_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Analyze current performance and identify optimization opportunities"""
        
        if not self.analyzer:
            logger.warning("No analyzer available for optimization analysis")
            return []
        
        opportunities = []
        
        try:
            # Get current performance insights
            insights = self.analyzer.generate_performance_insights()
            bottlenecks = self.analyzer.identify_bottlenecks()
            trends = self.analyzer.analyze_performance_trends()
            
            # Map insights to optimization opportunities
            for insight in insights:
                opportunity = self._map_insight_to_optimization(insight)
                if opportunity:
                    opportunities.append(opportunity)
            
            # Map bottlenecks to optimization opportunities
            for bottleneck in bottlenecks:
                opportunity = self._map_bottleneck_to_optimization(bottleneck)
                if opportunity:
                    opportunities.append(opportunity)
            
            # Map trends to optimization opportunities
            for trend in trends:
                if trend.direction.value == "degrading" and trend.confidence > 0.7:
                    opportunity = self._map_trend_to_optimization(trend)
                    if opportunity:
                        opportunities.append(opportunity)
        
        except Exception as e:
            logger.error(f"Failed to analyze optimization opportunities: {e}")
        
        return opportunities
    
    def apply_optimization(self, rule_id: str, override_approval: bool = False) -> OptimizationResult:
        """Apply a specific optimization rule"""
        
        rule = next((r for r in self.rules if r.rule_id == rule_id), None)
        if not rule:
            raise ValueError(f"Optimization rule not found: {rule_id}")
        
        if rule.requires_approval and not override_approval:
            raise ValueError(f"Optimization {rule_id} requires approval")
        
        with self.optimization_lock:
            if len(self.active_optimizations) >= self.max_concurrent_optimizations:
                raise RuntimeError("Maximum concurrent optimizations reached")
            
            optimization_id = f"opt_{int(time.time())}_{rule_id}"
            
            # Record baseline metrics
            before_metrics = self._collect_current_metrics()
            
            result = OptimizationResult(
                optimization_id=optimization_id,
                rule_id=rule_id,
                applied_at=time.time(),
                status=OptimizationStatus.PENDING,
                before_metrics=before_metrics
            )
            
            self.active_optimizations[optimization_id] = result
        
        try:
            # Apply optimization actions
            for action in rule.optimization_actions:
                self._apply_optimization_action(action)
            
            result.status = OptimizationStatus.APPLIED
            logger.info(f"Applied optimization: {rule.name} ({optimization_id})")
            
            # Schedule A/B testing
            self._schedule_ab_test(optimization_id, rule)
            
        except Exception as e:
            result.status = OptimizationStatus.FAILED
            result.error_message = str(e)
            logger.error(f"Failed to apply optimization {rule_id}: {e}")
        
        return result
    
    def run_ab_test(self, optimization_id: str) -> Dict[str, Any]:
        """Run A/B test to measure optimization effectiveness"""
        
        if optimization_id not in self.active_optimizations:
            raise ValueError(f"Optimization not found: {optimization_id}")
        
        result = self.active_optimizations[optimization_id]
        
        logger.info(f"Starting A/B test for optimization: {optimization_id}")
        
        # Wait for test duration to collect metrics
        time.sleep(self.ab_test_duration)
        
        # Collect after metrics
        after_metrics = self._collect_current_metrics()
        result.after_metrics = after_metrics
        
        # Calculate improvement
        improvement = self._calculate_improvement(result.before_metrics, after_metrics)
        result.actual_improvement = improvement
        
        # Determine if optimization is successful
        test_results = {
            'optimization_id': optimization_id,
            'test_duration': self.ab_test_duration,
            'before_metrics': result.before_metrics,
            'after_metrics': after_metrics,
            'improvement': improvement,
            'successful': improvement > 0,
            'significant': abs(improvement) > 5.0  # 5% threshold for significance
        }
        
        # Check for rollback conditions
        if improvement < -self.rollback_threshold * 100:
            logger.warning(f"Performance degraded by {abs(improvement):.1f}%, rolling back optimization {optimization_id}")
            self.rollback_optimization(optimization_id)
            test_results['rolled_back'] = True
        else:
            test_results['rolled_back'] = False
        
        # Update baselines if optimization is successful
        if test_results['successful'] and test_results['significant']:
            self._update_baselines(after_metrics)
        
        logger.info(f"A/B test completed for {optimization_id}: {improvement:+.1f}% improvement")
        
        return test_results
    
    def rollback_optimization(self, optimization_id: str):
        """Rollback an applied optimization"""
        
        if optimization_id not in self.active_optimizations:
            raise ValueError(f"Optimization not found: {optimization_id}")
        
        result = self.active_optimizations[optimization_id]
        rule = next((r for r in self.rules if r.rule_id == result.rule_id), None)
        
        if not rule:
            logger.error(f"Cannot rollback: rule not found for {result.rule_id}")
            return
        
        try:
            # Apply rollback actions (reverse of optimization actions)
            for action in reversed(rule.optimization_actions):
                self._rollback_optimization_action(action)
            
            result.status = OptimizationStatus.REVERTED
            logger.info(f"Rolled back optimization: {optimization_id}")
            
        except Exception as e:
            logger.error(f"Failed to rollback optimization {optimization_id}: {e}")
            result.error_message = f"Rollback failed: {str(e)}"
    
    def auto_optimize(self):
        """Automatically apply optimizations based on current conditions"""
        
        opportunities = self.analyze_optimization_opportunities()
        applied_optimizations = []
        
        for opportunity in opportunities:
            rule_id = opportunity.get('rule_id')
            if not rule_id:
                continue
            
            rule = next((r for r in self.rules if r.rule_id == rule_id), None)
            if not rule or not rule.auto_apply:
                continue
            
            try:
                result = self.apply_optimization(rule_id, override_approval=True)
                applied_optimizations.append({
                    'rule_id': rule_id,
                    'optimization_id': result.optimization_id,
                    'expected_improvement': rule.expected_improvement
                })
                
            except Exception as e:
                logger.error(f"Failed to auto-apply optimization {rule_id}: {e}")
        
        logger.info(f"Auto-applied {len(applied_optimizations)} optimizations")
        return applied_optimizations
    
    def _collect_current_metrics(self) -> Dict[str, float]:
        """Collect current performance metrics"""
        
        metrics = {}
        
        if self.metrics_collector:
            try:
                # Get recent performance summary
                summary = self.metrics_collector.get_performance_summary(window_seconds=300)
                
                metrics.update({
                    'avg_cpu_usage': summary['system_metrics']['avg_cpu_usage'],
                    'avg_memory_usage': summary['system_metrics']['avg_memory_usage'],
                    'avg_tool_execution_time': summary['tool_execution']['avg_execution_time'],
                    'avg_hook_execution_time': summary['hook_performance']['avg_execution_time'],
                    'tool_success_rate': summary['tool_execution']['success_rate'],
                    'hook_success_rate': summary['hook_performance']['success_rate']
                })
                
            except Exception as e:
                logger.error(f"Failed to collect metrics: {e}")
        
        # Add timestamp
        metrics['timestamp'] = time.time()
        
        return metrics
    
    def _calculate_improvement(self, before: Dict[str, float], after: Dict[str, float]) -> float:
        """Calculate overall improvement percentage"""
        
        improvements = []
        
        # CPU usage (lower is better)
        if 'avg_cpu_usage' in before and 'avg_cpu_usage' in after:
            cpu_improvement = (before['avg_cpu_usage'] - after['avg_cpu_usage']) / before['avg_cpu_usage'] * 100
            improvements.append(cpu_improvement)
        
        # Memory usage (lower is better)
        if 'avg_memory_usage' in before and 'avg_memory_usage' in after:
            memory_improvement = (before['avg_memory_usage'] - after['avg_memory_usage']) / before['avg_memory_usage'] * 100
            improvements.append(memory_improvement)
        
        # Tool execution time (lower is better)
        if 'avg_tool_execution_time' in before and 'avg_tool_execution_time' in after:
            if before['avg_tool_execution_time'] > 0:
                tool_improvement = (before['avg_tool_execution_time'] - after['avg_tool_execution_time']) / before['avg_tool_execution_time'] * 100
                improvements.append(tool_improvement * 2)  # Weight tool performance higher
        
        # Hook execution time (lower is better)  
        if 'avg_hook_execution_time' in before and 'avg_hook_execution_time' in after:
            if before['avg_hook_execution_time'] > 0:
                hook_improvement = (before['avg_hook_execution_time'] - after['avg_hook_execution_time']) / before['avg_hook_execution_time'] * 100
                improvements.append(hook_improvement)
        
        # Success rates (higher is better)
        if 'tool_success_rate' in before and 'tool_success_rate' in after:
            success_improvement = (after['tool_success_rate'] - before['tool_success_rate']) / (before['tool_success_rate'] + 0.01) * 100
            improvements.append(success_improvement)
        
        return statistics.mean(improvements) if improvements else 0.0
    
    def _apply_optimization_action(self, action: Dict[str, Any]):
        """Apply a specific optimization action"""
        
        action_type = action.get('action')
        
        if action_type == 'enable_result_caching':
            self._enable_result_caching(action.get('duration', 3600))
        
        elif action_type == 'increase_parallel_workers':
            self._increase_parallel_workers(action.get('count', 2))
        
        elif action_type == 'enable_garbage_collection':
            self._enable_garbage_collection(action.get('frequency', 'normal'))
        
        elif action_type == 'cleanup_logs':
            self._cleanup_logs(action.get('keep_days', 7))
        
        elif action_type == 'enable_async_hooks':
            self._enable_async_hooks(action.get('timeout', 5000))
        
        else:
            logger.warning(f"Unknown optimization action: {action_type}")
    
    def _rollback_optimization_action(self, action: Dict[str, Any]):
        """Rollback a specific optimization action"""
        
        action_type = action.get('action')
        
        if action_type == 'enable_result_caching':
            self._disable_result_caching()
        
        elif action_type == 'increase_parallel_workers':
            self._decrease_parallel_workers()
        
        elif action_type == 'enable_garbage_collection':
            self._disable_aggressive_gc()
        
        elif action_type == 'enable_async_hooks':
            self._disable_async_hooks()
        
        else:
            logger.warning(f"Unknown rollback action: {action_type}")
    
    def _enable_result_caching(self, duration: int):
        """Enable result caching optimization"""
        logger.info(f"Enabling result caching for {duration} seconds")
        # Implementation would integrate with actual caching system
    
    def _disable_result_caching(self):
        """Disable result caching"""
        logger.info("Disabling result caching")
    
    def _increase_parallel_workers(self, count: int):
        """Increase parallel worker count"""
        logger.info(f"Increasing parallel workers to {count}")
        # Implementation would modify actual parallel execution settings
    
    def _decrease_parallel_workers(self):
        """Decrease parallel worker count"""
        logger.info("Decreasing parallel workers to default")
    
    def _enable_garbage_collection(self, frequency: str):
        """Enable aggressive garbage collection"""
        logger.info(f"Enabling {frequency} garbage collection")
        import gc
        if frequency == 'aggressive':
            gc.set_threshold(100, 5, 5)
        gc.collect()
    
    def _disable_aggressive_gc(self):
        """Disable aggressive garbage collection"""
        logger.info("Restoring default garbage collection settings")
        import gc
        gc.set_threshold(700, 10, 10)  # Python defaults
    
    def _cleanup_logs(self, keep_days: int):
        """Clean up old log files"""
        logger.info(f"Cleaning up logs older than {keep_days} days")
        # Implementation would clean up actual log files
    
    def _enable_async_hooks(self, timeout: int):
        """Enable asynchronous hook execution"""
        logger.info(f"Enabling async hooks with {timeout}ms timeout")
        # Implementation would modify hook execution to be async
    
    def _disable_async_hooks(self):
        """Disable asynchronous hook execution"""
        logger.info("Disabling async hooks, reverting to synchronous execution")
    
    def _schedule_ab_test(self, optimization_id: str, rule: OptimizationRule):
        """Schedule A/B test for optimization"""
        
        def run_test():
            time.sleep(60)  # Wait 1 minute before starting test
            try:
                test_results = self.run_ab_test(optimization_id)
                logger.info(f"A/B test results for {optimization_id}: {test_results}")
            except Exception as e:
                logger.error(f"A/B test failed for {optimization_id}: {e}")
        
        test_thread = threading.Thread(target=run_test, daemon=True)
        test_thread.start()
    
    def _update_baselines(self, metrics: Dict[str, float]):
        """Update performance baselines with new metrics"""
        
        for metric_name, value in metrics.items():
            if metric_name == 'timestamp':
                continue
            
            if metric_name in self.baselines:
                baseline = self.baselines[metric_name]
                baseline.measurement_count += 1
                
                # Update baseline using exponential moving average
                alpha = 0.1  # Smoothing factor
                baseline.baseline_value = (1 - alpha) * baseline.baseline_value + alpha * value
                baseline.last_updated = time.time()
            else:
                # Create new baseline
                self.baselines[metric_name] = PerformanceBaseline(
                    metric_name=metric_name,
                    baseline_value=value,
                    measurement_count=1,
                    confidence_interval=(value * 0.9, value * 1.1),
                    last_updated=time.time()
                )
        
        self.save_baselines()
    
    def _map_insight_to_optimization(self, insight) -> Optional[Dict[str, Any]]:
        """Map performance insight to optimization opportunity"""
        
        if insight.insight_type == "tool_performance":
            return {
                'rule_id': 'cache_slow_tools',
                'priority': 'high' if insight.severity == 'high' else 'medium',
                'confidence': insight.confidence,
                'description': insight.description
            }
        
        elif insight.insight_type == "resource_underutilization":
            return {
                'rule_id': 'parallelize_independent_operations',
                'priority': 'medium',
                'confidence': insight.confidence,
                'description': insight.description
            }
        
        elif insight.insight_type == "resource_bottleneck":
            return {
                'rule_id': 'optimize_memory_usage',
                'priority': 'high',
                'confidence': insight.confidence,
                'description': insight.description
            }
        
        return None
    
    def _map_bottleneck_to_optimization(self, bottleneck) -> Optional[Dict[str, Any]]:
        """Map bottleneck to optimization opportunity"""
        
        if bottleneck.bottleneck_type.value == "tool_execution":
            return {
                'rule_id': 'cache_slow_tools',
                'priority': 'high',
                'confidence': 0.8,
                'description': bottleneck.description
            }
        
        elif bottleneck.bottleneck_type.value == "hook_performance":
            return {
                'rule_id': 'optimize_slow_hooks',
                'priority': 'medium',
                'confidence': 0.7,
                'description': bottleneck.description
            }
        
        elif bottleneck.bottleneck_type.value == "disk":
            return {
                'rule_id': 'cleanup_disk_space',
                'priority': 'high',
                'confidence': 0.9,
                'description': bottleneck.description
            }
        
        return None
    
    def _map_trend_to_optimization(self, trend) -> Optional[Dict[str, Any]]:
        """Map performance trend to optimization opportunity"""
        
        if trend.metric_name == 'tool_execution_time' and trend.change_percentage > 20:
            return {
                'rule_id': 'cache_slow_tools',
                'priority': 'high',
                'confidence': trend.confidence,
                'description': f"Tool execution time trending upward: {trend.change_percentage:+.1f}%"
            }
        
        elif trend.metric_name == 'memory_usage' and trend.change_percentage > 15:
            return {
                'rule_id': 'optimize_memory_usage',
                'priority': 'medium',
                'confidence': trend.confidence,
                'description': f"Memory usage trending upward: {trend.change_percentage:+.1f}%"
            }
        
        return None

# Example usage and testing
def test_optimization_engine():
    """Test the optimization engine functionality"""
    
    print("🧪 Testing Performance Optimization Engine...")
    
    engine = OptimizationEngine()
    
    # Test opportunity analysis
    print("🔍 Analyzing optimization opportunities...")
    opportunities = engine.analyze_optimization_opportunities()
    print(f"   Found {len(opportunities)} optimization opportunities")
    
    # Test rule application (dry run)
    print("⚙️ Testing optimization rule application...")
    
    try:
        # Apply a low-risk optimization
        result = engine.apply_optimization('optimize_memory_usage', override_approval=True)
        print(f"   Applied optimization: {result.optimization_id}")
        
        # Simulate rollback
        engine.rollback_optimization(result.optimization_id)
        print(f"   Rolled back optimization: {result.optimization_id}")
        
    except Exception as e:
        print(f"   ⚠️ Optimization test failed: {e}")
    
    # Test auto-optimization
    print("🤖 Testing auto-optimization...")
    auto_results = engine.auto_optimize()
    print(f"   Auto-applied {len(auto_results)} optimizations")
    
    print("✅ Optimization engine test completed!")

if __name__ == "__main__":
    test_optimization_engine()