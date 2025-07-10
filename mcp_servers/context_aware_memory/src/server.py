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
        self.memory_stats = {
            'total_memories': 0,
            'total_retrievals': 0,
            'cache_hits': 0,
            'predictions_made': 0
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
        
        # Load existing memories
        await self._load_existing_memories()
        
        logger.info("Context-Aware Memory Server initialized successfully")
    
    async def _shutdown(self):
        """Save state on shutdown"""
        if self.semantic_store:
            await self.semantic_store.save_state()
            logger.info("Memory state saved successfully")
        
        await super()._shutdown()
    
    async def _store_memory(self, request: MemoryStoreRequest) -> Dict[str, Any]:
        """Store memory item with semantic indexing"""
        try:
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
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _retrieve_memories(self, request: MemoryRetrievalRequest) -> List[Dict[str, Any]]:
        """Retrieve memories using intelligent strategies"""
        try:
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
            
            logger.info(f"Retrieved {len(memories)} memories for query: {request.query[:50]}")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
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