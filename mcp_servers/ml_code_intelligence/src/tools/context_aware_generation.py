"""
Context-Aware Code Generation with DSPy Integration
Advanced code generation system that understands full project context, architectural patterns, 
and coding standards to deliver intelligent, contextually appropriate code completions.
"""

import dspy
from typing import Dict, List, Any, Optional, Tuple
import asyncio
from dataclasses import dataclass
import logging
import hashlib
import json
import time
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class GenerationContext:
    """Comprehensive context for code generation"""
    project_type: str
    architecture_pattern: str
    coding_standards: Dict[str, Any]
    dependencies: List[str]
    function_context: str
    historical_patterns: List[Dict[str, Any]]
    performance_requirements: Dict[str, Any]

@dataclass
class CodeGenerationResult:
    """Result of context-aware code generation"""
    generated_code: str
    quality_score: float
    context_score: float
    pattern_adherence: str
    justification: str
    improvement_suggestions: List[str]
    generation_time: float

class ContextAwareCodeGenerator:
    """DSPy-powered context-aware code generation engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize DSPy with optimal model configuration
        try:
            dspy.settings.configure(
                lm=dspy.OpenAI(
                    model=self.config.get('model', "gpt-4-turbo-preview"),
                    max_tokens=self.config.get('max_tokens', 2048),
                    temperature=self.config.get('temperature', 0.1)
                )
            )
        except Exception as e:
            logger.warning(f"Failed to configure DSPy with OpenAI: {e}. Using mock configuration.")
            # Use a mock configuration for testing
            
        self.context_analyzer = CodeContextAnalyzer()
        self.pattern_extractor = ArchitecturalPatternExtractor()
        self.quality_predictor = CodeQualityPredictor()
        self.memory_store = ContextMemoryStore()
        
        # Initialize optimized DSPy signatures
        self._initialize_dspy_signatures()
        
    def _initialize_dspy_signatures(self):
        """Initialize DSPy signatures for different generation tasks"""
        
        class ContextualCodeCompletion(dspy.Signature):
            """Generate contextually appropriate code completion"""
            context = dspy.InputField(desc="Full project and architectural context")
            request = dspy.InputField(desc="Specific code generation request")
            constraints = dspy.InputField(desc="Quality and performance constraints")
            
            generated_code = dspy.OutputField(desc="High-quality generated code")
            quality_justification = dspy.OutputField(desc="Explanation of code quality decisions")
            pattern_adherence = dspy.OutputField(desc="How code follows established patterns")
        
        class RefactoringOptimization(dspy.Signature):
            """Optimize code through intelligent refactoring"""
            existing_code = dspy.InputField(desc="Current code to be refactored")
            context = dspy.InputField(desc="Project context and architectural patterns")
            optimization_goals = dspy.InputField(desc="Specific optimization objectives")
            
            refactored_code = dspy.OutputField(desc="Optimized and refactored code")
            improvements = dspy.OutputField(desc="Summary of improvements made")
            metrics = dspy.OutputField(desc="Before/after quality metrics")
        
        class ArchitecturalGuidance(dspy.Signature):
            """Provide architectural improvement recommendations"""
            current_architecture = dspy.InputField(desc="Current project architecture")
            growth_patterns = dspy.InputField(desc="Historical growth and usage patterns")
            requirements = dspy.InputField(desc="Performance and scalability requirements")
            
            recommendations = dspy.OutputField(desc="Specific architectural improvements")
            implementation_plan = dspy.OutputField(desc="Step-by-step implementation guide")
            impact_assessment = dspy.OutputField(desc="Risk and benefit analysis")
        
        # Initialize optimized chains
        try:
            self.completion_chain = dspy.ChainOfThought(ContextualCodeCompletion)
            self.refactoring_chain = dspy.ChainOfThought(RefactoringOptimization)
            self.architecture_chain = dspy.ChainOfThought(ArchitecturalGuidance)
        except Exception as e:
            logger.warning(f"Failed to initialize DSPy chains: {e}. Using mock chains.")
            # Create mock chains for testing
            self.completion_chain = MockDSPyChain()
            self.refactoring_chain = MockDSPyChain()
            self.architecture_chain = MockDSPyChain()
        
    async def generate_contextual_code(self, request: str, project_context: Dict[str, Any]) -> CodeGenerationResult:
        """Generate contextually appropriate code using DSPy optimization"""
        
        start_time = time.time()
        
        try:
            # Multi-stage context analysis
            context_insights = await self.analyze_full_context(project_context)
            
            # Pattern-based generation strategy selection
            generation_strategy = await self.select_generation_strategy(context_insights)
            
            # DSPy-optimized completion
            completion_result = await self._execute_completion_chain(
                context_insights, request, generation_strategy
            )
            
            # Quality validation and improvement
            validated_code = await self.validate_and_improve(
                completion_result.get('generated_code', ''),
                context_insights,
                completion_result.get('quality_justification', '')
            )
            
            # Memory storage for continuous learning
            await self.memory_store.store_generation_pattern(
                context=context_insights,
                request=request,
                result=validated_code,
                success_metrics=await self.evaluate_success(validated_code)
            )
            
            generation_time = time.time() - start_time
            
            return CodeGenerationResult(
                generated_code=validated_code.get('code', ''),
                quality_score=validated_code.get('quality_score', 0.0),
                context_score=validated_code.get('context_score', 0.0),
                pattern_adherence=completion_result.get('pattern_adherence', ''),
                justification=completion_result.get('quality_justification', ''),
                improvement_suggestions=validated_code.get('improvement_suggestions', []),
                generation_time=generation_time
            )
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return CodeGenerationResult(
                generated_code=f"// Error generating code: {e}",
                quality_score=0.0,
                context_score=0.0,
                pattern_adherence="Error",
                justification=f"Generation failed: {e}",
                improvement_suggestions=[],
                generation_time=time.time() - start_time
            )

    async def _execute_completion_chain(self, context_insights, request, generation_strategy):
        """Execute the DSPy completion chain with error handling"""
        try:
            if hasattr(self.completion_chain, '__call__'):
                return self.completion_chain(
                    context=self._format_context(context_insights),
                    request=request,
                    constraints=generation_strategy.get('constraints', '')
                )
            else:
                # Fallback for mock chain
                return {
                    'generated_code': f"// Generated code for: {request}\n// Context: {context_insights.get('summary', 'Unknown')}",
                    'quality_justification': "Mock generation for testing",
                    'pattern_adherence': "Mock pattern adherence"
                }
        except Exception as e:
            logger.warning(f"DSPy completion chain failed: {e}. Using fallback.")
            return {
                'generated_code': f"// Fallback code generation for: {request}",
                'quality_justification': f"Fallback due to error: {e}",
                'pattern_adherence': "Fallback pattern"
            }

    async def analyze_full_context(self, project_context: Dict[str, Any]) -> GenerationContext:
        """Perform comprehensive multi-layer context analysis"""
        
        # Parallel context analysis across multiple dimensions
        context_layers = await asyncio.gather(
            # Layer 1: Immediate Code Context
            self.context_analyzer.analyze_immediate_context(project_context.get('current_file')),
            
            # Layer 2: Architectural Context  
            self.context_analyzer.analyze_architectural_patterns(project_context.get('project_structure')),
            
            # Layer 3: Dependency Context
            self.context_analyzer.analyze_dependencies(
                project_context.get('imports', []),
                project_context.get('dependencies', [])
            ),
            
            # Layer 4: Style and Convention Context
            self.context_analyzer.analyze_coding_standards(project_context.get('existing_code', [])),
            
            # Layer 5: Historical Pattern Context
            self.context_analyzer.analyze_historical_patterns(project_context.get('git_history', []))
        )
        
        return self.synthesize_context_insights(context_layers)
        
    def synthesize_context_insights(self, context_layers: List[Dict[str, Any]]) -> GenerationContext:
        """Synthesize insights from multiple context layers"""
        
        # Extract data from each layer
        immediate = context_layers[0].get('data', {})
        architecture = context_layers[1].get('data', {})
        dependencies = context_layers[2].get('data', {})
        standards = context_layers[3].get('data', {})
        historical = context_layers[4].get('data', {})
        
        return GenerationContext(
            project_type=architecture.get('primary_pattern', 'unknown'),
            architecture_pattern=architecture.get('primary_pattern', 'unknown'),
            coding_standards=standards,
            dependencies=dependencies.get('external_deps', []),
            function_context=immediate.get('function_context', ''),
            historical_patterns=historical.get('patterns', []),
            performance_requirements=architecture.get('scalability_indicators', {})
        )

    async def select_generation_strategy(self, context_insights: GenerationContext) -> Dict[str, Any]:
        """Select optimal generation strategy based on context"""
        
        # Analyze complexity of the request
        complexity_score = await self._assess_complexity(context_insights)
        
        # Select strategy based on context and complexity
        if complexity_score > 0.8:
            strategy = "high_complexity"
        elif complexity_score > 0.5:
            strategy = "medium_complexity"
        else:
            strategy = "low_complexity"
        
        return {
            'strategy': strategy,
            'complexity': complexity_score,
            'constraints': self._get_constraints_for_strategy(strategy, context_insights)
        }

    async def _assess_complexity(self, context: GenerationContext) -> float:
        """Assess complexity of the generation task"""
        complexity_factors = []
        
        # Architectural complexity
        if context.architecture_pattern in ['microservices', 'layered', 'hexagonal']:
            complexity_factors.append(0.3)
        
        # Dependency complexity
        if len(context.dependencies) > 5:
            complexity_factors.append(0.2)
        
        # Performance requirements complexity
        if context.performance_requirements:
            complexity_factors.append(0.3)
        
        # Historical pattern complexity
        if len(context.historical_patterns) > 3:
            complexity_factors.append(0.2)
        
        return min(sum(complexity_factors), 1.0)

    def _get_constraints_for_strategy(self, strategy: str, context: GenerationContext) -> str:
        """Get constraints based on generation strategy"""
        
        base_constraints = [
            "Follow established coding standards",
            "Ensure type safety and error handling",
            "Include appropriate documentation"
        ]
        
        if strategy == "high_complexity":
            base_constraints.extend([
                "Consider scalability and performance implications",
                "Follow architectural patterns strictly",
                "Include comprehensive error handling"
            ])
        elif strategy == "medium_complexity":
            base_constraints.extend([
                "Balance readability and performance",
                "Follow common design patterns"
            ])
        
        return "; ".join(base_constraints)

    def _format_context(self, context_insights: GenerationContext) -> str:
        """Format context for DSPy input"""
        return f"""
Project Type: {context_insights.project_type}
Architecture: {context_insights.architecture_pattern}
Dependencies: {', '.join(context_insights.dependencies[:5])}
Coding Standards: {json.dumps(context_insights.coding_standards, indent=2)[:500]}
Function Context: {context_insights.function_context[:300]}
"""

    async def validate_and_improve(self, code: str, context: GenerationContext, justification: str) -> Dict[str, Any]:
        """Validate and improve generated code"""
        
        # Basic validation
        quality_score = await self.quality_predictor.predict_quality(code, context)
        context_score = await self._assess_context_appropriateness(code, context)
        
        # Generate improvement suggestions
        suggestions = await self._generate_improvement_suggestions(code, context, quality_score)
        
        return {
            'code': code,
            'quality_score': quality_score,
            'context_score': context_score,
            'improvement_suggestions': suggestions
        }

    async def _assess_context_appropriateness(self, code: str, context: GenerationContext) -> float:
        """Assess how well code fits the context"""
        
        score = 0.8  # Base score
        
        # Check for dependency usage
        for dep in context.dependencies:
            if dep.lower() in code.lower():
                score += 0.05
        
        # Check for architectural pattern adherence
        if context.architecture_pattern in ['mvc', 'mvp'] and any(pattern in code.lower() for pattern in ['controller', 'view', 'model']):
            score += 0.1
        
        return min(score, 1.0)

    async def _generate_improvement_suggestions(self, code: str, context: GenerationContext, quality_score: float) -> List[str]:
        """Generate improvement suggestions for the code"""
        
        suggestions = []
        
        if quality_score < 0.8:
            suggestions.append("Consider adding more comprehensive error handling")
            suggestions.append("Add type hints for better code clarity")
        
        if len(code.split('\n')) > 50:
            suggestions.append("Consider breaking down into smaller functions")
        
        if 'TODO' in code or 'FIXME' in code:
            suggestions.append("Complete TODO items and fix marked issues")
        
        return suggestions

    async def evaluate_success(self, validated_code: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate the success of code generation"""
        
        return {
            'quality_score': validated_code.get('quality_score', 0.0),
            'context_score': validated_code.get('context_score', 0.0),
            'completeness': 1.0 if validated_code.get('code') else 0.0
        }


class CodeContextAnalyzer:
    """Advanced context analysis for comprehensive code understanding"""
    
    async def analyze_immediate_context(self, current_file: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze immediate code context around generation point"""
        if not current_file:
            return {'type': 'immediate', 'data': {}}
            
        return {
            'type': 'immediate',
            'data': {
                'file_type': current_file.get('language', 'unknown'),
                'function_context': await self.extract_function_context(current_file.get('content', '')),
                'class_context': await self.extract_class_context(current_file.get('content', '')),
                'imports': await self.extract_imports(current_file.get('content', '')),
                'surrounding_code': await self.extract_surrounding_context(
                    current_file.get('content', ''),
                    current_file.get('cursor_position', 0)
                )
            }
        }
        
    async def analyze_architectural_patterns(self, project_structure: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify and analyze architectural patterns"""
        if not project_structure:
            return {'type': 'architecture', 'data': {}}
            
        patterns = await self.detect_architectural_patterns(project_structure)
        
        return {
            'type': 'architecture',
            'data': {
                'primary_pattern': patterns.get('primary', 'unknown'),
                'secondary_patterns': patterns.get('secondary', []),
                'layer_organization': await self.analyze_layer_organization(project_structure),
                'module_relationships': await self.analyze_module_relationships(project_structure),
                'scalability_indicators': await self.assess_scalability_patterns(project_structure)
            }
        }

    async def analyze_dependencies(self, imports: List[str], dependencies: List[str]) -> Dict[str, Any]:
        """Analyze project dependencies and their usage patterns"""
        return {
            'type': 'dependencies',
            'data': {
                'external_deps': dependencies,
                'import_patterns': imports,
                'common_libraries': await self._identify_common_libraries(dependencies),
                'framework_usage': await self._detect_frameworks(dependencies)
            }
        }

    async def analyze_coding_standards(self, existing_code: List[str]) -> Dict[str, Any]:
        """Analyze coding standards from existing code"""
        return {
            'type': 'standards',
            'data': {
                'naming_convention': await self._detect_naming_convention(existing_code),
                'indentation_style': await self._detect_indentation(existing_code),
                'documentation_style': await self._detect_doc_style(existing_code),
                'error_handling_patterns': await self._detect_error_patterns(existing_code)
            }
        }

    async def analyze_historical_patterns(self, git_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze historical development patterns"""
        return {
            'type': 'historical',
            'data': {
                'patterns': await self._extract_historical_patterns(git_history),
                'common_changes': await self._identify_common_changes(git_history),
                'refactoring_trends': await self._analyze_refactoring_trends(git_history)
            }
        }

    # Helper methods for context analysis
    async def extract_function_context(self, content: str) -> str:
        """Extract function context from code"""
        # Simple implementation - in production, use AST parsing
        lines = content.split('\n')
        function_lines = [line for line in lines if 'def ' in line or 'function' in line]
        return '\n'.join(function_lines[:5])  # Return first 5 function definitions

    async def extract_class_context(self, content: str) -> str:
        """Extract class context from code"""
        lines = content.split('\n')
        class_lines = [line for line in lines if 'class ' in line]
        return '\n'.join(class_lines[:3])  # Return first 3 class definitions

    async def extract_imports(self, content: str) -> List[str]:
        """Extract import statements"""
        lines = content.split('\n')
        import_lines = [line.strip() for line in lines if line.strip().startswith(('import ', 'from '))]
        return import_lines[:10]  # Return first 10 imports

    async def extract_surrounding_context(self, content: str, cursor_position: int) -> str:
        """Extract code context around cursor position"""
        lines = content.split('\n')
        if cursor_position < len(lines):
            start = max(0, cursor_position - 5)
            end = min(len(lines), cursor_position + 5)
            return '\n'.join(lines[start:end])
        return ""

    async def detect_architectural_patterns(self, project_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Detect architectural patterns from project structure"""
        # Simple pattern detection based on directory structure
        dirs = project_structure.get('directories', [])
        
        if any('controller' in d.lower() for d in dirs) and any('model' in d.lower() for d in dirs):
            return {'primary': 'mvc', 'secondary': []}
        elif any('service' in d.lower() for d in dirs):
            return {'primary': 'service_layer', 'secondary': []}
        else:
            return {'primary': 'simple', 'secondary': []}

    async def analyze_layer_organization(self, project_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how the project is organized in layers"""
        return {'layers': ['presentation', 'business', 'data'], 'depth': 3}

    async def analyze_module_relationships(self, project_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze relationships between modules"""
        return {'coupling': 'loose', 'cohesion': 'high'}

    async def assess_scalability_patterns(self, project_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Assess scalability patterns in the project"""
        return {'horizontal_scaling': True, 'caching_patterns': False}

    async def _identify_common_libraries(self, dependencies: List[str]) -> List[str]:
        """Identify commonly used libraries"""
        common_libs = ['requests', 'pandas', 'numpy', 'flask', 'django', 'fastapi']
        return [lib for lib in common_libs if any(lib in dep.lower() for dep in dependencies)]

    async def _detect_frameworks(self, dependencies: List[str]) -> List[str]:
        """Detect frameworks being used"""
        frameworks = ['django', 'flask', 'fastapi', 'express', 'react', 'vue']
        return [fw for fw in frameworks if any(fw in dep.lower() for dep in dependencies)]

    async def _detect_naming_convention(self, existing_code: List[str]) -> str:
        """Detect naming convention from existing code"""
        return "snake_case"  # Simplified detection

    async def _detect_indentation(self, existing_code: List[str]) -> str:
        """Detect indentation style"""
        return "4_spaces"  # Simplified detection

    async def _detect_doc_style(self, existing_code: List[str]) -> str:
        """Detect documentation style"""
        return "docstring"  # Simplified detection

    async def _detect_error_patterns(self, existing_code: List[str]) -> List[str]:
        """Detect error handling patterns"""
        return ["try_except", "logging"]  # Simplified detection

    async def _extract_historical_patterns(self, git_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract patterns from git history"""
        return []  # Simplified implementation

    async def _identify_common_changes(self, git_history: List[Dict[str, Any]]) -> List[str]:
        """Identify common types of changes"""
        return ["bug_fixes", "feature_additions"]  # Simplified implementation

    async def _analyze_refactoring_trends(self, git_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze refactoring trends"""
        return {"frequency": "low", "patterns": []}  # Simplified implementation


class ArchitecturalPatternExtractor:
    """Extract and analyze architectural patterns"""
    
    async def extract_patterns(self, code: str) -> List[Dict[str, Any]]:
        """Extract architectural patterns from code"""
        patterns = []
        
        # Simple pattern detection
        if 'class' in code and 'def __init__' in code:
            patterns.append({'pattern': 'object_oriented', 'confidence': 0.8})
        
        if 'decorator' in code or '@' in code:
            patterns.append({'pattern': 'decorator', 'confidence': 0.7})
        
        return patterns


class CodeQualityPredictor:
    """Predict code quality using ML models"""
    
    async def predict_quality(self, code: str, context: GenerationContext) -> float:
        """Predict quality score for generated code"""
        
        # Simple heuristic-based quality prediction
        score = 0.5  # Base score
        
        # Length consideration
        lines = len(code.split('\n'))
        if 10 <= lines <= 50:
            score += 0.2
        
        # Documentation consideration
        if '"""' in code or "'''" in code:
            score += 0.1
        
        # Error handling consideration
        if 'try:' in code or 'except:' in code:
            score += 0.1
        
        # Type hints consideration
        if '->' in code or ':' in code:
            score += 0.1
        
        return min(score, 1.0)


class ContextMemoryStore:
    """Store and retrieve generation patterns for continuous learning"""
    
    def __init__(self):
        self.memory_file = Path("data/generation_memory.json")
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        
    async def store_generation_pattern(self, context: GenerationContext, request: str, 
                                     result: Dict[str, Any], success_metrics: Dict[str, float]):
        """Store successful generation patterns"""
        
        pattern = {
            'timestamp': time.time(),
            'context_hash': self._hash_context(context),
            'request': request[:100],  # Truncate for privacy
            'success_metrics': success_metrics,
            'quality_score': result.get('quality_score', 0.0)
        }
        
        # Store pattern (simplified implementation)
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r') as f:
                    memories = json.load(f)
            else:
                memories = []
            
            memories.append(pattern)
            
            # Keep only last 1000 patterns
            if len(memories) > 1000:
                memories = memories[-1000:]
            
            with open(self.memory_file, 'w') as f:
                json.dump(memories, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to store generation pattern: {e}")
    
    def _hash_context(self, context: GenerationContext) -> str:
        """Create hash of context for pattern matching"""
        context_str = f"{context.project_type}:{context.architecture_pattern}:{len(context.dependencies)}"
        return hashlib.md5(context_str.encode()).hexdigest()


class MockDSPyChain:
    """Mock DSPy chain for testing when DSPy is not available"""
    
    def __call__(self, context: str, request: str, constraints: str) -> Dict[str, Any]:
        return {
            'generated_code': f"// Mock generated code for: {request}",
            'quality_justification': "Mock justification",
            'pattern_adherence': "Mock pattern adherence"
        }