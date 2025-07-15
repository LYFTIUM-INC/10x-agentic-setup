#!/usr/bin/env python3
"""
Comprehensive tests for ML Testing QA MCP Server
Testing intelligent test generation, quality prediction, and adaptive strategies
"""

import asyncio
import json
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from server import (
    MLTestingQAServer,
    IntelligentTestGenerator,
    QualityPredictor,
    AdaptiveTestingStrategist,
    CodeFeatureExtractor
)


class TestCodeFeatureExtractor:
    """Test code feature extraction functionality"""
    
    def setup_method(self):
        self.extractor = CodeFeatureExtractor()
    
    def test_extract_basic_features(self):
        """Test basic feature extraction"""
        code = '''
def simple_function(x, y):
    """Simple function for testing"""
    if x > 0:
        return x + y
    return 0
'''
        features = self.extractor.extract_features(code)
        
        assert features['function_count'] == 1
        assert features['lines_of_code'] > 0
        assert features['cyclomatic_complexity'] >= 2  # Base + if statement
        assert features['comment_ratio'] > 0  # Has docstring
    
    def test_extract_complex_features(self):
        """Test feature extraction for complex code"""
        code = '''
class TestClass:
    def __init__(self):
        self.value = 0
    
    def complex_method(self, data):
        try:
            for item in data:
                if item > 0:
                    if item % 2 == 0:
                        self.value += item
                    else:
                        self.value -= item
                elif item < 0:
                    self.value = 0
        except Exception as e:
            print(f"Error: {e}")
            return None
        return self.value
'''
        features = self.extractor.extract_features(code)
        
        assert features['class_count'] == 1
        assert features['function_count'] == 2  # __init__ and complex_method
        assert features['cyclomatic_complexity'] > 5  # Multiple conditions
        assert features['nested_depth'] > 2  # Nested if statements
        assert features['exception_handling'] == 1  # Try-except block
    
    def test_syntax_error_handling(self):
        """Test handling of syntax errors"""
        code = '''
def invalid_function(
    # Missing closing parenthesis
    return "This will cause syntax error"
'''
        features = self.extractor.extract_features(code)
        
        assert 'syntax_errors' in features
        assert features['syntax_errors'] == 1
        assert features['function_count'] == 0


class TestIntelligentTestGenerator:
    """Test intelligent test generation functionality"""
    
    def setup_method(self):
        self.generator = IntelligentTestGenerator()
    
    @pytest.mark.asyncio
    async def test_generate_tests_simple_function(self):
        """Test test generation for simple function"""
        code = '''
def add_numbers(a, b):
    """Add two numbers"""
    return a + b
'''
        result = await self.generator.generate_tests(code)
        
        assert 'unit_tests' in result
        assert 'edge_case_tests' in result
        assert 'coverage_estimate' in result
        assert 'test_quality_score' in result
        assert len(result['unit_tests']) > 0
        assert result['coverage_estimate'] > 0
    
    @pytest.mark.asyncio
    async def test_generate_tests_complex_function(self):
        """Test test generation for complex function"""
        code = '''
def process_data(data_list):
    """Process a list of data with validation"""
    if not data_list:
        raise ValueError("Empty data list")
    
    result = []
    for item in data_list:
        if isinstance(item, (int, float)):
            if item > 0:
                result.append(item * 2)
            else:
                result.append(0)
        else:
            raise TypeError(f"Invalid type: {type(item)}")
    
    return result
'''
        result = await self.generator.generate_tests(code)
        
        assert len(result['unit_tests']) > 0
        assert len(result['edge_case_tests']) > 0
        assert result['coverage_estimate'] > 50  # Should be reasonable coverage
        assert result['test_quality_score'] > 0
        
        # Check that generated tests include edge cases
        edge_tests = result['edge_case_tests']
        assert any('edge_case' in test.lower() for test in edge_tests)
    
    @pytest.mark.asyncio
    async def test_generate_tests_with_context(self):
        """Test test generation with additional context"""
        code = '''
def calculate_discount(price, discount_rate):
    """Calculate discount amount"""
    return price * discount_rate
'''
        context = {
            'test_framework': 'pytest',
            'coverage_target': 98,
            'include_performance_tests': True,
            'include_security_tests': True
        }
        
        result = await self.generator.generate_tests(code, context)
        
        assert 'performance_tests' in result
        assert 'security_tests' in result
        assert result['coverage_estimate'] > 80
    
    @pytest.mark.asyncio
    async def test_error_handling_in_generation(self):
        """Test error handling during test generation"""
        invalid_code = "This is not valid Python code {"
        
        result = await self.generator.generate_tests(invalid_code)
        
        assert 'error' in result or len(result['unit_tests']) == 0
        assert 'coverage_estimate' in result
    
    def test_extract_functions(self):
        """Test function extraction from code"""
        code = '''
def func1(x):
    return x * 2

class TestClass:
    def method1(self, y):
        return y + 1
    
    @staticmethod
    def static_method(z):
        return z - 1
'''
        functions = self.generator._extract_functions(code)
        
        assert len(functions) == 3
        function_names = [f['name'] for f in functions]
        assert 'func1' in function_names
        assert 'method1' in function_names
        assert 'static_method' in function_names
    
    def test_coverage_estimation(self):
        """Test test coverage estimation"""
        functions = [
            {'name': 'func1', 'complexity': 1},
            {'name': 'func2', 'complexity': 5},
            {'name': 'func3', 'complexity': 3}
        ]
        
        tests = {
            'unit_tests': ['test1', 'test2', 'test3'],
            'edge_case_tests': ['edge1', 'edge2'],
            'integration_tests': ['int1'],
            'performance_tests': [],
            'security_tests': []
        }
        
        coverage = self.generator._estimate_coverage(functions, tests)
        
        assert isinstance(coverage, float)
        assert 0 <= coverage <= 100
    
    def test_test_quality_score(self):
        """Test test quality scoring"""
        tests = {
            'unit_tests': ['test1', 'test2'],
            'edge_case_tests': ['edge1'],
            'integration_tests': ['int1'],
            'performance_tests': ['perf1'],
            'security_tests': ['sec1']
        }
        
        score = self.generator._calculate_test_quality_score(tests)
        
        assert isinstance(score, float)
        assert 0 <= score <= 100
        assert score == 100  # All test types present


class TestQualityPredictor:
    """Test quality prediction functionality"""
    
    def setup_method(self):
        self.predictor = QualityPredictor()
    
    @pytest.mark.asyncio
    async def test_predict_quality_simple_code(self):
        """Test quality prediction for simple code"""
        code = '''
def clean_function(x):
    """Well-documented function"""
    if x is None:
        raise ValueError("Input cannot be None")
    return x * 2
'''
        result = await self.predictor.predict_quality(code)
        
        assert 'overall_quality_score' in result
        assert 'maintainability_score' in result
        assert 'complexity_score' in result
        assert 'documentation_score' in result
        assert 'security_score' in result
        assert 'bug_prediction' in result
        assert 'recommendations' in result
        assert 'confidence_scores' in result
        
        # Good code should have decent scores
        assert result['overall_quality_score'] > 50
        assert result['documentation_score'] > 30  # Has docstring
    
    @pytest.mark.asyncio
    async def test_predict_quality_complex_code(self):
        """Test quality prediction for complex code"""
        code = '''
def complex_function(data):
    result = []
    for item in data:
        if item > 0:
            if item % 2 == 0:
                if item > 100:
                    result.append(item * 3)
                else:
                    result.append(item * 2)
            else:
                result.append(item)
        else:
            result.append(0)
    return result
'''
        result = await self.predictor.predict_quality(code)
        
        # Complex code should have lower complexity score
        assert result['complexity_score'] < 80
        assert result['overall_quality_score'] < 90
        assert len(result['recommendations']) > 0
    
    @pytest.mark.asyncio
    async def test_predict_quality_risky_code(self):
        """Test quality prediction for risky code"""
        code = '''
import os
import subprocess

def risky_function(user_input):
    # Security risks
    os.system(user_input)
    result = eval(user_input)
    subprocess.call(user_input, shell=True)
    return result
'''
        result = await self.predictor.predict_quality(code)
        
        # Risky code should have low security score
        assert result['security_score'] < 50
        assert result['bug_prediction']['risk_level'] in ['medium', 'high']
        assert any('security' in rec.lower() for rec in result['recommendations'])
    
    @pytest.mark.asyncio
    async def test_predict_quality_with_context(self):
        """Test quality prediction with context"""
        code = '''
def api_function(request):
    return {"status": "ok"}
'''
        context = {
            'project_type': 'web_app',
            'team_size': 10,
            'criticality': 'high'
        }
        
        result = await self.predictor.predict_quality(code, context)
        
        assert 'overall_quality_score' in result
        assert 'recommendations' in result
    
    def test_calculate_maintainability_score(self):
        """Test maintainability score calculation"""
        features = {
            'maintainability_index': 75.5,
            'comment_ratio': 0.2,
            'cyclomatic_complexity': 5
        }
        
        score = self.predictor._calculate_maintainability_score(features)
        
        assert score == 75.5
    
    def test_calculate_security_score(self):
        """Test security score calculation"""
        risky_code = '''
import os
def dangerous():
    os.system("rm -rf /")
    eval("malicious_code")
'''
        features = {'exception_handling': 0}
        
        score = self.predictor._calculate_security_score(risky_code, features)
        
        assert score < 50  # Should be low due to risky patterns
    
    def test_bug_prediction(self):
        """Test bug probability prediction"""
        high_risk_features = {
            'cyclomatic_complexity': 15,
            'nested_depth': 6,
            'lines_of_code': 200,
            'comment_ratio': 0.05,
            'exception_handling': 0,
            'global_variables': 5
        }
        
        prediction = self.predictor._predict_bug_probability(high_risk_features)
        
        assert 'probability' in prediction
        assert 'risk_level' in prediction
        assert 'risk_factors' in prediction
        assert 'confidence' in prediction
        assert prediction['probability'] > 0.5  # High risk should have high probability
        assert prediction['risk_level'] == 'high'
    
    def test_technical_debt_calculation(self):
        """Test technical debt calculation"""
        features = {
            'technical_debt_ratio': 0.3,
            'cyclomatic_complexity': 20,
            'comment_ratio': 0.05
        }
        
        debt = self.predictor._calculate_technical_debt(features)
        
        assert 'total_debt_score' in debt
        assert 'complexity_debt' in debt
        assert 'documentation_debt' in debt
        assert 'estimated_hours_to_fix' in debt
        assert debt['total_debt_score'] > 0


class TestAdaptiveTestingStrategist:
    """Test adaptive testing strategy optimization"""
    
    def setup_method(self):
        self.strategist = AdaptiveTestingStrategist()
    
    @pytest.mark.asyncio
    async def test_optimize_strategy_web_app(self):
        """Test strategy optimization for web application"""
        context = {
            'code': '''
from flask import Flask
app = Flask(__name__)

@app.route('/api/users')
def get_users():
    return {"users": []}
''',
            'features': {
                'cyclomatic_complexity': 5,
                'lines_of_code': 50
            }
        }
        
        result = await self.strategist.optimize_strategy(context)
        
        assert 'recommended_strategy' in result
        assert 'project_analysis' in result
        assert 'test_distribution' in result
        assert 'priority_areas' in result
        assert 'optimization_tips' in result
        assert 'estimated_effort_reduction' in result
        
        # Web app should likely use user_journey or integration_focused strategy
        strategy = result['recommended_strategy']
        assert strategy['distribution']['e2e'] > 0.1  # Should have some E2E tests
    
    @pytest.mark.asyncio
    async def test_optimize_strategy_api(self):
        """Test strategy optimization for API"""
        context = {
            'code': '''
def get_user(user_id):
    return {"id": user_id, "name": "User"}

def create_user(user_data):
    return {"id": 123, "name": user_data["name"]}
''',
            'features': {
                'cyclomatic_complexity': 3,
                'function_count': 2,
                'class_count': 0
            }
        }
        
        result = await self.strategist.optimize_strategy(context)
        
        # API should likely use unit_heavy strategy
        strategy = result['recommended_strategy']
        assert strategy['distribution']['unit'] >= 0.5  # Should focus on unit tests
    
    @pytest.mark.asyncio
    async def test_optimize_strategy_high_risk(self):
        """Test strategy optimization for high-risk code"""
        context = {
            'code': '''
def process_payment(amount, card_number, auth_token):
    # Security-sensitive financial processing
    if not validate_auth(auth_token):
        raise AuthError("Invalid token")
    
    # Complex processing logic
    for i in range(10):
        if complex_condition(i):
            if another_condition():
                process_transaction(amount, card_number)
''',
            'features': {
                'cyclomatic_complexity': 12,
                'lines_of_code': 100,
                'comment_ratio': 0.05
            }
        }
        
        result = await self.strategist.optimize_strategy(context)
        
        # High-risk should use risk_based strategy
        analysis = result['project_analysis']
        assert analysis['risk_level'] == 'high'
        
        # Should recommend thorough testing
        assert 'security_validation' in result['priority_areas']
    
    def test_analyze_project_type(self):
        """Test project type analysis"""
        web_context = {
            'code': 'from flask import Flask\\n@app.route("/")\\ndef index(): return "Hello"',
            'features': {}
        }
        
        project_type = self.strategist._analyze_project_type(web_context)
        assert project_type == 'web_app'
        
        api_context = {
            'code': 'def get_users(): return jsonify(users)',
            'features': {}
        }
        
        project_type = self.strategist._analyze_project_type(api_context)
        assert project_type == 'api'
    
    def test_assess_risk_level(self):
        """Test risk level assessment"""
        high_risk_context = {
            'code': 'password = "secret"\\nauth_token = user_input',
            'features': {
                'cyclomatic_complexity': 20,
                'comment_ratio': 0.02
            }
        }
        
        risk_level = self.strategist._assess_risk_level(high_risk_context)
        assert risk_level == 'high'
        
        low_risk_context = {
            'code': 'def simple_math(x): return x + 1',
            'features': {
                'cyclomatic_complexity': 1,
                'comment_ratio': 0.3
            }
        }
        
        risk_level = self.strategist._assess_risk_level(low_risk_context)
        assert risk_level == 'low'
    
    def test_assess_complexity(self):
        """Test complexity assessment"""
        high_complexity_features = {
            'cyclomatic_complexity': 25,
            'lines_of_code': 600,
            'nested_depth': 6
        }
        
        complexity = self.strategist._assess_complexity({'features': high_complexity_features})
        assert complexity == 'high'
        
        low_complexity_features = {
            'cyclomatic_complexity': 2,
            'lines_of_code': 50,
            'nested_depth': 1
        }
        
        complexity = self.strategist._assess_complexity({'features': low_complexity_features})
        assert complexity == 'low'
    
    def test_select_strategy(self):
        """Test strategy selection logic"""
        # Test risk-based selection
        strategy = self.strategist._select_strategy('general', 'high', 'medium')
        assert strategy['description'] == 'Risk-based testing for critical systems'
        
        # Test web app selection
        strategy = self.strategist._select_strategy('web_app', 'medium', 'medium')
        assert strategy['description'] == 'E2E focused for user-facing applications'
        
        # Test API selection
        strategy = self.strategist._select_strategy('api', 'low', 'low')
        assert strategy['description'] == 'Unit test focused strategy for stable APIs'
    
    def test_identify_priority_areas(self):
        """Test priority area identification"""
        context = {
            'code': 'def auth_function(token): return validate(token)',
            'features': {
                'cyclomatic_complexity': 15,
                'exception_handling': 0
            }
        }
        
        priority_areas = self.strategist._identify_priority_areas(context)
        
        assert 'complex_logic_paths' in priority_areas
        assert 'error_handling' in priority_areas
        assert 'security_validation' in priority_areas
    
    def test_generate_optimization_tips(self):
        """Test optimization tip generation"""
        strategy = {
            'focus': 'speed_and_coverage',
            'distribution': {'unit': 0.7, 'integration': 0.2, 'e2e': 0.1}
        }
        
        tips = self.strategist._generate_optimization_tips(strategy)
        
        assert len(tips) > 0
        assert any('speed_and_coverage' in tip for tip in tips)
        assert any('70%-20%-10%' in tip for tip in tips)
    
    def test_estimate_effort_reduction(self):
        """Test effort reduction estimation"""
        strategy = {
            'description': 'Unit test focused strategy for stable APIs'
        }
        
        estimation = self.strategist._estimate_effort_reduction(strategy)
        
        assert 'testing_effort_reduction' in estimation
        assert 'time_savings_per_cycle' in estimation
        assert 'annual_savings_estimate' in estimation
        assert '%' in estimation['testing_effort_reduction']


class TestMLTestingQAServer:
    """Test the main ML Testing QA server"""
    
    def setup_method(self):
        self.server = MLTestingQAServer()
    
    @pytest.mark.asyncio
    async def test_handle_test_generation(self):
        """Test test generation handling"""
        request = {
            'code': '''
def add(a, b):
    return a + b
''',
            'context': {'test_framework': 'pytest'}
        }
        
        result = await self.server.handle_test_generation(request)
        
        assert 'unit_tests' in result
        assert 'coverage_estimate' in result
        assert 'request_metadata' in result
        assert 'timestamp' in result['request_metadata']
    
    @pytest.mark.asyncio
    async def test_handle_quality_prediction(self):
        """Test quality prediction handling"""
        request = {
            'code': '''
def calculate(x, y):
    return x * y
''',
            'context': {'project_type': 'utility'}
        }
        
        result = await self.server.handle_quality_prediction(request)
        
        assert 'overall_quality_score' in result
        assert 'bug_prediction' in result
        assert 'request_metadata' in result
    
    @pytest.mark.asyncio
    async def test_handle_strategy_optimization(self):
        """Test strategy optimization handling"""
        request = {
            'project_context': {
                'project_type': 'web_app',
                'team_size': 5,
                'risk_tolerance': 'medium'
            },
            'code': '''
from flask import Flask
app = Flask(__name__)
'''
        }
        
        result = await self.server.handle_strategy_optimization(request)
        
        assert 'recommended_strategy' in result
        assert 'project_analysis' in result
        assert 'request_metadata' in result
    
    @pytest.mark.asyncio
    async def test_handle_comprehensive_analysis(self):
        """Test comprehensive analysis handling"""
        request = {
            'code': '''
def process_data(data):
    if not data:
        return []
    
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    
    return result
''',
            'context': {
                'project_type': 'data_processing',
                'criticality': 'medium'
            }
        }
        
        result = await self.server.handle_comprehensive_analysis(request)
        
        assert 'test_generation' in result
        assert 'quality_prediction' in result
        assert 'strategy_optimization' in result
        assert 'comprehensive_summary' in result
        assert 'request_metadata' in result
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in server methods"""
        # Test with missing code
        request = {}
        
        result = await self.server.handle_test_generation(request)
        assert 'error' in result
        
        result = await self.server.handle_quality_prediction(request)
        assert 'error' in result
    
    def test_performance_metrics_tracking(self):
        """Test performance metrics tracking"""
        from datetime import datetime
        
        # Test successful request
        start_time = datetime.now()
        self.server._update_performance_metrics(True, start_time)
        
        metrics = self.server.get_performance_metrics()
        
        assert metrics['total_requests'] == 1
        assert metrics['successful_requests'] == 1
        assert metrics['success_rate_percentage'] == 100.0
        assert metrics['average_response_time'] > 0
    
    def test_comprehensive_summary_generation(self):
        """Test comprehensive summary generation"""
        test_results = {
            'coverage_estimate': 85,
            'test_quality_score': 90
        }
        
        quality_results = {
            'overall_quality_score': 75,
            'security_score': 80,
            'recommendations': ['Add more tests', 'Improve documentation'],
            'risk_areas': ['High complexity'],
            'bug_prediction': {'risk_level': 'medium'}
        }
        
        strategy_results = {
            'optimization_tips': ['Use unit tests', 'Add integration tests', 'Consider E2E']
        }
        
        summary = self.server._generate_comprehensive_summary(
            test_results, quality_results, strategy_results
        )
        
        assert 'overall_assessment' in summary
        assert 'key_recommendations' in summary
        assert 'priority_actions' in summary
        assert 'risk_level' in summary
        assert 'estimated_effort' in summary
        
        assert summary['overall_assessment'] == 'good'  # 75 is good
        assert len(summary['key_recommendations']) > 0
        assert len(summary['priority_actions']) > 0


class TestIntegration:
    """Integration tests for the complete system"""
    
    def setup_method(self):
        self.server = MLTestingQAServer()
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete workflow from code to recommendations"""
        code = '''
def user_authentication(username, password):
    """Authenticate user with username and password"""
    if not username or not password:
        return False
    
    # Simulate database check
    if username == "admin" and password == "password123":
        return True
    
    return False

def process_user_data(user_data):
    """Process user data with validation"""
    if not isinstance(user_data, dict):
        raise TypeError("User data must be a dictionary")
    
    required_fields = ['name', 'email', 'age']
    for field in required_fields:
        if field not in user_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate age
    if user_data['age'] < 0 or user_data['age'] > 150:
        raise ValueError("Invalid age")
    
    return {
        'id': hash(user_data['email']),
        'name': user_data['name'],
        'email': user_data['email'],
        'age': user_data['age'],
        'processed': True
    }
'''
        
        # Test comprehensive analysis
        result = await self.server.handle_comprehensive_analysis({
            'code': code,
            'context': {
                'project_type': 'web_app',
                'criticality': 'high',
                'team_size': 8
            }
        })
        
        # Verify all components worked
        assert 'test_generation' in result
        assert 'quality_prediction' in result
        assert 'strategy_optimization' in result
        assert 'comprehensive_summary' in result
        
        # Verify test generation
        test_gen = result['test_generation']
        assert 'unit_tests' in test_gen
        assert 'edge_case_tests' in test_gen
        assert test_gen['coverage_estimate'] > 0
        
        # Verify quality prediction
        quality_pred = result['quality_prediction']
        assert 'overall_quality_score' in quality_pred
        assert 'bug_prediction' in quality_pred
        assert 'security_score' in quality_pred
        
        # Verify strategy optimization
        strategy_opt = result['strategy_optimization']
        assert 'recommended_strategy' in strategy_opt
        assert 'project_analysis' in strategy_opt
        
        # Verify comprehensive summary
        summary = result['comprehensive_summary']
        assert 'overall_assessment' in summary
        assert 'key_recommendations' in summary
        assert 'priority_actions' in summary
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Test performance with multiple concurrent requests"""
        code = '''
def simple_function(x):
    return x * 2
'''
        
        # Create multiple concurrent requests
        tasks = []
        for i in range(5):
            task = self.server.handle_test_generation({
                'code': code,
                'context': {'test_framework': 'pytest'}
            })
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all requests succeeded
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == 5
        
        # Check performance metrics
        metrics = self.server.get_performance_metrics()
        assert metrics['total_requests'] >= 5
        assert metrics['success_rate_percentage'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])