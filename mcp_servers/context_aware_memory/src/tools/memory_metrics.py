"""
Memory Metrics and Performance Monitoring
Advanced metrics tracking for memory system performance
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import numpy as np
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics tracked"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ACCURACY = "accuracy"
    MEMORY_USAGE = "memory_usage"
    PATTERN_EFFECTIVENESS = "pattern_effectiveness"
    FEDERATION_HEALTH = "federation_health"
    PRIVACY_COMPLIANCE = "privacy_compliance"


@dataclass
class MetricSnapshot:
    """Snapshot of a metric at a point in time"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class PerformanceReport:
    """Comprehensive performance report"""
    report_id: str
    period_start: datetime
    period_end: datetime
    metrics_summary: Dict[str, Any]
    recommendations: List[str]
    anomalies: List[Dict[str, Any]]
    trends: Dict[str, str]


class MemoryMetricsCollector:
    """Collects and analyzes metrics for the memory system"""
    
    def __init__(self, window_size: int = 1000, anomaly_threshold: float = 3.0):
        self.window_size = window_size
        self.anomaly_threshold = anomaly_threshold
        
        # Metric storage
        self.metrics: Dict[MetricType, deque] = {
            metric_type: deque(maxlen=window_size)
            for metric_type in MetricType
        }
        
        # Performance baselines
        self.baselines: Dict[MetricType, float] = {}
        
        # Anomaly detection
        self.anomaly_history: List[Dict[str, Any]] = []
        
        # Real-time stats
        self.real_time_stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'average_latency_ms': 0.0,
            'peak_memory_mb': 0.0,
            'active_patterns': 0,
            'federation_nodes': 0,
            'privacy_violations': 0
        }
        
        # Metric aggregations
        self.hourly_aggregates: Dict[str, List[float]] = defaultdict(list)
        self.daily_aggregates: Dict[str, List[float]] = defaultdict(list)
    
    async def record_metric(self, metric_type: MetricType, value: float, 
                          context: Optional[Dict[str, Any]] = None,
                          tags: Optional[List[str]] = None):
        """Record a metric value"""
        snapshot = MetricSnapshot(
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(),
            context=context or {},
            tags=tags or []
        )
        
        self.metrics[metric_type].append(snapshot)
        
        # Check for anomalies
        if await self._is_anomaly(metric_type, value):
            await self._record_anomaly(snapshot)
        
        # Update real-time stats
        await self._update_real_time_stats(metric_type, value)
        
        # Aggregate for reporting
        await self._aggregate_metric(snapshot)
    
    async def record_operation_latency(self, operation: str, latency_ms: float, 
                                     success: bool = True):
        """Record latency for an operation"""
        await self.record_metric(
            MetricType.LATENCY,
            latency_ms,
            context={'operation': operation, 'success': success},
            tags=['operation_latency', operation]
        )
        
        self.real_time_stats['total_operations'] += 1
        if success:
            self.real_time_stats['successful_operations'] += 1
        else:
            self.real_time_stats['failed_operations'] += 1
    
    async def record_memory_usage(self, usage_mb: float, component: str):
        """Record memory usage for a component"""
        await self.record_metric(
            MetricType.MEMORY_USAGE,
            usage_mb,
            context={'component': component},
            tags=['memory', component]
        )
        
        # Update peak memory
        if usage_mb > self.real_time_stats['peak_memory_mb']:
            self.real_time_stats['peak_memory_mb'] = usage_mb
    
    async def record_pattern_effectiveness(self, pattern_id: str, effectiveness: float,
                                         pattern_type: str):
        """Record pattern effectiveness metric"""
        await self.record_metric(
            MetricType.PATTERN_EFFECTIVENESS,
            effectiveness,
            context={'pattern_id': pattern_id, 'pattern_type': pattern_type},
            tags=['pattern', pattern_type]
        )
    
    async def record_federation_health(self, node_id: str, health_score: float,
                                     trust_level: float):
        """Record federation node health"""
        await self.record_metric(
            MetricType.FEDERATION_HEALTH,
            health_score,
            context={'node_id': node_id, 'trust_level': trust_level},
            tags=['federation', 'node_health']
        )
    
    async def record_privacy_compliance(self, operation: str, compliant: bool,
                                      privacy_level: str):
        """Record privacy compliance metric"""
        compliance_score = 1.0 if compliant else 0.0
        await self.record_metric(
            MetricType.PRIVACY_COMPLIANCE,
            compliance_score,
            context={'operation': operation, 'privacy_level': privacy_level},
            tags=['privacy', 'compliance']
        )
        
        if not compliant:
            self.real_time_stats['privacy_violations'] += 1
    
    async def generate_performance_report(self, period_hours: int = 24) -> PerformanceReport:
        """Generate comprehensive performance report"""
        period_end = datetime.now()
        period_start = period_end - timedelta(hours=period_hours)
        
        # Collect metrics for period
        period_metrics = await self._collect_period_metrics(period_start, period_end)
        
        # Generate summary
        metrics_summary = await self._generate_metrics_summary(period_metrics)
        
        # Detect trends
        trends = await self._detect_trends(period_metrics)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(metrics_summary, trends)
        
        # Find anomalies in period
        period_anomalies = [
            a for a in self.anomaly_history
            if period_start <= datetime.fromisoformat(a['timestamp']) <= period_end
        ]
        
        report = PerformanceReport(
            report_id=f"report_{int(period_end.timestamp())}",
            period_start=period_start,
            period_end=period_end,
            metrics_summary=metrics_summary,
            recommendations=recommendations,
            anomalies=period_anomalies,
            trends=trends
        )
        
        logger.info(f"Generated performance report for {period_hours} hour period")
        
        return report
    
    async def get_real_time_dashboard(self) -> Dict[str, Any]:
        """Get real-time metrics dashboard data"""
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'system_health': await self._calculate_system_health(),
            'real_time_stats': self.real_time_stats.copy(),
            'recent_metrics': {},
            'alerts': []
        }
        
        # Add recent metrics
        for metric_type in MetricType:
            recent = list(self.metrics[metric_type])[-10:]  # Last 10 values
            if recent:
                values = [m.value for m in recent]
                dashboard['recent_metrics'][metric_type.value] = {
                    'current': values[-1],
                    'average': np.mean(values),
                    'min': min(values),
                    'max': max(values),
                    'trend': 'up' if len(values) > 1 and values[-1] > values[0] else 'down'
                }
        
        # Add alerts for anomalies
        recent_anomalies = [
            a for a in self.anomaly_history[-5:]  # Last 5 anomalies
            if (datetime.now() - datetime.fromisoformat(a['timestamp'])).seconds < 3600
        ]
        
        for anomaly in recent_anomalies:
            dashboard['alerts'].append({
                'type': 'anomaly',
                'severity': 'warning' if anomaly['severity'] < 0.8 else 'critical',
                'message': f"Anomaly detected in {anomaly['metric_type']}: {anomaly['description']}",
                'timestamp': anomaly['timestamp']
            })
        
        return dashboard
    
    async def optimize_based_on_metrics(self) -> Dict[str, Any]:
        """Generate optimization suggestions based on metrics"""
        optimizations = {
            'suggestions': [],
            'expected_improvements': {},
            'priority_actions': []
        }
        
        # Analyze latency metrics
        latency_metrics = [m for m in self.metrics[MetricType.LATENCY] if m]
        if latency_metrics:
            avg_latency = np.mean([m.value for m in latency_metrics])
            if avg_latency > 100:  # Over 100ms average
                optimizations['suggestions'].append({
                    'area': 'latency',
                    'suggestion': 'Enable caching for frequently accessed memories',
                    'expected_improvement': '30-50% latency reduction'
                })
                optimizations['priority_actions'].append('enable_caching')
        
        # Analyze memory usage
        memory_metrics = [m for m in self.metrics[MetricType.MEMORY_USAGE] if m]
        if memory_metrics:
            avg_memory = np.mean([m.value for m in memory_metrics])
            if avg_memory > 500:  # Over 500MB average
                optimizations['suggestions'].append({
                    'area': 'memory',
                    'suggestion': 'Implement memory pruning for old patterns',
                    'expected_improvement': '20-30% memory reduction'
                })
                optimizations['priority_actions'].append('memory_pruning')
        
        # Analyze pattern effectiveness
        pattern_metrics = [m for m in self.metrics[MetricType.PATTERN_EFFECTIVENESS] if m]
        if pattern_metrics:
            low_effectiveness = [m for m in pattern_metrics if m.value < 0.5]
            if len(low_effectiveness) > len(pattern_metrics) * 0.3:  # >30% low effectiveness
                optimizations['suggestions'].append({
                    'area': 'patterns',
                    'suggestion': 'Retrain patterns with low effectiveness',
                    'expected_improvement': '15-25% accuracy improvement'
                })
                optimizations['priority_actions'].append('pattern_retraining')
        
        # Calculate expected improvements
        optimizations['expected_improvements'] = {
            'latency': '-30%' if 'enable_caching' in optimizations['priority_actions'] else '0%',
            'memory': '-25%' if 'memory_pruning' in optimizations['priority_actions'] else '0%',
            'accuracy': '+20%' if 'pattern_retraining' in optimizations['priority_actions'] else '0%'
        }
        
        return optimizations
    
    # Helper methods
    
    async def _is_anomaly(self, metric_type: MetricType, value: float) -> bool:
        """Detect if a value is an anomaly"""
        recent_values = [m.value for m in list(self.metrics[metric_type])[-50:]]
        
        if len(recent_values) < 10:
            return False
        
        # Calculate z-score
        mean = np.mean(recent_values)
        std = np.std(recent_values)
        
        if std == 0:
            return False
        
        z_score = abs((value - mean) / std)
        
        return z_score > self.anomaly_threshold
    
    async def _record_anomaly(self, snapshot: MetricSnapshot):
        """Record an anomaly"""
        recent_values = [m.value for m in list(self.metrics[snapshot.metric_type])[-50:]]
        mean = np.mean(recent_values)
        std = np.std(recent_values)
        
        anomaly = {
            'timestamp': snapshot.timestamp.isoformat(),
            'metric_type': snapshot.metric_type.value,
            'value': snapshot.value,
            'expected_range': f"{mean - 2*std:.2f} - {mean + 2*std:.2f}",
            'severity': min(1.0, abs(snapshot.value - mean) / (3 * std)) if std > 0 else 0.5,
            'description': f"Value {snapshot.value:.2f} outside expected range",
            'context': snapshot.context
        }
        
        self.anomaly_history.append(anomaly)
        
        # Keep only recent anomalies
        if len(self.anomaly_history) > 100:
            self.anomaly_history = self.anomaly_history[-100:]
        
        logger.warning(f"Anomaly detected: {anomaly['description']}")
    
    async def _update_real_time_stats(self, metric_type: MetricType, value: float):
        """Update real-time statistics"""
        if metric_type == MetricType.LATENCY:
            # Update average latency
            recent_latencies = [
                m.value for m in list(self.metrics[MetricType.LATENCY])[-100:]
            ]
            if recent_latencies:
                self.real_time_stats['average_latency_ms'] = np.mean(recent_latencies)
        
        elif metric_type == MetricType.PATTERN_EFFECTIVENESS:
            # Count active patterns
            recent_patterns = list(self.metrics[MetricType.PATTERN_EFFECTIVENESS])[-50:]
            unique_patterns = set(m.context.get('pattern_id') for m in recent_patterns if m.context)
            self.real_time_stats['active_patterns'] = len(unique_patterns)
        
        elif metric_type == MetricType.FEDERATION_HEALTH:
            # Count federation nodes
            recent_nodes = list(self.metrics[MetricType.FEDERATION_HEALTH])[-20:]
            unique_nodes = set(m.context.get('node_id') for m in recent_nodes if m.context)
            self.real_time_stats['federation_nodes'] = len(unique_nodes)
    
    async def _aggregate_metric(self, snapshot: MetricSnapshot):
        """Aggregate metric for reporting"""
        hour_key = snapshot.timestamp.strftime('%Y-%m-%d-%H')
        day_key = snapshot.timestamp.strftime('%Y-%m-%d')
        
        # Hourly aggregation
        self.hourly_aggregates[f"{snapshot.metric_type.value}_{hour_key}"].append(snapshot.value)
        
        # Daily aggregation
        self.daily_aggregates[f"{snapshot.metric_type.value}_{day_key}"].append(snapshot.value)
        
        # Cleanup old aggregates
        await self._cleanup_old_aggregates()
    
    async def _cleanup_old_aggregates(self):
        """Remove old aggregate data"""
        cutoff_hourly = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d-%H')
        cutoff_daily = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Clean hourly
        hourly_keys_to_remove = [
            k for k in self.hourly_aggregates.keys()
            if k.split('_')[-1] < cutoff_hourly
        ]
        for k in hourly_keys_to_remove:
            del self.hourly_aggregates[k]
        
        # Clean daily
        daily_keys_to_remove = [
            k for k in self.daily_aggregates.keys()
            if k.split('_')[-1] < cutoff_daily
        ]
        for k in daily_keys_to_remove:
            del self.daily_aggregates[k]
    
    async def _collect_period_metrics(self, start: datetime, end: datetime) -> Dict[MetricType, List[MetricSnapshot]]:
        """Collect metrics for a specific period"""
        period_metrics = {}
        
        for metric_type, metrics_deque in self.metrics.items():
            period_metrics[metric_type] = [
                m for m in metrics_deque
                if start <= m.timestamp <= end
            ]
        
        return period_metrics
    
    async def _generate_metrics_summary(self, period_metrics: Dict[MetricType, List[MetricSnapshot]]) -> Dict[str, Any]:
        """Generate summary statistics for metrics"""
        summary = {}
        
        for metric_type, snapshots in period_metrics.items():
            if snapshots:
                values = [s.value for s in snapshots]
                metric_summary = {
                    'count': len(values),
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': min(values),
                    'max': max(values)
                }
                
                # Only add percentiles if we have enough data points
                if len(values) >= 3:
                    metric_summary['percentiles'] = {
                        'p50': np.percentile(values, 50),
                        'p95': np.percentile(values, 95),
                        'p99': np.percentile(values, 99)
                    }
                    # Add percentiles to main level for backward compatibility
                    metric_summary['p50'] = metric_summary['percentiles']['p50']
                    metric_summary['p95'] = metric_summary['percentiles']['p95']
                    metric_summary['p99'] = metric_summary['percentiles']['p99']
                else:
                    # Use mean as fallback for percentiles
                    metric_summary['p50'] = metric_summary['mean']
                    metric_summary['p95'] = metric_summary['mean']
                    metric_summary['p99'] = metric_summary['mean']
                
                summary[metric_type.value] = metric_summary
            else:
                summary[metric_type.value] = {'count': 0}
        
        return summary
    
    async def _detect_trends(self, period_metrics: Dict[MetricType, List[MetricSnapshot]]) -> Dict[str, str]:
        """Detect trends in metrics"""
        trends = {}
        
        for metric_type, snapshots in period_metrics.items():
            if len(snapshots) > 10:
                values = [s.value for s in snapshots]
                timestamps = [s.timestamp.timestamp() for s in snapshots]
                
                # Simple linear regression for trend
                if len(set(timestamps)) > 1:  # Need at least 2 different timestamps
                    slope = np.polyfit(timestamps, values, 1)[0]
                    
                    if abs(slope) < 0.001:
                        trends[metric_type.value] = "stable"
                    elif slope > 0:
                        trends[metric_type.value] = "increasing"
                    else:
                        trends[metric_type.value] = "decreasing"
                else:
                    trends[metric_type.value] = "insufficient_data"
            else:
                trends[metric_type.value] = "insufficient_data"
        
        return trends
    
    async def _generate_recommendations(self, summary: Dict[str, Any], trends: Dict[str, str]) -> List[str]:
        """Generate recommendations based on metrics and trends"""
        recommendations = []
        
        # Latency recommendations
        if MetricType.LATENCY.value in summary and summary[MetricType.LATENCY.value]['count'] > 0:
            latency_stats = summary[MetricType.LATENCY.value]
            if latency_stats['p95'] > 200:  # 95th percentile over 200ms
                recommendations.append("High latency detected - consider implementing request batching")
            if trends.get(MetricType.LATENCY.value) == "increasing":
                recommendations.append("Latency trend increasing - investigate performance bottlenecks")
        
        # Memory recommendations
        if MetricType.MEMORY_USAGE.value in summary and summary[MetricType.MEMORY_USAGE.value]['count'] > 0:
            memory_stats = summary[MetricType.MEMORY_USAGE.value]
            if memory_stats['max'] > 1000:  # Over 1GB
                recommendations.append("High memory usage detected - implement memory limits")
            if trends.get(MetricType.MEMORY_USAGE.value) == "increasing":
                recommendations.append("Memory usage trending up - check for memory leaks")
        
        # Pattern effectiveness recommendations
        if MetricType.PATTERN_EFFECTIVENESS.value in summary and summary[MetricType.PATTERN_EFFECTIVENESS.value]['count'] > 0:
            pattern_stats = summary[MetricType.PATTERN_EFFECTIVENESS.value]
            if pattern_stats['mean'] < 0.6:  # Low average effectiveness
                recommendations.append("Low pattern effectiveness - review and update learning algorithms")
        
        # Federation health recommendations
        if MetricType.FEDERATION_HEALTH.value in summary and summary[MetricType.FEDERATION_HEALTH.value]['count'] > 0:
            federation_stats = summary[MetricType.FEDERATION_HEALTH.value]
            if federation_stats['mean'] < 0.7:  # Low average health
                recommendations.append("Federation health below threshold - review node connectivity")
        
        # Privacy compliance recommendations
        if MetricType.PRIVACY_COMPLIANCE.value in summary and summary[MetricType.PRIVACY_COMPLIANCE.value]['count'] > 0:
            privacy_stats = summary[MetricType.PRIVACY_COMPLIANCE.value]
            if privacy_stats['mean'] < 0.95:  # Less than 95% compliance
                recommendations.append("Privacy compliance issues detected - strengthen privacy controls")
        
        return recommendations
    
    async def _calculate_system_health(self) -> float:
        """Calculate overall system health score"""
        health_factors = []
        
        # Factor 1: Success rate
        if self.real_time_stats['total_operations'] > 0:
            success_rate = self.real_time_stats['successful_operations'] / self.real_time_stats['total_operations']
            health_factors.append(success_rate)
        
        # Factor 2: Latency health
        if self.real_time_stats['average_latency_ms'] > 0:
            latency_health = min(1.0, 100 / self.real_time_stats['average_latency_ms'])  # 100ms as baseline
            health_factors.append(latency_health)
        
        # Factor 3: Memory health
        if self.real_time_stats['peak_memory_mb'] > 0:
            memory_health = min(1.0, 500 / self.real_time_stats['peak_memory_mb'])  # 500MB as baseline
            health_factors.append(memory_health)
        
        # Factor 4: Privacy health
        privacy_health = 1.0 - min(1.0, self.real_time_stats['privacy_violations'] / 100)  # 100 violations = 0 health
        health_factors.append(privacy_health)
        
        # Calculate weighted health score
        if health_factors:
            weights = [0.3, 0.25, 0.2, 0.25]  # Success rate weighted highest
            health_score = sum(f * w for f, w in zip(health_factors, weights[:len(health_factors)]))
            return min(1.0, max(0.0, health_score))
        
        return 0.5  # Default health score
    
    async def export_metrics(self, format: str = "json") -> Dict[str, Any]:
        """Export metrics for external analysis"""
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'metrics': {},
            'aggregates': {
                'hourly': dict(self.hourly_aggregates),
                'daily': dict(self.daily_aggregates)
            },
            'anomalies': self.anomaly_history,
            'real_time_stats': self.real_time_stats.copy(),
            'baselines': self.baselines.copy()
        }
        
        # Export recent metrics
        for metric_type in MetricType:
            recent = list(self.metrics[metric_type])[-1000:]  # Last 1000 values
            export_data['metrics'][metric_type.value] = [
                {
                    'value': m.value,
                    'timestamp': m.timestamp.isoformat(),
                    'context': m.context,
                    'tags': m.tags
                }
                for m in recent
            ]
        
        return export_data
    
    def set_baseline(self, metric_type: MetricType, baseline_value: float):
        """Set performance baseline for a metric"""
        self.baselines[metric_type] = baseline_value
        logger.info(f"Set baseline for {metric_type.value}: {baseline_value}")
    
    async def compare_to_baseline(self, metric_type: MetricType) -> Dict[str, Any]:
        """Compare current performance to baseline"""
        if metric_type not in self.baselines:
            return {'error': 'No baseline set for this metric'}
        
        recent_values = [m.value for m in list(self.metrics[metric_type])[-100:]]
        if not recent_values:
            return {'error': 'No recent data for comparison'}
        
        baseline = self.baselines[metric_type]
        current_mean = np.mean(recent_values)
        
        comparison = {
            'baseline': baseline,
            'current': current_mean,
            'difference': current_mean - baseline,
            'percentage_change': ((current_mean - baseline) / baseline * 100) if baseline != 0 else 0,
            'status': 'better' if current_mean < baseline else 'worse' if current_mean > baseline else 'same'
        }
        
        # For some metrics, higher is better
        if metric_type in [MetricType.ACCURACY, MetricType.PATTERN_EFFECTIVENESS, 
                          MetricType.FEDERATION_HEALTH, MetricType.PRIVACY_COMPLIANCE]:
            comparison['status'] = 'better' if current_mean > baseline else 'worse' if current_mean < baseline else 'same'
        
        return comparison