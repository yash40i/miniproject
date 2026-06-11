"""
Main package __init__.py file.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__description__ = "Resume-Insight AI - Semantic Resume Analysis & Learning Path Generation"

# Import main components
from src.pipeline import run_pipeline, ResumePipeline
from src.config import PipelineConfig

__all__ = [
    'run_pipeline',
    'ResumePipeline',
    'PipelineConfig',
]
