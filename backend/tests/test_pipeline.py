"""
Integration test for the complete Resume-Insight AI pipeline.
Tests end-to-end functionality with sample data.
"""

import sys
from pathlib import Path
import pytest

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import PipelineConfig, EmbeddingConfig, TextCleaningConfig
from src.pipeline.text_cleaner import TextCleaner
from src.pipeline.embeddings import EmbeddingGenerator
from src.pipeline.semantic_matcher import SemanticMatcher


class TestTextCleaning:
    """Test text cleaning functionality."""
    
    def test_basic_cleaning(self):
        """Test basic text cleaning."""
        cleaner = TextCleaner()
        
        text = "  Check out https://example.com and email me at test@email.com  "
        cleaned = cleaner.clean(text)
        
        assert "https://example.com" not in cleaned
        assert "test@email.com" not in cleaned
        assert "  " not in cleaned
    
    def test_abbreviation_expansion(self):
        """Test abbreviation expansion."""
        cleaner = TextCleaner()
        
        text = "Experience with ML and AI"
        cleaned = cleaner.clean(text)
        
        assert "machine learning" in cleaned
        assert "artificial intelligence" in cleaned


class TestEmbeddings:
    """Test embedding generation."""
    
    def test_embed_single_text(self):
        """Test embedding a single text."""
        gen = EmbeddingGenerator()
        embedding = gen.embed("This is a test sentence")
        
        assert embedding.shape == (384,)  # Default model dimension
    
    def test_embed_multiple_texts(self):
        """Test embedding multiple texts."""
        gen = EmbeddingGenerator()
        texts = ["First text", "Second text", "Third text"]
        embeddings = gen.embed(texts)
        
        assert embeddings.shape == (3, 384)
    
    def test_similarity_calculation(self):
        """Test cosine similarity calculation."""
        gen = EmbeddingGenerator()
        
        embed1 = gen.embed("Python programming")
        embed2 = gen.embed("Python coding")
        
        similarity = gen.similarity(embed1, embed2)
        
        # Should be high similarity
        assert 0.5 < similarity < 1.0


class TestSemanticMatching:
    """Test semantic matching."""
    
    def test_basic_matching(self):
        """Test basic matching between resume and job."""
        matcher = SemanticMatcher()
        
        resume = "Experience in Python, Machine Learning, and Data Analysis"
        job = "Required skills: Python, ML, and Data Science"
        
        result = matcher.match(resume, job)
        
        # Should find some matches
        assert len(result.matched_skills) > 0
        assert result.overall_score > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
