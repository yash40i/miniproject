"""
Quick start guide for Resume-Insight AI
"""

# QUICK START GUIDE

## Step 1: Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

## Step 2: Configuration

Create `.env` file:

```env
OPENAI_API_KEY=sk_...  # Or GROQ_API_KEY or GEMINI_API_KEY
```

## Step 3: Basic Usage

```python
from src.pipeline import run_pipeline

result = run_pipeline(
    resume_path="your_resume.pdf",
    job_description="Job description text..."
)

# Get results
print(f"Match Score: {result.matching_result.overall_score}%")
print(f"Missing Skills: {result.matching_result.missing_skills}")
```

## Pipeline Stages

1. **PDF Parsing** → Extract text from resume
2. **Text Cleaning** → Remove noise, expand abbreviations
3. **Embedding** → Convert to vector representation
4. **Semantic Matching** → Find skill correspondences
5. **LLM Feedback** → Generate recommendations
6. **Learning Path** → Create learning roadmap

## Example: Full Report

```python
from src.pipeline import ResumePipeline, run_pipeline
from src.config import PipelineConfig

config = PipelineConfig()
result = run_pipeline("resume.pdf", "job_description.txt", config)

pipeline = ResumePipeline(config)
report = pipeline.format_report(result)
print(report)
```

## Configuration Options

```python
from src.config import PipelineConfig, EmbeddingConfig, LLMConfig

config = PipelineConfig(
    embedding_config=EmbeddingConfig(
        model_name="all-MiniLM-L6-v2",  # Fast
        device="cpu"
    ),
    llm_config=LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        temperature=0.7
    )
)
```

## Available Models

- **Embedding**: all-MiniLM-L6-v2 (fast), all-mpnet-base-v2 (accurate)
- **LLM**: OpenAI (gpt-3.5-turbo), Groq (mixtral-8x7b)

## Troubleshooting

- **spaCy model error**: `python -m spacy download en_core_web_sm`
- **API key error**: Ensure .env file is created with valid API key
- **PDF parsing issues**: Check PDF is not corrupted or password-protected

## Next Steps

1. Test with sample resume + job description
2. Review matching results and feedback
3. Optimize embedding model for your use case
4. Integrate with frontend (coming soon)
"""
