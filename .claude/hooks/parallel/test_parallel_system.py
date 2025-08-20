#!/usr/bin/env python3
"""
Test Suite for Parallel MCP Coordination System
Validates the complete parallel coordination functionality
"""

import asyncio
import time
import json
import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules
from dispatch_engine import ParallelDispatcher, TaskResult
from coordination_manager import CoordinationManager, CoordinationTask
from aggregation_engine import AggregationEngine, ResultMetadata, AggregationStrategy

class ParallelSystemTester:
    """Comprehensive tester for the parallel MCP system"""
    
    def __init__(self):
        self.test_results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'performance_metrics': {},
            'detailed_results': []
        }
    
    async def run_all_tests(self):
        """Run all test suites"""
        
        print("🧪 Starting Parallel MCP System Tests...")
        print("=" * 60)
        
        # Test individual components
        await self.test_dispatcher()
        await self.test_coordinator()
        await self.test_aggregator()
        
        # Test integration
        await self.test_end_to_end_integration()
        
        # Performance tests
        await self.test_performance_benchmarks()
        
        # Generate final report
        self.generate_final_report()
    
    async def test_dispatcher(self):
        """Test the ParallelDispatcher"""
        
        print("\n🚀 Testing ParallelDispatcher...")
        
        try:
            async with ParallelDispatcher() as dispatcher:
                # Test 1: Basic dispatch functionality
                await self.run_test("Dispatcher Basic Functionality", 
                                  self.test_dispatcher_basic_functionality(dispatcher))
                
                # Test 2: Server health checks
                await self.run_test("Dispatcher Health Checks",
                                  self.test_dispatcher_health_checks(dispatcher))
                
                # Test 3: Command-specific server selection
                await self.run_test("Command-Specific Server Selection",
                                  self.test_command_specific_selection(dispatcher))
                
                # Test 4: Parallel execution
                await self.run_test("Parallel Execution",
                                  self.test_parallel_execution(dispatcher))
        
        except Exception as e:
            logger.error(f"Dispatcher tests failed: {e}")
            self.record_test_failure("Dispatcher Tests", str(e))
    
    async def test_dispatcher_basic_functionality(self, dispatcher):
        """Test basic dispatcher functionality"""
        
        # Test server registry
        assert len(dispatcher.mcp_servers) == 5, f"Expected 5 servers, got {len(dispatcher.mcp_servers)}"
        
        # Test server capabilities
        expected_servers = {
            'ml-code-intelligence', 'context-aware-memory', 'agentic-workflow',
            'predictive-analytics', 'ml-testing-qa'
        }
        actual_servers = set(dispatcher.mcp_servers.keys())
        assert expected_servers == actual_servers, f"Server mismatch: {expected_servers} vs {actual_servers}"
        
        # Test task creation
        context = {'query': 'test analysis', 'scope': 'full'}
        tasks = dispatcher.create_parallel_tasks('/analyze_10x', context)
        
        assert len(tasks) > 0, "No tasks created"
        assert len(tasks) <= 5, f"Too many tasks created: {len(tasks)}"
        
        return {"tasks_created": len(tasks), "servers": list(actual_servers)}
    
    async def test_dispatcher_health_checks(self, dispatcher):
        """Test health check functionality"""
        
        await dispatcher.check_all_server_health()
        
        # Check that all servers have status
        for server_name, server_info in dispatcher.mcp_servers.items():
            assert server_info.status is not None, f"Server {server_name} has no status"
        
        stats = dispatcher.get_server_stats()
        assert stats['total_servers'] == 5, f"Expected 5 servers in stats, got {stats['total_servers']}"
        
        return stats
    
    async def test_command_specific_selection(self, dispatcher):
        """Test that different commands select appropriate servers"""
        
        commands = ['/analyze_10x', '/implement_10x', '/qa:comprehensive_10x']
        server_selections = {}
        
        for command in commands:
            servers = dispatcher.determine_optimal_servers(command, {})
            server_selections[command] = servers
            assert len(servers) > 0, f"No servers selected for {command}"
        
        # All commands should use all servers for comprehensive analysis
        for command, servers in server_selections.items():
            assert len(servers) == 5, f"{command} should use all 5 servers, got {len(servers)}"
        
        return server_selections
    
    async def test_parallel_execution(self, dispatcher):
        """Test parallel execution of tasks"""
        
        context = {'query': 'test parallel execution', 'mode': 'deep'}
        
        start_time = time.time()
        results = await dispatcher.dispatch_parallel('/analyze_10x', context)
        execution_time = time.time() - start_time
        
        assert len(results) > 0, "No results from parallel execution"
        
        # Check that execution was reasonably fast (parallel)
        assert execution_time < 5.0, f"Parallel execution took too long: {execution_time:.2f}s"
        
        successful_results = [r for r in results if r.success]
        assert len(successful_results) > 0, "No successful results"
        
        return {
            "total_results": len(results),
            "successful_results": len(successful_results),
            "execution_time": execution_time,
            "parallel_efficiency": len(successful_results) / max(1, len(results))
        }
    
    async def test_coordinator(self):
        """Test the CoordinationManager"""
        
        print("\n📋 Testing CoordinationManager...")
        
        try:
            coordinator = CoordinationManager(max_concurrent_tasks=3)
            
            # Test 1: Basic task coordination
            await self.run_test("Coordinator Basic Task Management",
                              self.test_coordinator_basic_tasks(coordinator))
            
            # Test 2: Dependency resolution
            await self.run_test("Coordinator Dependency Resolution",
                              self.test_coordinator_dependencies(coordinator))
            
            # Test 3: Resource management
            await self.run_test("Coordinator Resource Management",
                              self.test_coordinator_resources(coordinator))
        
        except Exception as e:
            logger.error(f"Coordinator tests failed: {e}")
            self.record_test_failure("Coordinator Tests", str(e))
    
    async def test_coordinator_basic_tasks(self, coordinator):
        """Test basic task coordination"""
        
        # Create simple tasks
        tasks = [
            CoordinationTask(
                task_id="test_1",
                server_name="ml-code-intelligence",
                operation="analyze",
                parameters={"test": True}
            ),
            CoordinationTask(
                task_id="test_2",
                server_name="context-aware-memory",
                operation="retrieve",
                parameters={"test": True}
            )
        ]
        
        start_time = time.time()
        results = await coordinator.coordinate_execution(tasks)
        execution_time = time.time() - start_time
        
        assert len(results) == 2, f"Expected 2 results, got {len(results)}"
        
        # Check coordination stats
        stats = coordinator.get_coordination_stats()
        assert stats['task_stats']['total_tasks'] == 2, "Task count mismatch"
        
        return {
            "tasks_executed": len(results),
            "execution_time": execution_time,
            "coordination_stats": stats
        }
    
    async def test_coordinator_dependencies(self, coordinator):
        """Test dependency resolution"""
        
        # Create tasks with dependencies
        task1 = CoordinationTask(
            task_id="dep_test_1",
            server_name="context-aware-memory",
            operation="retrieve",
            parameters={}
        )
        
        task2 = CoordinationTask(
            task_id="dep_test_2", 
            server_name="ml-code-intelligence",
            operation="analyze",
            parameters={},
            dependencies={"dep_test_1"}  # Depends on task1
        )
        
        tasks = [task1, task2]
        
        start_time = time.time()
        results = await coordinator.coordinate_execution(tasks)
        execution_time = time.time() - start_time
        
        # Check that dependent task ran after dependency
        task1_result = next(r for r in results if r.task_id == "dep_test_1")
        task2_result = next(r for r in results if r.task_id == "dep_test_2")
        
        if task1_result.completed_at and task2_result.started_at:
            assert task1_result.completed_at <= task2_result.started_at, \
                "Dependent task started before dependency completed"
        
        return {
            "dependency_respected": True,
            "execution_time": execution_time
        }
    
    async def test_coordinator_resources(self, coordinator):
        """Test resource management"""
        
        # Test resource availability
        available = coordinator.resource_manager.get_available_resources()
        assert len(available) > 0, "No available resources"
        
        # Test resource allocation
        from coordination_manager import ResourceRequirement, ResourceType
        
        requirements = [
            ResourceRequirement(ResourceType.CPU, 2.0),
            ResourceRequirement(ResourceType.MEMORY, 1024.0)
        ]
        
        can_allocate = coordinator.resource_manager.can_allocate(requirements)
        assert can_allocate, "Should be able to allocate basic resources"
        
        # Test actual allocation
        allocated = coordinator.resource_manager.allocate_resources("test_task", requirements)
        assert allocated, "Resource allocation failed"
        
        # Test deallocation
        coordinator.resource_manager.deallocate_resources("test_task")
        
        usage = coordinator.resource_manager.get_resource_usage()
        assert usage['active_allocations'] == 0, "Resources not properly deallocated"
        
        return {"resource_management": "working", "usage_stats": usage}
    
    async def test_aggregator(self):
        """Test the AggregationEngine"""
        
        print("\n🔄 Testing AggregationEngine...")
        
        try:
            aggregator = AggregationEngine()
            
            # Test 1: Basic aggregation
            await self.run_test("Aggregator Basic Functionality",
                              self.test_aggregator_basic(aggregator))
            
            # Test 2: Different strategies
            await self.run_test("Aggregation Strategies",
                              self.test_aggregation_strategies(aggregator))
            
            # Test 3: Conflict detection
            await self.run_test("Conflict Detection",
                              self.test_conflict_detection(aggregator))
            
            # Test 4: Quality assessment
            await self.run_test("Quality Assessment", 
                              self.test_quality_assessment(aggregator))
        
        except Exception as e:
            logger.error(f"Aggregator tests failed: {e}")
            self.record_test_failure("Aggregator Tests", str(e))
    
    async def test_aggregator_basic(self, aggregator):
        """Test basic aggregation functionality"""
        
        # Create test results and metadata
        results = [
            {"analysis": "good", "score": 0.8},
            {"context": "relevant", "score": 0.9},
            {"risk": "low", "score": 0.7}
        ]
        
        metadatas = [
            ResultMetadata("ml-code-intelligence", "analyze", time.time(), 1.0, 0.9),
            ResultMetadata("context-aware-memory", "retrieve", time.time(), 0.8, 0.95),
            ResultMetadata("predictive-analytics", "risk_analysis", time.time(), 1.2, 0.85)
        ]
        
        aggregated = aggregator.aggregate_results('/analyze_10x', results, metadatas)
        
        assert aggregated.command_type == '/analyze_10x'
        assert len(aggregated.source_results) == 3
        assert 0.0 <= aggregated.confidence_score <= 1.0
        assert aggregated.processing_time > 0
        
        return {
            "results_processed": len(results),
            "confidence_score": aggregated.confidence_score,
            "processing_time": aggregated.processing_time,
            "conflicts": len(aggregated.conflicts_detected)
        }
    
    async def test_aggregation_strategies(self, aggregator):
        """Test different aggregation strategies"""
        
        results = [
            {"value": 1, "text": "first"},
            {"value": 2, "text": "second"},
            {"value": 3, "text": "third"}
        ]
        
        metadatas = [
            ResultMetadata(f"server_{i}", "test", time.time(), 1.0, 0.9)
            for i in range(3)
        ]
        
        strategies = [
            AggregationStrategy.MERGE,
            AggregationStrategy.WEIGHTED,
            AggregationStrategy.CONSENSUS,
            AggregationStrategy.BEST_OF
        ]
        
        strategy_results = {}
        
        for strategy in strategies:
            aggregated = aggregator.aggregate_results(
                '/test', results, metadatas, strategy
            )
            strategy_results[strategy.value] = {
                "confidence": aggregated.confidence_score,
                "processing_time": aggregated.processing_time,
                "strategy": aggregated.aggregation_strategy.value
            }
        
        assert len(strategy_results) == 4, "Not all strategies tested"
        
        return strategy_results
    
    async def test_conflict_detection(self, aggregator):
        """Test conflict detection"""
        
        # Create conflicting results
        conflicting_results = [
            {"score": 0.8, "status": "good"},
            {"score": 0.3, "status": "bad"},  # Conflict!
            {"score": 0.9, "status": "excellent"}
        ]
        
        conflicts = aggregator.conflict_detector.detect_conflicts(conflicting_results)
        
        assert len(conflicts) > 0, "Should detect conflicts in conflicting data"
        
        # Test non-conflicting results
        non_conflicting_results = [
            {"score": 0.8, "status": "good"},
            {"score": 0.82, "status": "good"},
            {"score": 0.85, "status": "good"}
        ]
        
        no_conflicts = aggregator.conflict_detector.detect_conflicts(non_conflicting_results)
        
        # Should have fewer or no conflicts
        assert len(no_conflicts) <= len(conflicts), "Non-conflicting data should have fewer conflicts"
        
        return {
            "conflicts_detected": len(conflicts),
            "non_conflicting_conflicts": len(no_conflicts),
            "conflict_detection_working": len(conflicts) > len(no_conflicts)
        }
    
    async def test_quality_assessment(self, aggregator):
        """Test quality assessment"""
        
        # High quality result
        high_quality = {"complete": True, "detailed": "very detailed analysis", "score": 0.95}
        high_quality_meta = ResultMetadata("reliable-server", "analyze", time.time(), 1.0, 0.95)
        
        high_quality_score = aggregator.quality_assessor.assess_result_quality(
            high_quality, high_quality_meta
        )
        
        # Low quality result
        low_quality = {"incomplete": True, "score": None}
        low_quality_meta = ResultMetadata("unreliable-server", "analyze", time.time(), 5.0, 0.3)
        
        low_quality_score = aggregator.quality_assessor.assess_result_quality(
            low_quality, low_quality_meta
        )
        
        assert high_quality_score > low_quality_score, \
            f"High quality ({high_quality_score}) should score higher than low quality ({low_quality_score})"
        
        assert 0.0 <= high_quality_score <= 1.0, "Quality score should be between 0 and 1"
        assert 0.0 <= low_quality_score <= 1.0, "Quality score should be between 0 and 1"
        
        return {
            "high_quality_score": high_quality_score,
            "low_quality_score": low_quality_score,
            "quality_assessment_working": high_quality_score > low_quality_score
        }
    
    async def test_end_to_end_integration(self):
        """Test complete end-to-end integration"""
        
        print("\n🔗 Testing End-to-End Integration...")
        
        try:
            # Simulate a complete /analyze_10x command flow
            context = {
                'command_type': '/analyze_10x',
                'mode': 'deep',
                'scope': 'full',
                'query': 'comprehensive analysis test'
            }
            
            # Step 1: Dispatch parallel tasks
            async with ParallelDispatcher() as dispatcher:
                await dispatcher.initialize()
                task_results = await dispatcher.dispatch_parallel('/analyze_10x', context)
            
            # Step 2: Coordinate if needed (for complex scenarios)
            coordinator = CoordinationManager()
            
            # Step 3: Aggregate results
            aggregator = AggregationEngine()
            
            if task_results:
                # Convert to aggregation format
                results = [r.result for r in task_results if r.success and r.result]
                metadatas = [
                    ResultMetadata(
                        r.server_name, r.operation, r.timestamp, 
                        r.execution_time, 0.9 if r.success else 0.3
                    )
                    for r in task_results
                ]
                
                if results and metadatas:
                    aggregated = aggregator.aggregate_results('/analyze_10x', results, metadatas)
                    
                    await self.run_test("End-to-End Integration",
                                      self.validate_e2e_results(task_results, aggregated))
                else:
                    self.record_test_failure("End-to-End Integration", "No valid results to aggregate")
            else:
                self.record_test_failure("End-to-End Integration", "No task results from dispatcher")
        
        except Exception as e:
            logger.error(f"End-to-end integration test failed: {e}")
            self.record_test_failure("End-to-End Integration", str(e))
    
    async def validate_e2e_results(self, task_results, aggregated_result):
        """Validate end-to-end test results"""
        
        # Validate task results
        total_tasks = len(task_results)
        successful_tasks = len([r for r in task_results if r.success])
        
        assert total_tasks > 0, "No tasks executed"
        assert successful_tasks > 0, "No successful tasks"
        
        # Validate aggregated result
        assert aggregated_result.command_type == '/analyze_10x'
        assert 0.0 <= aggregated_result.confidence_score <= 1.0
        assert aggregated_result.processing_time > 0
        
        # Calculate performance metrics
        total_execution_time = sum(r.execution_time for r in task_results)
        max_execution_time = max(r.execution_time for r in task_results)
        parallel_efficiency = total_execution_time / (max_execution_time * total_tasks) if max_execution_time > 0 else 0
        
        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "success_rate": successful_tasks / total_tasks,
            "parallel_efficiency": parallel_efficiency,
            "total_execution_time": total_execution_time,
            "max_execution_time": max_execution_time,
            "aggregation_confidence": aggregated_result.confidence_score,
            "conflicts_detected": len(aggregated_result.conflicts_detected)
        }
    
    async def test_performance_benchmarks(self):
        """Test performance benchmarks"""
        
        print("\n⚡ Testing Performance Benchmarks...")
        
        try:
            # Benchmark 1: Multiple parallel executions
            await self.run_test("Multiple Parallel Executions",
                              self.benchmark_multiple_executions())
            
            # Benchmark 2: Large aggregation
            await self.run_test("Large Result Aggregation",
                              self.benchmark_large_aggregation())
        
        except Exception as e:
            logger.error(f"Performance benchmarks failed: {e}")
            self.record_test_failure("Performance Benchmarks", str(e))
    
    async def benchmark_multiple_executions(self):
        """Benchmark multiple parallel executions"""
        
        execution_times = []
        
        async with ParallelDispatcher() as dispatcher:
            await dispatcher.initialize()
            
            # Run 5 parallel executions
            for i in range(5):
                context = {'query': f'benchmark test {i}', 'mode': 'standard'}
                
                start_time = time.time()
                results = await dispatcher.dispatch_parallel('/analyze_10x', context)
                execution_time = time.time() - start_time
                
                execution_times.append(execution_time)
        
        avg_time = sum(execution_times) / len(execution_times)
        max_time = max(execution_times)
        min_time = min(execution_times)
        
        # Performance assertion: should complete in reasonable time
        assert avg_time < 10.0, f"Average execution time too high: {avg_time:.2f}s"
        
        return {
            "executions": len(execution_times),
            "avg_time": avg_time,
            "max_time": max_time,
            "min_time": min_time,
            "consistency": (max_time - min_time) / avg_time if avg_time > 0 else 0
        }
    
    async def benchmark_large_aggregation(self):
        """Benchmark large result aggregation"""
        
        # Create large dataset
        results = []
        metadatas = []
        
        for i in range(50):  # 50 results
            results.append({
                f"field_{j}": f"value_{i}_{j}" for j in range(20)  # 20 fields each
            })
            metadatas.append(
                ResultMetadata(f"server_{i%5}", f"operation_{i}", time.time(), 1.0, 0.9)
            )
        
        aggregator = AggregationEngine()
        
        start_time = time.time()
        aggregated = aggregator.aggregate_results('/test', results, metadatas)
        processing_time = time.time() - start_time
        
        # Performance assertion: should handle large datasets efficiently
        assert processing_time < 5.0, f"Large aggregation too slow: {processing_time:.2f}s"
        
        return {
            "results_processed": len(results),
            "fields_per_result": 20,
            "processing_time": processing_time,
            "throughput": len(results) / processing_time,
            "memory_efficient": True  # If we got here without memory errors
        }
    
    async def run_test(self, test_name: str, test_coro):
        """Run a single test and record results"""
        
        self.test_results['tests_run'] += 1
        
        try:
            print(f"  🔍 {test_name}...")
            result = await test_coro
            
            print(f"    ✅ PASSED")
            self.test_results['tests_passed'] += 1
            self.test_results['detailed_results'].append({
                'name': test_name,
                'status': 'PASSED',
                'result': result
            })
            
        except AssertionError as e:
            print(f"    ❌ FAILED: {str(e)}")
            self.record_test_failure(test_name, str(e))
        except Exception as e:
            print(f"    ❌ ERROR: {str(e)}")
            self.record_test_failure(test_name, f"Unexpected error: {str(e)}")
    
    def record_test_failure(self, test_name: str, error: str):
        """Record a test failure"""
        self.test_results['tests_failed'] += 1
        self.test_results['detailed_results'].append({
            'name': test_name,
            'status': 'FAILED',
            'error': error
        })
    
    def generate_final_report(self):
        """Generate final test report"""
        
        print("\n" + "=" * 60)
        print("🧪 PARALLEL MCP SYSTEM TEST RESULTS")
        print("=" * 60)
        
        total = self.test_results['tests_run']
        passed = self.test_results['tests_passed']
        failed = self.test_results['tests_failed']
        
        print(f"📊 Overall Results:")
        print(f"   Total Tests: {total}")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📈 Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results['detailed_results']:
                if result['status'] == 'FAILED':
                    print(f"   • {result['name']}: {result.get('error', 'Unknown error')}")
        
        print(f"\n🎯 System Status: {'✅ READY FOR PRODUCTION' if failed == 0 else '⚠️ NEEDS ATTENTION'}")
        
        # Save detailed report
        report_file = Path(__file__).parent / "test_results.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"📄 Detailed report saved to: {report_file}")

async def main():
    """Main test runner"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        print("🏃 Running quick tests...")
        # Quick test mode - run basic functionality only
        tester = ParallelSystemTester()
        async with ParallelDispatcher() as dispatcher:
            await tester.run_test("Quick Dispatcher Test",
                                tester.test_dispatcher_basic_functionality(dispatcher))
        tester.generate_final_report()
    else:
        # Full test suite
        tester = ParallelSystemTester()
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())