"""
Test suite for ML Testing QA MCP Server - Enhanced ML test generation capabilities
Tests TestGen-LLM, bug prediction, edge case discovery, and quality assessment
"""

import pytest
import asyncio
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from server import (
    TestGenLLMModel,
    BugPredictionModel,
    EdgeCaseDiscoveryEngine,
    BoundaryValueAnalyzer,
    EquivalencePartitioner,
    MutationTestGenerator,
    IntelligentTestGenerator,
    QualityPredictor,
    AdaptiveTestingStrategist,
    MLTestingQAServer
)

class TestTestGenLLMModel:
    """Test TestGen-LLM model for intelligent test generation"""
    
    @pytest.fixture
    def llm_model(self):
        return TestGenLLMModel()
    
    @pytest.fixture
    def sample_code_context(self):
        """Sample code context for test generation"""
        return {
            'function_name': 'calculate_fibonacci',
            'function_signature': 'def calculate_fibonacci(n: int) -> int:',
            'function_body': '''
def calculate_fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("Input must be non-negative")
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
''',
            'docstring': 'Calculate the nth Fibonacci number using recursion',
            'complexity_metrics': {
                'cyclomatic_complexity': 4,
                'lines_of_code': 6
            }
        }
    
    @pytest.mark.asyncio
    async def test_llm_initialization(self, llm_model):
        """Test LLM model initialization"""
        await llm_model.initialize()
        
        # Should initialize without errors (may use fallback)
        assert llm_model is not None
        assert hasattr(llm_model, 'is_initialized')
    
    @pytest.mark.asyncio
    async def test_prompt_generation(self, llm_model, sample_code_context):
        """Test generation of LLM prompts"""
        prompt = llm_model._create_generation_prompt(sample_code_context)
        
        assert 'calculate_fibonacci' in prompt
        assert 'Requirements:' in prompt
        assert 'Test normal cases' in prompt
        assert 'Test edge cases' in prompt
        assert len(prompt) > 100
    
    @pytest.mark.asyncio
    async def test_test_generation(self, llm_model, sample_code_context):
        """Test test case generation"""
        generated_tests = await llm_model.generate_tests(sample_code_context)
        
        assert isinstance(generated_tests, list)
        assert len(generated_tests) > 0
        
        # Check that generated tests contain basic structure
        for test in generated_tests:
            assert 'def test_' in test
            assert 'calculate_fibonacci' in test
    
    def test_hallucination_detection(self, llm_model, sample_code_context):
        """Test detection of hallucinated test code"""
        
        # Valid test
        valid_test = """
def test_calculate_fibonacci_basic():
    assert calculate_fibonacci(5) == 5
"""
        assert llm_model._is_valid_test(valid_test, sample_code_context)
        
        # Invalid test with hallucination
        invalid_test = """
def test_calculate_fibonacci_fake():
    import non_existent_module
    assert magic_function() == 42
"""
        assert not llm_model._is_valid_test(invalid_test, sample_code_context)
        
        # Test without proper structure
        malformed_test = "print('not a test')"
        assert not llm_model._is_valid_test(malformed_test, sample_code_context)
    
    @pytest.mark.asyncio
    async def test_template_fallback(self, llm_model, sample_code_context):
        """Test template-based fallback when LLM unavailable"""
        template_tests = await llm_model._generate_template_tests(sample_code_context)
        
        assert isinstance(template_tests, list)
        assert len(template_tests) >= 3
        
        for template in template_tests:
            assert 'def test_calculate_fibonacci' in template
            assert 'TODO:' in template or 'assert' in template

class TestBugPredictionModel:
    """Test ML bug prediction model"""
    
    @pytest.fixture
    def bug_predictor(self):
        return BugPredictionModel()
    
    @pytest.fixture
    def sample_code_metrics(self):
        """Sample code metrics for bug prediction"""
        return {
            'cyclomatic_complexity': 8,
            'lines_of_code': 150,
            'number_of_functions': 5,
            'depth_of_nesting': 3,
            'number_of_parameters': 4,
            'halstead_volume': 250.5,
            'maintainability_index': 65.0,
            'imports': ['os', 'sys', 'json'],
            'exceptions_caught': ['ValueError', 'TypeError'],
            'global_variables': ['CONFIG']
        }
    
    @pytest.mark.asyncio
    async def test_model_training(self, bug_predictor):
        """Test bug prediction model training"""
        # Should train with synthetic data
        await bug_predictor.train_model([])
        
        # Model should be in some state (trained or fallback)
        assert bug_predictor is not None
    
    @pytest.mark.asyncio
    async def test_bug_prediction(self, bug_predictor, sample_code_metrics):
        """Test bug probability prediction"""
        prediction = await bug_predictor.predict_bugs(sample_code_metrics)
        
        assert 'bug_probability' in prediction
        assert 'prediction' in prediction
        assert 'confidence' in prediction
        assert 'risk_level' in prediction
        assert 'recommendations' in prediction
        
        # Validate ranges
        assert 0 <= prediction['bug_probability'] <= 1
        assert 0 <= prediction['confidence'] <= 1
        assert prediction['risk_level'] in ['low', 'medium', 'high', 'critical']
        assert isinstance(prediction['recommendations'], list)
    
    def test_feature_extraction(self, bug_predictor, sample_code_metrics):
        """Test feature extraction for prediction"""
        features = bug_predictor._extract_prediction_features(sample_code_metrics)
        
        assert isinstance(features, list)
        assert len(features) == 10  # Expected number of features
        assert all(isinstance(f, (int, float)) for f in features)
    
    def test_synthetic_data_generation(self, bug_predictor):
        """Test synthetic training data generation"""
        synthetic_data = bug_predictor._create_synthetic_data()
        
        assert isinstance(synthetic_data, list)
        assert len(synthetic_data) == 100
        
        for item in synthetic_data:
            assert 'metrics' in item
            assert 'has_bugs' in item
            assert isinstance(item['has_bugs'], bool)
    
    def test_heuristic_fallback(self, bug_predictor, sample_code_metrics):
        """Test heuristic-based prediction fallback"""
        prediction = bug_predictor._heuristic_bug_prediction(sample_code_metrics)
        
        assert 'bug_probability' in prediction
        assert prediction['confidence'] == 0.7  # Heuristic confidence
        assert isinstance(prediction['contributing_factors'], dict)
    
    def test_recommendation_generation(self, bug_predictor, sample_code_metrics):
        """Test generation of actionable recommendations"""
        # High complexity scenario
        high_complexity_metrics = sample_code_metrics.copy()
        high_complexity_metrics['cyclomatic_complexity'] = 15
        high_complexity_metrics['lines_of_code'] = 300
        high_complexity_metrics['depth_of_nesting'] = 6
        
        recommendations = bug_predictor._generate_recommendations(high_complexity_metrics, 0.8)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Should recommend complexity reduction
        complexity_recommendations = [r for r in recommendations if 'complexity' in r.lower()]
        assert len(complexity_recommendations) > 0

class TestEdgeCaseDiscoveryEngine:
    """Test edge case discovery engine"""
    
    @pytest.fixture
    def edge_discoverer(self):
        return EdgeCaseDiscoveryEngine()
    
    @pytest.fixture
    def sample_code_analysis(self):
        """Sample code analysis for edge case discovery"""
        return {
            'function_name': 'validate_input',
            'function_body': '''
def validate_input(data, max_length=100):
    if data is None:
        raise ValueError("Data cannot be None")
    if len(data) > max_length:
        raise ValueError("Data too long")
    if len(data) == 0:
        return False
    return True
''',
            'parameters': ['data', 'max_length'],
            'complexity_metrics': {
                'cyclomatic_complexity': 4
            }
        }
    
    @pytest.mark.asyncio
    async def test_edge_case_discovery(self, edge_discoverer, sample_code_analysis):
        """Test comprehensive edge case discovery"""
        edge_cases = await edge_discoverer.discover_edge_cases(sample_code_analysis)
        
        assert isinstance(edge_cases, list)
        assert len(edge_cases) <= 20  # Should limit to top 20
        
        # Check edge case structure
        for case in edge_cases:
            assert 'case_type' in case
            assert 'description' in case
            assert 'importance_score' in case
            assert 0 <= case['importance_score'] <= 1
    
    @pytest.mark.asyncio
    async def test_edge_case_ranking(self, edge_discoverer, sample_code_analysis):
        """Test edge case ranking by importance"""
        sample_cases = [
            {'case_type': 'null_input', 'complexity_score': 0.3, 'coverage_potential': 0.8, 'bug_correlation': 0.9},
            {'case_type': 'boundary_max', 'complexity_score': 0.5, 'coverage_potential': 0.6, 'bug_correlation': 0.7},
            {'case_type': 'empty_input', 'complexity_score': 0.2, 'coverage_potential': 0.7, 'bug_correlation': 0.8}
        ]
        
        ranked_cases = await edge_discoverer._rank_edge_cases(sample_cases, sample_code_analysis)
        
        # Should be sorted by importance score
        for i in range(len(ranked_cases) - 1):
            assert ranked_cases[i]['importance_score'] >= ranked_cases[i + 1]['importance_score']
    
    def test_basic_edge_case_generation(self, edge_discoverer, sample_code_analysis):
        """Test basic edge case generation fallback"""
        basic_cases = edge_discoverer._generate_basic_edge_cases(sample_code_analysis)
        
        assert isinstance(basic_cases, list)
        assert len(basic_cases) >= 4
        
        case_types = [case['case_type'] for case in basic_cases]
        assert 'null_input' in case_types
        assert 'empty_input' in case_types
        assert 'boundary_max' in case_types
        assert 'boundary_min' in case_types

class TestBoundaryValueAnalyzer:
    """Test boundary value analysis"""
    
    @pytest.fixture
    def boundary_analyzer(self):
        return BoundaryValueAnalyzer()
    
    @pytest.fixture
    def sample_boundary_code(self):
        """Sample code with boundary conditions"""
        return {
            'function_name': 'process_data',
            'function_body': '''
def process_data(value, limit=50):
    if value < 0:
        raise ValueError("Negative values not allowed")
    if value >= limit:
        return "Too high"
    if len(str(value)) > 10:
        return "Too long"
    return value * 2
'''
        }
    
    @pytest.mark.asyncio
    async def test_boundary_analysis(self, boundary_analyzer, sample_boundary_code):
        """Test boundary value analysis"""
        boundary_cases = await boundary_analyzer.analyze(sample_boundary_code)
        
        assert isinstance(boundary_cases, list)
        
        # Should find boundary cases for numeric values
        numeric_cases = [case for case in boundary_cases if 'boundary' in case['case_type']]
        assert len(numeric_cases) > 0
    
    def test_numeric_value_extraction(self, boundary_analyzer, sample_boundary_code):
        """Test extraction of numeric values from code"""
        numeric_values = boundary_analyzer._extract_numeric_values(sample_boundary_code)
        
        assert isinstance(numeric_values, list)
        assert 50 in numeric_values  # From limit=50
        assert 10 in numeric_values  # From len check
    
    def test_boundary_test_generation(self, boundary_analyzer, sample_boundary_code):
        """Test generation of boundary test cases"""
        boundary_tests = boundary_analyzer._generate_boundary_tests(50, sample_boundary_code)
        
        assert len(boundary_tests) == 3  # below, exact, above
        
        test_values = [test['test_value'] for test in boundary_tests]
        assert 49 in test_values  # below
        assert 50 in test_values  # exact
        assert 51 in test_values  # above
    
    def test_string_constraint_extraction(self, boundary_analyzer, sample_boundary_code):
        """Test extraction of string length constraints"""
        constraints = boundary_analyzer._extract_string_constraints(sample_boundary_code)
        
        assert isinstance(constraints, list)
        # Should find len() > 10 constraint
        length_constraints = [c for c in constraints if c.get('type') == 'string_length']
        assert len(length_constraints) > 0

class TestEquivalencePartitioner:
    """Test equivalence partitioning"""
    
    @pytest.fixture
    def partitioner(self):
        return EquivalencePartitioner()
    
    @pytest.fixture
    def sample_partition_analysis(self):
        """Sample analysis for partitioning"""
        return {
            'function_name': 'classify_number',
            'function_body': '''
def classify_number(num):
    if isinstance(num, str):
        return "string"
    if num < 0:
        return "negative"
    if num == 0:
        return "zero"
    return "positive"
'''
        }
    
    @pytest.mark.asyncio
    async def test_partition_generation(self, partitioner, sample_partition_analysis):
        """Test equivalence partition generation"""
        partition_cases = await partitioner.generate(sample_partition_analysis)
        
        assert isinstance(partition_cases, list)
        assert len(partition_cases) > 0
        
        # Check partition diversity
        case_types = [case['case_type'] for case in partition_cases]
        assert any('numeric' in ct for ct in case_types)
        assert any('string' in ct for ct in case_types)
        assert any('boolean' in ct for ct in case_types)
    
    def test_input_domain_analysis(self, partitioner, sample_partition_analysis):
        """Test input domain analysis"""
        domains = partitioner._analyze_input_domains(sample_partition_analysis)
        
        assert isinstance(domains, list)
        assert len(domains) >= 4  # numeric, string, boolean, collection
        
        domain_types = [domain['type'] for domain in domains]
        assert 'numeric' in domain_types
        assert 'string' in domain_types
        assert 'boolean' in domain_types
        assert 'collection' in domain_types
    
    def test_partition_test_values(self, partitioner):
        """Test partition test value generation"""
        # Test numeric partitions
        assert partitioner._get_partition_test_value('numeric', 'negative') == '-1'
        assert partitioner._get_partition_test_value('numeric', 'zero') == '0'
        assert partitioner._get_partition_test_value('numeric', 'positive') == '1'
        
        # Test string partitions
        assert partitioner._get_partition_test_value('string', 'empty') == '""'
        assert partitioner._get_partition_test_value('string', 'single_char') == '"a"'
        
        # Test boolean partitions
        assert partitioner._get_partition_test_value('boolean', 'true') == 'True'
        assert partitioner._get_partition_test_value('boolean', 'false') == 'False'

class TestMutationTestGenerator:
    """Test mutation-based test generation"""
    
    @pytest.fixture
    def mutation_generator(self):
        return MutationTestGenerator()
    
    @pytest.fixture
    def sample_mutation_code(self):
        """Sample code for mutation testing"""
        return {
            'function_name': 'compare_values',
            'function_body': '''
def compare_values(a, b):
    if a > b:
        return "greater"
    elif a < b:
        return "less"
    elif a == b:
        return "equal"
    return "unknown"
'''
        }
    
    @pytest.mark.asyncio
    async def test_mutation_generation(self, mutation_generator, sample_mutation_code):
        """Test mutation-based test case generation"""
        mutation_cases = await mutation_generator.generate(sample_mutation_code)
        
        assert isinstance(mutation_cases, list)
        
        # Should generate mutation test cases
        if len(mutation_cases) > 0:
            for case in mutation_cases:
                assert 'mutation' in case['case_type']
                assert 'mutant_type' in case
                assert 'mutation' in case
    
    def test_mutant_generation(self, mutation_generator, sample_mutation_code):
        """Test generation of code mutants"""
        mutants = mutation_generator._generate_mutants(sample_mutation_code)
        
        assert isinstance(mutants, list)
        assert len(mutants) <= 10  # Should limit mutants
        
        # Should find mutations for comparison operators
        mutation_types = [mutant['type'] for mutant in mutants]
        assert any('arithmetic_operator' in mt for mt in mutation_types)
    
    def test_mutant_killing_test_generation(self, mutation_generator, sample_mutation_code):
        """Test generation of mutant-killing tests"""
        sample_mutant = {
            'type': 'arithmetic_operator',
            'original': '>',
            'mutated': '<=',
            'kill_difficulty': 0.6
        }
        
        killing_test = mutation_generator._generate_mutant_killing_test(sample_mutant, sample_mutation_code)
        
        if killing_test:
            assert 'mutation' in killing_test['case_type']
            assert 'compare_values' in killing_test['test_code']
            assert killing_test['mutant_type'] == 'arithmetic_operator'
    
    def test_mutant_exposing_inputs(self, mutation_generator):
        """Test generation of inputs that expose mutations"""
        # Test arithmetic operator exposure
        exposing_input = mutation_generator._get_mutant_exposing_input('arithmetic_operator', '+', '-')
        assert exposing_input == '1, 1'
        
        # Test boundary condition exposure
        exposing_input = mutation_generator._get_mutant_exposing_input('boundary_condition', '<=', '<')
        assert exposing_input == '5, 5'
        
        # Test unknown mutation
        exposing_input = mutation_generator._get_mutant_exposing_input('unknown', 'x', 'y')
        assert exposing_input is None

@pytest.mark.integration
class TestMLTestingQAIntegration:
    """Integration tests for complete ML Testing QA workflow"""
    
    @pytest.fixture
    def qa_server(self):
        return MLTestingQAServer()
    
    @pytest.fixture
    def sample_test_request(self):
        """Sample test generation request"""
        return {
            'code': '''
def factorial(n):
    if n < 0:
        raise ValueError("Negative numbers not allowed")
    if n <= 1:
        return 1
    return n * factorial(n-1)
''',
            'test_types': ['unit', 'edge_cases', 'property_based'],
            'coverage_target': 0.9,
            'quality_threshold': 0.8
        }
    
    @pytest.mark.asyncio
    async def test_comprehensive_test_generation(self, qa_server, sample_test_request):
        """Test complete test generation workflow"""
        result = await qa_server.handle_test_generation(sample_test_request)
        
        assert 'generated_tests' in result
        assert 'quality_metrics' in result
        assert 'coverage_analysis' in result
        assert 'success' in result
        
        if result['success']:
            assert len(result['generated_tests']) > 0
            assert 'bug_prediction' in result['quality_metrics']
    
    @pytest.mark.asyncio
    async def test_quality_prediction_workflow(self, qa_server):
        """Test code quality prediction workflow"""
        quality_request = {
            'code': '''
def complex_function(a, b, c, d, e):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return a + b + c + d + e
                    else:
                        return a + b + c + d
                else:
                    return a + b + c
            else:
                return a + b
        else:
            return a
    return 0
''',
            'metrics_to_analyze': ['complexity', 'maintainability', 'bug_probability']
        }
        
        result = await qa_server.handle_quality_prediction(quality_request)
        
        assert 'quality_analysis' in result
        assert 'bug_prediction' in result
        assert 'recommendations' in result
        assert 'success' in result
    
    @pytest.mark.asyncio
    async def test_strategy_optimization(self, qa_server):
        """Test testing strategy optimization"""
        strategy_request = {
            'project_context': {
                'code_complexity': 'high',
                'team_size': 5,
                'timeline': 'tight',
                'quality_requirements': 'high'
            },
            'current_coverage': 0.6,
            'target_coverage': 0.9
        }
        
        result = await qa_server.handle_strategy_optimization(strategy_request)
        
        assert 'optimized_strategy' in result
        assert 'test_prioritization' in result
        assert 'resource_allocation' in result
        assert 'success' in result
    
    def test_performance_metrics(self, qa_server):
        """Test server performance metrics"""
        metrics = qa_server.get_performance_metrics()
        
        assert 'test_generation_count' in metrics
        assert 'average_generation_time' in metrics
        assert 'model_performance' in metrics
        assert 'uptime' in metrics

if __name__ == "__main__":
    pytest.main([__file__, "-v"])