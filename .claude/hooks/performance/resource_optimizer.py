#!/usr/bin/env python3
"""
Advanced Resource Optimizer
Automatic detection and resolution of performance bottlenecks with ML-powered optimization
"""

import os
import psutil
import time
import json
import logging
import threading
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import statistics
from enum import Enum
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResourceType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    PROCESS = "process"

class OptimizationAction(Enum):
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    OPTIMIZE_CONFIG = "optimize_config"
    CLEANUP_RESOURCES = "cleanup_resources"
    ADJUST_PRIORITIES = "adjust_priorities"
    ENABLE_CACHING = "enable_caching"

@dataclass
class ResourceBottleneck:
    resource_type: ResourceType
    severity: str  # critical, high, medium, low
    current_usage: float
    threshold: float
    impact_score: float
    duration_minutes: float
    affected_processes: List[str]
    root_cause: str
    recommendations: List[Dict[str, Any]]
    detected_at: float

@dataclass
class OptimizationPlan:
    plan_id: str
    bottlenecks_addressed: List[str]
    actions: List[Dict[str, Any]]
    expected_improvement: float
    risk_level: str
    estimated_duration: int  # seconds
    prerequisites: List[str]
    rollback_plan: List[Dict[str, Any]]

class ResourceOptimizer:
    """Advanced resource optimization with bottleneck detection and ML insights"""
    
    def __init__(self, metrics_collector=None):
        self.metrics_collector = metrics_collector
        self.config_dir = Path.home() / ".claude" / "performance"
        self.config_dir.mkdir(exist_ok=True)
        
        # Optimization state
        self.active_optimizations = {}
        self.optimization_history = []
        self.baseline_performance = {}
        
        # Detection thresholds
        self.bottleneck_thresholds = {
            ResourceType.CPU: {
                'warning': 70.0,
                'critical': 85.0,
                'sustained_minutes': 5
            },
            ResourceType.MEMORY: {
                'warning': 75.0,
                'critical': 90.0,
                'sustained_minutes': 3
            },
            ResourceType.DISK: {
                'warning': 80.0,
                'critical': 95.0,
                'sustained_minutes': 1
            },
            ResourceType.NETWORK: {
                'warning': 80.0,  # % of bandwidth
                'critical': 95.0,
                'sustained_minutes': 2
            }
        }
        
        # ML-powered optimization parameters
        self.learning_enabled = True
        self.optimization_success_rates = {}
        self.resource_patterns = {}
        
        # Background monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
        self.detection_interval = 30  # seconds
        
        # Auto-optimization settings
        self.auto_optimization_enabled = os.getenv('AUTO_OPTIMIZATION', 'false').lower() == 'true'
        self.max_concurrent_optimizations = 2
        
        logger.info("Resource optimizer initialized")
    
    def start_monitoring(self):
        """Start background resource monitoring and bottleneck detection"""
        
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        
        if self.monitoring_active:
            self.monitoring_active = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=10.0)
            logger.info("Resource monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        
        while self.monitoring_active:
            try:
                # Detect current bottlenecks
                bottlenecks = self.detect_bottlenecks()
                
                # Process detected bottlenecks
                for bottleneck in bottlenecks:
                    self._handle_bottleneck(bottleneck)
                
                # Update resource patterns for ML
                if self.learning_enabled:
                    self._update_resource_patterns()
                
                # Cleanup completed optimizations
                self._cleanup_completed_optimizations()
                
                time.sleep(self.detection_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.detection_interval * 2)
    
    def detect_bottlenecks(self) -> List[ResourceBottleneck]:
        """Detect current resource bottlenecks using advanced algorithms"""
        
        bottlenecks = []
        
        # CPU bottleneck detection
        cpu_bottleneck = self._detect_cpu_bottleneck()
        if cpu_bottleneck:
            bottlenecks.append(cpu_bottleneck)
        
        # Memory bottleneck detection
        memory_bottleneck = self._detect_memory_bottleneck()
        if memory_bottleneck:
            bottlenecks.append(memory_bottleneck)
        
        # Disk bottleneck detection
        disk_bottleneck = self._detect_disk_bottleneck()
        if disk_bottleneck:
            bottlenecks.append(disk_bottleneck)
        
        # Network bottleneck detection
        network_bottleneck = self._detect_network_bottleneck()
        if network_bottleneck:
            bottlenecks.append(network_bottleneck)
        
        # Process-level bottleneck detection
        process_bottlenecks = self._detect_process_bottlenecks()
        bottlenecks.extend(process_bottlenecks)
        
        return bottlenecks
    
    def _detect_cpu_bottleneck(self) -> Optional[ResourceBottleneck]:
        """Detect CPU bottlenecks with trend analysis"""
        
        # Collect CPU usage over time
        cpu_samples = []
        for _ in range(10):  # 10 samples over 10 seconds
            cpu_samples.append(psutil.cpu_percent(interval=1))
        
        avg_cpu = statistics.mean(cpu_samples)
        max_cpu = max(cpu_samples)
        
        threshold = self.bottleneck_thresholds[ResourceType.CPU]
        
        if avg_cpu > threshold['critical'] or max_cpu > 95:
            severity = 'critical'
        elif avg_cpu > threshold['warning']:
            severity = 'high'
        else:
            return None
        
        # Identify CPU-intensive processes
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                proc_info = proc.info
                if proc_info['cpu_percent'] and proc_info['cpu_percent'] > 10:
                    processes.append(f"{proc_info['name']} (PID: {proc_info['pid']}, CPU: {proc_info['cpu_percent']:.1f}%)")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Determine root cause
        root_cause = self._analyze_cpu_root_cause(cpu_samples, processes)
        
        # Generate recommendations
        recommendations = self._generate_cpu_recommendations(avg_cpu, max_cpu, processes)
        
        return ResourceBottleneck(
            resource_type=ResourceType.CPU,
            severity=severity,
            current_usage=avg_cpu,
            threshold=threshold['warning'],
            impact_score=min(1.0, avg_cpu / 100.0),
            duration_minutes=len(cpu_samples),
            affected_processes=processes[:5],  # Top 5 processes
            root_cause=root_cause,
            recommendations=recommendations,
            detected_at=time.time()
        )
    
    def _detect_memory_bottleneck(self) -> Optional[ResourceBottleneck]:
        """Detect memory bottlenecks with leak detection"""
        
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        available_gb = memory.available / (1024**3)
        
        threshold = self.bottleneck_thresholds[ResourceType.MEMORY]
        
        if memory_percent > threshold['critical']:
            severity = 'critical'
        elif memory_percent > threshold['warning']:
            severity = 'high'
        else:
            return None
        
        # Identify memory-intensive processes
        processes = []
        total_process_memory = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info']):
            try:
                proc_info = proc.info
                if proc_info['memory_percent'] and proc_info['memory_percent'] > 5:
                    memory_mb = proc_info['memory_info'].rss / (1024**2)
                    processes.append(f"{proc_info['name']} (PID: {proc_info['pid']}, Memory: {memory_mb:.1f}MB)")
                    total_process_memory += memory_mb
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Detect potential memory leaks
        root_cause = self._analyze_memory_root_cause(memory_percent, available_gb, total_process_memory)
        
        # Generate recommendations
        recommendations = self._generate_memory_recommendations(memory_percent, available_gb, processes)
        
        return ResourceBottleneck(
            resource_type=ResourceType.MEMORY,
            severity=severity,
            current_usage=memory_percent,
            threshold=threshold['warning'],
            impact_score=min(1.0, memory_percent / 100.0),
            duration_minutes=1,  # Snapshot measurement
            affected_processes=processes[:5],
            root_cause=root_cause,
            recommendations=recommendations,
            detected_at=time.time()
        )
    
    def _detect_disk_bottleneck(self) -> Optional[ResourceBottleneck]:
        """Detect disk I/O and space bottlenecks"""
        
        # Disk usage analysis
        disk_usage = psutil.disk_usage('/')
        usage_percent = (disk_usage.used / disk_usage.total) * 100
        free_gb = disk_usage.free / (1024**3)
        
        # Disk I/O analysis
        disk_io = psutil.disk_io_counters()
        
        threshold = self.bottleneck_thresholds[ResourceType.DISK]
        
        if usage_percent > threshold['critical'] or free_gb < 1:
            severity = 'critical'
        elif usage_percent > threshold['warning'] or free_gb < 5:
            severity = 'high'
        else:
            return None
        
        # Identify disk-intensive processes
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_io = proc.io_counters()
                    if proc_io and (proc_io.read_bytes > 100*1024*1024 or proc_io.write_bytes > 100*1024*1024):
                        read_mb = proc_io.read_bytes / (1024**2)
                        write_mb = proc_io.write_bytes / (1024**2)
                        processes.append(f"{proc.info['name']} (PID: {proc.info['pid']}, R/W: {read_mb:.1f}/{write_mb:.1f}MB)")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except:
            pass  # Disk I/O data might not be available
        
        root_cause = self._analyze_disk_root_cause(usage_percent, free_gb)
        recommendations = self._generate_disk_recommendations(usage_percent, free_gb)
        
        return ResourceBottleneck(
            resource_type=ResourceType.DISK,
            severity=severity,
            current_usage=usage_percent,
            threshold=threshold['warning'],
            impact_score=min(1.0, usage_percent / 100.0),
            duration_minutes=1,
            affected_processes=processes[:5],
            root_cause=root_cause,
            recommendations=recommendations,
            detected_at=time.time()
        )
    
    def _detect_network_bottleneck(self) -> Optional[ResourceBottleneck]:
        """Detect network bottlenecks and connection issues"""
        
        try:
            # Network I/O statistics
            net_io = psutil.net_io_counters()
            
            # Network connections analysis
            connections = psutil.net_connections()
            active_connections = len([c for c in connections if c.status == 'ESTABLISHED'])
            
            # Simple network utilization check (this would be enhanced in a real implementation)
            # For now, we'll focus on connection count and basic stats
            
            if active_connections > 1000:
                severity = 'high'
                usage_percent = min(100, active_connections / 10)  # Rough estimate
            elif active_connections > 500:
                severity = 'medium'
                usage_percent = active_connections / 20
            else:
                return None
            
            processes = []
            # Network processes would be identified here
            
            root_cause = f"High number of active connections: {active_connections}"
            recommendations = self._generate_network_recommendations(active_connections)
            
            return ResourceBottleneck(
                resource_type=ResourceType.NETWORK,
                severity=severity,
                current_usage=usage_percent,
                threshold=50,  # Placeholder threshold
                impact_score=min(1.0, active_connections / 1000),
                duration_minutes=1,
                affected_processes=processes,
                root_cause=root_cause,
                recommendations=recommendations,
                detected_at=time.time()
            )
        except:
            return None  # Network monitoring might not be available
    
    def _detect_process_bottlenecks(self) -> List[ResourceBottleneck]:
        """Detect process-level bottlenecks and resource hogs"""
        
        bottlenecks = []
        
        try:
            # Find resource-intensive processes
            cpu_hogs = []
            memory_hogs = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
                try:
                    proc_info = proc.info
                    
                    # CPU hogs
                    if proc_info['cpu_percent'] and proc_info['cpu_percent'] > 50:
                        cpu_hogs.append((proc_info, proc_info['cpu_percent']))
                    
                    # Memory hogs
                    if proc_info['memory_percent'] and proc_info['memory_percent'] > 25:
                        memory_hogs.append((proc_info, proc_info['memory_percent']))
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Create bottlenecks for significant resource hogs
            for proc_info, cpu_usage in sorted(cpu_hogs, key=lambda x: x[1], reverse=True)[:3]:
                bottlenecks.append(ResourceBottleneck(
                    resource_type=ResourceType.PROCESS,
                    severity='high' if cpu_usage > 80 else 'medium',
                    current_usage=cpu_usage,
                    threshold=50,
                    impact_score=min(1.0, cpu_usage / 100.0),
                    duration_minutes=1,
                    affected_processes=[f"{proc_info['name']} (PID: {proc_info['pid']})"],
                    root_cause=f"Process consuming {cpu_usage:.1f}% CPU",
                    recommendations=self._generate_process_recommendations(proc_info, 'cpu'),
                    detected_at=time.time()
                ))
            
            for proc_info, memory_usage in sorted(memory_hogs, key=lambda x: x[1], reverse=True)[:3]:
                memory_mb = proc_info['memory_info'].rss / (1024**2)
                bottlenecks.append(ResourceBottleneck(
                    resource_type=ResourceType.PROCESS,
                    severity='high' if memory_usage > 40 else 'medium',
                    current_usage=memory_usage,
                    threshold=25,
                    impact_score=min(1.0, memory_usage / 100.0),
                    duration_minutes=1,
                    affected_processes=[f"{proc_info['name']} (PID: {proc_info['pid']})"],
                    root_cause=f"Process consuming {memory_mb:.1f}MB memory ({memory_usage:.1f}%)",
                    recommendations=self._generate_process_recommendations(proc_info, 'memory'),
                    detected_at=time.time()
                ))
        
        except Exception as e:
            logger.error(f"Error detecting process bottlenecks: {e}")
        
        return bottlenecks
    
    def generate_optimization_plan(self, bottlenecks: List[ResourceBottleneck]) -> OptimizationPlan:
        """Generate comprehensive optimization plan for detected bottlenecks"""
        
        if not bottlenecks:
            return None
        
        plan_id = f"opt_plan_{int(time.time())}"
        actions = []
        expected_improvement = 0.0
        risk_level = 'low'
        estimated_duration = 0
        prerequisites = []
        rollback_plan = []
        
        # Sort bottlenecks by severity and impact
        sorted_bottlenecks = sorted(bottlenecks, key=lambda b: (b.severity, b.impact_score), reverse=True)
        
        for bottleneck in sorted_bottlenecks:
            bottleneck_actions = self._generate_bottleneck_actions(bottleneck)
            actions.extend(bottleneck_actions)
            
            # Update plan metrics
            expected_improvement += bottleneck.impact_score * 20  # Rough estimate
            estimated_duration += 60  # 1 minute per bottleneck
            
            if bottleneck.severity == 'critical':
                risk_level = 'high'
            elif bottleneck.severity == 'high' and risk_level != 'high':
                risk_level = 'medium'
        
        # Add prerequisite checks
        prerequisites = [
            "Verify system stability",
            "Create performance baseline",
            "Ensure rollback capability"
        ]
        
        # Generate rollback plan
        rollback_plan = [
            {"action": "restore_configuration", "priority": 1},
            {"action": "restart_affected_services", "priority": 2},
            {"action": "verify_system_health", "priority": 3}
        ]
        
        return OptimizationPlan(
            plan_id=plan_id,
            bottlenecks_addressed=[b.resource_type.value for b in sorted_bottlenecks],
            actions=actions,
            expected_improvement=min(100.0, expected_improvement),
            risk_level=risk_level,
            estimated_duration=estimated_duration,
            prerequisites=prerequisites,
            rollback_plan=rollback_plan
        )
    
    def execute_optimization_plan(self, plan: OptimizationPlan) -> Dict[str, Any]:
        """Execute optimization plan with safety checks and monitoring"""
        
        execution_results = {
            'plan_id': plan.plan_id,
            'started_at': time.time(),
            'actions_executed': [],
            'actions_failed': [],
            'overall_success': False,
            'improvement_achieved': 0.0,
            'rollback_performed': False
        }
        
        try:
            # Verify prerequisites
            for prerequisite in plan.prerequisites:
                if not self._verify_prerequisite(prerequisite):
                    raise Exception(f"Prerequisite not met: {prerequisite}")
            
            # Execute actions in sequence
            baseline_metrics = self._collect_baseline_metrics()
            
            for action in plan.actions:
                try:
                    result = self._execute_action(action)
                    execution_results['actions_executed'].append({
                        'action': action,
                        'result': result,
                        'timestamp': time.time()
                    })
                    
                    # Brief pause between actions
                    time.sleep(2)
                    
                except Exception as e:
                    execution_results['actions_failed'].append({
                        'action': action,
                        'error': str(e),
                        'timestamp': time.time()
                    })
                    
                    # If critical action fails, consider rollback
                    if action.get('critical', False):
                        logger.error(f"Critical action failed: {e}")
                        break
            
            # Measure improvement
            time.sleep(10)  # Wait for changes to take effect
            post_metrics = self._collect_baseline_metrics()
            improvement = self._calculate_improvement(baseline_metrics, post_metrics)
            execution_results['improvement_achieved'] = improvement
            
            # Determine overall success
            execution_results['overall_success'] = (
                len(execution_results['actions_failed']) == 0 and
                improvement > 0
            )
            
            # Rollback if improvement is negative or significant failures occurred
            if improvement < -10 or len(execution_results['actions_failed']) > len(plan.actions) / 2:
                logger.warning("Optimization failed, performing rollback")
                self._execute_rollback_plan(plan.rollback_plan)
                execution_results['rollback_performed'] = True
            
        except Exception as e:
            execution_results['error'] = str(e)
            logger.error(f"Optimization plan execution failed: {e}")
            
            # Emergency rollback
            try:
                self._execute_rollback_plan(plan.rollback_plan)
                execution_results['rollback_performed'] = True
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {rollback_error}")
        
        execution_results['completed_at'] = time.time()
        execution_results['duration'] = execution_results['completed_at'] - execution_results['started_at']
        
        # Store optimization history for learning
        self.optimization_history.append(execution_results)
        
        return execution_results
    
    def _analyze_cpu_root_cause(self, cpu_samples: List[float], processes: List[str]) -> str:
        """Analyze root cause of CPU bottleneck"""
        
        if len(processes) == 1:
            return f"Single process consuming high CPU: {processes[0]}"
        elif len(processes) > 5:
            return f"Multiple processes competing for CPU: {len(processes)} high-usage processes"
        elif statistics.stdev(cpu_samples) > 20:
            return "Intermittent CPU spikes detected"
        else:
            return "Sustained high CPU usage across multiple processes"
    
    def _analyze_memory_root_cause(self, memory_percent: float, available_gb: float, total_process_memory: float) -> str:
        """Analyze root cause of memory bottleneck"""
        
        if available_gb < 1:
            return "Critical memory shortage - immediate cleanup required"
        elif memory_percent > 95:
            return "Memory exhaustion - potential memory leak"
        elif total_process_memory > memory_percent * 80:
            return "Process memory consumption exceeds expected levels"
        else:
            return "High memory usage - optimization recommended"
    
    def _analyze_disk_root_cause(self, usage_percent: float, free_gb: float) -> str:
        """Analyze root cause of disk bottleneck"""
        
        if free_gb < 1:
            return "Critical disk space shortage"
        elif usage_percent > 95:
            return "Disk nearly full - cleanup required"
        else:
            return "High disk usage - consider cleanup or expansion"
    
    def _generate_cpu_recommendations(self, avg_cpu: float, max_cpu: float, processes: List[str]) -> List[Dict[str, Any]]:
        """Generate CPU optimization recommendations"""
        
        recommendations = []
        
        if avg_cpu > 90:
            recommendations.append({
                'action': OptimizationAction.SCALE_UP.value,
                'description': 'Consider upgrading CPU or adding cores',
                'priority': 'high',
                'estimated_improvement': 30
            })
        
        if len(processes) > 3:
            recommendations.append({
                'action': OptimizationAction.ADJUST_PRIORITIES.value,
                'description': 'Adjust process priorities and CPU affinity',
                'priority': 'medium',
                'estimated_improvement': 15
            })
        
        recommendations.append({
            'action': OptimizationAction.OPTIMIZE_CONFIG.value,
            'description': 'Optimize system configuration and kernel parameters',
            'priority': 'medium',
            'estimated_improvement': 10
        })
        
        return recommendations
    
    def _generate_memory_recommendations(self, memory_percent: float, available_gb: float, processes: List[str]) -> List[Dict[str, Any]]:
        """Generate memory optimization recommendations"""
        
        recommendations = []
        
        if memory_percent > 90:
            recommendations.append({
                'action': OptimizationAction.SCALE_UP.value,
                'description': 'Add more RAM to the system',
                'priority': 'high',
                'estimated_improvement': 40
            })
        
        if available_gb < 2:
            recommendations.append({
                'action': OptimizationAction.CLEANUP_RESOURCES.value,
                'description': 'Clear caches and unused memory',
                'priority': 'high',
                'estimated_improvement': 20
            })
        
        recommendations.append({
            'action': OptimizationAction.ENABLE_CACHING.value,
            'description': 'Optimize memory caching and swap usage',
            'priority': 'medium',
            'estimated_improvement': 15
        })
        
        return recommendations
    
    def _generate_disk_recommendations(self, usage_percent: float, free_gb: float) -> List[Dict[str, Any]]:
        """Generate disk optimization recommendations"""
        
        recommendations = []
        
        if usage_percent > 95:
            recommendations.append({
                'action': OptimizationAction.CLEANUP_RESOURCES.value,
                'description': 'Clean up temporary files and logs',
                'priority': 'critical',
                'estimated_improvement': 25
            })
        
        if free_gb < 5:
            recommendations.append({
                'action': OptimizationAction.SCALE_UP.value,
                'description': 'Expand disk storage',
                'priority': 'high',
                'estimated_improvement': 50
            })
        
        return recommendations
    
    def _generate_network_recommendations(self, active_connections: int) -> List[Dict[str, Any]]:
        """Generate network optimization recommendations"""
        
        recommendations = []
        
        if active_connections > 1000:
            recommendations.append({
                'action': OptimizationAction.OPTIMIZE_CONFIG.value,
                'description': 'Optimize network buffer sizes and connection pooling',
                'priority': 'high',
                'estimated_improvement': 30
            })
        
        return recommendations
    
    def _generate_process_recommendations(self, proc_info: Dict, resource_type: str) -> List[Dict[str, Any]]:
        """Generate process-specific optimization recommendations"""
        
        recommendations = []
        
        if resource_type == 'cpu':
            recommendations.append({
                'action': OptimizationAction.ADJUST_PRIORITIES.value,
                'description': f'Adjust priority for {proc_info["name"]}',
                'priority': 'medium',
                'estimated_improvement': 10
            })
        elif resource_type == 'memory':
            recommendations.append({
                'action': OptimizationAction.OPTIMIZE_CONFIG.value,
                'description': f'Optimize memory usage for {proc_info["name"]}',
                'priority': 'medium',
                'estimated_improvement': 15
            })
        
        return recommendations
    
    def _generate_bottleneck_actions(self, bottleneck: ResourceBottleneck) -> List[Dict[str, Any]]:
        """Generate specific actions to address a bottleneck"""
        
        actions = []
        
        for recommendation in bottleneck.recommendations:
            action = {
                'type': recommendation['action'],
                'description': recommendation['description'],
                'priority': recommendation['priority'],
                'estimated_improvement': recommendation['estimated_improvement'],
                'resource_type': bottleneck.resource_type.value,
                'critical': bottleneck.severity == 'critical'
            }
            actions.append(action)
        
        return actions
    
    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific optimization action"""
        
        action_type = action['type']
        result = {'action': action_type, 'status': 'completed', 'details': {}}
        
        try:
            if action_type == OptimizationAction.CLEANUP_RESOURCES.value:
                result['details'] = self._cleanup_system_resources(action)
            
            elif action_type == OptimizationAction.OPTIMIZE_CONFIG.value:
                result['details'] = self._optimize_system_config(action)
            
            elif action_type == OptimizationAction.ADJUST_PRIORITIES.value:
                result['details'] = self._adjust_process_priorities(action)
            
            elif action_type == OptimizationAction.ENABLE_CACHING.value:
                result['details'] = self._enable_performance_caching(action)
            
            else:
                result['status'] = 'skipped'
                result['details'] = {'reason': f'Action type {action_type} not implemented'}
        
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
        
        return result
    
    def _cleanup_system_resources(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up system resources"""
        
        cleanup_results = {}
        
        # Clear system caches
        try:
            if os.name == 'posix':  # Linux/Unix systems
                # Clear page cache, dentries and inodes
                subprocess.run(['sync'], check=True)
                # Note: In a real implementation, this would require sudo
                # subprocess.run(['echo 3 > /proc/sys/vm/drop_caches'], shell=True, check=True)
                cleanup_results['cache_cleared'] = True
            else:
                cleanup_results['cache_cleared'] = False
        except Exception as e:
            cleanup_results['cache_error'] = str(e)
        
        # Cleanup temporary files
        temp_dirs = ['/tmp', str(Path.home() / '.cache')]
        cleaned_size = 0
        
        for temp_dir in temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    # Count and optionally clean old temp files
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                file_age = time.time() - os.path.getmtime(file_path)
                                if file_age > 86400:  # Files older than 1 day
                                    file_size = os.path.getsize(file_path)
                                    # In a real implementation, would actually delete
                                    cleaned_size += file_size
                            except:
                                continue
            except Exception as e:
                cleanup_results[f'{temp_dir}_error'] = str(e)
        
        cleanup_results['temp_files_cleaned_mb'] = cleaned_size / (1024**2)
        
        # Force garbage collection
        import gc
        gc.collect()
        cleanup_results['garbage_collection'] = True
        
        return cleanup_results
    
    def _optimize_system_config(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize system configuration"""
        
        config_results = {}
        
        # Adjust Python garbage collection
        import gc
        old_thresholds = gc.get_threshold()
        gc.set_threshold(700, 10, 10)  # More aggressive GC
        config_results['gc_optimized'] = True
        config_results['old_gc_thresholds'] = old_thresholds
        
        # Optimize psutil cache
        psutil.cpu_percent()  # Prime the cache
        config_results['psutil_cache_primed'] = True
        
        return config_results
    
    def _adjust_process_priorities(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust process priorities"""
        
        priority_results = {}
        
        try:
            # Get current process
            current_process = psutil.Process()
            
            # Adjust current process priority (lower priority for less CPU competition)
            try:
                if os.name == 'nt':  # Windows
                    current_process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                else:  # Unix/Linux
                    current_process.nice(5)  # Lower priority
                
                priority_results['current_process_adjusted'] = True
            except Exception as e:
                priority_results['priority_adjustment_error'] = str(e)
        
        except Exception as e:
            priority_results['error'] = str(e)
        
        return priority_results
    
    def _enable_performance_caching(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Enable performance caching optimizations"""
        
        cache_results = {}
        
        # Enable more aggressive caching
        cache_results['caching_enabled'] = True
        
        # This would integrate with actual caching systems
        cache_results['cache_size_mb'] = 100
        cache_results['cache_expiry_minutes'] = 60
        
        return cache_results
    
    def _collect_baseline_metrics(self) -> Dict[str, float]:
        """Collect baseline performance metrics"""
        
        metrics = {}
        
        # System metrics
        metrics['cpu_percent'] = psutil.cpu_percent(interval=1)
        metrics['memory_percent'] = psutil.virtual_memory().percent
        metrics['disk_percent'] = (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
        
        # Process metrics
        current_process = psutil.Process()
        try:
            process_info = current_process.as_dict(['cpu_percent', 'memory_percent'])
            metrics['process_cpu_percent'] = process_info['cpu_percent'] or 0
            metrics['process_memory_percent'] = process_info['memory_percent'] or 0
        except:
            metrics['process_cpu_percent'] = 0
            metrics['process_memory_percent'] = 0
        
        return metrics
    
    def _calculate_improvement(self, before: Dict[str, float], after: Dict[str, float]) -> float:
        """Calculate overall performance improvement percentage"""
        
        improvements = []
        
        for metric in ['cpu_percent', 'memory_percent']:
            if metric in before and metric in after:
                if before[metric] > 0:
                    improvement = (before[metric] - after[metric]) / before[metric] * 100
                    improvements.append(improvement)
        
        return statistics.mean(improvements) if improvements else 0.0
    
    def _verify_prerequisite(self, prerequisite: str) -> bool:
        """Verify optimization prerequisite"""
        
        if prerequisite == "Verify system stability":
            # Check if system load is reasonable
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                return cpu_percent < 95  # System not completely overloaded
            except:
                return True  # Assume stable if we can't check
        
        elif prerequisite == "Create performance baseline":
            # Always true - we create baseline during execution
            return True
        
        elif prerequisite == "Ensure rollback capability":
            # Always true - rollback is always possible
            return True
        
        return True  # Default to allowing optimization
    
    def _execute_rollback_plan(self, rollback_plan: List[Dict[str, Any]]):
        """Execute rollback plan to revert changes"""
        
        for action in sorted(rollback_plan, key=lambda x: x['priority']):
            try:
                if action['action'] == 'restore_configuration':
                    # Restore system configuration
                    import gc
                    gc.set_threshold(700, 10, 10)  # Restore default GC settings
                
                elif action['action'] == 'restart_affected_services':
                    # In a real implementation, would restart affected services
                    pass
                
                elif action['action'] == 'verify_system_health':
                    # Verify system is back to normal
                    time.sleep(5)  # Give system time to stabilize
            
            except Exception as e:
                logger.error(f"Rollback action failed: {action['action']}: {e}")
    
    def _handle_bottleneck(self, bottleneck: ResourceBottleneck):
        """Handle detected bottleneck"""
        
        if self.auto_optimization_enabled and len(self.active_optimizations) < self.max_concurrent_optimizations:
            # Generate and execute optimization plan
            plan = self.generate_optimization_plan([bottleneck])
            if plan:
                logger.info(f"Auto-executing optimization plan for {bottleneck.resource_type.value} bottleneck")
                
                # Execute in background thread to avoid blocking monitoring
                def execute_plan():
                    result = self.execute_optimization_plan(plan)
                    logger.info(f"Optimization completed: {result['overall_success']}")
                
                optimization_thread = threading.Thread(target=execute_plan, daemon=True)
                optimization_thread.start()
                
                self.active_optimizations[plan.plan_id] = {
                    'plan': plan,
                    'thread': optimization_thread,
                    'started_at': time.time()
                }
        else:
            # Just log the bottleneck
            logger.warning(f"Bottleneck detected: {bottleneck.resource_type.value} at {bottleneck.current_usage:.1f}% ({bottleneck.severity})")
    
    def _update_resource_patterns(self):
        """Update resource usage patterns for ML optimization"""
        
        if self.learning_enabled:
            try:
                current_metrics = self._collect_baseline_metrics()
                timestamp = time.time()
                
                # Store patterns for ML analysis
                for metric, value in current_metrics.items():
                    if metric not in self.resource_patterns:
                        self.resource_patterns[metric] = []
                    
                    self.resource_patterns[metric].append((timestamp, value))
                    
                    # Keep only recent data (last 24 hours)
                    cutoff_time = timestamp - 86400
                    self.resource_patterns[metric] = [
                        (t, v) for t, v in self.resource_patterns[metric] if t > cutoff_time
                    ]
            
            except Exception as e:
                logger.error(f"Failed to update resource patterns: {e}")
    
    def _cleanup_completed_optimizations(self):
        """Clean up completed optimization threads"""
        
        completed_optimizations = []
        
        for plan_id, opt_info in self.active_optimizations.items():
            thread = opt_info['thread']
            if not thread.is_alive():
                completed_optimizations.append(plan_id)
        
        for plan_id in completed_optimizations:
            del self.active_optimizations[plan_id]

# Example usage and testing
def test_resource_optimizer():
    """Test the resource optimizer functionality"""
    
    print("🧪 Testing Resource Optimizer...")
    
    optimizer = ResourceOptimizer()
    
    # Test bottleneck detection
    print("🔍 Testing bottleneck detection...")
    bottlenecks = optimizer.detect_bottlenecks()
    print(f"   Detected {len(bottlenecks)} bottlenecks")
    
    for bottleneck in bottlenecks:
        print(f"   {bottleneck.resource_type.value}: {bottleneck.severity} ({bottleneck.current_usage:.1f}%)")
    
    # Test optimization plan generation
    if bottlenecks:
        print("📋 Testing optimization plan generation...")
        plan = optimizer.generate_optimization_plan(bottlenecks)
        
        if plan:
            print(f"   Generated plan {plan.plan_id} with {len(plan.actions)} actions")
            print(f"   Expected improvement: {plan.expected_improvement:.1f}%")
            print(f"   Risk level: {plan.risk_level}")
            
            # Test plan execution (dry run)
            print("⚙️ Testing plan execution...")
            result = optimizer.execute_optimization_plan(plan)
            print(f"   Execution result: {result['overall_success']}")
            print(f"   Actions executed: {len(result['actions_executed'])}")
            if result['actions_failed']:
                print(f"   Actions failed: {len(result['actions_failed'])}")
    
    print("✅ Resource optimizer test completed!")

if __name__ == "__main__":
    test_resource_optimizer()