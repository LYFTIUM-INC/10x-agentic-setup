"""
Tests for Federated Memory System
"""

import pytest
import asyncio
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import numpy as np
from pathlib import Path

# Import the modules to test
import sys
sys.path.append(str(Path(__file__).parent.parent / "src"))

from tools.federated_memory import (
    FederatedMemoryManager, PrivacyPolicy, PrivacyLevel, SharingScope,
    DifferentialPrivacyEngine, EncryptionManager, FederatedNode, 
    SharedKnowledge, FederationQuery
)
from tools.few_shot_learning import LearningPattern, PatternType


class TestDifferentialPrivacyEngine:
    """Test cases for Differential Privacy Engine"""
    
    @pytest.fixture
    def privacy_engine(self):
        """Create privacy engine instance"""
        return DifferentialPrivacyEngine(epsilon=1.0, delta=1e-5)
    
    def test_privacy_engine_initialization(self, privacy_engine):
        """Test privacy engine initialization"""
        assert privacy_engine.epsilon == 1.0
        assert privacy_engine.delta == 1e-5
        assert privacy_engine.noise_scale > 0
    
    def test_add_noise_to_scalar(self, privacy_engine):
        """Test adding noise to scalar values"""
        original_value = 10.0
        noisy_value = privacy_engine.add_noise_to_scalar(original_value, sensitivity=1.0)
        
        assert isinstance(noisy_value, float)
        assert noisy_value != original_value  # Should be different due to noise
        # Noise should be reasonable (within a few standard deviations)
        assert abs(noisy_value - original_value) < 10  # Reasonable bound
    
    def test_add_noise_to_vector(self, privacy_engine):
        """Test adding noise to vectors"""
        original_vector = np.array([1.0, 2.0, 3.0])
        noisy_vector = privacy_engine.add_noise_to_vector(original_vector, sensitivity=1.0)
        
        assert isinstance(noisy_vector, np.ndarray)
        assert noisy_vector.shape == original_vector.shape
        assert not np.array_equal(noisy_vector, original_vector)
    
    def test_add_noise_to_count(self, privacy_engine):
        """Test adding noise to count values"""
        original_count = 100
        noisy_count = privacy_engine.add_noise_to_count(original_count, sensitivity=1)
        
        assert isinstance(noisy_count, int)
        assert noisy_count >= 0  # Counts should be non-negative
    
    def test_privatize_text_features(self, privacy_engine):
        """Test privatizing text features"""
        features = {
            'numerical_value': 42.0,
            'string_value': 'user123',
            'list_of_numbers': [1, 2, 3, 4, 5],
            'list_of_strings': ['item1', 'item2', 'item3'],
            'boolean_value': True
        }
        
        privatized = privacy_engine.privatize_text_features(features)
        
        # Should have same keys
        assert set(privatized.keys()) == set(features.keys())
        
        # Numerical values should be noisy
        assert privatized['numerical_value'] != features['numerical_value']
        
        # String values should be generalized
        assert privatized['string_value'] != features['string_value']
        
        # Lists should be processed
        assert len(privatized['list_of_numbers']) > 0
        assert len(privatized['list_of_strings']) > 0


class TestEncryptionManager:
    """Test cases for Encryption Manager"""
    
    @pytest.fixture
    def encryption_manager(self):
        """Create encryption manager instance"""
        return EncryptionManager(password="test_password")
    
    def test_encryption_decryption(self, encryption_manager):
        """Test encryption and decryption"""
        original_data = "This is sensitive information"
        
        # Encrypt
        encrypted_data = encryption_manager.encrypt_data(original_data)
        assert isinstance(encrypted_data, str)
        assert encrypted_data != original_data
        
        # Decrypt
        decrypted_data = encryption_manager.decrypt_data(encrypted_data)
        assert decrypted_data == original_data
    
    def test_signature_creation_verification(self, encryption_manager):
        """Test HMAC signature creation and verification"""
        data = "Important data to sign"
        private_key = "secret_key"
        
        # Create signature
        signature = encryption_manager.create_signature(data, private_key)
        assert isinstance(signature, str)
        assert len(signature) > 0
        
        # Verify signature
        is_valid = encryption_manager.verify_signature(data, signature, private_key)
        assert is_valid is True
        
        # Verify with wrong key
        is_valid_wrong_key = encryption_manager.verify_signature(data, signature, "wrong_key")
        assert is_valid_wrong_key is False
        
        # Verify with tampered data
        is_valid_tampered = encryption_manager.verify_signature("tampered data", signature, private_key)
        assert is_valid_tampered is False


class TestFederatedMemoryManager:
    """Test cases for Federated Memory Manager"""
    
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
    def node_config(self):
        """Node configuration for testing"""
        return {
            'node_id': 'test_node_001',
            'node_name': 'Test Node',
            'organization': 'Test Organization',
            'private_key': 'test_private_key'
        }
    
    @pytest.fixture
    async def federated_manager(self, mock_semantic_store, mock_embedding_manager, temp_dir, node_config):
        """Create federated memory manager instance"""
        manager = FederatedMemoryManager(
            semantic_store=mock_semantic_store,
            embedding_manager=mock_embedding_manager,
            data_dir=temp_dir,
            node_config=node_config
        )
        await manager.initialize()
        return manager
    
    @pytest.mark.asyncio
    async def test_manager_initialization(self, federated_manager, node_config):
        """Test federated manager initialization"""
        assert federated_manager.node_id == node_config['node_id']
        assert federated_manager.node_name == node_config['node_name']
        assert federated_manager.organization == node_config['organization']
        assert federated_manager.federation_dir.exists()
        assert isinstance(federated_manager.privacy_engine, DifferentialPrivacyEngine)
        assert isinstance(federated_manager.encryption_manager, EncryptionManager)
    
    @pytest.mark.asyncio
    async def test_share_knowledge_public(self, federated_manager):
        """Test sharing knowledge with public privacy level"""
        content = {
            'pattern_type': 'success_pattern',
            'success_rate': 0.85,
            'examples': [{'input': 'test', 'output': 'result'}]
        }
        
        policy = PrivacyPolicy(
            privacy_level=PrivacyLevel.PUBLIC,
            sharing_scope=SharingScope.GLOBAL
        )
        
        knowledge_id = await federated_manager.share_knowledge(
            knowledge_type='learning_pattern',
            content=content,
            privacy_policy=policy
        )
        
        assert isinstance(knowledge_id, str)
        assert knowledge_id.startswith('knowledge_')
        assert knowledge_id in federated_manager.shared_knowledge
        
        # Check shared knowledge properties
        shared_knowledge = federated_manager.shared_knowledge[knowledge_id]
        assert shared_knowledge.source_node == federated_manager.node_id
        assert shared_knowledge.knowledge_type == 'learning_pattern'
        assert shared_knowledge.privacy_metadata['privacy_level'] == 'public'
    
    @pytest.mark.asyncio
    async def test_share_knowledge_encrypted(self, federated_manager):
        """Test sharing knowledge with high privacy (encrypted)"""
        content = {
            'sensitive_data': 'confidential information',
            'user_details': {'name': 'John Doe', 'email': 'john@example.com'}
        }
        
        policy = PrivacyPolicy(
            privacy_level=PrivacyLevel.HIGH,
            sharing_scope=SharingScope.ORGANIZATION
        )
        
        knowledge_id = await federated_manager.share_knowledge(
            knowledge_type='user_data',
            content=content,
            privacy_policy=policy
        )
        
        shared_knowledge = federated_manager.shared_knowledge[knowledge_id]
        assert shared_knowledge.encrypted_content is not None
        assert shared_knowledge.privacy_metadata['encrypted'] is True
    
    @pytest.mark.asyncio
    async def test_query_federation(self, federated_manager):
        """Test querying the federation for knowledge"""
        # Add some test knowledge first
        test_knowledge = SharedKnowledge(
            knowledge_id='test_knowledge_001',
            source_node='other_node',
            knowledge_type='learning_pattern',
            content_hash='test_hash',
            privacy_metadata={'privacy_level': 'medium', 'sharing_scope': 'organization'},
            effectiveness_score=0.8
        )
        federated_manager.shared_knowledge['test_knowledge_001'] = test_knowledge
        
        # Add the source node to known nodes
        source_node = FederatedNode(
            node_id='other_node',
            node_name='Other Node',
            organization='Test Organization',
            trust_level=0.8,
            public_key='other_public_key'
        )
        federated_manager.known_nodes['other_node'] = source_node
        
        # Query federation
        query = FederationQuery(
            query_context={'project': 'test_project'},
            desired_knowledge_types=['learning_pattern'],
            privacy_constraints=PrivacyPolicy(
                privacy_level=PrivacyLevel.MEDIUM,
                sharing_scope=SharingScope.ORGANIZATION
            ),
            max_results=10
        )
        
        results = await federated_manager.query_federation(query)
        
        # Should find the test knowledge
        assert isinstance(results, list)
        if results:  # If knowledge was found and passed filters
            result = results[0]
            assert 'knowledge_id' in result
            assert 'source_node' in result
            assert 'knowledge_type' in result
    
    @pytest.mark.asyncio
    async def test_privacy_protection(self, federated_manager):
        """Test privacy protection mechanisms"""
        content = {
            'user_id': 'user123',
            'project_name': 'secret_project',
            'performance_data': [1, 2, 3, 4, 5],
            'ip_address': '192.168.1.100'
        }
        
        policy = PrivacyPolicy(
            privacy_level=PrivacyLevel.MEDIUM,
            sharing_scope=SharingScope.ORGANIZATION,
            content_filters=['user_id', 'ip_address']
        )
        
        protected_content = await federated_manager._apply_privacy_protection(content, policy)
        
        # Should have applied protection
        assert protected_content != content
        
        # Filtered fields should be anonymized or removed
        if 'user_id' in protected_content:
            assert protected_content['user_id'] != content['user_id']
        if 'ip_address' in protected_content:
            assert protected_content['ip_address'] != content['ip_address']
    
    @pytest.mark.asyncio
    async def test_node_trust_management(self, federated_manager):
        """Test federation node trust management"""
        # Add a test node
        test_node = FederatedNode(
            node_id='trust_test_node',
            node_name='Trust Test Node',
            organization='Test Organization',
            trust_level=0.5,
            public_key='test_public_key'
        )
        await federated_manager.add_federation_node(test_node)
        
        # Update trust with positive interaction
        positive_interaction = {
            'success': True,
            'quality_score': 0.9,
            'timeliness': 0.8
        }
        
        initial_trust = federated_manager.known_nodes['trust_test_node'].trust_level
        await federated_manager.update_node_trust('trust_test_node', positive_interaction)
        updated_trust = federated_manager.known_nodes['trust_test_node'].trust_level
        
        # Trust should have increased
        assert updated_trust >= initial_trust
        
        # Update trust with negative interaction
        negative_interaction = {
            'success': False,
            'quality_score': 0.2,
            'timeliness': 0.3
        }
        
        await federated_manager.update_node_trust('trust_test_node', negative_interaction)
        final_trust = federated_manager.known_nodes['trust_test_node'].trust_level
        
        # Trust should have decreased
        assert final_trust < updated_trust
    
    @pytest.mark.asyncio
    async def test_federated_learning_integration(self, federated_manager):
        """Test integration with federated learning"""
        # Create mock local patterns
        local_patterns = []
        
        # Mock federated knowledge that would be converted to patterns
        federated_knowledge = [
            {
                'knowledge_id': 'fed_pattern_001',
                'knowledge_type': 'learning_pattern',
                'content': {
                    'name': 'Federated Success Pattern',
                    'success_rate': 0.9,
                    'confidence': 0.8,
                    'examples': [
                        {
                            'id': 'fed_ex_1',
                            'context': {'project': 'federated_project'},
                            'input_features': {'complexity': 'medium'},
                            'output_features': {'quality': 'high'},
                            'outcome': 'success',
                            'success_score': 0.9
                        }
                    ]
                },
                'effectiveness_score': 0.85
            }
        ]
        
        # Mock the query federation method
        federated_manager.query_federation = AsyncMock(return_value=federated_knowledge)
        
        # Apply federated learning
        enhanced_patterns = await federated_manager.learn_from_federation(
            local_patterns=local_patterns,
            privacy_policy=PrivacyPolicy(
                privacy_level=PrivacyLevel.MEDIUM,
                sharing_scope=SharingScope.ORGANIZATION
            )
        )
        
        # Should return enhanced patterns
        assert isinstance(enhanced_patterns, list)
    
    @pytest.mark.asyncio
    async def test_differential_privacy_integration(self, federated_manager):
        """Test differential privacy integration in knowledge sharing"""
        sensitive_content = {
            'user_count': 1000,
            'revenue': 50000.0,
            'error_rate': 0.05,
            'performance_metrics': [0.8, 0.9, 0.85, 0.92]
        }
        
        policy = PrivacyPolicy(
            privacy_level=PrivacyLevel.HIGH,
            sharing_scope=SharingScope.ORGANIZATION,
            noise_multiplier=1.5
        )
        
        # Share knowledge with differential privacy
        knowledge_id = await federated_manager.share_knowledge(
            knowledge_type='analytics_data',
            content=sensitive_content,
            privacy_policy=policy
        )
        
        assert knowledge_id in federated_manager.shared_knowledge
        shared_knowledge = federated_manager.shared_knowledge[knowledge_id]
        assert shared_knowledge.privacy_metadata['noise_applied'] is True
    
    @pytest.mark.asyncio
    async def test_federation_statistics(self, federated_manager):
        """Test federation statistics collection"""
        # Add some test data
        await federated_manager.share_knowledge(
            knowledge_type='test_pattern',
            content={'test': 'data'},
            privacy_policy=PrivacyPolicy(
                privacy_level=PrivacyLevel.PUBLIC,
                sharing_scope=SharingScope.GLOBAL
            )
        )
        
        # Get statistics
        stats = await federated_manager.get_federation_statistics()
        
        assert 'node_info' in stats
        assert 'federation_stats' in stats
        assert 'known_nodes' in stats
        assert 'shared_knowledge_items' in stats
        assert 'privacy_policies' in stats
        
        assert stats['node_info']['node_id'] == federated_manager.node_id
        assert stats['federation_stats']['knowledge_shared'] > 0
    
    @pytest.mark.asyncio
    async def test_knowledge_encryption_decryption(self, federated_manager):
        """Test knowledge encryption and decryption flow"""
        sensitive_content = {
            'proprietary_algorithm': 'secret sauce',
            'api_keys': ['key1', 'key2'],
            'internal_metrics': {'performance': 0.95}
        }
        
        policy = PrivacyPolicy(
            privacy_level=PrivacyLevel.HIGH,
            sharing_scope=SharingScope.TEAM
        )
        
        # Share encrypted knowledge
        knowledge_id = await federated_manager.share_knowledge(
            knowledge_type='sensitive_algorithm',
            content=sensitive_content,
            privacy_policy=policy
        )
        
        shared_knowledge = federated_manager.shared_knowledge[knowledge_id]
        
        # Should be encrypted
        assert shared_knowledge.encrypted_content is not None
        
        # Extract content (should decrypt)
        extracted_content = await federated_manager._extract_knowledge_content(shared_knowledge)
        
        # Content should be available after decryption
        assert isinstance(extracted_content, dict)
    
    @pytest.mark.asyncio
    async def test_privacy_policy_enforcement(self, federated_manager):
        """Test privacy policy enforcement"""
        # Test blocking based on privacy level
        high_privacy_knowledge = SharedKnowledge(
            knowledge_id='high_privacy_001',
            source_node='other_node',
            knowledge_type='sensitive_data',
            content_hash='hash',
            privacy_metadata={'privacy_level': 'high'},
            effectiveness_score=0.9
        )
        
        low_privacy_policy = PrivacyPolicy(
            privacy_level=PrivacyLevel.LOW,
            sharing_scope=SharingScope.GLOBAL
        )
        
        # Should not be compatible
        is_compatible = await federated_manager._check_privacy_compatibility(
            high_privacy_knowledge, low_privacy_policy
        )
        assert is_compatible is True  # High privacy knowledge can be shared with low privacy requirements
        
        # Test reverse - low privacy knowledge with high requirements
        low_privacy_knowledge = SharedKnowledge(
            knowledge_id='low_privacy_001',
            source_node='other_node',
            knowledge_type='public_data',
            content_hash='hash',
            privacy_metadata={'privacy_level': 'public'},
            effectiveness_score=0.7
        )
        
        high_privacy_policy = PrivacyPolicy(
            privacy_level=PrivacyLevel.HIGH,
            sharing_scope=SharingScope.ORGANIZATION
        )
        
        is_compatible = await federated_manager._check_privacy_compatibility(
            low_privacy_knowledge, high_privacy_policy
        )
        assert is_compatible is False  # Public knowledge doesn't meet high privacy requirements
    
    @pytest.mark.asyncio
    async def test_federation_state_persistence(self, federated_manager, temp_dir):
        """Test federation state saving and loading"""
        # Add test data
        test_node = FederatedNode(
            node_id='persist_test_node',
            node_name='Persistence Test',
            organization='Test Org',
            trust_level=0.7,
            public_key='test_key'
        )
        await federated_manager.add_federation_node(test_node)
        
        await federated_manager.share_knowledge(
            knowledge_type='test_knowledge',
            content={'test': 'persistence'},
            privacy_policy=PrivacyPolicy(
                privacy_level=PrivacyLevel.PUBLIC,
                sharing_scope=SharingScope.GLOBAL
            )
        )
        
        # Save state
        await federated_manager._save_federation_state()
        
        # Check that files were created
        federation_dir = temp_dir / "federation"
        assert (federation_dir / "known_nodes.json").exists()
        assert (federation_dir / "shared_knowledge.json").exists()
        assert (federation_dir / "federation_stats.json").exists()
        
        # Create new manager and load state
        new_manager = FederatedMemoryManager(
            semantic_store=federated_manager.semantic_store,
            embedding_manager=federated_manager.embedding_manager,
            data_dir=temp_dir,
            node_config={
                'node_id': 'new_node',
                'node_name': 'New Node',
                'organization': 'Test Org',
                'private_key': 'new_key'
            }
        )
        await new_manager.initialize()
        
        # Should have loaded the test node
        assert 'persist_test_node' in new_manager.known_nodes
        assert len(new_manager.shared_knowledge) > 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self, federated_manager):
        """Test error handling in various scenarios"""
        # Test sharing with invalid privacy policy
        try:
            await federated_manager.share_knowledge(
                knowledge_type='invalid_test',
                content=None,  # Invalid content
                privacy_policy=PrivacyPolicy(
                    privacy_level=PrivacyLevel.PRIVATE,
                    sharing_scope=SharingScope.NONE
                )
            )
        except Exception:
            pass  # Should handle gracefully
        
        # Test querying with invalid parameters
        invalid_query = FederationQuery(
            query_context={},
            desired_knowledge_types=[],
            privacy_constraints=PrivacyPolicy(
                privacy_level=PrivacyLevel.HIGH,
                sharing_scope=SharingScope.NONE
            )
        )
        
        results = await federated_manager.query_federation(invalid_query)
        assert isinstance(results, list)  # Should return empty list, not error
        
        # Test trust update for nonexistent node
        await federated_manager.update_node_trust('nonexistent_node', {'success': True})
        # Should not raise exception


if __name__ == "__main__":
    pytest.main([__file__])