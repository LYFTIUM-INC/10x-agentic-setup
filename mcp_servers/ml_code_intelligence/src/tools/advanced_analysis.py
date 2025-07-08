"""
Advanced Code Analysis Tools
Enhanced analysis beyond basic metrics including pattern detection, refactoring suggestions, and architectural insights
"""

import ast
import re
import logging
import time
import math
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


@dataclass
class RefactoringSuggestion:
    """Refactoring suggestion with priority and impact"""
    type: str  # "extract_method", "reduce_complexity", "improve_naming", etc.
    location: str  # file:line:column or function name
    description: str
    reasoning: str
    priority: str  # "high", "medium", "low"
    estimated_effort: str  # "small", "medium", "large"
    impact: str  # "performance", "maintainability", "readability"


@dataclass
class ArchitecturalInsight:
    """Architectural-level insights about code structure"""
    type: str  # "dependency", "coupling", "cohesion", "pattern"
    description: str
    components: List[str]
    severity: str  # "info", "warning", "critical"
    recommendation: str


@dataclass
class CodePattern:
    """Detected code pattern (good or bad)"""
    name: str
    type: str  # "design_pattern", "anti_pattern", "code_smell"
    confidence: float  # 0.0 to 1.0
    locations: List[Dict[str, Any]]
    description: str


class AdvancedPythonAnalyzer:
    """Advanced Python code analysis with ML-enhanced insights"""
    
    def __init__(self):
        self.refactoring_suggestions: List[RefactoringSuggestion] = []
        self.architectural_insights: List[ArchitecturalInsight] = []
        self.detected_patterns: List[CodePattern] = []
        self.function_metrics: Dict[str, Dict[str, Any]] = {}
        self.class_metrics: Dict[str, Dict[str, Any]] = {}
    
    def analyze_advanced(self, code: str, filename: str = "unknown") -> Dict[str, Any]:
        """Perform advanced code analysis"""
        try:
            tree = ast.parse(code)
            
            # Reset analysis state
            self.refactoring_suggestions = []
            self.architectural_insights = []
            self.detected_patterns = []
            self.function_metrics = {}
            self.class_metrics = {}
            
            # Perform various analyses
            self._analyze_functions(tree)
            self._analyze_classes(tree)
            self._detect_code_patterns(tree)
            self._analyze_dependencies(tree)
            self._generate_refactoring_suggestions(tree)
            self._analyze_architecture(tree)
            
            return {
                'refactoring_suggestions': [
                    {
                        'type': s.type,
                        'location': s.location,
                        'description': s.description,
                        'reasoning': s.reasoning,
                        'priority': s.priority,
                        'estimated_effort': s.estimated_effort,
                        'impact': s.impact
                    }
                    for s in self.refactoring_suggestions
                ],
                'architectural_insights': [
                    {
                        'type': i.type,
                        'description': i.description,
                        'components': i.components,
                        'severity': i.severity,
                        'recommendation': i.recommendation
                    }
                    for i in self.architectural_insights
                ],
                'detected_patterns': [
                    {
                        'name': p.name,
                        'type': p.type,
                        'confidence': p.confidence,
                        'locations': p.locations,
                        'description': p.description
                    }
                    for p in self.detected_patterns
                ],
                'function_metrics': self.function_metrics,
                'class_metrics': self.class_metrics
            }
            
        except SyntaxError as e:
            logger.error(f"Syntax error in code analysis: {e}")
            return {'error': f"Syntax error: {e}"}
        except Exception as e:
            logger.error(f"Advanced analysis failed: {e}")
            return {'error': f"Analysis failed: {e}"}
    
    def _analyze_functions(self, tree: ast.AST) -> None:
        """Analyze function-level metrics and characteristics"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics = self._calculate_function_metrics(node)
                self.function_metrics[node.name] = metrics
                
                # Check for function-level issues
                if metrics['lines_of_code'] > 50:
                    self.refactoring_suggestions.append(RefactoringSuggestion(
                        type="extract_method",
                        location=f"{node.name}:{node.lineno}",
                        description=f"Function '{node.name}' is too long ({metrics['lines_of_code']} lines)",
                        reasoning="Long functions are harder to understand, test, and maintain",
                        priority="medium",
                        estimated_effort="medium",
                        impact="maintainability"
                    ))
                
                if metrics['cyclomatic_complexity'] > 10:
                    self.refactoring_suggestions.append(RefactoringSuggestion(
                        type="reduce_complexity",
                        location=f"{node.name}:{node.lineno}",
                        description=f"Function '{node.name}' has high complexity ({metrics['cyclomatic_complexity']})",
                        reasoning="High complexity increases the likelihood of bugs and makes testing difficult",
                        priority="high",
                        estimated_effort="large",
                        impact="maintainability"
                    ))
                
                if metrics['parameter_count'] > 5:
                    self.refactoring_suggestions.append(RefactoringSuggestion(
                        type="parameter_object",
                        location=f"{node.name}:{node.lineno}",
                        description=f"Function '{node.name}' has too many parameters ({metrics['parameter_count']})",
                        reasoning="Too many parameters suggest the function may be doing too much",
                        priority="medium",
                        estimated_effort="medium",
                        impact="readability"
                    ))
    
    def _calculate_function_metrics(self, func_node: ast.FunctionDef) -> Dict[str, Any]:
        """Calculate detailed metrics for a function"""
        # Count lines of code
        if hasattr(func_node, 'end_lineno'):
            loc = func_node.end_lineno - func_node.lineno + 1
        else:
            loc = len([n for n in ast.walk(func_node) if hasattr(n, 'lineno')])
        
        # Count parameters
        param_count = len(func_node.args.args) + len(func_node.args.posonlyargs)
        if func_node.args.vararg:
            param_count += 1
        if func_node.args.kwarg:
            param_count += 1
        param_count += len(func_node.args.kwonlyargs)
        
        # Calculate cyclomatic complexity
        complexity = 1  # Base complexity
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                               ast.With, ast.Assert, ast.BoolOp)):
                complexity += 1
        
        # Count return statements
        returns = len([n for n in ast.walk(func_node) if isinstance(n, ast.Return)])
        
        # Count nested functions/classes
        nested = len([n for n in ast.walk(func_node) 
                     if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                     and n != func_node])
        
        # Check for docstring
        has_docstring = (isinstance(func_node.body[0], ast.Expr) and
                        isinstance(func_node.body[0].value, ast.Constant) and
                        isinstance(func_node.body[0].value.value, str)) if func_node.body else False
        
        return {
            'lines_of_code': loc,
            'parameter_count': param_count,
            'cyclomatic_complexity': complexity,
            'return_statements': returns,
            'nested_functions': nested,
            'has_docstring': has_docstring,
            'line_number': func_node.lineno
        }
    
    def _analyze_classes(self, tree: ast.AST) -> None:
        """Analyze class-level metrics and characteristics"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                metrics = self._calculate_class_metrics(node)
                self.class_metrics[node.name] = metrics
                
                # Check for class-level issues
                if metrics['method_count'] > 20:
                    self.refactoring_suggestions.append(RefactoringSuggestion(
                        type="split_class",
                        location=f"{node.name}:{node.lineno}",
                        description=f"Class '{node.name}' has too many methods ({metrics['method_count']})",
                        reasoning="Large classes violate the Single Responsibility Principle",
                        priority="medium",
                        estimated_effort="large",
                        impact="maintainability"
                    ))
                
                if metrics['inheritance_depth'] > 5:
                    self.architectural_insights.append(ArchitecturalInsight(
                        type="coupling",
                        description=f"Class '{node.name}' has deep inheritance hierarchy",
                        components=[node.name],
                        severity="warning",
                        recommendation="Consider composition over inheritance"
                    ))
    
    def _calculate_class_metrics(self, class_node: ast.ClassDef) -> Dict[str, Any]:
        """Calculate detailed metrics for a class"""
        methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]
        properties = [n for n in class_node.body if isinstance(n, ast.AsyncFunctionDef)]
        
        # Count different types of methods
        public_methods = [m for m in methods if not m.name.startswith('_')]
        private_methods = [m for m in methods if m.name.startswith('_') and not m.name.startswith('__')]
        magic_methods = [m for m in methods if m.name.startswith('__') and m.name.endswith('__')]
        
        # Calculate inheritance depth (simplified)
        inheritance_depth = len(class_node.bases)
        
        # Check for docstring
        has_docstring = (isinstance(class_node.body[0], ast.Expr) and
                        isinstance(class_node.body[0].value, ast.Constant) and
                        isinstance(class_node.body[0].value.value, str)) if class_node.body else False
        
        return {
            'method_count': len(methods),
            'property_count': len(properties),
            'public_methods': len(public_methods),
            'private_methods': len(private_methods),
            'magic_methods': len(magic_methods),
            'inheritance_depth': inheritance_depth,
            'has_docstring': has_docstring,
            'line_number': class_node.lineno
        }
    
    def _detect_code_patterns(self, tree: ast.AST) -> None:
        """Detect common code patterns and anti-patterns"""
        # Detect Singleton pattern
        self._detect_singleton_pattern(tree)
        
        # Detect Factory pattern
        self._detect_factory_pattern(tree)
        
        # Detect anti-patterns
        self._detect_god_object(tree)
        self._detect_feature_envy(tree)
        self._detect_dead_code(tree)
    
    def _detect_singleton_pattern(self, tree: ast.AST) -> None:
        """Detect Singleton design pattern"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Look for singleton indicators
                has_instance_var = False
                has_new_method = False
                
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        if child.name == '__new__':
                            has_new_method = True
                        # Check for instance class variable
                        for stmt in ast.walk(child):
                            if isinstance(stmt, ast.Assign):
                                for target in stmt.targets:
                                    if isinstance(target, ast.Attribute) and target.attr == '_instance':
                                        has_instance_var = True
                
                if has_instance_var and has_new_method:
                    self.detected_patterns.append(CodePattern(
                        name="Singleton Pattern",
                        type="design_pattern",
                        confidence=0.8,
                        locations=[{'class': node.name, 'line': node.lineno}],
                        description="Implementation of Singleton design pattern detected"
                    ))
    
    def _detect_factory_pattern(self, tree: ast.AST) -> None:
        """Detect Factory design pattern"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Look for factory method indicators
                if any(keyword in node.name.lower() for keyword in ['create', 'make', 'build', 'factory']):
                    # Check if it returns different types based on parameters
                    returns = [n for n in ast.walk(node) if isinstance(n, ast.Return)]
                    if len(returns) > 1:
                        self.detected_patterns.append(CodePattern(
                            name="Factory Pattern",
                            type="design_pattern",
                            confidence=0.6,
                            locations=[{'function': node.name, 'line': node.lineno}],
                            description="Possible Factory pattern implementation detected"
                        ))
    
    def _detect_god_object(self, tree: ast.AST) -> None:
        """Detect God Object anti-pattern"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > 15:  # Threshold for god object
                    self.detected_patterns.append(CodePattern(
                        name="God Object",
                        type="anti_pattern",
                        confidence=0.7,
                        locations=[{'class': node.name, 'line': node.lineno}],
                        description=f"Class '{node.name}' has {len(methods)} methods, suggesting God Object anti-pattern"
                    ))
    
    def _detect_feature_envy(self, tree: ast.AST) -> None:
        """Detect Feature Envy anti-pattern"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count attribute accesses to other objects
                external_accesses = defaultdict(int)
                for child in ast.walk(node):
                    if isinstance(child, ast.Attribute):
                        if isinstance(child.value, ast.Name) and child.value.id != 'self':
                            external_accesses[child.value.id] += 1
                
                # If method accesses other objects more than self, it might have feature envy
                self_accesses = sum(1 for child in ast.walk(node) 
                                  if isinstance(child, ast.Attribute) and 
                                  isinstance(child.value, ast.Name) and 
                                  child.value.id == 'self')
                
                for obj, count in external_accesses.items():
                    if count > self_accesses and count > 3:
                        self.detected_patterns.append(CodePattern(
                            name="Feature Envy",
                            type="code_smell",
                            confidence=0.6,
                            locations=[{'function': node.name, 'line': node.lineno, 'envied_object': obj}],
                            description=f"Function '{node.name}' accesses '{obj}' more than self"
                        ))
    
    def _detect_dead_code(self, tree: ast.AST) -> None:
        """Detect potentially dead code"""
        defined_functions = set()
        called_functions = set()
        
        # Collect all function definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                defined_functions.add(node.name)
        
        # Collect all function calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_functions.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    called_functions.add(node.func.attr)
        
        # Find potentially unused functions
        unused_functions = defined_functions - called_functions
        for func_name in unused_functions:
            # Don't flag special methods or main functions
            if not func_name.startswith('__') and func_name not in ['main', 'test_']:
                self.detected_patterns.append(CodePattern(
                    name="Dead Code",
                    type="code_smell",
                    confidence=0.5,
                    locations=[{'function': func_name}],
                    description=f"Function '{func_name}' appears to be unused"
                ))
    
    def _analyze_dependencies(self, tree: ast.AST) -> None:
        """Analyze import dependencies and coupling"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        imports.append(f"{node.module}.{alias.name}")
        
        # Analyze dependency patterns
        stdlib_imports = []
        third_party_imports = []
        local_imports = []
        
        for imp in imports:
            if any(imp.startswith(stdlib) for stdlib in ['os', 'sys', 're', 'json', 'math', 'datetime']):
                stdlib_imports.append(imp)
            elif '.' in imp and not imp.startswith('.'):
                third_party_imports.append(imp)
            else:
                local_imports.append(imp)
        
        if len(third_party_imports) > 10:
            self.architectural_insights.append(ArchitecturalInsight(
                type="dependency",
                description=f"High number of third-party dependencies ({len(third_party_imports)})",
                components=third_party_imports[:5],  # Show first 5
                severity="warning",
                recommendation="Consider reducing dependencies to improve maintainability"
            ))
    
    def _generate_refactoring_suggestions(self, tree: ast.AST) -> None:
        """Generate additional refactoring suggestions based on analysis"""
        # Check for duplicate code patterns
        self._detect_duplicate_code(tree)
        
        # Check for long parameter lists
        self._detect_long_parameter_lists(tree)
        
        # Check for nested loops/conditionals
        self._detect_deep_nesting(tree)
    
    def _detect_duplicate_code(self, tree: ast.AST) -> None:
        """Detect potential code duplication"""
        # Simplified duplicate detection - look for similar AST structures
        function_bodies = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Convert function body to a simplified string for comparison
                body_str = ast.dump(ast.Module(body=node.body, type_ignores=[]))
                function_bodies.append((node.name, body_str, node.lineno))
        
        # Check for similar bodies
        for i, (name1, body1, line1) in enumerate(function_bodies):
            for name2, body2, line2 in function_bodies[i+1:]:
                # Simple similarity check (could be enhanced with ML)
                if len(body1) > 100 and self._similarity_ratio(body1, body2) > 0.8:
                    self.refactoring_suggestions.append(RefactoringSuggestion(
                        type="extract_common_code",
                        location=f"{name1}:{line1}, {name2}:{line2}",
                        description=f"Functions '{name1}' and '{name2}' have similar implementations",
                        reasoning="Duplicate code increases maintenance burden",
                        priority="medium",
                        estimated_effort="medium",
                        impact="maintainability"
                    ))
    
    def _similarity_ratio(self, str1: str, str2: str) -> float:
        """Calculate similarity ratio between two strings"""
        # Simple Jaccard similarity
        set1 = set(str1.split())
        set2 = set(str2.split())
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0
    
    def _detect_long_parameter_lists(self, tree: ast.AST) -> None:
        """Detect functions with too many parameters"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                param_count = len(node.args.args)
                if param_count > 6:
                    self.refactoring_suggestions.append(RefactoringSuggestion(
                        type="introduce_parameter_object",
                        location=f"{node.name}:{node.lineno}",
                        description=f"Function '{node.name}' has {param_count} parameters",
                        reasoning="Long parameter lists are hard to remember and use",
                        priority="medium",
                        estimated_effort="medium",
                        impact="readability"
                    ))
    
    def _detect_deep_nesting(self, tree: ast.AST) -> None:
        """Detect deeply nested code structures"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                max_depth = self._calculate_nesting_depth(node)
                if max_depth > 4:
                    self.refactoring_suggestions.append(RefactoringSuggestion(
                        type="reduce_nesting",
                        location=f"{node.name}:{node.lineno}",
                        description=f"Function '{node.name}' has deep nesting (depth {max_depth})",
                        reasoning="Deep nesting makes code hard to follow and understand",
                        priority="medium",
                        estimated_effort="medium",
                        impact="readability"
                    ))
    
    def _calculate_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth in a code block"""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                depth = self._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, depth)
            else:
                depth = self._calculate_nesting_depth(child, current_depth)
                max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _analyze_architecture(self, tree: ast.AST) -> None:
        """Analyze architectural patterns and provide insights"""
        # Check for MVC pattern
        self._detect_mvc_pattern(tree)
        
        # Check for dependency injection
        self._detect_dependency_injection(tree)
        
        # Check for proper error handling
        self._analyze_error_handling(tree)
    
    def _detect_mvc_pattern(self, tree: ast.AST) -> None:
        """Detect MVC architectural pattern"""
        class_names = [node.name.lower() for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        has_model = any('model' in name for name in class_names)
        has_view = any('view' in name for name in class_names)
        has_controller = any('controller' in name for name in class_names)
        
        if has_model and has_view and has_controller:
            self.architectural_insights.append(ArchitecturalInsight(
                type="pattern",
                description="MVC architectural pattern detected",
                components=[name for name in class_names if any(mvc in name for mvc in ['model', 'view', 'controller'])],
                severity="info",
                recommendation="Ensure clear separation of concerns between MVC components"
            ))
    
    def _detect_dependency_injection(self, tree: ast.AST) -> None:
        """Detect dependency injection pattern"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == '__init__':
                # Check if dependencies are injected through constructor
                if len(node.args.args) > 2:  # self + dependencies
                    self.architectural_insights.append(ArchitecturalInsight(
                        type="pattern",
                        description="Dependency injection pattern detected",
                        components=[arg.arg for arg in node.args.args[1:]],  # Skip 'self'
                        severity="info",
                        recommendation="Good use of dependency injection for testability"
                    ))
    
    def _analyze_error_handling(self, tree: ast.AST) -> None:
        """Analyze error handling patterns"""
        try_blocks = [node for node in ast.walk(tree) if isinstance(node, ast.Try)]
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        if len(functions) > 0:
            error_handling_ratio = len(try_blocks) / len(functions)
            
            if error_handling_ratio < 0.3:
                self.architectural_insights.append(ArchitecturalInsight(
                    type="pattern",
                    description="Low error handling coverage",
                    components=[f"{len(try_blocks)} try blocks in {len(functions)} functions"],
                    severity="warning",
                    recommendation="Consider adding more comprehensive error handling"
                ))


# Integration with existing code analysis
def enhance_code_analysis(code: str, language: str = "python") -> Dict[str, Any]:
    """Enhanced code analysis combining basic and advanced analysis"""
    if language.lower() != "python":
        return {"error": "Advanced analysis currently only supports Python"}
    
    try:
        analyzer = AdvancedPythonAnalyzer()
        advanced_results = analyzer.analyze_advanced(code)
        
        return {
            "status": "success",
            "advanced_analysis": advanced_results,
            "analysis_timestamp": math.floor(time.time() * 1000),  # milliseconds
            "language": language
        }
        
    except Exception as e:
        logger.error(f"Enhanced analysis failed: {e}")
        return {"error": f"Enhanced analysis failed: {e}"}


if __name__ == "__main__":
    # Test the advanced analyzer
    sample_code = '''
class UserManager:
    def __init__(self, db, cache, logger, email_service, notification_service):
        self.db = db
        self.cache = cache
        self.logger = logger
        self.email_service = email_service
        self.notification_service = notification_service
    
    def create_user(self, name, email, password, address, phone, age, gender, preferences):
        if not name or not email:
            return None
        
        if self.db.user_exists(email):
            return None
            
        user = self.db.create_user(name, email, password)
        self.cache.set(f"user_{user.id}", user)
        self.logger.info(f"Created user {user.id}")
        self.email_service.send_welcome_email(email)
        return user
    
    def get_user(self, user_id):
        cached = self.cache.get(f"user_{user_id}")
        if cached:
            return cached
        return self.db.get_user(user_id)
    
    def update_user_profile(self, user_id, name, email, address, phone):
        user = self.get_user(user_id)
        if not user:
            return False
        user.name = name
        user.email = email
        user.address = address
        user.phone = phone
        self.db.save_user(user)
        self.cache.set(f"user_{user.id}", user)
        return True

def unused_function():
    return "This function is never called"
'''
    
    import time
    result = enhance_code_analysis(sample_code, "python")
    print("Advanced Analysis Results:")
    for key, value in result.items():
        if key != "advanced_analysis":
            print(f"{key}: {value}")
    
    if "advanced_analysis" in result:
        analysis = result["advanced_analysis"]
        print(f"\nRefactoring Suggestions: {len(analysis.get('refactoring_suggestions', []))}")
        for suggestion in analysis.get('refactoring_suggestions', [])[:3]:
            print(f"  - {suggestion['type']}: {suggestion['description']}")
        
        print(f"\nDetected Patterns: {len(analysis.get('detected_patterns', []))}")
        for pattern in analysis.get('detected_patterns', []):
            print(f"  - {pattern['name']} ({pattern['type']}): {pattern['confidence']:.2f}")
        
        print(f"\nArchitectural Insights: {len(analysis.get('architectural_insights', []))}")
        for insight in analysis.get('architectural_insights', []):
            print(f"  - {insight['type']}: {insight['description']}")