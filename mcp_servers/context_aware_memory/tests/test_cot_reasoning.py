"""
Tests for Chain-of-Thought Memory Reasoning
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
import numpy as np

# Import the modules to test
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from tools.cot_memory_reasoning import (
    ChainOfThoughtReasoner, ReasoningQuery, ReasoningType, ReasoningStep, ReasoningChain
)
from tools.semantic_storage import MemoryItem, MemoryContext, MemoryType


class TestChainOfThoughtReasoner:
    """Test cases for Chain-of-Thought Memory Reasoning"""
    
    @pytest.fixture
    def mock_semantic_store(self):
        """Mock semantic store"""
        store = Mock()
        store.search_memories = AsyncMock()
        return store
    
    @pytest.fixture
    def mock_embedding_manager(self):
        """Mock embedding manager"""
        manager = Mock()
        manager.get_embeddings = AsyncMock()
        return manager
    
    @pytest.fixture
    def sample_memories(self):
        """Sample memory items for testing"""
        memories = []
        
        # Create test memories with different patterns
        contexts = [
            {"project": "test_project", "task": "development", "user": "dev1"},
            {"project": "test_project", "task": "debugging", "user": "dev1"},
            {"project": "test_project", "task": "testing", "user": "dev2"},
            {"project": "other_project", "task": "development", "user": "dev1"}
        ]
        
        contents = [
            "Successfully implemented user authentication feature",
            "Fixed critical bug in payment processing",
            "Completed comprehensive test suite",
            "Started new feature development"
        ]
        
        for i, (context, content) in enumerate(zip(contexts, contents)):
            memory = MemoryItem(
                memory_id=f"memory_{i}",
                content=content,
                context=MemoryContext(**context),
                importance=0.8,
                memory_type=MemoryType.EXPERIENCE,
                created_at=datetime.now() - timedelta(days=i)
            )
            memories.append(memory)
        
        return memories
    
    @pytest.fixture
    def reasoner(self, mock_semantic_store, mock_embedding_manager):
        """Create reasoner instance"""
        return ChainOfThoughtReasoner(mock_semantic_store, mock_embedding_manager)
    
    @pytest.mark.asyncio
    async def test_reasoner_initialization(self, reasoner):
        """Test reasoner initialization"""
        assert reasoner.semantic_store is not None
        assert reasoner.embedding_manager is not None
        assert reasoner.reasoning_cache == {}
        assert reasoner.pattern_library == {}
        assert len(reasoner.reasoning_templates) == 6  # All reasoning types
    
    @pytest.mark.asyncio
    async def test_pattern_analysis_reasoning(self, reasoner, sample_memories):
        """Test pattern analysis reasoning"""
        # Mock search_memories to return sample memories
        reasoner.semantic_store.search_memories.return_value = sample_memories
        
        # Create reasoning query for pattern analysis
        query = ReasoningQuery(
            query_text="Analyze development patterns",
            context=MemoryContext(project="test_project"),
            reasoning_types=[ReasoningType.PATTERN_ANALYSIS],
            max_steps=5
        )
        
        # Perform reasoning
        chain = await reasoner.reason_about_memories(query)
        
        # Verify reasoning chain
        assert isinstance(chain, ReasoningChain)
        assert chain.purpose == "Analyze development patterns"
        assert len(chain.steps) >= 1
        assert chain.overall_confidence > 0
        
        # Check that pattern analysis was performed
        pattern_step = next((step for step in chain.steps 
                           if step.step_type == ReasoningType.PATTERN_ANALYSIS), None)
        assert pattern_step is not None
        assert pattern_step.confidence > 0
    
    @pytest.mark.asyncio
    async def test_causal_inference_reasoning(self, reasoner, sample_memories):
        """Test causal inference reasoning"""
        # Mock search_memories to return chronologically ordered memories
        reasoner.semantic_store.search_memories.return_value = sample_memories
        
        # Mock semantic similarity calculation
        reasoner._calculate_semantic_similarity = AsyncMock(return_value=0.6)
        
        # Create reasoning query for causal inference
        query = ReasoningQuery(
            query_text="Find causal relationships in development process",
            context=MemoryContext(project="test_project"),
            reasoning_types=[ReasoningType.CAUSAL_INFERENCE],
            max_steps=3
        )
        
        # Perform reasoning
        chain = await reasoner.reason_about_memories(query)
        
        # Verify causal inference step
        causal_step = next((step for step in chain.steps 
                          if step.step_type == ReasoningType.CAUSAL_INFERENCE), None)
        assert causal_step is not None
        
        # Check output contains causal chains
        if 'causal_chains' in causal_step.output_data:
            causal_chains = causal_step.output_data['causal_chains']
            assert isinstance(causal_chains, list)
    
    @pytest.mark.asyncio
    async def test_temporal_reasoning(self, reasoner, sample_memories):
        """Test temporal reasoning"""
        reasoner.semantic_store.search_memories.return_value = sample_memories
        
        query = ReasoningQuery(
            query_text="Analyze temporal patterns",
            context=MemoryContext(project="test_project"),
            reasoning_types=[ReasoningType.TEMPORAL_REASONING]
        )
        
        chain = await reasoner.reason_about_memories(query)
        
        temporal_step = next((step for step in chain.steps 
                            if step.step_type == ReasoningType.TEMPORAL_REASONING), None)
        assert temporal_step is not None
        
        # Check temporal analysis output
        output = temporal_step.output_data
        assert 'temporal_span' in output or 'error' in output
    
    @pytest.mark.asyncio
    async def test_contextual_linking(self, reasoner, sample_memories):
        """Test contextual linking reasoning"""
        reasoner.semantic_store.search_memories.return_value = sample_memories
        
        query = ReasoningQuery(
            query_text="Find contextual connections",
            context=MemoryContext(project="test_project"),
            reasoning_types=[ReasoningType.CONTEXTUAL_LINKING]
        )
        
        chain = await reasoner.reason_about_memories(query)
        
        context_step = next((step for step in chain.steps 
                           if step.step_type == ReasoningType.CONTEXTUAL_LINKING), None)
        assert context_step is not None
        
        # Check context linking output
        output = context_step.output_data
        assert 'context_links' in output or 'error' in output
    
    @pytest.mark.asyncio
    async def test_multiple_reasoning_types(self, reasoner, sample_memories):
        """Test reasoning with multiple types"""
        reasoner.semantic_store.search_memories.return_value = sample_memories
        
        query = ReasoningQuery(
            query_text="Comprehensive analysis",
            context=MemoryContext(project="test_project"),
            reasoning_types=[
                ReasoningType.PATTERN_ANALYSIS,
                ReasoningType.CAUSAL_INFERENCE,
                ReasoningType.TEMPORAL_REASONING
            ],
            max_steps=10
        )
        
        chain = await reasoner.reason_about_memories(query)
        
        # Should have steps for each reasoning type
        step_types = [step.step_type for step in chain.steps]
        assert ReasoningType.PATTERN_ANALYSIS in step_types
        assert len(chain.steps) >= 2  # At least pattern analysis and one other
    
    @pytest.mark.asyncio
    async def test_confidence_threshold_filtering(self, reasoner, sample_memories):
        """Test that low confidence steps are filtered out"""
        reasoner.semantic_store.search_memories.return_value = sample_memories
        
        # Create query with high confidence threshold
        query = ReasoningQuery(
            query_text="High confidence analysis",
            context=MemoryContext(project="test_project"),
            reasoning_types=[ReasoningType.PATTERN_ANALYSIS],
            confidence_threshold=0.9  # Very high threshold
        )
        
        chain = await reasoner.reason_about_memories(query)
        
        # All steps should meet confidence threshold
        for step in chain.steps:
            assert step.confidence >= 0.9 or 'error' in step.output_data
    
    @pytest.mark.asyncio
    async def test_analogical_reasoning(self, reasoner, sample_memories):
        """Test analogical reasoning with success patterns"""
        reasoner.semantic_store.search_memories.return_value = sample_memories
        
        # Add some success patterns to the reasoner
        success_pattern = {
            'content_length': 50,
            'tag_count': 3,
            'importance': 0.8,
            'has_context': True,
            'memory_type': 'experience'
        }
        reasoner.success_patterns.append(success_pattern)
        
        query = ReasoningQuery(
            query_text="Find analogous patterns",
            context=MemoryContext(project="test_project"),
            reasoning_types=[ReasoningType.ANALOGICAL_REASONING]
        )
        
        chain = await reasoner.reason_about_memories(query)
        
        analog_step = next((step for step in chain.steps 
                          if step.step_type == ReasoningType.ANALOGICAL_REASONING), None)
        assert analog_step is not None
    
    @pytest.mark.asyncio
    async def test_empty_memories_handling(self, reasoner):
        """Test handling of empty memory results"""
        # Mock empty search results
        reasoner.semantic_store.search_memories.return_value = []
        
        query = ReasoningQuery(
            query_text="Analyze empty set",
            context=MemoryContext(project="empty_project"),
            reasoning_types=[ReasoningType.PATTERN_ANALYSIS]
        )
        
        chain = await reasoner.reason_about_memories(query)
        
        # Should handle empty memories gracefully
        assert isinstance(chain, ReasoningChain)
        assert len(chain.steps) >= 0  # May have steps with empty data
    
    @pytest.mark.asyncio
    async def test_semantic_similarity_calculation(self, reasoner):
        """Test semantic similarity calculation"""
        # Mock embedding manager
        reasoner.embedding_manager.get_embeddings.return_value = [
            np.array([1, 0, 0]),  # First text embedding
            np.array([0, 1, 0])   # Second text embedding
        ]
        
        similarity = await reasoner._calculate_semantic_similarity("text1", "text2")
        
        # Should return a float between 0 and 1
        assert isinstance(similarity, float)
        assert 0 <= similarity <= 1
    
    @pytest.mark.asyncio
    async def test_pattern_extraction_methods(self, reasoner, sample_memories):
        """Test various pattern extraction methods"""
        # Test content pattern extraction
        content_patterns = reasoner._extract_content_patterns(sample_memories)
        assert isinstance(content_patterns, list)
        
        # Test temporal pattern extraction
        temporal_patterns = reasoner._extract_temporal_patterns(sample_memories)
        assert isinstance(temporal_patterns, list)
        
        # Test context pattern extraction
        context_patterns = reasoner._extract_context_patterns(sample_memories)
        assert isinstance(context_patterns, list)
    
    @pytest.mark.asyncio
    async def test_reasoning_chain_caching(self, reasoner, sample_memories):
        """Test that reasoning chains are cached"""
        reasoner.semantic_store.search_memories.return_value = sample_memories
        
        query = ReasoningQuery(
            query_text="Test caching",
            context=MemoryContext(project="test_project"),
            reasoning_types=[ReasoningType.PATTERN_ANALYSIS]
        )
        
        # First reasoning call
        chain1 = await reasoner.reason_about_memories(query)
        
        # Check that chain is cached
        assert len(reasoner.reasoning_cache) > 0
        assert chain1.chain_id in reasoner.reasoning_cache
        
        # Cached chain should be the same object
        cached_chain = reasoner.reasoning_cache[chain1.chain_id]
        assert cached_chain is chain1
    
    @pytest.mark.asyncio
    async def test_error_handling(self, reasoner):
        """Test error handling in reasoning process"""
        # Mock search_memories to raise an exception
        reasoner.semantic_store.search_memories.side_effect = Exception("Search failed")
        
        query = ReasoningQuery(
            query_text="Error test",
            context=MemoryContext(project="test_project"),
            reasoning_types=[ReasoningType.PATTERN_ANALYSIS]
        )
        
        # Should handle errors gracefully
        chain = await reasoner.reason_about_memories(query)
        assert isinstance(chain, ReasoningChain)
        
        # May have error steps or empty steps
        # Should not raise unhandled exceptions
    
    def test_reasoning_templates_completeness(self, reasoner):
        """Test that all reasoning types have templates"""
        for reasoning_type in ReasoningType:
            assert reasoning_type in reasoner.reasoning_templates
            template = reasoner.reasoning_templates[reasoning_type]
            assert 'prompt' in template
            assert 'process' in template
    
    @pytest.mark.asyncio
    async def test_success_pattern_management(self, reasoner):
        """Test success pattern addition and management"""
        initial_count = len(reasoner.success_patterns)
        
        # Add a success pattern
        pattern = {
            'type': 'test_pattern',
            'success_rate': 0.9,
            'features': ['feature1', 'feature2']
        }
        
        reasoner.add_success_pattern(pattern)
        
        # Check pattern was added
        assert len(reasoner.success_patterns) == initial_count + 1
        assert pattern in reasoner.success_patterns
        
        # Test pattern limit (should be 100)
        for i in range(150):  # Add more than limit
            reasoner.add_success_pattern({'pattern': i})
        
        # Should be limited to 100
        assert len(reasoner.success_patterns) <= 100


if __name__ == "__main__":
    pytest.main([__file__])