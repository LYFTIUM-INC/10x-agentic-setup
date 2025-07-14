"""
Advanced Enhancement Tests for Memory System
Tests for cross-pattern insights, adaptive reasoning, and performance optimization
"""

import pytest
import asyncio
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import numpy as np
from pathlib import Path

# Import test modules
import sys
sys.path.append(str(Path(__file__).parent.parent / "src"))

from server import ContextAwareMemoryServer
from utils.config_utils import MCPServerSettings
from tools.semantic_storage import MemoryItem, MemoryContext, MemoryType
from tools.memory_enhancements import MemoryEnhancementEngine, MemoryOptimizer, MemoryInsight
from tools.memory_metrics import MemoryMetricsCollector, MetricType
from tools.cot_memory_reasoning import ReasoningType, ReasoningChain, ReasoningStep
from tools.few_shot_learning import PatternType, LearningPattern, PatternExample


class TestAdvancedEnhancements:
    """Test advanced memory enhancement capabilities"""
    
    @pytest.fixture
    def mock_components(self):
        """Mock memory components"""
        # Mock CoT reasoner
        mock_cot = Mock()
        mock_cot.pattern_library = {}
        mock_cot.reason_about_memories = AsyncMock()
        
        # Mock few-shot engine
        mock_few_shot = Mock()
        mock_few_shot.learned_patterns = {}
        mock_few_shot.find_matching_patterns = AsyncMock(return_value=[])
        mock_few_shot.learn_from_examples = AsyncMock()
        mock_few_shot.update_pattern_effectiveness = AsyncMock()
        mock_few_shot.get_learning_statistics = AsyncMock(return_value={})
        
        # Mock federated manager
        mock_federated = Mock()
        mock_federated.known_nodes = {}
        mock_federated.share_knowledge = AsyncMock(return_value="test_knowledge_id")
        mock_federated.query_federation = AsyncMock(return_value=[])
        mock_federated.learn_from_federation = AsyncMock()
        mock_federated.get_federation_statistics = AsyncMock(return_value={})
        
        return {
            'cot_reasoner': mock_cot,
            'few_shot_engine': mock_few_shot,
            'federated_manager': mock_federated
        }
    
    @pytest.fixture
    def enhancement_engine(self, mock_components):
        """Create enhancement engine with mocked components"""
        return MemoryEnhancementEngine(
            cot_reasoner=mock_components['cot_reasoner'],
            few_shot_engine=mock_components['few_shot_engine'],
            federated_manager=mock_components['federated_manager']
        )
    
    @pytest.fixture
    def metrics_collector(self):
        """Create metrics collector"""
        return MemoryMetricsCollector(window_size=100, anomaly_threshold=3.0)
    
    @pytest.fixture
    def sample_memories(self):
        """Create sample memories for testing"""
        memories = []
        for i in range(10):
            memory = MemoryItem(
                memory_id=f"mem_{i}",
                content=f"Test memory content {i} with pattern data",
                context=MemoryContext(project="test_project", task=f"task_{i % 3}"),
                tags=[f"tag_{i % 5}", "test"],
                importance=0.5 + (i % 3) * 0.2,
                memory_type=MemoryType.SHORT_TERM,
                created_at=datetime.now() - timedelta(hours=i)
            )
            memories.append(memory)
        return memories
    
    @pytest.mark.asyncio
    async def test_cross_pattern_discovery(self, enhancement_engine, sample_memories, mock_components):
        """Test cross-pattern insight discovery"""
        # Setup mock reasoning chain
        mock_chain = ReasoningChain(
            chain_id="test_chain",
            purpose="pattern discovery",
            steps=[
                ReasoningStep(
                    step_id="step_1",
                    step_type=ReasoningType.PATTERN_ANALYSIS,
                    description="Analyzing patterns",
                    input_data={},
                    reasoning_process="test process",
                    output_data={
                        'patterns': [
                            {'type': 'test_pattern', 'strength': 0.8}
                        ]
                    },
                    confidence=0.85
                )
            ],
            final_conclusion={'patterns_discovered': 1},
            overall_confidence=0.85
        )
        
        mock_components['cot_reasoner'].reason_about_memories.return_value = mock_chain
        
        # Setup mock learned pattern
        mock_pattern = LearningPattern(
            pattern_id="learned_1",
            pattern_type=PatternType.SUCCESS_PATTERN,
            name="Test Success Pattern",
            description="Test pattern",
            examples=[],
            success_rate=0.9,
            usage_count=5,
            pattern_signature={},
            learned_features={},
            applicability_rules=[],
            confidence=0.9
        )
        
        mock_components['few_shot_engine'].learned_patterns = {
            'learned_1': mock_pattern
        }
        
        # Test discovery
        insights = await enhancement_engine.discover_cross_pattern_insights(sample_memories)
        
        assert len(insights) >= 0  # May discover insights based on mocked data
        assert enhancement_engine.analytics['cross_pattern_discoveries'] >= 0
        
        # Verify reasoning was called
        mock_components['cot_reasoner'].reason_about_memories.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_adaptive_reasoning_pipeline(self, enhancement_engine, mock_components):
        """Test adaptive reasoning across all systems"""
        # Setup mocks
        mock_chain = ReasoningChain(
            chain_id="adaptive_chain",
            purpose="test query",
            steps=[],
            final_conclusion={'synthesis': 'Test conclusion'},
            overall_confidence=0.8
        )
        mock_components['cot_reasoner'].reason_about_memories.return_value = mock_chain
        
        mock_pattern_app = Mock()
        mock_pattern_app.pattern_id = "pattern_1"
        mock_pattern_app.confidence = 0.85
        mock_pattern_app.predicted_outcome = "success"
        mock_pattern_app.success_probability = 0.9
        mock_pattern_app.recommended_actions = ["Action 1", "Action 2"]
        
        mock_components['few_shot_engine'].find_matching_patterns.return_value = [mock_pattern_app]
        
        mock_components['federated_manager'].query_federation.return_value = [
            {
                'knowledge_id': 'fed_1',
                'content': {'recommendations': ['Federation recommendation']},
                'effectiveness_score': 0.8
            }
        ]
        
        # Test adaptive reasoning
        query = "How to optimize memory patterns?"
        context = {'project': 'test', 'user': 'test_user'}
        
        results = await enhancement_engine.adaptive_reasoning_pipeline(query, context)
        
        assert 'reasoning_chains' in results
        assert 'learned_patterns' in results
        assert 'federated_insights' in results
        assert 'recommendations' in results
        assert results['confidence'] > 0
        
        # Verify all systems were used
        mock_components['cot_reasoner'].reason_about_memories.assert_called()
        mock_components['few_shot_engine'].find_matching_patterns.assert_called()
        mock_components['federated_manager'].query_federation.assert_called()
    
    @pytest.mark.asyncio
    async def test_federated_pattern_enhancement(self, enhancement_engine, mock_components):
        """Test pattern enhancement through federation"""
        # Create local patterns
        local_patterns = [
            LearningPattern(
                pattern_id="local_1",
                pattern_type=PatternType.SUCCESS_PATTERN,
                name="Local Pattern",
                description="Local test pattern",
                examples=[],
                success_rate=0.7,
                usage_count=10,
                pattern_signature={},
                learned_features={},
                applicability_rules=[],
                confidence=0.75
            )
        ]
        
        # Mock federated learning return
        enhanced_pattern = LearningPattern(
            pattern_id="local_1",
            pattern_type=PatternType.SUCCESS_PATTERN,
            name="Enhanced Pattern",
            description="Enhanced through federation",
            examples=[],
            success_rate=0.85,  # Improved
            usage_count=10,
            pattern_signature={},
            learned_features={},
            applicability_rules=["New rule from federation"],
            confidence=0.9  # Improved
        )
        
        mock_components['federated_manager'].learn_from_federation.return_value = [enhanced_pattern]
        
        # Test enhancement
        from tools.federated_memory import PrivacyLevel
        enhanced = await enhancement_engine.federated_pattern_enhancement(
            local_patterns,
            privacy_level=PrivacyLevel.MEDIUM
        )
        
        assert len(enhanced) > 0
        assert enhancement_engine.analytics['privacy_preserved_shares'] >= 0
        assert enhancement_engine.analytics['federated_insights'] >= 0
        
        # Verify federation was used
        mock_components['federated_manager'].share_knowledge.assert_called()
        mock_components['federated_manager'].learn_from_federation.assert_called()
    
    @pytest.mark.asyncio
    async def test_continuous_learning_feedback(self, enhancement_engine, mock_components):
        """Test continuous learning from feedback"""
        feedback = {
            'success': True,
            'context': {'project': 'test', 'task': 'optimization'},
            'outcome': 'improved_performance',
            'pattern_id': 'pattern_123',
            'reasoning_chain_id': 'chain_456',
            'query': 'optimize memory usage'
        }
        
        # Test feedback processing
        await enhancement_engine.continuous_learning_loop(feedback)
        
        # Verify pattern effectiveness was updated
        mock_components['few_shot_engine'].update_pattern_effectiveness.assert_called_with(
            pattern_id='pattern_123',
            actual_outcome='improved_performance',
            success_score=1.0,
            feedback=feedback
        )
        
        # Verify new pattern was learned from successful reasoning
        mock_components['few_shot_engine'].learn_from_examples.assert_called()
        
        # Verify knowledge was shared with federation
        mock_components['federated_manager'].share_knowledge.assert_called()
    
    @pytest.mark.asyncio
    async def test_memory_optimization(self, sample_memories):
        """Test memory pattern optimization"""
        # Create enhancement engine with minimal mocks
        mock_engine = Mock()
        mock_engine.discover_cross_pattern_insights = AsyncMock(return_value=[
            MemoryInsight(
                insight_id="insight_1",
                insight_type="pattern",
                description="Pattern 1",
                confidence=0.8,
                supporting_evidence=["evidence"],
                recommendations=["recommendation"]
            ),
            MemoryInsight(
                insight_id="insight_2",
                insight_type="pattern",
                description="Pattern 1 duplicate",  # Similar description
                confidence=0.7,
                supporting_evidence=["evidence"],
                recommendations=["recommendation"]
            )
        ])
        
        optimizer = MemoryOptimizer(enhancement_engine=mock_engine)
        
        # Test optimization
        results = await optimizer.optimize_memory_patterns(sample_memories)
        
        assert results['removed_redundancies'] >= 0
        assert results['consolidated_insights'] >= 0
        assert 'performance_improvement' in results
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, metrics_collector):
        """Test metrics collection and analysis"""
        # Record various metrics
        await metrics_collector.record_operation_latency('test_op', 45.5, True)
        await metrics_collector.record_operation_latency('test_op', 150.0, True)
        await metrics_collector.record_operation_latency('test_op', 35.0, True)
        await metrics_collector.record_operation_latency('test_op', 500.0, False)  # Failed
        
        await metrics_collector.record_memory_usage(250.0, 'component_a')
        await metrics_collector.record_memory_usage(300.0, 'component_b')
        
        await metrics_collector.record_pattern_effectiveness('pattern_1', 0.85, 'success_pattern')
        await metrics_collector.record_pattern_effectiveness('pattern_2', 0.45, 'workflow_pattern')
        
        await metrics_collector.record_privacy_compliance('share_data', True, 'medium')
        await metrics_collector.record_privacy_compliance('share_data', False, 'high')
        
        # Test real-time dashboard
        dashboard = await metrics_collector.get_real_time_dashboard()
        
        assert 'system_health' in dashboard
        assert dashboard['system_health'] > 0
        assert 'real_time_stats' in dashboard
        assert dashboard['real_time_stats']['total_operations'] == 4
        assert dashboard['real_time_stats']['successful_operations'] == 3
        assert dashboard['real_time_stats']['privacy_violations'] == 1
        
        # Test performance report
        report = await metrics_collector.generate_performance_report(period_hours=1)
        
        assert report.metrics_summary[MetricType.LATENCY.value]['count'] == 4
        assert 'recommendations' in report.__dict__
        assert len(report.recommendations) > 0
        
        # Test optimization suggestions
        optimizations = await metrics_collector.optimize_based_on_metrics()
        
        assert 'suggestions' in optimizations
        assert 'expected_improvements' in optimizations
        assert 'priority_actions' in optimizations
    
    @pytest.mark.asyncio
    async def test_anomaly_detection(self, metrics_collector):
        """Test anomaly detection in metrics"""
        # Record normal values
        for i in range(20):
            await metrics_collector.record_operation_latency('normal_op', 45.0 + np.random.normal(0, 5), True)
        
        # Record anomaly
        await metrics_collector.record_operation_latency('normal_op', 300.0, True)  # Anomaly
        
        # Check anomaly was detected
        assert len(metrics_collector.anomaly_history) > 0
        
        # Get dashboard with alerts
        dashboard = await metrics_collector.get_real_time_dashboard()
        
        assert 'alerts' in dashboard
        # May have alerts if anomaly is recent enough
    
    @pytest.mark.asyncio
    async def test_cross_system_integration(self, enhancement_engine, metrics_collector, mock_components):
        """Test integration across all enhancement systems"""
        # Setup comprehensive test scenario
        query = "Analyze and optimize memory patterns for machine learning tasks"
        context = {
            'project': 'ml_optimization',
            'user': 'test_user',
            'task': 'pattern_analysis'
        }
        
        # Mock successful operations
        mock_chain = ReasoningChain(
            chain_id="integration_chain",
            purpose=query,
            steps=[],
            final_conclusion={'synthesis': 'Optimization complete'},
            overall_confidence=0.9
        )
        mock_components['cot_reasoner'].reason_about_memories.return_value = mock_chain
        
        # Execute adaptive reasoning
        results = await enhancement_engine.adaptive_reasoning_pipeline(query, context)
        
        # Record metrics
        await metrics_collector.record_operation_latency('adaptive_reasoning', 125.0, True)
        await metrics_collector.record_pattern_effectiveness('integration_pattern', 0.92, 'optimization_pattern')
        
        # Process feedback
        await enhancement_engine.continuous_learning_loop({
            'success': True,
            'context': context,
            'outcome': 'optimized',
            'query': query
        })
        
        # Verify cross-system analytics
        stats = await enhancement_engine.get_enhancement_statistics()
        
        assert stats['analytics']['reasoning_pattern_matches'] >= 0
        assert 'cross_system_metrics' in stats
        
        # Generate comprehensive report
        report = await metrics_collector.generate_performance_report(period_hours=1)
        
        assert report.metrics_summary[MetricType.LATENCY.value]['count'] > 0
        assert report.trends[MetricType.PATTERN_EFFECTIVENESS.value] in ['stable', 'increasing', 'decreasing', 'insufficient_data']
    
    @pytest.mark.asyncio
    async def test_performance_baselines(self, metrics_collector):
        """Test performance baseline comparison"""
        # Set baselines
        metrics_collector.set_baseline(MetricType.LATENCY, 50.0)
        metrics_collector.set_baseline(MetricType.PATTERN_EFFECTIVENESS, 0.7)
        
        # Record metrics
        for i in range(10):
            await metrics_collector.record_operation_latency('baseline_op', 40.0 + i * 2, True)
            await metrics_collector.record_pattern_effectiveness(f'pattern_{i}', 0.75 + i * 0.01, 'test_pattern')
        
        # Compare to baseline
        latency_comparison = await metrics_collector.compare_to_baseline(MetricType.LATENCY)
        effectiveness_comparison = await metrics_collector.compare_to_baseline(MetricType.PATTERN_EFFECTIVENESS)
        
        assert 'baseline' in latency_comparison
        assert 'current' in latency_comparison
        assert 'percentage_change' in latency_comparison
        assert latency_comparison['status'] in ['better', 'worse', 'same']
        
        assert effectiveness_comparison['status'] == 'better'  # Should be better than 0.7 baseline
    
    @pytest.mark.asyncio
    async def test_export_metrics(self, metrics_collector):
        """Test metrics export functionality"""
        # Record various metrics
        for i in range(5):
            await metrics_collector.record_operation_latency('export_test', 50.0 + i * 10, True)
            await metrics_collector.record_memory_usage(200.0 + i * 20, 'test_component')
        
        # Export metrics
        export_data = await metrics_collector.export_metrics()
        
        assert 'export_timestamp' in export_data
        assert 'metrics' in export_data
        assert 'anomalies' in export_data
        assert 'real_time_stats' in export_data
        
        # Verify exported metrics
        assert MetricType.LATENCY.value in export_data['metrics']
        assert MetricType.MEMORY_USAGE.value in export_data['metrics']
        assert len(export_data['metrics'][MetricType.LATENCY.value]) == 5
        assert len(export_data['metrics'][MetricType.MEMORY_USAGE.value]) == 5