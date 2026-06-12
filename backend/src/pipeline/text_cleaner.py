"""
Text cleaning module for Resume-Insight AI.
Handles text normalization, standardization, and noise removal.
"""

import re
import nltk
from typing import List
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import spacy

from src.config.config import TextCleaningConfig

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class TextCleaner:
    """
    Comprehensive text cleaning pipeline using spaCy and NLTK.
    Handles URL removal, abbreviation expansion, and standardization.
    """
    
    # Common abbreviations in resumes
    ABBREVIATIONS = {
        "ML": "Machine Learning",
        "AI": "Artificial Intelligence",
        "NLP": "Natural Language Processing",
        "CV": "Computer Vision",
        "DL": "Deep Learning",
        "SQL": "Structured Query Language",
        "API": "Application Programming Interface",
        "REST": "Representational State Transfer",
        "JSON": "JavaScript Object Notation",
        "HTML": "HyperText Markup Language",
        "CSS": "Cascading Style Sheets",
        "JS": "JavaScript",
        "UI": "User Interface",
        "UX": "User Experience",
        "MVP": "Minimum Viable Product",
        "SaaS": "Software as a Service",
        "AWS": "Amazon Web Services",
        "GCP": "Google Cloud Platform",
        "CI/CD": "Continuous Integration Continuous Deployment",
        "DevOps": "Development Operations",
        "RDBMS": "Relational Database Management System",
        "NoSQL": "Not Only SQL",
        "ETL": "Extract Transform Load",
        "BI": "Business Intelligence",
        "AR": "Augmented Reality",
        "VR": "Virtual Reality",
    }
    
    def __init__(self, config: TextCleaningConfig = None):
        """
        Initialize text cleaner.
        
        Args:
            config: TextCleaningConfig object
        """
        self.config = config or TextCleaningConfig()
        
        # Load spaCy model for advanced NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spaCy model...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        self.stop_words = set(stopwords.words('english'))
    
    def clean(self, text: str) -> str:
        """
        Apply full cleaning pipeline to text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Step 1: Remove URLs
        if self.config.remove_urls:
            text = self._remove_urls(text)
        
        # Step 2: Remove emails
        if self.config.remove_emails:
            text = self._remove_emails(text)
        
        # Step 3: Expand abbreviations
        if self.config.expand_abbreviations:
            text = self._expand_abbreviations(text)
        
        # Step 4: Lowercase
        if self.config.lowercase:
            text = text.lower()
        
        # Step 5: Remove extra whitespace
        if self.config.remove_extra_whitespace:
            text = self._remove_extra_whitespace(text)
        
        # Step 6: Remove special characters (optional)
        if self.config.remove_special_chars:
            text = self._remove_special_characters(text)
        
        # Step 7: Remove stopwords (optional)
        if self.config.remove_stopwords:
            text = self._remove_stopwords(text)
        
        return text
    
    def clean_with_nlp(self, text: str) -> str:
        """
        Clean text with advanced spaCy NLP processing.
        Includes lemmatization and POS-based filtering.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned and processed text
        """
        # First apply basic cleaning
        text = self.clean(text)
        
        # Process with spaCy
        doc = self.nlp(text)
        
        # Extract meaningful tokens (nouns, verbs, adjectives, proper nouns)
        meaningful_tokens = []
        for token in doc:
            if token.pos_ in ["NOUN", "VERB", "ADJ", "PROPN"]:
                meaningful_tokens.append(token.lemma_)
        
        return " ".join(meaningful_tokens)
    
    def _remove_urls(self, text: str) -> str:
        """Remove URLs from text."""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.sub(url_pattern, "", text)
    
    def _remove_emails(self, text: str) -> str:
        """Remove email addresses from text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.sub(email_pattern, "", text)
    
    def _expand_abbreviations(self, text: str) -> str:
        """Expand common abbreviations."""
        for abbr, expansion in self.ABBREVIATIONS.items():
            # Use word boundaries to avoid partial replacements
            pattern = r'\b' + re.escape(abbr) + r'\b'
            text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
        return text
    
    def _remove_extra_whitespace(self, text: str) -> str:
        """Remove extra whitespace and normalize line breaks."""
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        # Replace multiple line breaks with double line break
        text = re.sub(r'\n\n+', '\n\n', text)
        return text.strip()
    
    def _remove_special_characters(self, text: str) -> str:
        """Remove special characters, keep alphanumeric and common punctuation."""
        # Keep letters, numbers, spaces, and common punctuation
        text = re.sub(r'[^a-zA-Z0-9\s\.\,\-]', '', text)
        return text
    
    def _remove_stopwords(self, text: str) -> str:
        """Remove common English stopwords."""
        tokens = word_tokenize(text)
        filtered_tokens = [token for token in tokens if token.lower() not in self.stop_words]
        return " ".join(filtered_tokens)


def clean_text(text: str, config: TextCleaningConfig = None) -> str:
    """
    Convenience function to clean text.
    
    Args:
        text: Text to clean
        config: TextCleaningConfig object
        
    Returns:
        Cleaned text
    """
    cleaner = TextCleaner(config)
    return cleaner.clean(text)
