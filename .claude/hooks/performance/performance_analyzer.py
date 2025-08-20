#!/usr/bin/env python3
"""
Performance Analysis Engine
Advanced analysis of performance metrics with trend detection and optimization recommendations
"""

import sqlite3
import time
import logging
import statistics
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import json
import numpy as np
from datetime import datetime, timedelta
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrendDirection(Enum):
    IMPROVING = "improving"
    DEGRADING = "degrading"
    STABLE = "stable"
    VOLATILE = "volatile"

class BottleneckType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    TOOL_EXECUTION = "tool_execution"
    HOOK_PERFORMANCE = "hook_performance"

@dataclass
class PerformanceTrend:
    metric_name: str
    direction: TrendDirection
    slope: float
    confidence: float
    current_value: float
    baseline_value: float
    change_percentage: float
    sample_count: int
    time_range: str

@dataclass
class Bottleneck:
    bottleneck_type: BottleneckType
    severity: str  # low, medium, high, critical
    description: str
    current_value: float
    threshold_value: float
    impact_score: float
    recommendations: List[str]
    affected_tools: List[str] = None

@dataclass
class PerformanceInsight:
    insight_type: str
    title: str
    description: str
    severity: str
    confidence: float
    supporting_data: Dict[str, Any]
    recommendations: List[str]
    estimated_impact: str

class PerformanceAnalyzer:
    """Advanced performance analysis with trend detection and optimization"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(Path.home() / ".claude" / "performance_metrics.db")
        
        # Analysis parameters
        self.trend_analysis_windows = {
            'short': 1800,   # 30 minutes
            'medium': 7200,  # 2 hours
            'long': 86400    # 24 hours
        }
        
        # Bottleneck thresholds
        self.bottleneck_thresholds = {
            'cpu_usage': {'medium': 70, 'high': 85, 'critical': 95},
            'memory_usage': {'medium': 75, 'high': 85, 'critical': 95},
            'disk_usage': {'medium': 80, 'high': 90, 'critical': 95},
            'tool_execution_time': {'medium': 10, 'high': 30, 'critical': 60},
            'hook_execution_time': {'medium': 2, 'high': 5, 'critical': 10}
        }
        
        # Performance baselines (to be loaded from database)
        self.baselines = {}
        
        logger.info("Performance analyzer initialized")
    
    def analyze_performance_trends(self, window: str = 'medium') -> List[PerformanceTrend]:
        """Analyze performance trends over specified time window"""
        
        window_seconds = self.trend_analysis_windows.get(window, 7200)
        start_time = time.time() - window_seconds
        
        trends = []
        
        with sqlite3.connect(self.db_path) as conn:
            # Analyze system metrics trends
            trends.extend(self._analyze_system_metrics_trends(conn, start_time))
            
            # Analyze tool execution trends
            trends.extend(self._analyze_tool_execution_trends(conn, start_time))
            
            # Analyze hook performance trends
            trends.extend(self._analyze_hook_performance_trends(conn, start_time))
        
        return trends
    
    def _analyze_system_metrics_trends(self, conn: sqlite3.Connection, start_time: float) -> List[PerformanceTrend]:
        """Analyze system metrics trends"""
        
        trends = []
        metrics = ['cpu_usage', 'memory_usage', 'disk_usage']
        
        for metric in metrics:
            cursor = conn.execute(f'''
                SELECT timestamp, {metric}
                FROM system_metrics
                WHERE timestamp >= ?
                ORDER BY timestamp
            ''', (start_time,))
            
            data = cursor.fetchall()
            if len(data) < 5:  # Need minimum data points
                continue
            
            timestamps = [row[0] for row in data]
            values = [row[1] for row in data]
            
            trend = self._calculate_trend(metric, timestamps, values, start_time)
            if trend:
                trends.append(trend)
        
        return trends
    
    def _analyze_tool_execution_trends(self, conn: sqlite3.Connection, start_time: float) -> List[PerformanceTrend]:
        """Analyze tool execution time trends"""
        
        cursor = conn.execute('''
            SELECT start_time, execution_time
            FROM tool_execution_metrics
            WHERE start_time >= ?
            ORDER BY start_time
        ''', (start_time,))
        
        data = cursor.fetchall()
        if len(data) < 5:
            return []
        
        timestamps = [row[0] for row in data]
        values = [row[1] for row in data]
        
        trend = self._calculate_trend('tool_execution_time', timestamps, values, start_time)
        return [trend] if trend else []
    
    def _analyze_hook_performance_trends(self, conn: sqlite3.Connection, start_time: float) -> List[PerformanceTrend]:
        """Analyze hook execution time trends"""
        
        cursor = conn.execute('''
            SELECT timestamp, execution_time
            FROM hook_performance_metrics
            WHERE timestamp >= ?
            ORDER BY timestamp
        ''', (start_time,))
        
        data = cursor.fetchall()
        if len(data) < 5:
            return []
        
        timestamps = [row[0] for row in data]
        values = [row[1] for row in data]
        
        trend = self._calculate_trend('hook_execution_time', timestamps, values, start_time)
        return [trend] if trend else []
    
    def _calculate_trend(self, metric_name: str, timestamps: List[float], 
                        values: List[float], start_time: float) -> Optional[PerformanceTrend]:
        """Calculate trend for a metric"""
        
        if len(values) < 5:
            return None
        
        # Normalize timestamps to start from 0
        normalized_times = [(t - start_time) for t in timestamps]
        
        # Calculate linear regression slope
        n = len(values)
        sum_x = sum(normalized_times)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(normalized_times, values))
        sum_x2 = sum(x * x for x in normalized_times)
        
        # Avoid division by zero
        if n * sum_x2 - sum_x * sum_x == 0:
            slope = 0
        else:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Calculate correlation coefficient for confidence
        mean_x = statistics.mean(normalized_times)
        mean_y = statistics.mean(values)
        
        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(normalized_times, values))
        denominator_x = sum((x - mean_x) ** 2 for x in normalized_times)
        denominator_y = sum((y - mean_y) ** 2 for y in values)
        
        if denominator_x == 0 or denominator_y == 0:
            correlation = 0
        else:
            correlation = numerator / (denominator_x * denominator_y) ** 0.5
        
        confidence = abs(correlation)
        
        # Determine trend direction
        if abs(slope) < 0.01 and statistics.stdev(values) / statistics.mean(values) < 0.1:
            direction = TrendDirection.STABLE
        elif abs(slope) < 0.01:
            direction = TrendDirection.VOLATILE
        elif slope > 0:
            direction = TrendDirection.DEGRADING if metric_name.endswith('_usage') or metric_name.endswith('_time') else TrendDirection.IMPROVING
        else:
            direction = TrendDirection.IMPROVING if metric_name.endswith('_usage') or metric_name.endswith('_time') else TrendDirection.DEGRADING
        
        current_value = values[-1]
        baseline_value = values[0]
        change_percentage = ((current_value - baseline_value) / baseline_value * 100) if baseline_value != 0 else 0
        
        time_range_hours = (timestamps[-1] - timestamps[0]) / 3600
        time_range = f"{time_range_hours:.1f} hours"
        
        return PerformanceTrend(
            metric_name=metric_name,
            direction=direction,
            slope=slope,
            confidence=confidence,
            current_value=current_value,
            baseline_value=baseline_value,
            change_percentage=change_percentage,
            sample_count=len(values),
            time_range=time_range
        )
    
    def identify_bottlenecks(self, window_hours: int = 1) -> List[Bottleneck]:
        """Identify current performance bottlenecks"""
        
        start_time = time.time() - (window_hours * 3600)
        bottlenecks = []
        
        with sqlite3.connect(self.db_path) as conn:
            # System resource bottlenecks
            bottlenecks.extend(self._identify_system_bottlenecks(conn, start_time))
            
            # Tool execution bottlenecks
            bottlenecks.extend(self._identify_tool_bottlenecks(conn, start_time))
            
            # Hook performance bottlenecks
            bottlenecks.extend(self._identify_hook_bottlenecks(conn, start_time))
        
        # Sort by impact score
        bottlenecks.sort(key=lambda b: b.impact_score, reverse=True)
        
        return bottlenecks
    
    def _identify_system_bottlenecks(self, conn: sqlite3.Connection, start_time: float) -> List[Bottleneck]:
        """Identify system resource bottlenecks"""
        
        bottlenecks = []
        
        # CPU bottleneck
        cursor = conn.execute('''
            SELECT AVG(cpu_usage), MAX(cpu_usage), COUNT(*)
            FROM system_metrics
            WHERE timestamp >= ?
        ''', (start_time,))
        
        cpu_stats = cursor.fetchone()
        if cpu_stats[0] and cpu_stats[2] > 0:
            avg_cpu, max_cpu, sample_count = cpu_stats
            
            if avg_cpu > self.bottleneck_thresholds['cpu_usage']['medium']:
                severity = self._determine_severity(avg_cpu, self.bottleneck_thresholds['cpu_usage'])
                
                bottlenecks.append(Bottleneck(
                    bottleneck_type=BottleneckType.CPU,
                    severity=severity,
                    description=f"High CPU usage detected (avg: {avg_cpu:.1f}%, max: {max_cpu:.1f}%)",
                    current_value=avg_cpu,
                    threshold_value=self.bottleneck_thresholds['cpu_usage']['medium'],
                    impact_score=self._calculate_impact_score(avg_cpu, self.bottleneck_thresholds['cpu_usage']['critical']),
                    recommendations=self._get_cpu_recommendations(avg_cpu, max_cpu)
                ))
        
        # Memory bottleneck
        cursor = conn.execute('''
            SELECT AVG(memory_usage), MAX(memory_usage), COUNT(*)
            FROM system_metrics
            WHERE timestamp >= ?
        ''', (start_time,))
        
        memory_stats = cursor.fetchone()
        if memory_stats[0] and memory_stats[2] > 0:
            avg_memory, max_memory, sample_count = memory_stats
            
            if avg_memory > self.bottleneck_thresholds['memory_usage']['medium']:
                severity = self._determine_severity(avg_memory, self.bottleneck_thresholds['memory_usage'])
                
                bottlenecks.append(Bottleneck(
                    bottleneck_type=BottleneckType.MEMORY,
                    severity=severity,
                    description=f"High memory usage detected (avg: {avg_memory:.1f}%, max: {max_memory:.1f}%)",
                    current_value=avg_memory,
                    threshold_value=self.bottleneck_thresholds['memory_usage']['medium'],
                    impact_score=self._calculate_impact_score(avg_memory, self.bottleneck_thresholds['memory_usage']['critical']),
                    recommendations=self._get_memory_recommendations(avg_memory, max_memory)
                ))
        
        # Disk bottleneck
        cursor = conn.execute('''
            SELECT AVG(disk_usage), MAX(disk_usage), COUNT(*)
            FROM system_metrics
            WHERE timestamp >= ?
        ''', (start_time,))
        
        disk_stats = cursor.fetchone()
        if disk_stats[0] and disk_stats[2] > 0:
            avg_disk, max_disk, sample_count = disk_stats
            
            if avg_disk > self.bottleneck_thresholds['disk_usage']['medium']:
                severity = self._determine_severity(avg_disk, self.bottleneck_thresholds['disk_usage'])
                
                bottlenecks.append(Bottleneck(
                    bottleneck_type=BottleneckType.DISK,
                    severity=severity,
                    description=f"High disk usage detected (avg: {avg_disk:.1f}%, max: {max_disk:.1f}%)",
                    current_value=avg_disk,
                    threshold_value=self.bottleneck_thresholds['disk_usage']['medium'],
                    impact_score=self._calculate_impact_score(avg_disk, self.bottleneck_thresholds['disk_usage']['critical']),
                    recommendations=self._get_disk_recommendations(avg_disk, max_disk)
                ))
        
        return bottlenecks
    
    def _identify_tool_bottlenecks(self, conn: sqlite3.Connection, start_time: float) -> List[Bottleneck]:
        """Identify tool execution bottlenecks"""
        
        bottlenecks = []
        
        # Slow tools analysis
        cursor = conn.execute('''
            SELECT tool_name, AVG(execution_time), MAX(execution_time), COUNT(*)
            FROM tool_execution_metrics
            WHERE start_time >= ?
            GROUP BY tool_name
            HAVING AVG(execution_time) > ?
            ORDER BY AVG(execution_time) DESC
        ''', (start_time, self.bottleneck_thresholds['tool_execution_time']['medium']))
        
        slow_tools = cursor.fetchall()
        
        for tool_name, avg_time, max_time, count in slow_tools:
            severity = self._determine_severity(avg_time, self.bottleneck_thresholds['tool_execution_time'])
            
            bottlenecks.append(Bottleneck(
                bottleneck_type=BottleneckType.TOOL_EXECUTION,
                severity=severity,
                description=f"Slow tool execution: {tool_name} (avg: {avg_time:.2f}s, max: {max_time:.2f}s)",
                current_value=avg_time,
                threshold_value=self.bottleneck_thresholds['tool_execution_time']['medium'],
                impact_score=self._calculate_impact_score(avg_time, self.bottleneck_thresholds['tool_execution_time']['critical']),
                recommendations=self._get_tool_recommendations(tool_name, avg_time, max_time),
                affected_tools=[tool_name]
            ))
        
        return bottlenecks
    
    def _identify_hook_bottlenecks(self, conn: sqlite3.Connection, start_time: float) -> List[Bottleneck]:
        """Identify hook performance bottlenecks"""
        
        bottlenecks = []
        
        # Slow hooks analysis
        cursor = conn.execute('''
            SELECT hook_name, hook_type, AVG(execution_time), MAX(execution_time), COUNT(*)
            FROM hook_performance_metrics
            WHERE timestamp >= ?
            GROUP BY hook_name, hook_type
            HAVING AVG(execution_time) > ?
            ORDER BY AVG(execution_time) DESC
        ''', (start_time, self.bottleneck_thresholds['hook_execution_time']['medium']))
        
        slow_hooks = cursor.fetchall()
        
        for hook_name, hook_type, avg_time, max_time, count in slow_hooks:
            severity = self._determine_severity(avg_time, self.bottleneck_thresholds['hook_execution_time'])
            
            bottlenecks.append(Bottleneck(
                bottleneck_type=BottleneckType.HOOK_PERFORMANCE,
                severity=severity,
                description=f"Slow hook execution: {hook_name} ({hook_type}) (avg: {avg_time:.2f}s, max: {max_time:.2f}s)",
                current_value=avg_time,
                threshold_value=self.bottleneck_thresholds['hook_execution_time']['medium'],
                impact_score=self._calculate_impact_score(avg_time, self.bottleneck_thresholds['hook_execution_time']['critical']),
                recommendations=self._get_hook_recommendations(hook_name, hook_type, avg_time, max_time)
            ))
        
        return bottlenecks
    
    def generate_performance_insights(self, analysis_window_hours: int = 24) -> List[PerformanceInsight]:
        """Generate high-level performance insights and recommendations"""
        
        insights = []
        start_time = time.time() - (analysis_window_hours * 3600)
        
        with sqlite3.connect(self.db_path) as conn:
            # Performance degradation insights
            insights.extend(self._analyze_performance_degradation(conn, start_time))
            
            # Resource utilization insights
            insights.extend(self._analyze_resource_utilization(conn, start_time))
            
            # Tool efficiency insights
            insights.extend(self._analyze_tool_efficiency(conn, start_time))
            
            # Hook performance insights
            insights.extend(self._analyze_hook_efficiency(conn, start_time))
        
        # Sort by confidence and severity
        insights.sort(key=lambda i: (i.confidence, 1 if i.severity == 'critical' else 0.8 if i.severity == 'high' else 0.6), reverse=True)
        
        return insights
    
    def _analyze_performance_degradation(self, conn: sqlite3.Connection, start_time: float) -> List[PerformanceInsight]:
        """Analyze performance degradation patterns"""
        
        insights = []
        
        # Check for significant performance changes
        trends = self.analyze_performance_trends('long')
        degrading_trends = [t for t in trends if t.direction == TrendDirection.DEGRADING and t.confidence > 0.7]
        
        if len(degrading_trends) > 0:
            affected_metrics = [t.metric_name for t in degrading_trends]
            
            insights.append(PerformanceInsight(
                insight_type="performance_degradation",
                title="Performance Degradation Detected",
                description=f"Multiple metrics showing degrading trends: {', '.join(affected_metrics)}",
                severity="high" if len(degrading_trends) > 2 else "medium",
                confidence=statistics.mean([t.confidence for t in degrading_trends]),
                supporting_data={
                    'degrading_metrics': len(degrading_trends),
                    'trends': [{'metric': t.metric_name, 'change': f"{t.change_percentage:+.1f}%"} for t in degrading_trends]
                },
                recommendations=[
                    "Monitor system resources closely",
                    "Review recent changes that might impact performance",
                    "Consider scaling resources if trend continues",
                    "Investigate root cause of degradation"
                ],
                estimated_impact="Medium to High"
            ))
        
        return insights
    
    def _analyze_resource_utilization(self, conn: sqlite3.Connection, start_time: float) -> List[PerformanceInsight]:
        """Analyze resource utilization patterns"""
        
        insights = []
        
        # Check resource efficiency
        cursor = conn.execute('''
            SELECT AVG(cpu_usage), AVG(memory_usage), AVG(disk_usage),
                   MAX(cpu_usage), MAX(memory_usage), MAX(disk_usage)
            FROM system_metrics
            WHERE timestamp >= ?
        ''', (start_time,))
        
        resource_stats = cursor.fetchone()
        if resource_stats[0] is not None:
            avg_cpu, avg_memory, avg_disk, max_cpu, max_memory, max_disk = resource_stats
            
            # Underutilized resources
            if avg_cpu < 20 and avg_memory < 30:
                insights.append(PerformanceInsight(
                    insight_type="resource_underutilization",
                    title="Resources Underutilized",
                    description=f"System resources are underutilized (CPU: {avg_cpu:.1f}%, Memory: {avg_memory:.1f}%)",
                    severity="info",
                    confidence=0.8,
                    supporting_data={
                        'avg_cpu': avg_cpu,
                        'avg_memory': avg_memory,
                        'avg_disk': avg_disk
                    },
                    recommendations=[
                        "Consider increasing parallelism",
                        "Optimize batch sizes for better resource utilization",
                        "Enable more concurrent operations"
                    ],
                    estimated_impact="Low"
                ))
            
            # Resource bottlenecks
            bottlenecked_resources = []
            if max_cpu > 90:
                bottlenecked_resources.append(f"CPU ({max_cpu:.1f}%)")
            if max_memory > 90:
                bottlenecked_resources.append(f"Memory ({max_memory:.1f}%)")
            if max_disk > 90:
                bottlenecked_resources.append(f"Disk ({max_disk:.1f}%)")
            
            if bottlenecked_resources:
                insights.append(PerformanceInsight(
                    insight_type="resource_bottleneck",
                    title="Resource Bottlenecks Detected",
                    description=f"Resource bottlenecks observed: {', '.join(bottlenecked_resources)}",
                    severity="high",
                    confidence=0.9,
                    supporting_data={
                        'bottlenecked_resources': bottlenecked_resources,
                        'max_cpu': max_cpu,
                        'max_memory': max_memory,
                        'max_disk': max_disk
                    },
                    recommendations=[
                        "Scale up resources or optimize resource usage",
                        "Implement resource pooling and management",
                        "Consider horizontal scaling",
                        "Profile and optimize resource-intensive operations"
                    ],
                    estimated_impact="High"
                ))
        
        return insights
    
    def _analyze_tool_efficiency(self, conn: sqlite3.Connection, start_time: float) -> List[PerformanceInsight]:
        """Analyze tool execution efficiency"""
        
        insights = []
        
        # Tool performance comparison
        cursor = conn.execute('''
            SELECT tool_name, COUNT(*), AVG(execution_time), 
                   AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate
            FROM tool_execution_metrics
            WHERE start_time >= ?
            GROUP BY tool_name
            HAVING COUNT(*) >= 5
            ORDER BY AVG(execution_time) DESC
        ''', (start_time,))
        
        tool_stats = cursor.fetchall()
        
        if tool_stats:
            # Identify slowest tools
            slowest_tools = tool_stats[:3]  # Top 3 slowest
            
            if slowest_tools[0][2] > 10:  # If slowest tool takes more than 10 seconds
                insights.append(PerformanceInsight(
                    insight_type="tool_performance",
                    title="Slow Tool Execution Detected",
                    description=f"Some tools are executing slowly: {slowest_tools[0][0]} ({slowest_tools[0][2]:.2f}s avg)",
                    severity="medium",
                    confidence=0.8,
                    supporting_data={
                        'slowest_tools': [{'name': t[0], 'avg_time': t[2], 'executions': t[1]} for t in slowest_tools],
                        'overall_tool_count': len(tool_stats)
                    },
                    recommendations=[
                        "Optimize slow tools or consider alternatives",
                        "Implement caching where appropriate",
                        "Consider parallel execution for independent operations",
                        "Profile tool execution to identify bottlenecks"
                    ],
                    estimated_impact="Medium"
                ))
            
            # Check success rates
            low_success_tools = [t for t in tool_stats if t[3] < 0.9]  # Less than 90% success
            
            if low_success_tools:
                insights.append(PerformanceInsight(
                    insight_type="tool_reliability",
                    title="Tool Reliability Issues",
                    description=f"Some tools have low success rates: {low_success_tools[0][0]} ({low_success_tools[0][3]*100:.1f}%)",
                    severity="high",
                    confidence=0.9,
                    supporting_data={
                        'unreliable_tools': [{'name': t[0], 'success_rate': t[3]*100, 'executions': t[1]} for t in low_success_tools]
                    },
                    recommendations=[
                        "Investigate and fix failing tools",
                        "Implement better error handling and retry logic",
                        "Add input validation and error prevention",
                        "Monitor tool health more closely"
                    ],
                    estimated_impact="High"
                ))
        
        return insights
    
    def _analyze_hook_efficiency(self, conn: sqlite3.Connection, start_time: float) -> List[PerformanceInsight]:
        """Analyze hook execution efficiency"""
        
        insights = []
        
        # Hook performance analysis
        cursor = conn.execute('''
            SELECT hook_name, hook_type, COUNT(*), AVG(execution_time),
                   AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate
            FROM hook_performance_metrics
            WHERE timestamp >= ?
            GROUP BY hook_name, hook_type
            HAVING COUNT(*) >= 3
            ORDER BY AVG(execution_time) DESC
        ''', (start_time,))
        
        hook_stats = cursor.fetchall()
        
        if hook_stats:
            # Identify slow hooks
            slow_hooks = [h for h in hook_stats if h[3] > 2.0]  # Hooks taking more than 2 seconds
            
            if slow_hooks:
                insights.append(PerformanceInsight(
                    insight_type="hook_performance",
                    title="Slow Hook Execution",
                    description=f"Some hooks are executing slowly: {slow_hooks[0][0]} ({slow_hooks[0][3]:.2f}s avg)",
                    severity="medium",
                    confidence=0.7,
                    supporting_data={
                        'slow_hooks': [{'name': h[0], 'type': h[1], 'avg_time': h[3], 'executions': h[2]} for h in slow_hooks]
                    },
                    recommendations=[
                        "Optimize hook implementations",
                        "Consider asynchronous hook execution",
                        "Reduce hook complexity or split into smaller hooks",
                        "Implement hook timeout and fallback mechanisms"
                    ],
                    estimated_impact="Low to Medium"
                ))
        
        return insights
    
    def _determine_severity(self, value: float, thresholds: Dict[str, int]) -> str:
        """Determine severity level based on thresholds"""
        if value >= thresholds['critical']:
            return 'critical'
        elif value >= thresholds['high']:
            return 'high'
        elif value >= thresholds['medium']:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_impact_score(self, current_value: float, critical_threshold: float) -> float:
        """Calculate impact score (0-1) based on current value vs critical threshold"""
        return min(1.0, current_value / critical_threshold)
    
    def _get_cpu_recommendations(self, avg_cpu: float, max_cpu: float) -> List[str]:
        """Get CPU optimization recommendations"""
        recommendations = []
        
        if avg_cpu > 80:
            recommendations.extend([
                "Consider upgrading to a higher CPU tier",
                "Optimize CPU-intensive operations",
                "Implement parallel processing where possible"
            ])
        
        if max_cpu > 95:
            recommendations.append("Enable CPU throttling protection")
        
        if not recommendations:
            recommendations.append("Monitor CPU usage patterns for optimization opportunities")
        
        return recommendations
    
    def _get_memory_recommendations(self, avg_memory: float, max_memory: float) -> List[str]:
        """Get memory optimization recommendations"""
        recommendations = []
        
        if avg_memory > 80:
            recommendations.extend([
                "Consider increasing available memory",
                "Optimize memory usage in applications",
                "Implement memory pooling and caching strategies"
            ])
        
        if max_memory > 95:
            recommendations.append("Implement memory pressure handling")
        
        if not recommendations:
            recommendations.append("Monitor memory allocation patterns")
        
        return recommendations
    
    def _get_disk_recommendations(self, avg_disk: float, max_disk: float) -> List[str]:
        """Get disk optimization recommendations"""
        recommendations = []
        
        if avg_disk > 85:
            recommendations.extend([
                "Clean up unnecessary files",
                "Implement log rotation and cleanup",
                "Consider expanding disk space"
            ])
        
        if max_disk > 95:
            recommendations.append("Enable disk space monitoring and alerts")
        
        return recommendations
    
    def _get_tool_recommendations(self, tool_name: str, avg_time: float, max_time: float) -> List[str]:
        """Get tool-specific optimization recommendations"""
        recommendations = [
            f"Profile {tool_name} execution to identify bottlenecks",
            f"Consider caching results for {tool_name}",
            f"Optimize {tool_name} input/output processing"
        ]
        
        if max_time > avg_time * 3:
            recommendations.append(f"Investigate {tool_name} performance spikes")
        
        return recommendations
    
    def _get_hook_recommendations(self, hook_name: str, hook_type: str, avg_time: float, max_time: float) -> List[str]:
        """Get hook-specific optimization recommendations"""
        recommendations = [
            f"Optimize {hook_name} ({hook_type}) implementation",
            f"Consider async execution for {hook_name}",
            f"Reduce complexity in {hook_name} hook"
        ]
        
        if avg_time > 5:
            recommendations.append(f"Consider breaking {hook_name} into smaller hooks")
        
        return recommendations

# Example usage and testing
def test_performance_analyzer():
    """Test the performance analyzer functionality"""
    
    print("🧪 Testing Performance Analyzer...")
    
    # Note: This test requires existing metrics database
    db_path = str(Path.home() / ".claude" / "performance_metrics.db")
    
    if not Path(db_path).exists():
        print("❌ No metrics database found. Run metrics collector first.")
        return
    
    analyzer = PerformanceAnalyzer(db_path)
    
    # Test trend analysis
    print("📈 Analyzing performance trends...")
    trends = analyzer.analyze_performance_trends('short')
    print(f"   Found {len(trends)} trends")
    
    for trend in trends[:3]:  # Show first 3
        print(f"   {trend.metric_name}: {trend.direction.value} ({trend.change_percentage:+.1f}%)")
    
    # Test bottleneck identification
    print("🔍 Identifying bottlenecks...")
    bottlenecks = analyzer.identify_bottlenecks()
    print(f"   Found {len(bottlenecks)} bottlenecks")
    
    for bottleneck in bottlenecks[:3]:  # Show first 3
        print(f"   {bottleneck.bottleneck_type.value}: {bottleneck.severity} - {bottleneck.description}")
    
    # Test performance insights
    print("💡 Generating performance insights...")
    insights = analyzer.generate_performance_insights()
    print(f"   Generated {len(insights)} insights")
    
    for insight in insights[:2]:  # Show first 2
        print(f"   {insight.title}: {insight.severity} - {insight.description}")
    
    print("✅ Performance analyzer test completed!")

if __name__ == "__main__":
    test_performance_analyzer()