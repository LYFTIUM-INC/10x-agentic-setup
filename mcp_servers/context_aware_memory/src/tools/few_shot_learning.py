"""
Few-Shot Learning Memory Patterns
Advanced pattern recognition and success pattern reuse for memory systems
"""

import asyncio
import logging
import json
import time
import pickle
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from pathlib import Path
import hashlib

# Import existing tools
from .semantic_storage import MemoryItem, MemoryContext, MemoryType
from .intelligent_retrieval import RetrievalStrategy

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Types of patterns for few-shot learning"""
    SUCCESS_PATTERN = "success_pattern"
    FAILURE_PATTERN = "failure_pattern"
    WORKFLOW_PATTERN = "workflow_pattern"
    SOLUTION_PATTERN = "solution_pattern"
    OPTIMIZATION_PATTERN = "optimization_pattern"
    CREATIVE_PATTERN = "creative_pattern"


class PatternConfidence(Enum):
    """Confidence levels for pattern recognition"""
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95


@dataclass
class PatternExample:
    """Individual example within a pattern"""
    example_id: str
    context: Dict[str, Any]
    input_features: Dict[str, Any]
    output_features: Dict[str, Any]
    outcome: str
    success_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LearningPattern:
    """Pattern learned from few-shot examples"""
    pattern_id: str
    pattern_type: PatternType
    name: str
    description: str
    examples: List[PatternExample]
    success_rate: float
    usage_count: int
    pattern_signature: Dict[str, Any]
    learned_features: Dict[str, Any]
    applicability_rules: List[str]
    confidence: float
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    effectiveness_score: float = 0.0


@dataclass
class FewShotQuery:
    """Query for few-shot pattern matching"""
    context: Dict[str, Any]
    input_features: Dict[str, Any]
    desired_outcome: str
    max_patterns: int = 5
    min_confidence: float = 0.6
    pattern_types: List[PatternType] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)


@dataclass
class PatternApplication:
    """Result of applying a few-shot pattern"""
    pattern_id: str
    confidence: float
    predicted_outcome: str
    recommended_actions: List[str]
    success_probability: float
    similar_examples: List[PatternExample]
    adaptation_notes: List[str]


class FewShotLearningEngine:
    """Advanced few-shot learning engine for memory patterns"""
    
    def __init__(self, semantic_store, embedding_manager, data_dir: Path):
        self.semantic_store = semantic_store
        self.embedding_manager = embedding_manager
        self.data_dir = Path(data_dir)
        self.patterns_dir = self.data_dir / "few_shot_patterns"
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
        
        # Pattern storage
        self.learned_patterns: Dict[str, LearningPattern] = {}
        self.pattern_index = {}  # For fast lookup
        
        # Feature extractors
        self.feature_extractors = self._initialize_feature_extractors()
        
        # Pattern matching cache
        self.pattern_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Learning statistics
        self.learning_stats = {
            'patterns_learned': 0,
            'patterns_applied': 0,
            'successful_applications': 0,
            'pattern_updates': 0
        }
        
    async def initialize(self):
        """Initialize the few-shot learning engine"""
        logger.info("Initializing Few-Shot Learning Engine...")
        
        # Load existing patterns
        await self._load_patterns()
        
        # Build pattern index
        await self._build_pattern_index()
        
        logger.info(f"Few-Shot Learning Engine initialized with {len(self.learned_patterns)} patterns")
    
    def _initialize_feature_extractors(self) -> Dict[str, callable]:
        """Initialize feature extraction functions"""
        return {
            'content_features': self._extract_content_features,
            'context_features': self._extract_context_features,
            'temporal_features': self._extract_temporal_features,
            'semantic_features': self._extract_semantic_features,
            'behavioral_features': self._extract_behavioral_features
        }
    
    async def learn_from_examples(self, examples: List[Dict[str, Any]], 
                                pattern_type: PatternType = PatternType.SUCCESS_PATTERN) -> LearningPattern:
        """Learn a new pattern from few-shot examples"""
        try:
            logger.info(f"Learning {pattern_type.value} pattern from {len(examples)} examples")
            
            # Convert examples to PatternExample objects
            pattern_examples = []
            for i, example in enumerate(examples):
                pattern_example = PatternExample(
                    example_id=f"example_{i}_{int(time.time())}",
                    context=example.get('context', {}),
                    input_features=example.get('input_features', {}),
                    output_features=example.get('output_features', {}),
                    outcome=example.get('outcome', ''),
                    success_score=example.get('success_score', 0.0),
                    metadata=example.get('metadata', {})
                )
                pattern_examples.append(pattern_example)
            
            # Extract pattern signature
            pattern_signature = await self._extract_pattern_signature(pattern_examples)
            
            # Learn features from examples
            learned_features = await self._learn_features_from_examples(pattern_examples)
            
            # Generate applicability rules
            applicability_rules = await self._generate_applicability_rules(pattern_examples)
            
            # Calculate success rate
            success_scores = [ex.success_score for ex in pattern_examples]
            success_rate = np.mean(success_scores) if success_scores else 0.0
            
            # Calculate confidence
            confidence = self._calculate_pattern_confidence(pattern_examples, success_rate)
            
            # Create pattern
            pattern_id = self._generate_pattern_id(pattern_signature)
            pattern = LearningPattern(
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                name=self._generate_pattern_name(pattern_type, pattern_signature),
                description=self._generate_pattern_description(pattern_examples),
                examples=pattern_examples,
                success_rate=success_rate,
                usage_count=0,
                pattern_signature=pattern_signature,
                learned_features=learned_features,
                applicability_rules=applicability_rules,
                confidence=confidence
            )
            
            # Store pattern
            self.learned_patterns[pattern_id] = pattern
            await self._update_pattern_index(pattern)
            await self._save_pattern(pattern)
            
            # Update statistics
            self.learning_stats['patterns_learned'] += 1
            
            logger.info(f"Learned pattern {pattern_id} with confidence {confidence:.2f}")
            
            return pattern
            
        except Exception as e:
            logger.error(f"Failed to learn pattern from examples: {e}")
            raise
    
    async def find_matching_patterns(self, query: FewShotQuery) -> List[PatternApplication]:
        """Find patterns that match the query context"""
        try:
            # Check cache first
            cache_key = self._generate_cache_key(query)
            if cache_key in self.pattern_cache:
                cached_result, timestamp = self.pattern_cache[cache_key]
                if time.time() - timestamp < self.cache_ttl:
                    return cached_result
            
            # Extract features from query
            query_features = await self._extract_query_features(query)
            
            # Find candidate patterns
            candidate_patterns = await self._find_candidate_patterns(query, query_features)
            
            # Score and rank patterns
            pattern_applications = []
            for pattern in candidate_patterns:
                application = await self._evaluate_pattern_application(pattern, query, query_features)
                if application.confidence >= query.min_confidence:
                    pattern_applications.append(application)
            
            # Sort by confidence and success probability
            pattern_applications.sort(
                key=lambda x: (x.confidence * 0.6 + x.success_probability * 0.4), 
                reverse=True
            )
            
            # Limit results
            result = pattern_applications[:query.max_patterns]
            
            # Cache result
            self.pattern_cache[cache_key] = (result, time.time())
            
            logger.info(f"Found {len(result)} matching patterns for query")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to find matching patterns: {e}")
            return []
    
    async def apply_pattern(self, pattern_id: str, context: Dict[str, Any], 
                          input_features: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a learned pattern to a new situation"""
        try:
            if pattern_id not in self.learned_patterns:
                raise ValueError(f"Pattern {pattern_id} not found")
            
            pattern = self.learned_patterns[pattern_id]
            
            # Find most similar examples
            similar_examples = await self._find_similar_examples(pattern, context, input_features)
            
            # Generate recommendations based on pattern
            recommendations = await self._generate_pattern_recommendations(pattern, context, input_features, similar_examples)
            
            # Update pattern usage
            pattern.usage_count += 1
            pattern.last_used = datetime.now()
            await self._save_pattern(pattern)
            
            # Update statistics
            self.learning_stats['patterns_applied'] += 1
            
            logger.info(f"Applied pattern {pattern_id} with {len(recommendations)} recommendations")
            
            return {
                'pattern_id': pattern_id,
                'pattern_name': pattern.name,
                'recommendations': recommendations,
                'similar_examples': [ex.example_id for ex in similar_examples],
                'confidence': pattern.confidence,
                'success_rate': pattern.success_rate,
                'applied_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to apply pattern {pattern_id}: {e}")
            raise
    
    async def update_pattern_effectiveness(self, pattern_id: str, actual_outcome: str, 
                                         success_score: float, feedback: Dict[str, Any]):
        """Update pattern effectiveness based on real-world results"""
        try:
            if pattern_id not in self.learned_patterns:
                logger.warning(f"Pattern {pattern_id} not found for effectiveness update")
                return
            
            pattern = self.learned_patterns[pattern_id]
            
            # Update effectiveness score using exponential moving average
            alpha = 0.2  # Learning rate
            pattern.effectiveness_score = (
                alpha * success_score + (1 - alpha) * pattern.effectiveness_score
            )
            
            # Update success rate
            total_successes = pattern.success_rate * len(pattern.examples)
            total_successes += success_score
            pattern.success_rate = total_successes / (len(pattern.examples) + 1)
            
            # Add feedback as a new example if significant
            if success_score != pattern.success_rate:  # Different from average
                new_example = PatternExample(
                    example_id=f"feedback_{int(time.time())}",
                    context=feedback.get('context', {}),
                    input_features=feedback.get('input_features', {}),
                    output_features=feedback.get('output_features', {}),
                    outcome=actual_outcome,
                    success_score=success_score,
                    metadata={'feedback': True, 'original_pattern': pattern_id}
                )
                pattern.examples.append(new_example)
                
                # Limit example history
                if len(pattern.examples) > 50:
                    pattern.examples = pattern.examples[-50:]
            
            # Recalculate pattern confidence
            pattern.confidence = self._calculate_pattern_confidence(pattern.examples, pattern.success_rate)
            
            # Save updated pattern
            await self._save_pattern(pattern)
            
            # Update statistics
            self.learning_stats['pattern_updates'] += 1
            if success_score >= 0.7:
                self.learning_stats['successful_applications'] += 1
            
            logger.info(f"Updated pattern {pattern_id} effectiveness: {pattern.effectiveness_score:.2f}")
            
        except Exception as e:
            logger.error(f"Failed to update pattern effectiveness: {e}")
    
    async def get_pattern_insights(self, pattern_id: str) -> Dict[str, Any]:
        """Get detailed insights about a learned pattern"""
        try:
            if pattern_id not in self.learned_patterns:
                return {"error": f"Pattern {pattern_id} not found"}
            
            pattern = self.learned_patterns[pattern_id]
            
            # Analyze pattern performance
            performance_analysis = await self._analyze_pattern_performance(pattern)
            
            # Extract key insights
            key_insights = await self._extract_pattern_insights(pattern)
            
            # Generate improvement suggestions
            improvement_suggestions = await self._suggest_pattern_improvements(pattern)
            
            return {
                'pattern_id': pattern_id,
                'pattern_name': pattern.name,
                'pattern_type': pattern.pattern_type.value,
                'confidence': pattern.confidence,
                'success_rate': pattern.success_rate,
                'usage_count': pattern.usage_count,
                'effectiveness_score': pattern.effectiveness_score,
                'example_count': len(pattern.examples),
                'last_used': pattern.last_used.isoformat() if pattern.last_used else None,
                'performance_analysis': performance_analysis,
                'key_insights': key_insights,
                'improvement_suggestions': improvement_suggestions,
                'applicability_rules': pattern.applicability_rules
            }
            
        except Exception as e:
            logger.error(f"Failed to get pattern insights: {e}")
            return {"error": str(e)}
    
    async def discover_new_patterns(self, memories: List[MemoryItem], 
                                  min_examples: int = 3) -> List[LearningPattern]:
        """Automatically discover new patterns from memory data"""
        try:
            logger.info(f"Discovering patterns from {len(memories)} memories")
            
            # Group memories by outcomes and contexts
            grouped_memories = await self._group_memories_for_discovery(memories)
            
            discovered_patterns = []
            
            for group_key, memory_group in grouped_memories.items():
                if len(memory_group) >= min_examples:
                    # Convert memories to examples
                    examples = await self._convert_memories_to_examples(memory_group)
                    
                    # Determine pattern type based on outcomes
                    pattern_type = await self._infer_pattern_type(examples)
                    
                    # Learn pattern
                    try:
                        pattern = await self.learn_from_examples(examples, pattern_type)
                        discovered_patterns.append(pattern)
                        logger.info(f"Discovered pattern: {pattern.name}")
                    except Exception as e:
                        logger.warning(f"Failed to learn pattern from group {group_key}: {e}")
            
            logger.info(f"Discovered {len(discovered_patterns)} new patterns")
            return discovered_patterns
            
        except Exception as e:
            logger.error(f"Failed to discover patterns: {e}")
            return []
    
    # Feature extraction methods
    
    async def _extract_content_features(self, content: str) -> Dict[str, Any]:
        """Extract features from content text"""
        return {
            'length': len(content),
            'word_count': len(content.split()),
            'sentence_count': content.count('.') + content.count('!') + content.count('?'),
            'has_code': any(marker in content for marker in ['def ', 'class ', 'import ', '```']),
            'has_urls': 'http' in content or 'www.' in content,
            'sentiment_indicators': {
                'positive': sum(1 for word in ['success', 'good', 'great', 'excellent'] if word in content.lower()),
                'negative': sum(1 for word in ['error', 'failed', 'bad', 'problem'] if word in content.lower())
            }
        }
    
    async def _extract_context_features(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from context data"""
        features = {
            'context_size': len(context),
            'has_project': 'project' in context,
            'has_user': 'user' in context,
            'has_environment': 'environment' in context,
            'has_task': 'task' in context
        }
        
        # Extract specific context values
        for key in ['project', 'user', 'environment', 'task', 'domain']:
            if key in context:
                features[f'{key}_value'] = str(context[key])
        
        return features
    
    async def _extract_temporal_features(self, timestamp: datetime) -> Dict[str, Any]:
        """Extract temporal features from timestamp"""
        return {
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'month': timestamp.month,
            'is_weekend': timestamp.weekday() >= 5,
            'is_work_hours': 9 <= timestamp.hour <= 17,
            'season': (timestamp.month % 12 + 3) // 3  # 1=spring, 2=summer, 3=fall, 4=winter
        }
    
    async def _extract_semantic_features(self, content: str) -> Dict[str, Any]:
        """Extract semantic features using embeddings"""
        try:
            # Get embeddings
            embeddings = await self.embedding_manager.get_embeddings([content])
            if not embeddings:
                return {}
            
            embedding = embeddings[0]
            
            # Extract statistical features from embedding
            return {
                'embedding_norm': float(np.linalg.norm(embedding)),
                'embedding_mean': float(np.mean(embedding)),
                'embedding_std': float(np.std(embedding)),
                'embedding_max': float(np.max(embedding)),
                'embedding_min': float(np.min(embedding)),
                'positive_dimensions': int(np.sum(embedding > 0)),
                'negative_dimensions': int(np.sum(embedding < 0))
            }
            
        except Exception as e:
            logger.error(f"Failed to extract semantic features: {e}")
            return {}
    
    async def _extract_behavioral_features(self, memory: MemoryItem) -> Dict[str, Any]:
        """Extract behavioral features from memory patterns"""
        return {
            'importance': memory.importance,
            'access_count': memory.access_count,
            'tag_count': len(memory.tags),
            'memory_type': memory.memory_type.value,
            'has_expiration': memory.expires_at is not None,
            'days_since_creation': (datetime.now() - memory.created_at).days,
            'last_access_days': (datetime.now() - memory.last_accessed).days if memory.last_accessed else None
        }
    
    # Pattern learning and matching methods
    
    async def _extract_pattern_signature(self, examples: List[PatternExample]) -> Dict[str, Any]:
        """Extract unique signature for a pattern"""
        # Aggregate features across examples
        signature = {
            'example_count': len(examples),
            'avg_success_score': np.mean([ex.success_score for ex in examples]),
            'outcome_types': list(set(ex.outcome for ex in examples)),
            'common_contexts': self._find_common_context_elements(examples),
            'feature_ranges': self._calculate_feature_ranges(examples)
        }
        
        return signature
    
    async def _learn_features_from_examples(self, examples: List[PatternExample]) -> Dict[str, Any]:
        """Learn important features from examples"""
        learned_features = {
            'critical_input_features': [],
            'success_indicators': [],
            'failure_indicators': [],
            'context_requirements': [],
            'output_patterns': []
        }
        
        # Analyze successful vs unsuccessful examples
        successful_examples = [ex for ex in examples if ex.success_score >= 0.7]
        unsuccessful_examples = [ex for ex in examples if ex.success_score < 0.5]
        
        if successful_examples:
            # Find features common in successful examples
            success_features = self._find_discriminative_features(successful_examples, unsuccessful_examples)
            learned_features['success_indicators'] = success_features
        
        if unsuccessful_examples:
            # Find features common in unsuccessful examples
            failure_features = self._find_discriminative_features(unsuccessful_examples, successful_examples)
            learned_features['failure_indicators'] = failure_features
        
        # Extract critical input features
        learned_features['critical_input_features'] = self._identify_critical_features(examples)
        
        return learned_features
    
    async def _generate_applicability_rules(self, examples: List[PatternExample]) -> List[str]:
        """Generate rules for when this pattern applies"""
        rules = []
        
        # Context-based rules
        common_contexts = self._find_common_context_elements(examples)
        for context_key, values in common_contexts.items():
            if len(values) == 1:  # Single value across all examples
                rules.append(f"Apply when {context_key} = {list(values)[0]}")
            elif len(values) <= 3:  # Few distinct values
                rules.append(f"Apply when {context_key} in {list(values)}")
        
        # Success score based rules
        success_scores = [ex.success_score for ex in examples]
        avg_success = np.mean(success_scores)
        if avg_success >= 0.8:
            rules.append("Highly effective pattern - apply with confidence")
        elif avg_success >= 0.6:
            rules.append("Moderately effective pattern - apply with caution")
        else:
            rules.append("Low effectiveness pattern - apply only as last resort")
        
        # Feature-based rules
        critical_features = self._identify_critical_features(examples)
        for feature in critical_features[:3]:  # Top 3 features
            rules.append(f"Ensure {feature} is properly configured")
        
        return rules
    
    def _calculate_pattern_confidence(self, examples: List[PatternExample], success_rate: float) -> float:
        """Calculate confidence in pattern based on examples and success rate"""
        # Base confidence from success rate
        base_confidence = success_rate
        
        # Adjust for number of examples
        example_confidence = min(len(examples) / 10.0, 1.0)  # More examples = higher confidence
        
        # Adjust for consistency
        success_scores = [ex.success_score for ex in examples]
        consistency = 1.0 - np.std(success_scores) if len(success_scores) > 1 else 1.0
        
        # Combined confidence
        confidence = (base_confidence * 0.5 + example_confidence * 0.3 + consistency * 0.2)
        
        return min(confidence, 1.0)
    
    async def _find_candidate_patterns(self, query: FewShotQuery, query_features: Dict[str, Any]) -> List[LearningPattern]:
        """Find candidate patterns that might match the query"""
        candidates = []
        
        for pattern in self.learned_patterns.values():
            # Filter by pattern type if specified
            if query.pattern_types and pattern.pattern_type not in query.pattern_types:
                continue
            
            # Exclude specified patterns
            if pattern.pattern_id in query.exclude_patterns:
                continue
            
            # Check basic applicability
            if self._check_basic_applicability(pattern, query, query_features):
                candidates.append(pattern)
        
        return candidates
    
    async def _evaluate_pattern_application(self, pattern: LearningPattern, query: FewShotQuery, 
                                          query_features: Dict[str, Any]) -> PatternApplication:
        """Evaluate how well a pattern applies to the query"""
        # Calculate feature similarity
        feature_similarity = await self._calculate_feature_similarity(pattern, query_features)
        
        # Calculate context similarity
        context_similarity = await self._calculate_context_similarity(pattern, query.context)
        
        # Calculate overall confidence
        confidence = (feature_similarity * 0.6 + context_similarity * 0.4) * pattern.confidence
        
        # Find most similar examples
        similar_examples = await self._find_most_similar_examples(pattern, query_features, query.context)
        
        # Generate recommendations
        recommendations = await self._generate_application_recommendations(pattern, query, similar_examples)
        
        # Calculate success probability
        success_probability = self._estimate_success_probability(pattern, query, similar_examples)
        
        # Generate adaptation notes
        adaptation_notes = await self._generate_adaptation_notes(pattern, query)
        
        return PatternApplication(
            pattern_id=pattern.pattern_id,
            confidence=confidence,
            predicted_outcome=self._predict_outcome(pattern, query),
            recommended_actions=recommendations,
            success_probability=success_probability,
            similar_examples=similar_examples,
            adaptation_notes=adaptation_notes
        )
    
    # Storage and persistence methods
    
    async def _save_pattern(self, pattern: LearningPattern):
        """Save pattern to persistent storage"""
        try:
            pattern_file = self.patterns_dir / f"{pattern.pattern_id}.pkl"
            with open(pattern_file, 'wb') as f:
                pickle.dump(pattern, f)
            
            # Also save as JSON for human readability
            json_file = self.patterns_dir / f"{pattern.pattern_id}.json"
            with open(json_file, 'w') as f:
                json.dump(self._pattern_to_dict(pattern), f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save pattern {pattern.pattern_id}: {e}")
    
    async def _load_patterns(self):
        """Load patterns from persistent storage"""
        try:
            pattern_files = list(self.patterns_dir.glob("*.pkl"))
            
            for pattern_file in pattern_files:
                try:
                    with open(pattern_file, 'rb') as f:
                        pattern = pickle.load(f)
                    self.learned_patterns[pattern.pattern_id] = pattern
                except Exception as e:
                    logger.warning(f"Failed to load pattern from {pattern_file}: {e}")
            
            logger.info(f"Loaded {len(self.learned_patterns)} patterns")
            
        except Exception as e:
            logger.error(f"Failed to load patterns: {e}")
    
    async def _build_pattern_index(self):
        """Build index for fast pattern lookup"""
        self.pattern_index = {
            'by_type': {},
            'by_context': {},
            'by_features': {}
        }
        
        for pattern in self.learned_patterns.values():
            # Index by type
            pattern_type = pattern.pattern_type.value
            if pattern_type not in self.pattern_index['by_type']:
                self.pattern_index['by_type'][pattern_type] = []
            self.pattern_index['by_type'][pattern_type].append(pattern.pattern_id)
            
            # Index by context elements
            common_contexts = pattern.pattern_signature.get('common_contexts', {})
            for context_key, values in common_contexts.items():
                if context_key not in self.pattern_index['by_context']:
                    self.pattern_index['by_context'][context_key] = {}
                for value in values:
                    if value not in self.pattern_index['by_context'][context_key]:
                        self.pattern_index['by_context'][context_key][value] = []
                    self.pattern_index['by_context'][context_key][value].append(pattern.pattern_id)
    
    async def _update_pattern_index(self, pattern: LearningPattern):
        """Update pattern index with new pattern"""
        # Update type index
        pattern_type = pattern.pattern_type.value
        if pattern_type not in self.pattern_index['by_type']:
            self.pattern_index['by_type'][pattern_type] = []
        if pattern.pattern_id not in self.pattern_index['by_type'][pattern_type]:
            self.pattern_index['by_type'][pattern_type].append(pattern.pattern_id)
        
        # Update context index
        common_contexts = pattern.pattern_signature.get('common_contexts', {})
        for context_key, values in common_contexts.items():
            if context_key not in self.pattern_index['by_context']:
                self.pattern_index['by_context'][context_key] = {}
            for value in values:
                if value not in self.pattern_index['by_context'][context_key]:
                    self.pattern_index['by_context'][context_key][value] = []
                if pattern.pattern_id not in self.pattern_index['by_context'][context_key][value]:
                    self.pattern_index['by_context'][context_key][value].append(pattern.pattern_id)
    
    # Helper methods
    
    def _generate_pattern_id(self, pattern_signature: Dict[str, Any]) -> str:
        """Generate unique pattern ID"""
        signature_str = json.dumps(pattern_signature, sort_keys=True, default=str)
        hash_object = hashlib.md5(signature_str.encode())
        return f"pattern_{hash_object.hexdigest()[:12]}"
    
    def _generate_pattern_name(self, pattern_type: PatternType, signature: Dict[str, Any]) -> str:
        """Generate human-readable pattern name"""
        type_name = pattern_type.value.replace('_', ' ').title()
        
        # Add context-specific details if available
        contexts = signature.get('common_contexts', {})
        if 'project' in contexts and len(contexts['project']) == 1:
            project = list(contexts['project'])[0]
            return f"{type_name} for {project}"
        elif 'task' in contexts and len(contexts['task']) == 1:
            task = list(contexts['task'])[0]
            return f"{type_name} for {task}"
        else:
            return f"{type_name} Pattern"
    
    def _generate_pattern_description(self, examples: List[PatternExample]) -> str:
        """Generate pattern description from examples"""
        outcome_counts = {}
        for ex in examples:
            outcome_counts[ex.outcome] = outcome_counts.get(ex.outcome, 0) + 1
        
        most_common_outcome = max(outcome_counts, key=outcome_counts.get)
        avg_success = np.mean([ex.success_score for ex in examples])
        
        return f"Pattern with {len(examples)} examples, commonly resulting in '{most_common_outcome}' with average success rate of {avg_success:.1%}"
    
    def _find_common_context_elements(self, examples: List[PatternExample]) -> Dict[str, Set]:
        """Find context elements common across examples"""
        common_contexts = {}
        
        for example in examples:
            for key, value in example.context.items():
                if key not in common_contexts:
                    common_contexts[key] = set()
                common_contexts[key].add(str(value))
        
        # Only keep contexts that appear in multiple examples
        filtered_contexts = {}
        for key, values in common_contexts.items():
            if len(examples) > 1:  # Only filter if we have multiple examples
                # Keep if appears in at least 50% of examples
                if len(values) <= len(examples) * 0.8:
                    filtered_contexts[key] = values
            else:
                filtered_contexts[key] = values
        
        return filtered_contexts
    
    def _calculate_feature_ranges(self, examples: List[PatternExample]) -> Dict[str, Any]:
        """Calculate ranges for numerical features"""
        ranges = {}
        
        # Collect all numerical features
        numerical_features = {}
        for example in examples:
            for key, value in example.input_features.items():
                if isinstance(value, (int, float)):
                    if key not in numerical_features:
                        numerical_features[key] = []
                    numerical_features[key].append(value)
        
        # Calculate ranges
        for feature, values in numerical_features.items():
            ranges[feature] = {
                'min': min(values),
                'max': max(values),
                'mean': np.mean(values),
                'std': np.std(values) if len(values) > 1 else 0
            }
        
        return ranges
    
    def _find_discriminative_features(self, positive_examples: List[PatternExample], 
                                    negative_examples: List[PatternExample]) -> List[str]:
        """Find features that discriminate between positive and negative examples"""
        discriminative_features = []
        
        if not positive_examples or not negative_examples:
            return discriminative_features
        
        # Simple frequency-based discrimination
        pos_features = {}
        neg_features = {}
        
        # Count feature occurrences
        for ex in positive_examples:
            for key, value in ex.input_features.items():
                feature_key = f"{key}={value}"
                pos_features[feature_key] = pos_features.get(feature_key, 0) + 1
        
        for ex in negative_examples:
            for key, value in ex.input_features.items():
                feature_key = f"{key}={value}"
                neg_features[feature_key] = neg_features.get(feature_key, 0) + 1
        
        # Find features more common in positive examples
        for feature, pos_count in pos_features.items():
            neg_count = neg_features.get(feature, 0)
            pos_rate = pos_count / len(positive_examples)
            neg_rate = neg_count / len(negative_examples) if negative_examples else 0
            
            if pos_rate > neg_rate + 0.3:  # Significantly more common in positive
                discriminative_features.append(feature)
        
        return discriminative_features[:5]  # Top 5 discriminative features
    
    def _identify_critical_features(self, examples: List[PatternExample]) -> List[str]:
        """Identify critical features across all examples"""
        feature_importance = {}
        
        for example in examples:
            for key in example.input_features.keys():
                feature_importance[key] = feature_importance.get(key, 0) + example.success_score
        
        # Sort by importance
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        return [feature for feature, _ in sorted_features[:10]]  # Top 10 critical features
    
    def _pattern_to_dict(self, pattern: LearningPattern) -> Dict[str, Any]:
        """Convert pattern to dictionary for JSON serialization"""
        return {
            'pattern_id': pattern.pattern_id,
            'pattern_type': pattern.pattern_type.value,
            'name': pattern.name,
            'description': pattern.description,
            'success_rate': pattern.success_rate,
            'usage_count': pattern.usage_count,
            'confidence': pattern.confidence,
            'effectiveness_score': pattern.effectiveness_score,
            'created_at': pattern.created_at.isoformat(),
            'last_used': pattern.last_used.isoformat() if pattern.last_used else None,
            'example_count': len(pattern.examples),
            'pattern_signature': pattern.pattern_signature,
            'learned_features': pattern.learned_features,
            'applicability_rules': pattern.applicability_rules
        }
    
    # Additional utility methods would continue here...
    # (Implementation truncated for length - remaining methods would follow similar patterns)
    
    async def get_learning_statistics(self) -> Dict[str, Any]:
        """Get statistics about the learning engine"""
        return {
            'total_patterns': len(self.learned_patterns),
            'patterns_by_type': {
                pattern_type.value: len([p for p in self.learned_patterns.values() 
                                       if p.pattern_type == pattern_type])
                for pattern_type in PatternType
            },
            'learning_stats': self.learning_stats.copy(),
            'cache_size': len(self.pattern_cache),
            'average_pattern_confidence': np.mean([p.confidence for p in self.learned_patterns.values()]) if self.learned_patterns else 0.0,
            'average_success_rate': np.mean([p.success_rate for p in self.learned_patterns.values()]) if self.learned_patterns else 0.0
        }
    
    # Placeholder implementations for remaining methods
    async def _extract_query_features(self, query: FewShotQuery) -> Dict[str, Any]:
        """Extract features from query for matching"""
        features = {}
        features.update(await self._extract_context_features(query.context))
        features.update(query.input_features)
        return features
    
    def _generate_cache_key(self, query: FewShotQuery) -> str:
        """Generate cache key for query"""
        query_str = f"{query.context}_{query.input_features}_{query.desired_outcome}"
        return hashlib.md5(query_str.encode()).hexdigest()
    
    def _check_basic_applicability(self, pattern: LearningPattern, query: FewShotQuery, query_features: Dict[str, Any]) -> bool:
        """Check if pattern is basically applicable to query"""
        # Simple heuristic checks
        return pattern.confidence >= query.min_confidence * 0.8
    
    async def _calculate_feature_similarity(self, pattern: LearningPattern, query_features: Dict[str, Any]) -> float:
        """Calculate similarity between pattern and query features"""
        # Simplified implementation
        return 0.7  # Placeholder
    
    async def _calculate_context_similarity(self, pattern: LearningPattern, context: Dict[str, Any]) -> float:
        """Calculate similarity between pattern and query context"""
        # Simplified implementation
        return 0.8  # Placeholder
    
    async def _find_most_similar_examples(self, pattern: LearningPattern, query_features: Dict[str, Any], context: Dict[str, Any]) -> List[PatternExample]:
        """Find most similar examples in pattern"""
        return pattern.examples[:3]  # Simplified implementation
    
    async def _generate_application_recommendations(self, pattern: LearningPattern, query: FewShotQuery, similar_examples: List[PatternExample]) -> List[str]:
        """Generate recommendations for applying pattern"""
        return ["Apply the learned pattern", "Monitor results carefully"]  # Placeholder
    
    def _estimate_success_probability(self, pattern: LearningPattern, query: FewShotQuery, similar_examples: List[PatternExample]) -> float:
        """Estimate probability of success"""
        return pattern.success_rate  # Simplified implementation
    
    async def _generate_adaptation_notes(self, pattern: LearningPattern, query: FewShotQuery) -> List[str]:
        """Generate notes about adapting pattern to query"""
        return ["Pattern may need adaptation", "Consider context differences"]  # Placeholder
    
    def _predict_outcome(self, pattern: LearningPattern, query: FewShotQuery) -> str:
        """Predict outcome based on pattern"""
        if pattern.examples:
            outcomes = [ex.outcome for ex in pattern.examples]
            return max(set(outcomes), key=outcomes.count)  # Most common outcome
        return query.desired_outcome
    
    # Additional placeholder implementations for discovery methods
    async def _group_memories_for_discovery(self, memories: List[MemoryItem]) -> Dict[str, List[MemoryItem]]:
        """Group memories for pattern discovery"""
        groups = {}
        for memory in memories:
            # Simple grouping by memory type
            key = memory.memory_type.value
            if key not in groups:
                groups[key] = []
            groups[key].append(memory)
        return groups
    
    async def _convert_memories_to_examples(self, memories: List[MemoryItem]) -> List[Dict[str, Any]]:
        """Convert memories to pattern examples"""
        examples = []
        for memory in memories:
            example = {
                'context': memory.context.to_dict() if memory.context else {},
                'input_features': await self._extract_content_features(memory.content),
                'output_features': {},
                'outcome': 'stored',
                'success_score': memory.importance,
                'metadata': {'memory_id': memory.memory_id}
            }
            examples.append(example)
        return examples
    
    async def _infer_pattern_type(self, examples: List[Dict[str, Any]]) -> PatternType:
        """Infer pattern type from examples"""
        # Simple heuristic based on success scores
        avg_success = np.mean([ex.get('success_score', 0.0) for ex in examples])
        if avg_success >= 0.7:
            return PatternType.SUCCESS_PATTERN
        else:
            return PatternType.WORKFLOW_PATTERN
    
    # Analysis methods
    async def _analyze_pattern_performance(self, pattern: LearningPattern) -> Dict[str, Any]:
        """Analyze pattern performance"""
        return {
            'usage_frequency': pattern.usage_count,
            'effectiveness_trend': 'stable',  # Placeholder
            'success_consistency': np.std([ex.success_score for ex in pattern.examples]) if pattern.examples else 0.0
        }
    
    async def _extract_pattern_insights(self, pattern: LearningPattern) -> List[str]:
        """Extract key insights from pattern"""
        insights = []
        if pattern.success_rate > 0.8:
            insights.append("High success rate indicates reliable pattern")
        if pattern.usage_count > 10:
            insights.append("Frequently used pattern with proven track record")
        return insights
    
    async def _suggest_pattern_improvements(self, pattern: LearningPattern) -> List[str]:
        """Suggest improvements for pattern"""
        suggestions = []
        if len(pattern.examples) < 5:
            suggestions.append("Collect more examples to improve pattern reliability")
        if pattern.confidence < 0.7:
            suggestions.append("Increase example quality to boost confidence")
        return suggestions
    
    async def _find_similar_examples(self, pattern: LearningPattern, context: Dict[str, Any], input_features: Dict[str, Any]) -> List[PatternExample]:
        """Find examples similar to current context"""
        return pattern.examples[:3]  # Simplified implementation
    
    async def _generate_pattern_recommendations(self, pattern: LearningPattern, context: Dict[str, Any], input_features: Dict[str, Any], similar_examples: List[PatternExample]) -> List[str]:
        """Generate recommendations based on pattern"""
        recommendations = []
        
        # Extract recommendations from successful examples
        for example in similar_examples:
            if example.success_score >= 0.7:
                recommendations.append(f"Apply approach from successful example: {example.outcome}")
        
        # Add pattern-specific recommendations
        if pattern.pattern_type == PatternType.SUCCESS_PATTERN:
            recommendations.append("Follow the proven success pattern")
        
        return recommendations[:5]  # Limit to top 5