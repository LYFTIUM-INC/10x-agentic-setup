"""
Quality Assessment Tools for Code Intelligence
ML-enhanced code quality scoring, technical debt analysis, and improvement recommendations
"""

import ast
import re
import logging
import time
import math
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict, Counter
from enum import Enum

logger = logging.getLogger(__name__)


class QualityCategory(Enum):
    """Quality assessment categories"""
    MAINTAINABILITY = "maintainability"
    RELIABILITY = "reliability"
    SECURITY = "security"
    PERFORMANCE = "performance"
    READABILITY = "readability"
    TESTABILITY = "testability"


@dataclass
class QualityMetric:
    """Quality metric with score and weight"""
    name: str
    score: float  # 0-100
    weight: float  # 0-1
    category: QualityCategory
    description: str
    evidence: List[str]
    improvement_suggestions: List[str]


@dataclass
class QualityReport:
    """Comprehensive quality assessment report"""
    overall_score: float
    category_scores: Dict[str, float]
    metrics: List[QualityMetric]
    technical_debt_ratio: float
    maintainability_index: float
    quality_trends: Dict[str, Any]
    improvement_priorities: List[Dict[str, Any]]


class CodeQualityAnalyzer:
    """ML-enhanced code quality analyzer"""
    
    def __init__(self):
        self.security_patterns = self._load_security_patterns()
        self.performance_patterns = self._load_performance_patterns()
        self.maintainability_weights = {
            'complexity': 0.25,
            'documentation': 0.20,
            'naming': 0.15,
            'structure': 0.20,
            'duplication': 0.20
        }
    
    def assess_quality(self, code: str, language: str = "python", 
                      include_trends: bool = False) -> QualityReport:
        """Comprehensive quality assessment"""
        try:
            if language.lower() != "python":
                return self._assess_general_quality(code, language)
            
            tree = ast.parse(code)
            
            # Calculate individual metrics
            metrics = []
            
            # Maintainability metrics
            metrics.extend(self._assess_maintainability(code, tree))
            
            # Reliability metrics
            metrics.extend(self._assess_reliability(code, tree))
            
            # Security metrics
            metrics.extend(self._assess_security(code, tree))
            
            # Performance metrics
            metrics.extend(self._assess_performance(code, tree))
            
            # Readability metrics
            metrics.extend(self._assess_readability(code, tree))
            
            # Testability metrics
            metrics.extend(self._assess_testability(code, tree))
            
            # Calculate category scores
            category_scores = self._calculate_category_scores(metrics)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(category_scores)
            
            # Calculate technical debt
            technical_debt = self._calculate_technical_debt(metrics)
            
            # Calculate maintainability index
            maintainability = self._calculate_maintainability_index(code, tree)
            
            # Generate improvement priorities
            priorities = self._generate_improvement_priorities(metrics)
            
            # Calculate trends (if historical data available)
            trends = self._calculate_trends(metrics) if include_trends else {}
            
            return QualityReport(
                overall_score=overall_score,
                category_scores=category_scores,
                metrics=metrics,
                technical_debt_ratio=technical_debt,
                maintainability_index=maintainability,
                quality_trends=trends,
                improvement_priorities=priorities
            )
            
        except SyntaxError as e:
            logger.error(f"Syntax error in quality assessment: {e}")
            return self._create_error_report(f"Syntax error: {e}")
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return self._create_error_report(f"Assessment failed: {e}")
    
    def _assess_maintainability(self, code: str, tree: ast.AST) -> List[QualityMetric]:
        """Assess code maintainability"""
        metrics = []
        
        # Complexity metric
        complexity_score = self._calculate_complexity_score(tree)
        metrics.append(QualityMetric(
            name="Cyclomatic Complexity",
            score=complexity_score,
            weight=0.25,
            category=QualityCategory.MAINTAINABILITY,
            description="Measures code complexity based on control flow",
            evidence=self._get_complexity_evidence(tree),
            improvement_suggestions=self._get_complexity_suggestions(tree)
        ))
        
        # Documentation metric
        doc_score = self._calculate_documentation_score(tree)
        metrics.append(QualityMetric(
            name="Documentation Quality",
            score=doc_score,
            weight=0.20,
            category=QualityCategory.MAINTAINABILITY,
            description="Measures quality and completeness of documentation",
            evidence=self._get_documentation_evidence(tree),
            improvement_suggestions=self._get_documentation_suggestions(tree)
        ))
        
        # Naming metric
        naming_score = self._calculate_naming_score(tree)
        metrics.append(QualityMetric(
            name="Naming Convention",
            score=naming_score,
            weight=0.15,
            category=QualityCategory.MAINTAINABILITY,
            description="Measures adherence to naming conventions",
            evidence=self._get_naming_evidence(tree),
            improvement_suggestions=self._get_naming_suggestions(tree)
        ))
        
        # Structure metric
        structure_score = self._calculate_structure_score(tree)
        metrics.append(QualityMetric(
            name="Code Structure",
            score=structure_score,
            weight=0.20,
            category=QualityCategory.MAINTAINABILITY,
            description="Measures code organization and structure",
            evidence=self._get_structure_evidence(tree),
            improvement_suggestions=self._get_structure_suggestions(tree)
        ))
        
        # Duplication metric
        duplication_score = self._calculate_duplication_score(tree)
        metrics.append(QualityMetric(
            name="Code Duplication",
            score=duplication_score,
            weight=0.20,
            category=QualityCategory.MAINTAINABILITY,
            description="Measures amount of duplicated code",
            evidence=self._get_duplication_evidence(tree),
            improvement_suggestions=self._get_duplication_suggestions(tree)
        ))
        
        return metrics
    
    def _assess_reliability(self, code: str, tree: ast.AST) -> List[QualityMetric]:
        """Assess code reliability"""
        metrics = []
        
        # Error handling metric
        error_handling_score = self._calculate_error_handling_score(tree)
        metrics.append(QualityMetric(
            name="Error Handling",
            score=error_handling_score,
            weight=0.30,
            category=QualityCategory.RELIABILITY,
            description="Measures quality of error handling",
            evidence=self._get_error_handling_evidence(tree),
            improvement_suggestions=self._get_error_handling_suggestions(tree)
        ))
        
        # Null safety metric
        null_safety_score = self._calculate_null_safety_score(tree)
        metrics.append(QualityMetric(
            name="Null Safety",
            score=null_safety_score,
            weight=0.25,
            category=QualityCategory.RELIABILITY,
            description="Measures protection against null/None errors",
            evidence=self._get_null_safety_evidence(tree),
            improvement_suggestions=self._get_null_safety_suggestions(tree)
        ))
        
        # Resource management metric
        resource_score = self._calculate_resource_management_score(tree)
        metrics.append(QualityMetric(
            name="Resource Management",
            score=resource_score,
            weight=0.20,
            category=QualityCategory.RELIABILITY,
            description="Measures proper resource handling",
            evidence=self._get_resource_evidence(tree),
            improvement_suggestions=self._get_resource_suggestions(tree)
        ))
        
        # Type safety metric
        type_safety_score = self._calculate_type_safety_score(tree)
        metrics.append(QualityMetric(
            name="Type Safety",
            score=type_safety_score,
            weight=0.25,
            category=QualityCategory.RELIABILITY,
            description="Measures type annotation usage",
            evidence=self._get_type_safety_evidence(tree),
            improvement_suggestions=self._get_type_safety_suggestions(tree)
        ))
        
        return metrics
    
    def _assess_security(self, code: str, tree: ast.AST) -> List[QualityMetric]:
        """Assess code security"""
        metrics = []
        
        # Dangerous functions metric
        dangerous_functions_score = self._calculate_dangerous_functions_score(tree)
        metrics.append(QualityMetric(
            name="Dangerous Functions",
            score=dangerous_functions_score,
            weight=0.30,
            category=QualityCategory.SECURITY,
            description="Checks for potentially dangerous function usage",
            evidence=self._get_dangerous_functions_evidence(tree),
            improvement_suggestions=self._get_dangerous_functions_suggestions(tree)
        ))
        
        # Input validation metric
        input_validation_score = self._calculate_input_validation_score(tree)
        metrics.append(QualityMetric(
            name="Input Validation",
            score=input_validation_score,
            weight=0.25,
            category=QualityCategory.SECURITY,
            description="Measures input validation practices",
            evidence=self._get_input_validation_evidence(tree),
            improvement_suggestions=self._get_input_validation_suggestions(tree)
        ))
        
        # Secrets handling metric
        secrets_score = self._calculate_secrets_handling_score(code, tree)
        metrics.append(QualityMetric(
            name="Secrets Handling",
            score=secrets_score,
            weight=0.25,
            category=QualityCategory.SECURITY,
            description="Checks for hardcoded secrets and credentials",
            evidence=self._get_secrets_evidence(code, tree),
            improvement_suggestions=self._get_secrets_suggestions(tree)
        ))
        
        # SQL injection metric
        sql_injection_score = self._calculate_sql_injection_score(tree)
        metrics.append(QualityMetric(
            name="SQL Injection Protection",
            score=sql_injection_score,
            weight=0.20,
            category=QualityCategory.SECURITY,
            description="Checks for SQL injection vulnerabilities",
            evidence=self._get_sql_injection_evidence(tree),
            improvement_suggestions=self._get_sql_injection_suggestions(tree)
        ))
        
        return metrics
    
    def _assess_performance(self, code: str, tree: ast.AST) -> List[QualityMetric]:
        """Assess code performance"""
        metrics = []
        
        # Algorithmic efficiency metric
        efficiency_score = self._calculate_algorithmic_efficiency_score(tree)
        metrics.append(QualityMetric(
            name="Algorithmic Efficiency",
            score=efficiency_score,
            weight=0.30,
            category=QualityCategory.PERFORMANCE,
            description="Measures algorithmic complexity and efficiency",
            evidence=self._get_efficiency_evidence(tree),
            improvement_suggestions=self._get_efficiency_suggestions(tree)
        ))
        
        # Memory usage metric
        memory_score = self._calculate_memory_usage_score(tree)
        metrics.append(QualityMetric(
            name="Memory Usage",
            score=memory_score,
            weight=0.25,
            category=QualityCategory.PERFORMANCE,
            description="Measures memory efficiency",
            evidence=self._get_memory_evidence(tree),
            improvement_suggestions=self._get_memory_suggestions(tree)
        ))
        
        # I/O efficiency metric
        io_score = self._calculate_io_efficiency_score(tree)
        metrics.append(QualityMetric(
            name="I/O Efficiency",
            score=io_score,
            weight=0.25,
            category=QualityCategory.PERFORMANCE,
            description="Measures I/O operation efficiency",
            evidence=self._get_io_evidence(tree),
            improvement_suggestions=self._get_io_suggestions(tree)
        ))
        
        # Caching metric
        caching_score = self._calculate_caching_score(tree)
        metrics.append(QualityMetric(
            name="Caching Strategy",
            score=caching_score,
            weight=0.20,
            category=QualityCategory.PERFORMANCE,
            description="Measures caching implementation",
            evidence=self._get_caching_evidence(tree),
            improvement_suggestions=self._get_caching_suggestions(tree)
        ))
        
        return metrics
    
    def _assess_readability(self, code: str, tree: ast.AST) -> List[QualityMetric]:
        """Assess code readability"""
        metrics = []
        
        # Line length metric
        line_length_score = self._calculate_line_length_score(code)
        metrics.append(QualityMetric(
            name="Line Length",
            score=line_length_score,
            weight=0.20,
            category=QualityCategory.READABILITY,
            description="Measures adherence to line length standards",
            evidence=self._get_line_length_evidence(code),
            improvement_suggestions=self._get_line_length_suggestions(code)
        ))
        
        # Comments quality metric
        comments_score = self._calculate_comments_quality_score(code)
        metrics.append(QualityMetric(
            name="Comments Quality",
            score=comments_score,
            weight=0.25,
            category=QualityCategory.READABILITY,
            description="Measures quality and helpfulness of comments",
            evidence=self._get_comments_evidence(code),
            improvement_suggestions=self._get_comments_suggestions(code)
        ))
        
        # Code formatting metric
        formatting_score = self._calculate_formatting_score(code)
        metrics.append(QualityMetric(
            name="Code Formatting",
            score=formatting_score,
            weight=0.30,
            category=QualityCategory.READABILITY,
            description="Measures adherence to formatting standards",
            evidence=self._get_formatting_evidence(code),
            improvement_suggestions=self._get_formatting_suggestions(code)
        ))
        
        # Function size metric
        function_size_score = self._calculate_function_size_score(tree)
        metrics.append(QualityMetric(
            name="Function Size",
            score=function_size_score,
            weight=0.25,
            category=QualityCategory.READABILITY,
            description="Measures function size and complexity",
            evidence=self._get_function_size_evidence(tree),
            improvement_suggestions=self._get_function_size_suggestions(tree)
        ))
        
        return metrics
    
    def _assess_testability(self, code: str, tree: ast.AST) -> List[QualityMetric]:
        """Assess code testability"""
        metrics = []
        
        # Function isolation metric
        isolation_score = self._calculate_function_isolation_score(tree)
        metrics.append(QualityMetric(
            name="Function Isolation",
            score=isolation_score,
            weight=0.30,
            category=QualityCategory.TESTABILITY,
            description="Measures how well functions can be tested in isolation",
            evidence=self._get_isolation_evidence(tree),
            improvement_suggestions=self._get_isolation_suggestions(tree)
        ))
        
        # Dependency injection metric
        dependency_injection_score = self._calculate_dependency_injection_score(tree)
        metrics.append(QualityMetric(
            name="Dependency Injection",
            score=dependency_injection_score,
            weight=0.25,
            category=QualityCategory.TESTABILITY,
            description="Measures use of dependency injection for testability",
            evidence=self._get_dependency_injection_evidence(tree),
            improvement_suggestions=self._get_dependency_injection_suggestions(tree)
        ))
        
        # Test coverage potential metric
        coverage_potential_score = self._calculate_coverage_potential_score(tree)
        metrics.append(QualityMetric(
            name="Test Coverage Potential",
            score=coverage_potential_score,
            weight=0.25,
            category=QualityCategory.TESTABILITY,
            description="Measures how easily code can achieve high test coverage",
            evidence=self._get_coverage_potential_evidence(tree),
            improvement_suggestions=self._get_coverage_potential_suggestions(tree)
        ))
        
        # Mock-ability metric
        mockability_score = self._calculate_mockability_score(tree)
        metrics.append(QualityMetric(
            name="Mock-ability",
            score=mockability_score,
            weight=0.20,
            category=QualityCategory.TESTABILITY,
            description="Measures how easily external dependencies can be mocked",
            evidence=self._get_mockability_evidence(tree),
            improvement_suggestions=self._get_mockability_suggestions(tree)
        ))
        
        return metrics
    
    # Implementation of scoring methods (simplified for brevity)
    def _calculate_complexity_score(self, tree: ast.AST) -> float:
        """Calculate complexity score (0-100, higher is better)"""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
        
        # Convert to score (lower complexity = higher score)
        if complexity <= 5:
            return 100.0
        elif complexity <= 10:
            return 80.0
        elif complexity <= 15:
            return 60.0
        elif complexity <= 20:
            return 40.0
        else:
            return 20.0
    
    def _calculate_documentation_score(self, tree: ast.AST) -> float:
        """Calculate documentation score"""
        documented_functions = 0
        total_functions = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                if (node.body and isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)):
                    documented_functions += 1
        
        if total_functions == 0:
            return 100.0
        
        return (documented_functions / total_functions) * 100.0
    
    def _calculate_naming_score(self, tree: ast.AST) -> float:
        """Calculate naming convention score"""
        score = 100.0
        violations = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not self._is_snake_case(node.name):
                    violations += 1
            elif isinstance(node, ast.ClassDef):
                if not self._is_pascal_case(node.name):
                    violations += 1
        
        # Deduct points for violations
        score -= violations * 10
        return max(0.0, score)
    
    def _is_snake_case(self, name: str) -> bool:
        """Check if name follows snake_case convention"""
        return re.match(r'^[a-z][a-z0-9_]*$', name) is not None
    
    def _is_pascal_case(self, name: str) -> bool:
        """Check if name follows PascalCase convention"""
        return re.match(r'^[A-Z][a-zA-Z0-9]*$', name) is not None
    
    def _calculate_structure_score(self, tree: ast.AST) -> float:
        """Calculate code structure score"""
        # Simple heuristic: penalize deeply nested code
        max_depth = 0
        
        def get_depth(node, depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, depth)
            
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                    get_depth(child, depth + 1)
                else:
                    get_depth(child, depth)
        
        get_depth(tree)
        
        if max_depth <= 3:
            return 100.0
        elif max_depth <= 5:
            return 80.0
        elif max_depth <= 7:
            return 60.0
        else:
            return 40.0
    
    def _calculate_duplication_score(self, tree: ast.AST) -> float:
        """Calculate code duplication score"""
        # Simplified: look for similar function patterns
        function_signatures = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                signature = (len(node.args.args), len(node.body))
                function_signatures.append(signature)
        
        if not function_signatures:
            return 100.0
        
        duplicates = len(function_signatures) - len(set(function_signatures))
        duplication_ratio = duplicates / len(function_signatures)
        
        return max(0.0, 100.0 - duplication_ratio * 100.0)
    
    # Error handling assessment methods
    def _calculate_error_handling_score(self, tree: ast.AST) -> float:
        """Calculate error handling score"""
        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        try_blocks = [n for n in ast.walk(tree) if isinstance(n, ast.Try)]
        
        if not functions:
            return 100.0
        
        # Heuristic: expect at least one try block for every 3 functions
        expected_try_blocks = len(functions) // 3
        if len(try_blocks) >= expected_try_blocks:
            return 100.0
        else:
            return (len(try_blocks) / max(1, expected_try_blocks)) * 100.0
    
    def _calculate_null_safety_score(self, tree: ast.AST) -> float:
        """Calculate null safety score"""
        # Look for None checks
        none_checks = 0
        comparisons = [n for n in ast.walk(tree) if isinstance(n, ast.Compare)]
        
        for comp in comparisons:
            if (isinstance(comp.left, ast.Constant) and comp.left.value is None) or \
               any(isinstance(c, ast.Constant) and c.value is None for c in comp.comparators):
                none_checks += 1
        
        # Heuristic scoring
        if none_checks >= 3:
            return 100.0
        elif none_checks >= 1:
            return 70.0
        else:
            return 50.0
    
    def _calculate_resource_management_score(self, tree: ast.AST) -> float:
        """Calculate resource management score"""
        # Look for 'with' statements for resource management
        with_statements = [n for n in ast.walk(tree) if isinstance(n, ast.With)]
        file_operations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ['open', 'connect', 'acquire']:
                    file_operations.append(node)
        
        if not file_operations:
            return 100.0
        
        # Score based on proper resource management
        managed_resources = len(with_statements)
        resource_score = min(100.0, (managed_resources / len(file_operations)) * 100.0)
        
        return resource_score
    
    def _calculate_type_safety_score(self, tree: ast.AST) -> float:
        """Calculate type safety score"""
        # Look for type annotations
        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        annotated_functions = 0
        
        for func in functions:
            if func.returns or any(arg.annotation for arg in func.args.args):
                annotated_functions += 1
        
        if not functions:
            return 100.0
        
        return (annotated_functions / len(functions)) * 100.0
    
    # Security assessment methods
    def _calculate_dangerous_functions_score(self, tree: ast.AST) -> float:
        """Calculate dangerous functions score"""
        dangerous_functions = {'eval', 'exec', 'compile', '__import__'}
        violations = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in dangerous_functions:
                    violations += 1
        
        return max(0.0, 100.0 - violations * 30.0)
    
    def _calculate_input_validation_score(self, tree: ast.AST) -> float:
        """Calculate input validation score"""
        # Look for validation patterns
        validations = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Look for validation patterns in if statements
                if self._contains_validation_pattern(node):
                    validations += 1
        
        # Heuristic scoring
        if validations >= 2:
            return 100.0
        elif validations >= 1:
            return 70.0
        else:
            return 50.0
    
    def _contains_validation_pattern(self, node: ast.If) -> bool:
        """Check if an if statement contains validation patterns"""
        # Simplified check for common validation patterns
        if isinstance(node.test, ast.Compare):
            return True
        if isinstance(node.test, ast.UnaryOp) and isinstance(node.test.op, ast.Not):
            return True
        return False
    
    def _calculate_secrets_handling_score(self, code: str, tree: ast.AST) -> float:
        """Calculate secrets handling score"""
        # Look for potential hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        violations = 0
        for pattern in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                violations += 1
        
        return max(0.0, 100.0 - violations * 25.0)
    
    def _calculate_sql_injection_score(self, tree: ast.AST) -> float:
        """Calculate SQL injection protection score"""
        # Look for string formatting in SQL contexts
        sql_operations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in ['execute', 'query', 'select']:
                    sql_operations.append(node)
        
        if not sql_operations:
            return 100.0
        
        # Check for parameterized queries
        safe_operations = 0
        for op in sql_operations:
            if len(op.args) > 1:  # Likely parameterized
                safe_operations += 1
        
        return (safe_operations / len(sql_operations)) * 100.0
    
    # Performance assessment methods
    def _calculate_algorithmic_efficiency_score(self, tree: ast.AST) -> float:
        """Calculate algorithmic efficiency score"""
        # Look for inefficient patterns
        inefficient_patterns = 0
        
        for node in ast.walk(tree):
            # Nested loops
            if isinstance(node, ast.For):
                for child in ast.walk(node):
                    if isinstance(child, ast.For) and child != node:
                        inefficient_patterns += 1
                        break
        
        return max(0.0, 100.0 - inefficient_patterns * 20.0)
    
    def _calculate_memory_usage_score(self, tree: ast.AST) -> float:
        """Calculate memory usage score"""
        # Look for memory-efficient patterns
        list_comprehensions = len([n for n in ast.walk(tree) if isinstance(n, ast.ListComp)])
        generator_expressions = len([n for n in ast.walk(tree) if isinstance(n, ast.GeneratorExp)])
        
        # Bonus for using generators and comprehensions
        efficiency_bonus = (list_comprehensions + generator_expressions) * 10
        
        return min(100.0, 70.0 + efficiency_bonus)
    
    def _calculate_io_efficiency_score(self, tree: ast.AST) -> float:
        """Calculate I/O efficiency score"""
        # Look for batch operations and proper I/O handling
        with_statements = len([n for n in ast.walk(tree) if isinstance(n, ast.With)])
        file_operations = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ['open', 'read', 'write']:
                    file_operations += 1
        
        if file_operations == 0:
            return 100.0
        
        return min(100.0, (with_statements / file_operations) * 100.0)
    
    def _calculate_caching_score(self, tree: ast.AST) -> float:
        """Calculate caching strategy score"""
        # Look for caching patterns
        cache_patterns = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if 'cache' in node.id.lower() or 'memo' in node.id.lower():
                    cache_patterns += 1
        
        return min(100.0, 50.0 + cache_patterns * 15.0)
    
    # Readability assessment methods
    def _calculate_line_length_score(self, code: str) -> float:
        """Calculate line length score"""
        lines = code.split('\n')
        long_lines = [line for line in lines if len(line) > 88]
        
        if not lines:
            return 100.0
        
        return max(0.0, 100.0 - (len(long_lines) / len(lines)) * 100.0)
    
    def _calculate_comments_quality_score(self, code: str) -> float:
        """Calculate comments quality score"""
        lines = code.split('\n')
        comment_lines = [line for line in lines if line.strip().startswith('#')]
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        
        if not code_lines:
            return 100.0
        
        comment_ratio = len(comment_lines) / len(code_lines)
        
        # Optimal comment ratio is around 10-20%
        if 0.1 <= comment_ratio <= 0.2:
            return 100.0
        elif comment_ratio < 0.1:
            return comment_ratio * 1000.0  # Scale up
        else:
            return max(0.0, 100.0 - (comment_ratio - 0.2) * 200.0)
    
    def _calculate_formatting_score(self, code: str) -> float:
        """Calculate formatting score"""
        # Simple heuristics for formatting
        lines = code.split('\n')
        
        # Check for consistent indentation
        indent_violations = 0
        for line in lines:
            if line.strip():
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces % 4 != 0:  # Assume 4-space indentation
                    indent_violations += 1
        
        if not lines:
            return 100.0
        
        return max(0.0, 100.0 - (indent_violations / len(lines)) * 200.0)
    
    def _calculate_function_size_score(self, tree: ast.AST) -> float:
        """Calculate function size score"""
        function_violations = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    func_length = node.end_lineno - node.lineno
                    if func_length > 50:  # Functions should be under 50 lines
                        function_violations += 1
        
        return max(0.0, 100.0 - function_violations * 20.0)
    
    # Testability assessment methods
    def _calculate_function_isolation_score(self, tree: ast.AST) -> float:
        """Calculate function isolation score"""
        # Look for functions with minimal external dependencies
        isolated_functions = 0
        total_functions = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                # Simple heuristic: functions with return statements and parameters
                if node.args.args and any(isinstance(n, ast.Return) for n in ast.walk(node)):
                    isolated_functions += 1
        
        if total_functions == 0:
            return 100.0
        
        return (isolated_functions / total_functions) * 100.0
    
    def _calculate_dependency_injection_score(self, tree: ast.AST) -> float:
        """Calculate dependency injection score"""
        # Look for dependency injection patterns
        di_patterns = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == '__init__':
                # Constructor with dependencies
                if len(node.args.args) > 1:  # More than just 'self'
                    di_patterns += 1
        
        return min(100.0, 50.0 + di_patterns * 25.0)
    
    def _calculate_coverage_potential_score(self, tree: ast.AST) -> float:
        """Calculate test coverage potential score"""
        # Heuristic: fewer branches = easier to test
        branches = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                branches += 1
        
        functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
        
        if functions == 0:
            return 100.0
        
        branch_density = branches / functions
        
        if branch_density <= 2:
            return 100.0
        elif branch_density <= 4:
            return 80.0
        else:
            return 60.0
    
    def _calculate_mockability_score(self, tree: ast.AST) -> float:
        """Calculate mockability score"""
        # Look for external dependencies that can be mocked
        external_calls = 0
        mockable_calls = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    external_calls += 1
                    # If it's a method call, it's potentially mockable
                    mockable_calls += 1
        
        if external_calls == 0:
            return 100.0
        
        return (mockable_calls / external_calls) * 100.0
    
    # Helper methods for evidence and suggestions
    def _get_complexity_evidence(self, tree: ast.AST) -> List[str]:
        """Get evidence for complexity issues"""
        evidence = []
        complexity = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_complexity = len([n for n in ast.walk(node) 
                                     if isinstance(n, (ast.If, ast.While, ast.For))])
                if func_complexity > 5:
                    evidence.append(f"Function '{node.name}' has complexity {func_complexity}")
        
        return evidence
    
    def _get_complexity_suggestions(self, tree: ast.AST) -> List[str]:
        """Get suggestions for reducing complexity"""
        suggestions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_complexity = len([n for n in ast.walk(node) 
                                     if isinstance(n, (ast.If, ast.While, ast.For))])
                if func_complexity > 5:
                    suggestions.append(f"Consider breaking down '{node.name}' into smaller functions")
        
        return suggestions
    
    def _get_documentation_evidence(self, tree: ast.AST) -> List[str]:
        """Get evidence for documentation issues"""
        evidence = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_docstring = (node.body and isinstance(node.body[0], ast.Expr) and
                               isinstance(node.body[0].value, ast.Constant) and
                               isinstance(node.body[0].value.value, str))
                if not has_docstring:
                    evidence.append(f"Function '{node.name}' lacks documentation")
        
        return evidence
    
    def _get_documentation_suggestions(self, tree: ast.AST) -> List[str]:
        """Get suggestions for improving documentation"""
        suggestions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_docstring = (node.body and isinstance(node.body[0], ast.Expr) and
                               isinstance(node.body[0].value, ast.Constant) and
                               isinstance(node.body[0].value.value, str))
                if not has_docstring:
                    suggestions.append(f"Add docstring to function '{node.name}'")
        
        return suggestions
    
    # Additional helper methods (simplified implementations)
    def _get_naming_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_naming_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_structure_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_structure_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_duplication_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_duplication_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_error_handling_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_error_handling_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_null_safety_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_null_safety_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_resource_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_resource_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_type_safety_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_type_safety_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_dangerous_functions_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_dangerous_functions_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_input_validation_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_input_validation_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_secrets_evidence(self, code: str, tree: ast.AST) -> List[str]:
        return []
    
    def _get_secrets_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_sql_injection_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_sql_injection_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_efficiency_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_efficiency_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_memory_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_memory_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_io_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_io_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_caching_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_caching_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_line_length_evidence(self, code: str) -> List[str]:
        return []
    
    def _get_line_length_suggestions(self, code: str) -> List[str]:
        return []
    
    def _get_comments_evidence(self, code: str) -> List[str]:
        return []
    
    def _get_comments_suggestions(self, code: str) -> List[str]:
        return []
    
    def _get_formatting_evidence(self, code: str) -> List[str]:
        return []
    
    def _get_formatting_suggestions(self, code: str) -> List[str]:
        return []
    
    def _get_function_size_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_function_size_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_isolation_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_isolation_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_dependency_injection_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_dependency_injection_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_coverage_potential_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_coverage_potential_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_mockability_evidence(self, tree: ast.AST) -> List[str]:
        return []
    
    def _get_mockability_suggestions(self, tree: ast.AST) -> List[str]:
        return []
    
    def _calculate_category_scores(self, metrics: List[QualityMetric]) -> Dict[str, float]:
        """Calculate weighted category scores"""
        category_scores = {}
        
        for category in QualityCategory:
            category_metrics = [m for m in metrics if m.category == category]
            if category_metrics:
                weighted_score = sum(m.score * m.weight for m in category_metrics)
                total_weight = sum(m.weight for m in category_metrics)
                category_scores[category.value] = weighted_score / total_weight
            else:
                category_scores[category.value] = 0.0
        
        return category_scores
    
    def _calculate_overall_score(self, category_scores: Dict[str, float]) -> float:
        """Calculate overall quality score"""
        if not category_scores:
            return 0.0
        
        # Weight categories
        weights = {
            'maintainability': 0.25,
            'reliability': 0.25,
            'security': 0.20,
            'performance': 0.15,
            'readability': 0.10,
            'testability': 0.05
        }
        
        weighted_score = sum(category_scores.get(cat, 0) * weight 
                           for cat, weight in weights.items())
        
        return weighted_score
    
    def _calculate_technical_debt(self, metrics: List[QualityMetric]) -> float:
        """Calculate technical debt ratio"""
        # Simple heuristic: inverse of average score
        if not metrics:
            return 0.0
        
        avg_score = sum(m.score for m in metrics) / len(metrics)
        return max(0.0, (100.0 - avg_score) / 100.0)
    
    def _calculate_maintainability_index(self, code: str, tree: ast.AST) -> float:
        """Calculate maintainability index"""
        lines = len(code.split('\n'))
        complexity = 1
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
        
        # Simplified maintainability index
        if lines > 0:
            mi = 171 - 5.2 * math.log(lines) - 0.23 * complexity
            return max(0.0, min(100.0, mi))
        
        return 0.0
    
    def _calculate_trends(self, metrics: List[QualityMetric]) -> Dict[str, Any]:
        """Calculate quality trends (placeholder)"""
        # In a real implementation, this would compare with historical data
        return {
            'trend_direction': 'stable',
            'improvement_rate': 0.0,
            'regression_risk': 'low'
        }
    
    def _generate_improvement_priorities(self, metrics: List[QualityMetric]) -> List[Dict[str, Any]]:
        """Generate improvement priorities"""
        # Sort metrics by score (lowest first) and weight (highest first)
        sorted_metrics = sorted(metrics, key=lambda m: (m.score, -m.weight))
        
        priorities = []
        for metric in sorted_metrics[:5]:  # Top 5 priorities
            if metric.score < 80:  # Only include metrics that need improvement
                priorities.append({
                    'metric': metric.name,
                    'category': metric.category.value,
                    'current_score': metric.score,
                    'priority': 'high' if metric.score < 50 else 'medium',
                    'estimated_effort': 'medium',
                    'suggestions': metric.improvement_suggestions[:3]
                })
        
        return priorities
    
    def _assess_general_quality(self, code: str, language: str) -> QualityReport:
        """Assess quality for non-Python languages"""
        # Simplified assessment for other languages
        lines = code.split('\n')
        loc = len([line for line in lines if line.strip()])
        
        # Basic metrics
        metrics = [
            QualityMetric(
                name="Lines of Code",
                score=max(0, 100 - loc // 10),  # Penalize very long files
                weight=1.0,
                category=QualityCategory.MAINTAINABILITY,
                description="Code length assessment",
                evidence=[f"File has {loc} lines of code"],
                improvement_suggestions=["Consider breaking into smaller modules"]
            )
        ]
        
        category_scores = self._calculate_category_scores(metrics)
        overall_score = self._calculate_overall_score(category_scores)
        
        return QualityReport(
            overall_score=overall_score,
            category_scores=category_scores,
            metrics=metrics,
            technical_debt_ratio=0.0,
            maintainability_index=overall_score,
            quality_trends={},
            improvement_priorities=[]
        )
    
    def _create_error_report(self, error_message: str) -> QualityReport:
        """Create error report for failed assessments"""
        return QualityReport(
            overall_score=0.0,
            category_scores={},
            metrics=[],
            technical_debt_ratio=1.0,
            maintainability_index=0.0,
            quality_trends={},
            improvement_priorities=[{
                'metric': 'Code Analysis',
                'category': 'error',
                'current_score': 0.0,
                'priority': 'high',
                'estimated_effort': 'high',
                'suggestions': [f"Fix analysis error: {error_message}"]
            }]
        )
    
    def _load_security_patterns(self) -> Dict[str, List[str]]:
        """Load security patterns for analysis"""
        return {
            'dangerous_functions': ['eval', 'exec', 'compile'],
            'sql_injection_patterns': ['execute', 'query', 'select'],
            'secret_patterns': ['password', 'api_key', 'secret', 'token']
        }
    
    def _load_performance_patterns(self) -> Dict[str, List[str]]:
        """Load performance patterns for analysis"""
        return {
            'inefficient_loops': ['nested_for', 'nested_while'],
            'memory_leaks': ['unclosed_file', 'infinite_recursion'],
            'slow_operations': ['deep_copy', 'regex_in_loop']
        }


def assess_code_quality(code: str, language: str = "python", 
                       include_trends: bool = False) -> Dict[str, Any]:
    """Assess code quality and return comprehensive report"""
    try:
        analyzer = CodeQualityAnalyzer()
        report = analyzer.assess_quality(code, language, include_trends)
        
        return {
            'status': 'success',
            'overall_score': report.overall_score,
            'category_scores': report.category_scores,
            'technical_debt_ratio': report.technical_debt_ratio,
            'maintainability_index': report.maintainability_index,
            'metrics': [
                {
                    'name': m.name,
                    'score': m.score,
                    'category': m.category.value,
                    'weight': m.weight,
                    'description': m.description,
                    'evidence': m.evidence,
                    'improvement_suggestions': m.improvement_suggestions
                }
                for m in report.metrics
            ],
            'improvement_priorities': report.improvement_priorities,
            'quality_trends': report.quality_trends,
            'assessment_timestamp': math.floor(time.time() * 1000)
        }
        
    except Exception as e:
        logger.error(f"Quality assessment failed: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'overall_score': 0.0
        }


if __name__ == "__main__":
    # Test the quality analyzer
    sample_code = '''
def calculate_fibonacci(n):
    """Calculate fibonacci number"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result

class DataProcessor:
    def __init__(self):
        self.cache = {}
    
    def process(self, data):
        if 'processed' in self.cache:
            return self.cache['processed']
        
        processed = []
        for item in data:
            if item is not None:
                processed.append(item.upper())
        
        self.cache['processed'] = processed
        return processed
'''
    
    result = assess_code_quality(sample_code, "python", include_trends=True)
    print(f"Overall Score: {result['overall_score']:.1f}")
    print(f"Technical Debt: {result['technical_debt_ratio']:.2f}")
    print(f"Maintainability Index: {result['maintainability_index']:.1f}")
    
    print("\nCategory Scores:")
    for category, score in result['category_scores'].items():
        print(f"  {category}: {score:.1f}")
    
    print(f"\nTop Improvement Priorities:")
    for priority in result['improvement_priorities'][:3]:
        print(f"  - {priority['metric']}: {priority['current_score']:.1f} ({priority['priority']})")