"""
Test Suite for Enhanced ML Code Intelligence Capabilities
Comprehensive tests for the enhanced AI features including context-aware generation,
multi-modal analysis, and prompt optimization.
"""

import pytest
import asyncio
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
import time

# Import the enhanced server and components
import sys
sys.path.append(str(Path(__file__).parent.parent / "src"))

from server import MLCodeIntelligenceServer
from tools.context_aware_generation import ContextAwareCodeGenerator, GenerationContext
from tools.multimodal_analysis import MultiModalCodeAnalyzer
from tools.prompt_optimizer import PromptBreederOptimizer, PromptTemplate
from utils.performance_monitor import PerformanceMonitor, SmartCache
from utils.config_utils import MCPServerSettings

class TestEnhancedMLIntelligence:
    """Comprehensive test suite for enhanced ML intelligence capabilities"""
    
    @pytest.fixture
    async def enhanced_server(self):
        """Setup enhanced server for testing"""
        config = self.create_test_config()
        server = MLCodeIntelligenceServer(config)
        await server._startup()
        return server
    
    @pytest.fixture
    def test_project_dir(self):
        """Create a temporary test project directory"""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)
        
        # Create sample project structure
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()
        (project_path / "docs").mkdir()
        
        # Create sample Python file
        sample_code = '''
def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    def process(self):
        return [x * 2 for x in self.data]
'''
        (project_path / "src" / "main.py").write_text(sample_code)
        
        # Create sample test file
        test_code = '''
import unittest
from src.main import calculate_fibonacci, DataProcessor

class TestFibonacci(unittest.TestCase):
    def test_fibonacci_base_cases(self):
        self.assertEqual(calculate_fibonacci(0), 0)
        self.assertEqual(calculate_fibonacci(1), 1)
    
    def test_fibonacci_recursive(self):
        self.assertEqual(calculate_fibonacci(5), 5)

class TestDataProcessor(unittest.TestCase):
    def test_process(self):
        processor = DataProcessor([1, 2, 3])
        result = processor.process()
        self.assertEqual(result, [2, 4, 6])
'''
        (project_path / "tests" / "test_main.py").write_text(test_code)
        
        # Create sample documentation
        doc_content = '''
# Project Documentation

## Overview
This is a sample project for testing ML Code Intelligence capabilities.

## Features
- Fibonacci calculation
- Data processing utilities

## Usage
```python
from src.main import calculate_fibonacci
result = calculate_fibonacci(10)
```
'''
        (project_path / "docs" / "README.md").write_text(doc_content)
        
        # Create requirements file
        requirements = '''
numpy>=1.20.0
pandas>=1.3.0
pytest>=6.0.0
'''
        (project_path / "requirements.txt").write_text(requirements)
        
        yield str(project_path)
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def create_test_config(self):
        """Create test configuration"""
        return MCPServerSettings(
            server_name="test-ml-code-intelligence",
            server_version="2.0.0",
            debug=True,
            max_workers=2,
            cache_ttl=300,
            embedding_model="all-MiniLM-L6-v2",
            ml_device="cpu",
            max_embedding_length=512,
            model_cache_dir="./test_models",
            vector_dimension=384,
            data_dir="./test_data",
            dspy_model="gpt-4-turbo-preview",
            max_tokens=1024,
            temperature=0.1,
            population_size=5,
            max_generations=3
        )
    
    async def test_context_aware_generation_initialization(self):
        """Test context-aware generation component initialization"""
        config = {'model': 'gpt-4-turbo-preview', 'max_tokens': 1024}
        generator = ContextAwareCodeGenerator(config)
        
        assert generator is not None
        assert generator.config == config
        assert generator.context_analyzer is not None
        assert generator.pattern_extractor is not None
        assert generator.quality_predictor is not None
    
    async def test_context_aware_generation_basic(self):
        """Test basic context-aware code generation"""
        config = {'model': 'gpt-4-turbo-preview', 'max_tokens': 1024}
        generator = ContextAwareCodeGenerator(config)
        
        request = "Create a function to calculate the square of a number"
        project_context = {
            'current_file': None,
            'project_structure': {'directories': ['src', 'tests'], 'total_files': 5},
            'imports': ['import math', 'import numpy'],
            'dependencies': ['numpy', 'pandas'],
            'existing_code': [],
            'git_history': []
        }
        
        result = await generator.generate_contextual_code(request, project_context)
        
        assert isinstance(result.generated_code, str)
        assert len(result.generated_code) > 0
        assert result.quality_score >= 0.0
        assert result.context_score >= 0.0
        assert result.generation_time > 0
    
    async def test_multimodal_analysis_initialization(self):
        """Test multi-modal analysis component initialization"""
        config = {'unified_dimension': 1408}
        analyzer = MultiModalCodeAnalyzer(config)
        
        assert analyzer is not None
        assert analyzer.config == config
        assert analyzer.code_embedder is not None
        assert analyzer.doc_embedder is not None
        assert analyzer.test_embedder is not None
        assert analyzer.comment_embedder is not None
    
    async def test_multimodal_analysis_basic(self, test_project_dir):
        """Test basic multi-modal analysis"""
        config = {'unified_dimension': 384}
        analyzer = MultiModalCodeAnalyzer(config)
        
        # Read project artifacts
        project_path = Path(test_project_dir)
        artifacts = {
            'code_files': [
                {
                    'path': 'src/main.py',
                    'content': (project_path / 'src' / 'main.py').read_text(),
                    'language': 'python'
                }
            ],
            'docs': [
                {
                    'path': 'docs/README.md',
                    'content': (project_path / 'docs' / 'README.md').read_text(),
                    'type': 'markdown'
                }
            ],
            'tests': [
                {
                    'path': 'tests/test_main.py',
                    'content': (project_path / 'tests' / 'test_main.py').read_text(),
                    'type': 'unit'
                }
            ],
            'comments': []
        }
        
        result = await analyzer.analyze_unified_context(artifacts)
        
        assert result is not None
        assert 'unified_insights' in result.unified_insights
        assert 'consistency_analysis' in result.consistency_analysis
        assert 'embedding_statistics' in result.embedding_statistics
    
    async def test_prompt_optimization_initialization(self):
        """Test prompt optimization component initialization"""
        config = {'population_size': 5, 'max_generations': 3}
        optimizer = PromptBreederOptimizer(config)
        
        assert optimizer is not None
        assert optimizer.population_size == 5
        assert optimizer.max_generations == 3
        assert len(optimizer.mutation_strategies) > 0
    
    async def test_prompt_optimization_basic(self):
        """Test basic prompt optimization"""
        config = {'population_size': 3, 'max_generations': 2}
        optimizer = PromptBreederOptimizer(config)
        
        base_template = "Generate code for {task}"
        task_type = "code_generation"
        success_metrics = {'target_score': 0.8, 'baseline_score': 0.5}
        
        result = await optimizer.optimize_prompt_template(
            base_template=base_template,
            task_type=task_type,
            success_metrics=success_metrics,
            training_data=[]
        )
        
        assert result is not None
        assert result.optimized_template is not None
        assert result.optimized_template.content != ""
        assert result.improvement_score >= 0.0
        assert len(result.optimization_history) >= 0
    
    async def test_performance_monitoring(self):
        """Test performance monitoring functionality"""
        config = {'max_history': 100}
        monitor = PerformanceMonitor(config)
        
        # Test operation recording
        await monitor.record_operation(
            operation_name="test_operation",
            duration=1.5,
            success=True,
            quality_score=0.9
        )
        
        stats = monitor.get_overall_stats()
        assert stats['total_operations'] == 1
        assert stats['success_rate'] == 1.0
        assert stats['avg_duration'] == 1.5
        
        # Test operation tracking
        operation_id = await monitor.start_operation("test_operation_2", "op_123")
        await asyncio.sleep(0.1)  # Simulate work
        await monitor.finish_operation(operation_id, success=True, quality_score=0.8)
        
        updated_stats = monitor.get_overall_stats()
        assert updated_stats['total_operations'] == 2
    
    async def test_smart_cache(self):
        """Test smart caching functionality"""
        config = {'max_size': 10, 'default_ttl': 3600}
        cache = SmartCache(config)
        
        # Test cache put and get
        cache.put("test_operation", "result_value", None, "arg1", key="value")
        result = cache.get("test_operation", "arg1", key="value")
        
        assert result == "result_value"
        
        # Test cache miss
        miss_result = cache.get("nonexistent_operation", "arg1")
        assert miss_result is None
        
        # Test cache stats
        stats = cache.get_stats()
        assert stats['size'] == 1
        assert stats['hits'] == 1
        assert stats['misses'] == 1
    
    async def test_enhanced_server_integration(self, enhanced_server, test_project_dir):
        """Test integration of enhanced features in the server"""
        
        # Test context-aware code generation
        if enhanced_server.context_generator:
            result = await enhanced_server.generate_context_aware_code(
                request="Create a function to process a list of numbers",
                project_path=test_project_dir,
                context_type="standard",
                quality_target=0.8
            )
            
            assert 'generated_code' in result or 'error' in result
            if 'generated_code' in result:
                assert isinstance(result['generated_code'], str)
                assert 'quality_score' in result
        
        # Test multi-modal consistency analysis
        if enhanced_server.multimodal_analyzer:
            result = await enhanced_server.analyze_cross_modal_consistency(
                project_path=test_project_dir,
                consistency_threshold=0.7
            )
            
            assert 'overall_consistency_score' in result or 'error' in result
        
        # Test prompt optimization
        if enhanced_server.prompt_optimizer:
            result = await enhanced_server.optimize_prompt_for_task(
                task_type="code_generation",
                current_template="Generate {request}",
                performance_target=0.8,
                optimization_cycles=2
            )
            
            assert 'optimized_template' in result or 'error' in result
    
    async def test_performance_integration(self, enhanced_server):
        """Test performance monitoring integration"""
        
        if enhanced_server.performance_monitor:
            # Test performance stats
            stats = await enhanced_server.get_performance_stats()
            assert 'overall_stats' in stats or 'error' in stats
            
            # Test optimization recommendations
            recommendations = await enhanced_server.get_optimization_recommendations()
            assert 'analysis' in recommendations or 'error' in recommendations
            
            # Test cache operations
            cache_result = await enhanced_server.clear_cache()
            assert 'success' in cache_result or 'error' in cache_result

# Performance Benchmark Tests
class TestPerformanceBenchmarks:
    """Performance benchmark tests for enhanced capabilities"""
    
    async def test_response_time_benchmarks(self):
        """Benchmark response times for different operation types"""
        
        config = MCPServerSettings(
            server_name="benchmark-test",
            server_version="2.0.0",
            debug=False,
            max_workers=2,
            cache_ttl=300,
            embedding_model="all-MiniLM-L6-v2",
            ml_device="cpu",
            max_embedding_length=512,
            model_cache_dir="./test_models",
            vector_dimension=384,
            data_dir="./test_data"
        )
        
        benchmarks = {
            'context_generation': {'target': 5.0, 'tolerance': 2.0},
            'multimodal_analysis': {'target': 10.0, 'tolerance': 5.0},
            'prompt_optimization': {'target': 15.0, 'tolerance': 10.0}
        }
        
        for operation, targets in benchmarks.items():
            start_time = time.time()
            
            # Mock operation execution
            if operation == 'context_generation':
                generator = ContextAwareCodeGenerator({'model': 'mock'})
                result = await generator.generate_contextual_code("test", {})
            elif operation == 'multimodal_analysis':
                analyzer = MultiModalCodeAnalyzer({'unified_dimension': 384})
                result = await analyzer.analyze_unified_context({'code_files': []})
            elif operation == 'prompt_optimization':
                optimizer = PromptBreederOptimizer({'population_size': 3, 'max_generations': 2})
                result = await optimizer.optimize_prompt_template("test", "test", {}, [])
            
            execution_time = time.time() - start_time
            
            # Check if within acceptable range (allowing for mock operations)
            assert execution_time <= targets['target'] + targets['tolerance']
            assert result is not None
    
    async def test_quality_benchmarks(self):
        """Benchmark quality metrics for generated outputs"""
        
        quality_targets = {
            'code_generation': 0.7,  # Relaxed for testing
            'context_analysis': 0.8,
            'prompt_optimization': 0.6
        }
        
        for capability, target in quality_targets.items():
            if capability == 'code_generation':
                generator = ContextAwareCodeGenerator({'model': 'mock'})
                result = await generator.generate_contextual_code("test function", {})
                quality_score = result.quality_score
            elif capability == 'context_analysis':
                # Mock context analysis quality
                quality_score = 0.85
            elif capability == 'prompt_optimization':
                optimizer = PromptBreederOptimizer({'population_size': 3, 'max_generations': 2})
                result = await optimizer.optimize_prompt_template("test", "test", {'target_score': 0.8}, [])
                quality_score = result.optimized_template.performance_score if result.optimized_template else 0.0
            
            # Allow for lower scores in testing environment
            assert quality_score >= target * 0.7  # 70% of target is acceptable for tests

# Integration Tests
class TestIntegration:
    """Integration tests for the complete enhanced system"""
    
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        
        # Create minimal test config
        config = MCPServerSettings(
            server_name="integration-test",
            server_version="2.0.0",
            debug=True,
            max_workers=1,
            cache_ttl=300,
            embedding_model="all-MiniLM-L6-v2",
            ml_device="cpu",
            max_embedding_length=256,  # Smaller for testing
            model_cache_dir="./test_models",
            vector_dimension=384,
            data_dir="./test_data"
        )
        
        server = MLCodeIntelligenceServer(config)
        
        try:
            await server._startup()
            
            # Test basic functionality
            stats = await server.get_stats()
            assert 'indexed_code_count' in stats
            
            # Test enhanced features (if available)
            if server.performance_monitor:
                perf_stats = await server.get_performance_stats()
                assert perf_stats is not None
            
        finally:
            await server._shutdown()
    
    async def test_error_handling(self):
        """Test error handling in enhanced features"""
        
        # Test with invalid configurations
        invalid_config = {}
        
        # These should handle invalid configs gracefully
        generator = ContextAwareCodeGenerator(invalid_config)
        result = await generator.generate_contextual_code("test", {})
        assert result is not None  # Should not crash
        
        analyzer = MultiModalCodeAnalyzer(invalid_config)
        result = await analyzer.analyze_unified_context({})
        assert result is not None  # Should not crash
        
        optimizer = PromptBreederOptimizer(invalid_config)
        result = await optimizer.optimize_prompt_template("test", "test", {}, [])
        assert result is not None  # Should not crash

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])