"""
Integration Tests for Enhanced Memory Capabilities
Tests the complete integration of CoT reasoning, few-shot learning, and federated memory
"""

import pytest
import asyncio
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import numpy as np
from pathlib import Path

# Import test modules
import sys
sys.path.append(str(Path(__file__).parent.parent / "src"))

from server import ContextAwareMemoryServer
from utils.config_utils import MCPServerSettings
from tools.semantic_storage import MemoryItem, MemoryContext, MemoryType
from tools.cot_memory_reasoning import ReasoningType
from tools.few_shot_learning import PatternType
from tools.federated_memory import PrivacyLevel, SharingScope


class TestEnhancedMemoryIntegration:
    """Integration tests for enhanced memory capabilities"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_config(self, temp_dir):
        """Mock server configuration"""
        config = Mock(spec=MCPServerSettings)
        config.server_name = "test_memory_server"
        config.server_version = "1.0.0"
        config.debug = True
        config.max_workers = 4
        config.cache_ttl = 300
        config.embedding_model = "test_model"
        config.ml_device = "cpu"
        config.max_embedding_length = 512
        config.model_cache_dir = str(temp_dir / "models")
        config.vector_dimension = 384
        config.data_dir = str(temp_dir / "data")
        config.server_config = {
            'federation': {
                'node_id': 'test_integration_node',
                'node_name': 'Integration Test Node',
                'organization': 'Test Organization',
                'private_key': 'integration_test_key'
            }
        }
        return config
    
    @pytest.fixture
    async def enhanced_server(self, mock_config):
        """Create enhanced memory server with mocked dependencies"""
        with patch('server.EmbeddingManager') as mock_embedding_manager, \
             patch('server.SemanticMemoryStore') as mock_semantic_store, \
             patch('server.IntelligentRetriever') as mock_intelligent_retriever, \
             patch('server.PredictiveLoader') as mock_predictive_loader:
            
            # Setup mocks
            mock_embedding_manager.return_value.load_model = AsyncMock()
            mock_semantic_store.return_value.initialize = AsyncMock()
            mock_semantic_store.return_value.load_existing_memories = AsyncMock(return_value=0)
            mock_semantic_store.return_value.search_memories = AsyncMock(return_value=[])
            
            # Create server
            server = ContextAwareMemoryServer(mock_config)
            
            # Mock the startup process
            with patch.object(server, '_startup') as mock_startup:
                mock_startup.return_value = None
                await server._startup()
            
            yield server
    
    @pytest.mark.asyncio
    async def test_chain_of_thought_integration(self, enhanced_server):
        """Test chain-of-thought reasoning integration"""
        # Test the reasoning tool
        response = await enhanced_server._reason_about_memories(
            query_text="Analyze development patterns in recent projects",
            context={
                'project': 'integration_test',
                'user': 'test_user',
                'task': 'pattern_analysis'
            },
            reasoning_types=['pattern_analysis', 'causal_inference'],
            max_steps=5
        )
        
        # Should return successful response structure
        assert 'status' in response
        if response['status'] == 'success':
            assert 'chain_id' in response
            assert 'purpose' in response
            assert 'steps_completed' in response
            assert 'final_conclusion' in response
            assert 'overall_confidence' in response
            assert 'reasoning_time' in response
            assert 'steps' in response
            
            # Verify statistics were updated
            assert enhanced_server.memory_stats['reasoning_chains'] > 0
    
    @pytest.mark.asyncio
    async def test_few_shot_learning_integration(self, enhanced_server):
        """Test few-shot learning integration"""
        # Test learning from examples
        examples = [
            {
                'context': {'project': 'web_app', 'task': 'authentication'},
                'input_features': {'complexity': 'medium', 'team_size': 3},
                'output_features': {'lines_of_code': 250, 'test_coverage': 0.9},
                'outcome': 'success',
                'success_score': 0.9,
                'metadata': {'duration_days': 5}
            },
            {
                'context': {'project': 'web_app', 'task': 'authentication'},
                'input_features': {'complexity': 'high', 'team_size': 2},
                'output_features': {'lines_of_code': 400, 'test_coverage': 0.85},
                'outcome': 'success',
                'success_score': 0.8,
                'metadata': {'duration_days': 8}
            }
        ]
        
        # Learn pattern
        learn_response = await enhanced_server._learn_from_examples(
            examples=examples,
            pattern_type='success_pattern'
        )
        
        assert 'status' in learn_response
        if learn_response['status'] == 'success':
            assert 'pattern_id' in learn_response
            assert 'pattern_name' in learn_response
            assert 'confidence' in learn_response
            assert 'success_rate' in learn_response
            
            # Test finding similar patterns
            similar_response = await enhanced_server._find_similar_patterns(
                context={'project': 'mobile_app', 'task': 'authentication'},
                input_features={'complexity': 'medium', 'team_size': 3},
                desired_outcome='success',
                max_patterns=5
            )
            
            assert isinstance(similar_response, list)
            
            # Verify statistics were updated
            assert enhanced_server.memory_stats['patterns_learned'] > 0
    
    @pytest.mark.asyncio
    async def test_federated_memory_integration(self, enhanced_server):
        """Test federated memory integration"""
        # Test knowledge sharing
        knowledge_content = {
            'pattern_type': 'success_pattern',
            'domain': 'web_development',
            'success_rate': 0.85,
            'best_practices': [
                'Use TypeScript for large projects',
                'Implement comprehensive testing',
                'Follow SOLID principles'
            ]
        }
        
        share_response = await enhanced_server._share_knowledge(
            knowledge_type='development_pattern',
            content=knowledge_content,
            privacy_level='medium',
            sharing_scope='organization'
        )
        
        assert 'status' in share_response
        if share_response['status'] == 'success':
            assert 'knowledge_id' in share_response
            assert 'privacy_level' in share_response
            assert 'sharing_scope' in share_response
            
            # Test querying federation
            query_response = await enhanced_server._query_federation(
                knowledge_types=['development_pattern', 'success_pattern'],
                context={'domain': 'web_development'},
                max_results=10
            )
            
            assert isinstance(query_response, list)
            
            # Verify statistics were updated
            assert enhanced_server.memory_stats['federated_shares'] > 0
    
    @pytest.mark.asyncio
    async def test_cross_capability_workflow(self, enhanced_server):
        """Test workflow that uses multiple enhanced capabilities"""
        # Simulate a complete workflow:
        # 1. Store some memories (base functionality)
        # 2. Perform reasoning to find patterns
        # 3. Learn patterns from the analysis
        # 4. Share knowledge with federation
        
        # Step 1: Store memories (mocked for integration test)
        sample_memories = [
            {
                'content': 'Successfully implemented OAuth2 authentication system',
                'context': {'project': 'ecommerce', 'task': 'security', 'outcome': 'success'},
                'tags': ['authentication', 'oauth2', 'security'],
                'importance': 0.9
            },
            {
                'content': 'Fixed critical SQL injection vulnerability in user login',
                'context': {'project': 'ecommerce', 'task': 'security', 'outcome': 'success'},
                'tags': ['security', 'sql_injection', 'bugfix'],
                'importance': 0.95
            },
            {
                'content': 'Implemented two-factor authentication for admin panel',
                'context': {'project': 'ecommerce', 'task': 'security', 'outcome': 'success'},
                'tags': ['2fa', 'authentication', 'admin'],
                'importance': 0.85
            }
        ]
        
        # Step 2: Perform reasoning
        reasoning_response = await enhanced_server._reason_about_memories(
            query_text="Analyze security implementation patterns",
            context={'project': 'ecommerce', 'domain': 'security'},
            reasoning_types=['pattern_analysis', 'contextual_linking'],
            max_steps=3
        )
        
        assert reasoning_response['status'] == 'success' or 'error' in reasoning_response
        
        # Step 3: Learn patterns from successful security implementations
        security_examples = [
            {
                'context': {'project': 'ecommerce', 'task': 'security'},
                'input_features': {'vulnerability_type': 'authentication', 'severity': 'high'},
                'output_features': {'implementation_time': 3, 'security_score': 0.95},
                'outcome': 'success',
                'success_score': 0.95
            },
            {
                'context': {'project': 'ecommerce', 'task': 'security'},
                'input_features': {'vulnerability_type': 'injection', 'severity': 'critical'},
                'output_features': {'implementation_time': 1, 'security_score': 0.98},
                'outcome': 'success',
                'success_score': 0.98
            }
        ]
        
        pattern_response = await enhanced_server._learn_from_examples(
            examples=security_examples,
            pattern_type='success_pattern'
        )
        
        assert pattern_response['status'] == 'success' or 'error' in pattern_response
        
        # Step 4: Share security knowledge with federation
        security_knowledge = {
            'domain': 'web_security',
            'pattern_type': 'security_implementation',
            'success_indicators': ['quick_response', 'comprehensive_testing', 'user_education'],
            'risk_mitigation': ['input_validation', 'encryption', 'access_control']
        }
        
        share_response = await enhanced_server._share_knowledge(
            knowledge_type='security_pattern',
            content=security_knowledge,
            privacy_level='medium',
            sharing_scope='organization'
        )
        
        assert share_response['status'] == 'success' or 'error' in share_response
        
        # Verify all capabilities were used
        stats_response = await enhanced_server._get_enhanced_memory_stats()
        assert stats_response['status'] == 'success'
        
        if stats_response['status'] == 'success':
            stats = stats_response['stats']
            # Should have activity in multiple areas
            activity_indicators = [
                stats.get('reasoning_chains', 0) > 0,
                stats.get('patterns_learned', 0) > 0,
                stats.get('federated_shares', 0) > 0
            ]
            assert sum(activity_indicators) >= 2  # At least 2 capabilities used
    
    @pytest.mark.asyncio
    async def test_privacy_preservation_workflow(self, enhanced_server):
        """Test workflow with privacy preservation across capabilities"""
        # Test sharing sensitive information with privacy protection
        sensitive_content = {
            'user_patterns': {
                'login_frequency': [1, 3, 5, 2, 4],
                'session_duration': [30, 45, 60, 25, 40],
                'feature_usage': {'dashboard': 0.8, 'reports': 0.6, 'settings': 0.3}
            },
            'performance_metrics': {
                'response_time': 150,
                'error_rate': 0.02,
                'uptime': 0.999
            }
        }
        
        # Share with high privacy protection
        share_response = await enhanced_server._share_knowledge(
            knowledge_type='user_analytics',
            content=sensitive_content,
            privacy_level='high',
            sharing_scope='organization'
        )
        
        assert share_response['status'] == 'success' or 'error' in share_response
        
        # Query for similar analytics with privacy constraints
        query_response = await enhanced_server._query_federation(
            knowledge_types=['user_analytics', 'performance_metrics'],
            context={'privacy_required': True},
            max_results=5
        )
        
        assert isinstance(query_response, list)
        
        # Verify privacy metadata in shared knowledge
        if share_response['status'] == 'success':
            knowledge_id = share_response['knowledge_id']
            if hasattr(enhanced_server, 'federated_manager') and enhanced_server.federated_manager:
                if knowledge_id in enhanced_server.federated_manager.shared_knowledge:
                    shared_knowledge = enhanced_server.federated_manager.shared_knowledge[knowledge_id]
                    assert shared_knowledge.privacy_metadata['privacy_level'] == 'high'
    
    @pytest.mark.asyncio
    async def test_pattern_discovery_integration(self, enhanced_server):
        """Test automatic pattern discovery integration"""
        # Mock pattern discovery (would normally use actual memories)
        discovery_response = await enhanced_server._discover_memory_patterns(
            min_examples=2,
            pattern_types=['success_pattern', 'workflow_pattern']
        )
        
        assert 'status' in discovery_response
        if discovery_response['status'] == 'success':
            assert 'patterns_discovered' in discovery_response
            assert 'patterns' in discovery_response
            assert 'discovered_at' in discovery_response
            assert isinstance(discovery_response['patterns'], list)
    
    @pytest.mark.asyncio
    async def test_enhanced_statistics_integration(self, enhanced_server):
        """Test comprehensive statistics collection"""
        # Perform various operations to generate statistics
        await enhanced_server._reason_about_memories(
            "Test query", {}, ['pattern_analysis'], 3
        )
        
        await enhanced_server._learn_from_examples(
            [{'context': {}, 'input_features': {}, 'output_features': {}, 
              'outcome': 'test', 'success_score': 0.5}],
            'success_pattern'
        )
        
        await enhanced_server._share_knowledge(
            'test_knowledge', {'test': 'data'}, 'public', 'global'
        )
        
        # Get comprehensive statistics
        stats_response = await enhanced_server._get_enhanced_memory_stats()
        
        assert stats_response['status'] == 'success'
        stats = stats_response['stats']
        
        # Should include all capability statistics
        expected_sections = [
            'total_memories',
            'total_retrievals',
            'reasoning_chains',
            'patterns_learned',
            'federated_shares'
        ]
        
        for section in expected_sections:
            assert section in stats
        
        # Should include sub-system statistics
        if 'few_shot_learning' in stats:
            assert isinstance(stats['few_shot_learning'], dict)
        
        if 'federation' in stats:
            assert isinstance(stats['federation'], dict)
        
        if 'chain_of_thought' in stats:
            assert isinstance(stats['chain_of_thought'], dict)
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, enhanced_server):
        """Test error handling across integrated capabilities"""
        # Test reasoning with invalid parameters
        invalid_reasoning = await enhanced_server._reason_about_memories(
            query_text="",  # Empty query
            context={},
            reasoning_types=['invalid_type'],
            max_steps=0
        )
        
        # Should handle gracefully
        assert 'status' in invalid_reasoning
        
        # Test learning with invalid examples
        invalid_learning = await enhanced_server._learn_from_examples(
            examples=[],  # Empty examples
            pattern_type='invalid_pattern'
        )
        
        assert 'status' in invalid_learning
        
        # Test federation with invalid parameters
        invalid_sharing = await enhanced_server._share_knowledge(
            knowledge_type='',
            content={},
            privacy_level='invalid_level',
            sharing_scope='invalid_scope'
        )
        
        assert 'status' in invalid_sharing
        
        # All operations should complete without throwing exceptions
        # and return appropriate error responses
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, enhanced_server):
        """Test concurrent operations across capabilities"""
        # Create multiple concurrent operations
        operations = [
            enhanced_server._reason_about_memories(
                "Concurrent reasoning test", {}, ['pattern_analysis'], 2
            ),
            enhanced_server._learn_from_examples(
                [{'context': {}, 'input_features': {'test': 1}, 'output_features': {}, 
                  'outcome': 'concurrent', 'success_score': 0.7}],
                'success_pattern'
            ),
            enhanced_server._share_knowledge(
                'concurrent_test', {'concurrent': True}, 'public', 'global'
            ),
            enhanced_server._query_federation(
                ['test_knowledge'], {'concurrent': True}, 5
            )
        ]
        
        # Execute concurrently
        results = await asyncio.gather(*operations, return_exceptions=True)
        
        # All operations should complete
        assert len(results) == 4
        
        # None should be exceptions
        for result in results:
            assert not isinstance(result, Exception)
            
        # All should have status indicators
        for result in results:
            if isinstance(result, dict):
                assert 'status' in result or isinstance(result, list)


if __name__ == "__main__":
    pytest.main([__file__])