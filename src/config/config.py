"""
Configuration module for Resume-Insight AI pipeline.
Manages all settings, API keys, and model configurations.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    model_name: str = "all-MiniLM-L6-v2"  # Default: 384 dims, lightweight & fast
    # Alternative: "all-mpnet-base-v2"  # 768 dims, slower but more accurate
    device: str = "cpu"  # Use "cuda" if GPU available
    batch_size: int = 32
    normalize_embeddings: bool = True


@dataclass
class TextCleaningConfig:
    """Configuration for text cleaning pipeline."""
    remove_urls: bool = True
    remove_emails: bool = True
    lowercase: bool = True
    remove_extra_whitespace: bool = True
    remove_special_chars: bool = False  # Set True to remove symbols
    expand_abbreviations: bool = True
    remove_stopwords: bool = False  # Set True to remove common words


@dataclass
class SemanticMatchingConfig:
    """Configuration for semantic matching."""
    similarity_threshold: float = 0.5  # Minimum similarity to consider a match
    top_k_matches: int = 10  # Return top-k skill matches
    chunk_size: int = 100  # Character limit for text chunks


@dataclass
class LLMConfig:
    """Configuration for LLM-based feedback generation."""
    provider: str = "groq"  # Options: "openai", "groq", "gemini" - Groq is FREE!
    model: str = "llama-3.1-8b-instant"  # Fast Llama 3.1 model - free & reliable
    temperature: float = 0.7
    max_tokens: int = 1000
    api_key: Optional[str] = None
    
    def __post_init__(self):
        """Load API key from environment if not provided."""
        if self.api_key is None:
            env_var = f"{self.provider.upper()}_API_KEY"
            self.api_key = os.getenv(env_var)
            if not self.api_key:
                raise ValueError(
                    f"LLM API key not found. Set {env_var} environment variable."
                )


@dataclass
class PipelineConfig:
    """Main pipeline configuration."""
    embedding_config: EmbeddingConfig = None
    text_cleaning_config: TextCleaningConfig = None
    semantic_matching_config: SemanticMatchingConfig = None
    llm_config: LLMConfig = None
    
    # Feature flags
    enable_feedback_generation: bool = True
    enable_learning_path_generation: bool = True
    
    def __post_init__(self):
        """Initialize nested configs with defaults."""
        if self.embedding_config is None:
            self.embedding_config = EmbeddingConfig()
        if self.text_cleaning_config is None:
            self.text_cleaning_config = TextCleaningConfig()
        if self.semantic_matching_config is None:
            self.semantic_matching_config = SemanticMatchingConfig()
        if self.llm_config is None:
            try:
                self.llm_config = LLMConfig()
            except ValueError:
                # LLM is optional for now
                self.llm_config = None
                self.enable_feedback_generation = False


# Global default configuration
DEFAULT_CONFIG = PipelineConfig()
