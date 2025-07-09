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
    """ML-Powered Code Intelligence MCP Server"""
    
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
        
        # Register tools
        self._register_tools()
    
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
    
    async def _startup(self):
        """Initialize ML components on startup"""
        logger.info("Initializing ML-Powered Code Intelligence Server...")
        
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
        
        logger.info("ML-Powered Code Intelligence Server initialized successfully")
    
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
            return search_results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
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
    
    async def _index_code_snippets(self, request: CodeIndexRequest) -> Dict[str, Any]:
        """Index code snippets for semantic search"""
        if not self.embedding_manager:
            raise ValueError("Embedding manager not initialized")
        
        try:
            indexed_count = 0
            failed_count = 0
            
            # Process in batches
            for i in range(0, len(request.code_snippets), request.batch_size):
                batch = request.code_snippets[i:i + request.batch_size]
                
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
            
            logger.info(f"Indexed {indexed_count} code snippets, {failed_count} failed")
            
            return {
                'indexed_count': indexed_count,
                'failed_count': failed_count,
                'total_indexed': self.indexed_code_count,
                'batch_size': request.batch_size
            }
            
        except Exception as e:
            logger.error(f"Code indexing failed: {e}")
            raise ValueError(f"Code indexing failed: {e}")
    
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