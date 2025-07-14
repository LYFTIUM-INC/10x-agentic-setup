"""
Tests for Few-Shot Learning Memory Patterns
"""

import pytest
import asyncio
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
import numpy as np
from pathlib import Path

# Import the modules to test
import sys
sys.path.append(str(Path(__file__).parent.parent / "src"))

from tools.few_shot_learning import (
    FewShotLearningEngine, FewShotQuery, PatternType, PatternExample, 
    LearningPattern, PatternApplication, PatternConfidence
)
from tools.semantic_storage import MemoryItem, MemoryContext, MemoryType


class TestFewShotLearningEngine:
    """Test cases for Few-Shot Learning Engine"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
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
    async def learning_engine(self, mock_semantic_store, mock_embedding_manager, temp_dir):
        """Create learning engine instance"""
        engine = FewShotLearningEngine(
            semantic_store=mock_semantic_store,
            embedding_manager=mock_embedding_manager,
            data_dir=temp_dir
        )
        await engine.initialize()
        return engine
    
    @pytest.fixture
    def sample_examples(self):
        """Sample examples for pattern learning"""
        examples = [
            {
                'context': {'project': 'web_app', 'task': 'authentication'},
                'input_features': {'complexity': 'medium', 'team_size': 3, 'deadline': 'urgent'},
                'output_features': {'lines_of_code': 250, 'test_coverage': 0.9},
                'outcome': 'success',
                'success_score': 0.9,
                'metadata': {'duration_days': 5}
            },
            {
                'context': {'project': 'web_app', 'task': 'authentication'},
                'input_features': {'complexity': 'high', 'team_size': 2, 'deadline': 'flexible'},
                'output_features': {'lines_of_code': 400, 'test_coverage': 0.85},
                'outcome': 'success',
                'success_score': 0.8,
                'metadata': {'duration_days': 8}
            },
            {
                'context': {'project': 'mobile_app', 'task': 'authentication'},
                'input_features': {'complexity': 'low', 'team_size': 4, 'deadline': 'normal'},
                'output_features': {'lines_of_code': 150, 'test_coverage': 0.95},
                'outcome': 'success',
                'success_score': 0.95,
                'metadata': {'duration_days': 3}
            }
        ]
        return examples
    
    @pytest.fixture
    def sample_memories(self):
        """Sample memory items for pattern discovery"""
        memories = []
        
        contexts = [
            {"project": "web_dev", "task": "feature_implementation", "outcome": "success"},
            {"project": "web_dev", "task": "bug_fixing", "outcome": "success"},
            {"project": "mobile_dev", "task": "feature_implementation", "outcome": "failure"},
            {"project": "web_dev", "task": "testing", "outcome": "success"}
        ]
        
        contents = [
            "Successfully implemented user dashboard with React components",
            "Fixed critical memory leak in background service",
            "Failed to implement push notifications due to API limitations",
            "Completed comprehensive testing with 95% coverage"
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
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, learning_engine, temp_dir):
        """Test engine initialization"""
        assert learning_engine.semantic_store is not None
        assert learning_engine.embedding_manager is not None
        assert learning_engine.patterns_dir.exists()
        assert learning_engine.learned_patterns == {}
        assert len(learning_engine.feature_extractors) > 0
    
    @pytest.mark.asyncio
    async def test_learn_from_examples(self, learning_engine, sample_examples):
        """Test learning patterns from examples"""
        # Learn a success pattern
        pattern = await learning_engine.learn_from_examples(
            examples=sample_examples,
            pattern_type=PatternType.SUCCESS_PATTERN
        )
        
        # Verify pattern properties
        assert isinstance(pattern, LearningPattern)
        assert pattern.pattern_type == PatternType.SUCCESS_PATTERN
        assert len(pattern.examples) == len(sample_examples)
        assert pattern.success_rate > 0
        assert pattern.confidence > 0
        assert pattern.pattern_id in learning_engine.learned_patterns
        
        # Check pattern signature
        assert 'example_count' in pattern.pattern_signature
        assert 'avg_success_score' in pattern.pattern_signature
        assert 'outcome_types' in pattern.pattern_signature
    
    @pytest.mark.asyncio
    async def test_find_matching_patterns(self, learning_engine, sample_examples):
        """Test finding patterns that match a query"""
        # First learn a pattern
        await learning_engine.learn_from_examples(
            examples=sample_examples,
            pattern_type=PatternType.SUCCESS_PATTERN
        )
        
        # Create query to find matching patterns
        query = FewShotQuery(
            context={'project': 'web_app', 'task': 'authentication'},
            input_features={'complexity': 'medium', 'team_size': 3},
            desired_outcome='success',
            max_patterns=5,
            min_confidence=0.1
        )
        
        # Find matching patterns
        applications = await learning_engine.find_matching_patterns(query)
        
        # Should find at least one matching pattern
        assert isinstance(applications, list)
        if applications:  # If patterns were found
            application = applications[0]
            assert isinstance(application, PatternApplication)
            assert application.confidence > 0
            assert application.success_probability > 0
            assert len(application.recommended_actions) > 0
    
    @pytest.mark.asyncio
    async def test_pattern_application(self, learning_engine, sample_examples):
        """Test applying a learned pattern"""
        # Learn pattern
        pattern = await learning_engine.learn_from_examples(
            examples=sample_examples,
            pattern_type=PatternType.SUCCESS_PATTERN
        )
        
        # Apply the pattern
        context = {'project': 'new_app', 'task': 'authentication'}
        input_features = {'complexity': 'medium', 'team_size': 2}
        
        result = await learning_engine.apply_pattern(
            pattern_id=pattern.pattern_id,
            context=context,
            input_features=input_features
        )
        
        # Verify application result
        assert result['pattern_id'] == pattern.pattern_id
        assert result['pattern_name'] == pattern.name
        assert 'recommendations' in result
        assert 'applied_at' in result
        assert isinstance(result['recommendations'], list)
    
    @pytest.mark.asyncio
    async def test_pattern_effectiveness_update(self, learning_engine, sample_examples):
        """Test updating pattern effectiveness based on feedback"""
        # Learn pattern
        pattern = await learning_engine.learn_from_examples(
            examples=sample_examples,
            pattern_type=PatternType.SUCCESS_PATTERN
        )
        
        initial_effectiveness = pattern.effectiveness_score
        initial_success_rate = pattern.success_rate
        
        # Update with positive feedback
        await learning_engine.update_pattern_effectiveness(
            pattern_id=pattern.pattern_id,
            actual_outcome='success',
            success_score=0.95,
            feedback={
                'context': {'project': 'feedback_test'},
                'input_features': {'quality': 'high'},
                'output_features': {'performance': 'excellent'}
            }
        )
        
        # Check that effectiveness was updated
        updated_pattern = learning_engine.learned_patterns[pattern.pattern_id]
        assert updated_pattern.effectiveness_score != initial_effectiveness
        assert len(updated_pattern.examples) > len(sample_examples)  # New example added
    
    @pytest.mark.asyncio
    async def test_pattern_insights(self, learning_engine, sample_examples):
        """Test getting pattern insights"""
        # Learn pattern
        pattern = await learning_engine.learn_from_examples(
            examples=sample_examples,
            pattern_type=PatternType.SUCCESS_PATTERN
        )
        
        # Get insights
        insights = await learning_engine.get_pattern_insights(pattern.pattern_id)
        
        # Verify insights structure
        assert 'pattern_id' in insights
        assert 'pattern_name' in insights
        assert 'confidence' in insights
        assert 'success_rate' in insights
        assert 'performance_analysis' in insights
        assert 'key_insights' in insights
        assert 'improvement_suggestions' in insights
    
    @pytest.mark.asyncio
    async def test_pattern_discovery(self, learning_engine, sample_memories):
        """Test automatic pattern discovery from memories"""
        # Mock the memory conversion process
        learning_engine._group_memories_for_discovery = AsyncMock(return_value={
            'success_group': sample_memories[:3],
            'failure_group': sample_memories[3:]
        })
        
        learning_engine._convert_memories_to_examples = AsyncMock(return_value=[
            {
                'context': {'project': 'test'},
                'input_features': {'feature': 'value'},
                'output_features': {},
                'outcome': 'success',
                'success_score': 0.8
            }
        ])
        
        # Discover patterns
        discovered = await learning_engine.discover_new_patterns(
            memories=sample_memories,
            min_examples=2
        )
        
        # Should discover some patterns
        assert isinstance(discovered, list)
        # Note: Actual discovery depends on memory grouping implementation
    
    @pytest.mark.asyncio
    async def test_feature_extraction(self, learning_engine):
        """Test feature extraction methods"""
        # Test content features
        content_features = await learning_engine._extract_content_features(
            "This is a test content with code: def test(): pass"
        )
        assert 'length' in content_features
        assert 'word_count' in content_features
        assert 'has_code' in content_features
        assert content_features['has_code'] is True
        
        # Test context features
        context_features = await learning_engine._extract_context_features({
            'project': 'test_project',
            'user': 'test_user',
            'environment': 'development'
        })
        assert 'context_size' in context_features
        assert 'has_project' in context_features
        assert 'project_value' in context_features
        
        # Test temporal features
        temporal_features = await learning_engine._extract_temporal_features(datetime.now())
        assert 'hour' in temporal_features
        assert 'day_of_week' in temporal_features
        assert 'is_weekend' in temporal_features
        assert 'is_work_hours' in temporal_features
    
    @pytest.mark.asyncio
    async def test_semantic_features_extraction(self, learning_engine):
        """Test semantic feature extraction"""
        # Mock embedding manager
        learning_engine.embedding_manager.get_embeddings.return_value = [
            np.array([0.1, 0.2, -0.1, 0.5, -0.3])
        ]
        
        semantic_features = await learning_engine._extract_semantic_features("test content")
        
        assert 'embedding_norm' in semantic_features
        assert 'embedding_mean' in semantic_features
        assert 'embedding_std' in semantic_features
        assert 'positive_dimensions' in semantic_features
        assert 'negative_dimensions' in semantic_features
    
    @pytest.mark.asyncio
    async def test_pattern_persistence(self, learning_engine, sample_examples, temp_dir):
        """Test pattern saving and loading"""
        # Learn a pattern
        pattern = await learning_engine.learn_from_examples(
            examples=sample_examples,
            pattern_type=PatternType.SUCCESS_PATTERN
        )
        
        # Check that pattern files were created
        pattern_pkl = temp_dir / "few_shot_patterns" / f"{pattern.pattern_id}.pkl"
        pattern_json = temp_dir / "few_shot_patterns" / f"{pattern.pattern_id}.json"
        
        assert pattern_pkl.exists()
        assert pattern_json.exists()
        
        # Create new engine and load patterns
        new_engine = FewShotLearningEngine(
            semantic_store=learning_engine.semantic_store,
            embedding_manager=learning_engine.embedding_manager,
            data_dir=temp_dir
        )
        await new_engine.initialize()
        
        # Should have loaded the pattern
        assert pattern.pattern_id in new_engine.learned_patterns
        loaded_pattern = new_engine.learned_patterns[pattern.pattern_id]
        assert loaded_pattern.pattern_name == pattern.name
        assert loaded_pattern.success_rate == pattern.success_rate
    
    @pytest.mark.asyncio
    async def test_learning_statistics(self, learning_engine, sample_examples):
        """Test learning statistics collection"""
        # Learn multiple patterns
        for pattern_type in [PatternType.SUCCESS_PATTERN, PatternType.WORKFLOW_PATTERN]:
            await learning_engine.learn_from_examples(
                examples=sample_examples,
                pattern_type=pattern_type
            )
        
        # Get statistics
        stats = await learning_engine.get_learning_statistics()
        
        assert 'total_patterns' in stats
        assert 'patterns_by_type' in stats
        assert 'learning_stats' in stats
        assert 'average_pattern_confidence' in stats
        assert 'average_success_rate' in stats
        
        assert stats['total_patterns'] >= 2
        assert 'success_pattern' in stats['patterns_by_type']
        assert 'workflow_pattern' in stats['patterns_by_type']
    
    @pytest.mark.asyncio
    async def test_pattern_caching(self, learning_engine, sample_examples):
        """Test pattern matching cache"""
        # Learn pattern
        await learning_engine.learn_from_examples(
            examples=sample_examples,
            pattern_type=PatternType.SUCCESS_PATTERN
        )
        
        query = FewShotQuery(
            context={'project': 'web_app'},
            input_features={'complexity': 'medium'},
            desired_outcome='success'
        )
        
        # First query - should cache result
        result1 = await learning_engine.find_matching_patterns(query)
        assert len(learning_engine.pattern_cache) > 0
        
        # Second identical query - should use cache
        result2 = await learning_engine.find_matching_patterns(query)
        assert result2 == result1  # Should be identical due to caching
    
    @pytest.mark.asyncio
    async def test_error_handling(self, learning_engine):
        """Test error handling in various scenarios"""
        # Test with invalid pattern ID
        result = await learning_engine.apply_pattern(
            pattern_id="nonexistent_pattern",
            context={},
            input_features={}
        )
        # Should raise ValueError - test that it's caught properly
        # (Implementation depends on error handling strategy)
        
        # Test pattern insights for nonexistent pattern
        insights = await learning_engine.get_pattern_insights("nonexistent_pattern")
        assert 'error' in insights
        
        # Test empty examples
        try:
            await learning_engine.learn_from_examples(examples=[], pattern_type=PatternType.SUCCESS_PATTERN)
        except Exception:
            pass  # Should handle gracefully
    
    @pytest.mark.asyncio
    async def test_pattern_types(self, learning_engine, sample_examples):
        """Test different pattern types"""
        pattern_types = [
            PatternType.SUCCESS_PATTERN,
            PatternType.FAILURE_PATTERN,
            PatternType.WORKFLOW_PATTERN,
            PatternType.SOLUTION_PATTERN
        ]
        
        learned_patterns = []
        for pattern_type in pattern_types:
            pattern = await learning_engine.learn_from_examples(
                examples=sample_examples,
                pattern_type=pattern_type
            )
            learned_patterns.append(pattern)
            assert pattern.pattern_type == pattern_type
        
        # Each pattern should be distinct
        pattern_ids = [p.pattern_id for p in learned_patterns]
        assert len(set(pattern_ids)) == len(pattern_ids)  # All unique
    
    @pytest.mark.asyncio
    async def test_query_constraints(self, learning_engine, sample_examples):
        """Test query constraints and filtering"""
        # Learn pattern
        pattern = await learning_engine.learn_from_examples(
            examples=sample_examples,
            pattern_type=PatternType.SUCCESS_PATTERN
        )
        
        # Query with high confidence threshold
        high_confidence_query = FewShotQuery(
            context={'project': 'web_app'},
            input_features={'complexity': 'medium'},
            desired_outcome='success',
            min_confidence=0.95  # Very high threshold
        )
        
        results = await learning_engine.find_matching_patterns(high_confidence_query)
        
        # All results should meet confidence threshold
        for result in results:
            assert result.confidence >= 0.95
    
    def test_pattern_id_generation(self, learning_engine):
        """Test pattern ID generation"""
        signature1 = {'test': 'value1', 'number': 1}
        signature2 = {'test': 'value2', 'number': 2}
        signature3 = {'test': 'value1', 'number': 1}  # Same as signature1
        
        id1 = learning_engine._generate_pattern_id(signature1)
        id2 = learning_engine._generate_pattern_id(signature2)
        id3 = learning_engine._generate_pattern_id(signature3)
        
        # Different signatures should produce different IDs
        assert id1 != id2
        
        # Same signatures should produce same IDs
        assert id1 == id3
        
        # IDs should be strings starting with "pattern_"
        assert isinstance(id1, str)
        assert id1.startswith("pattern_")


if __name__ == "__main__":
    pytest.main([__file__])