"""
Memory Enhancement Utilities
Additional utilities for enhanced memory capabilities
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

from .semantic_storage import MemoryItem, MemoryContext
from .cot_memory_reasoning import ReasoningType, ChainOfThoughtReasoner
from .few_shot_learning import PatternType, FewShotLearningEngine
from .federated_memory import PrivacyLevel, FederatedMemoryManager

logger = logging.getLogger(__name__)


@dataclass
class MemoryInsight:
    """Represents an insight derived from memory analysis"""
    insight_id: str
    insight_type: str
    description: str
    confidence: float
    supporting_evidence: List[str]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CrossPatternConnection:
    """Connection between different patterns across reasoning types"""
    connection_id: str
    source_pattern: str
    target_pattern: str
    connection_type: str
    strength: float
    bidirectional: bool
    context: Dict[str, Any] = field(default_factory=dict)


class MemoryEnhancementEngine:
    """Advanced engine for memory capability enhancements"""
    
    def __init__(self, cot_reasoner: ChainOfThoughtReasoner, 
                 few_shot_engine: FewShotLearningEngine,
                 federated_manager: FederatedMemoryManager):
        self.cot_reasoner = cot_reasoner
        self.few_shot_engine = few_shot_engine
        self.federated_manager = federated_manager
        
        # Cross-system connections
        self.pattern_connections: Dict[str, CrossPatternConnection] = {}
        self.insight_cache: Dict[str, MemoryInsight] = {}
        
        # Enhanced analytics
        self.analytics = {
            'cross_pattern_discoveries': 0,
            'federated_insights': 0,
            'reasoning_pattern_matches': 0,
            'privacy_preserved_shares': 0
        }
    
    async def discover_cross_pattern_insights(self, memories: List[MemoryItem]) -> List[MemoryInsight]:
        """Discover insights by combining CoT reasoning with few-shot patterns"""
        insights = []
        
        try:
            # Step 1: Apply CoT reasoning to find patterns
            from .cot_memory_reasoning import ReasoningQuery
            reasoning_query = ReasoningQuery(
                query_text="Discover hidden patterns and connections",
                context=MemoryContext(project="cross_pattern_discovery"),
                reasoning_types=[ReasoningType.PATTERN_ANALYSIS, ReasoningType.ANALOGICAL_REASONING],
                max_steps=10
            )
            
            reasoning_chain = await self.cot_reasoner.reason_about_memories(reasoning_query)
            
            # Step 2: Extract patterns from reasoning
            discovered_patterns = self._extract_patterns_from_reasoning(reasoning_chain)
            
            # Step 3: Match with few-shot learning patterns
            for pattern_data in discovered_patterns:
                similar_learned = await self._find_similar_learned_patterns(pattern_data)
                
                if similar_learned:
                    # Create cross-pattern insight
                    insight = self._create_cross_pattern_insight(pattern_data, similar_learned)
                    insights.append(insight)
                    
                    # Track connection
                    connection = CrossPatternConnection(
                        connection_id=f"conn_{insight.insight_id}",
                        source_pattern=pattern_data.get('pattern_id', 'unknown'),
                        target_pattern=similar_learned[0].pattern_id,
                        connection_type="reasoning_to_learning",
                        strength=pattern_data.get('confidence', 0.5),
                        bidirectional=True,
                        context={'discovery_time': datetime.now().isoformat()}
                    )
                    self.pattern_connections[connection.connection_id] = connection
            
            # Update analytics
            self.analytics['cross_pattern_discoveries'] += len(insights)
            
            logger.info(f"Discovered {len(insights)} cross-pattern insights")
            
        except Exception as e:
            logger.error(f"Failed to discover cross-pattern insights: {e}")
        
        return insights
    
    async def federated_pattern_enhancement(self, local_patterns: List[Any], 
                                          privacy_level: PrivacyLevel = PrivacyLevel.MEDIUM) -> List[Any]:
        """Enhance local patterns with federated knowledge while preserving privacy"""
        enhanced_patterns = []
        
        try:
            # Step 1: Prepare patterns for federated sharing
            shareable_patterns = await self._prepare_patterns_for_federation(local_patterns, privacy_level)
            
            # Step 2: Share with federation
            for pattern in shareable_patterns:
                knowledge_id = await self.federated_manager.share_knowledge(
                    knowledge_type="enhanced_pattern",
                    content=pattern,
                    privacy_policy=self.federated_manager.default_policy
                )
                
                if knowledge_id:
                    self.analytics['privacy_preserved_shares'] += 1
            
            # Step 3: Learn from federation
            enhanced = await self.federated_manager.learn_from_federation(
                local_patterns,
                privacy_policy=self.federated_manager.default_policy
            )
            
            enhanced_patterns.extend(enhanced)
            
            # Step 4: Create federated insights
            for pattern in enhanced:
                insight = MemoryInsight(
                    insight_id=f"fed_insight_{int(datetime.now().timestamp())}",
                    insight_type="federated_enhancement",
                    description=f"Pattern enhanced through federated learning: {pattern.name}",
                    confidence=pattern.confidence,
                    supporting_evidence=[f"Federated sources: {pattern.usage_count}"],
                    recommendations=["Apply federated knowledge to similar patterns"],
                    metadata={'pattern_id': pattern.pattern_id}
                )
                self.insight_cache[insight.insight_id] = insight
                self.analytics['federated_insights'] += 1
            
            logger.info(f"Enhanced {len(enhanced_patterns)} patterns through federation")
            
        except Exception as e:
            logger.error(f"Failed in federated pattern enhancement: {e}")
            return local_patterns
        
        return enhanced_patterns
    
    async def adaptive_reasoning_pipeline(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptive reasoning that combines all three enhanced capabilities"""
        results = {
            'reasoning_chains': [],
            'learned_patterns': [],
            'federated_insights': [],
            'recommendations': [],
            'confidence': 0.0
        }
        
        try:
            # Phase 1: Initial CoT reasoning
            from .cot_memory_reasoning import ReasoningQuery
            initial_reasoning = ReasoningQuery(
                query_text=query,
                context=MemoryContext(**context),
                reasoning_types=[ReasoningType.PATTERN_ANALYSIS, ReasoningType.PREDICTIVE_REASONING],
                max_steps=5
            )
            
            chain = await self.cot_reasoner.reason_about_memories(initial_reasoning)
            results['reasoning_chains'].append(self._chain_to_dict(chain))
            
            # Phase 2: Apply few-shot learning
            from .few_shot_learning import FewShotQuery
            few_shot_query = FewShotQuery(
                context=context,
                input_features={'query': query, 'reasoning_confidence': chain.overall_confidence},
                desired_outcome="optimal_solution",
                pattern_types=[PatternType.SUCCESS_PATTERN, PatternType.SOLUTION_PATTERN]
            )
            
            matching_patterns = await self.few_shot_engine.find_matching_patterns(few_shot_query)
            results['learned_patterns'] = [self._pattern_application_to_dict(p) for p in matching_patterns]
            
            # Phase 3: Query federation for additional insights
            from .federated_memory import FederationQuery, PrivacyPolicy
            fed_query = FederationQuery(
                query_context=context,
                desired_knowledge_types=['solution_pattern', 'best_practice'],
                privacy_constraints=PrivacyPolicy(
                    privacy_level=PrivacyLevel.MEDIUM,
                    sharing_scope=self.federated_manager.default_policy.sharing_scope
                ),
                max_results=5
            )
            
            federated_results = await self.federated_manager.query_federation(fed_query)
            results['federated_insights'] = federated_results
            
            # Phase 4: Synthesize recommendations
            recommendations = await self._synthesize_recommendations(chain, matching_patterns, federated_results)
            results['recommendations'] = recommendations
            
            # Calculate overall confidence
            confidence_factors = [
                chain.overall_confidence,
                np.mean([p.confidence for p in matching_patterns]) if matching_patterns else 0.0,
                len(federated_results) / 5.0  # Normalize by max results
            ]
            results['confidence'] = np.mean([c for c in confidence_factors if c > 0])
            
            # Update analytics
            self.analytics['reasoning_pattern_matches'] += len(matching_patterns)
            
        except Exception as e:
            logger.error(f"Failed in adaptive reasoning pipeline: {e}")
            results['error'] = str(e)
        
        return results
    
    async def continuous_learning_loop(self, feedback: Dict[str, Any]):
        """Continuous learning from user feedback and system performance"""
        try:
            # Extract learning signals
            success = feedback.get('success', False)
            context = feedback.get('context', {})
            outcome = feedback.get('outcome', 'unknown')
            
            # Update few-shot patterns
            if 'pattern_id' in feedback:
                await self.few_shot_engine.update_pattern_effectiveness(
                    pattern_id=feedback['pattern_id'],
                    actual_outcome=outcome,
                    success_score=1.0 if success else 0.0,
                    feedback=feedback
                )
            
            # Add successful reasoning chains as new patterns
            if success and 'reasoning_chain_id' in feedback:
                # Extract pattern from successful reasoning
                new_pattern_data = {
                    'context': context,
                    'input_features': {'query': feedback.get('query', '')},
                    'output_features': {'outcome': outcome},
                    'outcome': outcome,
                    'success_score': 1.0
                }
                
                await self.few_shot_engine.learn_from_examples(
                    [new_pattern_data],
                    PatternType.SUCCESS_PATTERN
                )
            
            # Share successful patterns with federation
            if success:
                await self.federated_manager.share_knowledge(
                    knowledge_type='success_feedback',
                    content={
                        'context': context,
                        'outcome': outcome,
                        'timestamp': datetime.now().isoformat()
                    }
                )
            
            logger.info("Continuous learning loop updated with feedback")
            
        except Exception as e:
            logger.error(f"Failed in continuous learning loop: {e}")
    
    # Helper methods
    
    def _extract_patterns_from_reasoning(self, reasoning_chain) -> List[Dict[str, Any]]:
        """Extract patterns from reasoning chain"""
        patterns = []
        
        for step in reasoning_chain.steps:
            if 'patterns' in step.output_data:
                for pattern in step.output_data['patterns']:
                    patterns.append({
                        'pattern_id': f"reasoning_{step.step_id}_{len(patterns)}",
                        'pattern_data': pattern,
                        'confidence': step.confidence,
                        'reasoning_type': step.step_type.value
                    })
        
        return patterns
    
    async def _find_similar_learned_patterns(self, pattern_data: Dict[str, Any]) -> List[Any]:
        """Find learned patterns similar to discovered pattern"""
        # Simple similarity check - in practice would be more sophisticated
        similar = []
        
        for pattern in self.few_shot_engine.learned_patterns.values():
            # Check if pattern types align
            if pattern_data.get('reasoning_type') == 'pattern_analysis' and \
               pattern.pattern_type in [PatternType.SUCCESS_PATTERN, PatternType.WORKFLOW_PATTERN]:
                similar.append(pattern)
        
        return similar[:3]  # Return top 3
    
    def _create_cross_pattern_insight(self, reasoning_pattern: Dict[str, Any], 
                                    learned_patterns: List[Any]) -> MemoryInsight:
        """Create insight from cross-pattern discovery"""
        insight = MemoryInsight(
            insight_id=f"cross_{int(datetime.now().timestamp())}",
            insight_type="cross_pattern_discovery",
            description=f"Discovered connection between reasoning pattern and {len(learned_patterns)} learned patterns",
            confidence=reasoning_pattern.get('confidence', 0.5) * 0.8,
            supporting_evidence=[
                f"Reasoning type: {reasoning_pattern.get('reasoning_type')}",
                f"Learned patterns: {[p.name for p in learned_patterns[:2]]}"
            ],
            recommendations=[
                "Apply learned patterns to enhance reasoning",
                "Update pattern library with new discoveries"
            ],
            metadata={
                'reasoning_pattern': reasoning_pattern,
                'learned_pattern_ids': [p.pattern_id for p in learned_patterns]
            }
        )
        
        return insight
    
    async def _prepare_patterns_for_federation(self, patterns: List[Any], 
                                             privacy_level: PrivacyLevel) -> List[Dict[str, Any]]:
        """Prepare patterns for federated sharing with privacy protection"""
        shareable = []
        
        for pattern in patterns:
            # Remove sensitive information based on privacy level
            pattern_data = {
                'pattern_type': pattern.pattern_type.value,
                'success_rate': pattern.success_rate,
                'confidence': pattern.confidence,
                'applicability_rules': pattern.applicability_rules[:3],  # Limit rules
                'example_count': len(pattern.examples)
            }
            
            if privacy_level == PrivacyLevel.LOW:
                pattern_data['name'] = pattern.name
                pattern_data['description'] = pattern.description
            
            shareable.append(pattern_data)
        
        return shareable
    
    def _chain_to_dict(self, chain) -> Dict[str, Any]:
        """Convert reasoning chain to dictionary"""
        return {
            'chain_id': chain.chain_id,
            'purpose': chain.purpose,
            'steps': len(chain.steps),
            'confidence': chain.overall_confidence,
            'reasoning_time': chain.reasoning_time,
            'final_conclusion': chain.final_conclusion
        }
    
    def _pattern_application_to_dict(self, application) -> Dict[str, Any]:
        """Convert pattern application to dictionary"""
        return {
            'pattern_id': application.pattern_id,
            'confidence': application.confidence,
            'predicted_outcome': application.predicted_outcome,
            'success_probability': application.success_probability,
            'recommendations': application.recommended_actions[:3]  # Limit recommendations
        }
    
    async def _synthesize_recommendations(self, reasoning_chain, pattern_applications, 
                                        federated_results) -> List[str]:
        """Synthesize recommendations from all sources"""
        recommendations = []
        
        # From reasoning chain
        if reasoning_chain.final_conclusion:
            if 'predictions' in reasoning_chain.final_conclusion:
                recommendations.append("Based on reasoning: " + 
                                     str(reasoning_chain.final_conclusion.get('synthesis', '')))
        
        # From pattern applications
        for app in pattern_applications[:2]:  # Top 2
            recommendations.extend([f"Pattern suggestion: {r}" for r in app.recommended_actions[:2]])
        
        # From federated results
        for result in federated_results[:2]:  # Top 2
            if 'recommendations' in result.get('content', {}):
                recommendations.append(f"Federation insight: {result['content']['recommendations'][0]}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:5]  # Return top 5
    
    async def get_enhancement_statistics(self) -> Dict[str, Any]:
        """Get statistics about memory enhancements"""
        stats = {
            'analytics': self.analytics.copy(),
            'pattern_connections': len(self.pattern_connections),
            'cached_insights': len(self.insight_cache),
            'cross_system_metrics': {
                'reasoning_patterns': len(self.cot_reasoner.pattern_library),
                'learned_patterns': len(self.few_shot_engine.learned_patterns),
                'federated_nodes': len(self.federated_manager.known_nodes)
            }
        }
        
        # Add connection strength distribution
        if self.pattern_connections:
            strengths = [conn.strength for conn in self.pattern_connections.values()]
            stats['connection_strengths'] = {
                'mean': np.mean(strengths),
                'std': np.std(strengths),
                'max': max(strengths),
                'min': min(strengths)
            }
        
        return stats


class MemoryOptimizer:
    """Optimizer for memory system performance"""
    
    def __init__(self, enhancement_engine: MemoryEnhancementEngine):
        self.enhancement_engine = enhancement_engine
        self.optimization_history = []
    
    async def optimize_memory_patterns(self, memories: List[MemoryItem]) -> Dict[str, Any]:
        """Optimize memory patterns for better performance"""
        optimization_results = {
            'optimized_patterns': 0,
            'removed_redundancies': 0,
            'consolidated_insights': 0,
            'performance_improvement': 0.0
        }
        
        try:
            # Analyze current patterns
            current_insights = await self.enhancement_engine.discover_cross_pattern_insights(memories)
            
            # Remove redundant patterns
            unique_patterns = self._remove_redundant_patterns(current_insights)
            optimization_results['removed_redundancies'] = len(current_insights) - len(unique_patterns)
            
            # Consolidate similar insights
            consolidated = self._consolidate_insights(unique_patterns)
            optimization_results['consolidated_insights'] = len(unique_patterns) - len(consolidated)
            
            # Measure performance improvement
            optimization_results['performance_improvement'] = self._calculate_improvement()
            
            # Record optimization
            self.optimization_history.append({
                'timestamp': datetime.now().isoformat(),
                'results': optimization_results
            })
            
        except Exception as e:
            logger.error(f"Failed to optimize memory patterns: {e}")
        
        return optimization_results
    
    def _remove_redundant_patterns(self, insights: List[MemoryInsight]) -> List[MemoryInsight]:
        """Remove redundant patterns based on similarity"""
        unique_insights = []
        seen_descriptions = set()
        
        for insight in insights:
            # Simple deduplication by description similarity
            key = insight.description[:50]  # Use first 50 chars as key
            if key not in seen_descriptions:
                seen_descriptions.add(key)
                unique_insights.append(insight)
        
        return unique_insights
    
    def _consolidate_insights(self, insights: List[MemoryInsight]) -> List[MemoryInsight]:
        """Consolidate similar insights"""
        # Group by insight type
        grouped = {}
        for insight in insights:
            if insight.insight_type not in grouped:
                grouped[insight.insight_type] = []
            grouped[insight.insight_type].append(insight)
        
        # Consolidate each group
        consolidated = []
        for insight_type, group in grouped.items():
            if len(group) > 1:
                # Create consolidated insight
                consolidated_insight = MemoryInsight(
                    insight_id=f"consolidated_{int(datetime.now().timestamp())}",
                    insight_type=insight_type,
                    description=f"Consolidated {len(group)} insights of type {insight_type}",
                    confidence=np.mean([i.confidence for i in group]),
                    supporting_evidence=[e for i in group for e in i.supporting_evidence[:2]],
                    recommendations=list(set(r for i in group for r in i.recommendations[:2])),
                    metadata={'consolidated_count': len(group)}
                )
                consolidated.append(consolidated_insight)
            else:
                consolidated.extend(group)
        
        return consolidated
    
    def _calculate_improvement(self) -> float:
        """Calculate performance improvement from optimization"""
        if len(self.optimization_history) < 2:
            return 0.0
        
        # Compare with previous optimization
        prev = self.optimization_history[-2]['results'] if len(self.optimization_history) >= 2 else {}
        curr = self.optimization_history[-1]['results'] if self.optimization_history else {}
        
        # Simple improvement metric
        prev_redundancy = prev.get('removed_redundancies', 0) + prev.get('consolidated_insights', 0)
        curr_redundancy = curr.get('removed_redundancies', 0) + curr.get('consolidated_insights', 0)
        
        if prev_redundancy > 0:
            improvement = (curr_redundancy - prev_redundancy) / prev_redundancy
        else:
            improvement = 0.0
        
        return max(-1.0, min(1.0, improvement))  # Clamp to [-1, 1]