#!/usr/bin/env python3
"""
Parallel MCP Aggregation Engine
Synthesizes results from multiple MCP servers into unified intelligence reports
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import hashlib
import re
from collections import defaultdict, Counter
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AggregationStrategy(Enum):
    MERGE = "merge"
    CONSENSUS = "consensus" 
    WEIGHTED = "weighted"
    PRIORITY = "priority"
    BEST_OF = "best_of"

class ConflictResolution(Enum):
    MAJORITY = "majority"
    HIGHEST_CONFIDENCE = "highest_confidence"
    MOST_RECENT = "most_recent"
    SERVER_PRIORITY = "server_priority"
    USER_PREFERENCE = "user_preference"

@dataclass
class ResultMetadata:
    server_name: str
    operation: str
    timestamp: float
    execution_time: float
    confidence: float = 1.0
    quality_score: float = 1.0
    source_data_size: int = 0
    
@dataclass
class AggregatedResult:
    command_type: str
    aggregation_id: str
    unified_result: Dict[str, Any]
    source_results: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    confidence_score: float
    quality_metrics: Dict[str, float]
    conflicts_detected: List[Dict[str, Any]]
    aggregation_strategy: AggregationStrategy
    processing_time: float
    created_at: float

class QualityAssessor:
    """Assesses quality of individual results and aggregated outputs"""
    
    def __init__(self):
        self.quality_weights = {
            'completeness': 0.25,
            'accuracy': 0.30,
            'relevance': 0.25,
            'freshness': 0.20
        }
        
    def assess_result_quality(self, result: Dict[str, Any], metadata: ResultMetadata) -> float:
        """Assess quality of a single result"""
        
        scores = {}
        
        # Completeness: How complete is the result
        scores['completeness'] = self.assess_completeness(result)
        
        # Accuracy: Based on server reliability and confidence
        scores['accuracy'] = self.assess_accuracy(result, metadata)
        
        # Relevance: How relevant is the result to the query
        scores['relevance'] = self.assess_relevance(result, metadata)
        
        # Freshness: How recent is the data
        scores['freshness'] = self.assess_freshness(metadata)
        
        # Calculate weighted score
        quality_score = sum(
            scores[metric] * self.quality_weights[metric]
            for metric in scores
        )
        
        return min(1.0, max(0.0, quality_score))
    
    def assess_completeness(self, result: Dict[str, Any]) -> float:
        """Assess completeness of result data"""
        if not result:
            return 0.0
        
        # Count non-empty fields
        total_fields = 0
        complete_fields = 0
        
        def count_fields(obj, path=""):
            nonlocal total_fields, complete_fields
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    total_fields += 1
                    if value and value != "" and value != []:
                        complete_fields += 1
                    if isinstance(value, (dict, list)):
                        count_fields(value, f"{path}.{key}")
            elif isinstance(obj, list):
                total_fields += len(obj)
                complete_fields += sum(1 for item in obj if item and item != "")
        
        count_fields(result)
        
        return complete_fields / total_fields if total_fields > 0 else 0.0
    
    def assess_accuracy(self, result: Dict[str, Any], metadata: ResultMetadata) -> float:
        """Assess accuracy based on server reliability and result confidence"""
        
        # Server reliability scores
        server_reliability = {
            'ml-code-intelligence': 0.95,
            'context-aware-memory': 0.98,
            'agentic-workflow': 0.93,
            'predictive-analytics': 0.90,
            'ml-testing-qa': 0.96
        }
        
        base_reliability = server_reliability.get(metadata.server_name, 0.85)
        
        # Factor in execution time (faster might indicate cached/simple results)
        time_factor = 1.0
        if metadata.execution_time < 0.1:
            time_factor = 0.9  # Might be cached
        elif metadata.execution_time > 10.0:
            time_factor = 0.8  # Might have encountered issues
        
        return base_reliability * metadata.confidence * time_factor
    
    def assess_relevance(self, result: Dict[str, Any], metadata: ResultMetadata) -> float:
        """Assess relevance of result to the operation"""
        
        # Operation-specific relevance assessment
        relevance_indicators = {
            'analyze_codebase': ['analysis', 'metrics', 'quality', 'recommendations'],
            'retrieve_context': ['context', 'history', 'relevant', 'suggestions'],
            'risk_analysis': ['risk', 'factors', 'mitigation', 'score'],
            'comprehensive_qa': ['quality', 'test', 'coverage', 'issues'],
            'orchestrate_implementation': ['workflow', 'steps', 'timeline', 'optimization']
        }
        
        indicators = relevance_indicators.get(metadata.operation, [])
        if not indicators:
            return 0.8  # Default relevance for unknown operations
        
        # Count how many relevance indicators are present
        result_text = json.dumps(result).lower()
        matches = sum(1 for indicator in indicators if indicator in result_text)
        
        return min(1.0, matches / len(indicators))
    
    def assess_freshness(self, metadata: ResultMetadata) -> float:
        """Assess freshness based on timestamp"""
        age_seconds = time.time() - metadata.timestamp
        age_minutes = age_seconds / 60
        
        # Fresher results get higher scores
        if age_minutes < 1:
            return 1.0
        elif age_minutes < 5:
            return 0.9
        elif age_minutes < 15:
            return 0.7
        elif age_minutes < 60:
            return 0.5
        else:
            return 0.3

class ConflictDetector:
    """Detects conflicts between results from different servers"""
    
    def __init__(self):
        self.numeric_tolerance = 0.1  # 10% tolerance for numeric values
        self.semantic_similarity_threshold = 0.8
        
    def detect_conflicts(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect conflicts between multiple results"""
        conflicts = []
        
        if len(results) < 2:
            return conflicts
        
        # Group results by field for comparison
        field_values = defaultdict(list)
        
        for i, result in enumerate(results):
            self.extract_comparable_fields(result, field_values, result_index=i)
        
        # Check for conflicts in each field
        for field_path, values in field_values.items():
            if len(set(str(v['value']) for v in values)) > 1:  # Different values
                conflict = self.analyze_field_conflict(field_path, values)
                if conflict:
                    conflicts.append(conflict)
        
        return conflicts
    
    def extract_comparable_fields(self, obj: Any, field_values: Dict, path: str = "", result_index: int = 0):
        """Extract comparable fields from result object"""
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                if isinstance(value, (str, int, float, bool)):
                    field_values[current_path].append({
                        'value': value,
                        'result_index': result_index,
                        'type': type(value).__name__
                    })
                elif isinstance(value, (dict, list)):
                    self.extract_comparable_fields(value, field_values, current_path, result_index)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]"
                if isinstance(item, (str, int, float, bool)):
                    field_values[current_path].append({
                        'value': item,
                        'result_index': result_index,
                        'type': type(item).__name__
                    })
                elif isinstance(item, (dict, list)):
                    self.extract_comparable_fields(item, field_values, current_path, result_index)
    
    def analyze_field_conflict(self, field_path: str, values: List[Dict]) -> Optional[Dict[str, Any]]:
        """Analyze a specific field conflict"""
        
        if not values or len(values) < 2:
            return None
        
        # Group by type
        by_type = defaultdict(list)
        for value_info in values:
            by_type[value_info['type']].append(value_info)
        
        # If all same type, check for semantic conflicts
        if len(by_type) == 1:
            value_type = next(iter(by_type.keys()))
            
            if value_type in ['int', 'float']:
                return self.analyze_numeric_conflict(field_path, values)
            elif value_type == 'str':
                return self.analyze_string_conflict(field_path, values)
            elif value_type == 'bool':
                return self.analyze_boolean_conflict(field_path, values)
        else:
            # Type mismatch
            return {
                'field': field_path,
                'conflict_type': 'type_mismatch',
                'values': [v['value'] for v in values],
                'types': [v['type'] for v in values],
                'severity': 'high',
                'resolution_suggestions': ['Use type conversion', 'Choose most reliable source']
            }
        
        return None
    
    def analyze_numeric_conflict(self, field_path: str, values: List[Dict]) -> Optional[Dict[str, Any]]:
        """Analyze conflicts in numeric values"""
        
        numeric_values = [float(v['value']) for v in values]
        
        # Check if values are within tolerance
        min_val = min(numeric_values)
        max_val = max(numeric_values)
        
        if min_val == 0:
            relative_diff = float('inf') if max_val != 0 else 0
        else:
            relative_diff = (max_val - min_val) / abs(min_val)
        
        if relative_diff > self.numeric_tolerance:
            return {
                'field': field_path,
                'conflict_type': 'numeric_variance',
                'values': numeric_values,
                'variance': statistics.variance(numeric_values) if len(numeric_values) > 1 else 0,
                'relative_difference': relative_diff,
                'severity': 'high' if relative_diff > 0.5 else 'medium',
                'resolution_suggestions': ['Use median value', 'Use weighted average', 'Investigate source accuracy']
            }
        
        return None
    
    def analyze_string_conflict(self, field_path: str, values: List[Dict]) -> Optional[Dict[str, Any]]:
        """Analyze conflicts in string values"""
        
        string_values = [str(v['value']) for v in values]
        unique_values = list(set(string_values))
        
        if len(unique_values) <= 1:
            return None
        
        # Calculate similarity between strings
        max_similarity = 0
        for i in range(len(unique_values)):
            for j in range(i + 1, len(unique_values)):
                similarity = self.calculate_string_similarity(unique_values[i], unique_values[j])
                max_similarity = max(max_similarity, similarity)
        
        severity = 'low' if max_similarity > 0.8 else 'medium' if max_similarity > 0.5 else 'high'
        
        return {
            'field': field_path,
            'conflict_type': 'string_difference',
            'values': unique_values,
            'max_similarity': max_similarity,
            'severity': severity,
            'resolution_suggestions': ['Use longest value', 'Concatenate unique parts', 'Choose most detailed']
        }
    
    def analyze_boolean_conflict(self, field_path: str, values: List[Dict]) -> Optional[Dict[str, Any]]:
        """Analyze conflicts in boolean values"""
        
        bool_values = [bool(v['value']) for v in values]
        
        if len(set(bool_values)) > 1:
            return {
                'field': field_path,
                'conflict_type': 'boolean_contradiction',
                'values': bool_values,
                'true_count': sum(bool_values),
                'false_count': len(bool_values) - sum(bool_values),
                'severity': 'high',
                'resolution_suggestions': ['Use majority vote', 'Check server reliability', 'Manual review required']
            }
        
        return None
    
    def calculate_string_similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity between two strings"""
        if not s1 or not s2:
            return 0.0
        
        # Simple character-based similarity
        s1_lower = s1.lower()
        s2_lower = s2.lower()
        
        if s1_lower == s2_lower:
            return 1.0
        
        # Calculate Jaccard similarity on character n-grams
        def get_ngrams(s, n=2):
            return set(s[i:i+n] for i in range(len(s) - n + 1))
        
        s1_ngrams = get_ngrams(s1_lower)
        s2_ngrams = get_ngrams(s2_lower)
        
        if not s1_ngrams and not s2_ngrams:
            return 1.0
        
        intersection = len(s1_ngrams & s2_ngrams)
        union = len(s1_ngrams | s2_ngrams)
        
        return intersection / union if union > 0 else 0.0

class AggregationEngine:
    """Main engine for aggregating results from multiple MCP servers"""
    
    def __init__(self):
        self.quality_assessor = QualityAssessor()
        self.conflict_detector = ConflictDetector()
        
        # Server priority weights (higher = more trusted)
        self.server_weights = {
            'context-aware-memory': 1.0,
            'ml-code-intelligence': 0.95,
            'ml-testing-qa': 0.96,
            'predictive-analytics': 0.90,
            'agentic-workflow': 0.93
        }
        
        # Operation-specific aggregation strategies
        self.strategy_mapping = {
            'analyze_codebase': AggregationStrategy.WEIGHTED,
            'retrieve_context': AggregationStrategy.MERGE,
            'risk_analysis': AggregationStrategy.CONSENSUS,
            'comprehensive_qa': AggregationStrategy.BEST_OF,
            'orchestrate_implementation': AggregationStrategy.PRIORITY
        }
        
    def aggregate_results(self, 
                         command_type: str,
                         results: List[Dict[str, Any]], 
                         metadatas: List[ResultMetadata],
                         strategy: Optional[AggregationStrategy] = None) -> AggregatedResult:
        """Aggregate multiple results into a unified result"""
        
        start_time = time.time()
        aggregation_id = str(uuid.uuid4())
        
        logger.info(f"Aggregating {len(results)} results for {command_type}")
        
        # Determine aggregation strategy
        if strategy is None:
            # Get strategy based on most common operation
            operations = [meta.operation for meta in metadatas]
            most_common_op = Counter(operations).most_common(1)[0][0]
            strategy = self.strategy_mapping.get(most_common_op, AggregationStrategy.WEIGHTED)
        
        # Assess quality of each result
        quality_scores = []
        for result, metadata in zip(results, metadatas):
            quality = self.quality_assessor.assess_result_quality(result, metadata)
            quality_scores.append(quality)
            metadata.quality_score = quality
        
        # Detect conflicts
        conflicts = self.conflict_detector.detect_conflicts(results)
        
        # Apply aggregation strategy
        unified_result = self.apply_aggregation_strategy(
            strategy, results, metadatas, quality_scores
        )
        
        # Calculate overall confidence
        confidence_score = self.calculate_confidence(results, metadatas, quality_scores, conflicts)
        
        # Generate quality metrics
        quality_metrics = self.generate_quality_metrics(results, metadatas, quality_scores)
        
        # Create aggregated result
        processing_time = time.time() - start_time
        
        aggregated = AggregatedResult(
            command_type=command_type,
            aggregation_id=aggregation_id,
            unified_result=unified_result,
            source_results=results,
            metadata={
                'server_count': len(set(meta.server_name for meta in metadatas)),
                'operation_count': len(set(meta.operation for meta in metadatas)),
                'total_execution_time': sum(meta.execution_time for meta in metadatas),
                'source_metadatas': [asdict(meta) for meta in metadatas]
            },
            confidence_score=confidence_score,
            quality_metrics=quality_metrics,
            conflicts_detected=conflicts,
            aggregation_strategy=strategy,
            processing_time=processing_time,
            created_at=start_time
        )
        
        logger.info(f"Aggregation completed in {processing_time:.3f}s "
                   f"with confidence {confidence_score:.2f}")
        
        return aggregated
    
    def apply_aggregation_strategy(self, 
                                 strategy: AggregationStrategy,
                                 results: List[Dict[str, Any]], 
                                 metadatas: List[ResultMetadata],
                                 quality_scores: List[float]) -> Dict[str, Any]:
        """Apply specific aggregation strategy"""
        
        if strategy == AggregationStrategy.MERGE:
            return self.merge_strategy(results, metadatas, quality_scores)
        elif strategy == AggregationStrategy.CONSENSUS:
            return self.consensus_strategy(results, metadatas, quality_scores)
        elif strategy == AggregationStrategy.WEIGHTED:
            return self.weighted_strategy(results, metadatas, quality_scores)
        elif strategy == AggregationStrategy.PRIORITY:
            return self.priority_strategy(results, metadatas, quality_scores)
        elif strategy == AggregationStrategy.BEST_OF:
            return self.best_of_strategy(results, metadatas, quality_scores)
        else:
            return self.weighted_strategy(results, metadatas, quality_scores)
    
    def merge_strategy(self, results: List[Dict], metadatas: List[ResultMetadata], quality_scores: List[float]) -> Dict[str, Any]:
        """Merge all results by combining non-conflicting information"""
        
        merged = {
            'summary': 'Merged results from multiple MCP servers',
            'sources': [meta.server_name for meta in metadatas],
            'combined_data': {}
        }
        
        # Combine all results
        for i, (result, metadata) in enumerate(zip(results, metadatas)):
            server_key = f"{metadata.server_name}_results"
            merged['combined_data'][server_key] = {
                'data': result,
                'quality_score': quality_scores[i],
                'execution_time': metadata.execution_time
            }
        
        # Extract common themes
        all_text = ' '.join([
            json.dumps(result) for result in results
        ])
        
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', all_text.lower())
        word_counts = Counter(words)
        common_themes = [word for word, count in word_counts.most_common(10) 
                        if count > 1 and len(word) > 3]
        
        merged['common_themes'] = common_themes
        
        return merged
    
    def consensus_strategy(self, results: List[Dict], metadatas: List[ResultMetadata], quality_scores: List[float]) -> Dict[str, Any]:
        """Use consensus among results, preferring majority opinion"""
        
        consensus = {
            'summary': 'Consensus view from multiple MCP servers',
            'agreement_level': 'medium',
            'consensus_data': {}
        }
        
        # Find fields that appear in multiple results
        field_consensus = defaultdict(list)
        
        for result in results:
            self.extract_consensus_fields(result, field_consensus)
        
        # Keep fields that appear in majority of results
        threshold = len(results) / 2
        for field, values in field_consensus.items():
            if len(values) >= threshold:
                # Use most common value
                value_counts = Counter(str(v) for v in values)
                consensus_value = value_counts.most_common(1)[0][0]
                
                # Try to convert back to original type
                try:
                    if consensus_value.isdigit():
                        consensus_value = int(consensus_value)
                    elif '.' in consensus_value and consensus_value.replace('.', '').isdigit():
                        consensus_value = float(consensus_value)
                except:
                    pass
                
                consensus['consensus_data'][field] = {
                    'value': consensus_value,
                    'agreement_count': len([v for v in values if str(v) == str(consensus_value)]),
                    'total_responses': len(values)
                }
        
        # Calculate agreement level
        if consensus['consensus_data']:
            agreement_scores = [
                item['agreement_count'] / item['total_responses']
                for item in consensus['consensus_data'].values()
            ]
            avg_agreement = statistics.mean(agreement_scores)
            
            if avg_agreement > 0.8:
                consensus['agreement_level'] = 'high'
            elif avg_agreement > 0.6:
                consensus['agreement_level'] = 'medium'
            else:
                consensus['agreement_level'] = 'low'
        
        return consensus
    
    def weighted_strategy(self, results: List[Dict], metadatas: List[ResultMetadata], quality_scores: List[float]) -> Dict[str, Any]:
        """Weight results by server reliability and quality scores"""
        
        weighted = {
            'summary': 'Weighted aggregation based on server reliability and quality',
            'weights_used': {},
            'weighted_data': {}
        }
        
        # Calculate weights
        weights = []
        for metadata, quality in zip(metadatas, quality_scores):
            server_weight = self.server_weights.get(metadata.server_name, 0.5)
            combined_weight = server_weight * quality * metadata.confidence
            weights.append(combined_weight)
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            normalized_weights = [w / total_weight for w in weights]
        else:
            normalized_weights = [1.0 / len(weights)] * len(weights)
        
        # Store weight information
        for i, (metadata, weight) in enumerate(zip(metadatas, normalized_weights)):
            weighted['weights_used'][metadata.server_name] = {
                'weight': weight,
                'quality_score': quality_scores[i],
                'server_reliability': self.server_weights.get(metadata.server_name, 0.5)
            }
        
        # Apply weights to combine results
        weighted_results = {}
        for i, (result, weight) in enumerate(zip(results, normalized_weights)):
            server_name = metadatas[i].server_name
            weighted_results[f"{server_name}_weighted"] = {
                'data': result,
                'weight': weight,
                'contribution': f"{weight*100:.1f}%"
            }
        
        weighted['weighted_data'] = weighted_results
        
        # Create summary recommendations
        recommendations = []
        for result, metadata, weight in zip(results, metadatas, normalized_weights):
            if weight > 0.2 and 'recommendations' in result:  # High weight results
                if isinstance(result['recommendations'], list):
                    recommendations.extend(result['recommendations'])
        
        if recommendations:
            weighted['combined_recommendations'] = list(set(recommendations))
        
        return weighted
    
    def priority_strategy(self, results: List[Dict], metadatas: List[ResultMetadata], quality_scores: List[float]) -> Dict[str, Any]:
        """Use server priority order to select best result"""
        
        # Sort by priority (server weight * quality)
        priority_scores = []
        for metadata, quality in zip(metadatas, quality_scores):
            server_weight = self.server_weights.get(metadata.server_name, 0.5)
            priority_score = server_weight * quality
            priority_scores.append(priority_score)
        
        # Find highest priority result
        best_index = priority_scores.index(max(priority_scores))
        best_result = results[best_index]
        best_metadata = metadatas[best_index]
        
        priority_result = {
            'summary': f'Selected highest priority result from {best_metadata.server_name}',
            'selected_server': best_metadata.server_name,
            'priority_score': priority_scores[best_index],
            'primary_result': best_result,
            'alternative_sources': []
        }
        
        # Include alternatives
        for i, (result, metadata, score) in enumerate(zip(results, metadatas, priority_scores)):
            if i != best_index:
                priority_result['alternative_sources'].append({
                    'server': metadata.server_name,
                    'priority_score': score,
                    'data': result
                })
        
        return priority_result
    
    def best_of_strategy(self, results: List[Dict], metadatas: List[ResultMetadata], quality_scores: List[float]) -> Dict[str, Any]:
        """Select the single best result based on quality score"""
        
        # Find best quality result
        best_index = quality_scores.index(max(quality_scores))
        best_result = results[best_index]
        best_metadata = metadatas[best_index]
        
        return {
            'summary': f'Best quality result selected from {best_metadata.server_name}',
            'selected_server': best_metadata.server_name,
            'quality_score': quality_scores[best_index],
            'best_result': best_result,
            'execution_time': best_metadata.execution_time,
            'confidence': best_metadata.confidence,
            'quality_ranking': [
                {
                    'server': metadata.server_name,
                    'quality_score': quality_scores[i],
                    'rank': i + 1
                }
                for i, metadata in sorted(enumerate(metadatas), 
                                        key=lambda x: quality_scores[x[0]], 
                                        reverse=True)
            ]
        }
    
    def extract_consensus_fields(self, obj: Any, field_values: Dict, path: str = ""):
        """Extract fields for consensus analysis"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, (str, int, float, bool)):
                    field_values[current_path].append(value)
                elif isinstance(value, (dict, list)):
                    self.extract_consensus_fields(value, field_values, current_path)
    
    def calculate_confidence(self, results: List[Dict], metadatas: List[ResultMetadata], 
                           quality_scores: List[float], conflicts: List[Dict]) -> float:
        """Calculate overall confidence in aggregated result"""
        
        if not results:
            return 0.0
        
        # Base confidence from individual results
        base_confidence = statistics.mean([meta.confidence for meta in metadatas])
        
        # Quality factor
        quality_factor = statistics.mean(quality_scores)
        
        # Agreement factor (lower if many conflicts)
        agreement_factor = max(0.1, 1.0 - (len(conflicts) * 0.1))
        
        # Server diversity factor (more servers = higher confidence)
        unique_servers = len(set(meta.server_name for meta in metadatas))
        diversity_factor = min(1.0, unique_servers / 5)  # Max of 5 servers
        
        # Combined confidence
        confidence = base_confidence * quality_factor * agreement_factor * diversity_factor
        
        return min(1.0, max(0.0, confidence))
    
    def generate_quality_metrics(self, results: List[Dict], metadatas: List[ResultMetadata], 
                                quality_scores: List[float]) -> Dict[str, float]:
        """Generate quality metrics for the aggregation"""
        
        return {
            'avg_quality_score': statistics.mean(quality_scores),
            'min_quality_score': min(quality_scores),
            'max_quality_score': max(quality_scores),
            'quality_variance': statistics.variance(quality_scores) if len(quality_scores) > 1 else 0,
            'avg_execution_time': statistics.mean([meta.execution_time for meta in metadatas]),
            'total_data_points': sum(len(json.dumps(result)) for result in results),
            'server_diversity': len(set(meta.server_name for meta in metadatas)) / len(metadatas),
            'temporal_spread': (max(meta.timestamp for meta in metadatas) - 
                               min(meta.timestamp for meta in metadatas)) if metadatas else 0
        }

# Example usage and testing
async def test_aggregation_engine():
    """Test the aggregation engine functionality"""
    
    engine = AggregationEngine()
    
    # Create test results and metadata
    results = [
        {
            'analysis': 'Code quality is good',
            'metrics': {'complexity': 0.7, 'maintainability': 0.8},
            'recommendations': ['Add error handling', 'Improve documentation']
        },
        {
            'context': 'Retrieved relevant project history',
            'suggestions': ['Consider previous approach', 'Review past decisions'],
            'relevance_score': 0.9
        },
        {
            'risk_score': 0.3,
            'risk_factors': ['Timeline pressure', 'Complex integration'],
            'mitigation': ['Phased rollout', 'Additional testing']
        }
    ]
    
    metadatas = [
        ResultMetadata(
            server_name='ml-code-intelligence',
            operation='analyze_codebase',
            timestamp=time.time(),
            execution_time=1.2,
            confidence=0.9
        ),
        ResultMetadata(
            server_name='context-aware-memory',
            operation='retrieve_context',
            timestamp=time.time(),
            execution_time=0.8,
            confidence=0.95
        ),
        ResultMetadata(
            server_name='predictive-analytics',
            operation='risk_analysis',
            timestamp=time.time(),
            execution_time=1.5,
            confidence=0.85
        )
    ]
    
    # Test different aggregation strategies
    strategies = [
        AggregationStrategy.MERGE,
        AggregationStrategy.WEIGHTED,
        AggregationStrategy.CONSENSUS,
        AggregationStrategy.BEST_OF
    ]
    
    for strategy in strategies:
        print(f"\n=== Testing {strategy.value} strategy ===")
        
        aggregated = engine.aggregate_results(
            command_type='/analyze_10x',
            results=results,
            metadatas=metadatas,
            strategy=strategy
        )
        
        print(f"Confidence: {aggregated.confidence_score:.3f}")
        print(f"Processing time: {aggregated.processing_time:.3f}s")
        print(f"Conflicts detected: {len(aggregated.conflicts_detected)}")
        print(f"Quality metrics: {aggregated.quality_metrics}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_aggregation_engine())