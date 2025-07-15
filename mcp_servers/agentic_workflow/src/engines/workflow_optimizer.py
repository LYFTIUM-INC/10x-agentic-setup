"""
Workflow Learning Engine Implementation for Agentic Workflow MCP
Handles pattern extraction, learning, and self-improving workflows
"""

import asyncio
import time
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import sqlite3
import pickle
import logging

logger = logging.getLogger(__name__)

@dataclass
class WorkflowPattern:
    """Represents a discovered workflow pattern"""
    pattern_id: str
    pattern_type: str  # "sequence", "decision", "resource", "timing"
    pattern_data: Dict[str, Any]
    success_rate: float
    frequency: int
    first_seen: datetime
    last_seen: datetime
    optimization_potential: float
    confidence: float

@dataclass
class WorkflowExecution:
    """Represents a complete workflow execution"""
    execution_id: str
    workflow_type: str
    start_time: datetime
    end_time: datetime
    duration: float
    success: bool
    steps: List[Dict[str, Any]]
    resources_used: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    context: Dict[str, Any]

@dataclass
class OptimizationRecommendation:
    """Represents an optimization recommendation"""
    recommendation_id: str
    recommendation_type: str
    description: str
    expected_improvement: float
    confidence: float
    implementation_effort: str  # "low", "medium", "high"
    pattern_evidence: List[str]
    suggested_changes: Dict[str, Any]

class SequenceAnalyzer:
    """Analyzes sequences of actions in workflows"""
    
    def __init__(self):
        self.common_sequences = defaultdict(int)
        self.sequence_outcomes = defaultdict(list)
        self.min_sequence_length = 2
        self.max_sequence_length = 10
    
    async def find_common_sequences(self, workflow_trace: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find common sequences of actions in the workflow trace"""
        
        sequences = []
        actions = [step.get("action", step.get("type", "unknown")) for step in workflow_trace]
        
        # Extract sequences of different lengths
        for length in range(self.min_sequence_length, min(len(actions) + 1, self.max_sequence_length + 1)):
            for i in range(len(actions) - length + 1):
                sequence = tuple(actions[i:i+length])
                self.common_sequences[sequence] += 1
                
                # Track outcomes for this sequence
                if i + length < len(workflow_trace):
                    next_step = workflow_trace[i + length]
                    outcome = {
                        "success": next_step.get("success", True),
                        "confidence": next_step.get("confidence", 0.5),
                        "duration": next_step.get("duration", 0.0)
                    }
                    self.sequence_outcomes[sequence].append(outcome)
        
        # Convert to analysis results
        for sequence, frequency in self.common_sequences.items():
            if frequency >= 2:  # Only include patterns seen multiple times
                outcomes = self.sequence_outcomes[sequence]
                avg_success = np.mean([o["success"] for o in outcomes]) if outcomes else 0.0
                avg_confidence = np.mean([o["confidence"] for o in outcomes]) if outcomes else 0.0
                
                sequences.append({
                    "sequence": list(sequence),
                    "frequency": frequency,
                    "success_rate": avg_success,
                    "confidence": avg_confidence,
                    "pattern_strength": frequency * avg_success
                })
        
        # Sort by pattern strength
        sequences.sort(key=lambda x: x["pattern_strength"], reverse=True)
        return sequences[:10]  # Return top 10 patterns

class SimilarityCalculator:
    """Calculates similarity between workflows and patterns"""
    
    def __init__(self):
        self.weight_factors = {
            "action_similarity": 0.4,
            "timing_similarity": 0.2,
            "outcome_similarity": 0.2,
            "resource_similarity": 0.2
        }
    
    async def calculate_workflow_similarity(self, workflow1: Dict[str, Any], 
                                          workflow2: Dict[str, Any]) -> float:
        """Calculate similarity between two workflows"""
        
        similarities = {}
        
        # Action sequence similarity
        actions1 = [step.get("action", "") for step in workflow1.get("steps", [])]
        actions2 = [step.get("action", "") for step in workflow2.get("steps", [])]
        similarities["action_similarity"] = await self._sequence_similarity(actions1, actions2)
        
        # Timing similarity
        timing1 = workflow1.get("performance_metrics", {}).get("duration", 0)
        timing2 = workflow2.get("performance_metrics", {}).get("duration", 0)
        similarities["timing_similarity"] = await self._timing_similarity(timing1, timing2)
        
        # Outcome similarity
        outcome1 = workflow1.get("success", False)
        outcome2 = workflow2.get("success", False)
        similarities["outcome_similarity"] = 1.0 if outcome1 == outcome2 else 0.0
        
        # Resource similarity
        resources1 = workflow1.get("resources_used", {})
        resources2 = workflow2.get("resources_used", {})
        similarities["resource_similarity"] = await self._resource_similarity(resources1, resources2)
        
        # Calculate weighted average
        total_similarity = sum(
            similarities[key] * self.weight_factors[key] 
            for key in similarities
        )
        
        return total_similarity
    
    async def _sequence_similarity(self, seq1: List[str], seq2: List[str]) -> float:
        """Calculate similarity between two action sequences"""
        if not seq1 or not seq2:
            return 0.0
        
        # Use Jaccard similarity for simplicity
        set1 = set(seq1)
        set2 = set(seq2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    async def _timing_similarity(self, timing1: float, timing2: float) -> float:
        """Calculate similarity between execution timings"""
        if timing1 == 0 and timing2 == 0:
            return 1.0
        
        max_timing = max(timing1, timing2)
        min_timing = min(timing1, timing2)
        
        return min_timing / max_timing if max_timing > 0 else 0.0
    
    async def _resource_similarity(self, resources1: Dict[str, Any], 
                                 resources2: Dict[str, Any]) -> float:
        """Calculate similarity between resource usage patterns"""
        if not resources1 or not resources2:
            return 0.0
        
        # Compare common resource types
        common_resources = set(resources1.keys()).intersection(set(resources2.keys()))
        
        if not common_resources:
            return 0.0
        
        similarities = []
        for resource in common_resources:
            val1 = resources1[resource]
            val2 = resources2[resource]
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                if val1 == 0 and val2 == 0:
                    similarities.append(1.0)
                else:
                    max_val = max(val1, val2)
                    min_val = min(val1, val2)
                    similarities.append(min_val / max_val if max_val > 0 else 0.0)
            else:
                similarities.append(1.0 if val1 == val2 else 0.0)
        
        return np.mean(similarities) if similarities else 0.0

class WorkflowPatternMiner:
    """Mines patterns from workflow execution data"""
    
    def __init__(self):
        self.sequence_analyzer = SequenceAnalyzer()
        self.similarity_calculator = SimilarityCalculator()
        self.pattern_database = {}
        self.min_pattern_frequency = 3
        self.min_pattern_confidence = 0.7
    
    async def extract_patterns(self, workflow_trace: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract various types of patterns from workflow trace"""
        
        patterns = {
            "action_sequences": [],
            "decision_points": [],
            "resource_usage": {},
            "timing_patterns": {},
            "success_factors": []
        }
        
        # Extract action sequences
        sequences = await self.sequence_analyzer.find_common_sequences(workflow_trace)
        patterns["action_sequences"] = sequences
        
        # Identify decision points
        decision_points = await self._identify_decision_points(workflow_trace)
        patterns["decision_points"] = decision_points
        
        # Analyze resource usage patterns
        resource_patterns = await self._analyze_resource_patterns(workflow_trace)
        patterns["resource_usage"] = resource_patterns
        
        # Extract timing patterns
        timing_patterns = await self._analyze_timing_patterns(workflow_trace)
        patterns["timing_patterns"] = timing_patterns
        
        # Identify success factors
        success_factors = await self._identify_success_factors(workflow_trace)
        patterns["success_factors"] = success_factors
        
        return patterns
    
    async def _identify_decision_points(self, workflow_trace: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify critical decision points in the workflow"""
        
        decision_points = []
        
        for i, step in enumerate(workflow_trace):
            # Look for steps with multiple possible actions or branches
            if step.get("alternatives") or step.get("branches"):
                decision_point = {
                    "step_index": i,
                    "decision_type": step.get("type", "unknown"),
                    "alternatives": step.get("alternatives", []),
                    "chosen_action": step.get("action", ""),
                    "outcome": step.get("success", False),
                    "confidence": step.get("confidence", 0.5)
                }
                decision_points.append(decision_point)
            
            # Look for conditional logic indicators
            elif any(keyword in str(step).lower() for keyword in ["if", "choose", "decide", "select"]):
                decision_point = {
                    "step_index": i,
                    "decision_type": "conditional",
                    "context": step.get("context", {}),
                    "action": step.get("action", ""),
                    "outcome": step.get("success", False)
                }
                decision_points.append(decision_point)
        
        return decision_points
    
    async def _analyze_resource_patterns(self, workflow_trace: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze resource usage patterns"""
        
        resource_usage = defaultdict(list)
        
        for step in workflow_trace:
            resources = step.get("resources", {})
            for resource_type, usage in resources.items():
                resource_usage[resource_type].append(usage)
        
        patterns = {}
        for resource_type, usage_list in resource_usage.items():
            if usage_list:
                patterns[resource_type] = {
                    "average_usage": np.mean(usage_list),
                    "max_usage": np.max(usage_list),
                    "min_usage": np.min(usage_list),
                    "std_deviation": np.std(usage_list),
                    "usage_trend": "increasing" if usage_list[-1] > usage_list[0] else "decreasing" if len(usage_list) > 1 else "stable"
                }
        
        return patterns
    
    async def _analyze_timing_patterns(self, workflow_trace: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze timing patterns in the workflow"""
        
        step_durations = []
        step_types = defaultdict(list)
        
        for step in workflow_trace:
            duration = step.get("duration", 0.0)
            step_type = step.get("type", "unknown")
            
            step_durations.append(duration)
            step_types[step_type].append(duration)
        
        patterns = {
            "total_duration": sum(step_durations),
            "average_step_duration": np.mean(step_durations) if step_durations else 0.0,
            "slowest_step": max(step_durations) if step_durations else 0.0,
            "fastest_step": min(step_durations) if step_durations else 0.0,
            "step_type_performance": {}
        }
        
        # Analyze performance by step type
        for step_type, durations in step_types.items():
            patterns["step_type_performance"][step_type] = {
                "average_duration": np.mean(durations),
                "max_duration": np.max(durations),
                "min_duration": np.min(durations),
                "frequency": len(durations)
            }
        
        return patterns
    
    async def _identify_success_factors(self, workflow_trace: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify factors that contribute to workflow success"""
        
        success_factors = []
        successful_steps = [step for step in workflow_trace if step.get("success", False)]
        failed_steps = [step for step in workflow_trace if not step.get("success", True)]
        
        if successful_steps:
            # Analyze common characteristics of successful steps
            common_actions = defaultdict(int)
            common_resources = defaultdict(list)
            
            for step in successful_steps:
                action = step.get("action", "")
                if action:
                    common_actions[action] += 1
                
                resources = step.get("resources", {})
                for resource_type, usage in resources.items():
                    common_resources[resource_type].append(usage)
            
            # Identify most successful actions
            total_successful = len(successful_steps)
            for action, count in common_actions.items():
                if count >= 2:  # Appears multiple times
                    success_factor = {
                        "type": "action_pattern",
                        "factor": action,
                        "frequency": count,
                        "success_rate": count / total_successful,
                        "confidence": min(count / 10.0, 1.0)  # Confidence based on frequency
                    }
                    success_factors.append(success_factor)
            
            # Analyze resource patterns in successful executions
            for resource_type, usage_list in common_resources.items():
                if len(usage_list) >= 2:
                    avg_usage = np.mean(usage_list)
                    success_factor = {
                        "type": "resource_pattern",
                        "factor": f"{resource_type}_optimal_usage",
                        "optimal_value": avg_usage,
                        "confidence": min(len(usage_list) / 10.0, 1.0)
                    }
                    success_factors.append(success_factor)
        
        return success_factors

class WorkflowSuccessPredictor:
    """Predicts workflow success based on historical patterns"""
    
    def __init__(self):
        self.prediction_model = {}
        self.feature_weights = {}
        self.training_data = []
        self.model_accuracy = 0.0
    
    async def predict_success(self, workflow_features: Dict[str, Any]) -> Tuple[float, float]:
        """Predict success probability and confidence for a workflow"""
        
        if not self.prediction_model:
            return 0.5, 0.1  # Default prediction if no model trained
        
        # Extract features
        features = await self._extract_prediction_features(workflow_features)
        
        # Calculate prediction score
        prediction_score = 0.0
        total_weight = 0.0
        
        for feature_name, feature_value in features.items():
            if feature_name in self.feature_weights:
                weight = self.feature_weights[feature_name]
                prediction_score += feature_value * weight
                total_weight += abs(weight)
        
        # Normalize prediction
        if total_weight > 0:
            prediction = max(0.0, min(1.0, prediction_score / total_weight))
        else:
            prediction = 0.5
        
        # Confidence based on model accuracy and feature coverage
        feature_coverage = len([f for f in features if f in self.feature_weights]) / max(len(features), 1)
        confidence = self.model_accuracy * feature_coverage
        
        return prediction, confidence
    
    async def update(self, patterns: Dict[str, Any], success_metrics: Dict[str, Any]) -> None:
        """Update the prediction model with new training data"""
        
        # Extract features from patterns
        features = await self._extract_prediction_features(patterns)
        success_score = success_metrics.get("overall_success", 0.0)
        
        # Add to training data
        training_example = {
            "features": features,
            "success": success_score,
            "timestamp": datetime.now()
        }
        self.training_data.append(training_example)
        
        # Retrain model if we have enough data
        if len(self.training_data) >= 10:
            await self._retrain_model()
    
    async def _extract_prediction_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract numerical features for prediction"""
        
        features = {}
        
        # Action sequence features
        action_sequences = data.get("action_sequences", [])
        if action_sequences:
            features["avg_sequence_strength"] = np.mean([seq.get("pattern_strength", 0) for seq in action_sequences])
            features["max_sequence_frequency"] = max([seq.get("frequency", 0) for seq in action_sequences])
            features["sequence_diversity"] = len(action_sequences)
        
        # Decision point features
        decision_points = data.get("decision_points", [])
        features["decision_count"] = len(decision_points)
        if decision_points:
            features["avg_decision_confidence"] = np.mean([dp.get("confidence", 0) for dp in decision_points])
        
        # Resource usage features
        resource_usage = data.get("resource_usage", {})
        for resource_type, pattern in resource_usage.items():
            if isinstance(pattern, dict):
                features[f"{resource_type}_avg_usage"] = pattern.get("average_usage", 0)
                features[f"{resource_type}_efficiency"] = pattern.get("average_usage", 0) / max(pattern.get("max_usage", 1), 1)
        
        # Timing features
        timing_patterns = data.get("timing_patterns", {})
        if timing_patterns:
            features["total_duration"] = timing_patterns.get("total_duration", 0)
            features["avg_step_duration"] = timing_patterns.get("average_step_duration", 0)
            features["duration_variance"] = timing_patterns.get("slowest_step", 0) - timing_patterns.get("fastest_step", 0)
        
        # Success factor features
        success_factors = data.get("success_factors", [])
        features["success_factor_count"] = len(success_factors)
        if success_factors:
            features["avg_success_confidence"] = np.mean([sf.get("confidence", 0) for sf in success_factors])
        
        return features
    
    async def _retrain_model(self) -> None:
        """Retrain the prediction model with accumulated data"""
        
        if len(self.training_data) < 5:
            return
        
        # Simple linear model training
        all_features = set()
        for example in self.training_data:
            all_features.update(example["features"].keys())
        
        # Calculate feature weights based on correlation with success
        new_weights = {}
        
        for feature_name in all_features:
            feature_values = []
            success_values = []
            
            for example in self.training_data:
                if feature_name in example["features"]:
                    feature_values.append(example["features"][feature_name])
                    success_values.append(example["success"])
            
            if len(feature_values) >= 3:
                # Calculate correlation
                correlation = np.corrcoef(feature_values, success_values)[0, 1]
                if not np.isnan(correlation):
                    new_weights[feature_name] = correlation
        
        self.feature_weights = new_weights
        
        # Calculate model accuracy using cross-validation
        await self._calculate_model_accuracy()
        
        logger.info(f"Model retrained with {len(self.training_data)} examples. Accuracy: {self.model_accuracy:.3f}")
    
    async def _calculate_model_accuracy(self) -> None:
        """Calculate model accuracy using cross-validation"""
        
        if len(self.training_data) < 5:
            self.model_accuracy = 0.5
            return
        
        correct_predictions = 0
        total_predictions = 0
        
        # Simple leave-one-out validation
        for i, test_example in enumerate(self.training_data):
            # Use all other examples for prediction
            test_features = test_example["features"]
            actual_success = test_example["success"]
            
            predicted_success, _ = await self.predict_success(test_features)
            
            # Convert to binary prediction
            predicted_binary = 1.0 if predicted_success > 0.5 else 0.0
            actual_binary = 1.0 if actual_success > 0.5 else 0.0
            
            if predicted_binary == actual_binary:
                correct_predictions += 1
            total_predictions += 1
        
        self.model_accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.5

class WorkflowOptimizer:
    """Generates optimizations for workflows based on learned patterns"""
    
    def __init__(self):
        self.optimization_rules = self._initialize_optimization_rules()
        self.pattern_database = {}
        self.optimization_history = []
    
    def _initialize_optimization_rules(self) -> Dict[str, Any]:
        """Initialize optimization rules and strategies"""
        
        return {
            "sequence_optimization": {
                "remove_redundant_steps": {
                    "description": "Remove duplicate or unnecessary steps",
                    "trigger": "duplicate_sequences",
                    "expected_improvement": 0.2
                },
                "reorder_steps": {
                    "description": "Reorder steps for better efficiency",
                    "trigger": "suboptimal_ordering",
                    "expected_improvement": 0.15
                },
                "parallel_execution": {
                    "description": "Execute independent steps in parallel",
                    "trigger": "independent_steps",
                    "expected_improvement": 0.3
                }
            },
            "resource_optimization": {
                "resource_pooling": {
                    "description": "Pool similar resources for better utilization",
                    "trigger": "underutilized_resources",
                    "expected_improvement": 0.25
                },
                "resource_scaling": {
                    "description": "Scale resources based on demand patterns",
                    "trigger": "resource_bottlenecks",
                    "expected_improvement": 0.35
                }
            },
            "timing_optimization": {
                "cache_results": {
                    "description": "Cache frequently used results",
                    "trigger": "repeated_computations",
                    "expected_improvement": 0.4
                },
                "lazy_loading": {
                    "description": "Load resources only when needed",
                    "trigger": "unused_resources",
                    "expected_improvement": 0.2
                }
            }
        }
    
    async def generate_optimizations(self, patterns: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on patterns"""
        
        recommendations = []
        
        # Analyze each pattern type for optimization opportunities
        for pattern_type, pattern_data in patterns.items():
            if pattern_type == "action_sequences":
                sequence_optimizations = await self._optimize_sequences(pattern_data)
                recommendations.extend(sequence_optimizations)
            
            elif pattern_type == "resource_usage":
                resource_optimizations = await self._optimize_resources(pattern_data)
                recommendations.extend(resource_optimizations)
            
            elif pattern_type == "timing_patterns":
                timing_optimizations = await self._optimize_timing(pattern_data)
                recommendations.extend(timing_optimizations)
            
            elif pattern_type == "decision_points":
                decision_optimizations = await self._optimize_decisions(pattern_data)
                recommendations.extend(decision_optimizations)
        
        # Sort recommendations by expected improvement
        recommendations.sort(key=lambda x: x.expected_improvement, reverse=True)
        
        return recommendations[:10]  # Return top 10 recommendations
    
    async def _optimize_sequences(self, sequences: List[Dict[str, Any]]) -> List[OptimizationRecommendation]:
        """Generate sequence-based optimizations"""
        
        recommendations = []
        
        for sequence_data in sequences:
            sequence = sequence_data.get("sequence", [])
            frequency = sequence_data.get("frequency", 0)
            success_rate = sequence_data.get("success_rate", 0.0)
            
            # Check for optimization opportunities
            if len(sequence) > 3 and success_rate > 0.8:
                # Look for redundancy
                if len(set(sequence)) < len(sequence):
                    recommendation = OptimizationRecommendation(
                        recommendation_id=f"seq_opt_{hash(tuple(sequence))}",
                        recommendation_type="sequence_optimization",
                        description=f"Remove redundant steps in sequence: {' -> '.join(sequence)}",
                        expected_improvement=0.2,
                        confidence=0.8,
                        implementation_effort="low",
                        pattern_evidence=[f"Sequence appears {frequency} times with {success_rate:.1%} success"],
                        suggested_changes={
                            "action": "remove_redundancy",
                            "sequence": sequence,
                            "optimized_sequence": list(dict.fromkeys(sequence))  # Remove duplicates while preserving order
                        }
                    )
                    recommendations.append(recommendation)
                
                # Look for parallelization opportunities
                if self._can_parallelize_sequence(sequence):
                    recommendation = OptimizationRecommendation(
                        recommendation_id=f"par_opt_{hash(tuple(sequence))}",
                        recommendation_type="parallelization",
                        description=f"Parallelize independent steps in: {' -> '.join(sequence)}",
                        expected_improvement=0.3,
                        confidence=0.7,
                        implementation_effort="medium",
                        pattern_evidence=[f"Sequence contains parallelizable steps"],
                        suggested_changes={
                            "action": "parallelize",
                            "sequence": sequence,
                            "parallel_groups": self._identify_parallel_groups(sequence)
                        }
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    def _can_parallelize_sequence(self, sequence: List[str]) -> bool:
        """Check if a sequence can be parallelized"""
        # Simple heuristic: if sequence contains independent operations
        independent_keywords = ["research", "analyze", "validate", "check"]
        
        independent_steps = [step for step in sequence if any(keyword in step.lower() for keyword in independent_keywords)]
        return len(independent_steps) >= 2
    
    def _identify_parallel_groups(self, sequence: List[str]) -> List[List[str]]:
        """Identify groups of steps that can be executed in parallel"""
        # Simple grouping based on operation types
        research_steps = [step for step in sequence if "research" in step.lower()]
        analysis_steps = [step for step in sequence if "analyze" in step.lower()]
        validation_steps = [step for step in sequence if any(keyword in step.lower() for keyword in ["validate", "test", "check"])]
        
        groups = []
        if len(research_steps) > 1:
            groups.append(research_steps)
        if len(analysis_steps) > 1:
            groups.append(analysis_steps)
        if len(validation_steps) > 1:
            groups.append(validation_steps)
        
        return groups
    
    async def _optimize_resources(self, resource_patterns: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate resource-based optimizations"""
        
        recommendations = []
        
        for resource_type, pattern in resource_patterns.items():
            if isinstance(pattern, dict):
                avg_usage = pattern.get("average_usage", 0)
                max_usage = pattern.get("max_usage", 0)
                std_dev = pattern.get("std_deviation", 0)
                
                # Check for underutilization
                utilization_ratio = avg_usage / max_usage if max_usage > 0 else 0
                
                if utilization_ratio < 0.5:  # Less than 50% utilization
                    recommendation = OptimizationRecommendation(
                        recommendation_id=f"res_opt_{resource_type}",
                        recommendation_type="resource_optimization",
                        description=f"Optimize {resource_type} allocation (currently {utilization_ratio:.1%} utilized)",
                        expected_improvement=0.25,
                        confidence=0.8,
                        implementation_effort="medium",
                        pattern_evidence=[f"Average utilization: {utilization_ratio:.1%}"],
                        suggested_changes={
                            "action": "reduce_allocation",
                            "resource_type": resource_type,
                            "current_max": max_usage,
                            "suggested_max": avg_usage * 1.2  # 20% buffer above average
                        }
                    )
                    recommendations.append(recommendation)
                
                # Check for high variability (potential for better scheduling)
                if std_dev > avg_usage * 0.5:  # High variability
                    recommendation = OptimizationRecommendation(
                        recommendation_id=f"sched_opt_{resource_type}",
                        recommendation_type="scheduling_optimization",
                        description=f"Implement better scheduling for {resource_type} to reduce variability",
                        expected_improvement=0.15,
                        confidence=0.7,
                        implementation_effort="high",
                        pattern_evidence=[f"High variability: σ={std_dev:.2f}, μ={avg_usage:.2f}"],
                        suggested_changes={
                            "action": "improve_scheduling",
                            "resource_type": resource_type,
                            "scheduling_strategy": "load_balancing"
                        }
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    async def _optimize_timing(self, timing_patterns: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate timing-based optimizations"""
        
        recommendations = []
        
        total_duration = timing_patterns.get("total_duration", 0)
        avg_step_duration = timing_patterns.get("average_step_duration", 0)
        step_performance = timing_patterns.get("step_type_performance", {})
        
        # Identify slow step types
        for step_type, performance in step_performance.items():
            avg_duration = performance.get("average_duration", 0)
            frequency = performance.get("frequency", 0)
            
            # If this step type takes more than 50% of average step time and appears frequently
            if avg_duration > avg_step_duration * 1.5 and frequency >= 3:
                recommendation = OptimizationRecommendation(
                    recommendation_id=f"timing_opt_{step_type}",
                    recommendation_type="performance_optimization",
                    description=f"Optimize {step_type} steps (avg: {avg_duration:.2f}s, appears {frequency} times)",
                    expected_improvement=0.3,
                    confidence=0.8,
                    implementation_effort="medium",
                    pattern_evidence=[f"Step type consistently slow: {avg_duration:.2f}s vs {avg_step_duration:.2f}s average"],
                    suggested_changes={
                        "action": "optimize_step_type",
                        "step_type": step_type,
                        "current_avg_duration": avg_duration,
                        "target_duration": avg_step_duration,
                        "optimization_strategies": ["caching", "algorithmic_improvement", "resource_scaling"]
                    }
                )
                recommendations.append(recommendation)
        
        # Check for caching opportunities
        if total_duration > 60:  # For workflows longer than 1 minute
            recommendation = OptimizationRecommendation(
                recommendation_id=f"cache_opt_{hash(str(timing_patterns))}",
                recommendation_type="caching_optimization",
                description="Implement result caching for long-running workflow",
                expected_improvement=0.4,
                confidence=0.6,
                implementation_effort="medium",
                pattern_evidence=[f"Total workflow duration: {total_duration:.2f}s"],
                suggested_changes={
                    "action": "implement_caching",
                    "cache_strategy": "result_memoization",
                    "cache_key_strategy": "input_hash"
                }
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    async def _optimize_decisions(self, decision_points: List[Dict[str, Any]]) -> List[OptimizationRecommendation]:
        """Generate decision-based optimizations"""
        
        recommendations = []
        
        # Analyze decision patterns
        low_confidence_decisions = [dp for dp in decision_points if dp.get("confidence", 1.0) < 0.7]
        
        if low_confidence_decisions:
            recommendation = OptimizationRecommendation(
                recommendation_id=f"decision_opt_{len(low_confidence_decisions)}",
                recommendation_type="decision_optimization",
                description=f"Improve {len(low_confidence_decisions)} low-confidence decision points",
                expected_improvement=0.2,
                confidence=0.7,
                implementation_effort="high",
                pattern_evidence=[f"{len(low_confidence_decisions)} decisions with confidence < 70%"],
                suggested_changes={
                    "action": "improve_decision_logic",
                    "low_confidence_decisions": low_confidence_decisions,
                    "strategies": ["gather_more_context", "implement_fallback_logic", "add_validation_steps"]
                }
            )
            recommendations.append(recommendation)
        
        return recommendations

class SelfImprovingWorkflow:
    """A workflow that improves itself based on execution history"""
    
    def __init__(self, base_workflow: Dict[str, Any]):
        self.workflow = base_workflow
        self.performance_history = deque(maxlen=50)  # Keep last 50 executions
        self.optimization_cycles = 0
        self.success_threshold = 0.85
        self.learning_engine = WorkflowLearningEngine()
        self.last_optimization = None
    
    async def execute_and_improve(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow and potentially improve it based on results"""
        
        execution_start = time.time()
        
        # Execute current workflow
        result = await self._execute_workflow(task)
        
        execution_time = time.time() - execution_start
        
        # Evaluate performance
        performance = await self._evaluate_performance(result, execution_time, task)
        self.performance_history.append(performance)
        
        # Check for improvement opportunity
        if await self._should_optimize():
            logger.info("Triggering workflow optimization")
            
            # Generate optimizations using learning engine
            optimizations = await self._generate_optimizations()
            
            if optimizations:
                # Apply optimizations
                self.workflow = await self._apply_optimizations(optimizations)
                self.optimization_cycles += 1
                self.last_optimization = datetime.now()
                
                # Log improvement
                await self._log_improvement(optimizations, performance)
        
        # Add performance data to result
        result["performance_data"] = performance
        result["optimization_cycle"] = self.optimization_cycles
        
        return result
    
    async def _execute_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the current workflow implementation"""
        
        # This would integrate with the actual workflow execution engine
        # For now, simulate execution based on workflow configuration
        
        steps = self.workflow.get("steps", [])
        results = {"steps_executed": [], "overall_success": True}
        
        for i, step in enumerate(steps):
            step_start = time.time()
            
            # Simulate step execution
            step_result = await self._execute_step(step, task)
            step_duration = time.time() - step_start
            
            step_result["duration"] = step_duration
            step_result["step_index"] = i
            
            results["steps_executed"].append(step_result)
            
            if not step_result.get("success", True):
                results["overall_success"] = False
                break
        
        return results
    
    async def _execute_step(self, step: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        
        # Simulate step execution
        step_type = step.get("type", "generic")
        complexity = step.get("complexity", "medium")
        
        # Simulate processing time based on complexity
        complexity_delays = {"low": 0.1, "medium": 0.3, "high": 0.8}
        await asyncio.sleep(complexity_delays.get(complexity, 0.3))
        
        # Simulate success/failure based on step configuration
        success_rate = step.get("success_rate", 0.9)
        success = np.random.random() < success_rate
        
        return {
            "type": step_type,
            "action": step.get("action", f"execute_{step_type}"),
            "success": success,
            "confidence": success_rate if success else 0.3,
            "resources": step.get("resources", {}),
            "complexity": complexity
        }
    
    async def _evaluate_performance(self, result: Dict[str, Any], execution_time: float, task: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the performance of the workflow execution"""
        
        steps_executed = result.get("steps_executed", [])
        overall_success = result.get("overall_success", False)
        
        # Calculate metrics
        total_steps = len(steps_executed)
        successful_steps = len([step for step in steps_executed if step.get("success", False)])
        avg_confidence = np.mean([step.get("confidence", 0) for step in steps_executed]) if steps_executed else 0
        
        performance = {
            "timestamp": datetime.now(),
            "execution_time": execution_time,
            "overall_success": overall_success,
            "success_rate": successful_steps / total_steps if total_steps > 0 else 0,
            "average_confidence": avg_confidence,
            "total_steps": total_steps,
            "successful_steps": successful_steps,
            "task_complexity": task.get("complexity", "medium"),
            "workflow_version": self.optimization_cycles
        }
        
        return performance
    
    async def _should_optimize(self) -> bool:
        """Determine if the workflow should be optimized"""
        
        if len(self.performance_history) < 5:
            return False
        
        # Don't optimize too frequently
        if self.last_optimization:
            time_since_last = datetime.now() - self.last_optimization
            if time_since_last < timedelta(hours=1):
                return False
        
        # Check recent performance trend
        recent_performances = list(self.performance_history)[-5:]
        recent_avg_success = np.mean([p["success_rate"] for p in recent_performances])
        recent_avg_confidence = np.mean([p["average_confidence"] for p in recent_performances])
        
        # Optimize if performance is below threshold
        if recent_avg_success < self.success_threshold or recent_avg_confidence < 0.7:
            return True
        
        # Optimize if performance is declining
        if len(self.performance_history) >= 10:
            older_performances = list(self.performance_history)[-10:-5]
            older_avg_success = np.mean([p["success_rate"] for p in older_performances])
            
            if recent_avg_success < older_avg_success - 0.05:  # 5% decline
                return True
        
        return False
    
    async def _generate_optimizations(self) -> List[OptimizationRecommendation]:
        """Generate optimizations based on performance history"""
        
        # Extract patterns from performance history
        execution_data = []
        for performance in self.performance_history:
            # Convert performance data to workflow trace format
            execution_trace = {
                "execution_id": str(uuid.uuid4()),
                "success": performance["overall_success"],
                "duration": performance["execution_time"],
                "steps": performance.get("steps_executed", []),
                "performance_metrics": performance
            }
            execution_data.append(execution_trace)
        
        # Use learning engine to extract patterns and generate optimizations
        patterns = {}
        for execution in execution_data:
            exec_patterns = await self.learning_engine.pattern_miner.extract_patterns(execution.get("steps", []))
            
            # Merge patterns
            for pattern_type, pattern_data in exec_patterns.items():
                if pattern_type not in patterns:
                    patterns[pattern_type] = []
                if isinstance(pattern_data, list):
                    patterns[pattern_type].extend(pattern_data)
                else:
                    patterns[pattern_type].append(pattern_data)
        
        # Generate optimizations
        optimizations = await self.learning_engine.optimizer.generate_optimizations(patterns)
        
        return optimizations
    
    async def _apply_optimizations(self, optimizations: List[OptimizationRecommendation]) -> Dict[str, Any]:
        """Apply optimizations to the workflow"""
        
        optimized_workflow = self.workflow.copy()
        
        for optimization in optimizations:
            if optimization.confidence >= 0.6:  # Only apply high-confidence optimizations
                try:
                    optimized_workflow = await self._apply_single_optimization(optimized_workflow, optimization)
                    logger.info(f"Applied optimization: {optimization.description}")
                except Exception as e:
                    logger.error(f"Failed to apply optimization {optimization.recommendation_id}: {str(e)}")
        
        return optimized_workflow
    
    async def _apply_single_optimization(self, workflow: Dict[str, Any], optimization: OptimizationRecommendation) -> Dict[str, Any]:
        """Apply a single optimization to the workflow"""
        
        optimized = workflow.copy()
        changes = optimization.suggested_changes
        
        if optimization.recommendation_type == "sequence_optimization":
            # Apply sequence optimizations
            if changes.get("action") == "remove_redundancy":
                optimized_sequence = changes.get("optimized_sequence", [])
                # Update workflow steps to remove redundancy
                optimized["steps"] = self._apply_sequence_changes(optimized.get("steps", []), optimized_sequence)
        
        elif optimization.recommendation_type == "parallelization":
            # Apply parallelization optimizations
            parallel_groups = changes.get("parallel_groups", [])
            optimized["parallel_execution"] = {
                "enabled": True,
                "groups": parallel_groups
            }
        
        elif optimization.recommendation_type == "resource_optimization":
            # Apply resource optimizations
            if changes.get("action") == "reduce_allocation":
                resource_type = changes.get("resource_type")
                suggested_max = changes.get("suggested_max")
                
                if "resource_limits" not in optimized:
                    optimized["resource_limits"] = {}
                optimized["resource_limits"][resource_type] = suggested_max
        
        elif optimization.recommendation_type == "caching_optimization":
            # Apply caching optimizations
            optimized["caching"] = {
                "enabled": True,
                "strategy": changes.get("cache_strategy", "result_memoization")
            }
        
        return optimized
    
    def _apply_sequence_changes(self, steps: List[Dict[str, Any]], optimized_sequence: List[str]) -> List[Dict[str, Any]]:
        """Apply sequence optimizations to workflow steps"""
        
        # Simple implementation: remove duplicate actions
        seen_actions = set()
        optimized_steps = []
        
        for step in steps:
            action = step.get("action", "")
            if action not in seen_actions:
                optimized_steps.append(step)
                seen_actions.add(action)
        
        return optimized_steps
    
    async def _log_improvement(self, optimizations: List[OptimizationRecommendation], performance: Dict[str, Any]) -> None:
        """Log the improvement applied to the workflow"""
        
        improvement_log = {
            "timestamp": datetime.now(),
            "optimization_cycle": self.optimization_cycles,
            "applied_optimizations": [
                {
                    "type": opt.recommendation_type,
                    "description": opt.description,
                    "expected_improvement": opt.expected_improvement,
                    "confidence": opt.confidence
                }
                for opt in optimizations
            ],
            "performance_before": performance,
            "total_expected_improvement": sum(opt.expected_improvement for opt in optimizations)
        }
        
        logger.info(f"Workflow optimization cycle {self.optimization_cycles} completed. "
                   f"Applied {len(optimizations)} optimizations with total expected improvement: "
                   f"{improvement_log['total_expected_improvement']:.1%}")

class WorkflowKnowledgeBase:
    """Stores and retrieves workflow patterns and optimizations"""
    
    def __init__(self, db_path: str = "workflow_knowledge.db"):
        self.db_path = db_path
        self.patterns = {}
        self.successful_patterns = {}
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize the knowledge base database"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables for storing patterns
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflow_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_type TEXT,
                    pattern_data BLOB,
                    success_rate REAL,
                    frequency INTEGER,
                    first_seen TEXT,
                    last_seen TEXT,
                    confidence REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS optimization_history (
                    optimization_id TEXT PRIMARY KEY,
                    workflow_id TEXT,
                    optimization_type TEXT,
                    optimization_data BLOB,
                    expected_improvement REAL,
                    actual_improvement REAL,
                    applied_at TEXT,
                    success BOOLEAN
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Knowledge base initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base: {str(e)}")
    
    async def store_successful_pattern(self, pattern: WorkflowPattern) -> None:
        """Store a successful workflow pattern"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Serialize pattern data
            pattern_blob = pickle.dumps(pattern.pattern_data)
            
            cursor.execute('''
                INSERT OR REPLACE INTO workflow_patterns 
                (pattern_id, pattern_type, pattern_data, success_rate, frequency, 
                 first_seen, last_seen, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern.pattern_id,
                pattern.pattern_type,
                pattern_blob,
                pattern.success_rate,
                pattern.frequency,
                pattern.first_seen.isoformat(),
                pattern.last_seen.isoformat(),
                pattern.confidence
            ))
            
            conn.commit()
            conn.close()
            
            # Also store in memory for quick access
            self.successful_patterns[pattern.pattern_id] = pattern
            
            logger.debug(f"Stored successful pattern: {pattern.pattern_id}")
            
        except Exception as e:
            logger.error(f"Failed to store pattern {pattern.pattern_id}: {str(e)}")
    
    async def retrieve_similar_patterns(self, query_pattern: Dict[str, Any], 
                                      similarity_threshold: float = 0.7) -> List[WorkflowPattern]:
        """Retrieve patterns similar to the query pattern"""
        
        similar_patterns = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM workflow_patterns')
            rows = cursor.fetchall()
            
            for row in rows:
                pattern_id, pattern_type, pattern_blob, success_rate, frequency, first_seen, last_seen, confidence = row
                
                # Deserialize pattern data
                pattern_data = pickle.loads(pattern_blob)
                
                # Calculate similarity (simplified)
                similarity = await self._calculate_pattern_similarity(query_pattern, pattern_data)
                
                if similarity >= similarity_threshold:
                    pattern = WorkflowPattern(
                        pattern_id=pattern_id,
                        pattern_type=pattern_type,
                        pattern_data=pattern_data,
                        success_rate=success_rate,
                        frequency=frequency,
                        first_seen=datetime.fromisoformat(first_seen),
                        last_seen=datetime.fromisoformat(last_seen),
                        optimization_potential=similarity * success_rate,
                        confidence=confidence
                    )
                    similar_patterns.append(pattern)
            
            conn.close()
            
            # Sort by optimization potential
            similar_patterns.sort(key=lambda p: p.optimization_potential, reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to retrieve similar patterns: {str(e)}")
        
        return similar_patterns
    
    async def _calculate_pattern_similarity(self, pattern1: Dict[str, Any], pattern2: Dict[str, Any]) -> float:
        """Calculate similarity between two patterns"""
        
        # Simple similarity calculation based on common keys and values
        if not pattern1 or not pattern2:
            return 0.0
        
        common_keys = set(pattern1.keys()).intersection(set(pattern2.keys()))
        if not common_keys:
            return 0.0
        
        similarities = []
        for key in common_keys:
            val1 = pattern1[key]
            val2 = pattern2[key]
            
            if val1 == val2:
                similarities.append(1.0)
            elif isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                if val1 == 0 and val2 == 0:
                    similarities.append(1.0)
                else:
                    max_val = max(abs(val1), abs(val2))
                    min_val = min(abs(val1), abs(val2))
                    similarities.append(min_val / max_val if max_val > 0 else 0.0)
            else:
                similarities.append(0.5)  # Partial similarity for different types
        
        return np.mean(similarities) if similarities else 0.0

class WorkflowLearningEngine:
    """
    Main workflow learning engine that coordinates pattern mining, prediction, and optimization
    """
    
    def __init__(self):
        self.pattern_miner = WorkflowPatternMiner()
        self.success_predictor = WorkflowSuccessPredictor()
        self.optimizer = WorkflowOptimizer()
        self.knowledge_base = WorkflowKnowledgeBase()
        self.execution_history = deque(maxlen=1000)  # Keep last 1000 executions
    
    async def learn_from_execution(self, workflow_trace: List[Dict[str, Any]], 
                                 outcome: Dict[str, Any]) -> Dict[str, Any]:
        """Learn from a workflow execution and generate insights"""
        
        logger.info("Learning from workflow execution")
        
        # Record execution
        execution = WorkflowExecution(
            execution_id=str(uuid.uuid4()),
            workflow_type=outcome.get("workflow_type", "unknown"),
            start_time=datetime.now() - timedelta(seconds=outcome.get("duration", 0)),
            end_time=datetime.now(),
            duration=outcome.get("duration", 0),
            success=outcome.get("success", False),
            steps=workflow_trace,
            resources_used=outcome.get("resources", {}),
            performance_metrics=outcome.get("metrics", {}),
            context=outcome.get("context", {})
        )
        
        self.execution_history.append(execution)
        
        # Extract patterns from execution
        patterns = await self.pattern_miner.extract_patterns(workflow_trace)
        
        # Evaluate success metrics
        success_metrics = await self._evaluate_success_metrics(outcome)
        
        # Update prediction model
        await self.success_predictor.update(patterns, success_metrics)
        
        # Store successful patterns
        if success_metrics["overall_success"] > 0.8:
            await self._store_successful_patterns(patterns, success_metrics)
        
        # Generate optimizations
        optimizations = await self.optimizer.generate_optimizations(patterns)
        
        # Generate learning insights
        insights = await self._generate_learning_insights(patterns, success_metrics, optimizations)
        
        learning_result = {
            "patterns_extracted": patterns,
            "success_metrics": success_metrics,
            "optimizations_generated": len(optimizations),
            "top_optimizations": optimizations[:3],  # Top 3 optimizations
            "insights": insights,
            "learning_confidence": await self._calculate_learning_confidence(patterns, success_metrics)
        }
        
        logger.info(f"Learning completed. Extracted {len(patterns)} pattern types, "
                   f"generated {len(optimizations)} optimizations")
        
        return learning_result
    
    async def _evaluate_success_metrics(self, outcome: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate comprehensive success metrics from workflow outcome"""
        
        success_metrics = {
            "overall_success": 0.0,
            "performance_score": 0.0,
            "efficiency_score": 0.0,
            "quality_score": 0.0,
            "reliability_score": 0.0
        }
        
        # Overall success
        success_metrics["overall_success"] = 1.0 if outcome.get("success", False) else 0.0
        
        # Performance score (based on execution time)
        expected_duration = outcome.get("expected_duration", 60.0)
        actual_duration = outcome.get("duration", 0.0)
        
        if actual_duration > 0:
            performance_ratio = expected_duration / actual_duration
            success_metrics["performance_score"] = min(1.0, max(0.0, performance_ratio))
        
        # Efficiency score (based on resource utilization)
        resources = outcome.get("resources", {})
        if resources:
            utilization_rates = []
            for resource_type, usage in resources.items():
                if isinstance(usage, dict) and "utilization" in usage:
                    utilization_rates.append(usage["utilization"])
            
            if utilization_rates:
                success_metrics["efficiency_score"] = np.mean(utilization_rates)
        
        # Quality score (based on output quality metrics)
        quality_metrics = outcome.get("quality", {})
        if quality_metrics:
            quality_scores = [v for v in quality_metrics.values() if isinstance(v, (int, float))]
            if quality_scores:
                success_metrics["quality_score"] = np.mean(quality_scores)
        
        # Reliability score (based on error rate and consistency)
        error_count = outcome.get("error_count", 0)
        total_steps = outcome.get("total_steps", 1)
        success_metrics["reliability_score"] = 1.0 - (error_count / total_steps)
        
        return success_metrics
    
    async def _store_successful_patterns(self, patterns: Dict[str, Any], 
                                       success_metrics: Dict[str, Any]) -> None:
        """Store patterns that led to successful outcomes"""
        
        overall_success = success_metrics["overall_success"]
        
        for pattern_type, pattern_data in patterns.items():
            if isinstance(pattern_data, list):
                for i, pattern in enumerate(pattern_data):
                    if isinstance(pattern, dict) and pattern.get("success_rate", 0) > 0.7:
                        workflow_pattern = WorkflowPattern(
                            pattern_id=f"{pattern_type}_{i}_{int(time.time())}",
                            pattern_type=pattern_type,
                            pattern_data=pattern,
                            success_rate=pattern.get("success_rate", overall_success),
                            frequency=pattern.get("frequency", 1),
                            first_seen=datetime.now(),
                            last_seen=datetime.now(),
                            optimization_potential=pattern.get("success_rate", 0) * pattern.get("frequency", 1),
                            confidence=pattern.get("confidence", 0.5)
                        )
                        
                        await self.knowledge_base.store_successful_pattern(workflow_pattern)
    
    async def _generate_learning_insights(self, patterns: Dict[str, Any], 
                                        success_metrics: Dict[str, Any],
                                        optimizations: List[OptimizationRecommendation]) -> List[str]:
        """Generate insights from the learning process"""
        
        insights = []
        
        # Pattern insights
        pattern_count = sum(len(p) if isinstance(p, list) else 1 for p in patterns.values())
        insights.append(f"Extracted {pattern_count} workflow patterns")
        
        # Success insights
        overall_success = success_metrics["overall_success"]
        if overall_success > 0.8:
            insights.append("High success rate indicates stable workflow pattern")
        elif overall_success > 0.5:
            insights.append("Moderate success rate suggests optimization opportunities")
        else:
            insights.append("Low success rate indicates need for significant improvements")
        
        # Performance insights
        performance_score = success_metrics.get("performance_score", 0.0)
        if performance_score > 0.8:
            insights.append("Excellent performance efficiency achieved")
        elif performance_score < 0.5:
            insights.append("Performance optimization opportunities identified")
        
        # Optimization insights
        if optimizations:
            high_impact_opts = [opt for opt in optimizations if opt.expected_improvement > 0.3]
            if high_impact_opts:
                insights.append(f"Identified {len(high_impact_opts)} high-impact optimization opportunities")
            
            total_improvement = sum(opt.expected_improvement for opt in optimizations)
            insights.append(f"Total potential improvement: {total_improvement:.1%}")
        
        # Pattern-specific insights
        if "action_sequences" in patterns:
            sequences = patterns["action_sequences"]
            if sequences:
                best_sequence = max(sequences, key=lambda s: s.get("pattern_strength", 0))
                insights.append(f"Most effective action sequence: {' -> '.join(best_sequence.get('sequence', []))}")
        
        return insights
    
    async def _calculate_learning_confidence(self, patterns: Dict[str, Any], 
                                           success_metrics: Dict[str, Any]) -> float:
        """Calculate confidence in the learning results"""
        
        confidence_factors = []
        
        # Pattern extraction confidence
        pattern_count = sum(len(p) if isinstance(p, list) else 1 for p in patterns.values())
        pattern_confidence = min(1.0, pattern_count / 10.0)  # Higher confidence with more patterns
        confidence_factors.append(pattern_confidence)
        
        # Success metrics confidence
        metrics_available = len([v for v in success_metrics.values() if v > 0])
        metrics_confidence = metrics_available / len(success_metrics)
        confidence_factors.append(metrics_confidence)
        
        # Historical data confidence
        execution_count = len(self.execution_history)
        history_confidence = min(1.0, execution_count / 50.0)  # Higher confidence with more executions
        confidence_factors.append(history_confidence)
        
        # Model accuracy confidence
        model_confidence = self.success_predictor.model_accuracy
        confidence_factors.append(model_confidence)
        
        return np.mean(confidence_factors)
    
    async def predict_workflow_success(self, workflow_plan: Dict[str, Any]) -> Tuple[float, float]:
        """Predict the success probability of a planned workflow"""
        
        # Extract features from workflow plan
        features = await self._extract_workflow_features(workflow_plan)
        
        # Use prediction model
        success_probability, confidence = await self.success_predictor.predict_success(features)
        
        return success_probability, confidence
    
    async def _extract_workflow_features(self, workflow_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from a workflow plan for prediction"""
        
        features = {}
        
        # Basic workflow characteristics
        steps = workflow_plan.get("steps", [])
        features["step_count"] = len(steps)
        features["estimated_duration"] = sum(step.get("estimated_duration", 1.0) for step in steps)
        features["complexity_score"] = sum(1 for step in steps if step.get("complexity", "medium") == "high")
        
        # Resource requirements
        total_resources = {}
        for step in steps:
            step_resources = step.get("resources", {})
            for resource_type, amount in step_resources.items():
                total_resources[resource_type] = total_resources.get(resource_type, 0) + amount
        
        for resource_type, total_amount in total_resources.items():
            features[f"total_{resource_type}"] = total_amount
        
        # Step type distribution
        step_types = defaultdict(int)
        for step in steps:
            step_type = step.get("type", "unknown")
            step_types[step_type] += 1
        
        for step_type, count in step_types.items():
            features[f"{step_type}_steps"] = count
        
        return features
    
    async def recommend_optimizations(self, workflow_type: str) -> List[OptimizationRecommendation]:
        """Recommend optimizations for a specific workflow type"""
        
        # Find similar historical executions
        similar_executions = []
        for execution in self.execution_history:
            if execution.workflow_type == workflow_type:
                similar_executions.append(execution)
        
        if not similar_executions:
            return []
        
        # Extract patterns from similar executions
        all_patterns = {"action_sequences": [], "resource_usage": {}, "timing_patterns": {}, "decision_points": []}
        
        for execution in similar_executions:
            execution_patterns = await self.pattern_miner.extract_patterns(execution.steps)
            
            # Merge patterns
            for pattern_type, pattern_data in execution_patterns.items():
                if pattern_type in all_patterns:
                    if isinstance(pattern_data, list):
                        all_patterns[pattern_type].extend(pattern_data)
                    elif isinstance(pattern_data, dict):
                        all_patterns[pattern_type].update(pattern_data)
        
        # Generate optimizations
        optimizations = await self.optimizer.generate_optimizations(all_patterns)
        
        return optimizations