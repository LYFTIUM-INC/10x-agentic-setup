#!/usr/bin/env python3
"""
Advanced Bottleneck Detection and Resolution System
ML-powered detection and automated resolution of performance bottlenecks
"""

import time
import json
import logging
import statistics
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BottleneckCategory(Enum):
    COMPUTATIONAL = "computational"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    CONCURRENCY = "concurrency"
    ALGORITHM = "algorithm"

class DetectionMethod(Enum):
    STATISTICAL_ANALYSIS = "statistical"
    PATTERN_MATCHING = "pattern_matching"
    ANOMALY_DETECTION = "anomaly_detection"
    PREDICTIVE_MODELING = "predictive"

@dataclass
class BottleneckSignature:
    signature_id: str
    category: BottleneckCategory
    symptoms: List[str]
    thresholds: Dict[str, float]
    detection_patterns: List[Dict[str, Any]]
    resolution_strategies: List[Dict[str, Any]]
    confidence_threshold: float

@dataclass
class DetectedBottleneck:
    bottleneck_id: str
    category: BottleneckCategory
    signature_match: str
    detection_method: DetectionMethod
    confidence: float
    severity: str
    symptoms_observed: List[str]
    metrics_snapshot: Dict[str, Any]
    root_cause_analysis: Dict[str, Any]
    resolution_recommendations: List[Dict[str, Any]]
    detected_at: float
    duration_estimated: float

class AdvancedBottleneckDetector:
    """ML-powered bottleneck detection with intelligent resolution"""
    
    def __init__(self, metrics_collector=None, analyzer=None):
        self.metrics_collector = metrics_collector
        self.analyzer = analyzer
        
        # Detection state
        self.metric_history = defaultdict(lambda: deque(maxlen=100))
        self.bottleneck_history = []
        self.detection_signatures = self._load_detection_signatures()
        
        # ML components
        self.anomaly_detector = AnomalyDetector()
        self.pattern_recognizer = PatternRecognizer()
        self.predictive_model = PredictiveBottleneckModel()
        
        # Detection parameters
        self.detection_interval = 15  # seconds
        self.history_window = 300  # 5 minutes
        self.confidence_threshold = 0.7
        
        # Performance tracking
        self.detection_statistics = {
            'total_detections': 0,
            'true_positives': 0,
            'false_positives': 0,
            'resolution_success_rate': 0.0
        }
        
        logger.info("Advanced bottleneck detector initialized")
    
    def _load_detection_signatures(self) -> List[BottleneckSignature]:
        """Load predefined bottleneck detection signatures"""
        
        signatures = [
            # CPU Bottleneck Signatures
            BottleneckSignature(
                signature_id="cpu_saturation",
                category=BottleneckCategory.COMPUTATIONAL,
                symptoms=["high_cpu_usage", "long_execution_times", "process_queuing"],
                thresholds={"cpu_usage": 85.0, "execution_time_increase": 50.0},
                detection_patterns=[
                    {"pattern": "sustained_high_cpu", "duration_min": 2},
                    {"pattern": "execution_time_spike", "multiplier": 2.0}
                ],
                resolution_strategies=[
                    {"strategy": "parallel_processing", "priority": 1},
                    {"strategy": "cpu_optimization", "priority": 2},
                    {"strategy": "workload_distribution", "priority": 3}
                ],
                confidence_threshold=0.8
            ),
            
            # Memory Bottleneck Signatures
            BottleneckSignature(
                signature_id="memory_pressure",
                category=BottleneckCategory.MEMORY,
                symptoms=["high_memory_usage", "swap_activity", "gc_pressure"],
                thresholds={"memory_usage": 80.0, "gc_frequency_increase": 100.0},
                detection_patterns=[
                    {"pattern": "memory_growth_trend", "rate_per_hour": 10.0},
                    {"pattern": "frequent_gc", "frequency_increase": 2.0}
                ],
                resolution_strategies=[
                    {"strategy": "memory_optimization", "priority": 1},
                    {"strategy": "cache_tuning", "priority": 2},
                    {"strategy": "memory_scaling", "priority": 3}
                ],
                confidence_threshold=0.75
            ),
            
            # I/O Bottleneck Signatures
            BottleneckSignature(
                signature_id="io_bottleneck",
                category=BottleneckCategory.STORAGE,
                symptoms=["high_disk_usage", "io_wait", "slow_file_operations"],
                thresholds={"disk_usage": 90.0, "io_wait_time": 20.0},
                detection_patterns=[
                    {"pattern": "io_queue_buildup", "queue_depth": 10},
                    {"pattern": "file_operation_slowdown", "slowdown_factor": 3.0}
                ],
                resolution_strategies=[
                    {"strategy": "io_optimization", "priority": 1},
                    {"strategy": "disk_cleanup", "priority": 2},
                    {"strategy": "storage_scaling", "priority": 3}
                ],
                confidence_threshold=0.7
            ),
            
            # Concurrency Bottleneck Signatures
            BottleneckSignature(
                signature_id="concurrency_limit",
                category=BottleneckCategory.CONCURRENCY,
                symptoms=["thread_contention", "lock_waiting", "serialization_points"],
                thresholds={"thread_utilization": 95.0, "lock_wait_time": 100.0},
                detection_patterns=[
                    {"pattern": "thread_pool_exhaustion", "utilization": 0.95},
                    {"pattern": "serialization_bottleneck", "wait_ratio": 0.5}
                ],
                resolution_strategies=[
                    {"strategy": "concurrency_optimization", "priority": 1},
                    {"strategy": "lock_optimization", "priority": 2},
                    {"strategy": "async_processing", "priority": 3}
                ],
                confidence_threshold=0.8
            ),
            
            # Algorithm Bottleneck Signatures
            BottleneckSignature(
                signature_id="algorithm_inefficiency",
                category=BottleneckCategory.ALGORITHM,
                symptoms=["execution_time_complexity", "resource_usage_scaling", "performance_degradation"],
                thresholds={"complexity_factor": 2.0, "scaling_factor": 1.5},
                detection_patterns=[
                    {"pattern": "exponential_scaling", "growth_rate": 2.0},
                    {"pattern": "inefficient_algorithm", "complexity_increase": 50.0}
                ],
                resolution_strategies=[
                    {"strategy": "algorithm_optimization", "priority": 1},
                    {"strategy": "data_structure_optimization", "priority": 2},
                    {"strategy": "caching_strategy", "priority": 3}
                ],
                confidence_threshold=0.6
            )
        ]
        
        return signatures
    
    def detect_bottlenecks(self, current_metrics: Dict[str, Any] = None) -> List[DetectedBottleneck]:
        """Detect bottlenecks using multiple detection methods"""
        
        if current_metrics is None:
            current_metrics = self._collect_current_metrics()
        
        # Update metric history
        self._update_metric_history(current_metrics)
        
        detected_bottlenecks = []
        
        # Statistical analysis detection
        statistical_bottlenecks = self._detect_statistical_anomalies(current_metrics)
        detected_bottlenecks.extend(statistical_bottlenecks)
        
        # Pattern matching detection
        pattern_bottlenecks = self._detect_pattern_bottlenecks(current_metrics)
        detected_bottlenecks.extend(pattern_bottlenecks)
        
        # Anomaly detection
        anomaly_bottlenecks = self._detect_anomalies(current_metrics)
        detected_bottlenecks.extend(anomaly_bottlenecks)
        
        # Predictive detection
        predictive_bottlenecks = self._detect_predictive_bottlenecks(current_metrics)
        detected_bottlenecks.extend(predictive_bottlenecks)
        
        # Deduplicate and rank bottlenecks
        deduplicated_bottlenecks = self._deduplicate_bottlenecks(detected_bottlenecks)
        
        # Update detection statistics
        self.detection_statistics['total_detections'] += len(deduplicated_bottlenecks)
        
        return deduplicated_bottlenecks
    
    def _detect_statistical_anomalies(self, metrics: Dict[str, Any]) -> List[DetectedBottleneck]:
        """Detect bottlenecks using statistical analysis"""
        
        bottlenecks = []
        
        for signature in self.detection_signatures:
            confidence = self._calculate_signature_match(signature, metrics)
            
            if confidence >= signature.confidence_threshold:
                bottleneck = DetectedBottleneck(
                    bottleneck_id=f"stat_{signature.signature_id}_{int(time.time())}",
                    category=signature.category,
                    signature_match=signature.signature_id,
                    detection_method=DetectionMethod.STATISTICAL_ANALYSIS,
                    confidence=confidence,
                    severity=self._calculate_severity(confidence, metrics),
                    symptoms_observed=self._identify_symptoms(signature, metrics),
                    metrics_snapshot=metrics.copy(),
                    root_cause_analysis=self._perform_root_cause_analysis(signature, metrics),
                    resolution_recommendations=signature.resolution_strategies,
                    detected_at=time.time(),
                    duration_estimated=self._estimate_bottleneck_duration(signature, metrics)
                )
                bottlenecks.append(bottleneck)
        
        return bottlenecks
    
    def _detect_pattern_bottlenecks(self, metrics: Dict[str, Any]) -> List[DetectedBottleneck]:
        """Detect bottlenecks using pattern recognition"""
        
        bottlenecks = []
        
        # Analyze patterns in metric history
        patterns = self.pattern_recognizer.analyze_patterns(self.metric_history)
        
        for pattern in patterns:
            if pattern['anomaly_score'] > 0.7:
                # Map pattern to bottleneck signature
                matching_signature = self._find_matching_signature(pattern)
                
                if matching_signature:
                    bottleneck = DetectedBottleneck(
                        bottleneck_id=f"pattern_{pattern['pattern_id']}_{int(time.time())}",
                        category=matching_signature.category,
                        signature_match=matching_signature.signature_id,
                        detection_method=DetectionMethod.PATTERN_MATCHING,
                        confidence=pattern['anomaly_score'],
                        severity=self._calculate_severity(pattern['anomaly_score'], metrics),
                        symptoms_observed=pattern['symptoms'],
                        metrics_snapshot=metrics.copy(),
                        root_cause_analysis=pattern['analysis'],
                        resolution_recommendations=matching_signature.resolution_strategies,
                        detected_at=time.time(),
                        duration_estimated=pattern.get('estimated_duration', 60.0)
                    )
                    bottlenecks.append(bottleneck)
        
        return bottlenecks
    
    def _detect_anomalies(self, metrics: Dict[str, Any]) -> List[DetectedBottleneck]:
        """Detect bottlenecks using anomaly detection"""
        
        bottlenecks = []
        
        # Run anomaly detection on current metrics
        anomalies = self.anomaly_detector.detect_anomalies(metrics, self.metric_history)
        
        for anomaly in anomalies:
            if anomaly['severity'] in ['high', 'critical']:
                # Find best matching signature
                best_signature = self._find_best_signature_for_anomaly(anomaly)
                
                if best_signature:
                    bottleneck = DetectedBottleneck(
                        bottleneck_id=f"anomaly_{anomaly['anomaly_id']}_{int(time.time())}",
                        category=best_signature.category,
                        signature_match=best_signature.signature_id,
                        detection_method=DetectionMethod.ANOMALY_DETECTION,
                        confidence=anomaly['confidence'],
                        severity=anomaly['severity'],
                        symptoms_observed=anomaly['symptoms'],
                        metrics_snapshot=metrics.copy(),
                        root_cause_analysis=anomaly['analysis'],
                        resolution_recommendations=best_signature.resolution_strategies,
                        detected_at=time.time(),
                        duration_estimated=anomaly.get('estimated_duration', 120.0)
                    )
                    bottlenecks.append(bottleneck)
        
        return bottlenecks
    
    def _detect_predictive_bottlenecks(self, metrics: Dict[str, Any]) -> List[DetectedBottleneck]:
        """Detect bottlenecks using predictive modeling"""
        
        bottlenecks = []
        
        # Run predictive analysis
        predictions = self.predictive_model.predict_bottlenecks(metrics, self.metric_history)
        
        for prediction in predictions:
            if prediction['probability'] > 0.8:  # High probability of bottleneck
                # Find signature for predicted bottleneck type
                signature = self._find_signature_by_category(prediction['category'])
                
                if signature:
                    bottleneck = DetectedBottleneck(
                        bottleneck_id=f"pred_{prediction['prediction_id']}_{int(time.time())}",
                        category=BottleneckCategory(prediction['category']),
                        signature_match=signature.signature_id,
                        detection_method=DetectionMethod.PREDICTIVE_MODELING,
                        confidence=prediction['probability'],
                        severity='medium',  # Predictive bottlenecks start as medium
                        symptoms_observed=prediction['early_symptoms'],
                        metrics_snapshot=metrics.copy(),
                        root_cause_analysis=prediction['analysis'],
                        resolution_recommendations=signature.resolution_strategies,
                        detected_at=time.time(),
                        duration_estimated=prediction['time_to_bottleneck']
                    )
                    bottlenecks.append(bottleneck)
        
        return bottlenecks
    
    def _calculate_signature_match(self, signature: BottleneckSignature, metrics: Dict[str, Any]) -> float:
        """Calculate how well current metrics match a signature"""
        
        match_scores = []
        
        # Check threshold-based matches
        for metric, threshold in signature.thresholds.items():
            if metric in metrics:
                value = metrics[metric]
                if value >= threshold:
                    # Score based on how much threshold is exceeded
                    score = min(1.0, value / threshold)
                    match_scores.append(score)
                else:
                    # Partial score for values approaching threshold
                    score = max(0.0, value / threshold * 0.5)
                    match_scores.append(score)
            else:
                # Penalize missing metrics
                match_scores.append(0.0)
        
        # Check pattern matches
        pattern_matches = []
        for pattern in signature.detection_patterns:
            pattern_score = self._evaluate_pattern(pattern, metrics)
            pattern_matches.append(pattern_score)
        
        # Combine threshold and pattern scores
        threshold_score = statistics.mean(match_scores) if match_scores else 0.0
        pattern_score = statistics.mean(pattern_matches) if pattern_matches else 0.0
        
        # Weighted combination
        final_score = (threshold_score * 0.6) + (pattern_score * 0.4)
        
        return final_score
    
    def _evaluate_pattern(self, pattern: Dict[str, Any], metrics: Dict[str, Any]) -> float:
        """Evaluate a specific pattern against current metrics"""
        
        pattern_type = pattern.get('pattern')
        
        if pattern_type == 'sustained_high_cpu':
            # Check if CPU has been high for specified duration
            cpu_history = list(self.metric_history['cpu_usage'])
            if len(cpu_history) >= pattern.get('duration_min', 2):
                recent_values = cpu_history[-pattern.get('duration_min', 2):]
                if all(value > 80 for value in recent_values):
                    return 1.0
            return 0.0
        
        elif pattern_type == 'execution_time_spike':
            # Check if execution times have spiked
            exec_time_history = list(self.metric_history['avg_execution_time'])
            if len(exec_time_history) >= 3:
                recent_avg = statistics.mean(exec_time_history[-3:])
                baseline_avg = statistics.mean(exec_time_history[:-3]) if len(exec_time_history) > 3 else recent_avg
                
                if baseline_avg > 0:
                    spike_ratio = recent_avg / baseline_avg
                    threshold = pattern.get('multiplier', 2.0)
                    if spike_ratio >= threshold:
                        return min(1.0, spike_ratio / threshold)
            return 0.0
        
        elif pattern_type == 'memory_growth_trend':
            # Check for memory growth trend
            memory_history = list(self.metric_history['memory_usage'])
            if len(memory_history) >= 10:
                # Calculate trend using linear regression
                x = list(range(len(memory_history)))
                y = memory_history
                
                # Simple linear regression slope
                n = len(x)
                slope = (n * sum(xi * yi for xi, yi in zip(x, y)) - sum(x) * sum(y)) / (n * sum(xi * xi for xi in x) - sum(x) ** 2)
                
                growth_rate = slope * 60  # Convert to per-hour rate
                threshold = pattern.get('rate_per_hour', 10.0)
                
                if growth_rate >= threshold:
                    return min(1.0, growth_rate / threshold)
            return 0.0
        
        # Default pattern evaluation
        return 0.5
    
    def _identify_symptoms(self, signature: BottleneckSignature, metrics: Dict[str, Any]) -> List[str]:
        """Identify which symptoms are currently observed"""
        
        observed_symptoms = []
        
        for symptom in signature.symptoms:
            if self._is_symptom_present(symptom, metrics):
                observed_symptoms.append(symptom)
        
        return observed_symptoms
    
    def _is_symptom_present(self, symptom: str, metrics: Dict[str, Any]) -> bool:
        """Check if a specific symptom is present in current metrics"""
        
        symptom_checks = {
            'high_cpu_usage': lambda m: m.get('cpu_usage', 0) > 80,
            'long_execution_times': lambda m: m.get('avg_execution_time', 0) > 10,
            'high_memory_usage': lambda m: m.get('memory_usage', 0) > 80,
            'high_disk_usage': lambda m: m.get('disk_usage', 0) > 85,
            'process_queuing': lambda m: m.get('active_processes', 0) > 100,
            'swap_activity': lambda m: m.get('swap_usage', 0) > 10,
            'gc_pressure': lambda m: m.get('gc_frequency', 0) > 5,
            'io_wait': lambda m: m.get('io_wait_time', 0) > 10,
            'thread_contention': lambda m: m.get('thread_contention', 0) > 0.5,
            'lock_waiting': lambda m: m.get('lock_wait_time', 0) > 50
        }
        
        check_function = symptom_checks.get(symptom)
        if check_function:
            return check_function(metrics)
        
        return False
    
    def _perform_root_cause_analysis(self, signature: BottleneckSignature, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Perform root cause analysis for detected bottleneck"""
        
        analysis = {
            'category': signature.category.value,
            'primary_factors': [],
            'contributing_factors': [],
            'confidence_factors': {}
        }
        
        # Analyze based on category
        if signature.category == BottleneckCategory.COMPUTATIONAL:
            analysis['primary_factors'] = self._analyze_cpu_factors(metrics)
        elif signature.category == BottleneckCategory.MEMORY:
            analysis['primary_factors'] = self._analyze_memory_factors(metrics)
        elif signature.category == BottleneckCategory.STORAGE:
            analysis['primary_factors'] = self._analyze_storage_factors(metrics)
        
        # Add confidence factors
        for symptom in signature.symptoms:
            if self._is_symptom_present(symptom, metrics):
                analysis['confidence_factors'][symptom] = 1.0
        
        return analysis
    
    def _analyze_cpu_factors(self, metrics: Dict[str, Any]) -> List[str]:
        """Analyze CPU-related bottleneck factors"""
        
        factors = []
        
        cpu_usage = metrics.get('cpu_usage', 0)
        if cpu_usage > 90:
            factors.append("CPU saturation - near maximum utilization")
        elif cpu_usage > 80:
            factors.append("High CPU load - approaching saturation")
        
        exec_time = metrics.get('avg_execution_time', 0)
        if exec_time > 20:
            factors.append("Extremely long execution times indicating CPU bottleneck")
        elif exec_time > 10:
            factors.append("Long execution times suggesting CPU pressure")
        
        return factors
    
    def _analyze_memory_factors(self, metrics: Dict[str, Any]) -> List[str]:
        """Analyze memory-related bottleneck factors"""
        
        factors = []
        
        memory_usage = metrics.get('memory_usage', 0)
        if memory_usage > 90:
            factors.append("Memory exhaustion - critical shortage")
        elif memory_usage > 80:
            factors.append("High memory pressure")
        
        return factors
    
    def _analyze_storage_factors(self, metrics: Dict[str, Any]) -> List[str]:
        """Analyze storage-related bottleneck factors"""
        
        factors = []
        
        disk_usage = metrics.get('disk_usage', 0)
        if disk_usage > 95:
            factors.append("Disk space critical - immediate cleanup required")
        elif disk_usage > 85:
            factors.append("High disk usage - cleanup recommended")
        
        return factors
    
    def _calculate_severity(self, confidence: float, metrics: Dict[str, Any]) -> str:
        """Calculate bottleneck severity"""
        
        if confidence > 0.9:
            return 'critical'
        elif confidence > 0.8:
            return 'high'
        elif confidence > 0.6:
            return 'medium'
        else:
            return 'low'
    
    def _estimate_bottleneck_duration(self, signature: BottleneckSignature, metrics: Dict[str, Any]) -> float:
        """Estimate how long the bottleneck will persist"""
        
        # Base duration estimates by category
        base_durations = {
            BottleneckCategory.COMPUTATIONAL: 300,  # 5 minutes
            BottleneckCategory.MEMORY: 600,         # 10 minutes
            BottleneckCategory.STORAGE: 1800,       # 30 minutes
            BottleneckCategory.NETWORK: 180,        # 3 minutes
            BottleneckCategory.CONCURRENCY: 120,    # 2 minutes
            BottleneckCategory.ALGORITHM: 3600      # 1 hour
        }
        
        base_duration = base_durations.get(signature.category, 300)
        
        # Adjust based on severity
        severity_multipliers = {'low': 0.5, 'medium': 1.0, 'high': 1.5, 'critical': 2.0}
        severity = self._calculate_severity(0.8, metrics)  # Use default confidence
        multiplier = severity_multipliers.get(severity, 1.0)
        
        return base_duration * multiplier
    
    def _collect_current_metrics(self) -> Dict[str, Any]:
        """Collect current performance metrics"""
        
        metrics = {}
        
        if self.metrics_collector:
            # Get metrics from collector
            try:
                summary = self.metrics_collector.get_performance_summary(window_seconds=60)
                metrics.update({
                    'cpu_usage': summary.get('system_metrics', {}).get('avg_cpu_usage', 0),
                    'memory_usage': summary.get('system_metrics', {}).get('avg_memory_usage', 0),
                    'disk_usage': summary.get('system_metrics', {}).get('avg_disk_usage', 0),
                    'avg_execution_time': summary.get('tool_execution', {}).get('avg_execution_time', 0),
                    'success_rate': summary.get('tool_execution', {}).get('success_rate', 100)
                })
            except:
                pass
        
        # Add timestamp
        metrics['timestamp'] = time.time()
        
        return metrics
    
    def _update_metric_history(self, metrics: Dict[str, Any]):
        """Update metric history with current values"""
        
        for metric, value in metrics.items():
            if isinstance(value, (int, float)):
                self.metric_history[metric].append(value)
    
    def _deduplicate_bottlenecks(self, bottlenecks: List[DetectedBottleneck]) -> List[DetectedBottleneck]:
        """Remove duplicate bottlenecks and keep the highest confidence ones"""
        
        # Group by category
        by_category = defaultdict(list)
        for bottleneck in bottlenecks:
            by_category[bottleneck.category].append(bottleneck)
        
        # Keep highest confidence from each category
        deduplicated = []
        for category, category_bottlenecks in by_category.items():
            if category_bottlenecks:
                # Sort by confidence and take the best
                best_bottleneck = max(category_bottlenecks, key=lambda b: b.confidence)
                deduplicated.append(best_bottleneck)
        
        return deduplicated
    
    def _find_matching_signature(self, pattern: Dict[str, Any]) -> Optional[BottleneckSignature]:
        """Find signature that matches a detected pattern"""
        
        # Simple pattern-to-signature mapping
        pattern_mappings = {
            'cpu_anomaly': 'cpu_saturation',
            'memory_anomaly': 'memory_pressure',
            'io_anomaly': 'io_bottleneck',
            'concurrency_anomaly': 'concurrency_limit'
        }
        
        pattern_type = pattern.get('pattern_type', 'unknown')
        signature_id = pattern_mappings.get(pattern_type)
        
        if signature_id:
            return next((s for s in self.detection_signatures if s.signature_id == signature_id), None)
        
        return None
    
    def _find_best_signature_for_anomaly(self, anomaly: Dict[str, Any]) -> Optional[BottleneckSignature]:
        """Find best matching signature for an anomaly"""
        
        # Map anomaly types to signatures
        anomaly_type = anomaly.get('anomaly_type', 'unknown')
        
        type_mappings = {
            'cpu': 'cpu_saturation',
            'memory': 'memory_pressure',
            'disk': 'io_bottleneck',
            'execution_time': 'algorithm_inefficiency'
        }
        
        signature_id = type_mappings.get(anomaly_type)
        
        if signature_id:
            return next((s for s in self.detection_signatures if s.signature_id == signature_id), None)
        
        return None
    
    def _find_signature_by_category(self, category: str) -> Optional[BottleneckSignature]:
        """Find signature by category"""
        
        try:
            category_enum = BottleneckCategory(category)
            return next((s for s in self.detection_signatures if s.category == category_enum), None)
        except ValueError:
            return None

class AnomalyDetector:
    """Simple anomaly detection for bottleneck detection"""
    
    def detect_anomalies(self, current_metrics: Dict[str, Any], 
                        metric_history: Dict[str, deque]) -> List[Dict[str, Any]]:
        """Detect anomalies in current metrics"""
        
        anomalies = []
        
        for metric, value in current_metrics.items():
            if isinstance(value, (int, float)) and metric in metric_history:
                history = list(metric_history[metric])
                
                if len(history) >= 10:
                    mean_val = statistics.mean(history)
                    std_val = statistics.stdev(history) if len(history) > 1 else 0
                    
                    # Z-score anomaly detection
                    if std_val > 0:
                        z_score = abs(value - mean_val) / std_val
                        
                        if z_score > 3:  # 3-sigma rule
                            anomalies.append({
                                'anomaly_id': f"anomaly_{metric}_{int(time.time())}",
                                'anomaly_type': metric.replace('_usage', '').replace('_', ''),
                                'metric': metric,
                                'value': value,
                                'expected_range': (mean_val - 2*std_val, mean_val + 2*std_val),
                                'z_score': z_score,
                                'severity': 'critical' if z_score > 4 else 'high',
                                'confidence': min(1.0, z_score / 5.0),
                                'symptoms': [f"{metric}_anomaly"],
                                'analysis': {
                                    'description': f"Significant deviation in {metric}",
                                    'z_score': z_score,
                                    'baseline': mean_val
                                }
                            })
        
        return anomalies

class PatternRecognizer:
    """Pattern recognition for bottleneck detection"""
    
    def analyze_patterns(self, metric_history: Dict[str, deque]) -> List[Dict[str, Any]]:
        """Analyze patterns in metric history"""
        
        patterns = []
        
        for metric, history in metric_history.items():
            if len(history) >= 20:  # Need sufficient history
                values = list(history)
                
                # Detect trends
                trend_pattern = self._detect_trend(metric, values)
                if trend_pattern:
                    patterns.append(trend_pattern)
                
                # Detect cycles
                cycle_pattern = self._detect_cycles(metric, values)
                if cycle_pattern:
                    patterns.append(cycle_pattern)
        
        return patterns
    
    def _detect_trend(self, metric: str, values: List[float]) -> Optional[Dict[str, Any]]:
        """Detect trend patterns in values"""
        
        if len(values) < 10:
            return None
        
        # Simple trend detection using linear regression
        x = list(range(len(values)))
        y = values
        
        n = len(x)
        slope = (n * sum(xi * yi for xi, yi in zip(x, y)) - sum(x) * sum(y)) / (n * sum(xi * xi for xi in x) - sum(x) ** 2)
        
        # Strong trend threshold
        if abs(slope) > 0.5:
            return {
                'pattern_id': f"trend_{metric}_{int(time.time())}",
                'pattern_type': f"{metric}_trend",
                'metric': metric,
                'trend_slope': slope,
                'anomaly_score': min(1.0, abs(slope) / 2.0),
                'symptoms': [f"{metric}_trend"],
                'analysis': {
                    'description': f"{'Increasing' if slope > 0 else 'Decreasing'} trend in {metric}",
                    'slope': slope
                }
            }
        
        return None
    
    def _detect_cycles(self, metric: str, values: List[float]) -> Optional[Dict[str, Any]]:
        """Detect cyclical patterns in values"""
        
        # Simple cycle detection (this would be more sophisticated in practice)
        if len(values) >= 30:
            # Look for repeating patterns
            variance = statistics.variance(values) if len(values) > 1 else 0
            
            if variance > 100:  # High variance might indicate cycles
                return {
                    'pattern_id': f"cycle_{metric}_{int(time.time())}",
                    'pattern_type': f"{metric}_cycle",
                    'metric': metric,
                    'variance': variance,
                    'anomaly_score': min(1.0, variance / 500.0),
                    'symptoms': [f"{metric}_volatility"],
                    'analysis': {
                        'description': f"High volatility detected in {metric}",
                        'variance': variance
                    }
                }
        
        return None

class PredictiveBottleneckModel:
    """Predictive modeling for bottleneck forecasting"""
    
    def predict_bottlenecks(self, current_metrics: Dict[str, Any], 
                          metric_history: Dict[str, deque]) -> List[Dict[str, Any]]:
        """Predict future bottlenecks"""
        
        predictions = []
        
        # Simple predictive rules (would be ML models in production)
        
        # CPU bottleneck prediction
        cpu_history = list(metric_history.get('cpu_usage', []))
        if len(cpu_history) >= 5:
            recent_trend = statistics.mean(cpu_history[-3:]) - statistics.mean(cpu_history[-5:-2])
            
            if recent_trend > 5:  # CPU usage increasing
                current_cpu = cpu_history[-1] if cpu_history else 0
                time_to_bottleneck = max(60, (85 - current_cpu) / recent_trend * 60)  # Seconds
                
                predictions.append({
                    'prediction_id': f"cpu_pred_{int(time.time())}",
                    'category': 'computational',
                    'probability': min(0.9, recent_trend / 10.0),
                    'time_to_bottleneck': time_to_bottleneck,
                    'early_symptoms': ['increasing_cpu_trend'],
                    'analysis': {
                        'description': 'CPU usage trending upward',
                        'trend_rate': recent_trend,
                        'current_usage': current_cpu
                    }
                })
        
        # Memory bottleneck prediction
        memory_history = list(metric_history.get('memory_usage', []))
        if len(memory_history) >= 5:
            recent_trend = statistics.mean(memory_history[-3:]) - statistics.mean(memory_history[-5:-2])
            
            if recent_trend > 3:  # Memory usage increasing
                current_memory = memory_history[-1] if memory_history else 0
                time_to_bottleneck = max(120, (85 - current_memory) / recent_trend * 60)
                
                predictions.append({
                    'prediction_id': f"memory_pred_{int(time.time())}",
                    'category': 'memory',
                    'probability': min(0.85, recent_trend / 8.0),
                    'time_to_bottleneck': time_to_bottleneck,
                    'early_symptoms': ['increasing_memory_trend'],
                    'analysis': {
                        'description': 'Memory usage trending upward',
                        'trend_rate': recent_trend,
                        'current_usage': current_memory
                    }
                })
        
        return predictions

# Example usage and testing
def test_bottleneck_detector():
    """Test the bottleneck detector functionality"""
    
    print("🧪 Testing Advanced Bottleneck Detector...")
    
    detector = AdvancedBottleneckDetector()
    
    # Test bottleneck detection
    print("🔍 Testing bottleneck detection...")
    
    # Simulate high CPU scenario
    high_cpu_metrics = {
        'cpu_usage': 95.0,
        'memory_usage': 60.0,
        'disk_usage': 70.0,
        'avg_execution_time': 15.0,
        'success_rate': 80.0
    }
    
    bottlenecks = detector.detect_bottlenecks(high_cpu_metrics)
    print(f"   Detected {len(bottlenecks)} bottlenecks with high CPU")
    
    for bottleneck in bottlenecks:
        print(f"   {bottleneck.category.value}: {bottleneck.severity} ({bottleneck.confidence:.2f})")
        print(f"     Symptoms: {', '.join(bottleneck.symptoms_observed)}")
        print(f"     Method: {bottleneck.detection_method.value}")
    
    # Test with memory pressure scenario
    print("\n🧠 Testing memory pressure detection...")
    
    high_memory_metrics = {
        'cpu_usage': 50.0,
        'memory_usage': 92.0,
        'disk_usage': 60.0,
        'avg_execution_time': 8.0,
        'success_rate': 85.0
    }
    
    bottlenecks = detector.detect_bottlenecks(high_memory_metrics)
    print(f"   Detected {len(bottlenecks)} bottlenecks with high memory")
    
    for bottleneck in bottlenecks:
        print(f"   {bottleneck.category.value}: {bottleneck.severity} ({bottleneck.confidence:.2f})")
        print(f"     Root cause: {bottleneck.root_cause_analysis.get('primary_factors', ['Unknown'])[0] if bottleneck.root_cause_analysis.get('primary_factors') else 'Unknown'}")
    
    print("\n✅ Bottleneck detector test completed!")

if __name__ == "__main__":
    test_bottleneck_detector()