"""
Multi-Modal Code Analysis System
Advanced multi-modal analysis system that creates unified understanding across code, 
documentation, tests, and comments, enabling holistic project comprehension.
"""

import asyncio
import logging
import numpy as np
import torch
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import time

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None
    logging.warning("sentence-transformers not available. Using mock embedder.")

logger = logging.getLogger(__name__)

@dataclass
class MultiModalAnalysisResult:
    """Result of multi-modal analysis"""
    unified_insights: Dict[str, Any]
    consistency_analysis: Dict[str, Any]
    embedding_statistics: Dict[str, Any]
    relationship_map: Dict[str, Any]

@dataclass
class CrossModalRelationship:
    """Relationship between different modalities"""
    source_type: str
    target_type: str
    similarity_score: float
    relationship_type: str
    metadata: Dict[str, Any]

class MultiModalCodeAnalyzer:
    """Advanced multi-modal analysis for unified code understanding"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize specialized embedders for different modalities
        self.code_embedder = CodeEmbedder(config)
        self.doc_embedder = DocumentationEmbedder(config)
        self.test_embedder = TestCaseEmbedder(config)
        self.comment_embedder = CommentEmbedder(config)
        
        # Unified embedding space (1408 dimensions for compatibility)
        self.unified_space = UnifiedEmbeddingSpace(dimension=1408)
        self.cross_modal_analyzer = CrossModalRelationshipAnalyzer()
        self.consistency_checker = ConsistencyChecker()
        
    async def analyze_unified_context(self, project_artifacts: Dict[str, Any]) -> MultiModalAnalysisResult:
        """Create unified understanding across all project modalities"""
        
        try:
            # Parallel embedding generation for all modalities
            embedding_tasks = await asyncio.gather(
                self.embed_code_artifacts(project_artifacts.get('code_files', [])),
                self.embed_documentation(project_artifacts.get('docs', [])),
                self.embed_test_suites(project_artifacts.get('tests', [])),
                self.embed_comments(project_artifacts.get('comments', []))
            )
            
            code_embeddings, doc_embeddings, test_embeddings, comment_embeddings = embedding_tasks
            
            # Cross-modal alignment and fusion
            aligned_embeddings = await self.align_cross_modal_embeddings({
                'code': code_embeddings,
                'docs': doc_embeddings,
                'tests': test_embeddings,
                'comments': comment_embeddings
            })
            
            # Unified analysis and insight generation
            unified_insights = await self.synthesize_cross_modal_insights(aligned_embeddings)
            
            # Consistency analysis
            consistency_analysis = await self.analyze_cross_modal_consistency(aligned_embeddings)
            
            return MultiModalAnalysisResult(
                unified_insights=unified_insights,
                consistency_analysis=consistency_analysis,
                embedding_statistics=self.calculate_embedding_statistics(aligned_embeddings),
                relationship_map=await self.generate_relationship_map(aligned_embeddings)
            )
            
        except Exception as e:
            logger.error(f"Multi-modal analysis failed: {e}")
            return MultiModalAnalysisResult(
                unified_insights={'error': str(e)},
                consistency_analysis={'error': str(e)},
                embedding_statistics={},
                relationship_map={}
            )

    async def embed_code_artifacts(self, code_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Embed code files with semantic enhancement"""
        return await self.code_embedder.embed_code_files(code_files)

    async def embed_documentation(self, docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Embed documentation with structural awareness"""
        return await self.doc_embedder.embed_documentation(docs)

    async def embed_test_suites(self, tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Embed test cases with behavior understanding"""
        return await self.test_embedder.embed_test_suites(tests)

    async def embed_comments(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Embed comments with context awareness"""
        return await self.comment_embedder.embed_comments(comments)

    async def align_cross_modal_embeddings(self, modal_embeddings: Dict[str, Any]) -> Dict[str, Any]:
        """Align embeddings across different modalities"""
        return await self.unified_space.align_embeddings(modal_embeddings)

    async def synthesize_cross_modal_insights(self, aligned_embeddings: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize insights from aligned embeddings"""
        
        insights = {
            'modality_coverage': await self._analyze_modality_coverage(aligned_embeddings),
            'semantic_clusters': await self._identify_semantic_clusters(aligned_embeddings),
            'knowledge_gaps': await self._identify_knowledge_gaps(aligned_embeddings),
            'cross_references': await self._extract_cross_references(aligned_embeddings)
        }
        
        return insights

    async def analyze_cross_modal_consistency(self, aligned_embeddings: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze consistency across modalities"""
        return await self.consistency_checker.check_consistency(aligned_embeddings)

    def calculate_embedding_statistics(self, aligned_embeddings: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistics for embeddings"""
        
        stats = {}
        for modality, embeddings in aligned_embeddings.items():
            if embeddings and isinstance(embeddings, dict):
                stats[modality] = {
                    'count': len(embeddings),
                    'avg_similarity': self._calculate_avg_similarity(embeddings),
                    'dimension': self._get_embedding_dimension(embeddings)
                }
        
        return stats

    async def generate_relationship_map(self, aligned_embeddings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a map of relationships between different modalities"""
        
        relationship_map = {}
        
        # Find relationships between code and docs
        if 'code' in aligned_embeddings and 'docs' in aligned_embeddings:
            relationship_map['code_docs'] = await self.cross_modal_analyzer.discover_code_doc_relationships(
                aligned_embeddings['code'], aligned_embeddings['docs']
            )
        
        # Find relationships between code and tests
        if 'code' in aligned_embeddings and 'tests' in aligned_embeddings:
            relationship_map['code_tests'] = await self.cross_modal_analyzer.analyze_test_coverage_semantics(
                aligned_embeddings['code'], aligned_embeddings['tests']
            )
        
        return relationship_map

    async def _analyze_modality_coverage(self, aligned_embeddings: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze coverage across different modalities"""
        
        coverage = {}
        for modality, embeddings in aligned_embeddings.items():
            if embeddings:
                coverage[modality] = {
                    'present': True,
                    'density': len(embeddings) if isinstance(embeddings, dict) else 0,
                    'quality': 'high' if len(embeddings) > 5 else 'medium'
                }
            else:
                coverage[modality] = {'present': False, 'density': 0, 'quality': 'none'}
        
        return coverage

    async def _identify_semantic_clusters(self, aligned_embeddings: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify semantic clusters across modalities"""
        
        clusters = []
        
        # Simple clustering based on similarity (in production, use proper clustering)
        for modality, embeddings in aligned_embeddings.items():
            if embeddings and len(embeddings) > 2:
                clusters.append({
                    'modality': modality,
                    'cluster_count': min(3, len(embeddings) // 2),
                    'coherence': 0.8  # Mock coherence score
                })
        
        return clusters

    async def _identify_knowledge_gaps(self, aligned_embeddings: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify gaps in knowledge across modalities"""
        
        gaps = []
        
        # Check for missing documentation
        if 'code' in aligned_embeddings and aligned_embeddings['code']:
            if not aligned_embeddings.get('docs'):
                gaps.append({
                    'type': 'missing_documentation',
                    'severity': 'high',
                    'description': 'Code exists but no documentation found'
                })
        
        # Check for missing tests
        if 'code' in aligned_embeddings and aligned_embeddings['code']:
            if not aligned_embeddings.get('tests'):
                gaps.append({
                    'type': 'missing_tests',
                    'severity': 'high',
                    'description': 'Code exists but no tests found'
                })
        
        return gaps

    async def _extract_cross_references(self, aligned_embeddings: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract cross-references between modalities"""
        
        cross_refs = {}
        
        # Simple implementation - in production, use semantic similarity
        for modality in aligned_embeddings:
            cross_refs[modality] = list(aligned_embeddings.keys())
        
        return cross_refs

    def _calculate_avg_similarity(self, embeddings: Dict[str, Any]) -> float:
        """Calculate average similarity within embeddings"""
        # Simplified calculation
        return 0.75  # Mock average similarity

    def _get_embedding_dimension(self, embeddings: Dict[str, Any]) -> int:
        """Get embedding dimension"""
        if embeddings:
            first_embedding = next(iter(embeddings.values()))
            if isinstance(first_embedding, dict) and 'embedding' in first_embedding:
                return getattr(first_embedding['embedding'], 'shape', [0])[-1] if hasattr(first_embedding['embedding'], 'shape') else 384
        return 384  # Default dimension


class CodeEmbedder:
    """Specialized embedder for source code with syntax and semantic awareness"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Use code-specific transformer model
        if SentenceTransformer:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Fallback to general model
            except Exception as e:
                logger.warning(f"Failed to load SentenceTransformer: {e}. Using mock embedder.")
                self.model = None
        else:
            self.model = None
            
        self.ast_parser = ASTSemanticParser()
        
    async def embed_code_files(self, code_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate embeddings for code files with semantic enhancement"""
        
        embeddings = {}
        
        for file_info in code_files:
            file_path = file_info.get('path', '')
            code_content = file_info.get('content', '')
            language = file_info.get('language', 'unknown')
            
            # AST-enhanced code representation
            semantic_representation = await self.ast_parser.extract_semantic_features(
                code_content, language
            )
            
            # Combine raw code with semantic features
            enhanced_code = self.enhance_code_with_semantics(
                code_content, semantic_representation
            )
            
            # Generate embedding
            embedding = await self._generate_embedding(enhanced_code)
            
            embeddings[file_path] = {
                'embedding': embedding,
                'metadata': {
                    'language': language,
                    'functions': semantic_representation.get('functions', []),
                    'classes': semantic_representation.get('classes', []),
                    'complexity': semantic_representation.get('complexity', 0),
                    'dependencies': semantic_representation.get('dependencies', [])
                }
            }
            
        return embeddings

    def enhance_code_with_semantics(self, code: str, semantic_representation: Dict[str, Any]) -> str:
        """Enhance code with semantic features for better embedding"""
        
        semantic_summary = f"Functions: {len(semantic_representation.get('functions', []))}, "
        semantic_summary += f"Classes: {len(semantic_representation.get('classes', []))}, "
        semantic_summary += f"Complexity: {semantic_representation.get('complexity', 0)}"
        
        return f"{semantic_summary}\n\n{code}"

    async def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        if self.model:
            try:
                return self.model.encode(text)
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")
        
        # Mock embedding
        return np.random.rand(384)


class DocumentationEmbedder:
    """Specialized embedder for documentation with context awareness"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        if SentenceTransformer:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                logger.warning(f"Failed to load SentenceTransformer: {e}. Using mock embedder.")
                self.model = None
        else:
            self.model = None
            
        self.doc_parser = DocumentationParser()
        
    async def embed_documentation(self, docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate embeddings for documentation with structural awareness"""
        
        embeddings = {}
        
        for doc_info in docs:
            doc_path = doc_info.get('path', '')
            doc_content = doc_info.get('content', '')
            doc_type = doc_info.get('type', 'markdown')
            
            # Parse documentation structure
            doc_structure = await self.doc_parser.parse_structure(doc_content, doc_type)
            
            # Generate section-wise embeddings
            section_embeddings = {}
            for section in doc_structure.get('sections', []):
                section_embedding = await self._generate_embedding(section.get('content', ''))
                section_embeddings[section.get('title', 'untitled')] = {
                    'embedding': section_embedding,
                    'metadata': section.get('metadata', {})
                }
            
            # Overall document embedding
            full_doc_embedding = await self._generate_embedding(doc_content)
            
            embeddings[doc_path] = {
                'full_embedding': full_doc_embedding,
                'section_embeddings': section_embeddings,
                'structure': doc_structure,
                'metadata': {
                    'type': doc_type,
                    'sections_count': len(doc_structure.get('sections', [])),
                    'api_references': doc_structure.get('api_references', [])
                }
            }
            
        return embeddings

    async def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        if self.model:
            try:
                return self.model.encode(text)
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")
        
        # Mock embedding
        return np.random.rand(384)


class TestCaseEmbedder:
    """Specialized embedder for test cases with behavior understanding"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        if SentenceTransformer:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                logger.warning(f"Failed to load SentenceTransformer: {e}. Using mock embedder.")
                self.model = None
        else:
            self.model = None

    async def embed_test_suites(self, tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate embeddings for test suites"""
        
        embeddings = {}
        
        for test_info in tests:
            test_path = test_info.get('path', '')
            test_content = test_info.get('content', '')
            test_type = test_info.get('type', 'unit')
            
            # Extract test cases
            test_cases = await self._extract_test_cases(test_content)
            
            # Generate embedding
            embedding = await self._generate_embedding(test_content)
            
            embeddings[test_path] = {
                'embedding': embedding,
                'metadata': {
                    'type': test_type,
                    'test_cases': test_cases,
                    'coverage_area': await self._identify_coverage_area(test_content)
                }
            }
            
        return embeddings

    async def _extract_test_cases(self, test_content: str) -> List[str]:
        """Extract individual test cases from test content"""
        # Simple extraction - in production, use AST parsing
        lines = test_content.split('\n')
        test_cases = [line.strip() for line in lines if 'def test_' in line or 'it(' in line]
        return test_cases

    async def _identify_coverage_area(self, test_content: str) -> str:
        """Identify what area the test covers"""
        # Simple heuristic - in production, use more sophisticated analysis
        if 'api' in test_content.lower():
            return 'api'
        elif 'database' in test_content.lower():
            return 'database'
        elif 'model' in test_content.lower():
            return 'model'
        else:
            return 'general'

    async def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        if self.model:
            try:
                return self.model.encode(text)
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")
        
        # Mock embedding
        return np.random.rand(384)


class CommentEmbedder:
    """Specialized embedder for comments with context awareness"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        if SentenceTransformer:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                logger.warning(f"Failed to load SentenceTransformer: {e}. Using mock embedder.")
                self.model = None
        else:
            self.model = None

    async def embed_comments(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate embeddings for comments"""
        
        embeddings = {}
        
        for comment_info in comments:
            comment_id = comment_info.get('id', str(hash(comment_info.get('content', ''))))
            comment_content = comment_info.get('content', '')
            comment_type = comment_info.get('type', 'inline')
            
            # Generate embedding
            embedding = await self._generate_embedding(comment_content)
            
            embeddings[comment_id] = {
                'embedding': embedding,
                'metadata': {
                    'type': comment_type,
                    'length': len(comment_content),
                    'line_number': comment_info.get('line_number'),
                    'file_path': comment_info.get('file_path')
                }
            }
            
        return embeddings

    async def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        if self.model:
            try:
                return self.model.encode(text)
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")
        
        # Mock embedding
        return np.random.rand(384)


class UnifiedEmbeddingSpace:
    """Unified embedding space for cross-modal alignment"""
    
    def __init__(self, dimension: int = 1408):
        self.dimension = dimension

    async def align_embeddings(self, modal_embeddings: Dict[str, Any]) -> Dict[str, Any]:
        """Align embeddings from different modalities to unified space"""
        
        aligned = {}
        
        for modality, embeddings in modal_embeddings.items():
            if embeddings:
                aligned[modality] = await self._project_to_unified_space(embeddings, modality)
        
        return aligned

    async def _project_to_unified_space(self, embeddings: Dict[str, Any], modality: str) -> Dict[str, Any]:
        """Project embeddings to unified space"""
        
        # Simple projection - in production, use learned projection matrices
        projected = {}
        
        for key, embedding_info in embeddings.items():
            if isinstance(embedding_info, dict) and 'embedding' in embedding_info:
                # Simple padding/truncation to target dimension
                original_embedding = embedding_info['embedding']
                if hasattr(original_embedding, 'shape'):
                    current_dim = original_embedding.shape[-1]
                    if current_dim < self.dimension:
                        # Pad with zeros
                        padding = np.zeros(self.dimension - current_dim)
                        projected_embedding = np.concatenate([original_embedding, padding])
                    else:
                        # Truncate
                        projected_embedding = original_embedding[:self.dimension]
                else:
                    projected_embedding = original_embedding
                
                projected[key] = {
                    **embedding_info,
                    'embedding': projected_embedding
                }
        
        return projected


class CrossModalRelationshipAnalyzer:
    """Advanced analysis of relationships between different modalities"""
    
    async def discover_code_doc_relationships(
        self, 
        code_embeddings: Dict[str, Any], 
        doc_embeddings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Discover semantic relationships between code and documentation"""
        
        relationships = {}
        similarity_threshold = 0.7
        
        for code_path, code_data in code_embeddings.items():
            relationships[code_path] = {
                'related_docs': [],
                'coverage_score': 0.0,
                'documentation_gaps': []
            }
            
            # Find related documentation using cosine similarity
            for doc_path, doc_data in doc_embeddings.items():
                # Simple similarity calculation (in production, use proper cosine similarity)
                similarity = 0.8  # Mock similarity
                
                if similarity > similarity_threshold:
                    relationships[code_path]['related_docs'].append({
                        'doc_path': doc_path,
                        'similarity': similarity,
                        'type': 'overall'
                    })
            
            # Calculate documentation coverage score
            relationships[code_path]['coverage_score'] = await self.calculate_documentation_coverage(
                code_data, relationships[code_path]['related_docs']
            )
            
            # Identify documentation gaps
            relationships[code_path]['documentation_gaps'] = await self.identify_documentation_gaps(
                code_data, relationships[code_path]['related_docs']
            )
        
        return relationships
    
    async def analyze_test_coverage_semantics(
        self, 
        code_embeddings: Dict[str, Any], 
        test_embeddings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze semantic test coverage beyond traditional metrics"""
        
        coverage_analysis = {}
        
        for code_path, code_data in code_embeddings.items():
            coverage_analysis[code_path] = {
                'semantic_coverage': 0.0,
                'related_tests': [],
                'coverage_gaps': [],
                'test_quality_score': 0.0
            }
            
            # Find semantically related tests
            related_tests = []
            for test_path, test_data in test_embeddings.items():
                # Simple similarity calculation
                test_similarity = 0.7  # Mock similarity
                
                if test_similarity > 0.6:  # Lower threshold for test relationships
                    related_tests.append({
                        'test_path': test_path,
                        'similarity': test_similarity,
                        'test_cases': test_data['metadata'].get('test_cases', [])
                    })
            
            coverage_analysis[code_path]['related_tests'] = related_tests
            
            # Calculate semantic coverage score
            coverage_analysis[code_path]['semantic_coverage'] = await self.calculate_semantic_coverage(
                code_data['metadata'].get('functions', []), related_tests
            )
            
            # Identify semantic gaps in testing
            coverage_analysis[code_path]['coverage_gaps'] = await self.identify_test_gaps(
                code_data, related_tests
            )
            
            # Assess test quality
            coverage_analysis[code_path]['test_quality_score'] = await self.assess_test_quality(
                related_tests
            )
        
        return coverage_analysis

    async def calculate_documentation_coverage(self, code_data: Dict[str, Any], related_docs: List[Dict[str, Any]]) -> float:
        """Calculate documentation coverage score"""
        if not related_docs:
            return 0.0
        
        # Simple coverage calculation
        function_count = len(code_data.get('metadata', {}).get('functions', []))
        doc_count = len(related_docs)
        
        return min(doc_count / max(function_count, 1), 1.0)

    async def identify_documentation_gaps(self, code_data: Dict[str, Any], related_docs: List[Dict[str, Any]]) -> List[str]:
        """Identify gaps in documentation"""
        gaps = []
        
        functions = code_data.get('metadata', {}).get('functions', [])
        if functions and not related_docs:
            gaps.append("No documentation found for implemented functions")
        
        if len(functions) > len(related_docs):
            gaps.append("Insufficient documentation coverage")
        
        return gaps

    async def calculate_semantic_coverage(self, functions: List[str], related_tests: List[Dict[str, Any]]) -> float:
        """Calculate semantic test coverage"""
        if not functions:
            return 1.0
        
        if not related_tests:
            return 0.0
        
        # Simple coverage calculation
        test_count = sum(len(test.get('test_cases', [])) for test in related_tests)
        return min(test_count / len(functions), 1.0)

    async def identify_test_gaps(self, code_data: Dict[str, Any], related_tests: List[Dict[str, Any]]) -> List[str]:
        """Identify gaps in test coverage"""
        gaps = []
        
        functions = code_data.get('metadata', {}).get('functions', [])
        if functions and not related_tests:
            gaps.append("No tests found for implemented functions")
        
        if len(functions) > len(related_tests):
            gaps.append("Insufficient test coverage")
        
        return gaps

    async def assess_test_quality(self, related_tests: List[Dict[str, Any]]) -> float:
        """Assess the quality of related tests"""
        if not related_tests:
            return 0.0
        
        # Simple quality assessment
        total_test_cases = sum(len(test.get('test_cases', [])) for test in related_tests)
        return min(total_test_cases / 10, 1.0)  # Arbitrary quality metric


class ConsistencyChecker:
    """Check consistency across different modalities"""
    
    async def check_consistency(self, aligned_embeddings: Dict[str, Any], threshold: float = 0.8) -> Dict[str, Any]:
        """Check consistency across modalities"""
        
        consistency_results = {
            'overall_score': 0.0,
            'modality_scores': {},
            'inconsistencies': [],
            'suggestions': [],
            'priority_fixes': []
        }
        
        # Calculate consistency scores for each modality pair
        modalities = list(aligned_embeddings.keys())
        total_score = 0.0
        pair_count = 0
        
        for i, mod1 in enumerate(modalities):
            for mod2 in modalities[i+1:]:
                if aligned_embeddings[mod1] and aligned_embeddings[mod2]:
                    score = await self._calculate_modality_consistency(
                        aligned_embeddings[mod1], 
                        aligned_embeddings[mod2]
                    )
                    consistency_results['modality_scores'][f"{mod1}_{mod2}"] = score
                    total_score += score
                    pair_count += 1
                    
                    if score < threshold:
                        consistency_results['inconsistencies'].append({
                            'modalities': [mod1, mod2],
                            'score': score,
                            'severity': 'high' if score < 0.5 else 'medium'
                        })
        
        if pair_count > 0:
            consistency_results['overall_score'] = total_score / pair_count
        
        # Generate suggestions
        consistency_results['suggestions'] = await self._generate_consistency_suggestions(
            consistency_results['inconsistencies']
        )
        
        # Identify priority fixes
        consistency_results['priority_fixes'] = [
            inc for inc in consistency_results['inconsistencies'] 
            if inc['severity'] == 'high'
        ]
        
        return consistency_results

    async def _calculate_modality_consistency(self, embeddings1: Dict[str, Any], embeddings2: Dict[str, Any]) -> float:
        """Calculate consistency between two modalities"""
        # Simplified consistency calculation
        
        if not embeddings1 or not embeddings2:
            return 0.0
        
        # Mock consistency score based on presence and overlap
        overlap_factor = min(len(embeddings1), len(embeddings2)) / max(len(embeddings1), len(embeddings2))
        base_score = 0.6  # Base consistency
        
        return min(base_score + overlap_factor * 0.4, 1.0)

    async def _generate_consistency_suggestions(self, inconsistencies: List[Dict[str, Any]]) -> List[str]:
        """Generate suggestions to improve consistency"""
        
        suggestions = []
        
        for inconsistency in inconsistencies:
            modalities = inconsistency['modalities']
            
            if 'code' in modalities and 'docs' in modalities:
                suggestions.append("Update documentation to better reflect the code implementation")
            
            if 'code' in modalities and 'tests' in modalities:
                suggestions.append("Add more comprehensive tests to cover code functionality")
            
            if 'docs' in modalities and 'tests' in modalities:
                suggestions.append("Ensure test descriptions align with documentation")
        
        return list(set(suggestions))  # Remove duplicates


class ASTSemanticParser:
    """Parse code to extract semantic features"""
    
    async def extract_semantic_features(self, code: str, language: str) -> Dict[str, Any]:
        """Extract semantic features from code"""
        
        features = {
            'functions': self._extract_functions(code),
            'classes': self._extract_classes(code),
            'complexity': self._calculate_complexity(code),
            'dependencies': self._extract_dependencies(code)
        }
        
        return features

    def _extract_functions(self, code: str) -> List[str]:
        """Extract function names from code"""
        lines = code.split('\n')
        functions = []
        
        for line in lines:
            if 'def ' in line:
                # Simple function extraction
                parts = line.split('def ')
                if len(parts) > 1:
                    func_name = parts[1].split('(')[0].strip()
                    functions.append(func_name)
        
        return functions

    def _extract_classes(self, code: str) -> List[str]:
        """Extract class names from code"""
        lines = code.split('\n')
        classes = []
        
        for line in lines:
            if 'class ' in line:
                # Simple class extraction
                parts = line.split('class ')
                if len(parts) > 1:
                    class_name = parts[1].split(':')[0].split('(')[0].strip()
                    classes.append(class_name)
        
        return classes

    def _calculate_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity (simplified)"""
        complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally']
        
        complexity = 1  # Base complexity
        for keyword in complexity_keywords:
            complexity += code.count(keyword)
        
        return complexity

    def _extract_dependencies(self, code: str) -> List[str]:
        """Extract dependencies from code"""
        lines = code.split('\n')
        dependencies = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                dependencies.append(line)
        
        return dependencies


class DocumentationParser:
    """Parse documentation to extract structure"""
    
    async def parse_structure(self, doc_content: str, doc_type: str) -> Dict[str, Any]:
        """Parse documentation structure"""
        
        structure = {
            'sections': self._extract_sections(doc_content, doc_type),
            'api_references': self._extract_api_references(doc_content),
            'code_examples': self._extract_code_examples(doc_content)
        }
        
        return structure

    def _extract_sections(self, content: str, doc_type: str) -> List[Dict[str, Any]]:
        """Extract sections from documentation"""
        sections = []
        
        if doc_type == 'markdown':
            lines = content.split('\n')
            current_section = None
            current_content = []
            
            for line in lines:
                if line.startswith('#'):
                    # Save previous section
                    if current_section:
                        sections.append({
                            'title': current_section,
                            'content': '\n'.join(current_content),
                            'metadata': {'level': current_section.count('#')}
                        })
                    
                    # Start new section
                    current_section = line.strip('#').strip()
                    current_content = []
                else:
                    current_content.append(line)
            
            # Save last section
            if current_section:
                sections.append({
                    'title': current_section,
                    'content': '\n'.join(current_content),
                    'metadata': {'level': current_section.count('#') if current_section.startswith('#') else 1}
                })
        
        return sections

    def _extract_api_references(self, content: str) -> List[str]:
        """Extract API references from documentation"""
        # Simple extraction - look for function-like patterns
        import re
        
        # Pattern for function calls or method names
        pattern = r'`([a-zA-Z_][a-zA-Z0-9_]*\([^)]*\))`'
        matches = re.findall(pattern, content)
        
        return matches

    def _extract_code_examples(self, content: str) -> List[str]:
        """Extract code examples from documentation"""
        # Simple extraction - look for code blocks
        import re
        
        # Pattern for markdown code blocks
        pattern = r'```[a-zA-Z]*\n(.*?)\n```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        return matches