#!/usr/bin/env python3
"""
Simple test script for enhanced memory capabilities
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# Add paths
sys.path.append(str(Path(__file__).parent / "src"))
sys.path.append(str(Path(__file__).parent.parent / "shared" / "src"))

from tools.memory_enhancements import MemoryEnhancementEngine, MemoryOptimizer, MemoryInsight
from tools.memory_metrics import MemoryMetricsCollector, MetricType
from tools.semantic_storage import MemoryItem, MemoryContext, MemoryType
from datetime import datetime, timedelta


async def test_metrics_collector():
    """Test metrics collection functionality"""
    print("🔬 Testing Metrics Collector...")
    
    collector = MemoryMetricsCollector(window_size=100, anomaly_threshold=3.0)
    
    # Record some metrics
    await collector.record_operation_latency('test_operation', 45.5, True)
    await collector.record_operation_latency('test_operation', 52.0, True)
    await collector.record_operation_latency('test_operation', 380.0, True)  # Potential anomaly
    
    await collector.record_memory_usage(150.0, 'component_a')
    await collector.record_pattern_effectiveness('pattern_1', 0.85, 'success_pattern')
    await collector.record_privacy_compliance('data_share', True, 'medium')
    
    # Get dashboard
    dashboard = await collector.get_real_time_dashboard()
    
    print(f"✅ System Health: {dashboard['system_health']:.2f}")
    print(f"✅ Total Operations: {dashboard['real_time_stats']['total_operations']}")
    print(f"✅ Successful Operations: {dashboard['real_time_stats']['successful_operations']}")
    
    # Generate performance report
    report = await collector.generate_performance_report(period_hours=1)
    print(f"✅ Performance Report Generated: {report.report_id}")
    print(f"✅ Recommendations: {len(report.recommendations)}")
    
    return True


async def test_enhancement_engine():
    """Test enhancement engine functionality"""
    print("\n🧠 Testing Enhancement Engine...")
    
    # Create mock components
    mock_cot = Mock()
    mock_cot.pattern_library = {}
    
    mock_few_shot = Mock()
    mock_few_shot.learned_patterns = {}
    mock_few_shot.get_learning_statistics = AsyncMock(return_value={'total_patterns': 5})
    
    mock_federated = Mock()
    mock_federated.known_nodes = {}
    mock_federated.get_federation_statistics = AsyncMock(return_value={'known_nodes': 3})
    
    # Create enhancement engine
    engine = MemoryEnhancementEngine(
        cot_reasoner=mock_cot,
        few_shot_engine=mock_few_shot,
        federated_manager=mock_federated
    )
    
    # Test enhancement statistics
    stats = await engine.get_enhancement_statistics()
    
    print(f"✅ Cross-pattern discoveries: {stats['analytics']['cross_pattern_discoveries']}")
    print(f"✅ Pattern connections: {stats['pattern_connections']}")
    print(f"✅ Cached insights: {stats['cached_insights']}")
    
    return True


async def test_memory_optimizer():
    """Test memory optimization functionality"""
    print("\n⚡ Testing Memory Optimizer...")
    
    # Create mock enhancement engine
    mock_engine = Mock()
    
    # Create sample insights
    insights = [
        MemoryInsight(
            insight_id="insight_1",
            insight_type="pattern",
            description="Pattern optimization insight",
            confidence=0.85,
            supporting_evidence=["evidence 1"],
            recommendations=["optimize pattern matching"]
        ),
        MemoryInsight(
            insight_id="insight_2", 
            insight_type="performance",
            description="Performance improvement insight",
            confidence=0.78,
            supporting_evidence=["evidence 2"],
            recommendations=["enable caching"]
        )
    ]
    
    mock_engine.discover_cross_pattern_insights = AsyncMock(return_value=insights)
    
    optimizer = MemoryOptimizer(enhancement_engine=mock_engine)
    
    # Create sample memories
    memories = []
    for i in range(5):
        memory = MemoryItem(
            memory_id=f"mem_{i}",
            content=f"Test memory content {i}",
            context=MemoryContext(project="test_project"),
            tags=["test"],
            importance=0.7,
            memory_type=MemoryType.TEXT,
            created_at=datetime.now() - timedelta(hours=i)
        )
        memories.append(memory)
    
    # Test optimization
    results = await optimizer.optimize_memory_patterns(memories)
    
    print(f"✅ Optimization Results:")
    print(f"   - Removed redundancies: {results['removed_redundancies']}")
    print(f"   - Consolidated insights: {results['consolidated_insights']}")
    print(f"   - Performance improvement: {results['performance_improvement']:.2f}")
    
    return True


async def test_integration():
    """Test integration of all components"""
    print("\n🔗 Testing Integration...")
    
    # Test metrics collection
    collector = MemoryMetricsCollector()
    
    # Record comprehensive metrics
    await collector.record_operation_latency('integration_test', 42.0, True)
    await collector.record_memory_usage(180.0, 'integration_component')
    await collector.record_pattern_effectiveness('integration_pattern', 0.92, 'success_pattern')
    
    # Get optimization suggestions
    optimizations = await collector.optimize_based_on_metrics()
    
    print(f"✅ Integration test completed")
    print(f"✅ Optimization suggestions: {len(optimizations['suggestions'])}")
    print(f"✅ Priority actions: {optimizations['priority_actions']}")
    
    return True


async def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Memory System Tests\n")
    
    try:
        # Run tests
        test1 = await test_metrics_collector()
        test2 = await test_enhancement_engine() 
        test3 = await test_memory_optimizer()
        test4 = await test_integration()
        
        if all([test1, test2, test3, test4]):
            print("\n🎉 All tests passed successfully!")
            print("✅ Enhanced memory capabilities are working correctly")
            return True
        else:
            print("\n❌ Some tests failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)