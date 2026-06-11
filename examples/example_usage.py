"""
Example usage of Resume-Insight AI pipeline.
Demonstrates complete workflow from PDF parsing to learning path generation.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline import run_pipeline
from src.config import PipelineConfig, EmbeddingConfig
from src.utils import validate_pdf_file, validate_job_description


def main():
    """Run example analysis."""
    
    print("🚀 Resume-Insight AI - Example Pipeline Run")
    print("=" * 80)
    
    # Example paths and job description
    # For testing, you'll need to provide actual files
    resume_path = "path/to/your/resume.pdf"
    
    job_description = """
    Senior Data Scientist - Requirements:
    - 5+ years of experience with Python and Machine Learning
    - Strong background in Deep Learning and Neural Networks
    - Experience with TensorFlow and PyTorch
    - SQL and database optimization skills
    - Experience with cloud platforms (AWS/GCP)
    - Strong communication and presentation skills
    - Background in Natural Language Processing preferred
    - Experience with data visualization tools (Tableau, PowerBI)
    
    Responsibilities:
    - Build and deploy machine learning models
    - Analyze large-scale datasets
    - Collaborate with engineering teams
    - Present insights to stakeholders
    - Mentoring junior data scientists
    """
    
    # Validate inputs
    print("\n📋 Validating Inputs...")
    if not validate_pdf_file(resume_path):
        print(f"⚠️  Using placeholder for demonstration (actual resume not found)")
        resume_path = None
    
    if not validate_job_description(job_description):
        print("❌ Invalid job description")
        return
    
    print("✅ Inputs validated")
    
    # Configure pipeline
    print("\n⚙️  Configuring Pipeline...")
    config = PipelineConfig(
        embedding_config=EmbeddingConfig(
            model_name="all-MiniLM-L6-v2",  # Lightweight, fast
            device="cpu",
        ),
        enable_feedback_generation=True,
        enable_learning_path_generation=True,
    )
    print("✅ Pipeline configured")
    
    # Run pipeline (only if resume exists)
    if resume_path and Path(resume_path).exists():
        print("\n🔄 Running Analysis Pipeline...")
        result = run_pipeline(
            resume_path=resume_path,
            job_description=job_description,
            config=config
        )
        
        # Display results
        print("\n" + "=" * 80)
        from src.pipeline import ResumePipeline
        pipeline = ResumePipeline(config)
        report = pipeline.format_report(result)
        print(report)
        
    else:
        print("\n⚠️  Demonstration Mode: Resume file not found")
        print("To use the full pipeline, provide a valid PDF resume path")
        print("\nExample usage:")
        print("  result = run_pipeline('path/to/resume.pdf', job_description)")


if __name__ == "__main__":
    main()
