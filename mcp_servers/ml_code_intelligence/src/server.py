"""
ML-Powered Code Intelligence MCP Server
Advanced code analysis, semantic search, and quality assessment using ML models
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json
import time

# Add shared utilities to path
sys.path.append(str(Path(__file__).parent.parent.parent / "shared" / "src"))

from base_server import BaseMCPServer, ServerConfig, BaseRequest, BaseResponse
from utils.ml_utils import EmbeddingManager, EmbeddingConfig, VectorDatabase
from utils.code_utils import GeneralCodeAnalyzer, LanguageDetector, get_code_summary, CodeMetrics, CodeIssue
from utils.config_utils import MCPServerSettings, ConfigManager
from tools.advanced_analysis import enhance_code_analysis, AdvancedPythonAnalyzer
from tools.quality_assessment import assess_code_quality, CodeQualityAnalyzer
from tools.context_aware_generation import ContextAwareCodeGenerator, CodeGenerationResult
from tools.multimodal_analysis import MultiModalCodeAnalyzer, MultiModalAnalysisResult
from tools.prompt_optimizer import PromptOptimizationEngine, OptimizationResult
from utils.performance_monitor import PerformanceMonitor, SmartCache, PerformanceOptimizer

from pydantic import BaseModel, Field
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeSearchRequest(BaseModel):
    """Request for semantic code search"""
    query: str = Field(..., description="Search query or code snippet")
    language: Optional[str] = Field(None, description="Programming language filter")
    max_results: int = Field(10, description="Maximum number of results")
    similarity_threshold: float = Field(0.5, description="Minimum similarity score")


class CodeSearchResult(BaseModel):
    """Code search result"""
    code: str = Field(..., description="Code snippet")
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    language: str = Field(..., description="Programming language")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")


class CodeAnalysisRequest(BaseModel):
    """Request for code analysis"""
    code: str = Field(..., description="Code to analyze")
    language: Optional[str] = Field(None, description="Programming language")
    include_metrics: bool = Field(True, description="Include code metrics")
    include_issues: bool = Field(True, description="Include code issues")
    include_advanced: bool = Field(False, description="Include advanced analysis (refactoring, patterns, architecture)")
    include_suggestions: bool = Field(False, description="Include refactoring suggestions")


class CodeAnalysisResponse(BaseModel):
    """Code analysis response"""
    language: str = Field(..., description="Detected programming language")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Code metrics")
    issues: Optional[List[Dict[str, Any]]] = Field(None, description="Code issues")
    summary: Dict[str, Any] = Field(..., description="Code summary")
    advanced_analysis: Optional[Dict[str, Any]] = Field(None, description="Advanced analysis results")
    refactoring_suggestions: Optional[List[Dict[str, Any]]] = Field(None, description="Refactoring suggestions")


class CodeIndexRequest(BaseModel):
    """Request to index code snippets"""
    code_snippets: List[Dict[str, Any]] = Field(..., description="Code snippets to index")
    batch_size: int = Field(32, description="Batch size for processing")


class MLCodeIntelligenceServer(BaseMCPServer):
    """Enhanced ML-Powered Code Intelligence MCP Server with Advanced AI Capabilities"""
    
    def __init__(self, config: MCPServerSettings):
        # Initialize base server
        super().__init__(ServerConfig(
            name=config.server_name,
            version=config.server_version,
            debug=config.debug,
            max_workers=config.max_workers,
            cache_ttl=config.cache_ttl
        ))
        
        self.settings = config
        self.embedding_manager = None
        self.vector_db = None
        self.code_analyzer = GeneralCodeAnalyzer()
        self.indexed_code_count = 0
        
        # Initialize enhanced components
        self.context_generator = None
        self.multimodal_analyzer = None
        self.prompt_optimizer = None
        
        # Initialize performance monitoring and caching
        self.performance_monitor = None
        self.smart_cache = None
        self.performance_optimizer = None
        
        # Register tools
        self._register_tools()
        
        # Register prompts
        self._register_prompts()
    
    def _register_tools(self):
        """Register all MCP tools"""
        
        @self.register_tool(
            name="semantic_code_search",
            description="Search for code snippets using semantic similarity"
        )
        async def semantic_code_search(request: CodeSearchRequest) -> List[CodeSearchResult]:
            """Search for similar code using semantic embeddings"""
            return await self._semantic_search(request)
        
        @self.register_tool(
            name="analyze_code",
            description="Analyze code for metrics, issues, and quality assessment"
        )
        async def analyze_code(request: CodeAnalysisRequest) -> CodeAnalysisResponse:
            """Analyze code and return metrics and issues"""
            return await self._analyze_code(request)
        
        @self.register_tool(
            name="index_code_snippets",
            description="Index code snippets for semantic search"
        )
        async def index_code_snippets(request: CodeIndexRequest) -> Dict[str, Any]:
            """Index code snippets for search"""
            return await self._index_code_snippets(request)
        
        @self.register_tool(
            name="get_server_stats",
            description="Get server statistics and status"
        )
        async def get_stats() -> Dict[str, Any]:
            """Get comprehensive server statistics"""
            stats = await self.get_server_stats()
            stats.update({
                "indexed_code_count": self.indexed_code_count,
                "embedding_model": self.settings.embedding_model,
                "vector_db_type": self.settings.vector_db_type,
                "ml_device": self.settings.ml_device
            })
            return stats
        
        @self.register_tool(
            name="get_supported_languages",
            description="Get list of supported programming languages"
        )
        async def get_supported_languages() -> List[str]:
            """Get supported programming languages"""
            return list(LanguageDetector.LANGUAGE_PATTERNS.keys())
        
        @self.register_tool(
            name="advanced_code_analysis",
            description="Perform advanced code analysis with refactoring suggestions and pattern detection"
        )
        async def advanced_code_analysis(code: str, language: Optional[str] = None) -> Dict[str, Any]:
            """Perform advanced code analysis"""
            return await self._advanced_analysis(code, language)
        
        @self.register_tool(
            name="get_refactoring_suggestions",
            description="Get refactoring suggestions for code improvement"
        )
        async def get_refactoring_suggestions(code: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
            """Get refactoring suggestions"""
            result = await self._advanced_analysis(code, language)
            return result.get('advanced_analysis', {}).get('refactoring_suggestions', [])
        
        @self.register_tool(
            name="detect_code_patterns",
            description="Detect design patterns and anti-patterns in code"
        )
        async def detect_code_patterns(code: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
            """Detect code patterns"""
            result = await self._advanced_analysis(code, language)
            return result.get('advanced_analysis', {}).get('detected_patterns', [])
        
        @self.register_tool(
            name="assess_code_quality",
            description="Comprehensive code quality assessment with scores and improvement recommendations"
        )
        async def assess_code_quality_tool(code: str, language: Optional[str] = None, include_trends: bool = False) -> Dict[str, Any]:
            """Assess comprehensive code quality"""
            return await self._assess_quality(code, language, include_trends)
        
        @self.register_tool(
            name="get_quality_metrics",
            description="Get detailed quality metrics for code assessment"
        )
        async def get_quality_metrics(code: str, language: Optional[str] = None) -> Dict[str, Any]:
            """Get quality metrics"""
            result = await self._assess_quality(code, language, False)
            return {
                'overall_score': result.get('overall_score', 0),
                'category_scores': result.get('category_scores', {}),
                'technical_debt_ratio': result.get('technical_debt_ratio', 0),
                'maintainability_index': result.get('maintainability_index', 0)
            }
        
        @self.register_tool(
            name="get_improvement_priorities",
            description="Get prioritized list of code improvements"
        )
        async def get_improvement_priorities(code: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
            """Get improvement priorities"""
            result = await self._assess_quality(code, language, False)
            return result.get('improvement_priorities', [])
        
        # Enhanced AI-powered tools
        @self.register_tool(
            name="generate_context_aware_code",
            description="Generate contextually appropriate code using advanced AI with full project understanding"
        )
        async def generate_context_aware_code(
            request: str,
            project_path: Optional[str] = None,
            context_type: str = "full",
            quality_target: float = 0.95
        ) -> Dict[str, Any]:
            """
            Generate context-aware code with DSPy optimization
            
            Args:
                request: Specific code generation request
                project_path: Path to project for context analysis
                context_type: Type of context analysis (quick, standard, full)
                quality_target: Target quality score (0.0-1.0)
            
            Returns:
                Generated code with quality metrics and explanations
            """
            
            if not self.context_generator:
                return {"error": "Context generator not initialized"}
            
            try:
                # Analyze project context
                project_context = await self._analyze_project_context(project_path, context_type)
                
                # Generate contextual code
                result = await self.context_generator.generate_contextual_code(
                    request, project_context
                )
                
                # Validate quality target
                if result.quality_score < quality_target:
                    # Trigger iterative improvement
                    result = await self._improve_generation(result, quality_target)
                
                return {
                    'generated_code': result.generated_code,
                    'quality_score': result.quality_score,
                    'context_score': result.context_score,
                    'pattern_adherence': result.pattern_adherence,
                    'justification': result.justification,
                    'improvement_suggestions': result.improvement_suggestions,
                    'generation_time': result.generation_time
                }
                
            except Exception as e:
                logger.error(f"Context-aware code generation failed: {e}")
                return {"error": f"Code generation failed: {e}"}
        
        @self.register_tool(
            name="analyze_cross_modal_consistency",
            description="Analyze consistency and alignment between code, documentation, and tests"
        )
        async def analyze_cross_modal_consistency(
            project_path: str,
            consistency_threshold: float = 0.8
        ) -> Dict[str, Any]:
            """
            Comprehensive cross-modal consistency analysis
            
            Args:
                project_path: Path to project for analysis
                consistency_threshold: Minimum consistency score (0.0-1.0)
            
            Returns:
                Detailed consistency report with discrepancy identification
            """
            
            if not self.multimodal_analyzer:
                return {"error": "Multi-modal analyzer not initialized"}
            
            try:
                # Gather project artifacts
                project_artifacts = await self._collect_project_artifacts(project_path)
                
                # Multi-modal analysis
                unified_analysis = await self.multimodal_analyzer.analyze_unified_context(project_artifacts)
                
                # Consistency checking
                consistency_results = await self._check_consistency(
                    unified_analysis, consistency_threshold
                )
                
                return {
                    'overall_consistency_score': consistency_results.consistency_analysis.get('overall_score', 0.0),
                    'modality_consistency': consistency_results.consistency_analysis.get('modality_scores', {}),
                    'inconsistencies': consistency_results.consistency_analysis.get('inconsistencies', []),
                    'improvement_suggestions': consistency_results.consistency_analysis.get('suggestions', []),
                    'priority_fixes': consistency_results.consistency_analysis.get('priority_fixes', [])
                }
                
            except Exception as e:
                logger.error(f"Cross-modal consistency analysis failed: {e}")
                return {"error": f"Consistency analysis failed: {e}"}
        
        @self.register_tool(
            name="optimize_prompt_for_task",
            description="Optimize prompt templates for specific tasks using advanced PromptBreeder techniques"
        )
        async def optimize_prompt_for_task(
            task_type: str,
            current_template: str,
            performance_target: float = 0.95,
            optimization_cycles: int = 10
        ) -> Dict[str, Any]:
            """
            Optimize prompt templates using PromptBreeder evolution
            
            Args:
                task_type: Type of task (code_generation, analysis, refactoring)
                current_template: Current prompt template to optimize
                performance_target: Target performance score (0.0-1.0)
                optimization_cycles: Number of optimization cycles
            
            Returns:
                Optimized template with performance predictions and evolution history
            """
            
            if not self.prompt_optimizer:
                return {"error": "Prompt optimizer not initialized"}
            
            try:
                # Optimize template
                optimization_result = await self.prompt_optimizer.optimize_template_for_task(
                    base_template=current_template,
                    task_type=task_type,
                    target_performance=performance_target
                )
                
                return {
                    'optimized_template': optimization_result.optimized_template.content,
                    'performance_improvement': optimization_result.improvement_score,
                    'optimization_history': optimization_result.optimization_history,
                    'performance_predictions': optimization_result.performance_predictions
                }
                
            except Exception as e:
                logger.error(f"Prompt optimization failed: {e}")
                return {"error": f"Prompt optimization failed: {e}"}
        
        @self.register_tool(
            name="generate_unified_project_summary",
            description="Create comprehensive project understanding summary from all available sources"
        )
        async def generate_unified_project_summary(
            project_path: str,
            summary_depth: str = "comprehensive"
        ) -> Dict[str, Any]:
            """
            Generate unified project understanding from multiple modalities
            
            Args:
                project_path: Path to project for analysis
                summary_depth: Depth of analysis (quick, standard, comprehensive)
            
            Returns:
                Multi-modal project insights and comprehensive summary
            """
            
            if not self.multimodal_analyzer:
                return {"error": "Multi-modal analyzer not initialized"}
            
            try:
                # Collect project artifacts
                project_artifacts = await self._collect_project_artifacts(project_path)
                
                # Unified context analysis
                unified_analysis = await self.multimodal_analyzer.analyze_unified_context(project_artifacts)
                
                # Generate human-readable summary
                summary = await self._generate_project_summary(unified_analysis, summary_depth)
                
                return {
                    'executive_summary': summary.get('executive', 'No summary available'),
                    'technical_overview': summary.get('technical', 'No technical overview available'),
                    'architecture_analysis': summary.get('architecture', 'No architecture analysis available'),
                    'quality_assessment': summary.get('quality', {}),
                    'recommendations': summary.get('recommendations', []),
                    'cross_modal_insights': unified_analysis.unified_insights
                }
                
            except Exception as e:
                logger.error(f"Unified project summary generation failed: {e}")
                return {"error": f"Project summary generation failed: {e}"}
        
        # Performance monitoring and optimization tools
        @self.register_tool(
            name="get_performance_stats",
            description="Get comprehensive performance statistics and monitoring data"
        )
        async def get_performance_stats(
            time_window: Optional[float] = None,
            include_cache_stats: bool = True
        ) -> Dict[str, Any]:
            """
            Get performance statistics and monitoring data
            
            Args:
                time_window: Time window in seconds for statistics (None for all time)
                include_cache_stats: Whether to include cache statistics
            
            Returns:
                Comprehensive performance statistics
            """
            
            if not self.performance_monitor:
                return {"error": "Performance monitoring not available"}
            
            try:
                stats = {
                    'overall_stats': self.performance_monitor.get_overall_stats(),
                    'alerts': self.performance_monitor.get_alerts(limit=20),
                    'active_operations': len(self.performance_monitor.active_operations)
                }
                
                if include_cache_stats and self.smart_cache:
                    stats['cache_stats'] = self.smart_cache.get_stats()
                
                # Add operation-specific stats
                operation_stats = {}
                for operation_name in self.performance_monitor.operation_stats.keys():
                    operation_stats[operation_name] = self.performance_monitor.get_operation_stats(
                        operation_name, time_window
                    )
                stats['operation_stats'] = operation_stats
                
                return stats
                
            except Exception as e:
                logger.error(f"Failed to get performance stats: {e}")
                return {"error": f"Performance stats failed: {e}"}
        
        @self.register_tool(
            name="get_optimization_recommendations",
            description="Get performance optimization recommendations based on current metrics"
        )
        async def get_optimization_recommendations() -> Dict[str, Any]:
            """
            Get performance optimization recommendations
            
            Returns:
                Optimization recommendations and suggestions
            """
            
            if not self.performance_optimizer:
                return {"error": "Performance optimizer not available"}
            
            try:
                analysis = self.performance_optimizer.analyze_performance()
                suggestions = self.performance_optimizer.get_optimization_suggestions()
                
                return {
                    'analysis': analysis,
                    'suggestions': suggestions,
                    'timestamp': time.time()
                }
                
            except Exception as e:
                logger.error(f"Failed to get optimization recommendations: {e}")
                return {"error": f"Optimization recommendations failed: {e}"}
        
        @self.register_tool(
            name="clear_cache",
            description="Clear the smart cache and reset cache statistics"
        )
        async def clear_cache() -> Dict[str, Any]:
            """
            Clear the smart cache
            
            Returns:
                Cache clearing status and statistics
            """
            
            if not self.smart_cache:
                return {"error": "Smart cache not available"}
            
            try:
                # Get stats before clearing
                stats_before = self.smart_cache.get_stats()
                
                # Clear cache
                self.smart_cache.clear()
                
                # Get stats after clearing
                stats_after = self.smart_cache.get_stats()
                
                return {
                    'success': True,
                    'stats_before': stats_before,
                    'stats_after': stats_after,
                    'entries_cleared': stats_before['size']
                }
                
            except Exception as e:
                logger.error(f"Failed to clear cache: {e}")
                return {"error": f"Cache clearing failed: {e}"}
    
    def _register_prompts(self):
        """Register prompt templates for common workflows"""
        
        @self.register_prompt(
            name="analyze_codebase",
            description="Comprehensive codebase analysis with customizable focus areas",
            arguments=[
                {
                    "name": "focus",
                    "description": "Analysis focus: security, performance, quality, or patterns",
                    "required": False
                },
                {
                    "name": "depth",
                    "description": "Analysis depth: quick, standard, or deep",
                    "required": False
                }
            ]
        )
        async def analyze_codebase_prompt(focus: str = "quality", depth: str = "standard") -> List[Dict[str, Any]]:
            """Prompt template for comprehensive codebase analysis"""
            return [
                {
                    "role": "system",
                    "content": f"You are a senior code analyst specializing in {focus} analysis. Perform a {depth} analysis of the codebase."
                },
                {
                    "role": "user",
                    "content": "Analyze the codebase focusing on the specified area. Use the semantic_code_search and analyze_code tools to examine relevant files. Provide actionable insights and prioritized recommendations."
                }
            ]
        
        @self.register_prompt(
            name="refactor_for_pattern",
            description="Generate refactoring suggestions to implement a specific design pattern",
            arguments=[
                {
                    "name": "pattern",
                    "description": "Design pattern to apply: SOLID, DRY, KISS, Factory, Singleton, etc.",
                    "required": True
                },
                {
                    "name": "file_path",
                    "description": "Path to the file to refactor",
                    "required": True
                }
            ]
        )
        async def refactor_for_pattern_prompt(pattern: str, file_path: str) -> List[Dict[str, Any]]:
            """Prompt template for pattern-based refactoring"""
            return [
                {
                    "role": "system",
                    "content": f"You are an expert in software design patterns. Help refactor code to implement the {pattern} pattern."
                },
                {
                    "role": "user",
                    "content": f"Analyze the code in {file_path} and provide specific refactoring suggestions to implement the {pattern} pattern. Use the advanced_code_analysis and get_refactoring_suggestions tools."
                }
            ]
        
        @self.register_prompt(
            name="security_audit",
            description="Perform a security-focused code audit",
            arguments=[
                {
                    "name": "severity_threshold",
                    "description": "Minimum severity to report: low, medium, high, critical",
                    "required": False
                }
            ]
        )
        async def security_audit_prompt(severity_threshold: str = "medium") -> List[Dict[str, Any]]:
            """Prompt template for security auditing"""
            return [
                {
                    "role": "system",
                    "content": "You are a security expert. Identify potential vulnerabilities and security issues in code."
                },
                {
                    "role": "user",
                    "content": f"Perform a comprehensive security audit. Focus on issues with severity {severity_threshold} or higher. Use analyze_code and detect_code_patterns tools to identify security vulnerabilities, injection risks, and other security concerns."
                }
            ]
        
        @self.register_prompt(
            name="performance_optimization",
            description="Identify and fix performance bottlenecks",
            arguments=[
                {
                    "name": "target_metric",
                    "description": "Performance metric to optimize: speed, memory, scalability",
                    "required": False
                }
            ]
        )
        async def performance_optimization_prompt(target_metric: str = "speed") -> List[Dict[str, Any]]:
            """Prompt template for performance optimization"""
            return [
                {
                    "role": "system",
                    "content": f"You are a performance optimization expert focusing on {target_metric} improvements."
                },
                {
                    "role": "user", 
                    "content": "Identify performance bottlenecks and provide optimization suggestions. Use assess_code_quality and advanced_code_analysis tools to find inefficient patterns and suggest improvements."
                }
            ]
        
        @self.register_prompt(
            name="code_review",
            description="Comprehensive code review with actionable feedback",
            arguments=[
                {
                    "name": "review_type",
                    "description": "Type of review: general, feature, bugfix, refactoring",
                    "required": False
                },
                {
                    "name": "strictness",
                    "description": "Review strictness level: lenient, balanced, strict",
                    "required": False
                }
            ]
        )
        async def code_review_prompt(review_type: str = "general", strictness: str = "balanced") -> List[Dict[str, Any]]:
            """Prompt template for code reviews"""
            return [
                {
                    "role": "system",
                    "content": f"You are a senior developer performing a {strictness} {review_type} code review."
                },
                {
                    "role": "user",
                    "content": "Review the code comprehensively. Use analyze_code, assess_code_quality, and detect_code_patterns tools. Provide feedback on code quality, potential bugs, style issues, and improvement suggestions."
                }
            ]
    
    async def _startup(self):
        """Initialize ML components on startup"""
        logger.info("Initializing Enhanced ML-Powered Code Intelligence Server...")
        
        # Initialize embedding manager
        embedding_config = EmbeddingConfig(
            model_name=self.settings.embedding_model,
            device=self.settings.ml_device,
            max_length=self.settings.max_embedding_length,
            cache_dir=self.settings.model_cache_dir
        )
        
        self.embedding_manager = EmbeddingManager(embedding_config)
        await self.embedding_manager.load_model()
        
        # Initialize vector database
        self.vector_db = VectorDatabase(
            dimension=self.settings.vector_dimension,
            index_type="flat"  # Start with flat index for simplicity
        )
        
        # Load existing index if available
        index_path = Path(self.settings.data_dir) / "code_index"
        if index_path.with_suffix('.faiss').exists():
            try:
                self.vector_db.load(str(index_path))
                self.indexed_code_count = self.vector_db.index.ntotal
                logger.info(f"Loaded existing code index with {self.indexed_code_count} snippets")
            except Exception as e:
                logger.warning(f"Failed to load existing index: {e}")
        
        # Initialize performance monitoring and caching
        try:
            performance_config = {
                'max_history': 10000,
                'enable_prometheus': getattr(self.settings, 'enable_prometheus', False),
                'performance_thresholds': {
                    'code_generation': {'warning': 5.0, 'critical': 10.0},
                    'analysis': {'warning': 3.0, 'critical': 8.0},
                    'search': {'warning': 1.0, 'critical': 3.0}
                }
            }
            
            cache_config = {
                'max_size': getattr(self.settings, 'cache_max_size', 1000),
                'default_ttl': getattr(self.settings, 'cache_ttl', 3600),
                'max_memory_mb': getattr(self.settings, 'cache_max_memory_mb', 100)
            }
            
            self.performance_monitor = PerformanceMonitor(performance_config)
            self.smart_cache = SmartCache(cache_config)
            self.performance_optimizer = PerformanceOptimizer(self.performance_monitor, self.smart_cache)
            
            logger.info("Performance monitoring and caching initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize performance monitoring: {e}. Monitoring disabled.")
            self.performance_monitor = None
            self.smart_cache = None
            self.performance_optimizer = None
        
        # Initialize enhanced AI components
        try:
            enhanced_config = {
                'model': getattr(self.settings, 'dspy_model', 'gpt-4-turbo-preview'),
                'max_tokens': getattr(self.settings, 'max_tokens', 2048),
                'temperature': getattr(self.settings, 'temperature', 0.1),
                'population_size': getattr(self.settings, 'population_size', 20),
                'max_generations': getattr(self.settings, 'max_generations', 10)
            }
            
            self.context_generator = ContextAwareCodeGenerator(enhanced_config)
            self.multimodal_analyzer = MultiModalCodeAnalyzer(enhanced_config)
            self.prompt_optimizer = PromptOptimizationEngine(enhanced_config)
            
            logger.info("Enhanced AI components initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize enhanced AI components: {e}. Enhanced features disabled.")
            self.context_generator = None
            self.multimodal_analyzer = None
            self.prompt_optimizer = None
        
        logger.info("Enhanced ML-Powered Code Intelligence Server initialized successfully")
    
    async def _shutdown(self):
        """Save state on shutdown"""
        if self.vector_db and self.vector_db.index.ntotal > 0:
            index_path = Path(self.settings.data_dir) / "code_index"
            index_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                self.vector_db.save(str(index_path))
                logger.info(f"Saved code index with {self.vector_db.index.ntotal} snippets")
            except Exception as e:
                logger.error(f"Failed to save index: {e}")
        
        await super()._shutdown()
    
    async def _semantic_search(self, request: CodeSearchRequest) -> List[CodeSearchResult]:
        """Perform semantic code search"""
        if not self.vector_db or self.vector_db.index.ntotal == 0:
            return []
        
        # Performance monitoring
        start_time = time.time()
        operation_id = f"semantic_search_{int(time.time() * 1000)}"
        if self.performance_monitor:
            await self.performance_monitor.start_operation("search", operation_id)
        
        try:
            # Generate embedding for query
            if request.language:
                # Add language context to improve search
                contextualized_query = f"Language: {request.language}\nCode:\n{request.query}"
            else:
                contextualized_query = request.query
            
            query_embedding = await self.embedding_manager.encode_texts([contextualized_query])
            
            # Search in vector database
            scores, results_metadata = self.vector_db.search(
                query_embedding, 
                k=min(request.max_results, self.vector_db.index.ntotal)
            )
            
            # Filter by similarity threshold and language
            search_results = []
            for i, (score, metadata) in enumerate(zip(scores[0], results_metadata[0])):
                if score < request.similarity_threshold:
                    continue
                
                if request.language and metadata.get('language') != request.language:
                    continue
                
                result = CodeSearchResult(
                    code=metadata.get('code', ''),
                    similarity_score=float(score),
                    language=metadata.get('language', 'unknown'),
                    metadata={
                        'file_path': metadata.get('file_path'),
                        'function_name': metadata.get('function_name'),
                        'line_number': metadata.get('line_number'),
                        'hash': metadata.get('hash')
                    }
                )
                search_results.append(result)
            
            logger.info(f"Semantic search found {len(search_results)} results")
            
            # Record performance
            if self.performance_monitor:
                await self.performance_monitor.finish_operation(operation_id, success=True)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            
            # Record performance failure
            if self.performance_monitor:
                await self.performance_monitor.finish_operation(operation_id, success=False, error_message=str(e))
            
            return []
    
    async def _analyze_code(self, request: CodeAnalysisRequest) -> CodeAnalysisResponse:
        """Analyze code for metrics and issues"""
        try:
            # Detect language if not provided
            language = request.language or LanguageDetector.detect(request.code)
            
            # Get basic code summary
            summary = get_code_summary(request.code, language)
            
            metrics_dict = None
            issues_list = None
            advanced_analysis_result = None
            refactoring_suggestions_list = None
            
            if request.include_metrics or request.include_issues:
                # Perform detailed analysis
                metrics, issues = self.code_analyzer.analyze_code(request.code, language)
                
                if request.include_metrics:
                    metrics_dict = {
                        'lines_of_code': metrics.lines_of_code,
                        'lines_of_comments': metrics.lines_of_comments,
                        'cyclomatic_complexity': metrics.cyclomatic_complexity,
                        'cognitive_complexity': metrics.cognitive_complexity,
                        'maintainability_index': metrics.maintainability_index,
                        'technical_debt_ratio': metrics.technical_debt_ratio,
                        'security_score': metrics.security_score,
                        'quality_score': metrics.quality_score
                    }
                
                if request.include_issues:
                    issues_list = [
                        {
                            'type': issue.type,
                            'line': issue.line,
                            'column': issue.column,
                            'message': issue.message,
                            'severity': issue.severity,
                            'rule': issue.rule,
                            'file_path': issue.file_path
                        }
                        for issue in issues
                    ]
            
            # Perform advanced analysis if requested
            if request.include_advanced or request.include_suggestions:
                try:
                    advanced_result = await self._advanced_analysis(request.code, language)
                    if 'advanced_analysis' in advanced_result:
                        advanced_analysis_result = advanced_result['advanced_analysis']
                        
                        if request.include_suggestions:
                            refactoring_suggestions_list = advanced_analysis_result.get('refactoring_suggestions', [])
                except Exception as e:
                    logger.warning(f"Advanced analysis failed: {e}")
            
            response = CodeAnalysisResponse(
                language=language,
                metrics=metrics_dict,
                issues=issues_list,
                summary=summary,
                advanced_analysis=advanced_analysis_result,
                refactoring_suggestions=refactoring_suggestions_list
            )
            
            logger.info(f"Analyzed {language} code with {summary['lines_of_code']} lines")
            return response
            
        except Exception as e:
            logger.error(f"Code analysis failed: {e}")
            raise ValueError(f"Code analysis failed: {e}")
    
    async def _index_code_snippets(self, request: CodeIndexRequest, progress_token: Optional[str] = None) -> Dict[str, Any]:
        """Index code snippets for semantic search"""
        if not self.embedding_manager:
            raise ValueError("Embedding manager not initialized")
        
        try:
            indexed_count = 0
            failed_count = 0
            total_snippets = len(request.code_snippets)
            
            # Start progress tracking if token provided
            operation_id = f"index_{int(time.time())}"
            if progress_token:
                await self.progress_manager.start_operation(
                    operation_id, progress_token, total_snippets
                )
            
            # Process in batches
            for i in range(0, total_snippets, request.batch_size):
                batch = request.code_snippets[i:i + request.batch_size]
                
                # Update progress
                if progress_token:
                    await self.progress_manager.update_progress(
                        operation_id, i, total_snippets,
                        f"Processing batch {i//request.batch_size + 1}"
                    )
                
                # Prepare code for embedding
                code_texts = []
                metadata_list = []
                
                for snippet in batch:
                    code = snippet.get('code', '')
                    language = snippet.get('language') or LanguageDetector.detect(code)
                    
                    if not code.strip():
                        failed_count += 1
                        continue
                    
                    # Add language context for better embeddings
                    contextualized_code = f"Language: {language}\nCode:\n{code}"
                    code_texts.append(contextualized_code)
                    
                    # Prepare metadata
                    metadata = {
                        'code': code,
                        'language': language,
                        'file_path': snippet.get('file_path'),
                        'function_name': snippet.get('function_name'),
                        'line_number': snippet.get('line_number'),
                        'hash': snippet.get('hash'),
                        'indexed_at': time.time()
                    }
                    metadata_list.append(metadata)
                
                if code_texts:
                    # Generate embeddings
                    embeddings = await self.embedding_manager.encode_texts(code_texts)
                    
                    # Add to vector database
                    self.vector_db.add_vectors(embeddings, metadata_list)
                    indexed_count += len(code_texts)
            
            self.indexed_code_count = self.vector_db.index.ntotal
            
            # Complete progress tracking
            if progress_token:
                await self.progress_manager.complete_operation(
                    operation_id, 
                    f"Successfully indexed {indexed_count} code snippets"
                )
            
            logger.info(f"Indexed {indexed_count} code snippets, {failed_count} failed")
            
            return self.response_formatter.success({
                'indexed_count': indexed_count,
                'failed_count': failed_count,
                'total_indexed': self.indexed_code_count,
                'batch_size': request.batch_size
            }, metadata={
                'operation_id': operation_id,
                'duration': time.time() - (self.progress_manager.active_operations.get(operation_id, {}).get('start_time', time.time()))
            })
            
        except Exception as e:
            logger.error(f"Code indexing failed: {e}")
            
            # Fail progress tracking
            if progress_token:
                await self.progress_manager.fail_operation(operation_id, str(e))
            
            return self.response_formatter.error(f"Code indexing failed: {e}", "INDEX_ERROR")
    
    async def _advanced_analysis(self, code: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Perform advanced code analysis with patterns and suggestions"""
        try:
            # Detect language if not provided
            detected_language = language or LanguageDetector.detect(code)
            
            # Use the enhanced analysis from our advanced analyzer
            result = enhance_code_analysis(code, detected_language)
            
            logger.info(f"Advanced analysis completed for {detected_language} code")
            return result
            
        except Exception as e:
            logger.error(f"Advanced analysis failed: {e}")
            return {
                'error': f"Advanced analysis failed: {e}",
                'language': language or 'unknown'
            }
    
    async def _assess_quality(self, code: str, language: Optional[str] = None, include_trends: bool = False) -> Dict[str, Any]:
        """Perform comprehensive code quality assessment"""
        try:
            # Detect language if not provided
            detected_language = language or LanguageDetector.detect(code)
            
            # Use the quality assessment from our quality analyzer
            result = assess_code_quality(code, detected_language, include_trends)
            
            logger.info(f"Quality assessment completed for {detected_language} code with score {result.get('overall_score', 0):.1f}")
            return result
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return {
                'status': 'error',
                'error': f"Quality assessment failed: {e}",
                'overall_score': 0.0,
                'language': language or 'unknown'
            }
    
    # Enhanced helper methods for new AI capabilities
    async def _analyze_project_context(self, project_path: Optional[str], context_type: str) -> Dict[str, Any]:
        """Analyze project context for code generation"""
        
        if not project_path:
            return {
                'current_file': None,
                'project_structure': None,
                'imports': [],
                'dependencies': [],
                'existing_code': [],
                'git_history': []
            }
        
        try:
            project_path_obj = Path(project_path)
            if not project_path_obj.exists():
                logger.warning(f"Project path does not exist: {project_path}")
                return {}
            
            context = {
                'current_file': await self._analyze_current_file(project_path_obj),
                'project_structure': await self._analyze_project_structure(project_path_obj),
                'imports': await self._extract_project_imports(project_path_obj),
                'dependencies': await self._extract_project_dependencies(project_path_obj),
                'existing_code': await self._sample_existing_code(project_path_obj),
                'git_history': await self._extract_git_history(project_path_obj) if context_type == "full" else []
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to analyze project context: {e}")
            return {}
    
    async def _collect_project_artifacts(self, project_path: str) -> Dict[str, Any]:
        """Collect project artifacts for multi-modal analysis"""
        
        try:
            project_path_obj = Path(project_path)
            if not project_path_obj.exists():
                return {}
            
            artifacts = {
                'code_files': await self._collect_code_files(project_path_obj),
                'docs': await self._collect_documentation(project_path_obj),
                'tests': await self._collect_test_files(project_path_obj),
                'comments': await self._extract_comments(project_path_obj)
            }
            
            return artifacts
            
        except Exception as e:
            logger.error(f"Failed to collect project artifacts: {e}")
            return {}
    
    async def _check_consistency(self, unified_analysis: MultiModalAnalysisResult, threshold: float) -> MultiModalAnalysisResult:
        """Check consistency in unified analysis"""
        return unified_analysis  # The analysis already includes consistency checking
    
    async def _improve_generation(self, result: CodeGenerationResult, quality_target: float) -> CodeGenerationResult:
        """Improve code generation iteratively"""
        # In a full implementation, this would use the prompt optimizer to improve the result
        return result
    
    async def _generate_project_summary(self, unified_analysis: MultiModalAnalysisResult, depth: str) -> Dict[str, Any]:
        """Generate human-readable project summary"""
        
        insights = unified_analysis.unified_insights
        
        summary = {
            'executive': f"Project analysis complete. Found {len(insights.get('semantic_clusters', []))} semantic clusters.",
            'technical': f"Code coverage: {insights.get('modality_coverage', {}).get('code', {}).get('density', 0)} files",
            'architecture': f"Architecture patterns detected: {insights.get('cross_references', {})}",
            'quality': unified_analysis.embedding_statistics,
            'recommendations': [
                "Consider adding more documentation",
                "Improve test coverage",
                "Enhance code comments"
            ]
        }
        
        if depth == "comprehensive":
            summary['detailed_analysis'] = unified_analysis.consistency_analysis
            summary['relationship_insights'] = unified_analysis.relationship_map
        
        return summary
    
    # Helper methods for project analysis
    async def _analyze_current_file(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze the current file being worked on"""
        # In a real implementation, this would identify the active file
        # For now, return None
        return None
    
    async def _analyze_project_structure(self, project_path: Path) -> Dict[str, Any]:
        """Analyze the overall project structure"""
        
        structure = {
            'directories': [],
            'file_types': {},
            'total_files': 0
        }
        
        try:
            for item in project_path.rglob('*'):
                if item.is_dir():
                    structure['directories'].append(str(item.relative_to(project_path)))
                elif item.is_file():
                    structure['total_files'] += 1
                    suffix = item.suffix.lower()
                    structure['file_types'][suffix] = structure['file_types'].get(suffix, 0) + 1
        except Exception as e:
            logger.warning(f"Failed to analyze project structure: {e}")
        
        return structure
    
    async def _extract_project_imports(self, project_path: Path) -> List[str]:
        """Extract import statements from project files"""
        
        imports = []
        try:
            for py_file in project_path.rglob('*.py'):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        file_imports = [
                            line.strip() for line in lines[:20]  # Only check first 20 lines
                            if line.strip().startswith(('import ', 'from '))
                        ]
                        imports.extend(file_imports)
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Failed to extract imports: {e}")
        
        return list(set(imports))[:50]  # Return unique imports, max 50
    
    async def _extract_project_dependencies(self, project_path: Path) -> List[str]:
        """Extract project dependencies from requirements files"""
        
        dependencies = []
        
        # Check common dependency files
        dep_files = ['requirements.txt', 'Pipfile', 'pyproject.toml', 'environment.yml']
        
        for dep_file in dep_files:
            dep_path = project_path / dep_file
            if dep_path.exists():
                try:
                    with open(dep_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Simple extraction - just get lines that look like package names
                        lines = content.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                package = line.split('=')[0].split('>')[0].split('<')[0].strip()
                                if package:
                                    dependencies.append(package)
                except Exception:
                    continue
        
        return list(set(dependencies))[:30]  # Return unique dependencies, max 30
    
    async def _sample_existing_code(self, project_path: Path) -> List[str]:
        """Sample existing code for style analysis"""
        
        code_samples = []
        try:
            py_files = list(project_path.rglob('*.py'))
            sample_files = py_files[:5]  # Sample first 5 Python files
            
            for py_file in sample_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if len(content) < 10000:  # Only include smaller files
                            code_samples.append(content)
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Failed to sample existing code: {e}")
        
        return code_samples
    
    async def _extract_git_history(self, project_path: Path) -> List[Dict[str, Any]]:
        """Extract git history for pattern analysis"""
        # In a real implementation, this would use git commands
        # For now, return empty list
        return []
    
    async def _collect_code_files(self, project_path: Path) -> List[Dict[str, Any]]:
        """Collect code files for analysis"""
        
        code_files = []
        try:
            for py_file in project_path.rglob('*.py'):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if len(content) < 50000:  # Skip very large files
                            code_files.append({
                                'path': str(py_file.relative_to(project_path)),
                                'content': content,
                                'language': 'python'
                            })
                except Exception:
                    continue
                    
                # Limit to 20 files for performance
                if len(code_files) >= 20:
                    break
                    
        except Exception as e:
            logger.warning(f"Failed to collect code files: {e}")
        
        return code_files
    
    async def _collect_documentation(self, project_path: Path) -> List[Dict[str, Any]]:
        """Collect documentation files"""
        
        docs = []
        doc_extensions = ['.md', '.rst', '.txt']
        
        try:
            for ext in doc_extensions:
                for doc_file in project_path.rglob(f'*{ext}'):
                    try:
                        with open(doc_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if len(content) < 100000:  # Skip very large files
                                docs.append({
                                    'path': str(doc_file.relative_to(project_path)),
                                    'content': content,
                                    'type': 'markdown' if ext == '.md' else 'text'
                                })
                    except Exception:
                        continue
                        
                    # Limit to 10 docs for performance
                    if len(docs) >= 10:
                        break
                        
        except Exception as e:
            logger.warning(f"Failed to collect documentation: {e}")
        
        return docs
    
    async def _collect_test_files(self, project_path: Path) -> List[Dict[str, Any]]:
        """Collect test files"""
        
        tests = []
        try:
            test_patterns = ['test_*.py', '*_test.py', 'tests/*.py']
            
            for pattern in test_patterns:
                for test_file in project_path.rglob(pattern):
                    try:
                        with open(test_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if len(content) < 50000:  # Skip very large files
                                tests.append({
                                    'path': str(test_file.relative_to(project_path)),
                                    'content': content,
                                    'type': 'unit'
                                })
                    except Exception:
                        continue
                        
                    # Limit to 15 tests for performance
                    if len(tests) >= 15:
                        break
                        
        except Exception as e:
            logger.warning(f"Failed to collect test files: {e}")
        
        return tests
    
    async def _extract_comments(self, project_path: Path) -> List[Dict[str, Any]]:
        """Extract comments from code files"""
        
        comments = []
        try:
            for py_file in project_path.rglob('*.py'):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            line = line.strip()
                            if line.startswith('#') and len(line) > 3:
                                comments.append({
                                    'id': f"{py_file.name}_{i}",
                                    'content': line[1:].strip(),
                                    'type': 'inline',
                                    'line_number': i + 1,
                                    'file_path': str(py_file.relative_to(project_path))
                                })
                except Exception:
                    continue
                    
                # Limit to 50 comments for performance
                if len(comments) >= 50:
                    break
                    
        except Exception as e:
            logger.warning(f"Failed to extract comments: {e}")
        
        return comments


def create_server_config() -> MCPServerSettings:
    """Create server configuration"""
    config_manager = ConfigManager()
    return config_manager.load_config("ml-code-intelligence")


def main():
    """Main entry point"""
    try:
        # Load configuration
        config = create_server_config()
        
        # Create and run server
        server = MLCodeIntelligenceServer(config)
        server.run(transport="stdio")
        
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()