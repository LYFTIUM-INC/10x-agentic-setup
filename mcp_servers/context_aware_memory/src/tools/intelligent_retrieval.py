"""
Intelligent Retrieval System for Context-Aware Memory
Advanced retrieval strategies with context awareness, learning, and optimization
"""

import asyncio
import logging
import json
import time
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import heapq

from .semantic_storage import MemoryItem, MemoryContext, MemoryQuery, MemoryType, AccessLevel

logger = logging.getLogger(__name__)


class RetrievalStrategy(Enum):
    """Different retrieval strategies"""
    SEMANTIC = "semantic"  # Vector similarity based
    CONTEXTUAL = "contextual"  # Context matching priority
    TEMPORAL = "temporal"  # Time-based relevance
    HYBRID = "hybrid"  # Combined approach
    ADAPTIVE = "adaptive"  # ML-learned strategy
    FREQUENCY = "frequency"  # Access frequency based
    IMPORTANCE = "importance"  # Importance score based
    COLLABORATIVE = "collaborative"  # User similarity based


class RankingFactor(Enum):
    """Factors used in ranking retrieved memories"""
    SEMANTIC_SIMILARITY = "semantic_similarity"
    CONTEXT_MATCH = "context_match"
    TEMPORAL_RELEVANCE = "temporal_relevance"
    ACCESS_FREQUENCY = "access_frequency"
    IMPORTANCE_SCORE = "importance_score"
    USER_PREFERENCE = "user_preference"
    RELATIONSHIP_STRENGTH = "relationship_strength"
    CONTENT_FRESHNESS = "content_freshness"


@dataclass
class RetrievalParameters:
    """Parameters for controlling retrieval behavior"""
    strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    max_results: int = 10
    similarity_threshold: float = 0.5
    context_weight: float = 0.3
    temporal_weight: float = 0.2
    frequency_weight: float = 0.1
    importance_weight: float = 0.2
    freshness_weight: float = 0.1
    diversity_factor: float = 0.1
    personalization_strength: float = 0.2
    include_related: bool = True
    max_age_hours: Optional[float] = None
    boost_recent_access: bool = True


@dataclass
class RetrievalResult:
    """Enhanced retrieval result with scoring details"""
    memory: MemoryItem
    total_score: float
    factor_scores: Dict[RankingFactor, float]
    retrieval_reason: str
    confidence: float
    rank: int = 0


@dataclass
class UserProfile:
    """User behavior and preference profile"""
    user_id: str
    preferences: Dict[str, float] = field(default_factory=dict)
    access_patterns: Dict[str, int] = field(default_factory=dict)
    content_preferences: Dict[MemoryType, float] = field(default_factory=dict)
    context_preferences: Dict[str, float] = field(default_factory=dict)
    temporal_patterns: Dict[str, float] = field(default_factory=dict)
    similar_users: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


class ContextAnalyzer:
    """Analyzes and enriches context for better retrieval"""
    
    def __init__(self):
        self.context_patterns = defaultdict(lambda: defaultdict(int))
        self.temporal_patterns = defaultdict(list)
        self.semantic_clusters = {}
    
    def analyze_context(self, context: MemoryContext, query: str) -> Dict[str, Any]:
        """Analyze context and extract relevant features"""
        features = {
            'temporal_context': self._analyze_temporal_context(context),
            'semantic_context': self._analyze_semantic_context(query),
            'project_context': self._analyze_project_context(context),
            'user_context': self._analyze_user_context(context),
            'session_context': self._analyze_session_context(context),
            'environment_context': self._analyze_environment_context(context)
        }
        
        return features
    
    def _analyze_temporal_context(self, context: MemoryContext) -> Dict[str, Any]:
        """Analyze temporal aspects of the context"""
        now = datetime.now()
        
        return {
            'hour_of_day': now.hour,
            'day_of_week': now.weekday(),
            'is_weekend': now.weekday() >= 5,
            'is_business_hours': 9 <= now.hour <= 17,
            'time_context': self._get_time_context(now)
        }
    
    def _analyze_semantic_context(self, query: str) -> Dict[str, Any]:
        """Extract semantic features from query"""
        words = query.lower().split()
        
        # Identify query type
        query_type = "general"
        if any(word in words for word in ['how', 'what', 'where', 'when', 'why']):
            query_type = "question"
        elif any(word in words for word in ['find', 'search', 'get', 'show']):
            query_type = "retrieval"
        elif any(word in words for word in ['create', 'make', 'build', 'generate']):
            query_type = "creation"
        
        # Identify domain
        domain = "general"
        if any(word in words for word in ['code', 'function', 'class', 'method', 'programming']):
            domain = "programming"
        elif any(word in words for word in ['meeting', 'call', 'discussion', 'decision']):
            domain = "communication"
        elif any(word in words for word in ['task', 'todo', 'project', 'deadline']):
            domain = "planning"
        
        return {
            'query_type': query_type,
            'domain': domain,
            'word_count': len(words),
            'has_technical_terms': self._has_technical_terms(words),
            'sentiment': self._analyze_sentiment(query)
        }
    
    def _analyze_project_context(self, context: MemoryContext) -> Dict[str, Any]:
        """Analyze project-specific context"""
        return {
            'project': context.project,
            'has_project': context.project is not None,
            'project_type': self._infer_project_type(context.project) if context.project else None
        }
    
    def _analyze_user_context(self, context: MemoryContext) -> Dict[str, Any]:
        """Analyze user-specific context"""
        return {
            'user': context.user,
            'has_user': context.user is not None,
            'is_collaborative': self._is_collaborative_context(context)
        }
    
    def _analyze_session_context(self, context: MemoryContext) -> Dict[str, Any]:
        """Analyze session-specific context"""
        return {
            'session': context.session,
            'has_session': context.session is not None,
            'session_length': self._estimate_session_length(context.session) if context.session else 0
        }
    
    def _analyze_environment_context(self, context: MemoryContext) -> Dict[str, Any]:
        """Analyze environment and application context"""
        return {
            'environment': context.environment,
            'application': context.application,
            'location': context.location,
            'has_location': context.location is not None
        }
    
    def _get_time_context(self, dt: datetime) -> str:
        """Get time-based context label"""
        hour = dt.hour
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def _has_technical_terms(self, words: List[str]) -> bool:
        """Check if query contains technical terms"""
        technical_terms = {
            'api', 'function', 'class', 'method', 'variable', 'database', 'server',
            'client', 'request', 'response', 'endpoint', 'authentication', 'authorization',
            'algorithm', 'data', 'model', 'pipeline', 'configuration', 'deployment'
        }
        return any(word in technical_terms for word in words)
    
    def _analyze_sentiment(self, query: str) -> str:
        """Simple sentiment analysis"""
        positive_words = {'good', 'great', 'excellent', 'best', 'awesome', 'perfect'}
        negative_words = {'bad', 'terrible', 'awful', 'worst', 'horrible', 'broken'}
        urgent_words = {'urgent', 'asap', 'immediately', 'quick', 'fast', 'emergency'}
        
        words = set(query.lower().split())
        
        if words.intersection(urgent_words):
            return "urgent"
        elif words.intersection(negative_words):
            return "negative"
        elif words.intersection(positive_words):
            return "positive"
        else:
            return "neutral"
    
    def _infer_project_type(self, project: str) -> str:
        """Infer project type from name"""
        project_lower = project.lower()
        if any(term in project_lower for term in ['web', 'frontend', 'react', 'vue', 'angular']):
            return "web_frontend"
        elif any(term in project_lower for term in ['api', 'backend', 'server', 'microservice']):
            return "backend"
        elif any(term in project_lower for term in ['ml', 'ai', 'model', 'data', 'analytics']):
            return "ml_ai"
        elif any(term in project_lower for term in ['mobile', 'ios', 'android', 'app']):
            return "mobile"
        else:
            return "general"
    
    def _is_collaborative_context(self, context: MemoryContext) -> bool:
        """Check if context suggests collaborative work"""
        return (context.metadata and 
                any(key in context.metadata for key in ['team', 'shared', 'collaboration']))
    
    def _estimate_session_length(self, session: str) -> float:
        """Estimate session length based on session ID patterns"""
        # This is a placeholder - in practice, you'd track actual session durations
        return 1.0


class IntelligentRetriever:
    """Intelligent memory retrieval system with multiple strategies"""
    
    def __init__(self, semantic_store, embedding_manager=None):
        self.semantic_store = semantic_store
        self.embedding_manager = embedding_manager
        self.context_analyzer = ContextAnalyzer()
        
        # User profiles and learning
        self.user_profiles: Dict[str, UserProfile] = {}
        self.retrieval_history: List[Dict[str, Any]] = []
        self.strategy_performance: Dict[RetrievalStrategy, List[float]] = defaultdict(list)
        
        # Optimization parameters
        self.default_parameters = RetrievalParameters()
        self.adaptive_weights = {}
        
        # Caching
        self.query_cache: Dict[str, Tuple[List[RetrievalResult], datetime]] = {}
        self.cache_ttl = timedelta(minutes=5)
    
    async def retrieve(self, query: MemoryQuery) -> List[MemoryItem]:
        """Main retrieval method with intelligent strategy selection"""
        try:
            start_time = time.time()
            
            # Check cache first
            cache_key = self._generate_cache_key(query)
            if cache_key in self.query_cache:
                cached_results, cached_time = self.query_cache[cache_key]
                if datetime.now() - cached_time < self.cache_ttl:
                    logger.debug(f"Cache hit for query: {query.query_text[:50]}")
                    return [result.memory for result in cached_results]
            
            # Analyze context
            context_features = self.context_analyzer.analyze_context(
                query.context or MemoryContext(), 
                query.query_text
            )
            
            # Get user profile
            user_profile = self._get_user_profile(query.context)
            
            # Select optimal strategy
            strategy = self._select_strategy(query, context_features, user_profile)
            
            # Retrieve candidates
            candidates = await self._retrieve_candidates(query, strategy)
            
            # Rank and score results
            ranked_results = await self._rank_and_score(
                candidates, query, context_features, user_profile, strategy
            )
            
            # Apply diversity and post-processing
            final_results = self._apply_diversity_and_filtering(
                ranked_results, query, context_features
            )
            
            # Update learning
            await self._update_learning(query, final_results, strategy, context_features)
            
            # Cache results
            self.query_cache[cache_key] = (final_results, datetime.now())
            
            retrieval_time = time.time() - start_time
            logger.info(f"Retrieved {len(final_results)} memories in {retrieval_time:.3f}s using {strategy.value}")
            
            return [result.memory for result in final_results]
            
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return []
    
    async def _retrieve_candidates(self, query: MemoryQuery, strategy: RetrievalStrategy) -> List[MemoryItem]:
        """Retrieve candidate memories based on strategy"""
        candidates = []
        
        if strategy == RetrievalStrategy.SEMANTIC:
            candidates = await self._semantic_retrieval(query)
        elif strategy == RetrievalStrategy.CONTEXTUAL:
            candidates = await self._contextual_retrieval(query)
        elif strategy == RetrievalStrategy.TEMPORAL:
            candidates = await self._temporal_retrieval(query)
        elif strategy == RetrievalStrategy.FREQUENCY:
            candidates = await self._frequency_retrieval(query)
        elif strategy == RetrievalStrategy.IMPORTANCE:
            candidates = await self._importance_retrieval(query)
        elif strategy == RetrievalStrategy.HYBRID:
            candidates = await self._hybrid_retrieval(query)
        elif strategy == RetrievalStrategy.ADAPTIVE:
            candidates = await self._adaptive_retrieval(query)
        elif strategy == RetrievalStrategy.COLLABORATIVE:
            candidates = await self._collaborative_retrieval(query)
        else:
            # Default to semantic
            candidates = await self._semantic_retrieval(query)
        
        return candidates
    
    async def _semantic_retrieval(self, query: MemoryQuery) -> List[MemoryItem]:
        """Retrieve based on semantic similarity"""
        if not self.embedding_manager:
            # Fallback to text search
            return await self.semantic_store.search(
                query.query_text, 
                filters=self._build_filters(query),
                limit=query.max_results * 2  # Get more candidates for ranking
            )
        
        # Generate query embedding
        query_embedding = await self.embedding_manager.encode_texts([query.query_text])
        
        # Find similar memories
        candidates = []
        for memory in self.semantic_store.memories.values():
            if not query.matches_memory(memory):
                continue
            
            if memory.embedding:
                similarity = self._calculate_similarity(query_embedding[0], memory.embedding)
                if similarity >= query.similarity_threshold:
                    memory.similarity_score = similarity
                    candidates.append(memory)
        
        # Sort by similarity
        candidates.sort(key=lambda m: m.similarity_score, reverse=True)
        return candidates[:query.max_results * 2]
    
    async def _contextual_retrieval(self, query: MemoryQuery) -> List[MemoryItem]:
        """Retrieve based on context matching"""
        candidates = []
        
        for memory in self.semantic_store.memories.values():
            if not query.matches_memory(memory):
                continue
            
            context_score = self._calculate_context_similarity(query.context, memory.context)
            if context_score > 0.3:  # Minimum context threshold
                memory.similarity_score = context_score
                candidates.append(memory)
        
        candidates.sort(key=lambda m: m.similarity_score, reverse=True)
        return candidates[:query.max_results * 2]
    
    async def _temporal_retrieval(self, query: MemoryQuery) -> List[MemoryItem]:
        """Retrieve based on temporal relevance"""
        candidates = []
        now = datetime.now()
        
        for memory in self.semantic_store.memories.values():
            if not query.matches_memory(memory):
                continue
            
            # Calculate temporal relevance
            age_hours = (now - memory.created_at).total_seconds() / 3600
            temporal_score = max(0.1, 1.0 - (age_hours / (24 * 7)))  # Week decay
            
            # Boost recently accessed memories
            if memory.last_accessed:
                access_hours = (now - memory.last_accessed).total_seconds() / 3600
                access_boost = max(1.0, 2.0 - (access_hours / 24))
                temporal_score *= access_boost
            
            memory.similarity_score = temporal_score
            candidates.append(memory)
        
        candidates.sort(key=lambda m: m.similarity_score, reverse=True)
        return candidates[:query.max_results * 2]
    
    async def _frequency_retrieval(self, query: MemoryQuery) -> List[MemoryItem]:
        """Retrieve based on access frequency"""
        candidates = []
        
        for memory in self.semantic_store.memories.values():
            if not query.matches_memory(memory):
                continue
            
            # Normalize access count by age
            age_days = max(1, (datetime.now() - memory.created_at).days)
            frequency_score = memory.access_count / age_days
            
            memory.similarity_score = min(1.0, frequency_score / 10)  # Normalize to 0-1
            candidates.append(memory)
        
        candidates.sort(key=lambda m: m.similarity_score, reverse=True)
        return candidates[:query.max_results * 2]
    
    async def _importance_retrieval(self, query: MemoryQuery) -> List[MemoryItem]:
        """Retrieve based on importance scores"""
        candidates = []
        
        for memory in self.semantic_store.memories.values():
            if not query.matches_memory(memory):
                continue
            
            memory.similarity_score = memory.importance
            candidates.append(memory)
        
        candidates.sort(key=lambda m: m.similarity_score, reverse=True)
        return candidates[:query.max_results * 2]
    
    async def _hybrid_retrieval(self, query: MemoryQuery) -> List[MemoryItem]:
        """Retrieve using multiple strategies combined"""
        # Get candidates from multiple strategies
        semantic_candidates = await self._semantic_retrieval(query)
        contextual_candidates = await self._contextual_retrieval(query)
        temporal_candidates = await self._temporal_retrieval(query)
        
        # Combine and deduplicate
        all_candidates = {}
        
        for memory in semantic_candidates:
            memory_id = memory.memory_id
            if memory_id not in all_candidates:
                all_candidates[memory_id] = memory
                all_candidates[memory_id].similarity_score = memory.similarity_score * 0.4
            else:
                all_candidates[memory_id].similarity_score += memory.similarity_score * 0.4
        
        for memory in contextual_candidates:
            memory_id = memory.memory_id
            if memory_id not in all_candidates:
                all_candidates[memory_id] = memory
                all_candidates[memory_id].similarity_score = memory.similarity_score * 0.3
            else:
                all_candidates[memory_id].similarity_score += memory.similarity_score * 0.3
        
        for memory in temporal_candidates:
            memory_id = memory.memory_id
            if memory_id not in all_candidates:
                all_candidates[memory_id] = memory
                all_candidates[memory_id].similarity_score = memory.similarity_score * 0.3
            else:
                all_candidates[memory_id].similarity_score += memory.similarity_score * 0.3
        
        candidates = list(all_candidates.values())
        candidates.sort(key=lambda m: m.similarity_score, reverse=True)
        return candidates[:query.max_results * 2]
    
    async def _adaptive_retrieval(self, query: MemoryQuery) -> List[MemoryItem]:
        """Retrieve using learned adaptive strategy"""
        # For now, fall back to hybrid with learned weights
        return await self._hybrid_retrieval(query)
    
    async def _collaborative_retrieval(self, query: MemoryQuery) -> List[MemoryItem]:
        """Retrieve based on similar user behavior"""
        user_profile = self._get_user_profile(query.context)
        
        if not user_profile or not user_profile.similar_users:
            # Fall back to semantic retrieval
            return await self._semantic_retrieval(query)
        
        # Find memories accessed by similar users
        candidates = []
        for memory in self.semantic_store.memories.values():
            if not query.matches_memory(memory):
                continue
            
            # Check if similar users accessed this memory
            collaborative_score = 0.0
            if memory.context and memory.context.user in user_profile.similar_users:
                collaborative_score = 0.8
            
            # Add base semantic similarity
            if memory.embedding and self.embedding_manager:
                query_embedding = await self.embedding_manager.encode_texts([query.query_text])
                semantic_score = self._calculate_similarity(query_embedding[0], memory.embedding)
                collaborative_score = max(collaborative_score, semantic_score * 0.5)
            
            if collaborative_score > 0.1:
                memory.similarity_score = collaborative_score
                candidates.append(memory)
        
        candidates.sort(key=lambda m: m.similarity_score, reverse=True)
        return candidates[:query.max_results * 2]
    
    async def _rank_and_score(self, candidates: List[MemoryItem], query: MemoryQuery,
                             context_features: Dict[str, Any], user_profile: UserProfile,
                             strategy: RetrievalStrategy) -> List[RetrievalResult]:
        """Rank and score candidate memories using multiple factors"""
        results = []
        
        for memory in candidates:
            factor_scores = {}
            
            # Semantic similarity
            factor_scores[RankingFactor.SEMANTIC_SIMILARITY] = getattr(memory, 'similarity_score', 0.0)
            
            # Context match
            factor_scores[RankingFactor.CONTEXT_MATCH] = self._calculate_context_similarity(
                query.context, memory.context
            )
            
            # Temporal relevance
            factor_scores[RankingFactor.TEMPORAL_RELEVANCE] = self._calculate_temporal_relevance(memory)
            
            # Access frequency
            factor_scores[RankingFactor.ACCESS_FREQUENCY] = self._calculate_frequency_score(memory)
            
            # Importance score
            factor_scores[RankingFactor.IMPORTANCE_SCORE] = memory.importance
            
            # User preference
            factor_scores[RankingFactor.USER_PREFERENCE] = self._calculate_user_preference(
                memory, user_profile
            )
            
            # Relationship strength
            factor_scores[RankingFactor.RELATIONSHIP_STRENGTH] = self._calculate_relationship_strength(
                memory, candidates
            )
            
            # Content freshness
            factor_scores[RankingFactor.CONTENT_FRESHNESS] = self._calculate_freshness_score(memory)
            
            # Calculate total score
            total_score = self._calculate_total_score(factor_scores, self.default_parameters)
            
            # Determine retrieval reason
            reason = self._determine_retrieval_reason(factor_scores)
            
            # Calculate confidence
            confidence = self._calculate_confidence(factor_scores, strategy)
            
            result = RetrievalResult(
                memory=memory,
                total_score=total_score,
                factor_scores=factor_scores,
                retrieval_reason=reason,
                confidence=confidence
            )
            
            results.append(result)
        
        # Sort by total score
        results.sort(key=lambda r: r.total_score, reverse=True)
        
        # Assign ranks
        for i, result in enumerate(results):
            result.rank = i + 1
        
        return results
    
    def _apply_diversity_and_filtering(self, ranked_results: List[RetrievalResult],
                                     query: MemoryQuery, context_features: Dict[str, Any]) -> List[RetrievalResult]:
        """Apply diversity constraints and final filtering"""
        if not ranked_results:
            return []
        
        final_results = []
        seen_content_hashes = set()
        content_type_counts = defaultdict(int)
        max_per_type = max(1, query.max_results // 3)
        
        for result in ranked_results:
            memory = result.memory
            
            # Skip duplicates
            if memory.content_hash in seen_content_hashes:
                continue
            
            # Apply diversity constraints
            if (self.default_parameters.diversity_factor > 0 and
                content_type_counts[memory.memory_type] >= max_per_type):
                continue
            
            # Apply final filters
            if result.confidence < 0.3:  # Minimum confidence threshold
                continue
            
            final_results.append(result)
            seen_content_hashes.add(memory.content_hash)
            content_type_counts[memory.memory_type] += 1
            
            if len(final_results) >= query.max_results:
                break
        
        return final_results
    
    def _select_strategy(self, query: MemoryQuery, context_features: Dict[str, Any],
                        user_profile: UserProfile) -> RetrievalStrategy:
        """Select optimal retrieval strategy based on context and learning"""
        # For now, use simple heuristics
        # In practice, this would use ML models trained on user behavior
        
        query_text = query.query_text.lower()
        
        # Check for temporal indicators
        temporal_words = {'recent', 'latest', 'yesterday', 'today', 'last', 'new'}
        if any(word in query_text for word in temporal_words):
            return RetrievalStrategy.TEMPORAL
        
        # Check for importance indicators
        importance_words = {'important', 'critical', 'urgent', 'priority', 'key'}
        if any(word in query_text for word in importance_words):
            return RetrievalStrategy.IMPORTANCE
        
        # Check for collaborative indicators
        collab_words = {'team', 'shared', 'others', 'colleagues', 'everyone'}
        if any(word in query_text for word in collab_words):
            return RetrievalStrategy.COLLABORATIVE
        
        # Check for specific context
        if query.context and query.context.project:
            return RetrievalStrategy.CONTEXTUAL
        
        # Default to hybrid for balanced results
        return RetrievalStrategy.HYBRID
    
    def _get_user_profile(self, context: Optional[MemoryContext]) -> UserProfile:
        """Get or create user profile"""
        if not context or not context.user:
            return UserProfile(user_id="anonymous")
        
        user_id = context.user
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id)
        
        return self.user_profiles[user_id]
    
    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        try:
            import numpy as np
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception:
            return 0.0
    
    def _calculate_context_similarity(self, context1: Optional[MemoryContext], 
                                    context2: Optional[MemoryContext]) -> float:
        """Calculate similarity between contexts"""
        if not context1 or not context2:
            return 0.0
        
        score = 0.0
        factors = 0
        
        # Project similarity
        if context1.project and context2.project:
            if context1.project == context2.project:
                score += 1.0
            factors += 1
        
        # User similarity
        if context1.user and context2.user:
            if context1.user == context2.user:
                score += 0.8
            factors += 1
        
        # Session similarity
        if context1.session and context2.session:
            if context1.session == context2.session:
                score += 0.6
            factors += 1
        
        # Application similarity
        if context1.application and context2.application:
            if context1.application == context2.application:
                score += 0.4
            factors += 1
        
        # Environment similarity
        if context1.environment and context2.environment:
            if context1.environment == context2.environment:
                score += 0.3
            factors += 1
        
        return score / max(1, factors)
    
    def _calculate_temporal_relevance(self, memory: MemoryItem) -> float:
        """Calculate temporal relevance score"""
        now = datetime.now()
        age_hours = (now - memory.created_at).total_seconds() / 3600
        
        # Base decay over time
        base_score = max(0.1, 1.0 - (age_hours / (24 * 7)))  # Week decay
        
        # Boost for recent access
        if memory.last_accessed:
            access_hours = (now - memory.last_accessed).total_seconds() / 3600
            access_boost = max(1.0, 1.5 - (access_hours / 24))
            base_score *= access_boost
        
        return min(1.0, base_score)
    
    def _calculate_frequency_score(self, memory: MemoryItem) -> float:
        """Calculate access frequency score"""
        age_days = max(1, (datetime.now() - memory.created_at).days)
        frequency = memory.access_count / age_days
        return min(1.0, frequency / 5)  # Normalize to 0-1
    
    def _calculate_user_preference(self, memory: MemoryItem, user_profile: UserProfile) -> float:
        """Calculate user preference score"""
        if not user_profile:
            return 0.5
        
        score = 0.0
        
        # Content type preference
        if memory.memory_type in user_profile.content_preferences:
            score += user_profile.content_preferences[memory.memory_type] * 0.4
        
        # Tag preferences
        for tag in memory.tags:
            if tag in user_profile.preferences:
                score += user_profile.preferences[tag] * 0.3
        
        # Context preferences
        if memory.context and memory.context.project:
            project_key = f"project:{memory.context.project}"
            if project_key in user_profile.context_preferences:
                score += user_profile.context_preferences[project_key] * 0.3
        
        return min(1.0, score)
    
    def _calculate_relationship_strength(self, memory: MemoryItem, 
                                       all_candidates: List[MemoryItem]) -> float:
        """Calculate relationship strength with other candidates"""
        if not memory.related_memories:
            return 0.0
        
        related_count = 0
        candidate_ids = {m.memory_id for m in all_candidates}
        
        for related_id in memory.related_memories:
            if related_id in candidate_ids:
                related_count += 1
        
        return min(1.0, related_count / max(1, len(memory.related_memories)))
    
    def _calculate_freshness_score(self, memory: MemoryItem) -> float:
        """Calculate content freshness score"""
        update_hours = (datetime.now() - memory.updated_at).total_seconds() / 3600
        return max(0.1, 1.0 - (update_hours / (24 * 3)))  # 3-day freshness window
    
    def _calculate_total_score(self, factor_scores: Dict[RankingFactor, float],
                              params: RetrievalParameters) -> float:
        """Calculate weighted total score"""
        total = 0.0
        
        total += factor_scores.get(RankingFactor.SEMANTIC_SIMILARITY, 0) * 0.3
        total += factor_scores.get(RankingFactor.CONTEXT_MATCH, 0) * params.context_weight
        total += factor_scores.get(RankingFactor.TEMPORAL_RELEVANCE, 0) * params.temporal_weight
        total += factor_scores.get(RankingFactor.ACCESS_FREQUENCY, 0) * params.frequency_weight
        total += factor_scores.get(RankingFactor.IMPORTANCE_SCORE, 0) * params.importance_weight
        total += factor_scores.get(RankingFactor.USER_PREFERENCE, 0) * params.personalization_strength
        total += factor_scores.get(RankingFactor.RELATIONSHIP_STRENGTH, 0) * 0.1
        total += factor_scores.get(RankingFactor.CONTENT_FRESHNESS, 0) * params.freshness_weight
        
        return min(1.0, total)
    
    def _determine_retrieval_reason(self, factor_scores: Dict[RankingFactor, float]) -> str:
        """Determine primary reason for retrieval"""
        max_factor = max(factor_scores.items(), key=lambda x: x[1])
        
        reason_map = {
            RankingFactor.SEMANTIC_SIMILARITY: "semantically similar content",
            RankingFactor.CONTEXT_MATCH: "matching context",
            RankingFactor.TEMPORAL_RELEVANCE: "recent or recently accessed",
            RankingFactor.ACCESS_FREQUENCY: "frequently accessed",
            RankingFactor.IMPORTANCE_SCORE: "high importance",
            RankingFactor.USER_PREFERENCE: "matches user preferences",
            RankingFactor.RELATIONSHIP_STRENGTH: "related to other results",
            RankingFactor.CONTENT_FRESHNESS: "recently updated content"
        }
        
        return reason_map.get(max_factor[0], "general relevance")
    
    def _calculate_confidence(self, factor_scores: Dict[RankingFactor, float],
                            strategy: RetrievalStrategy) -> float:
        """Calculate confidence in retrieval result"""
        # Base confidence from strongest factor
        max_score = max(factor_scores.values()) if factor_scores else 0.0
        
        # Boost for multiple strong factors
        strong_factors = sum(1 for score in factor_scores.values() if score > 0.7)
        multi_factor_boost = min(0.2, strong_factors * 0.05)
        
        # Strategy-specific adjustments
        strategy_boost = 0.0
        if strategy in [RetrievalStrategy.HYBRID, RetrievalStrategy.ADAPTIVE]:
            strategy_boost = 0.1
        
        confidence = min(1.0, max_score + multi_factor_boost + strategy_boost)
        return confidence
    
    def _build_filters(self, query: MemoryQuery) -> Dict[str, Any]:
        """Build filters for memory search"""
        filters = {}
        
        if query.memory_types:
            filters['memory_type'] = [mt.value for mt in query.memory_types]
        
        if query.tags:
            filters['tags'] = query.tags
        
        if query.importance_threshold > 0:
            filters['min_importance'] = query.importance_threshold
        
        if query.time_range:
            filters['time_range'] = query.time_range
        
        if query.context:
            if query.context.project:
                filters['project'] = query.context.project
            if query.context.user:
                filters['user'] = query.context.user
        
        if query.access_level:
            filters['access_level'] = query.access_level.value
        
        return filters
    
    def _generate_cache_key(self, query: MemoryQuery) -> str:
        """Generate cache key for query"""
        import hashlib
        
        key_data = {
            'query': query.query_text,
            'max_results': query.max_results,
            'threshold': query.similarity_threshold,
            'strategy': query.strategy.value if hasattr(query, 'strategy') else 'default',
            'context': query.context.to_dict() if query.context else None
        }
        
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def _update_learning(self, query: MemoryQuery, results: List[RetrievalResult],
                              strategy: RetrievalStrategy, context_features: Dict[str, Any]):
        """Update learning models based on retrieval results"""
        # Record retrieval event
        event = {
            'timestamp': datetime.now().isoformat(),
            'query': query.query_text,
            'strategy': strategy.value,
            'result_count': len(results),
            'context_features': context_features,
            'avg_score': sum(r.total_score for r in results) / len(results) if results else 0.0
        }
        
        self.retrieval_history.append(event)
        
        # Update user profile
        if query.context and query.context.user:
            user_profile = self._get_user_profile(query.context)
            
            # Update content type preferences
            for result in results:
                memory_type = result.memory.memory_type
                if memory_type not in user_profile.content_preferences:
                    user_profile.content_preferences[memory_type] = 0.5
                
                # Increase preference for successful retrievals
                user_profile.content_preferences[memory_type] = min(1.0,
                    user_profile.content_preferences[memory_type] + 0.05
                )
            
            # Update tag preferences
            for result in results:
                for tag in result.memory.tags:
                    if tag not in user_profile.preferences:
                        user_profile.preferences[tag] = 0.5
                    
                    user_profile.preferences[tag] = min(1.0,
                        user_profile.preferences[tag] + 0.02
                    )
            
            user_profile.last_updated = datetime.now()
        
        # Update strategy performance
        if results:
            avg_confidence = sum(r.confidence for r in results) / len(results)
            self.strategy_performance[strategy].append(avg_confidence)
            
            # Keep only recent performance data
            if len(self.strategy_performance[strategy]) > 100:
                self.strategy_performance[strategy] = self.strategy_performance[strategy][-50:]


# Example usage and testing
if __name__ == "__main__":
    async def test_intelligent_retrieval():
        from .semantic_storage import SemanticMemoryStore, MemoryItem, MemoryContext, MemoryType
        
        # Create memory store
        store = SemanticMemoryStore(data_dir="./test_memory")
        await store.initialize()
        
        # Create retriever
        retriever = IntelligentRetriever(store)
        
        # Add test memories
        memories = [
            MemoryItem(
                content="Python function for calculating Fibonacci numbers",
                memory_type=MemoryType.CODE,
                context=MemoryContext(project="math_lib", user="alice"),
                tags=["python", "fibonacci", "math"],
                importance=0.8
            ),
            MemoryItem(
                content="Meeting notes about API design decisions",
                memory_type=MemoryType.CONVERSATION,
                context=MemoryContext(project="api_service", user="bob"),
                tags=["meeting", "api", "design"],
                importance=0.9
            ),
            MemoryItem(
                content="Documentation for REST API endpoints",
                memory_type=MemoryType.DOCUMENT,
                context=MemoryContext(project="api_service", user="alice"),
                tags=["documentation", "api", "rest"],
                importance=0.7
            )
        ]
        
        for memory in memories:
            await store.store_memory(memory)
        
        # Test different retrieval strategies
        query = MemoryQuery(
            query_text="API documentation",
            context=MemoryContext(project="api_service", user="alice"),
            max_results=5
        )
        
        results = await retriever.retrieve(query)
        print(f"Retrieved {len(results)} memories")
        
        for memory in results:
            print(f"- {memory.content[:50]}... (importance: {memory.importance})")
    
    asyncio.run(test_intelligent_retrieval())