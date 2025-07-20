#!/usr/bin/env python3
"""
ML Testing QA MCP Server
Intelligent test generation, quality prediction, and adaptive testing strategies

This server implements:
1. Intelligent Test Generator - AI-powered test case creation with edge case discovery
2. Quality Prediction Engine - ML-based code quality assessment and bug prediction
3. Adaptive Testing Strategist - Dynamic test strategy optimization
4. Edge Case Discoverer - Advanced boundary condition detection
5. Test Coverage Optimizer - Intelligent coverage maximization

Performance Targets:
- 95%+ automated test coverage
- 80% reduction in production bugs
- 60% reduction in testing effort
- 90%+ bug prediction accuracy
"""

import asyncio
import json
import logging
import os
import sys
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Add the src directory to the Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import MCP components
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        LoggingLevel
    )
except ImportError:
    print("MCP library not found. Installing...")
    os.system("pip install mcp")
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        LoggingLevel
    )

# Import ML and analysis libraries
try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
except ImportError:
    print("Installing required ML libraries...")
    os.system("pip install numpy pandas scikit-learn")
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

# Import code analysis libraries
try:
    import ast
    import re
    from collections import defaultdict, Counter
except ImportError as e:
    print(f"Standard library import error: {e}")
    raise

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ml_testing_qa.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("ml-testing-qa")


class CodeFeatureExtractor:
    """Extract features from code for ML analysis"""
    
    def __init__(self):
        self.complexity_weights = {
            'if': 1, 'elif': 1, 'else': 0.5, 'for': 2, 'while': 2,
            'try': 1, 'except': 1, 'finally': 0.5, 'with': 1,
            'and': 0.5, 'or': 0.5, 'not': 0.5, 'lambda': 1
        }
    
    def extract_features(self, code: str) -> Dict[str, Any]:
        """Extract comprehensive features from code"""
        try:
            tree = ast.parse(code)
            features = {
                'lines_of_code': len(code.splitlines()),
                'cyclomatic_complexity': self._calculate_complexity(tree),
                'function_count': len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                'class_count': len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                'import_count': len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]),
                'comment_ratio': self._calculate_comment_ratio(code),
                'string_literals': len([n for n in ast.walk(tree) if isinstance(n, ast.Str)]),
                'nested_depth': self._calculate_max_depth(tree),
                'exception_handling': len([n for n in ast.walk(tree) if isinstance(n, ast.Try)]),
                'comprehensions': len([n for n in ast.walk(tree) if isinstance(n, (ast.ListComp, ast.DictComp, ast.SetComp))]),
                'lambda_functions': len([n for n in ast.walk(tree) if isinstance(n, ast.Lambda)]),
                'decorator_count': sum(len(n.decorator_list) for n in ast.walk(tree) if hasattr(n, 'decorator_list')),
                'global_variables': len([n for n in ast.walk(tree) if isinstance(n, ast.Global)]),
                'binary_operations': len([n for n in ast.walk(tree) if isinstance(n, ast.BinOp)]),
                'comparison_operations': len([n for n in ast.walk(tree) if isinstance(n, ast.Compare)])
            }
            
            # Add code quality metrics
            features.update(self._extract_quality_metrics(code, tree))
            
            return features
            
        except SyntaxError:
            # Return basic metrics for invalid syntax
            return {
                'lines_of_code': len(code.splitlines()),
                'syntax_errors': 1,
                'cyclomatic_complexity': 0,
                'function_count': 0,
                'class_count': 0
            }
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _calculate_comment_ratio(self, code: str) -> float:
        """Calculate ratio of comments to code lines"""
        lines = code.splitlines()
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        total_lines = len([line for line in lines if line.strip()])
        
        return comment_lines / max(total_lines, 1)
    
    def _calculate_max_depth(self, tree: ast.AST) -> int:
        """Calculate maximum nesting depth"""
        def get_depth(node, current_depth=0):
            max_depth = current_depth
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.FunctionDef, ast.ClassDef)):
                    child_depth = get_depth(child, current_depth + 1)
                    max_depth = max(max_depth, child_depth)
                else:
                    child_depth = get_depth(child, current_depth)
                    max_depth = max(max_depth, child_depth)
            return max_depth
        
        return get_depth(tree)
    
    def _extract_quality_metrics(self, code: str, tree: ast.AST) -> Dict[str, Any]:
        """Extract code quality metrics"""
        # Maintainability Index approximation
        halstead = self._calculate_halstead_metrics(tree)
        lines = len(code.splitlines())
        complexity = self._calculate_complexity(tree)
        comment_ratio = self._calculate_comment_ratio(code)
        
        # Simplified Maintainability Index
        maintainability_index = max(0, (
            171 - 
            5.2 * np.log(halstead.get('volume', 1)) -
            0.23 * complexity -
            16.2 * np.log(max(lines, 1)) +
            50 * comment_ratio
        ))
        
        return {
            'maintainability_index': maintainability_index,
            'halstead_volume': halstead.get('volume', 0),
            'halstead_difficulty': halstead.get('difficulty', 0),
            'halstead_effort': halstead.get('effort', 0),
            'technical_debt_ratio': max(0, (100 - maintainability_index) / 100)
        }
    
    def _calculate_halstead_metrics(self, tree: ast.AST) -> Dict[str, float]:
        """Calculate Halstead complexity metrics"""
        operators = set()
        operands = set()
        operator_count = 0
        operand_count = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)):
                operators.add(type(node).__name__)
                operator_count += 1
            elif isinstance(node, (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
                operators.add(type(node).__name__)
                operator_count += 1
            elif isinstance(node, ast.Name):
                operands.add(node.id)
                operand_count += 1
            elif isinstance(node, ast.Num):
                operands.add(str(node.n))
                operand_count += 1
        
        n1 = len(operators)  # unique operators
        n2 = len(operands)   # unique operands
        N1 = operator_count  # total operators
        N2 = operand_count   # total operands
        
        vocabulary = n1 + n2
        length = N1 + N2
        
        if n2 == 0:
            return {'volume': 0, 'difficulty': 0, 'effort': 0}
        
        volume = length * np.log2(max(vocabulary, 1))
        difficulty = (n1 / 2) * (N2 / max(n2, 1))
        effort = difficulty * volume
        
        return {
            'volume': volume,
            'difficulty': difficulty,
            'effort': effort
        }


class TestGenLLMModel:
    """Advanced LLM-based test generation using fine-tuned models"""
    
    def __init__(self):
        self.model_name = "microsoft/CodeT5-small"  # Or use local model
        self.tokenizer = None
        self.model = None
        self.max_length = 512
        self.temperature = 0.7
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the LLM model for test generation"""
        try:
            # Try to import transformers - if not available, use mock
            try:
                from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
                self.is_initialized = True
                logging.info("TestGen-LLM model initialized successfully")
            except ImportError:
                logging.warning("Transformers not available, using mock LLM")
                self.is_initialized = False
        except Exception as e:
            logging.error(f"Failed to initialize LLM model: {e}")
            self.is_initialized = False
    
    async def generate_tests(self, code_context: Dict[str, Any]) -> List[str]:
        """Generate test cases using LLM with context understanding"""
        
        if not self.is_initialized:
            # Fallback to template-based generation
            return await self._generate_template_tests(code_context)
        
        try:
            # Prepare prompt for LLM
            prompt = self._create_generation_prompt(code_context)
            
            # Generate tests using LLM
            generated_tests = await self._llm_generate(prompt)
            
            # Filter and validate generated tests
            valid_tests = await self._filter_and_validate(generated_tests, code_context)
            
            return valid_tests
            
        except Exception as e:
            logging.error(f"LLM test generation failed: {e}")
            return await self._generate_template_tests(code_context)
    
    def _create_generation_prompt(self, code_context: Dict[str, Any]) -> str:
        """Create optimized prompt for test generation"""
        
        function_signature = code_context.get('function_signature', '')
        function_body = code_context.get('function_body', '')
        docstring = code_context.get('docstring', '')
        complexity_metrics = code_context.get('complexity_metrics', {})
        
        prompt = f"""Generate comprehensive test cases for the following function:

Function Signature: {function_signature}
Function Body: {function_body}
Documentation: {docstring}
Complexity: {complexity_metrics.get('cyclomatic_complexity', 'unknown')}

Requirements:
1. Test normal cases with typical inputs
2. Test edge cases and boundary conditions  
3. Test error handling with invalid inputs
4. Test performance with large inputs if applicable
5. Include property-based tests where relevant
6. Use pytest framework with proper assertions
7. Include docstrings explaining test purpose

Generate tests:"""
        
        return prompt
    
    async def _llm_generate(self, prompt: str) -> List[str]:
        """Generate tests using the LLM model"""
        
        if not self.is_initialized:
            return []
        
        try:
            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=self.max_length, truncation=True)
            
            # Generate output
            try:
                import torch
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs,
                        max_length=self.max_length * 2,
                        temperature=self.temperature,
                        num_return_sequences=3,  # Generate multiple variants
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
            except ImportError:
                logging.warning("PyTorch not available for LLM generation")
                return []
            
            # Decode generated tests
            generated_tests = []
            for output in outputs:
                test_code = self.tokenizer.decode(output, skip_special_tokens=True)
                generated_tests.append(test_code)
            
            return generated_tests
            
        except Exception as e:
            logging.error(f"LLM generation error: {e}")
            return []
    
    async def _filter_and_validate(self, generated_tests: List[str], code_context: Dict[str, Any]) -> List[str]:
        """Filter out invalid tests and validate syntax"""
        
        valid_tests = []
        
        for test_code in generated_tests:
            try:
                # Check syntax validity
                ast.parse(test_code)
                
                # Check for hallucinations and invalid patterns
                if self._is_valid_test(test_code, code_context):
                    valid_tests.append(test_code)
                    
            except SyntaxError:
                logging.debug(f"Invalid syntax in generated test: {test_code[:100]}...")
                continue
            except Exception as e:
                logging.debug(f"Test validation error: {e}")
                continue
        
        return valid_tests
    
    def _is_valid_test(self, test_code: str, code_context: Dict[str, Any]) -> bool:
        """Validate that generated test is reasonable and not hallucinated"""
        
        function_name = code_context.get('function_name', '')
        
        # Check that test actually tests the target function
        if function_name and function_name not in test_code:
            return False
        
        # Check for common hallucination patterns
        hallucination_patterns = [
            r'import\s+non_existent_module',
            r'from\s+fake_library',
            r'assert\s+impossible_condition',
            r'magic_function\(',
            r'undefined_variable'
        ]
        
        for pattern in hallucination_patterns:
            if re.search(pattern, test_code):
                return False
        
        # Check for proper test structure
        if 'def test_' not in test_code or 'assert' not in test_code:
            return False
        
        return True
    
    async def _generate_template_tests(self, code_context: Dict[str, Any]) -> List[str]:
        """Fallback template-based test generation"""
        
        function_name = code_context.get('function_name', 'unknown_function')
        function_signature = code_context.get('function_signature', '')
        
        templates = [
            f"""
def test_{function_name}_basic():
    \"\"\"Test basic functionality of {function_name}\"\"\"
    # TODO: Implement basic test case
    result = {function_name}()  # Add appropriate parameters
    assert result is not None
""",
            f"""
def test_{function_name}_edge_cases():
    \"\"\"Test edge cases for {function_name}\"\"\"
    # TODO: Implement edge case tests
    with pytest.raises((ValueError, TypeError)):
        {function_name}(None)
""",
            f"""
def test_{function_name}_invalid_input():
    \"\"\"Test error handling in {function_name}\"\"\"
    # TODO: Implement error handling tests
    with pytest.raises(Exception):
        {function_name}("invalid_input")
"""
        ]
        
        return templates


class BugPredictionModel:
    """ML model for predicting bug probability in code"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.feature_vectorizer = TfidfVectorizer(max_features=1000)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
        
    async def train_model(self, training_data: List[Dict[str, Any]]):
        """Train the bug prediction model on historical data"""
        
        try:
            if not training_data:
                # Create synthetic training data for demonstration
                training_data = self._create_synthetic_data()
            
            # Extract features from training data
            features, labels = self._extract_training_features(training_data)
            
            if len(features) == 0:
                logging.warning("No training data available, using default model")
                return
            
            # Split data for validation
            X_train, X_test, y_train, y_test = train_test_split(
                features, labels, test_size=0.2, random_state=42
            )
            
            # Train the model
            self.model.fit(X_train, y_train)
            self.is_trained = True
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            
            logging.info(f"Bug prediction model trained - Accuracy: {accuracy:.3f}, Precision: {precision:.3f}, Recall: {recall:.3f}")
            
        except Exception as e:
            logging.error(f"Model training failed: {e}")
            self.is_trained = False
    
    async def predict_bugs(self, code_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Predict bug probability for given code"""
        
        if not self.is_trained:
            # Use heuristic-based prediction as fallback
            return self._heuristic_bug_prediction(code_metrics)
        
        try:
            # Extract features for prediction
            features = self._extract_prediction_features(code_metrics)
            
            if len(features) == 0:
                return self._heuristic_bug_prediction(code_metrics)
            
            # Make prediction
            bug_probability = self.model.predict_proba([features])[0][1]  # Probability of bug class
            prediction = self.model.predict([features])[0]
            
            # Get feature importance for explanation
            feature_importance = self._get_feature_importance(features)
            
            return {
                'bug_probability': float(bug_probability),
                'prediction': bool(prediction),
                'confidence': float(max(self.model.predict_proba([features])[0])),
                'risk_level': self._get_risk_level(bug_probability),
                'contributing_factors': feature_importance,
                'recommendations': self._generate_recommendations(code_metrics, bug_probability)
            }
            
        except Exception as e:
            logging.error(f"Bug prediction failed: {e}")
            return self._heuristic_bug_prediction(code_metrics)
    
    def _extract_training_features(self, training_data: List[Dict[str, Any]]) -> Tuple[List[List[float]], List[int]]:
        """Extract features from training data"""
        
        features = []
        labels = []
        
        for item in training_data:
            try:
                code_metrics = item.get('metrics', {})
                has_bugs = item.get('has_bugs', False)
                
                feature_vector = [
                    code_metrics.get('cyclomatic_complexity', 0),
                    code_metrics.get('lines_of_code', 0),
                    code_metrics.get('number_of_functions', 0),
                    code_metrics.get('depth_of_nesting', 0),
                    code_metrics.get('number_of_parameters', 0),
                    code_metrics.get('halstead_volume', 0),
                    code_metrics.get('maintainability_index', 100),
                    len(code_metrics.get('imports', [])),
                    len(code_metrics.get('exceptions_caught', [])),
                    len(code_metrics.get('global_variables', []))
                ]
                
                features.append(feature_vector)
                labels.append(1 if has_bugs else 0)
                
            except Exception as e:
                logging.debug(f"Feature extraction error: {e}")
                continue
        
        return features, labels
    
    def _extract_prediction_features(self, code_metrics: Dict[str, Any]) -> List[float]:
        """Extract features for prediction"""
        
        return [
            code_metrics.get('cyclomatic_complexity', 0),
            code_metrics.get('lines_of_code', 0),
            code_metrics.get('number_of_functions', 0),
            code_metrics.get('depth_of_nesting', 0),
            code_metrics.get('number_of_parameters', 0),
            code_metrics.get('halstead_volume', 0),
            code_metrics.get('maintainability_index', 100),
            len(code_metrics.get('imports', [])),
            len(code_metrics.get('exceptions_caught', [])),
            len(code_metrics.get('global_variables', []))
        ]
    
    def _create_synthetic_data(self) -> List[Dict[str, Any]]:
        """Create synthetic training data for demonstration"""
        
        synthetic_data = []
        
        # Generate samples with different complexity levels
        for i in range(100):
            complexity = np.random.uniform(1, 20)
            loc = int(np.random.uniform(10, 500))
            
            # Higher complexity correlates with more bugs
            bug_probability = min(0.9, complexity / 15 + np.random.normal(0, 0.1))
            has_bugs = np.random.random() < bug_probability
            
            synthetic_data.append({
                'metrics': {
                    'cyclomatic_complexity': complexity,
                    'lines_of_code': loc,
                    'number_of_functions': max(1, int(loc / 20)),
                    'depth_of_nesting': int(np.random.uniform(1, 8)),
                    'number_of_parameters': int(np.random.uniform(0, 10)),
                    'halstead_volume': np.random.uniform(50, 1000),
                    'maintainability_index': np.random.uniform(0, 100),
                    'imports': ['module' + str(j) for j in range(int(np.random.uniform(0, 10)))],
                    'exceptions_caught': ['Exception' + str(j) for j in range(int(np.random.uniform(0, 5)))],
                    'global_variables': ['var' + str(j) for j in range(int(np.random.uniform(0, 5)))]
                },
                'has_bugs': has_bugs
            })
        
        return synthetic_data
    
    def _heuristic_bug_prediction(self, code_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback heuristic-based bug prediction"""
        
        complexity = code_metrics.get('cyclomatic_complexity', 0)
        loc = code_metrics.get('lines_of_code', 0)
        nesting = code_metrics.get('depth_of_nesting', 0)
        
        # Simple heuristic: higher complexity = higher bug probability
        risk_score = (complexity * 0.4 + loc / 100 * 0.3 + nesting * 0.3) / 10
        bug_probability = min(0.95, risk_score)
        
        return {
            'bug_probability': bug_probability,
            'prediction': bug_probability > 0.5,
            'confidence': 0.7,  # Moderate confidence for heuristics
            'risk_level': self._get_risk_level(bug_probability),
            'contributing_factors': {
                'cyclomatic_complexity': complexity,
                'lines_of_code': loc,
                'depth_of_nesting': nesting
            },
            'recommendations': self._generate_recommendations(code_metrics, bug_probability)
        }
    
    def _get_risk_level(self, bug_probability: float) -> str:
        """Convert bug probability to risk level"""
        
        if bug_probability < 0.2:
            return 'low'
        elif bug_probability < 0.5:
            return 'medium'
        elif bug_probability < 0.8:
            return 'high'
        else:
            return 'critical'
    
    def _get_feature_importance(self, features: List[float]) -> Dict[str, float]:
        """Get feature importance for explanation"""
        
        if not self.is_trained:
            return {}
        
        feature_names = [
            'cyclomatic_complexity', 'lines_of_code', 'number_of_functions',
            'depth_of_nesting', 'number_of_parameters', 'halstead_volume',
            'maintainability_index', 'imports_count', 'exceptions_count', 'globals_count'
        ]
        
        importance_dict = {}
        feature_importances = self.model.feature_importances_
        
        for i, importance in enumerate(feature_importances):
            if i < len(feature_names):
                importance_dict[feature_names[i]] = float(importance)
        
        return importance_dict
    
    def _generate_recommendations(self, code_metrics: Dict[str, Any], bug_probability: float) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        complexity = code_metrics.get('cyclomatic_complexity', 0)
        loc = code_metrics.get('lines_of_code', 0)
        nesting = code_metrics.get('depth_of_nesting', 0)
        
        if complexity > 10:
            recommendations.append("Reduce cyclomatic complexity by breaking down complex functions")
        
        if loc > 200:
            recommendations.append("Consider splitting large functions into smaller, focused functions")
        
        if nesting > 4:
            recommendations.append("Reduce nesting depth by using early returns or extracting nested logic")
        
        if bug_probability > 0.7:
            recommendations.append("Add comprehensive unit tests with edge case coverage")
            recommendations.append("Consider code review with senior developers")
            recommendations.append("Implement static analysis tools and linting")
        
        return recommendations


class EdgeCaseDiscoveryEngine:
    """Advanced edge case discovery using ML and heuristics"""
    
    def __init__(self):
        self.boundary_analyzer = BoundaryValueAnalyzer()
        self.equivalence_partitioner = EquivalencePartitioner()
        self.mutation_generator = MutationTestGenerator()
        
    async def discover_edge_cases(self, code_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Discover edge cases using multiple techniques"""
        
        edge_cases = []
        
        try:
            # Boundary value analysis
            boundary_cases = await self.boundary_analyzer.analyze(code_analysis)
            edge_cases.extend(boundary_cases)
            
            # Equivalence partitioning
            partition_cases = await self.equivalence_partitioner.generate(code_analysis)
            edge_cases.extend(partition_cases)
            
            # Mutation-based edge cases
            mutation_cases = await self.mutation_generator.generate(code_analysis)
            edge_cases.extend(mutation_cases)
            
            # Rank edge cases by importance
            ranked_cases = await self._rank_edge_cases(edge_cases, code_analysis)
            
            return ranked_cases[:20]  # Return top 20 edge cases
            
        except Exception as e:
            logging.error(f"Edge case discovery failed: {e}")
            return self._generate_basic_edge_cases(code_analysis)
    
    async def _rank_edge_cases(self, edge_cases: List[Dict[str, Any]], code_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank edge cases by likelihood to find bugs"""
        
        for case in edge_cases:
            # Calculate importance score based on multiple factors
            score = 0.0
            
            # Complexity of the test case
            score += case.get('complexity_score', 0) * 0.3
            
            # Coverage potential
            score += case.get('coverage_potential', 0) * 0.3
            
            # Historical bug correlation
            score += case.get('bug_correlation', 0) * 0.4
            
            case['importance_score'] = score
        
        # Sort by importance score
        return sorted(edge_cases, key=lambda x: x.get('importance_score', 0), reverse=True)
    
    def _generate_basic_edge_cases(self, code_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate basic edge cases as fallback"""
        
        function_name = code_analysis.get('function_name', 'unknown')
        
        basic_cases = [
            {
                'case_type': 'null_input',
                'description': 'Test with None/null input',
                'test_code': f'pytest.raises(TypeError, {function_name}, None)',
                'importance_score': 0.8,
                'complexity_score': 0.3
            },
            {
                'case_type': 'empty_input',
                'description': 'Test with empty input',
                'test_code': f'pytest.raises(ValueError, {function_name}, "")',
                'importance_score': 0.7,
                'complexity_score': 0.3
            },
            {
                'case_type': 'boundary_max',
                'description': 'Test with maximum boundary value',
                'test_code': f'{function_name}(sys.maxsize)',
                'importance_score': 0.6,
                'complexity_score': 0.4
            },
            {
                'case_type': 'boundary_min',
                'description': 'Test with minimum boundary value',
                'test_code': f'{function_name}(-sys.maxsize)',
                'importance_score': 0.6,
                'complexity_score': 0.4
            }
        ]
        
        return basic_cases


class BoundaryValueAnalyzer:
    """Analyzes code to identify boundary values for testing"""
    
    async def analyze(self, code_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze code for boundary value test cases"""
        
        boundary_cases = []
        
        try:
            # Extract numeric literals and ranges from code
            numeric_values = self._extract_numeric_values(code_analysis)
            
            # Generate boundary tests for each numeric value
            for value in numeric_values:
                boundary_cases.extend(self._generate_boundary_tests(value, code_analysis))
            
            # Extract string length constraints
            string_constraints = self._extract_string_constraints(code_analysis)
            
            # Generate boundary tests for string lengths
            for constraint in string_constraints:
                boundary_cases.extend(self._generate_string_boundary_tests(constraint, code_analysis))
            
            return boundary_cases
            
        except Exception as e:
            logging.error(f"Boundary analysis failed: {e}")
            return []
    
    def _extract_numeric_values(self, code_analysis: Dict[str, Any]) -> List[int]:
        """Extract numeric values from code for boundary testing"""
        
        numeric_values = []
        code = code_analysis.get('function_body', '')
        
        # Find numeric literals in code
        numeric_pattern = r'\b\d+\b'
        matches = re.findall(numeric_pattern, code)
        
        for match in matches:
            try:
                value = int(match)
                if value > 0:  # Only consider positive values for boundary testing
                    numeric_values.append(value)
            except ValueError:
                continue
        
        return list(set(numeric_values))  # Remove duplicates
    
    def _generate_boundary_tests(self, value: int, code_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate boundary test cases for a numeric value"""
        
        function_name = code_analysis.get('function_name', 'unknown')
        
        boundary_tests = [
            {
                'case_type': 'boundary_below',
                'description': f'Test with value just below boundary ({value-1})',
                'test_code': f'{function_name}({value-1})',
                'boundary_value': value,
                'test_value': value - 1,
                'importance_score': 0.8,
                'complexity_score': 0.4
            },
            {
                'case_type': 'boundary_exact',
                'description': f'Test with exact boundary value ({value})',
                'test_code': f'{function_name}({value})',
                'boundary_value': value,
                'test_value': value,
                'importance_score': 0.9,
                'complexity_score': 0.3
            },
            {
                'case_type': 'boundary_above',
                'description': f'Test with value just above boundary ({value+1})',
                'test_code': f'{function_name}({value+1})',
                'boundary_value': value,
                'test_value': value + 1,
                'importance_score': 0.8,
                'complexity_score': 0.4
            }
        ]
        
        return boundary_tests
    
    def _extract_string_constraints(self, code_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract string length constraints from code"""
        
        constraints = []
        code = code_analysis.get('function_body', '')
        
        # Look for string length checks
        length_patterns = [
            r'len\([^)]+\)\s*[<>=]+\s*(\d+)',
            r'[^.]+\.length\s*[<>=]+\s*(\d+)',
            r'if\s+.+\s*[<>=]+\s*(\d+)'
        ]
        
        for pattern in length_patterns:
            matches = re.findall(pattern, code)
            for match in matches:
                try:
                    length_limit = int(match)
                    constraints.append({
                        'type': 'string_length',
                        'limit': length_limit
                    })
                except ValueError:
                    continue
        
        return constraints
    
    def _generate_string_boundary_tests(self, constraint: Dict[str, Any], code_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate boundary test cases for string constraints"""
        
        function_name = code_analysis.get('function_name', 'unknown')
        limit = constraint.get('limit', 10)
        
        string_tests = [
            {
                'case_type': 'string_empty',
                'description': 'Test with empty string',
                'test_code': f'{function_name}("")',
                'importance_score': 0.8,
                'complexity_score': 0.3
            },
            {
                'case_type': 'string_limit_below',
                'description': f'Test with string length below limit ({limit-1})',
                'test_code': f'{function_name}("{"a" * (limit-1)}")',
                'importance_score': 0.7,
                'complexity_score': 0.4
            },
            {
                'case_type': 'string_limit_exact',
                'description': f'Test with string length at exact limit ({limit})',
                'test_code': f'{function_name}("{"a" * limit}")',
                'importance_score': 0.9,
                'complexity_score': 0.4
            },
            {
                'case_type': 'string_limit_above',
                'description': f'Test with string length above limit ({limit+1})',
                'test_code': f'{function_name}("{"a" * (limit+1)}")',
                'importance_score': 0.8,
                'complexity_score': 0.4
            }
        ]
        
        return string_tests


class EquivalencePartitioner:
    """Generates test cases using equivalence partitioning"""
    
    async def generate(self, code_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate equivalence partition test cases"""
        
        partition_cases = []
        
        try:
            # Analyze input domains
            input_domains = self._analyze_input_domains(code_analysis)
            
            # Generate test cases for each partition
            for domain in input_domains:
                partition_cases.extend(self._generate_partition_tests(domain, code_analysis))
            
            return partition_cases
            
        except Exception as e:
            logging.error(f"Equivalence partitioning failed: {e}")
            return []
    
    def _analyze_input_domains(self, code_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze input domains for partitioning"""
        
        domains = []
        
        # Basic input type domains
        domains.append({
            'type': 'numeric',
            'partitions': ['negative', 'zero', 'positive', 'very_large']
        })
        
        domains.append({
            'type': 'string',
            'partitions': ['empty', 'single_char', 'normal', 'very_long']
        })
        
        domains.append({
            'type': 'boolean',
            'partitions': ['true', 'false']
        })
        
        domains.append({
            'type': 'collection',
            'partitions': ['empty', 'single_element', 'multiple_elements']
        })
        
        return domains
    
    def _generate_partition_tests(self, domain: Dict[str, Any], code_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test cases for a specific domain partition"""
        
        function_name = code_analysis.get('function_name', 'unknown')
        domain_type = domain.get('type', 'unknown')
        partitions = domain.get('partitions', [])
        
        partition_tests = []
        
        for partition in partitions:
            test_value = self._get_partition_test_value(domain_type, partition)
            
            partition_tests.append({
                'case_type': f'{domain_type}_{partition}',
                'description': f'Test {domain_type} with {partition} value',
                'test_code': f'{function_name}({test_value})',
                'domain_type': domain_type,
                'partition': partition,
                'importance_score': 0.6,
                'complexity_score': 0.3
            })
        
        return partition_tests
    
    def _get_partition_test_value(self, domain_type: str, partition: str) -> str:
        """Get test value for a specific partition"""
        
        test_values = {
            'numeric': {
                'negative': '-1',
                'zero': '0',
                'positive': '1',
                'very_large': '999999'
            },
            'string': {
                'empty': '""',
                'single_char': '"a"',
                'normal': '"test_string"',
                'very_long': '"a" * 1000'
            },
            'boolean': {
                'true': 'True',
                'false': 'False'
            },
            'collection': {
                'empty': '[]',
                'single_element': '[1]',
                'multiple_elements': '[1, 2, 3, 4, 5]'
            }
        }
        
        return test_values.get(domain_type, {}).get(partition, 'None')


class MutationTestGenerator:
    """Generates test cases based on code mutations"""
    
    async def generate(self, code_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mutation-based test cases"""
        
        mutation_cases = []
        
        try:
            # Generate mutants of the original code
            mutants = self._generate_mutants(code_analysis)
            
            # Create test cases to kill each mutant
            for mutant in mutants:
                test_case = self._generate_mutant_killing_test(mutant, code_analysis)
                if test_case:
                    mutation_cases.append(test_case)
            
            return mutation_cases
            
        except Exception as e:
            logging.error(f"Mutation test generation failed: {e}")
            return []
    
    def _generate_mutants(self, code_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate code mutants for testing"""
        
        mutants = []
        code = code_analysis.get('function_body', '')
        
        # Arithmetic operator mutations
        arithmetic_mutations = [
            ('+', '-'), ('-', '+'), ('*', '/'), ('/', '*'),
            ('==', '!='), ('!=', '=='), ('<', '>='), ('>', '<=')
        ]
        
        for original, mutated in arithmetic_mutations:
            if original in code:
                mutant_code = code.replace(original, mutated, 1)
                mutants.append({
                    'type': 'arithmetic_operator',
                    'original': original,
                    'mutated': mutated,
                    'mutant_code': mutant_code,
                    'kill_difficulty': 0.6
                })
        
        # Boolean operator mutations
        boolean_mutations = [
            ('and', 'or'), ('or', 'and'), ('True', 'False'), ('False', 'True')
        ]
        
        for original, mutated in boolean_mutations:
            if original in code:
                mutant_code = code.replace(original, mutated, 1)
                mutants.append({
                    'type': 'boolean_operator',
                    'original': original,
                    'mutated': mutated,
                    'mutant_code': mutant_code,
                    'kill_difficulty': 0.7
                })
        
        # Boundary mutations
        boundary_mutations = [
            ('<=', '<'), ('>=', '>'), ('<', '<='), ('>', '>=')
        ]
        
        for original, mutated in boundary_mutations:
            if original in code:
                mutant_code = code.replace(original, mutated, 1)
                mutants.append({
                    'type': 'boundary_condition',
                    'original': original,
                    'mutated': mutated,
                    'mutant_code': mutant_code,
                    'kill_difficulty': 0.8
                })
        
        return mutants[:10]  # Limit to 10 mutants
    
    def _generate_mutant_killing_test(self, mutant: Dict[str, Any], code_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate a test case designed to kill a specific mutant"""
        
        function_name = code_analysis.get('function_name', 'unknown')
        mutant_type = mutant.get('type', 'unknown')
        original = mutant.get('original', '')
        mutated = mutant.get('mutated', '')
        
        # Generate test input that would expose the mutation
        test_input = self._get_mutant_exposing_input(mutant_type, original, mutated)
        
        if not test_input:
            return None
        
        return {
            'case_type': f'mutation_{mutant_type}',
            'description': f'Test to kill {mutant_type} mutation ({original} -> {mutated})',
            'test_code': f'assert {function_name}({test_input}) != mutated_{function_name}({test_input})',
            'mutant_type': mutant_type,
            'mutation': f'{original} -> {mutated}',
            'importance_score': mutant.get('kill_difficulty', 0.5),
            'complexity_score': 0.6
        }
    
    def _get_mutant_exposing_input(self, mutant_type: str, original: str, mutated: str) -> Optional[str]:
        """Get input that would expose the mutation"""
        
        exposing_inputs = {
            'arithmetic_operator': {
                ('+', '-'): '1, 1',  # 1+1=2 vs 1-1=0
                ('-', '+'): '5, 3',  # 5-3=2 vs 5+3=8
                ('*', '/'): '6, 2',  # 6*2=12 vs 6/2=3
                ('/', '*'): '8, 2',  # 8/2=4 vs 8*2=16
            },
            'boolean_operator': {
                ('and', 'or'): 'True, False',  # True and False != True or False
                ('or', 'and'): 'True, False',  # True or False != True and False
            },
            'boundary_condition': {
                ('<=', '<'): '5, 5',  # 5<=5 is True, 5<5 is False
                ('>=', '>'): '5, 5',  # 5>=5 is True, 5>5 is False
                ('<', '<='): '5, 5',  # 5<5 is False, 5<=5 is True
                ('>', '>='): '5, 5',  # 5>5 is False, 5>=5 is True
            }
        }
        
        mutation_key = (original, mutated)
        return exposing_inputs.get(mutant_type, {}).get(mutation_key)


class IntelligentTestGenerator:
    """Enhanced AI-powered test case generation with edge case discovery"""
    
    def __init__(self):
        self.feature_extractor = CodeFeatureExtractor()
        self.testgen_llm = TestGenLLMModel()
        self.bug_predictor = BugPredictionModel()
        self.edge_discoverer = EdgeCaseDiscoveryEngine()
        self.test_patterns = {
            'unit_test_templates': {
                'basic_function': '''
def test_{function_name}_basic():
    """Test basic functionality of {function_name}"""
    # Arrange
    {arrange_code}
    
    # Act
    result = {function_call}
    
    # Assert
    assert result == {expected_result}
''',
                'edge_cases': '''
def test_{function_name}_edge_cases():
    """Test edge cases for {function_name}"""
    # Test empty input
    with pytest.raises(ValueError):
        {function_name}()
    
    # Test None input
    with pytest.raises(TypeError):
        {function_name}(None)
    
    # Test boundary values
    assert {function_name}({min_value}) == {min_expected}
    assert {function_name}({max_value}) == {max_expected}
''',
                'error_handling': '''
def test_{function_name}_error_handling():
    """Test error handling in {function_name}"""
    # Test invalid input types
    with pytest.raises(TypeError):
        {function_name}("invalid_type")
    
    # Test invalid values
    with pytest.raises(ValueError):
        {function_name}({invalid_value})
'''
            }
        }
        
        # Edge case patterns based on data types
        self.edge_case_patterns = {
            'int': [0, -1, 1, sys.maxsize, -sys.maxsize-1],
            'float': [0.0, -0.0, float('inf'), float('-inf'), float('nan')],
            'str': ["", " ", "\n", "\t", "null", "None", "<script>"],
            'list': [[], [None], [1], list(range(1000))],
            'dict': [{}, {None: None}, {'': ''}, {'key': 'value'}],
            'bool': [True, False]
        }
    
    async def generate_tests(self, code: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate comprehensive test suite with edge cases"""
        try:
            logger.info("Starting intelligent test generation")
            
            # Analyze code structure
            features = self.feature_extractor.extract_features(code)
            functions = self._extract_functions(code)
            
            generated_tests = {
                'unit_tests': [],
                'integration_tests': [],
                'edge_case_tests': [],
                'performance_tests': [],
                'security_tests': [],
                'coverage_estimate': 0,
                'test_quality_score': 0,
                'generation_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'code_features': features,
                    'functions_analyzed': len(functions)
                }
            }
            
            # Generate tests for each function
            for func_info in functions:
                # Generate unit tests
                unit_tests = await self._generate_unit_tests(func_info, code)
                generated_tests['unit_tests'].extend(unit_tests)
                
                # Generate edge case tests
                edge_tests = await self._generate_edge_case_tests(func_info)
                generated_tests['edge_case_tests'].extend(edge_tests)
                
                # Generate performance tests
                perf_tests = await self._generate_performance_tests(func_info)
                generated_tests['performance_tests'].extend(perf_tests)
            
            # Generate integration tests
            integration_tests = await self._generate_integration_tests(functions, code)
            generated_tests['integration_tests'] = integration_tests
            
            # Generate security tests
            security_tests = await self._generate_security_tests(code)
            generated_tests['security_tests'] = security_tests
            
            # Calculate coverage estimate
            generated_tests['coverage_estimate'] = self._estimate_coverage(functions, generated_tests)
            
            # Calculate test quality score
            generated_tests['test_quality_score'] = self._calculate_test_quality_score(generated_tests)
            
            logger.info(f"Generated {sum(len(tests) for tests in generated_tests.values() if isinstance(tests, list))} tests")
            
            return generated_tests
            
        except Exception as e:
            logger.error(f"Error in test generation: {e}")
            return {
                'error': str(e),
                'unit_tests': [],
                'coverage_estimate': 0
            }
    
    def _extract_functions(self, code: str) -> List[Dict[str, Any]]:
        """Extract function information from code"""
        try:
            tree = ast.parse(code)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'returns': self._get_return_type(node),
                        'complexity': self._calculate_function_complexity(node),
                        'docstring': ast.get_docstring(node),
                        'line_number': node.lineno,
                        'decorators': [self._get_decorator_name(d) for d in node.decorator_list]
                    }
                    functions.append(func_info)
            
            return functions
            
        except Exception as e:
            logger.warning(f"Error extracting functions: {e}")
            return []
    
    def _get_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Get return type annotation if available"""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
        return None
    
    def _get_decorator_name(self, decorator) -> str:
        """Get decorator name"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
            return decorator.func.id
        return str(decorator)
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate complexity for a specific function"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
        return complexity
    
    async def _generate_unit_tests(self, func_info: Dict[str, Any], code: str) -> List[str]:
        """Generate unit tests for a function"""
        tests = []
        func_name = func_info['name']
        args = func_info['args']
        
        # Basic functionality test
        basic_test = f'''
def test_{func_name}_basic():
    """Test basic functionality of {func_name}"""
    # TODO: Add appropriate test inputs and assertions
    # result = {func_name}({', '.join(f'test_{arg}' for arg in args)})
    # assert result is not None
    pass
'''
        tests.append(basic_test)
        
        # Happy path test
        if args:
            happy_path_test = f'''
def test_{func_name}_happy_path():
    """Test {func_name} with valid inputs"""
    # TODO: Replace with actual valid inputs
    {', '.join(f'{arg} = None  # Replace with valid value' for arg in args)}
    result = {func_name}({', '.join(args)})
    # TODO: Add appropriate assertions
    assert result is not None
'''
            tests.append(happy_path_test)
        
        return tests
    
    async def _generate_edge_case_tests(self, func_info: Dict[str, Any]) -> List[str]:
        """Generate edge case tests"""
        tests = []
        func_name = func_info['name']
        args = func_info['args']
        
        if not args:
            return tests
        
        # Empty/None inputs
        edge_test = f'''
def test_{func_name}_edge_cases():
    """Test edge cases for {func_name}"""
    # Test with None inputs
    try:
        result = {func_name}({', '.join('None' for _ in args)})
        # TODO: Add appropriate assertions
    except (TypeError, ValueError) as e:
        # Expected behavior for None inputs
        pass
    
    # Test with empty inputs where applicable
    # TODO: Add specific edge cases based on parameter types
'''
        tests.append(edge_test)
        
        # Boundary value tests
        boundary_test = f'''
def test_{func_name}_boundary_values():
    """Test boundary values for {func_name}"""
    # TODO: Add boundary value tests based on parameter types
    # For integers: 0, -1, 1, max_int, min_int
    # For strings: "", single char, very long string
    # For lists: [], [single_item], large_list
    pass
'''
        tests.append(boundary_test)
        
        return tests
    
    async def _generate_performance_tests(self, func_info: Dict[str, Any]) -> List[str]:
        """Generate performance tests"""
        tests = []
        func_name = func_info['name']
        complexity = func_info.get('complexity', 1)
        
        if complexity > 5:  # Only for complex functions
            perf_test = f'''
def test_{func_name}_performance():
    """Test performance of {func_name}"""
    import time
    
    # TODO: Replace with appropriate large inputs
    large_input = None  # Create large test input
    
    start_time = time.time()
    result = {func_name}(large_input)
    end_time = time.time()
    
    execution_time = end_time - start_time
    # TODO: Set appropriate performance threshold
    assert execution_time < 1.0, f"Function took too long: {{execution_time:.2f}}s"
'''
            tests.append(perf_test)
        
        return tests
    
    async def _generate_integration_tests(self, functions: List[Dict], code: str) -> List[str]:
        """Generate integration tests"""
        tests = []
        
        if len(functions) > 1:
            integration_test = '''
def test_function_integration():
    """Test integration between functions"""
    # TODO: Test how functions work together
    # Call functions in sequence and verify data flow
    pass
'''
            tests.append(integration_test)
        
        return tests
    
    async def _generate_security_tests(self, code: str) -> List[str]:
        """Generate security-focused tests"""
        tests = []
        
        # Check for common security issues
        if 'input(' in code or 'eval(' in code or 'exec(' in code:
            security_test = '''
def test_security_input_validation():
    """Test security aspects of input handling"""
    # TODO: Test with malicious inputs
    # - SQL injection attempts
    # - XSS attempts
    # - Command injection attempts
    # - Buffer overflow attempts
    pass
'''
            tests.append(security_test)
        
        return tests
    
    def _estimate_coverage(self, functions: List[Dict], tests: Dict) -> float:
        """Estimate test coverage percentage"""
        if not functions:
            return 0.0
        
        total_tests = sum(len(test_list) for test_list in tests.values() if isinstance(test_list, list))
        function_count = len(functions)
        
        # Basic estimation: aim for 3-5 tests per function for good coverage
        target_tests_per_function = 4
        coverage = min(100, (total_tests / (function_count * target_tests_per_function)) * 100)
        
        return round(coverage, 2)
    
    def _calculate_test_quality_score(self, tests: Dict) -> float:
        """Calculate test quality score based on test variety and completeness"""
        score = 0
        
        # Points for different test types
        if tests.get('unit_tests'):
            score += 30
        if tests.get('edge_case_tests'):
            score += 25
        if tests.get('integration_tests'):
            score += 20
        if tests.get('performance_tests'):
            score += 15
        if tests.get('security_tests'):
            score += 10
        
        return min(100, score)


class QualityPredictor:
    """ML-based code quality assessment and bug prediction"""
    
    def __init__(self):
        self.feature_extractor = CodeFeatureExtractor()
        self.models = {
            'bug_prediction': RandomForestClassifier(n_estimators=100, random_state=42),
            'maintainability': RandomForestClassifier(n_estimators=100, random_state=42),
            'performance_risk': IsolationForest(contamination=0.1, random_state=42),
            'security_risk': LogisticRegression(random_state=42)
        }
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Quality thresholds
        self.quality_thresholds = {
            'excellent': 90,
            'good': 75,
            'fair': 60,
            'poor': 40
        }
    
    async def predict_quality(self, code: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Predict code quality with ML models"""
        try:
            logger.info("Starting quality prediction")
            
            # Extract features
            features = self.feature_extractor.extract_features(code)
            
            # Calculate quality scores
            quality_assessment = {
                'overall_quality_score': self._calculate_overall_quality(features),
                'maintainability_score': self._calculate_maintainability_score(features),
                'complexity_score': self._calculate_complexity_score(features),
                'documentation_score': self._calculate_documentation_score(features),
                'security_score': self._calculate_security_score(code, features),
                'performance_score': self._calculate_performance_score(features),
                'bug_prediction': self._predict_bug_probability(features),
                'technical_debt': self._calculate_technical_debt(features),
                'recommendations': [],
                'risk_areas': [],
                'confidence_scores': {},
                'feature_analysis': features
            }
            
            # Generate recommendations based on scores
            quality_assessment['recommendations'] = self._generate_recommendations(quality_assessment)
            
            # Identify risk areas
            quality_assessment['risk_areas'] = self._identify_risk_areas(quality_assessment)
            
            # Calculate confidence scores
            quality_assessment['confidence_scores'] = self._calculate_confidence_scores(features)
            
            logger.info(f"Quality prediction completed. Overall score: {quality_assessment['overall_quality_score']:.2f}")
            
            return quality_assessment
            
        except Exception as e:
            logger.error(f"Error in quality prediction: {e}")
            return {
                'error': str(e),
                'overall_quality_score': 0,
                'recommendations': ['Unable to analyze code quality due to errors']
            }
    
    def _calculate_overall_quality(self, features: Dict[str, Any]) -> float:
        """Calculate overall quality score (0-100)"""
        # Weighted combination of different quality aspects
        weights = {
            'maintainability_index': 0.3,
            'complexity': 0.25,
            'documentation': 0.15,
            'structure': 0.15,
            'modularity': 0.15
        }
        
        # Normalize complexity (lower is better)
        complexity_score = max(0, 100 - (features.get('cyclomatic_complexity', 0) * 2))
        
        # Documentation score
        doc_score = min(100, features.get('comment_ratio', 0) * 300)  # Scale comment ratio
        
        # Structure score based on various factors
        structure_score = min(100, (
            (features.get('function_count', 0) * 5) +  # More functions = better structure
            (features.get('class_count', 0) * 10) +    # Classes indicate OOP
            (100 - features.get('nested_depth', 0) * 10)  # Less nesting = better
        ))
        
        # Modularity score
        modularity_score = min(100, (
            features.get('import_count', 0) * 5 +  # Imports show modular design
            (100 - features.get('lines_of_code', 0) / 50)  # Shorter functions are better
        ))
        
        overall_score = (
            features.get('maintainability_index', 50) * weights['maintainability_index'] +
            complexity_score * weights['complexity'] +
            doc_score * weights['documentation'] +
            structure_score * weights['structure'] +
            modularity_score * weights['modularity']
        )
        
        return max(0, min(100, overall_score))
    
    def _calculate_maintainability_score(self, features: Dict[str, Any]) -> float:
        """Calculate maintainability score"""
        return features.get('maintainability_index', 50)
    
    def _calculate_complexity_score(self, features: Dict[str, Any]) -> float:
        """Calculate complexity score (inverse of complexity)"""
        complexity = features.get('cyclomatic_complexity', 1)
        # Convert to 0-100 scale where lower complexity = higher score
        return max(0, 100 - (complexity * 2))
    
    def _calculate_documentation_score(self, features: Dict[str, Any]) -> float:
        """Calculate documentation score"""
        comment_ratio = features.get('comment_ratio', 0)
        # Scale comment ratio to 0-100
        return min(100, comment_ratio * 300)
    
    def _calculate_security_score(self, code: str, features: Dict[str, Any]) -> float:
        """Calculate security score"""
        security_issues = 0
        
        # Check for potential security issues
        risky_patterns = [
            r'eval\(', r'exec\(', r'input\(.*\)', r'os\.system',
            r'subprocess\.call', r'__import__', r'open\(.*["\']w',
            r'pickle\.loads', r'yaml\.load(?!_safe)', r'sql.*%.*%'
        ]
        
        for pattern in risky_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                security_issues += 1
        
        # Exception handling reduces security risks
        exception_handling = features.get('exception_handling', 0)
        security_bonus = min(20, exception_handling * 5)
        
        # Calculate score (start at 100, subtract for issues, add bonus)
        security_score = 100 - (security_issues * 15) + security_bonus
        
        return max(0, min(100, security_score))
    
    def _calculate_performance_score(self, features: Dict[str, Any]) -> float:
        """Calculate performance score"""
        # Performance factors
        complexity_penalty = features.get('cyclomatic_complexity', 0) * 2
        nested_depth_penalty = features.get('nested_depth', 0) * 5
        comprehension_bonus = features.get('comprehensions', 0) * 3
        
        performance_score = 100 - complexity_penalty - nested_depth_penalty + comprehension_bonus
        
        return max(0, min(100, performance_score))
    
    def _predict_bug_probability(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict bug probability based on code features"""
        # Simple heuristic-based bug prediction
        risk_factors = {
            'high_complexity': features.get('cyclomatic_complexity', 0) > 10,
            'deep_nesting': features.get('nested_depth', 0) > 4,
            'large_function': features.get('lines_of_code', 0) > 100,
            'no_documentation': features.get('comment_ratio', 0) < 0.1,
            'no_exception_handling': features.get('exception_handling', 0) == 0,
            'many_globals': features.get('global_variables', 0) > 2
        }
        
        risk_count = sum(risk_factors.values())
        total_factors = len(risk_factors)
        
        # Calculate probability (0-1)
        bug_probability = risk_count / total_factors
        
        # Risk level
        if bug_probability < 0.3:
            risk_level = 'low'
        elif bug_probability < 0.6:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        return {
            'probability': bug_probability,
            'risk_level': risk_level,
            'risk_factors': {k: v for k, v in risk_factors.items() if v},
            'confidence': 0.75  # Heuristic confidence
        }
    
    def _calculate_technical_debt(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate technical debt indicators"""
        debt_score = features.get('technical_debt_ratio', 0) * 100
        
        # Additional debt factors
        complexity_debt = max(0, features.get('cyclomatic_complexity', 0) - 10) * 5
        documentation_debt = max(0, (0.2 - features.get('comment_ratio', 0)) * 200)
        
        total_debt = debt_score + complexity_debt + documentation_debt
        
        return {
            'total_debt_score': min(100, total_debt),
            'complexity_debt': complexity_debt,
            'documentation_debt': documentation_debt,
            'estimated_hours_to_fix': total_debt / 10  # Rough estimate
        }
    
    def _generate_recommendations(self, assessment: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Quality-based recommendations
        if assessment['overall_quality_score'] < 60:
            recommendations.append("Overall code quality needs improvement. Focus on reducing complexity and improving documentation.")
        
        if assessment['complexity_score'] < 50:
            recommendations.append("High complexity detected. Consider breaking down large functions into smaller, more focused ones.")
        
        if assessment['documentation_score'] < 40:
            recommendations.append("Add more comments and docstrings to improve code documentation.")
        
        if assessment['security_score'] < 70:
            recommendations.append("Security concerns detected. Review and fix potential security vulnerabilities.")
        
        if assessment['performance_score'] < 60:
            recommendations.append("Performance optimization recommended. Consider algorithmic improvements and code profiling.")
        
        # Bug prediction recommendations
        bug_pred = assessment.get('bug_prediction', {})
        if bug_pred.get('risk_level') == 'high':
            recommendations.append("High bug risk detected. Increase test coverage and consider code review.")
        
        return recommendations
    
    def _identify_risk_areas(self, assessment: Dict[str, Any]) -> List[str]:
        """Identify high-risk areas in the code"""
        risk_areas = []
        
        if assessment['complexity_score'] < 40:
            risk_areas.append("High cyclomatic complexity")
        
        if assessment['security_score'] < 60:
            risk_areas.append("Security vulnerabilities")
        
        if assessment['maintainability_score'] < 50:
            risk_areas.append("Poor maintainability")
        
        bug_pred = assessment.get('bug_prediction', {})
        if bug_pred.get('probability', 0) > 0.7:
            risk_areas.append("High bug probability")
        
        return risk_areas
    
    def _calculate_confidence_scores(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for predictions"""
        # Base confidence on code analysis completeness
        base_confidence = 0.8
        
        # Adjust based on code characteristics
        if features.get('lines_of_code', 0) > 20:
            base_confidence += 0.1
        
        if features.get('function_count', 0) > 0:
            base_confidence += 0.05
        
        return {
            'overall_assessment': min(0.95, base_confidence),
            'bug_prediction': 0.75,
            'security_assessment': 0.70,
            'performance_assessment': 0.65
        }


class AdaptiveTestingStrategist:
    """Dynamic test strategy optimization"""
    
    def __init__(self):
        self.strategy_library = {
            'unit_heavy': {
                'description': 'Unit test focused strategy for stable APIs',
                'distribution': {'unit': 0.70, 'integration': 0.20, 'e2e': 0.10},
                'suitable_for': ['libraries', 'apis', 'utilities'],
                'focus': 'speed_and_coverage'
            },
            'integration_focused': {
                'description': 'Integration heavy for complex systems',
                'distribution': {'unit': 0.40, 'integration': 0.50, 'e2e': 0.10},
                'suitable_for': ['microservices', 'distributed_systems'],
                'focus': 'system_reliability'
            },
            'user_journey': {
                'description': 'E2E focused for user-facing applications',
                'distribution': {'unit': 0.30, 'integration': 0.30, 'e2e': 0.40},
                'suitable_for': ['web_apps', 'mobile_apps', 'ui'],
                'focus': 'user_experience'
            },
            'risk_based': {
                'description': 'Risk-based testing for critical systems',
                'distribution': {'unit': 0.50, 'integration': 0.30, 'e2e': 0.20},
                'suitable_for': ['financial', 'healthcare', 'safety_critical'],
                'focus': 'risk_mitigation'
            }
        }
        
        self.effectiveness_history = []
    
    async def optimize_strategy(self, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize testing strategy based on project context"""
        try:
            logger.info("Optimizing testing strategy")
            
            # Analyze project characteristics
            project_type = self._analyze_project_type(project_context)
            risk_level = self._assess_risk_level(project_context)
            complexity = self._assess_complexity(project_context)
            
            # Select optimal strategy
            optimal_strategy = self._select_strategy(project_type, risk_level, complexity)
            
            # Customize strategy based on context
            customized_strategy = self._customize_strategy(optimal_strategy, project_context)
            
            # Add optimization recommendations
            optimization_result = {
                'recommended_strategy': customized_strategy,
                'project_analysis': {
                    'type': project_type,
                    'risk_level': risk_level,
                    'complexity': complexity
                },
                'test_distribution': customized_strategy['distribution'],
                'priority_areas': self._identify_priority_areas(project_context),
                'optimization_tips': self._generate_optimization_tips(customized_strategy),
                'estimated_effort_reduction': self._estimate_effort_reduction(customized_strategy),
                'success_metrics': self._define_success_metrics(customized_strategy)
            }
            
            logger.info(f"Strategy optimization completed: {customized_strategy['description']}")
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Error in strategy optimization: {e}")
            return {
                'error': str(e),
                'recommended_strategy': self.strategy_library['unit_heavy'],
                'priority_areas': ['error_handling']
            }
    
    def _analyze_project_type(self, context: Dict[str, Any]) -> str:
        """Analyze project type from context"""
        code = context.get('code', '')
        features = context.get('features', {})
        
        # Check for web frameworks
        web_indicators = ['flask', 'django', 'fastapi', 'requests', 'http']
        if any(indicator in code.lower() for indicator in web_indicators):
            return 'web_app'
        
        # Check for API patterns
        api_indicators = ['@app.route', 'def get_', 'def post_', 'return jsonify']
        if any(indicator in code for indicator in api_indicators):
            return 'api'
        
        # Check for data processing
        data_indicators = ['pandas', 'numpy', 'dataframe', 'csv', 'json']
        if any(indicator in code.lower() for indicator in data_indicators):
            return 'data_processing'
        
        # Check for library/utility code
        if features.get('function_count', 0) > features.get('class_count', 0) * 2:
            return 'utility'
        
        return 'general'
    
    def _assess_risk_level(self, context: Dict[str, Any]) -> str:
        """Assess risk level of the project"""
        features = context.get('features', {})
        code = context.get('code', '')
        
        risk_score = 0
        
        # High complexity increases risk
        if features.get('cyclomatic_complexity', 0) > 15:
            risk_score += 2
        
        # Security-sensitive code increases risk
        security_keywords = ['password', 'auth', 'login', 'credential', 'token']
        if any(keyword in code.lower() for keyword in security_keywords):
            risk_score += 2
        
        # Database operations increase risk
        db_keywords = ['database', 'sql', 'query', 'transaction']
        if any(keyword in code.lower() for keyword in db_keywords):
            risk_score += 1
        
        # Poor documentation increases risk
        if features.get('comment_ratio', 0) < 0.1:
            risk_score += 1
        
        if risk_score >= 4:
            return 'high'
        elif risk_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _assess_complexity(self, context: Dict[str, Any]) -> str:
        """Assess complexity level"""
        features = context.get('features', {})
        
        complexity_score = 0
        
        # Cyclomatic complexity
        if features.get('cyclomatic_complexity', 0) > 20:
            complexity_score += 3
        elif features.get('cyclomatic_complexity', 0) > 10:
            complexity_score += 2
        elif features.get('cyclomatic_complexity', 0) > 5:
            complexity_score += 1
        
        # Code size
        if features.get('lines_of_code', 0) > 500:
            complexity_score += 2
        elif features.get('lines_of_code', 0) > 200:
            complexity_score += 1
        
        # Nesting depth
        if features.get('nested_depth', 0) > 5:
            complexity_score += 2
        elif features.get('nested_depth', 0) > 3:
            complexity_score += 1
        
        if complexity_score >= 5:
            return 'high'
        elif complexity_score >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _select_strategy(self, project_type: str, risk_level: str, complexity: str) -> Dict[str, Any]:
        """Select optimal testing strategy"""
        # Strategy selection logic
        if risk_level == 'high':
            return self.strategy_library['risk_based']
        
        if project_type in ['web_app', 'mobile_app']:
            return self.strategy_library['user_journey']
        
        if project_type in ['microservices', 'distributed_system']:
            return self.strategy_library['integration_focused']
        
        if project_type in ['api', 'utility', 'library']:
            return self.strategy_library['unit_heavy']
        
        # Default strategy
        return self.strategy_library['unit_heavy']
    
    def _customize_strategy(self, base_strategy: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Customize strategy based on specific project needs"""
        customized = base_strategy.copy()
        features = context.get('features', {})
        
        # Adjust distribution based on complexity
        if features.get('cyclomatic_complexity', 0) > 15:
            # Increase unit test ratio for complex code
            dist = customized['distribution'].copy()
            dist['unit'] = min(0.8, dist['unit'] + 0.1)
            dist['integration'] = max(0.1, dist['integration'] - 0.05)
            dist['e2e'] = max(0.1, dist['e2e'] - 0.05)
            customized['distribution'] = dist
        
        return customized
    
    def _identify_priority_areas(self, context: Dict[str, Any]) -> List[str]:
        """Identify priority testing areas"""
        priority_areas = []
        features = context.get('features', {})
        code = context.get('code', '')
        
        # High complexity areas
        if features.get('cyclomatic_complexity', 0) > 10:
            priority_areas.append('complex_logic_paths')
        
        # Error handling
        if features.get('exception_handling', 0) == 0:
            priority_areas.append('error_handling')
        
        # Security-sensitive areas
        if any(keyword in code.lower() for keyword in ['auth', 'password', 'token']):
            priority_areas.append('security_validation')
        
        # Data processing
        if any(keyword in code.lower() for keyword in ['parse', 'validate', 'transform']):
            priority_areas.append('data_validation')
        
        # Performance-critical areas
        if any(keyword in code.lower() for keyword in ['loop', 'recursive', 'algorithm']):
            priority_areas.append('performance_optimization')
        
        return priority_areas or ['basic_functionality']
    
    def _generate_optimization_tips(self, strategy: Dict[str, Any]) -> List[str]:
        """Generate testing optimization tips"""
        tips = [
            f"Focus on {strategy['focus']} based on your project type",
            f"Follow the {strategy['distribution']['unit']:.0%}-{strategy['distribution']['integration']:.0%}-{strategy['distribution']['e2e']:.0%} test distribution"
        ]
        
        if strategy['distribution']['unit'] > 0.6:
            tips.append("Prioritize fast unit tests for quick feedback")
        
        if strategy['distribution']['integration'] > 0.4:
            tips.append("Invest in robust integration test infrastructure")
        
        if strategy['distribution']['e2e'] > 0.3:
            tips.append("Implement reliable E2E test automation")
        
        tips.extend([
            "Use test doubles (mocks/stubs) to isolate units",
            "Implement continuous testing in your CI/CD pipeline",
            "Monitor test execution time and optimize slow tests",
            "Maintain test code quality with the same standards as production code"
        ])
        
        return tips
    
    def _estimate_effort_reduction(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate effort reduction from optimized strategy"""
        # Baseline effort reduction based on strategy type
        base_reduction = {
            'unit_heavy': 0.6,
            'integration_focused': 0.4,
            'user_journey': 0.3,
            'risk_based': 0.5
        }
        
        strategy_name = strategy.get('description', '').split()[0].lower() + '_heavy'
        if 'integration' in strategy.get('description', '').lower():
            strategy_name = 'integration_focused'
        elif 'user' in strategy.get('description', '').lower():
            strategy_name = 'user_journey'
        elif 'risk' in strategy.get('description', '').lower():
            strategy_name = 'risk_based'
        
        reduction_percentage = base_reduction.get(strategy_name, 0.4)
        
        return {
            'testing_effort_reduction': f"{reduction_percentage:.0%}",
            'time_savings_per_cycle': f"{reduction_percentage * 40:.0f} hours",
            'annual_savings_estimate': f"{reduction_percentage * 40 * 26:.0f} hours"  # 26 cycles per year
        }
    
    def _define_success_metrics(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Define success metrics for the testing strategy"""
        return {
            'coverage_target': '95%',
            'defect_escape_rate': '<5%',
            'test_execution_time': '<30 minutes',
            'test_maintenance_effort': '<20% of development time',
            'false_positive_rate': '<2%',
            'bug_detection_rate': '>90%'
        }


class MLTestingQAServer:
    """Main ML Testing QA MCP Server"""
    
    def __init__(self):
        self.test_generator = IntelligentTestGenerator()
        self.quality_predictor = QualityPredictor()
        self.testing_strategist = AdaptiveTestingStrategist()
        
        # Performance tracking
        self.performance_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'average_response_time': 0,
            'last_request_time': None
        }
    
    async def handle_test_generation(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle test generation requests"""
        start_time = datetime.now()
        
        try:
            code = request.get('code', '')
            context = request.get('context', {})
            
            if not code:
                return {'error': 'No code provided for test generation'}
            
            # Generate tests
            tests = await self.test_generator.generate_tests(code, context)
            
            # Add generation metadata
            tests['request_metadata'] = {
                'timestamp': start_time.isoformat(),
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'code_length': len(code),
                'context_provided': bool(context)
            }
            
            self._update_performance_metrics(True, start_time)
            
            return tests
            
        except Exception as e:
            logger.error(f"Error in test generation: {e}")
            self._update_performance_metrics(False, start_time)
            return {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': start_time.isoformat()
            }
    
    async def handle_quality_prediction(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle quality prediction requests"""
        start_time = datetime.now()
        
        try:
            code = request.get('code', '')
            context = request.get('context', {})
            
            if not code:
                return {'error': 'No code provided for quality prediction'}
            
            # Predict quality
            quality_assessment = await self.quality_predictor.predict_quality(code, context)
            
            # Add prediction metadata
            quality_assessment['request_metadata'] = {
                'timestamp': start_time.isoformat(),
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'code_length': len(code),
                'context_provided': bool(context)
            }
            
            self._update_performance_metrics(True, start_time)
            
            return quality_assessment
            
        except Exception as e:
            logger.error(f"Error in quality prediction: {e}")
            self._update_performance_metrics(False, start_time)
            return {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': start_time.isoformat()
            }
    
    async def handle_strategy_optimization(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle testing strategy optimization requests"""
        start_time = datetime.now()
        
        try:
            project_context = request.get('project_context', {})
            
            # If code is provided, extract features for context
            if 'code' in request:
                features = self.test_generator.feature_extractor.extract_features(request['code'])
                project_context['features'] = features
                project_context['code'] = request['code']
            
            # Optimize strategy
            optimization_result = await self.testing_strategist.optimize_strategy(project_context)
            
            # Add optimization metadata
            optimization_result['request_metadata'] = {
                'timestamp': start_time.isoformat(),
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'context_provided': bool(project_context)
            }
            
            self._update_performance_metrics(True, start_time)
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Error in strategy optimization: {e}")
            self._update_performance_metrics(False, start_time)
            return {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': start_time.isoformat()
            }
    
    async def handle_comprehensive_analysis(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle comprehensive analysis combining all capabilities"""
        start_time = datetime.now()
        
        try:
            code = request.get('code', '')
            context = request.get('context', {})
            
            if not code:
                return {'error': 'No code provided for comprehensive analysis'}
            
            # Run all analyses in parallel
            test_generation_task = self.handle_test_generation({'code': code, 'context': context})
            quality_prediction_task = self.handle_quality_prediction({'code': code, 'context': context})
            strategy_optimization_task = self.handle_strategy_optimization({
                'code': code,
                'project_context': context
            })
            
            # Wait for all tasks to complete
            test_results, quality_results, strategy_results = await asyncio.gather(
                test_generation_task,
                quality_prediction_task,
                strategy_optimization_task,
                return_exceptions=True
            )
            
            # Combine results
            comprehensive_analysis = {
                'test_generation': test_results if not isinstance(test_results, Exception) else {'error': str(test_results)},
                'quality_prediction': quality_results if not isinstance(quality_results, Exception) else {'error': str(quality_results)},
                'strategy_optimization': strategy_results if not isinstance(strategy_results, Exception) else {'error': str(strategy_results)},
                'comprehensive_summary': self._generate_comprehensive_summary(
                    test_results, quality_results, strategy_results
                ),
                'request_metadata': {
                    'timestamp': start_time.isoformat(),
                    'processing_time': (datetime.now() - start_time).total_seconds(),
                    'code_length': len(code),
                    'analysis_type': 'comprehensive'
                }
            }
            
            self._update_performance_metrics(True, start_time)
            
            return comprehensive_analysis
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            self._update_performance_metrics(False, start_time)
            return {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': start_time.isoformat()
            }
    
    def _generate_comprehensive_summary(self, test_results, quality_results, strategy_results) -> Dict[str, Any]:
        """Generate a comprehensive summary of all analyses"""
        summary = {
            'overall_assessment': 'unknown',
            'key_recommendations': [],
            'priority_actions': [],
            'risk_level': 'medium',
            'estimated_effort': 'medium'
        }
        
        try:
            # Extract key metrics
            if isinstance(quality_results, dict) and 'overall_quality_score' in quality_results:
                quality_score = quality_results['overall_quality_score']
                
                if quality_score >= 80:
                    summary['overall_assessment'] = 'excellent'
                elif quality_score >= 60:
                    summary['overall_assessment'] = 'good'
                elif quality_score >= 40:
                    summary['overall_assessment'] = 'fair'
                else:
                    summary['overall_assessment'] = 'poor'
            
            # Combine recommendations
            if isinstance(quality_results, dict) and 'recommendations' in quality_results:
                summary['key_recommendations'].extend(quality_results['recommendations'])
            
            if isinstance(strategy_results, dict) and 'optimization_tips' in strategy_results:
                summary['key_recommendations'].extend(strategy_results['optimization_tips'][:3])  # Top 3
            
            # Determine priority actions
            if isinstance(quality_results, dict) and 'risk_areas' in quality_results:
                for risk_area in quality_results['risk_areas']:
                    summary['priority_actions'].append(f"Address {risk_area}")
            
            if isinstance(test_results, dict) and 'coverage_estimate' in test_results:
                coverage = test_results['coverage_estimate']
                if coverage < 80:
                    summary['priority_actions'].append("Increase test coverage")
            
            # Assess overall risk
            risk_indicators = 0
            if isinstance(quality_results, dict):
                if quality_results.get('overall_quality_score', 100) < 60:
                    risk_indicators += 1
                if quality_results.get('security_score', 100) < 70:
                    risk_indicators += 1
                bug_pred = quality_results.get('bug_prediction', {})
                if bug_pred.get('risk_level') == 'high':
                    risk_indicators += 1
            
            if risk_indicators >= 2:
                summary['risk_level'] = 'high'
            elif risk_indicators == 1:
                summary['risk_level'] = 'medium'
            else:
                summary['risk_level'] = 'low'
            
            # Estimate effort based on recommendations
            rec_count = len(summary['key_recommendations']) + len(summary['priority_actions'])
            if rec_count <= 3:
                summary['estimated_effort'] = 'low'
            elif rec_count <= 6:
                summary['estimated_effort'] = 'medium'
            else:
                summary['estimated_effort'] = 'high'
            
        except Exception as e:
            logger.warning(f"Error generating comprehensive summary: {e}")
            summary['error'] = f"Summary generation error: {e}"
        
        return summary
    
    def _update_performance_metrics(self, success: bool, start_time: datetime):
        """Update performance tracking metrics"""
        self.performance_metrics['total_requests'] += 1
        if success:
            self.performance_metrics['successful_requests'] += 1
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Update average response time
        if self.performance_metrics['average_response_time'] == 0:
            self.performance_metrics['average_response_time'] = processing_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.performance_metrics['average_response_time'] = (
                alpha * processing_time +
                (1 - alpha) * self.performance_metrics['average_response_time']
            )
        
        self.performance_metrics['last_request_time'] = datetime.now().isoformat()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        success_rate = 0
        if self.performance_metrics['total_requests'] > 0:
            success_rate = (
                self.performance_metrics['successful_requests'] /
                self.performance_metrics['total_requests']
            ) * 100
        
        return {
            **self.performance_metrics,
            'success_rate_percentage': round(success_rate, 2),
            'average_response_time_ms': round(self.performance_metrics['average_response_time'] * 1000, 2)
        }


# Initialize the main server instance
ml_testing_qa_server = MLTestingQAServer()


# MCP Server Tool Definitions
@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available ML Testing QA tools"""
    return [
        Tool(
            name="generate_intelligent_tests",
            description="Generate comprehensive test suites with AI-powered edge case discovery",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Source code to generate tests for"
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context for test generation",
                        "properties": {
                            "test_framework": {"type": "string", "default": "pytest"},
                            "coverage_target": {"type": "number", "default": 95},
                            "include_performance_tests": {"type": "boolean", "default": True},
                            "include_security_tests": {"type": "boolean", "default": True}
                        }
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="predict_code_quality",
            description="Predict code quality and bug probability using ML models",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Source code to analyze for quality prediction"
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context for quality analysis",
                        "properties": {
                            "project_type": {"type": "string"},
                            "team_size": {"type": "number"},
                            "criticality": {"type": "string", "enum": ["low", "medium", "high"]}
                        }
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="optimize_testing_strategy",
            description="Optimize testing strategy using adaptive ML algorithms",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_context": {
                        "type": "object",
                        "description": "Project context for strategy optimization",
                        "properties": {
                            "project_type": {"type": "string"},
                            "team_size": {"type": "number"},
                            "release_cycle": {"type": "string"},
                            "risk_tolerance": {"type": "string", "enum": ["low", "medium", "high"]},
                            "budget_constraints": {"type": "string"}
                        }
                    },
                    "code": {
                        "type": "string",
                        "description": "Optional: Source code for analysis"
                    }
                },
                "required": ["project_context"]
            }
        ),
        Tool(
            name="comprehensive_testing_analysis",
            description="Perform comprehensive testing analysis combining all ML capabilities",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Source code for comprehensive analysis"
                    },
                    "context": {
                        "type": "object",
                        "description": "Project and analysis context",
                        "properties": {
                            "project_type": {"type": "string"},
                            "test_framework": {"type": "string", "default": "pytest"},
                            "coverage_target": {"type": "number", "default": 95},
                            "team_size": {"type": "number"},
                            "criticality": {"type": "string", "enum": ["low", "medium", "high"]}
                        }
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="get_server_metrics",
            description="Get ML Testing QA server performance metrics and statistics",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls"""
    try:
        if name == "generate_intelligent_tests":
            result = await ml_testing_qa_server.handle_test_generation(arguments)
            
        elif name == "predict_code_quality":
            result = await ml_testing_qa_server.handle_quality_prediction(arguments)
            
        elif name == "optimize_testing_strategy":
            result = await ml_testing_qa_server.handle_strategy_optimization(arguments)
            
        elif name == "comprehensive_testing_analysis":
            result = await ml_testing_qa_server.handle_comprehensive_analysis(arguments)
            
        elif name == "get_server_metrics":
            result = ml_testing_qa_server.get_performance_metrics()
            
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
        
    except Exception as e:
        logger.error(f"Error in tool call {name}: {e}")
        error_result = {
            "error": str(e),
            "tool": name,
            "traceback": traceback.format_exc()
        }
        return [TextContent(
            type="text",
            text=json.dumps(error_result, indent=2)
        )]


async def main():
    """Main server entry point"""
    logger.info("Starting ML Testing QA MCP Server")
    
    # Server configuration - create proper capability objects
    from mcp.types import ServerCapabilities, ToolsCapability, LoggingCapability
    
    capabilities = ServerCapabilities(
        tools=ToolsCapability(),
        logging=LoggingCapability()
    )
    
    options = InitializationOptions(
        server_name="ml-testing-qa",
        server_version="1.0.0",
        capabilities=capabilities
    )
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                options
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    logger.info("ML Testing QA MCP Server starting...")
    asyncio.run(main())
