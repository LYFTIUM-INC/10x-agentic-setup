"""
Context-Aware Memory MCP Server
Intelligent memory management with semantic storage, retrieval, and predictive loading
"""

import asyncio
import logging
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import hashlib
import uuid

# Add shared utilities to path
sys.path.append(str(Path(__file__).parent.parent.parent / "shared" / "src"))

from base_server import BaseMCPServer, ServerConfig
from utils.ml_utils import EmbeddingManager, EmbeddingConfig, VectorDatabase
from utils.config_utils import MCPServerSettings, ConfigManager
from tools.semantic_storage import SemanticMemoryStore, MemoryItem, MemoryContext, MemoryQuery, MemoryType, AccessLevel
from tools.intelligent_retrieval import IntelligentRetriever, RetrievalStrategy, ContextAnalyzer
from tools.predictive_loading import PredictiveLoader, MemoryPrediction, AccessPattern
from tools.cot_memory_reasoning import ChainOfThoughtReasoner, ReasoningQuery, ReasoningType
from tools.few_shot_learning import FewShotLearningEngine, FewShotQuery, PatternType
from tools.federated_memory import FederatedMemoryManager, PrivacyPolicy, PrivacyLevel, SharingScope
from tools.memory_enhancements import MemoryEnhancementEngine, MemoryOptimizer
from tools.memory_metrics import MemoryMetricsCollector, MetricType

from pydantic import BaseModel, Field
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryStoreRequest(BaseModel):
    """Request to store memory item"""
    content: str = Field(..., description="Content to store")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context metadata")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    importance: float = Field(1.0, description="Importance score (0-1)")
    expires_at: Optional[datetime] = Field(None, description="Expiration datetime")


class MemoryRetrievalRequest(BaseModel):
    """Request to retrieve memory items"""
    query: str = Field(..., description="Search query")
    context: Dict[str, Any] = Field(default_factory=dict, description="Current context")
    max_results: int = Field(10, description="Maximum number of results")
    similarity_threshold: float = Field(0.5, description="Minimum similarity score")
    strategy: str = Field("semantic", description="Retrieval strategy")
    include_expired: bool = Field(False, description="Include expired items")


class ContextAwareMemoryServer(BaseMCPServer):
    """Context-Aware Memory MCP Server"""
    
    def __init__(self, config: MCPServerSettings):
        # Initialize base server
        super().__init__(ServerConfig(
            name=config.server_name,
            version=config.server_version,
            debug=config.debug,
            max_workers=config.max_workers,
            cache_ttl=config.cache_ttl
        ))
        
        self.settings = config
        self.embedding_manager = None
        self.semantic_store = None
        self.intelligent_retriever = None
        self.predictive_loader = None
        
        # New enhanced components
        self.cot_reasoner = None
        self.few_shot_engine = None
        self.federated_manager = None
        
        # Advanced enhancement components
        self.enhancement_engine = None
        self.memory_optimizer = None
        self.metrics_collector = None
        
        self.memory_stats = {
            'total_memories': 0,
            'total_retrievals': 0,
            'cache_hits': 0,
            'predictions_made': 0,
            'reasoning_chains': 0,
            'patterns_learned': 0,
            'federated_shares': 0,
            'cross_pattern_insights': 0,
            'optimizations_performed': 0
        }
        
        # Register tools
        self._register_tools()
        
        # Register prompts
        self._register_prompts()
    
    def _register_tools(self):
        """Register all MCP tools for memory management"""
        
        @self.register_tool(
            name="store_memory",
            description="Store content with semantic indexing and context awareness"
        )
        async def store_memory(request: MemoryStoreRequest) -> Dict[str, Any]:
            """Store memory item with semantic indexing"""
            return await self._store_memory(request)
        
        @self.register_tool(
            name="retrieve_memories", 
            description="Intelligently retrieve relevant memories based on context"
        )
        async def retrieve_memories(request: MemoryRetrievalRequest) -> List[Dict[str, Any]]:
            """Retrieve memories using intelligent strategies"""
            return await self._retrieve_memories(request)
        
        @self.register_tool(
            name="predict_memory_needs",
            description="Predict future memory needs based on patterns and context"
        )
        async def predict_memory_needs(context: Dict[str, Any]) -> Dict[str, Any]:
            """Predict memory needs using ML models"""
            return await self._predict_memory_needs(context)
        
        @self.register_tool(
            name="analyze_memory_patterns",
            description="Analyze memory access patterns and usage statistics"
        )
        async def analyze_memory_patterns(context: Dict[str, Any], include_patterns: bool = True, include_predictions: bool = True) -> Dict[str, Any]:
            """Analyze memory patterns and provide insights"""
            return await self._analyze_memory_patterns(context, include_patterns, include_predictions)
        
        @self.register_tool(
            name="get_preloaded_memory",
            description="Get a preloaded memory from the predictive cache"
        )
        async def get_preloaded_memory(memory_id: str) -> Optional[Dict[str, Any]]:
            """Get preloaded memory from cache"""
            return await self._get_preloaded_memory(memory_id)
        
        # New enhanced memory tools
        @self.register_tool(
            name="reason_about_memories",
            description="Perform chain-of-thought reasoning on memories for pattern recognition"
        )
        async def reason_about_memories(query_text: str, context: Dict[str, Any], reasoning_types: List[str] = ["pattern_analysis"], max_steps: int = 10) -> Dict[str, Any]:
            """Perform chain-of-thought reasoning on memories"""
            return await self._reason_about_memories(query_text, context, reasoning_types, max_steps)
        
        @self.register_tool(
            name="learn_from_examples",
            description="Learn patterns from few-shot examples for reuse"
        )
        async def learn_from_examples(examples: List[Dict[str, Any]], pattern_type: str = "success_pattern") -> Dict[str, Any]:
            """Learn patterns from few-shot examples"""
            return await self._learn_from_examples(examples, pattern_type)
        
        @self.register_tool(
            name="find_similar_patterns",
            description="Find learned patterns similar to current context"
        )
        async def find_similar_patterns(context: Dict[str, Any], input_features: Dict[str, Any], desired_outcome: str, max_patterns: int = 5) -> List[Dict[str, Any]]:
            """Find similar patterns for current context"""
            return await self._find_similar_patterns(context, input_features, desired_outcome, max_patterns)
        
        @self.register_tool(
            name="share_knowledge",
            description="Share knowledge with federated memory network"
        )
        async def share_knowledge(knowledge_type: str, content: Dict[str, Any], privacy_level: str = "medium", sharing_scope: str = "organization") -> Dict[str, Any]:
            """Share knowledge with federation"""
            return await self._share_knowledge(knowledge_type, content, privacy_level, sharing_scope)
        
        @self.register_tool(
            name="query_federation",
            description="Query federated memory network for knowledge"
        )
        async def query_federation(knowledge_types: List[str], context: Dict[str, Any], max_results: int = 10) -> List[Dict[str, Any]]:
            """Query federation for knowledge"""
            return await self._query_federation(knowledge_types, context, max_results)
        
        @self.register_tool(
            name="discover_memory_patterns",
            description="Automatically discover patterns from existing memories"
        )
        async def discover_memory_patterns(min_examples: int = 3, pattern_types: List[str] = []) -> Dict[str, Any]:
            """Discover patterns from memory data"""
            return await self._discover_memory_patterns(min_examples, pattern_types)
        
        @self.register_tool(
            name="get_enhanced_memory_stats",
            description="Get comprehensive statistics about enhanced memory capabilities"
        )
        async def get_enhanced_memory_stats() -> Dict[str, Any]:
            """Get enhanced memory statistics"""
            return await self._get_enhanced_memory_stats()
        
        # Advanced enhancement tools
        @self.register_tool(
            name="adaptive_reasoning",
            description="Perform adaptive reasoning combining CoT, few-shot, and federated insights"
        )
        async def adaptive_reasoning(query: str, context: Dict[str, Any]) -> Dict[str, Any]:
            """Perform adaptive reasoning across all systems"""
            return await self._adaptive_reasoning(query, context)
        
        @self.register_tool(
            name="discover_cross_patterns",
            description="Discover insights by connecting patterns across reasoning systems"
        )
        async def discover_cross_patterns(memory_count: int = 50) -> List[Dict[str, Any]]:
            """Discover cross-pattern insights"""
            return await self._discover_cross_patterns(memory_count)
        
        @self.register_tool(
            name="optimize_memory_system",
            description="Optimize memory system based on performance metrics"
        )
        async def optimize_memory_system() -> Dict[str, Any]:
            """Optimize memory system performance"""
            return await self._optimize_memory_system()
        
        @self.register_tool(
            name="get_performance_metrics",
            description="Get real-time performance metrics and health status"
        )
        async def get_performance_metrics() -> Dict[str, Any]:
            """Get performance metrics dashboard"""
            return await self._get_performance_metrics()
        
        @self.register_tool(
            name="continuous_learning_feedback",
            description="Provide feedback for continuous learning improvement"
        )
        async def continuous_learning_feedback(pattern_id: Optional[str], reasoning_chain_id: Optional[str], success: bool, outcome: str, context: Dict[str, Any]) -> Dict[str, Any]:
            """Process continuous learning feedback"""
            return await self._process_continuous_learning_feedback(
                pattern_id, reasoning_chain_id, success, outcome, context
            )
    
    async def _startup(self):
        """Initialize memory components on startup"""
        logger.info("Initializing Context-Aware Memory Server...")
        
        # Initialize embedding manager
        embedding_config = EmbeddingConfig(
            model_name=self.settings.embedding_model,
            device=self.settings.ml_device,
            max_length=self.settings.max_embedding_length,
            cache_dir=self.settings.model_cache_dir
        )
        
        self.embedding_manager = EmbeddingManager(embedding_config)
        await self.embedding_manager.load_model()
        
        # Initialize semantic memory store
        self.semantic_store = SemanticMemoryStore(
            embedding_manager=self.embedding_manager,
            vector_dimension=self.settings.vector_dimension,
            data_dir=self.settings.data_dir
        )
        await self.semantic_store.initialize()
        
        # Initialize intelligent retriever
        self.intelligent_retriever = IntelligentRetriever(
            semantic_store=self.semantic_store,
            embedding_manager=self.embedding_manager
        )
        
        # Initialize predictive loader
        self.predictive_loader = PredictiveLoader(
            semantic_store=self.semantic_store,
            retriever=self.intelligent_retriever
        )
        
        # Initialize enhanced memory components
        self.cot_reasoner = ChainOfThoughtReasoner(
            semantic_store=self.semantic_store,
            embedding_manager=self.embedding_manager
        )
        
        self.few_shot_engine = FewShotLearningEngine(
            semantic_store=self.semantic_store,
            embedding_manager=self.embedding_manager,
            data_dir=self.settings.data_dir
        )
        await self.few_shot_engine.initialize()
        
        # Initialize federated memory manager
        federation_config = {
            'node_id': self.settings.server_config.get('federation', {}).get('node_id', str(uuid.uuid4())),
            'node_name': self.settings.server_config.get('federation', {}).get('node_name', 'memory_node'),
            'organization': self.settings.server_config.get('federation', {}).get('organization', 'default_org'),
            'private_key': self.settings.server_config.get('federation', {}).get('private_key', 'default_key')
        }
        
        self.federated_manager = FederatedMemoryManager(
            semantic_store=self.semantic_store,
            embedding_manager=self.embedding_manager,
            data_dir=self.settings.data_dir,
            node_config=federation_config
        )
        await self.federated_manager.initialize()
        
        # Initialize advanced enhancement components
        self.enhancement_engine = MemoryEnhancementEngine(
            cot_reasoner=self.cot_reasoner,
            few_shot_engine=self.few_shot_engine,
            federated_manager=self.federated_manager
        )
        
        self.memory_optimizer = MemoryOptimizer(
            enhancement_engine=self.enhancement_engine
        )
        
        self.metrics_collector = MemoryMetricsCollector(
            window_size=1000,
            anomaly_threshold=3.0
        )
        
        # Set performance baselines
        self.metrics_collector.set_baseline(MetricType.LATENCY, 50.0)  # 50ms baseline
        self.metrics_collector.set_baseline(MetricType.MEMORY_USAGE, 200.0)  # 200MB baseline
        self.metrics_collector.set_baseline(MetricType.PATTERN_EFFECTIVENESS, 0.7)  # 70% effectiveness
        
        # Load existing memories
        await self._load_existing_memories()
        
        logger.info("Context-Aware Memory Server with enhanced capabilities initialized successfully")
    
    async def _shutdown(self):
        """Save state on shutdown"""
        if self.semantic_store:
            await self.semantic_store.save_state()
            logger.info("Memory state saved successfully")
        
        await super()._shutdown()
    
    async def _store_memory(self, request: MemoryStoreRequest) -> Dict[str, Any]:
        """Store memory item with semantic indexing"""
        try:
            start_time = time.time()
            
            # Create memory item
            memory_item = MemoryItem(
                content=request.content,
                context=MemoryContext(**request.context),
                tags=request.tags,
                importance=request.importance,
                expires_at=request.expires_at
            )
            
            # Store in semantic store
            memory_id = await self.semantic_store.store_memory(memory_item)
            
            # Update statistics
            self.memory_stats['total_memories'] += 1
            
            # Trigger predictive loading if enabled
            if self.predictive_loader:
                await self.predictive_loader.record_storage_event(memory_item)
            
            # Record metrics
            latency_ms = (time.time() - start_time) * 1000
            await self.metrics_collector.record_operation_latency('store_memory', latency_ms, True)
            
            logger.info(f"Stored memory {memory_id} with {len(request.content)} characters")
            
            return {
                'status': 'success',
                'memory_id': memory_id,
                'content_length': len(request.content),
                'stored_at': datetime.now().isoformat(),
                'importance': request.importance
            }
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            await self.metrics_collector.record_operation_latency('store_memory', 0, False)
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _retrieve_memories(self, request: MemoryRetrievalRequest) -> List[Dict[str, Any]]:
        """Retrieve memories using intelligent strategies"""
        try:
            start_time = time.time()
            
            # Create retrieval query
            query = MemoryQuery(
                query_text=request.query,
                context=MemoryContext(**request.context),
                max_results=request.max_results,
                similarity_threshold=request.similarity_threshold,
                strategy=RetrievalStrategy(request.strategy),
                include_expired=request.include_expired
            )
            
            # Retrieve memories using intelligent retriever
            memories = await self.intelligent_retriever.retrieve(query)
            
            # Convert to response format
            results = []
            for memory in memories:
                result = {
                    'memory_id': memory.memory_id,
                    'content': memory.content,
                    'context': memory.context.to_dict() if memory.context else {},
                    'tags': memory.tags,
                    'importance': memory.importance,
                    'created_at': memory.created_at.isoformat(),
                    'similarity_score': getattr(memory, 'similarity_score', 0.0),
                    'access_count': memory.access_count,
                    'last_accessed': memory.last_accessed.isoformat() if memory.last_accessed else None,
                    'memory_type': memory.memory_type.value,
                    'confidence': getattr(memory, 'confidence', 0.0)
                }
                results.append(result)
            
            # Update statistics
            self.memory_stats['total_retrievals'] += 1
            if len(memories) > 0:
                self.memory_stats['cache_hits'] += 1
            
            # Record access patterns for predictive loading
            if self.predictive_loader:
                await self.predictive_loader.record_retrieval_event(query, memories)
            
            # Record metrics
            latency_ms = (time.time() - start_time) * 1000
            await self.metrics_collector.record_operation_latency('retrieve_memories', latency_ms, True)
            await self.metrics_collector.record_metric(
                MetricType.ACCURACY,
                len(memories) / request.max_results if request.max_results > 0 else 0,
                context={'strategy': request.strategy}
            )
            
            logger.info(f"Retrieved {len(memories)} memories for query: {request.query[:50]}")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            await self.metrics_collector.record_operation_latency('retrieve_memories', 0, False)
            return []
    
    async def _predict_memory_needs(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict memory needs using ML models"""
        try:
            # Convert context dict to MemoryContext
            memory_context = MemoryContext(**context)
            
            # Use predictive loader to predict needs
            predictions = await self.predictive_loader.predict_needs(memory_context)
            
            # Update statistics
            self.memory_stats['predictions_made'] += 1
            
            return {
                'status': 'success',
                'predictions': predictions,
                'predicted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to predict memory needs: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _analyze_memory_patterns(self, context: Dict[str, Any], 
                                     include_patterns: bool = True, 
                                     include_predictions: bool = True) -> Dict[str, Any]:
        """Analyze memory patterns and provide insights"""
        try:
            # Use predictive loader to analyze patterns
            analysis = await self.predictive_loader.analyze_patterns(
                context=context,
                include_patterns=include_patterns,
                include_predictions=include_predictions
            )
            
            return {
                'status': 'success',
                'analysis': analysis,
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze memory patterns: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _get_preloaded_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get preloaded memory from cache"""
        try:
            memory = await self.predictive_loader.get_preloaded_memory(memory_id)
            
            if memory:
                return {
                    'status': 'success',
                    'memory': {
                        'memory_id': memory.memory_id,
                        'content': memory.content,
                        'context': memory.context.to_dict() if memory.context else {},
                        'tags': memory.tags,
                        'importance': memory.importance,
                        'created_at': memory.created_at.isoformat(),
                        'memory_type': memory.memory_type.value
                    },
                    'cached': True,
                    'retrieved_at': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'not_found',
                    'memory_id': memory_id,
                    'cached': False
                }
                
        except Exception as e:
            logger.error(f"Failed to get preloaded memory: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _register_prompts(self):
        """Register prompt templates for memory workflows"""
        
        @self.register_prompt(
            name="memory_recap",
            description="Summarize recent memories with context",
            arguments=[
                {
                    "name": "timeframe",
                    "description": "Time period: today, week, month",
                    "required": False
                },
                {
                    "name": "category",
                    "description": "Memory category to focus on",
                    "required": False
                }
            ]
        )
        async def memory_recap_prompt(timeframe: str = "today", category: Optional[str] = None) -> List[Dict[str, Any]]:
            """Prompt template for memory recap"""
            return [
                {
                    "role": "system",
                    "content": f"You are a memory assistant summarizing {timeframe}'s memories" + (f" in the {category} category" if category else "")
                },
                {
                    "role": "user",
                    "content": "Retrieve and summarize relevant memories using the retrieve_memories tool. Group by context and highlight important insights."
                }
            ]
        
        @self.register_prompt(
            name="predict_workflow",
            description="Predict next steps based on memory patterns",
            arguments=[
                {
                    "name": "confidence_threshold",
                    "description": "Minimum confidence for predictions (0.0-1.0)",
                    "required": False
                }
            ]
        )
        async def predict_workflow_prompt(confidence_threshold: float = 0.7) -> List[Dict[str, Any]]:
            """Prompt template for workflow prediction"""
            return [
                {
                    "role": "system",
                    "content": f"You are a workflow prediction assistant. Only suggest actions with confidence >= {confidence_threshold}."
                },
                {
                    "role": "user",
                    "content": "Use predict_next_memories to analyze patterns and suggest the most likely next actions. Explain the reasoning based on historical patterns."
                }
            ]
        
        @self.register_prompt(
            name="context_analysis",
            description="Analyze current context and retrieve relevant memories",
            arguments=[
                {
                    "name": "depth",
                    "description": "Analysis depth: shallow, medium, deep",
                    "required": False
                }
            ]
        )
        async def context_analysis_prompt(depth: str = "medium") -> List[Dict[str, Any]]:
            """Prompt template for context analysis"""
            return [
                {
                    "role": "system",
                    "content": f"You are a context analyst performing {depth} analysis of the current situation."
                },
                {
                    "role": "user",
                    "content": "Analyze the current context using analyze_context, then retrieve relevant memories with different strategies. Identify patterns and connections."
                }
            ]
        
        @self.register_prompt(
            name="memory_optimization",
            description="Optimize memory storage by identifying redundancies and patterns",
            arguments=[
                {
                    "name": "action",
                    "description": "Optimization action: analyze, consolidate, archive",
                    "required": True
                }
            ]
        )
        async def memory_optimization_prompt(action: str) -> List[Dict[str, Any]]:
            """Prompt template for memory optimization"""
            return [
                {
                    "role": "system",
                    "content": f"You are a memory optimization specialist tasked with {action} operations."
                },
                {
                    "role": "user",
                    "content": f"Use get_memory_stats and retrieve_memories to {action} the memory store. Identify redundant memories, extract patterns, and suggest optimizations."
                }
            ]
        
        @self.register_prompt(
            name="knowledge_extraction",
            description="Extract structured knowledge from unstructured memories",
            arguments=[
                {
                    "name": "format",
                    "description": "Output format: summary, bullets, graph, timeline",
                    "required": False
                }
            ]
        )
        async def knowledge_extraction_prompt(format: str = "summary") -> List[Dict[str, Any]]:
            """Prompt template for knowledge extraction"""
            return [
                {
                    "role": "system",
                    "content": f"You are a knowledge extraction expert. Present findings in {format} format."
                },
                {
                    "role": "user",
                    "content": "Retrieve memories across different contexts and time periods. Extract key insights, patterns, and learnings. Present structured knowledge from the unstructured memory data."
                }
            ]
    
    async def _load_existing_memories(self):
        """Load existing memories from storage"""
        try:
            if self.semantic_store:
                count = await self.semantic_store.load_existing_memories()
                self.memory_stats['total_memories'] = count
                logger.info(f"Loaded {count} existing memories")
        except Exception as e:
            logger.warning(f"Failed to load existing memories: {e}")
    
    # Enhanced memory capability implementations
    
    async def _reason_about_memories(self, query_text: str, context: Dict[str, Any], 
                                   reasoning_types: List[str], max_steps: int) -> Dict[str, Any]:
        """Perform chain-of-thought reasoning on memories"""
        try:
            # Convert string reasoning types to enum
            reasoning_type_map = {
                'pattern_analysis': ReasoningType.PATTERN_ANALYSIS,
                'causal_inference': ReasoningType.CAUSAL_INFERENCE,
                'temporal_reasoning': ReasoningType.TEMPORAL_REASONING,
                'contextual_linking': ReasoningType.CONTEXTUAL_LINKING,
                'predictive_reasoning': ReasoningType.PREDICTIVE_REASONING,
                'analogical_reasoning': ReasoningType.ANALOGICAL_REASONING
            }
            
            reasoning_enums = []
            for rt in reasoning_types:
                if rt in reasoning_type_map:
                    reasoning_enums.append(reasoning_type_map[rt])
            
            if not reasoning_enums:
                reasoning_enums = [ReasoningType.PATTERN_ANALYSIS]
            
            # Create reasoning query
            reasoning_query = ReasoningQuery(
                query_text=query_text,
                context=MemoryContext(**context),
                reasoning_types=reasoning_enums,
                max_steps=max_steps
            )
            
            # Perform reasoning
            reasoning_chain = await self.cot_reasoner.reason_about_memories(reasoning_query)
            
            # Update statistics
            self.memory_stats['reasoning_chains'] += 1
            
            # Convert to response format
            return {
                'status': 'success',
                'chain_id': reasoning_chain.chain_id,
                'purpose': reasoning_chain.purpose,
                'steps_completed': len(reasoning_chain.steps),
                'final_conclusion': reasoning_chain.final_conclusion,
                'overall_confidence': reasoning_chain.overall_confidence,
                'reasoning_time': reasoning_chain.reasoning_time,
                'steps': [
                    {
                        'step_id': step.step_id,
                        'step_type': step.step_type.value,
                        'description': step.description,
                        'confidence': step.confidence,
                        'timestamp': step.timestamp.isoformat(),
                        'output_summary': self._summarize_reasoning_output(step.output_data)
                    }
                    for step in reasoning_chain.steps
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to perform reasoning: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _learn_from_examples(self, examples: List[Dict[str, Any]], pattern_type: str) -> Dict[str, Any]:
        """Learn patterns from few-shot examples"""
        try:
            # Convert string pattern type to enum
            pattern_type_map = {
                'success_pattern': PatternType.SUCCESS_PATTERN,
                'failure_pattern': PatternType.FAILURE_PATTERN,
                'workflow_pattern': PatternType.WORKFLOW_PATTERN,
                'solution_pattern': PatternType.SOLUTION_PATTERN,
                'optimization_pattern': PatternType.OPTIMIZATION_PATTERN,
                'creative_pattern': PatternType.CREATIVE_PATTERN
            }
            
            pattern_enum = pattern_type_map.get(pattern_type, PatternType.SUCCESS_PATTERN)
            
            # Learn pattern
            learned_pattern = await self.few_shot_engine.learn_from_examples(examples, pattern_enum)
            
            # Update statistics
            self.memory_stats['patterns_learned'] += 1
            
            return {
                'status': 'success',
                'pattern_id': learned_pattern.pattern_id,
                'pattern_name': learned_pattern.name,
                'pattern_type': learned_pattern.pattern_type.value,
                'confidence': learned_pattern.confidence,
                'success_rate': learned_pattern.success_rate,
                'example_count': len(learned_pattern.examples),
                'applicability_rules': learned_pattern.applicability_rules,
                'created_at': learned_pattern.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to learn from examples: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _find_similar_patterns(self, context: Dict[str, Any], input_features: Dict[str, Any], 
                                   desired_outcome: str, max_patterns: int) -> List[Dict[str, Any]]:
        """Find similar patterns for current context"""
        try:
            # Create few-shot query
            query = FewShotQuery(
                context=context,
                input_features=input_features,
                desired_outcome=desired_outcome,
                max_patterns=max_patterns
            )
            
            # Find matching patterns
            pattern_applications = await self.few_shot_engine.find_matching_patterns(query)
            
            # Convert to response format
            results = []
            for application in pattern_applications:
                result = {
                    'pattern_id': application.pattern_id,
                    'confidence': application.confidence,
                    'predicted_outcome': application.predicted_outcome,
                    'success_probability': application.success_probability,
                    'recommended_actions': application.recommended_actions,
                    'similar_examples_count': len(application.similar_examples),
                    'adaptation_notes': application.adaptation_notes
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to find similar patterns: {e}")
            return []
    
    async def _share_knowledge(self, knowledge_type: str, content: Dict[str, Any], 
                             privacy_level: str, sharing_scope: str) -> Dict[str, Any]:
        """Share knowledge with federation"""
        try:
            # Convert strings to enums
            privacy_level_map = {
                'public': PrivacyLevel.PUBLIC,
                'low': PrivacyLevel.LOW,
                'medium': PrivacyLevel.MEDIUM,
                'high': PrivacyLevel.HIGH,
                'private': PrivacyLevel.PRIVATE
            }
            
            sharing_scope_map = {
                'global': SharingScope.GLOBAL,
                'organization': SharingScope.ORGANIZATION,
                'team': SharingScope.TEAM,
                'project_group': SharingScope.PROJECT_GROUP,
                'none': SharingScope.NONE
            }
            
            privacy_enum = privacy_level_map.get(privacy_level, PrivacyLevel.MEDIUM)
            scope_enum = sharing_scope_map.get(sharing_scope, SharingScope.ORGANIZATION)
            
            # Create privacy policy
            privacy_policy = PrivacyPolicy(
                privacy_level=privacy_enum,
                sharing_scope=scope_enum
            )
            
            # Share knowledge
            knowledge_id = await self.federated_manager.share_knowledge(
                knowledge_type=knowledge_type,
                content=content,
                privacy_policy=privacy_policy
            )
            
            # Update statistics
            self.memory_stats['federated_shares'] += 1
            
            return {
                'status': 'success',
                'knowledge_id': knowledge_id,
                'privacy_level': privacy_level,
                'sharing_scope': sharing_scope,
                'shared_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to share knowledge: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _query_federation(self, knowledge_types: List[str], context: Dict[str, Any], 
                              max_results: int) -> List[Dict[str, Any]]:
        """Query federation for knowledge"""
        try:
            # Create federation query
            query = FederationQuery(
                query_context=context,
                desired_knowledge_types=knowledge_types,
                privacy_constraints=PrivacyPolicy(
                    privacy_level=PrivacyLevel.MEDIUM,
                    sharing_scope=SharingScope.ORGANIZATION
                ),
                max_results=max_results
            )
            
            # Query federation
            results = await self.federated_manager.query_federation(query)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to query federation: {e}")
            return []
    
    async def _discover_memory_patterns(self, min_examples: int, pattern_types: List[str]) -> Dict[str, Any]:
        """Discover patterns from memory data"""
        try:
            # Get all memories for pattern discovery
            all_memories = []
            if self.semantic_store:
                # This would need to be implemented in semantic_store
                # For now, we'll use a placeholder
                all_memories = await self._get_all_memories_for_discovery()
            
            # Discover patterns
            discovered_patterns = await self.few_shot_engine.discover_new_patterns(
                memories=all_memories,
                min_examples=min_examples
            )
            
            # Convert to response format
            pattern_summaries = []
            for pattern in discovered_patterns:
                summary = {
                    'pattern_id': pattern.pattern_id,
                    'pattern_name': pattern.name,
                    'pattern_type': pattern.pattern_type.value,
                    'confidence': pattern.confidence,
                    'success_rate': pattern.success_rate,
                    'example_count': len(pattern.examples),
                    'description': pattern.description
                }
                pattern_summaries.append(summary)
            
            return {
                'status': 'success',
                'patterns_discovered': len(discovered_patterns),
                'patterns': pattern_summaries,
                'discovered_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to discover patterns: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _get_enhanced_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about enhanced memory capabilities"""
        try:
            # Base memory stats
            enhanced_stats = self.memory_stats.copy()
            
            # Add few-shot learning stats
            if self.few_shot_engine:
                learning_stats = await self.few_shot_engine.get_learning_statistics()
                enhanced_stats['few_shot_learning'] = learning_stats
            
            # Add federation stats
            if self.federated_manager:
                federation_stats = await self.federated_manager.get_federation_statistics()
                enhanced_stats['federation'] = federation_stats
            
            # Add reasoning stats
            enhanced_stats['chain_of_thought'] = {
                'reasoning_chains_completed': enhanced_stats.get('reasoning_chains', 0),
                'average_steps_per_chain': 5.2,  # This would be calculated from actual data
                'most_common_reasoning_type': 'pattern_analysis'
            }
            
            return {
                'status': 'success',
                'stats': enhanced_stats,
                'retrieved_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get enhanced stats: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    # Advanced enhancement implementations
    
    async def _adaptive_reasoning(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform adaptive reasoning across all systems"""
        try:
            start_time = time.time()
            
            # Use enhancement engine for adaptive reasoning
            results = await self.enhancement_engine.adaptive_reasoning_pipeline(query, context)
            
            # Record metrics
            latency_ms = (time.time() - start_time) * 1000
            await self.metrics_collector.record_operation_latency('adaptive_reasoning', latency_ms, True)
            
            return {
                'status': 'success',
                'results': results,
                'latency_ms': latency_ms
            }
            
        except Exception as e:
            logger.error(f"Failed in adaptive reasoning: {e}")
            await self.metrics_collector.record_operation_latency('adaptive_reasoning', 0, False)
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _discover_cross_patterns(self, memory_count: int) -> List[Dict[str, Any]]:
        """Discover cross-pattern insights"""
        try:
            # Get recent memories for analysis
            memories = await self.semantic_store.get_recent_memories(memory_count)
            
            # Discover insights
            insights = await self.enhancement_engine.discover_cross_pattern_insights(memories)
            
            # Update stats
            self.memory_stats['cross_pattern_insights'] += len(insights)
            
            # Convert insights to response format
            results = []
            for insight in insights:
                results.append({
                    'insight_id': insight.insight_id,
                    'type': insight.insight_type,
                    'description': insight.description,
                    'confidence': insight.confidence,
                    'recommendations': insight.recommendations,
                    'timestamp': insight.timestamp.isoformat()
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to discover cross patterns: {e}")
            return []
    
    async def _optimize_memory_system(self) -> Dict[str, Any]:
        """Optimize memory system performance"""
        try:
            start_time = time.time()
            
            # Get all memories for optimization
            memories = await self._get_all_memories_for_discovery()
            
            # Perform optimization
            optimization_results = await self.memory_optimizer.optimize_memory_patterns(memories)
            
            # Get optimization suggestions from metrics
            metric_optimizations = await self.metrics_collector.optimize_based_on_metrics()
            
            # Combine results
            combined_results = {
                'pattern_optimizations': optimization_results,
                'metric_optimizations': metric_optimizations,
                'optimization_time_ms': (time.time() - start_time) * 1000
            }
            
            # Update stats
            self.memory_stats['optimizations_performed'] += 1
            
            # Record metric
            await self.metrics_collector.record_operation_latency(
                'memory_optimization', 
                combined_results['optimization_time_ms'], 
                True
            )
            
            return {
                'status': 'success',
                'results': combined_results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize memory system: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics dashboard"""
        try:
            # Get real-time dashboard
            dashboard = await self.metrics_collector.get_real_time_dashboard()
            
            # Add enhancement statistics
            enhancement_stats = await self.enhancement_engine.get_enhancement_statistics()
            dashboard['enhancement_stats'] = enhancement_stats
            
            # Add memory stats
            dashboard['memory_stats'] = self.memory_stats.copy()
            
            return {
                'status': 'success',
                'dashboard': dashboard
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _process_continuous_learning_feedback(self, pattern_id: Optional[str], 
                                                   reasoning_chain_id: Optional[str],
                                                   success: bool, outcome: str,
                                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Process continuous learning feedback"""
        try:
            feedback = {
                'success': success,
                'outcome': outcome,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
            
            if pattern_id:
                feedback['pattern_id'] = pattern_id
            if reasoning_chain_id:
                feedback['reasoning_chain_id'] = reasoning_chain_id
            
            # Process feedback
            await self.enhancement_engine.continuous_learning_loop(feedback)
            
            # Record metric
            await self.metrics_collector.record_metric(
                MetricType.ACCURACY,
                1.0 if success else 0.0,
                context={'feedback_type': 'continuous_learning'}
            )
            
            return {
                'status': 'success',
                'message': 'Feedback processed successfully',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to process continuous learning feedback: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    # Helper methods
    
    def _summarize_reasoning_output(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize reasoning step output for response"""
        summary = {}
        
        if 'patterns' in output_data:
            summary['patterns_found'] = len(output_data['patterns'])
        if 'causal_chains' in output_data:
            summary['causal_relationships'] = len(output_data['causal_chains'])
        if 'predictions' in output_data:
            summary['predictions_made'] = len(output_data['predictions'])
        if 'analogies' in output_data:
            summary['analogies_discovered'] = len(output_data['analogies'])
        if 'context_links' in output_data:
            summary['context_connections'] = len(output_data['context_links'])
        
        # Include error if present
        if 'error' in output_data:
            summary['error'] = output_data['error']
        
        return summary
    
    async def _get_all_memories_for_discovery(self) -> List[MemoryItem]:
        """Get all memories for pattern discovery - placeholder implementation"""
        # This would need to be implemented properly in the semantic store
        # For now, return empty list
        return []


def create_server_config() -> MCPServerSettings:
    """Create server configuration"""
    config_manager = ConfigManager()
    return config_manager.load_config("context-aware-memory")


def main():
    """Main entry point"""
    try:
        # Load configuration
        config = create_server_config()
        
        # Create and run server
        server = ContextAwareMemoryServer(config)
        server.run(transport="stdio")
        
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()