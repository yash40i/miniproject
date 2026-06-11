"""
Utility functions for Resume-Insight AI pipeline.
Helper functions for logging, validation, and data processing.
"""

import logging
from typing import List, Dict, Any
import json
from pathlib import Path


# Configure logging
def setup_logging(log_level: int = logging.INFO) -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger("resume_insight")
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(log_level)
    return logger


def validate_pdf_file(pdf_path: str) -> bool:
    """
    Validate that PDF file exists and is readable.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        True if valid, False otherwise
    """
    path = Path(pdf_path)
    
    if not path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        return False
    
    if path.suffix.lower() != '.pdf':
        print(f"Error: File is not a PDF: {pdf_path}")
        return False
    
    if not path.is_file():
        print(f"Error: Path is not a file: {pdf_path}")
        return False
    
    return True


def validate_job_description(text: str) -> bool:
    """
    Validate job description text.
    
    Args:
        text: Job description text
        
    Returns:
        True if valid, False otherwise
    """
    if not text or len(text.strip()) < 50:
        print("Error: Job description too short (minimum 50 characters)")
        return False
    
    return True


def save_results_to_json(results: Dict[str, Any], output_path: str) -> None:
    """
    Save analysis results to JSON file.
    
    Args:
        results: Dictionary of results
        output_path: Output file path
    """
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"Results saved to: {output_path}")


def load_job_description(file_path: str) -> str:
    """
    Load job description from text file.
    
    Args:
        file_path: Path to job description file
        
    Returns:
        Job description text
    """
    with open(file_path, 'r') as f:
        return f.read()


def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract potential skills from text using simple heuristics.
    
    Args:
        text: Input text
        
    Returns:
        List of extracted skills
    """
    # Simple extraction: split by common delimiters and filter
    skills = []
    
    for delimiter in [',', ';', '\n', '|', '•', '·']:
        parts = text.split(delimiter)
        for part in parts:
            part = part.strip()
            # Keep if 2-30 characters and looks like a skill
            if 2 <= len(part) <= 30 and not part.startswith('-'):
                skills.append(part)
    
    # Remove duplicates and sort
    skills = list(set(skills))
    skills.sort()
    
    return skills


def calculate_improvement_percentage(current: float, target: float) -> float:
    """
    Calculate improvement percentage.
    
    Args:
        current: Current score
        target: Target score
        
    Returns:
        Improvement percentage
    """
    if current >= target:
        return 0.0
    
    improvement = ((target - current) / (100 - current)) * 100
    return improvement
