"""
Code Agent Implementation for Agentic Workflow MCP
Specialized agent for code generation, analysis, and optimization tasks
"""

import asyncio
import ast
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

from .base_agent import BaseAgent, AgentTask

logger = logging.getLogger(__name__)

class CodeAgent(BaseAgent):
    """
    Specialized agent for code-related tasks
    
    Capabilities:
    - Code generation and implementation
    - Code analysis and quality assessment
    - Refactoring and optimization
    - Architecture design and patterns
    - Documentation generation
    - Bug detection and fixing
    """
    
    def __init__(self, agent_id: str):
        capabilities = [
            "code_generation",
            "code_analysis",
            "refactoring",
            "optimization",
            "architecture_design",
            "documentation_generation",
            "bug_detection",
            "code_review",
            "pattern_implementation",
            "quality_assessment"
        ]
        
        super().__init__(agent_id, "code_agent", capabilities)
        
        self.code_templates = {}
        self.quality_metrics = {}
        self.supported_languages = ["python", "javascript", "typescript", "java", "cpp", "go"]
        self.code_patterns = {}
        self.optimization_rules = {}
        self._initialize_code_knowledge()
    
    def _initialize_code_knowledge(self) -> None:
        """Initialize code templates, patterns, and rules"""
        
        # Initialize code templates
        self.code_templates = {
            "python": {
                "class": """class {class_name}:
    \"\"\"
    {description}
    \"\"\"
    
    def __init__(self):
        pass
    
    def {method_name}(self):
        \"\"\"
        {method_description}
        \"\"\"
        pass
""",
                "function": """def {function_name}({parameters}):
    \"\"\"
    {description}
    
    Args:
        {args_description}
    
    Returns:
        {return_description}
    \"\"\"
    pass
""",
                "async_function": """async def {function_name}({parameters}):
    \"\"\"
    {description}
    
    Args:
        {args_description}
    
    Returns:
        {return_description}
    \"\"\"
    pass
""",
                "test_function": """def test_{function_name}():
    \"\"\"Test {function_name} functionality\"\"\"
    # Arrange
    {setup_code}
    
    # Act
    result = {function_name}({test_args})
    
    # Assert
    assert {assertion}
"""
            },
            "javascript": {
                "class": """class {class_name} {{
    /**
     * {description}
     */
    constructor() {{
        // Initialize class
    }}
    
    /**
     * {method_description}
     */
    {method_name}() {{
        // Implementation
    }}
}}""",
                "function": """/**
 * {description}
 * @param {{{param_types}}} {parameters}
 * @returns {{{return_type}}}
 */
function {function_name}({parameters}) {{
    // Implementation
}}""",
                "async_function": """/**
 * {description}
 * @param {{{param_types}}} {parameters}
 * @returns {{Promise<{return_type}>}}
 */
async function {function_name}({parameters}) {{
    // Implementation
}}"""
            }
        }
        
        # Initialize code patterns
        self.code_patterns = {
            "singleton": {
                "description": "Singleton pattern implementation",
                "use_cases": ["Database connections", "Configuration management", "Logging"],
                "languages": ["python", "javascript", "java"]
            },
            "factory": {
                "description": "Factory pattern implementation",
                "use_cases": ["Object creation", "Plugin systems", "Database drivers"],
                "languages": ["python", "javascript", "java", "cpp"]
            },
            "observer": {
                "description": "Observer pattern implementation",
                "use_cases": ["Event handling", "Model-View architectures", "Pub/Sub systems"],
                "languages": ["python", "javascript", "java"]
            }
        }
        
        # Initialize optimization rules
        self.optimization_rules = {
            "performance": [
                "Use list comprehensions instead of loops where possible",
                "Avoid unnecessary object creation in loops",
                "Use generators for large datasets",
                "Implement caching for expensive operations"
            ],
            "memory": [
                "Use __slots__ for classes with many instances",
                "Clean up resources properly with context managers",
                "Avoid circular references",
                "Use weak references where appropriate"
            ],
            "readability": [
                "Use meaningful variable and function names",
                "Keep functions small and focused",
                "Add comprehensive docstrings",
                "Follow PEP 8 style guidelines"
            ]
        }
    
    async def _agent_specific_initialization(self, config: Dict[str, Any]) -> None:
        """Initialize code-specific tools and configurations"""
        
        # Initialize code tools
        self.tools.update({
            "code_generator": self._generate_code,
            "code_analyzer": self._analyze_code,
            "quality_checker": self._check_code_quality,
            "refactor_engine": self._refactor_code,
            "optimizer": self._optimize_code,
            "documentation_generator": self._generate_documentation,
            "bug_detector": self._detect_bugs,
            "pattern_implementer": self._implement_pattern
        })
        
        # Initialize quality metrics
        self.quality_metrics = config.get("quality_metrics", {
            "complexity_threshold": 10,
            "coverage_threshold": 0.8,
            "maintainability_threshold": 0.7,
            "security_level": "medium"
        })
        
        # Update supported languages from config
        if "supported_languages" in config:
            self.supported_languages = config["supported_languages"]
    
    async def _can_handle_task(self, task: AgentTask) -> bool:
        """Check if this code agent can handle the given task"""
        
        code_task_types = [
            "code", "implement", "develop", "build", "create", "program",
            "refactor", "optimize", "analyze", "review", "debug", "fix"
        ]
        
        task_type_lower = task.task_type.lower()
        task_description_lower = task.description.lower()
        
        # Check if task type or description contains code-related keywords
        return (any(keyword in task_type_lower for keyword in code_task_types) or
                any(keyword in task_description_lower for keyword in code_task_types))
    
    async def _execute_agent_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute code-specific task logic"""
        
        code_task_type = await self._determine_code_task_type(task)
        language = task.parameters.get("language", "python")
        
        if language not in self.supported_languages:
            raise ValueError(f"Unsupported language: {language}")
        
        logger.info(f"Code agent {self.agent_id} executing {code_task_type} task in {language}")
        
        # Execute based on task type
        if code_task_type == "generation":
            result = await self._execute_code_generation(task, language)
        elif code_task_type == "analysis":
            result = await self._execute_code_analysis(task, language)
        elif code_task_type == "refactoring":
            result = await self._execute_code_refactoring(task, language)
        elif code_task_type == "optimization":
            result = await self._execute_code_optimization(task, language)
        elif code_task_type == "documentation":
            result = await self._execute_documentation_generation(task, language)
        elif code_task_type == "debugging":
            result = await self._execute_bug_detection(task, language)
        else:
            # Default to general code processing
            result = await self._execute_general_code_task(task, language)
        
        # Add code-specific metadata
        result.update({
            "task_type": code_task_type,
            "language": language,
            "quality_score": await self._calculate_code_quality_score(result),
            "complexity_analysis": await self._analyze_complexity(result),
            "recommendations": await self._generate_code_recommendations(result, task)
        })
        
        return result
    
    async def _determine_code_task_type(self, task: AgentTask) -> str:
        """Determine the specific type of code task"""
        
        description = task.description.lower()
        
        if any(keyword in description for keyword in ["generate", "create", "implement", "build"]):
            return "generation"
        elif any(keyword in description for keyword in ["analyze", "review", "examine"]):
            return "analysis"
        elif any(keyword in description for keyword in ["refactor", "restructure", "improve"]):
            return "refactoring"
        elif any(keyword in description for keyword in ["optimize", "performance", "speed"]):
            return "optimization"
        elif any(keyword in description for keyword in ["document", "comments", "documentation"]):
            return "documentation"
        elif any(keyword in description for keyword in ["debug", "fix", "bug", "error"]):
            return "debugging"
        else:
            return "general"
    
    async def _execute_code_generation(self, task: AgentTask, language: str) -> Dict[str, Any]:
        """Execute code generation task"""
        
        generation_type = task.parameters.get("generation_type", "function")
        requirements = task.parameters.get("requirements", {})
        
        # Generate code based on type
        if generation_type == "class":
            generated_code = await self._generate_class(requirements, language)
        elif generation_type == "function":
            generated_code = await self._generate_function(requirements, language)
        elif generation_type == "module":
            generated_code = await self._generate_module(requirements, language)
        elif generation_type == "test":
            generated_code = await self._generate_test_code(requirements, language)
        else:
            generated_code = await self._generate_generic_code(requirements, language)
        
        # Validate generated code
        validation_result = await self._validate_generated_code(generated_code, language)
        
        return {
            "generated_code": generated_code,
            "generation_type": generation_type,
            "validation": validation_result,
            "estimated_complexity": await self._estimate_code_complexity(generated_code),
            "implementation_notes": await self._generate_implementation_notes(generated_code, requirements)
        }
    
    async def _generate_class(self, requirements: Dict[str, Any], language: str) -> str:
        """Generate class implementation"""
        
        class_name = requirements.get("class_name", "GeneratedClass")
        description = requirements.get("description", "Generated class")
        methods = requirements.get("methods", [])
        
        if language == "python":
            template = self.code_templates["python"]["class"]
            
            # Generate methods
            method_implementations = []
            for method in methods:
                method_code = f"""    def {method.get('name', 'method')}(self{', ' + method.get('parameters', '') if method.get('parameters') else ''}):
        \"\"\"
        {method.get('description', 'Method description')}
        \"\"\"
        {method.get('implementation', 'pass')}
"""
                method_implementations.append(method_code)
            
            generated_code = template.format(
                class_name=class_name,
                description=description,
                method_name=methods[0].get("name", "example_method") if methods else "example_method",
                method_description=methods[0].get("description", "Example method") if methods else "Example method"
            )
            
            # Add additional methods
            if len(methods) > 1:
                generated_code += "\n" + "\n".join(method_implementations[1:])
        
        elif language == "javascript":
            template = self.code_templates["javascript"]["class"]
            generated_code = template.format(
                class_name=class_name,
                description=description,
                method_name=methods[0].get("name", "exampleMethod") if methods else "exampleMethod",
                method_description=methods[0].get("description", "Example method") if methods else "Example method"
            )
        
        else:
            # Generic class template
            generated_code = f"""// Generated {class_name} class
class {class_name} {{
    // {description}
    
    constructor() {{
        // Initialize class
    }}
    
    // Add methods here
}}"""
        
        return generated_code
    
    async def _generate_function(self, requirements: Dict[str, Any], language: str) -> str:
        """Generate function implementation"""
        
        function_name = requirements.get("function_name", "generated_function")
        description = requirements.get("description", "Generated function")
        parameters = requirements.get("parameters", [])
        return_type = requirements.get("return_type", "Any")
        is_async = requirements.get("async", False)
        
        if language == "python":
            template = self.code_templates["python"]["async_function" if is_async else "function"]
            
            # Format parameters
            param_str = ", ".join(parameters) if parameters else ""
            args_desc = "\n        ".join([f"{param}: Parameter description" for param in parameters])
            
            generated_code = template.format(
                function_name=function_name,
                parameters=param_str,
                description=description,
                args_description=args_desc or "No parameters",
                return_description=f"{return_type} description"
            )
            
            # Add basic implementation
            implementation = requirements.get("implementation", "")
            if implementation:
                generated_code = generated_code.replace("pass", implementation)
        
        elif language == "javascript":
            template = self.code_templates["javascript"]["async_function" if is_async else "function"]
            
            param_str = ", ".join(parameters) if parameters else ""
            param_types = " | ".join(["string" for _ in parameters]) if parameters else ""
            
            generated_code = template.format(
                function_name=function_name,
                parameters=param_str,
                description=description,
                param_types=param_types,
                return_type=return_type
            )
        
        else:
            # Generic function template
            async_keyword = "async " if is_async else ""
            param_str = ", ".join(parameters) if parameters else ""
            generated_code = f"""// Generated {function_name} function
{async_keyword}function {function_name}({param_str}) {{
    // {description}
    // Implementation goes here
}}"""
        
        return generated_code
    
    async def _generate_module(self, requirements: Dict[str, Any], language: str) -> str:
        """Generate module implementation"""
        
        module_name = requirements.get("module_name", "generated_module")
        description = requirements.get("description", "Generated module")
        exports = requirements.get("exports", [])
        
        if language == "python":
            generated_code = f'''"""
{module_name} - {description}

This module provides:
{chr(10).join(f"- {export}" for export in exports)}
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Module implementation
'''
            
            # Add exports
            for export in exports:
                if export.get("type") == "function":
                    func_code = await self._generate_function(export, language)
                    generated_code += f"\n\n{func_code}"
                elif export.get("type") == "class":
                    class_code = await self._generate_class(export, language)
                    generated_code += f"\n\n{class_code}"
        
        elif language == "javascript":
            generated_code = f"""/**
 * {module_name} - {description}
 * 
 * This module provides:
 * {chr(10).join(f" * - {export}" for export in exports)}
 */

// Module implementation
"""
        
        else:
            generated_code = f"""// {module_name} - {description}
// Module implementation
"""
        
        return generated_code
    
    async def _generate_test_code(self, requirements: Dict[str, Any], language: str) -> str:
        """Generate test code"""
        
        test_target = requirements.get("test_target", "function")
        test_cases = requirements.get("test_cases", [])
        
        if language == "python":
            generated_code = f"""import unittest
from unittest.mock import patch, MagicMock
import pytest

class Test{test_target.title()}(unittest.TestCase):
    \"\"\"Test cases for {test_target}\"\"\"
    
    def setUp(self):
        \"\"\"Set up test fixtures\"\"\"
        pass
    
    def tearDown(self):
        \"\"\"Clean up after tests\"\"\"
        pass
"""
            
            # Add test methods
            for i, test_case in enumerate(test_cases):
                test_method = f"""
    def test_{test_case.get('name', f'case_{i}')}(self):
        \"\"\"Test {test_case.get('description', 'test case')}\"\"\"
        # Arrange
        {test_case.get('setup', 'pass')}
        
        # Act
        result = {test_case.get('action', 'target_function()')}
        
        # Assert
        {test_case.get('assertion', 'self.assertTrue(result)')}
"""
                generated_code += test_method
        
        elif language == "javascript":
            generated_code = f"""const {{ expect }} = require('chai');
const {{ describe, it, beforeEach, afterEach }} = require('mocha');

describe('{test_target}', () => {{
    beforeEach(() => {{
        // Setup
    }});
    
    afterEach(() => {{
        // Cleanup
    }});
"""
            
            # Add test cases
            for test_case in test_cases:
                test_code = f"""
    it('{test_case.get('description', 'should work correctly')}', () => {{
        // Arrange
        {test_case.get('setup', '')}
        
        // Act
        const result = {test_case.get('action', 'targetFunction()')};
        
        // Assert
        {test_case.get('assertion', 'expect(result).to.be.true;')}
    }});
"""
                generated_code += test_code
            
            generated_code += "\n});"
        
        else:
            generated_code = f"""// Test code for {test_target}
// Test implementation
"""
        
        return generated_code
    
    async def _generate_generic_code(self, requirements: Dict[str, Any], language: str) -> str:
        """Generate generic code based on requirements"""
        
        code_type = requirements.get("type", "script")
        description = requirements.get("description", "Generated code")
        
        if language == "python":
            generated_code = f'''"""
{description}
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

def main():
    """Main function"""
    logger.info("Starting execution")
    
    # Implementation goes here
    
    logger.info("Execution completed")

if __name__ == "__main__":
    main()
'''
        
        elif language == "javascript":
            generated_code = f"""/**
 * {description}
 */

console.log('Starting execution');

// Implementation goes here

console.log('Execution completed');
"""
        
        else:
            generated_code = f"""// {description}
// Implementation goes here
"""
        
        return generated_code
    
    async def _validate_generated_code(self, code: str, language: str) -> Dict[str, Any]:
        """Validate generated code"""
        
        validation_result = {
            "syntax_valid": True,
            "style_compliant": True,
            "security_issues": [],
            "warnings": [],
            "suggestions": []
        }
        
        if language == "python":
            # Basic Python syntax validation
            try:
                ast.parse(code)
                validation_result["syntax_valid"] = True
            except SyntaxError as e:
                validation_result["syntax_valid"] = False
                validation_result["warnings"].append(f"Syntax error: {str(e)}")
        
        # Check for basic style issues
        if not re.search(r'"""[^"]*"""', code) and not re.search(r"'''[^']*'''", code):
            validation_result["suggestions"].append("Consider adding docstrings")
        
        if re.search(r'\btodo\b|\bfixme\b|\bhack\b', code.lower()):
            validation_result["warnings"].append("Code contains TODO/FIXME/HACK comments")
        
        return validation_result
    
    async def _estimate_code_complexity(self, code: str) -> Dict[str, Any]:
        """Estimate code complexity"""
        
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        complexity = {
            "total_lines": len(lines),
            "code_lines": len(non_empty_lines),
            "estimated_cyclomatic": 1,  # Base complexity
            "complexity_level": "low"
        }
        
        # Simple complexity estimation
        complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'with']
        
        for line in non_empty_lines:
            for keyword in complexity_keywords:
                if keyword in line.lower():
                    complexity["estimated_cyclomatic"] += 1
        
        # Determine complexity level
        if complexity["estimated_cyclomatic"] <= 5:
            complexity["complexity_level"] = "low"
        elif complexity["estimated_cyclomatic"] <= 10:
            complexity["complexity_level"] = "medium"
        else:
            complexity["complexity_level"] = "high"
        
        return complexity
    
    async def _generate_implementation_notes(self, code: str, requirements: Dict[str, Any]) -> List[str]:
        """Generate implementation notes"""
        
        notes = []
        
        # Add requirement-based notes
        if requirements.get("async"):
            notes.append("This is an async implementation - ensure proper await usage")
        
        if requirements.get("error_handling"):
            notes.append("Error handling has been implemented")
        
        # Add code-based notes
        if "import" in code:
            notes.append("External dependencies may be required")
        
        if "# TODO" in code or "# FIXME" in code:
            notes.append("Implementation contains TODO items that need attention")
        
        # Add general notes
        notes.append("Review and test the generated code before production use")
        notes.append("Consider adding additional error handling as needed")
        
        return notes
    
    async def _execute_code_analysis(self, task: AgentTask, language: str) -> Dict[str, Any]:
        """Execute code analysis task"""
        
        code_to_analyze = task.parameters.get("code", "")
        analysis_type = task.parameters.get("analysis_type", "comprehensive")
        
        if not code_to_analyze:
            raise ValueError("No code provided for analysis")
        
        # Perform different types of analysis
        analysis_results = {
            "syntax_analysis": await self._analyze_syntax(code_to_analyze, language),
            "complexity_analysis": await self._analyze_complexity({"generated_code": code_to_analyze}),
            "quality_analysis": await self._analyze_code_quality(code_to_analyze, language),
            "security_analysis": await self._analyze_security(code_to_analyze, language),
            "style_analysis": await self._analyze_style(code_to_analyze, language),
            "performance_analysis": await self._analyze_performance(code_to_analyze, language)
        }
        
        # Generate overall assessment
        overall_score = await self._calculate_overall_analysis_score(analysis_results)
        
        return {
            "analysis_results": analysis_results,
            "overall_score": overall_score,
            "recommendations": await self._generate_analysis_recommendations(analysis_results),
            "priority_issues": await self._identify_priority_issues(analysis_results)
        }
    
    async def _analyze_syntax(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code syntax"""
        
        syntax_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        if language == "python":
            try:
                ast.parse(code)
                syntax_result["valid"] = True
            except SyntaxError as e:
                syntax_result["valid"] = False
                syntax_result["errors"].append(f"Syntax error at line {e.lineno}: {e.msg}")
        
        return syntax_result
    
    async def _analyze_complexity(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code complexity"""
        
        code = result.get("generated_code", "")
        if not code:
            return {"complexity_score": 0, "level": "unknown"}
        
        return await self._estimate_code_complexity(code)
    
    async def _analyze_code_quality(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code quality"""
        
        quality_result = {
            "score": 0.0,
            "metrics": {},
            "issues": []
        }
        
        lines = code.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        # Basic quality metrics
        quality_result["metrics"] = {
            "total_lines": len(lines),
            "code_lines": len(non_empty_lines),
            "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
            "blank_lines": len(lines) - len(non_empty_lines)
        }
        
        # Calculate quality score
        score = 0.5  # Base score
        
        # Docstring presence
        if '"""' in code or "'''" in code:
            score += 0.2
        
        # Comment ratio
        comment_ratio = quality_result["metrics"]["comment_lines"] / max(1, quality_result["metrics"]["code_lines"])
        if comment_ratio > 0.1:
            score += 0.1
        
        # Function/class structure
        if 'def ' in code or 'class ' in code:
            score += 0.1
        
        # Error handling
        if 'try:' in code or 'except:' in code:
            score += 0.1
        
        quality_result["score"] = min(1.0, score)
        
        return quality_result
    
    async def _analyze_security(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code security"""
        
        security_result = {
            "risk_level": "low",
            "vulnerabilities": [],
            "recommendations": []
        }
        
        # Check for common security issues
        security_patterns = {
            "sql_injection": [r"execute\s*\([^)]*%", r"query\s*\([^)]*\+"],
            "command_injection": [r"os\.system\s*\(", r"subprocess\.call\s*\("],
            "hardcoded_secrets": [r"password\s*=\s*['\"][^'\"]+['\"]", r"api_key\s*=\s*['\"][^'\"]+['\"]"],
            "eval_usage": [r"\beval\s*\(", r"\bexec\s*\("]
        }
        
        for vulnerability_type, patterns in security_patterns.items():
            for pattern in patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    security_result["vulnerabilities"].append({
                        "type": vulnerability_type,
                        "pattern": pattern,
                        "severity": "high" if vulnerability_type in ["sql_injection", "command_injection"] else "medium"
                    })
        
        # Determine risk level
        if security_result["vulnerabilities"]:
            high_severity = [v for v in security_result["vulnerabilities"] if v["severity"] == "high"]
            if high_severity:
                security_result["risk_level"] = "high"
            else:
                security_result["risk_level"] = "medium"
        
        return security_result
    
    async def _analyze_style(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code style"""
        
        style_result = {
            "compliance_score": 0.0,
            "issues": [],
            "suggestions": []
        }
        
        if language == "python":
            # Basic PEP 8 checks
            lines = code.split('\n')
            
            # Check line length
            long_lines = [i for i, line in enumerate(lines) if len(line) > 79]
            if long_lines:
                style_result["issues"].append(f"Lines exceed 79 characters: {long_lines}")
            
            # Check indentation
            inconsistent_indentation = False
            for line in lines:
                if line.startswith(' ') and line.startswith('    '):
                    # Mixed spaces and tabs
                    inconsistent_indentation = True
                    break
            
            if inconsistent_indentation:
                style_result["issues"].append("Inconsistent indentation detected")
            
            # Calculate compliance score
            total_checks = 2
            passed_checks = total_checks - len(style_result["issues"])
            style_result["compliance_score"] = passed_checks / total_checks
        
        return style_result
    
    async def _analyze_performance(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code performance"""
        
        performance_result = {
            "performance_score": 0.0,
            "bottlenecks": [],
            "optimizations": []
        }
        
        # Check for performance anti-patterns
        if re.search(r'for\s+\w+\s+in\s+range\(len\(', code):
            performance_result["bottlenecks"].append("Use of range(len()) instead of enumerate()")
            performance_result["optimizations"].append("Replace range(len()) with enumerate()")
        
        if re.search(r'\+\s*=.*\[', code):
            performance_result["bottlenecks"].append("List concatenation in loop")
            performance_result["optimizations"].append("Use list comprehension or join()")
        
        # Calculate performance score
        base_score = 0.8
        penalty = len(performance_result["bottlenecks"]) * 0.1
        performance_result["performance_score"] = max(0.0, base_score - penalty)
        
        return performance_result
    
    async def _calculate_overall_analysis_score(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate overall analysis score"""
        
        scores = []
        
        # Extract scores from different analyses
        if analysis_results["syntax_analysis"]["valid"]:
            scores.append(1.0)
        else:
            scores.append(0.0)
        
        quality_score = analysis_results["quality_analysis"]["score"]
        scores.append(quality_score)
        
        # Security score (inverse of risk)
        security_risk = analysis_results["security_analysis"]["risk_level"]
        security_score = {"low": 1.0, "medium": 0.6, "high": 0.2}.get(security_risk, 0.5)
        scores.append(security_score)
        
        style_score = analysis_results["style_analysis"]["compliance_score"]
        scores.append(style_score)
        
        performance_score = analysis_results["performance_analysis"]["performance_score"]
        scores.append(performance_score)
        
        # Calculate weighted average
        return sum(scores) / len(scores) if scores else 0.0
    
    async def _generate_analysis_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        
        recommendations = []
        
        # Syntax recommendations
        if not analysis_results["syntax_analysis"]["valid"]:
            recommendations.append("Fix syntax errors before proceeding")
        
        # Quality recommendations
        quality_score = analysis_results["quality_analysis"]["score"]
        if quality_score < 0.7:
            recommendations.append("Improve code quality by adding documentation and comments")
        
        # Security recommendations
        security_vulns = analysis_results["security_analysis"]["vulnerabilities"]
        if security_vulns:
            recommendations.append("Address security vulnerabilities immediately")
        
        # Style recommendations
        style_score = analysis_results["style_analysis"]["compliance_score"]
        if style_score < 0.8:
            recommendations.append("Improve code style compliance")
        
        # Performance recommendations
        performance_score = analysis_results["performance_analysis"]["performance_score"]
        if performance_score < 0.7:
            recommendations.append("Optimize performance bottlenecks")
        
        return recommendations
    
    async def _identify_priority_issues(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Identify priority issues that need immediate attention"""
        
        priority_issues = []
        
        # High priority: Syntax errors
        if not analysis_results["syntax_analysis"]["valid"]:
            priority_issues.extend(analysis_results["syntax_analysis"]["errors"])
        
        # High priority: Security vulnerabilities
        security_vulns = analysis_results["security_analysis"]["vulnerabilities"]
        high_severity_vulns = [v for v in security_vulns if v["severity"] == "high"]
        if high_severity_vulns:
            priority_issues.append(f"High severity security vulnerabilities: {len(high_severity_vulns)}")
        
        # Medium priority: Performance bottlenecks
        bottlenecks = analysis_results["performance_analysis"]["bottlenecks"]
        if bottlenecks:
            priority_issues.extend(bottlenecks)
        
        return priority_issues
    
    async def _execute_code_refactoring(self, task: AgentTask, language: str) -> Dict[str, Any]:
        """Execute code refactoring task"""
        
        code_to_refactor = task.parameters.get("code", "")
        refactoring_goals = task.parameters.get("goals", ["readability", "maintainability"])
        
        if not code_to_refactor:
            raise ValueError("No code provided for refactoring")
        
        # Apply refactoring techniques
        refactored_code = code_to_refactor
        refactoring_actions = []
        
        for goal in refactoring_goals:
            if goal == "readability":
                refactored_code, actions = await self._improve_readability(refactored_code, language)
                refactoring_actions.extend(actions)
            elif goal == "maintainability":
                refactored_code, actions = await self._improve_maintainability(refactored_code, language)
                refactoring_actions.extend(actions)
            elif goal == "performance":
                refactored_code, actions = await self._improve_performance(refactored_code, language)
                refactoring_actions.extend(actions)
        
        # Compare before and after
        complexity_before = await self._estimate_code_complexity(code_to_refactor)
        complexity_after = await self._estimate_code_complexity(refactored_code)
        
        return {
            "original_code": code_to_refactor,
            "refactored_code": refactored_code,
            "refactoring_actions": refactoring_actions,
            "complexity_before": complexity_before,
            "complexity_after": complexity_after,
            "improvement_summary": await self._generate_improvement_summary(complexity_before, complexity_after, refactoring_actions)
        }
    
    async def _improve_readability(self, code: str, language: str) -> Tuple[str, List[str]]:
        """Improve code readability"""
        
        improved_code = code
        actions = []
        
        # Add meaningful variable names (simplified)
        if re.search(r'\b[a-z]\b', code):
            actions.append("Suggested improving variable names")
        
        # Add spacing improvements
        if not re.search(r'\n\s*\n', code):
            improved_code = re.sub(r'(\n)(def |class )', r'\1\n\2', improved_code)
            actions.append("Added spacing between functions/classes")
        
        return improved_code, actions
    
    async def _improve_maintainability(self, code: str, language: str) -> Tuple[str, List[str]]:
        """Improve code maintainability"""
        
        improved_code = code
        actions = []
        
        # Add docstrings if missing
        if '"""' not in code and "'''" not in code:
            if language == "python":
                # Add module docstring
                improved_code = '"""\nModule documentation\n"""\n\n' + improved_code
                actions.append("Added module docstring")
        
        return improved_code, actions
    
    async def _improve_performance(self, code: str, language: str) -> Tuple[str, List[str]]:
        """Improve code performance"""
        
        improved_code = code
        actions = []
        
        # Replace range(len()) with enumerate()
        if re.search(r'for\s+\w+\s+in\s+range\(len\(\w+\)\)', code):
            # This is a simplified replacement
            actions.append("Suggested replacing range(len()) with enumerate()")
        
        return improved_code, actions
    
    async def _generate_improvement_summary(self, complexity_before: Dict[str, Any], 
                                          complexity_after: Dict[str, Any], 
                                          actions: List[str]) -> Dict[str, Any]:
        """Generate improvement summary"""
        
        return {
            "complexity_improvement": {
                "before": complexity_before["estimated_cyclomatic"],
                "after": complexity_after["estimated_cyclomatic"],
                "reduction": complexity_before["estimated_cyclomatic"] - complexity_after["estimated_cyclomatic"]
            },
            "actions_taken": len(actions),
            "improvement_areas": list(set(action.split()[1] for action in actions if len(action.split()) > 1))
        }
    
    async def _execute_code_optimization(self, task: AgentTask, language: str) -> Dict[str, Any]:
        """Execute code optimization task"""
        
        code_to_optimize = task.parameters.get("code", "")
        optimization_targets = task.parameters.get("targets", ["performance"])
        
        if not code_to_optimize:
            raise ValueError("No code provided for optimization")
        
        # Apply optimization techniques
        optimized_code = code_to_optimize
        optimization_actions = []
        
        for target in optimization_targets:
            if target == "performance":
                optimized_code, actions = await self._optimize_performance(optimized_code, language)
                optimization_actions.extend(actions)
            elif target == "memory":
                optimized_code, actions = await self._optimize_memory(optimized_code, language)
                optimization_actions.extend(actions)
        
        return {
            "original_code": code_to_optimize,
            "optimized_code": optimized_code,
            "optimization_actions": optimization_actions,
            "estimated_improvement": await self._estimate_optimization_improvement(optimization_actions)
        }
    
    async def _optimize_performance(self, code: str, language: str) -> Tuple[str, List[str]]:
        """Optimize code performance"""
        
        optimized_code = code
        actions = []
        
        # Apply performance optimizations from rules
        for rule in self.optimization_rules["performance"]:
            if "list comprehensions" in rule.lower() and "for " in code:
                actions.append("Suggested using list comprehensions")
            elif "caching" in rule.lower() and "def " in code:
                actions.append("Suggested implementing caching")
        
        return optimized_code, actions
    
    async def _optimize_memory(self, code: str, language: str) -> Tuple[str, List[str]]:
        """Optimize code memory usage"""
        
        optimized_code = code
        actions = []
        
        # Apply memory optimizations from rules
        for rule in self.optimization_rules["memory"]:
            if "__slots__" in rule.lower() and "class " in code:
                actions.append("Suggested using __slots__")
            elif "context managers" in rule.lower() and "open(" in code:
                actions.append("Suggested using context managers")
        
        return optimized_code, actions
    
    async def _estimate_optimization_improvement(self, actions: List[str]) -> Dict[str, Any]:
        """Estimate optimization improvement"""
        
        improvement_estimates = {
            "performance": 0.0,
            "memory": 0.0,
            "maintainability": 0.0
        }
        
        for action in actions:
            if "performance" in action.lower() or "caching" in action.lower():
                improvement_estimates["performance"] += 0.2
            elif "memory" in action.lower() or "slots" in action.lower():
                improvement_estimates["memory"] += 0.15
            elif "comprehensions" in action.lower():
                improvement_estimates["performance"] += 0.1
                improvement_estimates["maintainability"] += 0.1
        
        return improvement_estimates
    
    async def _execute_documentation_generation(self, task: AgentTask, language: str) -> Dict[str, Any]:
        """Execute documentation generation task"""
        
        code_to_document = task.parameters.get("code", "")
        documentation_type = task.parameters.get("type", "docstrings")
        
        if not code_to_document:
            raise ValueError("No code provided for documentation")
        
        # Generate documentation
        if documentation_type == "docstrings":
            documentation = await self._generate_docstrings(code_to_document, language)
        elif documentation_type == "api":
            documentation = await self._generate_api_documentation(code_to_document, language)
        elif documentation_type == "user_guide":
            documentation = await self._generate_user_guide(code_to_document, language)
        else:
            documentation = await self._generate_general_documentation(code_to_document, language)
        
        return {
            "original_code": code_to_document,
            "documentation": documentation,
            "documentation_type": documentation_type,
            "coverage": await self._calculate_documentation_coverage(code_to_document, documentation)
        }
    
    async def _generate_docstrings(self, code: str, language: str) -> str:
        """Generate docstrings for code"""
        
        if language == "python":
            # Simple docstring generation
            lines = code.split('\n')
            documented_lines = []
            
            for line in lines:
                documented_lines.append(line)
                
                # Add docstring after function definition
                if re.match(r'\s*def\s+\w+\s*\(', line):
                    indent = len(line) - len(line.lstrip())
                    docstring = f'{" " * (indent + 4)}"""\n{" " * (indent + 4)}Function documentation\n{" " * (indent + 4)}"""'
                    documented_lines.append(docstring)
                
                # Add docstring after class definition
                elif re.match(r'\s*class\s+\w+', line):
                    indent = len(line) - len(line.lstrip())
                    docstring = f'{" " * (indent + 4)}"""\n{" " * (indent + 4)}Class documentation\n{" " * (indent + 4)}"""'
                    documented_lines.append(docstring)
            
            return '\n'.join(documented_lines)
        
        return f"// Documentation for code\n{code}"
    
    async def _generate_api_documentation(self, code: str, language: str) -> str:
        """Generate API documentation"""
        
        return f"""# API Documentation

## Overview
This module provides the following functionality:

## Functions
- Generated from code analysis

## Classes
- Generated from code analysis

## Usage Examples
```{language}
{code[:200]}...
```
"""
    
    async def _generate_user_guide(self, code: str, language: str) -> str:
        """Generate user guide"""
        
        return f"""# User Guide

## Getting Started
This guide explains how to use the code.

## Installation
Install the required dependencies.

## Usage
```{language}
{code[:200]}...
```

## Examples
See the examples section for common use cases.
"""
    
    async def _generate_general_documentation(self, code: str, language: str) -> str:
        """Generate general documentation"""
        
        return f"""# Documentation

## Code Overview
{code[:200]}...

## Implementation Details
This code implements functionality using {language}.

## Usage
See the code comments for usage information.
"""
    
    async def _calculate_documentation_coverage(self, code: str, documentation: str) -> float:
        """Calculate documentation coverage"""
        
        # Count functions and classes
        functions = len(re.findall(r'def\s+\w+', code))
        classes = len(re.findall(r'class\s+\w+', code))
        total_items = functions + classes
        
        if total_items == 0:
            return 1.0
        
        # Count documented items (simplified)
        documented_items = len(re.findall(r'"""[^"]*"""', documentation))
        
        return min(1.0, documented_items / total_items)
    
    async def _execute_bug_detection(self, task: AgentTask, language: str) -> Dict[str, Any]:
        """Execute bug detection task"""
        
        code_to_analyze = task.parameters.get("code", "")
        bug_types = task.parameters.get("bug_types", ["syntax", "logic", "runtime"])
        
        if not code_to_analyze:
            raise ValueError("No code provided for bug detection")
        
        # Detect different types of bugs
        detected_bugs = []
        
        for bug_type in bug_types:
            if bug_type == "syntax":
                bugs = await self._detect_syntax_bugs(code_to_analyze, language)
                detected_bugs.extend(bugs)
            elif bug_type == "logic":
                bugs = await self._detect_logic_bugs(code_to_analyze, language)
                detected_bugs.extend(bugs)
            elif bug_type == "runtime":
                bugs = await self._detect_runtime_bugs(code_to_analyze, language)
                detected_bugs.extend(bugs)
        
        return {
            "analyzed_code": code_to_analyze,
            "detected_bugs": detected_bugs,
            "bug_summary": await self._generate_bug_summary(detected_bugs),
            "fix_suggestions": await self._generate_fix_suggestions(detected_bugs)
        }
    
    async def _detect_syntax_bugs(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Detect syntax bugs"""
        
        bugs = []
        
        if language == "python":
            try:
                ast.parse(code)
            except SyntaxError as e:
                bugs.append({
                    "type": "syntax",
                    "severity": "high",
                    "line": e.lineno,
                    "message": e.msg,
                    "code": e.text
                })
        
        return bugs
    
    async def _detect_logic_bugs(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Detect logic bugs"""
        
        bugs = []
        
        # Check for common logic errors
        if re.search(r'if\s+\w+\s*=\s*', code):
            bugs.append({
                "type": "logic",
                "severity": "medium",
                "message": "Possible assignment in condition instead of comparison",
                "pattern": "if variable = value"
            })
        
        if re.search(r'while\s+True\s*:', code) and 'break' not in code:
            bugs.append({
                "type": "logic",
                "severity": "high",
                "message": "Infinite loop detected",
                "pattern": "while True without break"
            })
        
        return bugs
    
    async def _detect_runtime_bugs(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Detect potential runtime bugs"""
        
        bugs = []
        
        # Check for common runtime errors
        if re.search(r'1\s*/\s*0', code):
            bugs.append({
                "type": "runtime",
                "severity": "high",
                "message": "Division by zero",
                "pattern": "1/0"
            })
        
        if re.search(r'\[\s*\d+\s*\]', code):
            bugs.append({
                "type": "runtime",
                "severity": "medium",
                "message": "Potential index out of bounds",
                "pattern": "list[index]"
            })
        
        return bugs
    
    async def _generate_bug_summary(self, bugs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate bug summary"""
        
        summary = {
            "total_bugs": len(bugs),
            "by_severity": {"high": 0, "medium": 0, "low": 0},
            "by_type": {"syntax": 0, "logic": 0, "runtime": 0}
        }
        
        for bug in bugs:
            severity = bug.get("severity", "medium")
            bug_type = bug.get("type", "unknown")
            
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            summary["by_type"][bug_type] = summary["by_type"].get(bug_type, 0) + 1
        
        return summary
    
    async def _generate_fix_suggestions(self, bugs: List[Dict[str, Any]]) -> List[str]:
        """Generate fix suggestions for detected bugs"""
        
        suggestions = []
        
        for bug in bugs:
            if bug["type"] == "syntax":
                suggestions.append(f"Fix syntax error: {bug['message']}")
            elif bug["type"] == "logic":
                suggestions.append(f"Review logic: {bug['message']}")
            elif bug["type"] == "runtime":
                suggestions.append(f"Add error handling for: {bug['message']}")
        
        return suggestions
    
    async def _execute_general_code_task(self, task: AgentTask, language: str) -> Dict[str, Any]:
        """Execute general code task"""
        
        return {
            "task_type": "general",
            "language": language,
            "message": "General code task executed",
            "recommendations": ["Review task requirements", "Specify more detailed parameters"]
        }
    
    async def _calculate_code_quality_score(self, result: Dict[str, Any]) -> float:
        """Calculate overall code quality score"""
        
        if "generated_code" in result:
            complexity = result.get("complexity_analysis", {})
            if complexity:
                complexity_score = {"low": 0.9, "medium": 0.7, "high": 0.5}.get(
                    complexity.get("complexity_level", "medium"), 0.7
                )
                return complexity_score
        
        return 0.75  # Default score
    
    async def _generate_code_recommendations(self, result: Dict[str, Any], task: AgentTask) -> List[str]:
        """Generate code-specific recommendations"""
        
        recommendations = []
        
        if "validation" in result:
            validation = result["validation"]
            if not validation.get("syntax_valid", True):
                recommendations.append("Fix syntax errors before deployment")
            
            if validation.get("warnings"):
                recommendations.append("Address code warnings")
        
        if "complexity_analysis" in result:
            complexity = result["complexity_analysis"]
            if complexity.get("complexity_level") == "high":
                recommendations.append("Consider refactoring to reduce complexity")
        
        # Add general recommendations
        recommendations.extend([
            "Review and test the code thoroughly",
            "Consider adding comprehensive documentation",
            "Implement proper error handling"
        ])
        
        return recommendations
    
    async def _cleanup_agent_resources(self) -> None:
        """Cleanup code agent specific resources"""
        
        # Clear caches and templates
        self.code_templates.clear()
        self.code_patterns.clear()
        self.optimization_rules.clear()
        
        # Reset tools
        self.tools.clear()
        
        logger.info(f"Code agent {self.agent_id} resources cleaned up")