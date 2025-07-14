"""
Chain-of-Thought Memory Reasoning
Advanced reasoning engine for complex pattern recognition and decision making in memory systems
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from pathlib import Path

# Import existing tools
from .semantic_storage import MemoryItem, MemoryContext, MemoryType
from .intelligent_retrieval import RetrievalStrategy

logger = logging.getLogger(__name__)


class ReasoningType(Enum):
    """Types of chain-of-thought reasoning"""
    PATTERN_ANALYSIS = "pattern_analysis"
    CAUSAL_INFERENCE = "causal_inference"
    TEMPORAL_REASONING = "temporal_reasoning"
    CONTEXTUAL_LINKING = "contextual_linking"
    PREDICTIVE_REASONING = "predictive_reasoning"
    ANALOGICAL_REASONING = "analogical_reasoning"


@dataclass
class ReasoningStep:
    """Individual step in chain-of-thought reasoning"""
    step_id: str
    step_type: ReasoningType
    description: str
    input_data: Dict[str, Any]
    reasoning_process: str
    output_data: Dict[str, Any]
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ReasoningChain:
    """Complete chain of reasoning steps"""
    chain_id: str
    purpose: str
    steps: List[ReasoningStep]
    final_conclusion: Dict[str, Any]
    overall_confidence: float
    created_at: datetime = field(default_factory=datetime.now)
    reasoning_time: float = 0.0


@dataclass
class ReasoningQuery:
    """Query for chain-of-thought reasoning"""
    query_text: str
    context: MemoryContext
    reasoning_types: List[ReasoningType]
    max_steps: int = 10
    confidence_threshold: float = 0.6
    include_analogies: bool = True
    depth_level: str = "medium"  # shallow, medium, deep


class ChainOfThoughtReasoner:
    """Advanced reasoning engine using chain-of-thought methodology"""
    
    def __init__(self, semantic_store, embedding_manager):
        self.semantic_store = semantic_store
        self.embedding_manager = embedding_manager
        self.reasoning_cache = {}
        self.pattern_library = {}
        
        # Reasoning templates for different types
        self.reasoning_templates = self._initialize_reasoning_templates()
        
        # Success patterns learned over time
        self.success_patterns = []
        
    def _initialize_reasoning_templates(self) -> Dict[ReasoningType, Dict[str, str]]:
        """Initialize reasoning templates for different thinking patterns"""
        return {
            ReasoningType.PATTERN_ANALYSIS: {
                "prompt": "Analyze the following memories for patterns: {memories}. Look for recurring themes, similar contexts, and behavioral patterns.",
                "process": "1. Extract key features from memories\n2. Group similar features\n3. Identify recurring patterns\n4. Assess pattern strength and significance"
            },
            ReasoningType.CAUSAL_INFERENCE: {
                "prompt": "Examine causal relationships in: {memories}. Identify cause-effect chains and contributing factors.",
                "process": "1. Identify potential causes and effects\n2. Analyze temporal sequences\n3. Consider confounding variables\n4. Establish causal strength"
            },
            ReasoningType.TEMPORAL_REASONING: {
                "prompt": "Analyze temporal patterns and sequences in: {memories}. Consider timing, duration, and chronological relationships.",
                "process": "1. Extract temporal features\n2. Identify sequences and cycles\n3. Analyze timing patterns\n4. Predict temporal trends"
            },
            ReasoningType.CONTEXTUAL_LINKING: {
                "prompt": "Find contextual connections between: {memories}. Look for shared contexts, environments, and situations.",
                "process": "1. Extract contextual features\n2. Calculate context similarity\n3. Identify shared elements\n4. Map contextual networks"
            },
            ReasoningType.PREDICTIVE_REASONING: {
                "prompt": "Based on patterns in: {memories}, predict likely future scenarios and outcomes.",
                "process": "1. Identify historical patterns\n2. Analyze trend directions\n3. Consider external factors\n4. Generate probabilistic predictions"
            },
            ReasoningType.ANALOGICAL_REASONING: {
                "prompt": "Find analogies and similar patterns between: {memories} and known successful cases.",
                "process": "1. Extract structural patterns\n2. Find analogous situations\n3. Map similarities and differences\n4. Transfer applicable insights"
            }
        }
    
    async def reason_about_memories(self, query: ReasoningQuery) -> ReasoningChain:
        """Perform chain-of-thought reasoning on memories"""
        start_time = time.time()
        
        # Generate unique chain ID
        chain_id = f"reasoning_{int(time.time())}_{hash(query.query_text) % 10000}"
        
        logger.info(f"Starting chain-of-thought reasoning for: {query.query_text[:50]}")
        
        # Step 1: Retrieve relevant memories
        relevant_memories = await self._retrieve_relevant_memories(query)
        
        # Step 2: Execute reasoning chain
        reasoning_steps = []
        current_data = {"memories": relevant_memories, "query": query.query_text}
        
        for i, reasoning_type in enumerate(query.reasoning_types):
            if len(reasoning_steps) >= query.max_steps:
                break
                
            step = await self._execute_reasoning_step(
                step_id=f"{chain_id}_step_{i}",
                reasoning_type=reasoning_type,
                input_data=current_data,
                query=query
            )
            
            if step.confidence >= query.confidence_threshold:
                reasoning_steps.append(step)
                current_data.update(step.output_data)
            else:
                logger.warning(f"Skipping step {i} due to low confidence: {step.confidence}")
        
        # Step 3: Synthesize final conclusion
        final_conclusion = await self._synthesize_conclusion(reasoning_steps, query)
        
        # Step 4: Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(reasoning_steps)
        
        reasoning_time = time.time() - start_time
        
        # Create reasoning chain
        chain = ReasoningChain(
            chain_id=chain_id,
            purpose=query.query_text,
            steps=reasoning_steps,
            final_conclusion=final_conclusion,
            overall_confidence=overall_confidence,
            reasoning_time=reasoning_time
        )
        
        # Cache the reasoning chain
        self.reasoning_cache[chain_id] = chain
        
        logger.info(f"Completed reasoning chain {chain_id} with {len(reasoning_steps)} steps in {reasoning_time:.2f}s")
        
        return chain
    
    async def _retrieve_relevant_memories(self, query: ReasoningQuery) -> List[MemoryItem]:
        """Retrieve memories relevant to the reasoning query"""
        try:
            # Use multiple retrieval strategies for comprehensive coverage
            strategies = [
                RetrievalStrategy.SEMANTIC,
                RetrievalStrategy.CONTEXTUAL,
                RetrievalStrategy.TEMPORAL
            ]
            
            all_memories = []
            for strategy in strategies:
                # Create retrieval query
                from .intelligent_retrieval import MemoryQuery
                memory_query = MemoryQuery(
                    query_text=query.query_text,
                    context=query.context,
                    max_results=20,
                    similarity_threshold=0.3,
                    strategy=strategy,
                    include_expired=False
                )
                
                memories = await self.semantic_store.search_memories(memory_query)
                all_memories.extend(memories)
            
            # Remove duplicates and sort by relevance
            unique_memories = {}
            for memory in all_memories:
                if memory.memory_id not in unique_memories:
                    unique_memories[memory.memory_id] = memory
                elif hasattr(memory, 'similarity_score') and hasattr(unique_memories[memory.memory_id], 'similarity_score'):
                    if memory.similarity_score > unique_memories[memory.memory_id].similarity_score:
                        unique_memories[memory.memory_id] = memory
            
            # Sort by similarity and importance
            sorted_memories = sorted(
                unique_memories.values(),
                key=lambda m: (getattr(m, 'similarity_score', 0) * 0.7 + m.importance * 0.3),
                reverse=True
            )
            
            return sorted_memories[:30]  # Limit to top 30 memories
            
        except Exception as e:
            logger.error(f"Failed to retrieve relevant memories: {e}")
            return []
    
    async def _execute_reasoning_step(self, step_id: str, reasoning_type: ReasoningType, 
                                    input_data: Dict[str, Any], query: ReasoningQuery) -> ReasoningStep:
        """Execute a single reasoning step"""
        try:
            template = self.reasoning_templates[reasoning_type]
            
            # Format the reasoning prompt
            memories = input_data.get("memories", [])
            memory_texts = [m.content for m in memories[:10]]  # Limit to avoid token limits
            
            reasoning_prompt = template["prompt"].format(
                memories="\n".join(memory_texts[:5])  # Use top 5 for reasoning
            )
            
            # Execute reasoning based on type
            output_data = {}
            confidence = 0.0
            reasoning_process = template["process"]
            
            if reasoning_type == ReasoningType.PATTERN_ANALYSIS:
                output_data, confidence = await self._analyze_patterns(memories)
            elif reasoning_type == ReasoningType.CAUSAL_INFERENCE:
                output_data, confidence = await self._infer_causality(memories)
            elif reasoning_type == ReasoningType.TEMPORAL_REASONING:
                output_data, confidence = await self._reason_temporally(memories)
            elif reasoning_type == ReasoningType.CONTEXTUAL_LINKING:
                output_data, confidence = await self._link_contexts(memories)
            elif reasoning_type == ReasoningType.PREDICTIVE_REASONING:
                output_data, confidence = await self._predict_outcomes(memories, input_data)
            elif reasoning_type == ReasoningType.ANALOGICAL_REASONING:
                output_data, confidence = await self._find_analogies(memories, query)
            
            return ReasoningStep(
                step_id=step_id,
                step_type=reasoning_type,
                description=f"Executing {reasoning_type.value} on {len(memories)} memories",
                input_data={"memory_count": len(memories), "query": query.query_text},
                reasoning_process=reasoning_process,
                output_data=output_data,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Failed to execute reasoning step {step_id}: {e}")
            return ReasoningStep(
                step_id=step_id,
                step_type=reasoning_type,
                description=f"Failed to execute {reasoning_type.value}",
                input_data=input_data,
                reasoning_process="Error in execution",
                output_data={"error": str(e)},
                confidence=0.0
            )
    
    async def _analyze_patterns(self, memories: List[MemoryItem]) -> Tuple[Dict[str, Any], float]:
        """Analyze patterns in memories"""
        try:
            if not memories:
                return {"patterns": []}, 0.0
            
            patterns = []
            confidence_scores = []
            
            # Analyze content patterns
            content_patterns = self._extract_content_patterns(memories)
            patterns.extend(content_patterns)
            
            # Analyze temporal patterns
            temporal_patterns = self._extract_temporal_patterns(memories)
            patterns.extend(temporal_patterns)
            
            # Analyze context patterns
            context_patterns = self._extract_context_patterns(memories)
            patterns.extend(context_patterns)
            
            # Calculate confidence based on pattern strength
            for pattern in patterns:
                confidence_scores.append(pattern.get("strength", 0.0))
            
            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            
            return {
                "patterns": patterns,
                "pattern_count": len(patterns),
                "strongest_pattern": max(patterns, key=lambda x: x.get("strength", 0)) if patterns else None
            }, min(avg_confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            return {"patterns": [], "error": str(e)}, 0.0
    
    async def _infer_causality(self, memories: List[MemoryItem]) -> Tuple[Dict[str, Any], float]:
        """Infer causal relationships between memories"""
        try:
            causal_chains = []
            
            # Sort memories by timestamp
            sorted_memories = sorted(memories, key=lambda m: m.created_at)
            
            # Look for temporal sequences that might indicate causality
            for i in range(len(sorted_memories) - 1):
                current = sorted_memories[i]
                next_mem = sorted_memories[i + 1]
                
                # Check temporal proximity (within reasonable timeframe)
                time_diff = (next_mem.created_at - current.created_at).total_seconds()
                if time_diff < 3600 * 24:  # Within 24 hours
                    
                    # Check content similarity for potential causality
                    content_similarity = await self._calculate_semantic_similarity(
                        current.content, next_mem.content
                    )
                    
                    if content_similarity > 0.3:  # Some relation
                        causal_chain = {
                            "cause": {
                                "memory_id": current.memory_id,
                                "content": current.content[:100],
                                "timestamp": current.created_at.isoformat()
                            },
                            "effect": {
                                "memory_id": next_mem.memory_id,
                                "content": next_mem.content[:100],
                                "timestamp": next_mem.created_at.isoformat()
                            },
                            "time_difference": time_diff,
                            "causal_strength": min(content_similarity * 0.8, 1.0)
                        }
                        causal_chains.append(causal_chain)
            
            # Calculate overall confidence
            confidences = [chain["causal_strength"] for chain in causal_chains]
            avg_confidence = np.mean(confidences) if confidences else 0.0
            
            return {
                "causal_chains": causal_chains,
                "chain_count": len(causal_chains),
                "strongest_causal_link": max(causal_chains, key=lambda x: x["causal_strength"]) if causal_chains else None
            }, min(avg_confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Causal inference failed: {e}")
            return {"causal_chains": [], "error": str(e)}, 0.0
    
    async def _reason_temporally(self, memories: List[MemoryItem]) -> Tuple[Dict[str, Any], float]:
        """Perform temporal reasoning on memories"""
        try:
            # Analyze temporal distribution
            timestamps = [m.created_at for m in memories]
            
            if len(timestamps) < 2:
                return {"temporal_patterns": []}, 0.0
            
            # Calculate time spans and intervals
            earliest = min(timestamps)
            latest = max(timestamps)
            total_span = (latest - earliest).total_seconds()
            
            # Find temporal clusters
            clusters = self._find_temporal_clusters(memories)
            
            # Identify periodic patterns
            periodic_patterns = self._find_periodic_patterns(memories)
            
            # Calculate confidence based on pattern regularity
            confidence = 0.0
            if clusters:
                confidence += 0.4
            if periodic_patterns:
                confidence += 0.4
            if total_span > 0:
                confidence += 0.2
            
            return {
                "temporal_span": total_span,
                "memory_count": len(memories),
                "temporal_clusters": clusters,
                "periodic_patterns": periodic_patterns,
                "earliest_memory": earliest.isoformat(),
                "latest_memory": latest.isoformat()
            }, min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Temporal reasoning failed: {e}")
            return {"temporal_patterns": [], "error": str(e)}, 0.0
    
    async def _link_contexts(self, memories: List[MemoryItem]) -> Tuple[Dict[str, Any], float]:
        """Link memories by contextual similarities"""
        try:
            context_groups = {}
            
            for memory in memories:
                if memory.context:
                    # Group by context attributes
                    context_key = self._generate_context_key(memory.context)
                    
                    if context_key not in context_groups:
                        context_groups[context_key] = []
                    context_groups[context_key].append(memory)
            
            # Find context links
            context_links = []
            for context_key, group_memories in context_groups.items():
                if len(group_memories) > 1:
                    context_links.append({
                        "context_signature": context_key,
                        "memory_count": len(group_memories),
                        "memories": [m.memory_id for m in group_memories],
                        "strength": min(len(group_memories) / 10.0, 1.0)
                    })
            
            # Calculate confidence
            total_memories = len(memories)
            linked_memories = sum(link["memory_count"] for link in context_links)
            confidence = linked_memories / total_memories if total_memories > 0 else 0.0
            
            return {
                "context_links": context_links,
                "unique_contexts": len(context_groups),
                "link_strength": confidence
            }, min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Context linking failed: {e}")
            return {"context_links": [], "error": str(e)}, 0.0
    
    async def _predict_outcomes(self, memories: List[MemoryItem], input_data: Dict[str, Any]) -> Tuple[Dict[str, Any], float]:
        """Predict future outcomes based on memory patterns"""
        try:
            # Analyze historical patterns for prediction
            patterns = []
            
            # Group memories by outcomes/results
            outcome_patterns = self._extract_outcome_patterns(memories)
            
            # Generate predictions
            predictions = []
            for pattern in outcome_patterns:
                prediction = {
                    "predicted_outcome": pattern["outcome"],
                    "confidence": pattern["confidence"],
                    "supporting_evidence": pattern["evidence_count"],
                    "pattern_frequency": pattern["frequency"]
                }
                predictions.append(prediction)
            
            # Sort by confidence
            predictions.sort(key=lambda x: x["confidence"], reverse=True)
            
            # Calculate overall confidence
            confidences = [p["confidence"] for p in predictions]
            avg_confidence = np.mean(confidences) if confidences else 0.0
            
            return {
                "predictions": predictions[:5],  # Top 5 predictions
                "prediction_count": len(predictions),
                "highest_confidence_prediction": predictions[0] if predictions else None
            }, min(avg_confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Predictive reasoning failed: {e}")
            return {"predictions": [], "error": str(e)}, 0.0
    
    async def _find_analogies(self, memories: List[MemoryItem], query: ReasoningQuery) -> Tuple[Dict[str, Any], float]:
        """Find analogous patterns and situations"""
        try:
            analogies = []
            
            # Extract structural patterns from memories
            patterns = self._extract_structural_patterns(memories)
            
            # Compare with known success patterns
            for pattern in patterns:
                for success_pattern in self.success_patterns:
                    similarity = self._calculate_pattern_similarity(pattern, success_pattern)
                    
                    if similarity > 0.6:  # Significant similarity
                        analogy = {
                            "current_pattern": pattern,
                            "analogous_pattern": success_pattern,
                            "similarity_score": similarity,
                            "transferable_insights": self._extract_transferable_insights(pattern, success_pattern)
                        }
                        analogies.append(analogy)
            
            # Sort by similarity
            analogies.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            # Calculate confidence
            avg_similarity = np.mean([a["similarity_score"] for a in analogies]) if analogies else 0.0
            
            return {
                "analogies": analogies[:3],  # Top 3 analogies
                "analogy_count": len(analogies),
                "best_analogy": analogies[0] if analogies else None
            }, min(avg_similarity, 1.0)
            
        except Exception as e:
            logger.error(f"Analogical reasoning failed: {e}")
            return {"analogies": [], "error": str(e)}, 0.0
    
    async def _synthesize_conclusion(self, reasoning_steps: List[ReasoningStep], query: ReasoningQuery) -> Dict[str, Any]:
        """Synthesize final conclusion from reasoning steps"""
        try:
            # Collect all insights from reasoning steps
            insights = []
            patterns = []
            predictions = []
            causal_chains = []
            
            for step in reasoning_steps:
                output = step.output_data
                
                if "patterns" in output:
                    patterns.extend(output["patterns"])
                if "predictions" in output:
                    predictions.extend(output["predictions"])
                if "causal_chains" in output:
                    causal_chains.extend(output["causal_chains"])
                if "context_links" in output:
                    insights.append(f"Found {len(output['context_links'])} contextual connections")
                if "analogies" in output:
                    insights.append(f"Identified {len(output['analogies'])} analogous patterns")
            
            # Generate summary insights
            summary = {
                "query": query.query_text,
                "reasoning_steps_completed": len(reasoning_steps),
                "key_insights": insights,
                "patterns_discovered": len(patterns),
                "predictions_made": len(predictions),
                "causal_relationships": len(causal_chains),
                "synthesis": self._generate_synthesis_text(reasoning_steps, query)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to synthesize conclusion: {e}")
            return {"error": str(e)}
    
    def _calculate_overall_confidence(self, reasoning_steps: List[ReasoningStep]) -> float:
        """Calculate overall confidence for the reasoning chain"""
        if not reasoning_steps:
            return 0.0
        
        # Weight confidence by step importance
        weighted_confidences = []
        for step in reasoning_steps:
            weight = 1.0
            if step.step_type == ReasoningType.PATTERN_ANALYSIS:
                weight = 1.2  # Pattern analysis is particularly important
            elif step.step_type == ReasoningType.PREDICTIVE_REASONING:
                weight = 1.1  # Predictions are valuable
            
            weighted_confidences.append(step.confidence * weight)
        
        return min(np.mean(weighted_confidences), 1.0)
    
    # Helper methods for pattern extraction and analysis
    
    def _extract_content_patterns(self, memories: List[MemoryItem]) -> List[Dict[str, Any]]:
        """Extract patterns from memory content"""
        patterns = []
        
        # Simple keyword frequency analysis
        word_counts = {}
        for memory in memories:
            words = memory.content.lower().split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    word_counts[word] = word_counts.get(word, 0) + 1
        
        # Find frequent patterns
        total_memories = len(memories)
        for word, count in word_counts.items():
            if count >= 2 and count / total_memories > 0.2:  # Appears in >20% of memories
                patterns.append({
                    "type": "keyword_pattern",
                    "pattern": word,
                    "frequency": count,
                    "strength": min(count / total_memories, 1.0)
                })
        
        return patterns
    
    def _extract_temporal_patterns(self, memories: List[MemoryItem]) -> List[Dict[str, Any]]:
        """Extract temporal patterns from memories"""
        patterns = []
        
        if len(memories) < 2:
            return patterns
        
        # Analyze creation time patterns
        timestamps = [m.created_at for m in memories]
        hours = [t.hour for t in timestamps]
        days = [t.weekday() for t in timestamps]
        
        # Find most common hours and days
        hour_counts = {}
        day_counts = {}
        
        for hour in hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        for day in days:
            day_counts[day] = day_counts.get(day, 0) + 1
        
        # Most active hour
        if hour_counts:
            most_active_hour = max(hour_counts, key=hour_counts.get)
            patterns.append({
                "type": "temporal_pattern",
                "pattern": f"most_active_hour_{most_active_hour}",
                "frequency": hour_counts[most_active_hour],
                "strength": hour_counts[most_active_hour] / len(memories)
            })
        
        # Most active day
        if day_counts:
            most_active_day = max(day_counts, key=day_counts.get)
            patterns.append({
                "type": "temporal_pattern",
                "pattern": f"most_active_day_{most_active_day}",
                "frequency": day_counts[most_active_day],
                "strength": day_counts[most_active_day] / len(memories)
            })
        
        return patterns
    
    def _extract_context_patterns(self, memories: List[MemoryItem]) -> List[Dict[str, Any]]:
        """Extract patterns from memory contexts"""
        patterns = []
        
        context_attributes = {}
        for memory in memories:
            if memory.context:
                context_dict = memory.context.to_dict() if hasattr(memory.context, 'to_dict') else {}
                for key, value in context_dict.items():
                    if key not in context_attributes:
                        context_attributes[key] = {}
                    
                    value_str = str(value)
                    if value_str not in context_attributes[key]:
                        context_attributes[key][value_str] = 0
                    context_attributes[key][value_str] += 1
        
        # Find common context patterns
        total_memories = len(memories)
        for attr, values in context_attributes.items():
            for value, count in values.items():
                if count / total_memories > 0.3:  # Appears in >30% of memories
                    patterns.append({
                        "type": "context_pattern",
                        "pattern": f"{attr}={value}",
                        "frequency": count,
                        "strength": count / total_memories
                    })
        
        return patterns
    
    async def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        try:
            # Use embedding manager to calculate similarity
            embedding1 = await self.embedding_manager.get_embeddings([text1])
            embedding2 = await self.embedding_manager.get_embeddings([text2])
            
            if embedding1 and embedding2:
                # Calculate cosine similarity
                similarity = np.dot(embedding1[0], embedding2[0]) / (
                    np.linalg.norm(embedding1[0]) * np.linalg.norm(embedding2[0])
                )
                return float(similarity)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate semantic similarity: {e}")
            return 0.0
    
    def _find_temporal_clusters(self, memories: List[MemoryItem]) -> List[Dict[str, Any]]:
        """Find temporal clusters in memories"""
        if len(memories) < 2:
            return []
        
        # Sort by timestamp
        sorted_memories = sorted(memories, key=lambda m: m.created_at)
        clusters = []
        current_cluster = [sorted_memories[0]]
        
        for i in range(1, len(sorted_memories)):
            time_diff = (sorted_memories[i].created_at - sorted_memories[i-1].created_at).total_seconds()
            
            # If within 1 hour, add to current cluster
            if time_diff <= 3600:
                current_cluster.append(sorted_memories[i])
            else:
                # Start new cluster if current has multiple memories
                if len(current_cluster) > 1:
                    clusters.append({
                        "start_time": current_cluster[0].created_at.isoformat(),
                        "end_time": current_cluster[-1].created_at.isoformat(),
                        "memory_count": len(current_cluster),
                        "duration": (current_cluster[-1].created_at - current_cluster[0].created_at).total_seconds()
                    })
                current_cluster = [sorted_memories[i]]
        
        # Add final cluster if it has multiple memories
        if len(current_cluster) > 1:
            clusters.append({
                "start_time": current_cluster[0].created_at.isoformat(),
                "end_time": current_cluster[-1].created_at.isoformat(),
                "memory_count": len(current_cluster),
                "duration": (current_cluster[-1].created_at - current_cluster[0].created_at).total_seconds()
            })
        
        return clusters
    
    def _find_periodic_patterns(self, memories: List[MemoryItem]) -> List[Dict[str, Any]]:
        """Find periodic patterns in memory creation"""
        patterns = []
        
        if len(memories) < 3:
            return patterns
        
        # Analyze daily patterns
        timestamps = [m.created_at for m in memories]
        hours = [t.hour for t in timestamps]
        
        # Check for regular hourly patterns
        hour_intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds() / 3600  # Hours
            hour_intervals.append(interval)
        
        # Look for common intervals
        interval_counts = {}
        for interval in hour_intervals:
            rounded_interval = round(interval)
            if rounded_interval > 0:
                interval_counts[rounded_interval] = interval_counts.get(rounded_interval, 0) + 1
        
        # Find periodic patterns
        for interval, count in interval_counts.items():
            if count >= 2 and count / len(hour_intervals) > 0.3:
                patterns.append({
                    "type": "periodic_pattern",
                    "interval_hours": interval,
                    "frequency": count,
                    "strength": count / len(hour_intervals)
                })
        
        return patterns
    
    def _generate_context_key(self, context: MemoryContext) -> str:
        """Generate a key for grouping similar contexts"""
        try:
            context_dict = context.to_dict() if hasattr(context, 'to_dict') else {}
            # Create a hash of relevant context attributes
            key_elements = []
            for attr in ['project', 'task', 'user', 'environment']:
                if attr in context_dict:
                    key_elements.append(f"{attr}:{context_dict[attr]}")
            
            return "|".join(sorted(key_elements))
            
        except Exception:
            return "unknown_context"
    
    def _extract_outcome_patterns(self, memories: List[MemoryItem]) -> List[Dict[str, Any]]:
        """Extract patterns related to outcomes and results"""
        outcome_patterns = []
        
        # Look for outcome indicators in memory content
        outcome_keywords = ['success', 'failed', 'completed', 'error', 'resolved', 'achieved', 'accomplished']
        
        for keyword in outcome_keywords:
            matches = [m for m in memories if keyword.lower() in m.content.lower()]
            if len(matches) >= 2:
                outcome_patterns.append({
                    "outcome": keyword,
                    "evidence_count": len(matches),
                    "confidence": min(len(matches) / len(memories), 1.0),
                    "frequency": len(matches) / len(memories)
                })
        
        return outcome_patterns
    
    def _extract_structural_patterns(self, memories: List[MemoryItem]) -> List[Dict[str, Any]]:
        """Extract structural patterns for analogical reasoning"""
        patterns = []
        
        # Analyze memory structure patterns
        for memory in memories:
            pattern = {
                "content_length": len(memory.content),
                "tag_count": len(memory.tags),
                "importance": memory.importance,
                "has_context": memory.context is not None,
                "memory_type": memory.memory_type.value
            }
            patterns.append(pattern)
        
        return patterns
    
    def _calculate_pattern_similarity(self, pattern1: Dict[str, Any], pattern2: Dict[str, Any]) -> float:
        """Calculate similarity between two patterns"""
        # Simple similarity based on matching attributes
        matching_attrs = 0
        total_attrs = len(set(pattern1.keys()) | set(pattern2.keys()))
        
        for key in pattern1:
            if key in pattern2:
                if pattern1[key] == pattern2[key]:
                    matching_attrs += 1
                elif isinstance(pattern1[key], (int, float)) and isinstance(pattern2[key], (int, float)):
                    # For numeric values, use ratio similarity
                    ratio = min(pattern1[key], pattern2[key]) / max(pattern1[key], pattern2[key])
                    if ratio > 0.8:
                        matching_attrs += ratio
        
        return matching_attrs / total_attrs if total_attrs > 0 else 0.0
    
    def _extract_transferable_insights(self, current_pattern: Dict[str, Any], success_pattern: Dict[str, Any]) -> List[str]:
        """Extract insights that can be transferred from successful patterns"""
        insights = []
        
        # Simple heuristic-based insight extraction
        if success_pattern.get("importance", 0) > current_pattern.get("importance", 0):
            insights.append("Consider increasing the importance rating for similar memories")
        
        if success_pattern.get("tag_count", 0) > current_pattern.get("tag_count", 0):
            insights.append("Adding more descriptive tags could improve categorization")
        
        if success_pattern.get("has_context") and not current_pattern.get("has_context"):
            insights.append("Including contextual information enhances memory effectiveness")
        
        return insights
    
    def _generate_synthesis_text(self, reasoning_steps: List[ReasoningStep], query: ReasoningQuery) -> str:
        """Generate synthesis text from reasoning steps"""
        try:
            synthesis_parts = []
            
            # Summarize findings from each reasoning type
            for step in reasoning_steps:
                if step.step_type == ReasoningType.PATTERN_ANALYSIS:
                    pattern_count = step.output_data.get("pattern_count", 0)
                    if pattern_count > 0:
                        synthesis_parts.append(f"Identified {pattern_count} significant patterns")
                
                elif step.step_type == ReasoningType.CAUSAL_INFERENCE:
                    chain_count = step.output_data.get("chain_count", 0)
                    if chain_count > 0:
                        synthesis_parts.append(f"Found {chain_count} potential causal relationships")
                
                elif step.step_type == ReasoningType.PREDICTIVE_REASONING:
                    pred_count = step.output_data.get("prediction_count", 0)
                    if pred_count > 0:
                        synthesis_parts.append(f"Generated {pred_count} predictive insights")
                
                elif step.step_type == ReasoningType.ANALOGICAL_REASONING:
                    analogy_count = step.output_data.get("analogy_count", 0)
                    if analogy_count > 0:
                        synthesis_parts.append(f"Discovered {analogy_count} analogous patterns")
            
            if synthesis_parts:
                synthesis = f"Chain-of-thought analysis for '{query.query_text}' revealed: " + "; ".join(synthesis_parts) + "."
            else:
                synthesis = f"Chain-of-thought analysis completed for '{query.query_text}' with limited insights due to insufficient data patterns."
            
            return synthesis
            
        except Exception as e:
            logger.error(f"Failed to generate synthesis text: {e}")
            return f"Analysis completed for '{query.query_text}' with processing challenges."
    
    def add_success_pattern(self, pattern: Dict[str, Any]):
        """Add a success pattern to the library for future analogical reasoning"""
        self.success_patterns.append(pattern)
        
        # Limit size to prevent memory bloat
        if len(self.success_patterns) > 100:
            self.success_patterns = self.success_patterns[-100:]