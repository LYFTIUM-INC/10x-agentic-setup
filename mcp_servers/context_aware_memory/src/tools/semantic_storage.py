"""
Semantic Storage System for Context-Aware Memory
Implements intelligent memory storage with semantic indexing and context awareness
"""

import asyncio
import logging
import json
import time
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import hashlib

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Types of memory content"""
    TEXT = "text"
    CODE = "code" 
    CONVERSATION = "conversation"
    DOCUMENT = "document"
    TASK = "task"
    REFERENCE = "reference"
    INSIGHT = "insight"
    PATTERN = "pattern"


class AccessLevel(Enum):
    """Memory access levels"""
    PUBLIC = "public"
    PRIVATE = "private"
    SHARED = "shared"
    ARCHIVED = "archived"


@dataclass
class MemoryContext:
    """Context information for memory items"""
    project: Optional[str] = None
    session: Optional[str] = None
    user: Optional[str] = None
    application: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    location: Optional[str] = None
    environment: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryContext':
        """Create from dictionary"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class MemoryItem:
    """Individual memory item with semantic and contextual information"""
    memory_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    content_hash: str = field(default="")
    memory_type: MemoryType = MemoryType.TEXT
    context: Optional[MemoryContext] = None
    tags: List[str] = field(default_factory=list)
    importance: float = 1.0  # 0.0 to 1.0
    confidence: float = 1.0  # 0.0 to 1.0
    access_level: AccessLevel = AccessLevel.PUBLIC
    
    # Temporal information
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    
    # Embedding and similarity
    embedding: Optional[List[float]] = None
    similarity_score: float = 0.0  # Used during retrieval
    
    # Relationships
    related_memories: List[str] = field(default_factory=list)
    parent_memory: Optional[str] = None
    child_memories: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize computed fields"""
        if not self.content_hash:
            self.content_hash = hashlib.md5(self.content.encode()).hexdigest()
        
        if not self.context:
            self.context = MemoryContext()
    
    def update_access(self):
        """Update access tracking information"""
        self.last_accessed = datetime.now()
        self.access_count += 1
    
    def is_expired(self) -> bool:
        """Check if memory item has expired"""
        return self.expires_at is not None and datetime.now() > self.expires_at
    
    def get_age_hours(self) -> float:
        """Get age in hours"""
        return (datetime.now() - self.created_at).total_seconds() / 3600
    
    def calculate_relevance_score(self, context: MemoryContext) -> float:
        """Calculate relevance score based on context"""
        score = self.importance
        
        # Boost for same project/session
        if self.context and context:
            if self.context.project == context.project:
                score *= 1.2
            if self.context.session == context.session:
                score *= 1.1
            if self.context.user == context.user:
                score *= 1.05
        
        # Decay based on age
        age_hours = self.get_age_hours()
        age_decay = max(0.1, 1.0 - (age_hours / (24 * 7)))  # Week decay
        score *= age_decay
        
        # Boost for recent access
        if self.last_accessed:
            hours_since_access = (datetime.now() - self.last_accessed).total_seconds() / 3600
            access_boost = max(1.0, 1.5 - (hours_since_access / 24))
            score *= access_boost
        
        return min(1.0, score)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['memory_type'] = self.memory_type.value
        result['access_level'] = self.access_level.value
        result['created_at'] = self.created_at.isoformat()
        result['updated_at'] = self.updated_at.isoformat()
        if self.expires_at:
            result['expires_at'] = self.expires_at.isoformat()
        if self.last_accessed:
            result['last_accessed'] = self.last_accessed.isoformat()
        if self.context:
            result['context'] = self.context.to_dict()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """Create from dictionary"""
        # Convert string enums back to enum objects
        if 'memory_type' in data:
            data['memory_type'] = MemoryType(data['memory_type'])
        if 'access_level' in data:
            data['access_level'] = AccessLevel(data['access_level'])
        
        # Convert ISO strings back to datetime objects
        for field_name in ['created_at', 'updated_at', 'expires_at', 'last_accessed']:
            if field_name in data and data[field_name]:
                data[field_name] = datetime.fromisoformat(data[field_name])
        
        # Convert context
        if 'context' in data and data['context']:
            data['context'] = MemoryContext.from_dict(data['context'])
        
        return cls(**data)


@dataclass
class MemoryQuery:
    """Query specification for memory retrieval"""
    query_text: str
    context: Optional[MemoryContext] = None
    memory_types: List[MemoryType] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    max_results: int = 10
    similarity_threshold: float = 0.5
    importance_threshold: float = 0.0
    include_expired: bool = False
    time_range: Optional[Tuple[datetime, datetime]] = None
    access_level: Optional[AccessLevel] = None
    strategy: Optional[str] = None
    
    def matches_memory(self, memory: MemoryItem) -> bool:
        """Check if memory item matches query filters"""
        # Check expiration
        if not self.include_expired and memory.is_expired():
            return False
        
        # Check memory types
        if self.memory_types and memory.memory_type not in self.memory_types:
            return False
        
        # Check tags
        if self.tags and not any(tag in memory.tags for tag in self.tags):
            return False
        
        # Check importance
        if memory.importance < self.importance_threshold:
            return False
        
        # Check time range
        if self.time_range:
            start, end = self.time_range
            if not (start <= memory.created_at <= end):
                return False
        
        # Check access level
        if self.access_level and memory.access_level != self.access_level:
            return False
        
        return True


class SemanticMemoryStore:
    """Semantic memory storage system with vector indexing"""
    
    def __init__(self, embedding_manager=None, vector_dimension: int = 384, 
                 data_dir: str = "./memory_data"):
        self.embedding_manager = embedding_manager
        self.vector_dimension = vector_dimension
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Memory storage
        self.memories: Dict[str, MemoryItem] = {}
        self.memory_index: Dict[str, Set[str]] = {}  # tag -> memory_ids
        self.context_index: Dict[str, Set[str]] = {}  # context_key -> memory_ids
        
        # Vector storage (simplified for now)
        self.embeddings: Dict[str, List[float]] = {}
        
        # Statistics
        self.stats = {
            'total_memories': 0,
            'total_retrievals': 0,
            'average_similarity': 0.0,
            'last_cleanup': None
        }
    
    async def initialize(self):
        """Initialize the memory store"""
        logger.info("Initializing semantic memory store...")
        
        # Load existing memories if available
        await self.load_memories()
        
        logger.info(f"Memory store initialized with {len(self.memories)} memories")
    
    async def store_memory(self, memory_item: MemoryItem) -> str:
        """Store a memory item with semantic indexing"""
        try:
            # Generate embedding if embedding manager is available
            if self.embedding_manager and memory_item.content:
                embedding = await self.embedding_manager.encode_texts([memory_item.content])
                memory_item.embedding = embedding[0].tolist()
                self.embeddings[memory_item.memory_id] = memory_item.embedding
            
            # Store memory
            self.memories[memory_item.memory_id] = memory_item
            
            # Update indexes
            self._update_indexes(memory_item)
            
            # Update statistics
            self.stats['total_memories'] = len(self.memories)
            
            # Save to disk (simplified)
            await self._save_memory_to_disk(memory_item)
            
            logger.debug(f"Stored memory {memory_item.memory_id}")
            return memory_item.memory_id
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise
    
    async def retrieve_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """Retrieve a specific memory by ID"""
        memory = self.memories.get(memory_id)
        if memory:
            memory.update_access()
            await self._save_memory_to_disk(memory)
        return memory
    
    async def search(self, query: str, filters: Dict[str, Any] = None, 
                    limit: int = 10) -> List[MemoryItem]:
        """Search memories using semantic similarity and filters"""
        try:
            results = []
            
            # Generate query embedding
            query_embedding = None
            if self.embedding_manager:
                query_embeddings = await self.embedding_manager.encode_texts([query])
                query_embedding = query_embeddings[0]
            
            # Calculate similarities and apply filters
            for memory in self.memories.values():
                # Apply filters
                if filters:
                    if not self._apply_filters(memory, filters):
                        continue
                
                # Calculate similarity
                similarity = 0.0
                if query_embedding is not None and memory.embedding:
                    similarity = self._calculate_similarity(query_embedding, memory.embedding)
                else:
                    # Fallback to text similarity
                    similarity = self._text_similarity(query, memory.content)
                
                memory.similarity_score = similarity
                
                if similarity > 0.1:  # Minimum threshold
                    results.append(memory)
            
            # Sort by similarity and limit
            results.sort(key=lambda m: m.similarity_score, reverse=True)
            results = results[:limit]
            
            # Update access information
            for memory in results:
                memory.update_access()
            
            self.stats['total_retrievals'] += 1
            if results:
                avg_sim = sum(m.similarity_score for m in results) / len(results)
                self.stats['average_similarity'] = avg_sim
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    async def update_memory(self, memory_id: str, content: Optional[str] = None,
                           context: Optional[MemoryContext] = None,
                           tags: Optional[List[str]] = None,
                           importance: Optional[float] = None) -> bool:
        """Update an existing memory"""
        try:
            memory = self.memories.get(memory_id)
            if not memory:
                return False
            
            # Update fields
            if content is not None:
                memory.content = content
                memory.content_hash = hashlib.md5(content.encode()).hexdigest()
                
                # Regenerate embedding
                if self.embedding_manager:
                    embedding = await self.embedding_manager.encode_texts([content])
                    memory.embedding = embedding[0].tolist()
                    self.embeddings[memory_id] = memory.embedding
            
            if context is not None:
                memory.context = context
            
            if tags is not None:
                memory.tags = tags
            
            if importance is not None:
                memory.importance = importance
            
            memory.updated_at = datetime.now()
            
            # Update indexes
            self._update_indexes(memory)
            
            # Save to disk
            await self._save_memory_to_disk(memory)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory item"""
        try:
            if memory_id in self.memories:
                memory = self.memories[memory_id]
                
                # Remove from indexes
                self._remove_from_indexes(memory)
                
                # Remove from storage
                del self.memories[memory_id]
                if memory_id in self.embeddings:
                    del self.embeddings[memory_id]
                
                # Remove from disk
                memory_file = self.data_dir / "memories" / f"{memory_id}.json"
                if memory_file.exists():
                    memory_file.unlink()
                
                self.stats['total_memories'] = len(self.memories)
                
                logger.debug(f"Deleted memory {memory_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False
    
    async def get_context_info(self, context_query: Dict[str, Any]) -> Dict[str, Any]:
        """Get contextual information about stored memories"""
        try:
            info = {
                'total_memories': len(self.memories),
                'memory_types': {},
                'tags': {},
                'contexts': {},
                'age_distribution': {},
                'importance_distribution': {}
            }
            
            # Analyze memories
            for memory in self.memories.values():
                # Memory types
                type_key = memory.memory_type.value
                info['memory_types'][type_key] = info['memory_types'].get(type_key, 0) + 1
                
                # Tags
                for tag in memory.tags:
                    info['tags'][tag] = info['tags'].get(tag, 0) + 1
                
                # Context analysis
                if memory.context:
                    if memory.context.project:
                        project_key = f"project:{memory.context.project}"
                        info['contexts'][project_key] = info['contexts'].get(project_key, 0) + 1
                    
                    if memory.context.user:
                        user_key = f"user:{memory.context.user}"
                        info['contexts'][user_key] = info['contexts'].get(user_key, 0) + 1
                
                # Age distribution
                age_hours = memory.get_age_hours()
                if age_hours < 24:
                    age_key = "today"
                elif age_hours < 24 * 7:
                    age_key = "this_week"
                elif age_hours < 24 * 30:
                    age_key = "this_month"
                else:
                    age_key = "older"
                
                info['age_distribution'][age_key] = info['age_distribution'].get(age_key, 0) + 1
                
                # Importance distribution
                if memory.importance >= 0.8:
                    imp_key = "high"
                elif memory.importance >= 0.5:
                    imp_key = "medium"
                else:
                    imp_key = "low"
                
                info['importance_distribution'][imp_key] = info['importance_distribution'].get(imp_key, 0) + 1
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get context info: {e}")
            return {}
    
    async def cleanup(self, dry_run: bool = True) -> Dict[str, Any]:
        """Clean up expired and low-value memories"""
        try:
            to_delete = []
            
            for memory in self.memories.values():
                should_delete = False
                reason = ""
                
                # Check expiration
                if memory.is_expired():
                    should_delete = True
                    reason = "expired"
                
                # Check low importance and age
                elif (memory.importance < 0.2 and 
                      memory.get_age_hours() > 24 * 30 and  # Older than 30 days
                      memory.access_count < 2):  # Rarely accessed
                    should_delete = True
                    reason = "low_value"
                
                if should_delete:
                    to_delete.append({
                        'memory_id': memory.memory_id,
                        'reason': reason,
                        'importance': memory.importance,
                        'age_hours': memory.get_age_hours(),
                        'access_count': memory.access_count
                    })
            
            deleted_count = 0
            if not dry_run:
                for item in to_delete:
                    await self.delete_memory(item['memory_id'])
                    deleted_count += 1
            
            result = {
                'candidates': to_delete,
                'deleted_count': deleted_count,
                'remaining_memories': len(self.memories) - deleted_count
            }
            
            if not dry_run:
                self.stats['last_cleanup'] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to cleanup memories: {e}")
            return {'error': str(e)}
    
    async def export_memories(self, format: str = "json", 
                             filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Export memories for backup or migration"""
        try:
            memories_to_export = []
            
            for memory in self.memories.values():
                if filters and not self._apply_filters(memory, filters):
                    continue
                
                memories_to_export.append(memory.to_dict())
            
            export_data = {
                'format': format,
                'exported_at': datetime.now().isoformat(),
                'memory_count': len(memories_to_export),
                'memories': memories_to_export,
                'stats': self.stats.copy()
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Failed to export memories: {e}")
            return {'error': str(e)}
    
    async def import_memories(self, data: Dict[str, Any], 
                             merge_strategy: str = "append") -> Dict[str, Any]:
        """Import memories from backup or external source"""
        try:
            imported_count = 0
            skipped_count = 0
            error_count = 0
            
            memories_data = data.get('memories', [])
            
            for memory_data in memories_data:
                try:
                    memory = MemoryItem.from_dict(memory_data)
                    
                    # Handle merge strategy
                    if merge_strategy == "skip_existing" and memory.memory_id in self.memories:
                        skipped_count += 1
                        continue
                    elif merge_strategy == "overwrite" or memory.memory_id not in self.memories:
                        await self.store_memory(memory)
                        imported_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to import memory: {e}")
                    error_count += 1
            
            return {
                'imported_count': imported_count,
                'skipped_count': skipped_count,
                'error_count': error_count,
                'total_memories': len(self.memories)
            }
            
        except Exception as e:
            logger.error(f"Failed to import memories: {e}")
            return {'error': str(e)}
    
    def get_memory_count(self) -> int:
        """Get total number of stored memories"""
        return len(self.memories)
    
    async def load_existing_memories(self) -> int:
        """Load existing memories from storage"""
        return await self.load_memories()
    
    async def save_state(self):
        """Save current state to persistent storage"""
        try:
            # Save statistics
            stats_file = self.data_dir / "stats.json"
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
            
            # Save indexes
            indexes_file = self.data_dir / "indexes.json" 
            indexes_data = {
                'memory_index': {k: list(v) for k, v in self.memory_index.items()},
                'context_index': {k: list(v) for k, v in self.context_index.items()}
            }
            with open(indexes_file, 'w') as f:
                json.dump(indexes_data, f, indent=2)
            
            logger.info("Memory state saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save memory state: {e}")
    
    # Private helper methods
    
    def _update_indexes(self, memory: MemoryItem):
        """Update search indexes for a memory item"""
        memory_id = memory.memory_id
        
        # Tag index
        for tag in memory.tags:
            if tag not in self.memory_index:
                self.memory_index[tag] = set()
            self.memory_index[tag].add(memory_id)
        
        # Context index
        if memory.context:
            if memory.context.project:
                key = f"project:{memory.context.project}"
                if key not in self.context_index:
                    self.context_index[key] = set()
                self.context_index[key].add(memory_id)
            
            if memory.context.user:
                key = f"user:{memory.context.user}"
                if key not in self.context_index:
                    self.context_index[key] = set()
                self.context_index[key].add(memory_id)
    
    def _remove_from_indexes(self, memory: MemoryItem):
        """Remove memory from search indexes"""
        memory_id = memory.memory_id
        
        # Remove from tag index
        for tag in memory.tags:
            if tag in self.memory_index:
                self.memory_index[tag].discard(memory_id)
                if not self.memory_index[tag]:
                    del self.memory_index[tag]
        
        # Remove from context index
        if memory.context:
            if memory.context.project:
                key = f"project:{memory.context.project}"
                if key in self.context_index:
                    self.context_index[key].discard(memory_id)
                    if not self.context_index[key]:
                        del self.context_index[key]
            
            if memory.context.user:
                key = f"user:{memory.context.user}"
                if key in self.context_index:
                    self.context_index[key].discard(memory_id)
                    if not self.context_index[key]:
                        del self.context_index[key]
    
    def _apply_filters(self, memory: MemoryItem, filters: Dict[str, Any]) -> bool:
        """Apply filters to memory item"""
        # Tag filters
        if 'tags' in filters:
            required_tags = filters['tags']
            if not any(tag in memory.tags for tag in required_tags):
                return False
        
        # Memory type filter
        if 'memory_type' in filters:
            if memory.memory_type.value != filters['memory_type']:
                return False
        
        # Importance filter
        if 'min_importance' in filters:
            if memory.importance < filters['min_importance']:
                return False
        
        # Context filters
        if 'project' in filters and memory.context:
            if memory.context.project != filters['project']:
                return False
        
        if 'user' in filters and memory.context:
            if memory.context.user != filters['user']:
                return False
        
        # Time range filter
        if 'time_range' in filters:
            start, end = filters['time_range']
            if not (start <= memory.created_at <= end):
                return False
        
        return True
    
    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        try:
            import numpy as np
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception:
            return 0.0
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity fallback"""
        # Simple Jaccard similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    async def _save_memory_to_disk(self, memory: MemoryItem):
        """Save individual memory to disk"""
        try:
            memories_dir = self.data_dir / "memories"
            memories_dir.mkdir(exist_ok=True)
            
            memory_file = memories_dir / f"{memory.memory_id}.json"
            with open(memory_file, 'w') as f:
                json.dump(memory.to_dict(), f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save memory to disk: {e}")
    
    async def load_memories(self) -> int:
        """Load memories from disk"""
        try:
            memories_dir = self.data_dir / "memories"
            if not memories_dir.exists():
                return 0
            
            loaded_count = 0
            
            for memory_file in memories_dir.glob("*.json"):
                try:
                    with open(memory_file, 'r') as f:
                        memory_data = json.load(f)
                    
                    memory = MemoryItem.from_dict(memory_data)
                    self.memories[memory.memory_id] = memory
                    
                    if memory.embedding:
                        self.embeddings[memory.memory_id] = memory.embedding
                    
                    self._update_indexes(memory)
                    loaded_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to load memory from {memory_file}: {e}")
            
            # Load statistics
            stats_file = self.data_dir / "stats.json"
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    self.stats.update(json.load(f))
            
            self.stats['total_memories'] = len(self.memories)
            
            logger.info(f"Loaded {loaded_count} memories from disk")
            return loaded_count
            
        except Exception as e:
            logger.error(f"Failed to load memories: {e}")
            return 0


# Example usage and testing
if __name__ == "__main__":
    async def test_semantic_storage():
        store = SemanticMemoryStore(data_dir="./test_memory")
        await store.initialize()
        
        # Test storing memories
        memory1 = MemoryItem(
            content="This is a test memory about Python programming",
            memory_type=MemoryType.TEXT,
            context=MemoryContext(project="test_project", user="test_user"),
            tags=["python", "programming", "test"],
            importance=0.8
        )
        
        memory_id = await store.store_memory(memory1)
        print(f"Stored memory: {memory_id}")
        
        # Test searching
        results = await store.search("Python programming", limit=5)
        print(f"Search results: {len(results)}")
        
        # Test context info
        context_info = await store.get_context_info({})
        print(f"Context info: {context_info}")
        
        await store.save_state()
    
    asyncio.run(test_semantic_storage())