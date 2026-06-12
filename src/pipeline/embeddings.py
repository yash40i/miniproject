"""
Embedding generation module for Resume-Insight AI.
Converts text into high-dimensional vector embeddings using Sentence Transformers.
"""

import numpy as np
from typing import List, Union, Tuple
from sentence_transformers import SentenceTransformer
import torch

from src.config.config import EmbeddingConfig


class EmbeddingGenerator:
    """
    Generates embeddings using Sentence Transformers.
    Supports multiple models with different dimensions and accuracy trade-offs.
    """
    
    # Pre-configured models
    MODELS = {
        "lightweight": "all-MiniLM-L6-v2",        # 384 dims, fast
        "balanced": "all-mpnet-base-v2",          # 768 dims, balanced
        "accurate": "all-roberta-large-v1",       # 1024 dims, slow but accurate
    }
    
    def __init__(self, config: EmbeddingConfig = None):
        """
        Initialize embedding generator.
        
        Args:
            config: EmbeddingConfig object
        """
        self.config = config or EmbeddingConfig()
        
        # Load model
        self.model = SentenceTransformer(
            self.config.model_name,
            device=self._get_device()
        )
        
        # Get embedding dimension
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def _get_device(self) -> str:
        """Determine which device to use (CPU or GPU)."""
        if self.config.device == "cuda" and torch.cuda.is_available():
            return "cuda"
        elif self.config.device == "mps" and torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    
    def embed(self, texts: Union[str, List[str]]) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Generate embeddings for one or more texts.
        
        Args:
            texts: Single text string or list of text strings
            
        Returns:
            Single embedding array or list of embedding arrays
        """
        if isinstance(texts, str):
            # Single text
            if not texts or len(texts.strip()) == 0:
                # Return empty embedding
                return np.array([])
            embedding = self.model.encode(
                texts,
                normalize_embeddings=self.config.normalize_embeddings
            )
            return embedding
        else:
            # Multiple texts - filter out empty strings
            if not texts or len(texts) == 0:
                # Return empty array
                return np.array([])
            
            # Filter out empty strings
            non_empty_texts = [t for t in texts if t and len(t.strip()) > 0]
            if not non_empty_texts:
                # All texts were empty
                return np.array([])
            
            # Multiple texts
            embeddings = self.model.encode(
                non_empty_texts,
                batch_size=self.config.batch_size,
                normalize_embeddings=self.config.normalize_embeddings,
                show_progress_bar=True
            )
            return embeddings
    
    def embed_with_pooling(
        self,
        texts: Union[str, List[str]],
        pooling_method: str = "mean"
    ) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Generate embeddings with optional pooling for chunk aggregation.
        
        Args:
            texts: Single text or list of texts
            pooling_method: "mean", "max", or "cls"
            
        Returns:
            Pooled embeddings
        """
        return self.embed(texts)
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0 to 1)
        """
        # Normalize embeddings if not already normalized
        norm1 = embedding1 / (np.linalg.norm(embedding1) + 1e-8)
        norm2 = embedding2 / (np.linalg.norm(embedding2) + 1e-8)
        
        similarity = np.dot(norm1, norm2)
        return float(similarity)
    
    def batch_similarity(
        self,
        embeddings1: List[np.ndarray],
        embeddings2: List[np.ndarray]
    ) -> np.ndarray:
        """
        Calculate similarities between two sets of embeddings.
        
        Args:
            embeddings1: List of embedding vectors (N, D)
            embeddings2: List of embedding vectors (M, D)
            
        Returns:
            Similarity matrix (N, M)
        """
        # Convert to numpy arrays if needed
        embeddings1 = np.array(embeddings1)
        embeddings2 = np.array(embeddings2)
        
        # Handle empty embeddings2 list (no job chunks)
        if len(embeddings2) == 0:
            if embeddings1.ndim == 1:
                embeddings1 = embeddings1.reshape(1, -1)
            n_rows = embeddings1.shape[0] if embeddings1.size > 0 else 0
            # Return empty matrix with shape (N, 0)
            return np.empty((n_rows, 0))
        
        # Handle empty embeddings1 list (no resume chunks)
        if len(embeddings1) == 0:
            if embeddings2.ndim == 1:
                embeddings2 = embeddings2.reshape(1, -1)
            m_cols = embeddings2.shape[0] if embeddings2.size > 0 else 0
            # Return empty matrix with shape (0, M)
            return np.empty((0, m_cols))
        
        # Ensure 2D arrays
        if embeddings1.ndim == 1:
            embeddings1 = embeddings1.reshape(1, -1)
        if embeddings2.ndim == 1:
            embeddings2 = embeddings2.reshape(1, -1)
        
        # Normalize
        embeddings1 = embeddings1 / (np.linalg.norm(embeddings1, axis=1, keepdims=True) + 1e-8)
        embeddings2 = embeddings2 / (np.linalg.norm(embeddings2, axis=1, keepdims=True) + 1e-8)
        
        # Compute similarity matrix
        similarity_matrix = np.dot(embeddings1, embeddings2.T)
        
        return similarity_matrix
    
    def most_similar(
        self,
        query_embedding: np.ndarray,
        corpus_embeddings: List[np.ndarray],
        top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Find most similar embeddings to a query.
        
        Args:
            query_embedding: Query embedding vector
            corpus_embeddings: List of corpus embeddings
            top_k: Number of top matches to return
            
        Returns:
            List of (index, similarity_score) tuples
        """
        corpus_embeddings = np.array(corpus_embeddings)
        
        # Compute similarities
        similarities = self.batch_similarity([query_embedding], corpus_embeddings)[0]
        
        # Get top-k indices
        top_k_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Return with scores
        results = [(int(idx), float(similarities[idx])) for idx in top_k_indices]
        
        return results
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        return {
            "model_name": self.config.model_name,
            "embedding_dim": self.embedding_dim,
            "device": self._get_device(),
            "normalize": self.config.normalize_embeddings,
        }


def embed_text(text: str, config: EmbeddingConfig = None) -> np.ndarray:
    """
    Convenience function to embed a single text.
    
    Args:
        text: Text to embed
        config: EmbeddingConfig object
        
    Returns:
        Embedding vector
    """
    generator = EmbeddingGenerator(config)
    return generator.embed(text)
