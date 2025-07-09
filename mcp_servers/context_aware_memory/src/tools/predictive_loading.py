"""
Predictive Loading System for Context-Aware Memory
ML-powered memory prediction, pre-loading, and proactive suggestions
"""

import asyncio
import logging
import json
import time
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import heapq
import statistics

from .semantic_storage import MemoryItem, MemoryContext, MemoryQuery, MemoryType, AccessLevel
from .intelligent_retrieval import IntelligentRetriever, RetrievalStrategy, UserProfile

logger = logging.getLogger(__name__)


class PredictionType(Enum):
    """Types of predictions the system can make"""
    NEXT_MEMORY = "next_memory"
    RELATED_MEMORIES = "related_memories"
    CONTEXT_MEMORIES = "context_memories"
    TEMPORAL_MEMORIES = "temporal_memories"
    COLLABORATIVE_MEMORIES = "collaborative_memories"
    WORKFLOW_MEMORIES = "workflow_memories"
    SEASONAL_MEMORIES = "seasonal_memories"


class PredictionConfidence(Enum):
    """Confidence levels for predictions"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class AccessPattern:
    """Represents a memory access pattern"""
    pattern_id: str
    user_id: str
    sequence: List[str]  # memory_ids in order
    context_features: Dict[str, Any]
    temporal_features: Dict[str, Any]
    frequency: int
    last_seen: datetime
    prediction_accuracy: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['last_seen'] = self.last_seen.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccessPattern':
        """Create from dictionary"""
        if 'last_seen' in data:
            data['last_seen'] = datetime.fromisoformat(data['last_seen'])
        return cls(**data)


@dataclass
class MemoryPrediction:
    """Represents a predicted memory need"""
    prediction_id: str
    predicted_memory_ids: List[str]
    prediction_type: PredictionType
    confidence: PredictionConfidence
    confidence_score: float
    reasoning: str
    context: MemoryContext
    predicted_at: datetime
    valid_until: datetime
    evidence: Dict[str, Any]
    
    def is_valid(self) -> bool:
        """Check if prediction is still valid"""
        return datetime.now() < self.valid_until
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['prediction_type'] = self.prediction_type.value
        result['confidence'] = self.confidence.value
        result['predicted_at'] = self.predicted_at.isoformat()
        result['valid_until'] = self.valid_until.isoformat()
        result['context'] = self.context.to_dict()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryPrediction':
        """Create from dictionary"""
        data['prediction_type'] = PredictionType(data['prediction_type'])
        data['confidence'] = PredictionConfidence(data['confidence'])
        data['predicted_at'] = datetime.fromisoformat(data['predicted_at'])
        data['valid_until'] = datetime.fromisoformat(data['valid_until'])
        data['context'] = MemoryContext.from_dict(data['context'])
        return cls(**data)


@dataclass
class PreloadCache:
    """Cache for preloaded memories"""
    memories: Dict[str, MemoryItem] = field(default_factory=dict)
    load_times: Dict[str, datetime] = field(default_factory=dict)
    access_counts: Dict[str, int] = field(default_factory=dict)
    hit_rate: float = 0.0
    max_size: int = 1000
    
    def add_memory(self, memory: MemoryItem):
        """Add memory to preload cache"""
        if len(self.memories) >= self.max_size:
            self._evict_oldest()
        
        self.memories[memory.memory_id] = memory
        self.load_times[memory.memory_id] = datetime.now()
        self.access_counts[memory.memory_id] = 0
    
    def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """Get memory from cache"""
        if memory_id in self.memories:
            self.access_counts[memory_id] += 1
            return self.memories[memory_id]
        return None
    
    def _evict_oldest(self):
        """Evict oldest memory from cache"""
        if not self.load_times:
            return
        
        oldest_id = min(self.load_times.keys(), key=lambda k: self.load_times[k])
        self.memories.pop(oldest_id, None)
        self.load_times.pop(oldest_id, None)
        self.access_counts.pop(oldest_id, None)
    
    def update_hit_rate(self):
        """Update cache hit rate"""
        total_accesses = sum(self.access_counts.values())
        hits = sum(1 for count in self.access_counts.values() if count > 0)
        self.hit_rate = hits / max(1, total_accesses)


class MemoryPredictor:
    """ML-powered memory prediction engine"""
    
    def __init__(self):
        self.patterns: Dict[str, AccessPattern] = {}
        self.temporal_patterns: Dict[str, List[Tuple[datetime, str]]] = defaultdict(list)
        self.context_associations: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.sequence_patterns: Dict[str, List[str]] = defaultdict(list)
        self.user_workflows: Dict[str, List[List[str]]] = defaultdict(list)
        
        # Learning parameters
        self.min_pattern_frequency = 3
        self.max_pattern_age_days = 30
        self.sequence_window = 5
        self.confidence_threshold = 0.6
    
    def learn_from_access(self, memory_id: str, context: MemoryContext, 
                         timestamp: datetime, user_id: str):
        """Learn from memory access event"""
        # Update temporal patterns
        self.temporal_patterns[user_id].append((timestamp, memory_id))
        
        # Keep only recent patterns
        cutoff = datetime.now() - timedelta(days=self.max_pattern_age_days)
        self.temporal_patterns[user_id] = [
            (t, mid) for t, mid in self.temporal_patterns[user_id] if t > cutoff
        ]
        
        # Update context associations
        context_key = self._get_context_key(context)
        self.context_associations[context_key][memory_id] += 1.0
        
        # Update sequence patterns
        self._update_sequence_patterns(user_id, memory_id)
        
        # Update workflow patterns
        self._update_workflow_patterns(user_id, memory_id, context)
    
    def predict_next_memories(self, context: MemoryContext, user_id: str, 
                            recent_accesses: List[str]) -> List[MemoryPrediction]:
        """Predict next memories based on patterns"""
        predictions = []
        
        # Sequence-based predictions
        seq_predictions = self._predict_from_sequences(user_id, recent_accesses, context)
        predictions.extend(seq_predictions)
        
        # Context-based predictions
        context_predictions = self._predict_from_context(context, user_id)
        predictions.extend(context_predictions)
        
        # Temporal predictions
        temporal_predictions = self._predict_from_temporal_patterns(user_id, context)
        predictions.extend(temporal_predictions)
        
        # Workflow predictions
        workflow_predictions = self._predict_from_workflows(user_id, context, recent_accesses)
        predictions.extend(workflow_predictions)
        
        # Collaborative predictions
        collaborative_predictions = self._predict_from_collaboration(user_id, context)
        predictions.extend(collaborative_predictions)
        
        # Rank and filter predictions
        predictions = self._rank_predictions(predictions)
        
        return predictions[:10]  # Return top 10 predictions
    
    def predict_related_memories(self, memory_id: str, context: MemoryContext) -> List[MemoryPrediction]:
        """Predict memories related to a specific memory"""
        predictions = []
        
        # Find memories that commonly appear together
        for user_id, patterns in self.temporal_patterns.items():
            related_ids = self._find_related_memories(memory_id, patterns)
            
            if related_ids:
                prediction = MemoryPrediction(
                    prediction_id=f"related_{memory_id}_{int(time.time())}",
                    predicted_memory_ids=related_ids,
                    prediction_type=PredictionType.RELATED_MEMORIES,
                    confidence=self._calculate_confidence(related_ids, context),
                    confidence_score=self._calculate_confidence_score(related_ids, patterns),
                    reasoning=f"Memories commonly accessed together with {memory_id}",
                    context=context,
                    predicted_at=datetime.now(),
                    valid_until=datetime.now() + timedelta(hours=24),
                    evidence={
                        'base_memory': memory_id,
                        'co_occurrence_patterns': len(related_ids),
                        'user_patterns': user_id
                    }
                )
                predictions.append(prediction)
        
        return predictions
    
    def predict_seasonal_memories(self, context: MemoryContext, user_id: str) -> List[MemoryPrediction]:
        """Predict memories based on seasonal/cyclical patterns"""
        predictions = []
        
        now = datetime.now()
        current_hour = now.hour
        current_day = now.weekday()
        current_month = now.month
        
        # Find memories accessed at similar times
        if user_id in self.temporal_patterns:
            seasonal_memories = []
            
            for access_time, memory_id in self.temporal_patterns[user_id]:
                # Check for similar time patterns
                if (abs(access_time.hour - current_hour) <= 1 and
                    access_time.weekday() == current_day):
                    seasonal_memories.append(memory_id)
                
                # Check for monthly patterns
                if access_time.month == current_month:
                    seasonal_memories.append(memory_id)
            
            if seasonal_memories:
                # Remove duplicates and get most frequent
                memory_counts = defaultdict(int)
                for mid in seasonal_memories:
                    memory_counts[mid] += 1
                
                top_memories = sorted(memory_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                
                prediction = MemoryPrediction(
                    prediction_id=f"seasonal_{user_id}_{int(time.time())}",
                    predicted_memory_ids=[mid for mid, _ in top_memories],
                    prediction_type=PredictionType.SEASONAL_MEMORIES,
                    confidence=PredictionConfidence.MEDIUM,
                    confidence_score=0.6,
                    reasoning="Memories typically accessed at this time",
                    context=context,
                    predicted_at=datetime.now(),
                    valid_until=datetime.now() + timedelta(hours=6),
                    evidence={
                        'time_patterns': {
                            'hour': current_hour,
                            'day': current_day,
                            'month': current_month
                        },
                        'pattern_strength': len(seasonal_memories)
                    }
                )
                predictions.append(prediction)
        
        return predictions
    
    def _predict_from_sequences(self, user_id: str, recent_accesses: List[str], 
                               context: MemoryContext) -> List[MemoryPrediction]:
        """Predict based on sequence patterns"""
        predictions = []
        
        if not recent_accesses:
            return predictions
        
        # Look for sequence patterns
        sequence_key = user_id
        if sequence_key in self.sequence_patterns:
            for pattern in self.sequence_patterns[sequence_key]:
                # Check if recent accesses match pattern prefix
                if len(recent_accesses) >= 2:
                    for i in range(len(pattern) - len(recent_accesses) + 1):
                        if pattern[i:i+len(recent_accesses)] == recent_accesses:
                            # Predict next items in sequence
                            next_items = pattern[i+len(recent_accesses):i+len(recent_accesses)+3]
                            
                            if next_items:
                                confidence_score = self._calculate_sequence_confidence(
                                    recent_accesses, next_items, pattern
                                )
                                
                                prediction = MemoryPrediction(
                                    prediction_id=f"sequence_{user_id}_{int(time.time())}",
                                    predicted_memory_ids=next_items,
                                    prediction_type=PredictionType.NEXT_MEMORY,
                                    confidence=self._score_to_confidence(confidence_score),
                                    confidence_score=confidence_score,
                                    reasoning="Based on observed access sequences",
                                    context=context,
                                    predicted_at=datetime.now(),
                                    valid_until=datetime.now() + timedelta(hours=2),
                                    evidence={
                                        'sequence_pattern': pattern,
                                        'match_position': i,
                                        'recent_accesses': recent_accesses
                                    }
                                )
                                predictions.append(prediction)
        
        return predictions
    
    def _predict_from_context(self, context: MemoryContext, user_id: str) -> List[MemoryPrediction]:
        """Predict based on context associations"""
        predictions = []
        
        context_key = self._get_context_key(context)
        
        if context_key in self.context_associations:
            # Get memories strongly associated with this context
            associated_memories = sorted(
                self.context_associations[context_key].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            if associated_memories:
                memory_ids = [mid for mid, _ in associated_memories]
                avg_strength = statistics.mean([strength for _, strength in associated_memories])
                
                prediction = MemoryPrediction(
                    prediction_id=f"context_{context_key}_{int(time.time())}",
                    predicted_memory_ids=memory_ids,
                    prediction_type=PredictionType.CONTEXT_MEMORIES,
                    confidence=self._score_to_confidence(avg_strength / 10),  # Normalize
                    confidence_score=min(1.0, avg_strength / 10),
                    reasoning=f"Memories commonly accessed in context: {context_key}",
                    context=context,
                    predicted_at=datetime.now(),
                    valid_until=datetime.now() + timedelta(hours=4),
                    evidence={
                        'context_key': context_key,
                        'association_strength': avg_strength,
                        'memory_count': len(memory_ids)
                    }
                )
                predictions.append(prediction)
        
        return predictions
    
    def _predict_from_temporal_patterns(self, user_id: str, context: MemoryContext) -> List[MemoryPrediction]:
        """Predict based on temporal access patterns"""
        predictions = []
        
        if user_id not in self.temporal_patterns:
            return predictions
        
        now = datetime.now()
        current_hour = now.hour
        current_day = now.weekday()
        
        # Find memories accessed at similar times
        temporal_memories = []
        for access_time, memory_id in self.temporal_patterns[user_id]:
            # Check for similar time patterns (within 1 hour, same day of week)
            if (abs(access_time.hour - current_hour) <= 1 and
                access_time.weekday() == current_day):
                temporal_memories.append(memory_id)
        
        if temporal_memories:
            # Count frequencies
            memory_counts = defaultdict(int)
            for mid in temporal_memories:
                memory_counts[mid] += 1
            
            # Get top memories
            top_memories = sorted(memory_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
            prediction = MemoryPrediction(
                prediction_id=f"temporal_{user_id}_{int(time.time())}",
                predicted_memory_ids=[mid for mid, _ in top_memories],
                prediction_type=PredictionType.TEMPORAL_MEMORIES,
                confidence=PredictionConfidence.MEDIUM,
                confidence_score=0.65,
                reasoning="Memories typically accessed at this time",
                context=context,
                predicted_at=datetime.now(),
                valid_until=datetime.now() + timedelta(hours=3),
                evidence={
                    'time_window': f"{current_hour}:00, {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][current_day]}",
                    'pattern_count': len(temporal_memories),
                    'top_frequencies': dict(top_memories)
                }
            )
            predictions.append(prediction)
        
        return predictions
    
    def _predict_from_workflows(self, user_id: str, context: MemoryContext, 
                               recent_accesses: List[str]) -> List[MemoryPrediction]:
        """Predict based on workflow patterns"""
        predictions = []
        
        if user_id not in self.user_workflows:
            return predictions
        
        # Find workflows that match recent accesses
        for workflow in self.user_workflows[user_id]:
            if len(recent_accesses) >= 2:
                # Check if recent accesses match workflow prefix
                for i in range(len(workflow) - len(recent_accesses) + 1):
                    if workflow[i:i+len(recent_accesses)] == recent_accesses:
                        # Predict next steps in workflow
                        next_steps = workflow[i+len(recent_accesses):i+len(recent_accesses)+2]
                        
                        if next_steps:
                            prediction = MemoryPrediction(
                                prediction_id=f"workflow_{user_id}_{int(time.time())}",
                                predicted_memory_ids=next_steps,
                                prediction_type=PredictionType.WORKFLOW_MEMORIES,
                                confidence=PredictionConfidence.HIGH,
                                confidence_score=0.8,
                                reasoning="Based on observed workflow patterns",
                                context=context,
                                predicted_at=datetime.now(),
                                valid_until=datetime.now() + timedelta(hours=1),
                                evidence={
                                    'workflow_pattern': workflow,
                                    'match_position': i,
                                    'workflow_length': len(workflow)
                                }
                            )
                            predictions.append(prediction)
        
        return predictions
    
    def _predict_from_collaboration(self, user_id: str, context: MemoryContext) -> List[MemoryPrediction]:
        """Predict based on collaborative patterns"""
        predictions = []
        
        # Find similar users based on access patterns
        similar_users = self._find_similar_users(user_id)
        
        if similar_users:
            collaborative_memories = []
            
            for similar_user in similar_users:
                if similar_user in self.temporal_patterns:
                    # Get recent accesses from similar users
                    recent_cutoff = datetime.now() - timedelta(hours=24)
                    recent_accesses = [
                        memory_id for access_time, memory_id in self.temporal_patterns[similar_user]
                        if access_time > recent_cutoff
                    ]
                    collaborative_memories.extend(recent_accesses)
            
            if collaborative_memories:
                # Count frequencies
                memory_counts = defaultdict(int)
                for mid in collaborative_memories:
                    memory_counts[mid] += 1
                
                # Get top memories
                top_memories = sorted(memory_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                
                prediction = MemoryPrediction(
                    prediction_id=f"collaborative_{user_id}_{int(time.time())}",
                    predicted_memory_ids=[mid for mid, _ in top_memories],
                    prediction_type=PredictionType.COLLABORATIVE_MEMORIES,
                    confidence=PredictionConfidence.MEDIUM,
                    confidence_score=0.55,
                    reasoning="Memories recently accessed by similar users",
                    context=context,
                    predicted_at=datetime.now(),
                    valid_until=datetime.now() + timedelta(hours=6),
                    evidence={
                        'similar_users': similar_users,
                        'collaborative_count': len(collaborative_memories),
                        'top_frequencies': dict(top_memories)
                    }
                )
                predictions.append(prediction)
        
        return predictions
    
    def _get_context_key(self, context: MemoryContext) -> str:
        """Generate context key for associations"""
        key_parts = []
        
        if context.project:
            key_parts.append(f"project:{context.project}")
        if context.user:
            key_parts.append(f"user:{context.user}")
        if context.application:
            key_parts.append(f"app:{context.application}")
        if context.environment:
            key_parts.append(f"env:{context.environment}")
        
        return "|".join(key_parts) if key_parts else "default"
    
    def _update_sequence_patterns(self, user_id: str, memory_id: str):
        """Update sequence patterns for user"""
        if user_id not in self.sequence_patterns:
            self.sequence_patterns[user_id] = []
        
        # Add to current sequence
        self.sequence_patterns[user_id].append(memory_id)
        
        # Keep only recent sequence
        if len(self.sequence_patterns[user_id]) > self.sequence_window:
            self.sequence_patterns[user_id] = self.sequence_patterns[user_id][-self.sequence_window:]
    
    def _update_workflow_patterns(self, user_id: str, memory_id: str, context: MemoryContext):
        """Update workflow patterns for user"""
        if user_id not in self.user_workflows:
            self.user_workflows[user_id] = []
        
        # Simple workflow detection: group by session
        if context.session:
            # Find or create workflow for this session
            current_workflow = None
            for workflow in self.user_workflows[user_id]:
                if len(workflow) > 0 and workflow[-1] == memory_id:
                    current_workflow = workflow
                    break
            
            if current_workflow is None:
                current_workflow = []
                self.user_workflows[user_id].append(current_workflow)
            
            if memory_id not in current_workflow:
                current_workflow.append(memory_id)
    
    def _find_related_memories(self, memory_id: str, patterns: List[Tuple[datetime, str]]) -> List[str]:
        """Find memories that commonly appear with given memory"""
        related = []
        
        # Find accesses of the target memory
        target_accesses = [t for t, mid in patterns if mid == memory_id]
        
        # Find other memories accessed around the same time
        for target_time in target_accesses:
            time_window = timedelta(hours=1)
            
            for access_time, other_memory_id in patterns:
                if (other_memory_id != memory_id and
                    abs(access_time - target_time) <= time_window):
                    related.append(other_memory_id)
        
        # Return most frequent related memories
        if related:
            memory_counts = defaultdict(int)
            for mid in related:
                memory_counts[mid] += 1
            
            return [mid for mid, count in 
                   sorted(memory_counts.items(), key=lambda x: x[1], reverse=True)[:3]]
        
        return []
    
    def _find_similar_users(self, user_id: str) -> List[str]:
        """Find users with similar access patterns"""
        if user_id not in self.temporal_patterns:
            return []
        
        user_memories = set(mid for _, mid in self.temporal_patterns[user_id])
        similar_users = []
        
        for other_user, other_patterns in self.temporal_patterns.items():
            if other_user != user_id:
                other_memories = set(mid for _, mid in other_patterns)
                
                # Calculate Jaccard similarity
                intersection = len(user_memories.intersection(other_memories))
                union = len(user_memories.union(other_memories))
                
                if union > 0:
                    similarity = intersection / union
                    if similarity > 0.3:  # Threshold for similarity
                        similar_users.append(other_user)
        
        return similar_users[:3]  # Return top 3 similar users
    
    def _calculate_confidence(self, memory_ids: List[str], context: MemoryContext) -> PredictionConfidence:
        """Calculate confidence level for prediction"""
        # Simple heuristic based on number of memories and context
        if len(memory_ids) >= 3 and context.project:
            return PredictionConfidence.HIGH
        elif len(memory_ids) >= 2:
            return PredictionConfidence.MEDIUM
        else:
            return PredictionConfidence.LOW
    
    def _calculate_confidence_score(self, memory_ids: List[str], 
                                  patterns: List[Tuple[datetime, str]]) -> float:
        """Calculate numerical confidence score"""
        base_score = min(0.9, len(memory_ids) / 5)  # More memories = higher confidence
        
        # Adjust based on pattern frequency
        memory_counts = defaultdict(int)
        for _, mid in patterns:
            if mid in memory_ids:
                memory_counts[mid] += 1
        
        avg_frequency = statistics.mean(memory_counts.values()) if memory_counts else 1
        frequency_bonus = min(0.3, avg_frequency / 10)
        
        return min(1.0, base_score + frequency_bonus)
    
    def _calculate_sequence_confidence(self, recent_accesses: List[str], 
                                     next_items: List[str], pattern: List[str]) -> float:
        """Calculate confidence for sequence prediction"""
        # Base confidence on pattern length and match quality
        match_length = len(recent_accesses)
        pattern_length = len(pattern)
        
        base_score = match_length / max(1, pattern_length)
        
        # Bonus for exact matches
        exact_match_bonus = 0.2 if recent_accesses else 0
        
        return min(1.0, base_score + exact_match_bonus)
    
    def _score_to_confidence(self, score: float) -> PredictionConfidence:
        """Convert numerical score to confidence level"""
        if score >= 0.8:
            return PredictionConfidence.VERY_HIGH
        elif score >= 0.6:
            return PredictionConfidence.HIGH
        elif score >= 0.4:
            return PredictionConfidence.MEDIUM
        elif score >= 0.2:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.VERY_LOW
    
    def _rank_predictions(self, predictions: List[MemoryPrediction]) -> List[MemoryPrediction]:
        """Rank predictions by confidence and relevance"""
        # Sort by confidence score (descending)
        predictions.sort(key=lambda p: p.confidence_score, reverse=True)
        
        # Remove duplicates based on predicted memory IDs
        seen_memories = set()
        unique_predictions = []
        
        for prediction in predictions:
            memory_set = set(prediction.predicted_memory_ids)
            if not memory_set.intersection(seen_memories):
                unique_predictions.append(prediction)
                seen_memories.update(memory_set)
        
        return unique_predictions


class PredictiveLoader:
    """Main predictive loading system"""
    
    def __init__(self, semantic_store, retriever: IntelligentRetriever):
        self.semantic_store = semantic_store
        self.retriever = retriever
        self.predictor = MemoryPredictor()
        self.preload_cache = PreloadCache()
        
        # Tracking
        self.recent_accesses: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10))
        self.predictions: List[MemoryPrediction] = []
        self.prediction_accuracy: Dict[str, float] = {}
        
        # Configuration
        self.preload_enabled = True
        self.max_predictions = 20
        self.prediction_validity_hours = 24
        
        # Performance metrics
        self.metrics = {
            'total_predictions': 0,
            'accurate_predictions': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'preload_time_saved': 0.0
        }
    
    async def record_storage_event(self, memory_item: MemoryItem):
        """Record memory storage event for learning"""
        if memory_item.context and memory_item.context.user:
            await self._trigger_contextual_predictions(memory_item.context)
    
    async def record_retrieval_event(self, query: MemoryQuery, retrieved_memories: List[MemoryItem]):
        """Record retrieval event for learning"""
        if not query.context or not query.context.user:
            return
        
        user_id = query.context.user
        
        # Record access patterns
        for memory in retrieved_memories:
            self.recent_accesses[user_id].append(memory.memory_id)
            self.predictor.learn_from_access(
                memory.memory_id,
                query.context,
                datetime.now(),
                user_id
            )
        
        # Check prediction accuracy
        await self._check_prediction_accuracy(retrieved_memories)
        
        # Generate new predictions
        await self._generate_predictions(query.context, user_id)
        
        # Preload predicted memories
        if self.preload_enabled:
            await self._preload_predicted_memories()
    
    async def record_access_event(self, memory_id: str, context: MemoryContext):
        """Record direct memory access event"""
        if context and context.user:
            user_id = context.user
            self.recent_accesses[user_id].append(memory_id)
            self.predictor.learn_from_access(memory_id, context, datetime.now(), user_id)
    
    async def predict_needs(self, context: MemoryContext) -> Dict[str, Any]:
        """Predict memory needs for given context"""
        if not context.user:
            return {'predictions': [], 'reasoning': 'No user context provided'}
        
        user_id = context.user
        recent_accesses = list(self.recent_accesses[user_id])
        
        # Generate predictions
        predictions = self.predictor.predict_next_memories(context, user_id, recent_accesses)
        
        # Add related memory predictions
        if recent_accesses:
            for recent_id in recent_accesses[-3:]:  # Last 3 accesses
                related_predictions = self.predictor.predict_related_memories(recent_id, context)
                predictions.extend(related_predictions)
        
        # Add seasonal predictions
        seasonal_predictions = self.predictor.predict_seasonal_memories(context, user_id)
        predictions.extend(seasonal_predictions)
        
        # Rank and filter
        predictions = self.predictor._rank_predictions(predictions)[:self.max_predictions]
        
        # Update metrics
        self.metrics['total_predictions'] += len(predictions)
        
        # Store predictions
        self.predictions.extend(predictions)
        
        return {
            'predictions': [p.to_dict() for p in predictions],
            'total_predictions': len(predictions),
            'user_id': user_id,
            'context_features': self._extract_context_features(context),
            'recent_accesses': recent_accesses,
            'reasoning': 'Predictions based on learned patterns and context'
        }
    
    async def analyze_patterns(self, context: Dict[str, Any], time_range: Optional[Tuple[datetime, datetime]] = None,
                             include_patterns: bool = True, include_predictions: bool = True) -> Dict[str, Any]:
        """Analyze memory access patterns and trends"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'patterns': {},
            'predictions': {},
            'metrics': self.metrics.copy()
        }
        
        if include_patterns:
            analysis['patterns'] = await self._analyze_access_patterns(context, time_range)
        
        if include_predictions:
            analysis['predictions'] = await self._analyze_prediction_performance()
        
        # Update cache metrics
        self.preload_cache.update_hit_rate()
        analysis['cache_performance'] = {
            'hit_rate': self.preload_cache.hit_rate,
            'cache_size': len(self.preload_cache.memories),
            'max_size': self.preload_cache.max_size
        }
        
        return analysis
    
    async def get_preloaded_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """Get preloaded memory from cache"""
        memory = self.preload_cache.get_memory(memory_id)
        
        if memory:
            self.metrics['cache_hits'] += 1
            return memory
        else:
            self.metrics['cache_misses'] += 1
            return None
    
    async def _generate_predictions(self, context: MemoryContext, user_id: str):
        """Generate predictions for user context"""
        recent_accesses = list(self.recent_accesses[user_id])
        
        # Generate various types of predictions
        predictions = []
        
        # Next memory predictions
        next_predictions = self.predictor.predict_next_memories(context, user_id, recent_accesses)
        predictions.extend(next_predictions)
        
        # Related memory predictions
        if recent_accesses:
            for memory_id in recent_accesses[-2:]:  # Last 2 accesses
                related_predictions = self.predictor.predict_related_memories(memory_id, context)
                predictions.extend(related_predictions)
        
        # Seasonal predictions
        seasonal_predictions = self.predictor.predict_seasonal_memories(context, user_id)
        predictions.extend(seasonal_predictions)
        
        # Filter and rank
        predictions = self.predictor._rank_predictions(predictions)
        
        # Keep only valid predictions
        valid_predictions = [p for p in predictions if p.is_valid()]
        
        # Update stored predictions
        self.predictions = valid_predictions[:self.max_predictions]
    
    async def _preload_predicted_memories(self):
        """Preload predicted memories into cache"""
        if not self.predictions:
            return
        
        # Get top predictions
        top_predictions = sorted(self.predictions, key=lambda p: p.confidence_score, reverse=True)[:10]
        
        for prediction in top_predictions:
            for memory_id in prediction.predicted_memory_ids:
                # Check if already in cache
                if memory_id not in self.preload_cache.memories:
                    # Retrieve from store
                    memory = await self.semantic_store.retrieve_memory(memory_id)
                    if memory:
                        self.preload_cache.add_memory(memory)
    
    async def _check_prediction_accuracy(self, retrieved_memories: List[MemoryItem]):
        """Check accuracy of previous predictions"""
        retrieved_ids = set(memory.memory_id for memory in retrieved_memories)
        
        for prediction in self.predictions:
            if prediction.is_valid():
                predicted_ids = set(prediction.predicted_memory_ids)
                intersection = predicted_ids.intersection(retrieved_ids)
                
                if intersection:
                    # Calculate accuracy
                    accuracy = len(intersection) / len(predicted_ids)
                    self.prediction_accuracy[prediction.prediction_id] = accuracy
                    
                    if accuracy > 0.5:  # Threshold for "accurate"
                        self.metrics['accurate_predictions'] += 1
    
    async def _trigger_contextual_predictions(self, context: MemoryContext):
        """Trigger predictions based on new memory storage"""
        if context.user:
            await self._generate_predictions(context, context.user)
    
    async def _analyze_access_patterns(self, context: Dict[str, Any], 
                                     time_range: Optional[Tuple[datetime, datetime]]) -> Dict[str, Any]:
        """Analyze access patterns"""
        pattern_analysis = {
            'temporal_patterns': {},
            'context_patterns': {},
            'sequence_patterns': {},
            'workflow_patterns': {}
        }
        
        # Analyze temporal patterns
        for user_id, patterns in self.predictor.temporal_patterns.items():
            if time_range:
                start, end = time_range
                patterns = [(t, mid) for t, mid in patterns if start <= t <= end]
            
            # Hour distribution
            hour_counts = defaultdict(int)
            for access_time, _ in patterns:
                hour_counts[access_time.hour] += 1
            
            # Day distribution
            day_counts = defaultdict(int)
            for access_time, _ in patterns:
                day_counts[access_time.weekday()] += 1
            
            pattern_analysis['temporal_patterns'][user_id] = {
                'hour_distribution': dict(hour_counts),
                'day_distribution': dict(day_counts),
                'total_accesses': len(patterns)
            }
        
        # Analyze context patterns
        for context_key, memory_counts in self.predictor.context_associations.items():
            pattern_analysis['context_patterns'][context_key] = {
                'memory_count': len(memory_counts),
                'total_accesses': sum(memory_counts.values()),
                'top_memories': sorted(memory_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            }
        
        # Analyze sequence patterns
        for user_id, sequences in self.predictor.sequence_patterns.items():
            pattern_analysis['sequence_patterns'][user_id] = {
                'sequence_length': len(sequences),
                'unique_memories': len(set(sequences)),
                'recent_sequence': sequences[-5:] if sequences else []
            }
        
        return pattern_analysis
    
    async def _analyze_prediction_performance(self) -> Dict[str, Any]:
        """Analyze prediction performance"""
        performance = {
            'total_predictions': self.metrics['total_predictions'],
            'accurate_predictions': self.metrics['accurate_predictions'],
            'accuracy_rate': 0.0,
            'prediction_types': defaultdict(int),
            'confidence_distribution': defaultdict(int),
            'avg_confidence': 0.0
        }
        
        if self.metrics['total_predictions'] > 0:
            performance['accuracy_rate'] = (
                self.metrics['accurate_predictions'] / self.metrics['total_predictions']
            )
        
        # Analyze prediction types and confidence
        if self.predictions:
            confidences = []
            for prediction in self.predictions:
                performance['prediction_types'][prediction.prediction_type.value] += 1
                performance['confidence_distribution'][prediction.confidence.value] += 1
                confidences.append(prediction.confidence_score)
            
            if confidences:
                performance['avg_confidence'] = statistics.mean(confidences)
        
        return performance
    
    def _extract_context_features(self, context: MemoryContext) -> Dict[str, Any]:
        """Extract features from context for analysis"""
        features = {
            'has_project': context.project is not None,
            'has_user': context.user is not None,
            'has_session': context.session is not None,
            'has_application': context.application is not None,
            'has_environment': context.environment is not None,
            'timestamp': datetime.now().isoformat()
        }
        
        if context.project:
            features['project'] = context.project
        if context.user:
            features['user'] = context.user
        if context.application:
            features['application'] = context.application
        if context.environment:
            features['environment'] = context.environment
        
        return features


# Example usage and testing
if __name__ == "__main__":
    async def test_predictive_loading():
        from .semantic_storage import SemanticMemoryStore
        from .intelligent_retrieval import IntelligentRetriever
        
        # Create components
        store = SemanticMemoryStore(data_dir="./test_memory_predictive")
        await store.initialize()
        
        retriever = IntelligentRetriever(store)
        predictor = PredictiveLoader(store, retriever)
        
        # Create test memories
        memories = [
            MemoryItem(
                content="Python function for data processing",
                memory_type=MemoryType.CODE,
                context=MemoryContext(project="data_project", user="alice"),
                tags=["python", "data", "processing"],
                importance=0.8
            ),
            MemoryItem(
                content="Database query for user analytics",
                memory_type=MemoryType.CODE,
                context=MemoryContext(project="data_project", user="alice"),
                tags=["sql", "analytics", "users"],
                importance=0.7
            ),
            MemoryItem(
                content="Machine learning model training script",
                memory_type=MemoryType.CODE,
                context=MemoryContext(project="ml_project", user="alice"),
                tags=["ml", "training", "model"],
                importance=0.9
            )
        ]
        
        # Store memories
        for memory in memories:
            await store.store_memory(memory)
        
        # Simulate access patterns
        context = MemoryContext(project="data_project", user="alice")
        
        # Record accesses
        for memory in memories[:2]:  # Access first two memories
            await predictor.record_access_event(memory.memory_id, context)
        
        # Generate predictions
        predictions = await predictor.predict_needs(context)
        
        print(f"Generated {len(predictions['predictions'])} predictions")
        for pred in predictions['predictions']:
            print(f"- {pred['prediction_type']}: {pred['confidence']} ({pred['confidence_score']:.2f})")
        
        # Analyze patterns
        analysis = await predictor.analyze_patterns(
            context={'project': 'data_project', 'user': 'alice'},
            include_patterns=True,
            include_predictions=True
        )
        
        print(f"\nPattern analysis: {len(analysis['patterns'])} pattern types")
        print(f"Prediction performance: {analysis['predictions']['accuracy_rate']:.2f}")
    
    asyncio.run(test_predictive_loading())