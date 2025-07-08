"""
ML Utilities for MCP Servers
Shared ML functionality including embeddings, model loading, and vector operations
"""

import asyncio
import logging
import os
import pickle
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import faiss

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingConfig:
    """Configuration for embedding models"""
    model_name: str
    device: str = "cpu"
    max_length: int = 512
    cache_dir: Optional[str] = None
    normalize: bool = True


class EmbeddingManager:
    """Manages embedding models and vector operations"""
    
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self._model_loaded = False
        
        # Set device
        if config.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = config.device
        
        logger.info(f"Embedding manager initialized with device: {self.device}")
    
    async def load_model(self) -> None:
        """Load embedding model asynchronously"""
        if self._model_loaded:
            return
        
        try:
            logger.info(f"Loading embedding model: {self.config.model_name}")
            
            # Use different loading strategies based on model type
            if "sentence-transformers" in self.config.model_name or "all-" in self.config.model_name:
                # Sentence Transformers model
                self.model = SentenceTransformer(
                    self.config.model_name,
                    device=self.device,
                    cache_folder=self.config.cache_dir
                )
            else:
                # Hugging Face Transformers model
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.config.model_name,
                    cache_dir=self.config.cache_dir
                )
                self.model = AutoModel.from_pretrained(
                    self.config.model_name,
                    cache_dir=self.config.cache_dir
                )
                self.model.to(self.device)
                self.model.eval()
            
            self._model_loaded = True
            logger.info(f"Model {self.config.model_name} loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model {self.config.model_name}: {e}")
            raise
    
    async def encode_texts(self, texts: List[str]) -> np.ndarray:
        """Encode texts to embeddings"""
        await self.load_model()
        
        if not texts:
            return np.array([])
        
        try:
            if isinstance(self.model, SentenceTransformer):
                # Sentence Transformers
                embeddings = self.model.encode(
                    texts,
                    normalize_embeddings=self.config.normalize,
                    convert_to_numpy=True
                )
            else:
                # Hugging Face Transformers
                embeddings = await self._encode_with_transformers(texts)
            
            logger.debug(f"Encoded {len(texts)} texts to embeddings of shape {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to encode texts: {e}")
            raise
    
    async def _encode_with_transformers(self, texts: List[str]) -> np.ndarray:
        """Encode texts using Hugging Face Transformers"""
        embeddings = []
        
        with torch.no_grad():
            for text in texts:
                # Tokenize
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    padding=True,
                    max_length=self.config.max_length
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # Get embeddings
                outputs = self.model(**inputs)
                # Use CLS token or mean pooling
                embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
                
                if self.config.normalize:
                    embedding = embedding / np.linalg.norm(embedding)
                
                embeddings.append(embedding[0])
        
        return np.array(embeddings)
    
    async def encode_code(self, code_snippets: List[str], language: str = "python") -> np.ndarray:
        """Encode code snippets with language context"""
        # Add language context to code
        contextualized_code = [
            f"Language: {language}\nCode:\n{code}" for code in code_snippets
        ]
        return await self.encode_texts(contextualized_code)
    
    def compute_similarity(self, embeddings1: np.ndarray, embeddings2: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between embeddings"""
        # Normalize embeddings
        norm1 = np.linalg.norm(embeddings1, axis=1, keepdims=True)
        norm2 = np.linalg.norm(embeddings2, axis=1, keepdims=True)
        
        normalized1 = embeddings1 / (norm1 + 1e-8)
        normalized2 = embeddings2 / (norm2 + 1e-8)
        
        # Compute cosine similarity
        return np.dot(normalized1, normalized2.T)


class VectorDatabase:
    """FAISS-based vector database for fast similarity search"""
    
    def __init__(self, dimension: int, index_type: str = "flat"):
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.metadata = []
        self._build_index()
    
    def _build_index(self) -> None:
        """Build FAISS index based on type"""
        if self.index_type == "flat":
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        elif self.index_type == "ivf":
            quantizer = faiss.IndexFlatIP(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
        elif self.index_type == "hnsw":
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")
        
        logger.info(f"Built FAISS index: {self.index_type} with dimension {self.dimension}")
    
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        """Add vectors to the index"""
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Vector dimension {vectors.shape[1]} doesn't match index dimension {self.dimension}")
        
        # Normalize vectors for cosine similarity
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        normalized_vectors = vectors / (norms + 1e-8)
        
        # Train index if needed
        if hasattr(self.index, 'is_trained') and not self.index.is_trained:
            self.index.train(normalized_vectors)
        
        # Add to index
        start_id = len(self.metadata)
        self.index.add(normalized_vectors)
        self.metadata.extend(metadata)
        
        logger.info(f"Added {len(vectors)} vectors to index (total: {self.index.ntotal})")
    
    def search(self, query_vectors: np.ndarray, k: int = 10) -> Tuple[np.ndarray, List[List[Dict[str, Any]]]]:
        """Search for similar vectors"""
        if self.index.ntotal == 0:
            return np.array([]), [[]]
        
        # Normalize query vectors
        norms = np.linalg.norm(query_vectors, axis=1, keepdims=True)
        normalized_queries = query_vectors / (norms + 1e-8)
        
        # Search
        scores, indices = self.index.search(normalized_queries, min(k, self.index.ntotal))
        
        # Get metadata for results
        results_metadata = []
        for query_indices in indices:
            query_metadata = []
            for idx in query_indices:
                if idx != -1 and idx < len(self.metadata):
                    query_metadata.append(self.metadata[idx])
                else:
                    query_metadata.append({})
            results_metadata.append(query_metadata)
        
        return scores, results_metadata
    
    def save(self, filepath: str) -> None:
        """Save index and metadata to file"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(path.with_suffix('.faiss')))
        
        # Save metadata
        with open(path.with_suffix('.metadata'), 'wb') as f:
            pickle.dump({
                'metadata': self.metadata,
                'dimension': self.dimension,
                'index_type': self.index_type
            }, f)
        
        logger.info(f"Saved vector database to {filepath}")
    
    def load(self, filepath: str) -> None:
        """Load index and metadata from file"""
        path = Path(filepath)
        
        # Load FAISS index
        self.index = faiss.read_index(str(path.with_suffix('.faiss')))
        
        # Load metadata
        with open(path.with_suffix('.metadata'), 'rb') as f:
            data = pickle.load(f)
            self.metadata = data['metadata']
            self.dimension = data['dimension']
            self.index_type = data['index_type']
        
        logger.info(f"Loaded vector database from {filepath}")


class ModelCache:
    """Cache for ML models and embeddings"""
    
    def __init__(self, cache_dir: str = ".model_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self._memory_cache = {}
    
    def get_cache_path(self, key: str) -> Path:
        """Get cache file path for a key"""
        return self.cache_dir / f"{key}.pkl"
    
    def save(self, key: str, data: Any) -> None:
        """Save data to cache"""
        cache_path = self.get_cache_path(key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            logger.debug(f"Saved to cache: {key}")
        except Exception as e:
            logger.warning(f"Failed to save cache {key}: {e}")
    
    def load(self, key: str) -> Optional[Any]:
        """Load data from cache"""
        # Check memory cache first
        if key in self._memory_cache:
            return self._memory_cache[key]
        
        # Check disk cache
        cache_path = self.get_cache_path(key)
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                # Store in memory cache
                self._memory_cache[key] = data
                logger.debug(f"Loaded from cache: {key}")
                return data
            except Exception as e:
                logger.warning(f"Failed to load cache {key}: {e}")
        
        return None
    
    def clear(self) -> None:
        """Clear all caches"""
        self._memory_cache.clear()
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        logger.info("Cleared all caches")


# Convenience functions
async def encode_texts_with_model(
    texts: List[str],
    model_name: str = "all-MiniLM-L6-v2",
    device: str = "auto"
) -> np.ndarray:
    """Quick function to encode texts with a specific model"""
    config = EmbeddingConfig(model_name=model_name, device=device)
    manager = EmbeddingManager(config)
    return await manager.encode_texts(texts)


async def encode_code_snippets(
    code_snippets: List[str],
    language: str = "python",
    model_name: str = "microsoft/codebert-base"
) -> np.ndarray:
    """Quick function to encode code snippets"""
    config = EmbeddingConfig(model_name=model_name)
    manager = EmbeddingManager(config)
    return await manager.encode_code(code_snippets, language)


# Example usage
if __name__ == "__main__":
    async def test_embeddings():
        # Test text embeddings
        texts = ["Hello world", "Machine learning", "Natural language processing"]
        embeddings = await encode_texts_with_model(texts)
        print(f"Text embeddings shape: {embeddings.shape}")
        
        # Test code embeddings
        code_samples = [
            "def hello(): return 'world'",
            "class MyClass: pass",
            "import numpy as np"
        ]
        code_embeddings = await encode_code_snippets(code_samples)
        print(f"Code embeddings shape: {code_embeddings.shape}")
        
        # Test vector database
        db = VectorDatabase(dimension=embeddings.shape[1])
        metadata = [{"text": text} for text in texts]
        db.add_vectors(embeddings, metadata)
        
        # Search
        query_embedding = embeddings[:1]  # Use first embedding as query
        scores, results = db.search(query_embedding, k=2)
        print(f"Search results: {scores}, {results}")
    
    asyncio.run(test_embeddings())