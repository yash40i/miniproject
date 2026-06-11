# Resume-Insight AI - Core ML Pipeline
# Complete NLP/ML-based Resume Analysis Engine

## 🎯 Project Overview

Resume-Insight AI is a sophisticated NLP and Machine Learning pipeline for semantic resume analysis. It matches resumes against job descriptions using advanced embeddings and generates personalized learning paths for skill development.

### Core Features (MVP Priority)

✅ **Layout-Aware PDF Parsing** - Multi-column resume extraction with logical reading order  
✅ **Advanced Text Cleaning** - Abbreviation expansion, noise removal, NLP standardization  
✅ **Semantic Embeddings** - High-dimensional vector representation using Sentence Transformers  
✅ **Intelligent Matching** - Cosine similarity-based semantic skill matching  
✅ **LLM-Powered Feedback** - Human-readable gap analysis and recommendations  
✅ **Learning Path Generation** - Structured milestone roadmaps with timelines  

---

## 📁 Project Structure

```
res_project/
├── src/
│   ├── __init__.py
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── pdf_parser.py          # PyMuPDF multi-column extraction
│   │   ├── text_cleaner.py        # spaCy/NLTK text standardization
│   │   ├── embeddings.py          # Sentence Transformers embeddings
│   │   ├── semantic_matcher.py    # Cosine similarity matching
│   │   ├── llm_feedback.py        # LLM-based feedback generation
│   │   ├── learning_path.py       # Learning roadmap generation
│   │   └── pipeline.py            # Main orchestrator
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py              # Configuration management
│   └── utils/
│       ├── __init__.py
│       └── helpers.py             # Utility functions
├── examples/
│   └── example_usage.py           # Complete example
├── tests/
│   └── (test files coming soon)
├── requirements.txt               # Python dependencies
├── setup.py                       # Package setup
├── .env.example                   # Environment variables template
└── README.md                      # Documentation
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone <repo-url>
cd res_project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model (one-time)
python -m spacy download en_core_web_sm
```

### 2. Configuration

Create `.env` file with API keys:

```env
# OpenAI (for LLM feedback generation)
OPENAI_API_KEY=sk_...

# Or Groq (faster LLM inference)
GROQ_API_KEY=gr_...

# Or Gemini
GEMINI_API_KEY=AIza...
```

### 3. Basic Usage

```python
from src.pipeline import run_pipeline

# Analyze resume
result = run_pipeline(
    resume_path="path/to/resume.pdf",
    job_description="Job description text here..."
)

# Display report
from src.pipeline import ResumePipeline
from src.config import PipelineConfig

config = PipelineConfig()
pipeline = ResumePipeline(config)
print(pipeline.format_report(result))
```

---

## 📊 Pipeline Architecture

### Stage 1: Input Stage
- **Resume:** PDF file (supports multi-page, multi-column layouts)
- **Job Description:** Plain text

### Stage 2: Layout-Aware Parsing
```
PDF → PyMuPDF → Block Detection → Position Sorting → Logical Text
```

### Stage 3: Text Cleaning
```
Raw Text → URL/Email Removal → Abbreviation Expansion → Lowercasing → Whitespace Normalization
```

### Stage 4: Embedding Generation
```
Text → Sentence Transformers (all-MiniLM-L6-v2 or all-mpnet-base-v2) → 384/768-dim vectors
```

### Stage 5: Semantic Matching
```
Resume Embeddings vs Job Embeddings → Cosine Similarity Matrix → Top-K Matching → Skill Gaps
```

### Stage 6: LLM Feedback (Optional)
```
Matching Results → OpenAI/Groq LLM → Gap Analysis + Recommendations
```

### Stage 7: Learning Path Generation
```
Priority Skills → Milestone Creation → Timeline Scheduling → Curated Resources
```

---

## 🔧 Configuration

All components are configurable via `PipelineConfig`:

```python
from src.config import PipelineConfig, EmbeddingConfig, LLMConfig

config = PipelineConfig(
    embedding_config=EmbeddingConfig(
        model_name="all-MiniLM-L6-v2",  # Fast, 384-dims
        # or "all-mpnet-base-v2"         # Accurate, 768-dims
        device="cpu"                     # Use "cuda" for GPU
    ),
    llm_config=LLMConfig(
        provider="openai",               # or "groq", "gemini"
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=1000
    ),
    enable_feedback_generation=True,
    enable_learning_path_generation=True
)
```

---

## 📈 Model Specifications

### Embedding Models

| Model | Dimensions | Inference Time | Use Case |
|-------|-----------|-----------------|----------|
| all-MiniLM-L6-v2 | 384 | ~50ms | Fast prototyping, mobile |
| all-mpnet-base-v2 | 768 | ~200ms | Balanced accuracy |
| all-roberta-large-v1 | 1024 | ~500ms | Maximum accuracy |

### LLM Providers

- **OpenAI:** Most capable, higher cost
- **Groq:** Faster inference, good quality
- **Gemini:** (Coming soon)

---

## 💡 Key Components

### PDFParser
Extracts text from PDFs with multi-column support using PyMuPDF's block detection.

### TextCleaner
Comprehensive text normalization including:
- URL/email removal
- Abbreviation expansion (ML→Machine Learning)
- Stopword removal
- Lemmatization via spaCy

### EmbeddingGenerator
Converts text to high-dimensional vectors using Sentence Transformers.
- Batch processing support
- Similarity computation
- Top-K retrieval

### SemanticMatcher
Identifies conceptual matches between resume and job description.
- Chunk-based extraction
- Cosine similarity scoring
- Match strength classification

### LLMFeedbackGenerator
Generates prescriptive feedback:
- Gap analysis
- Specific recommendations
- Priority skill identification
- Actionable next steps

### LearningPathGenerator
Creates structured learning roadmaps:
- Milestone-based milestones
- Realistic timelines
- Curated resource links
- Difficulty estimation

---

## 📚 Output Format

### Analysis Result
```python
AnalysisResult(
    matching_result=MatchingResult(
        overall_score=78.5,              # 0-100
        matched_skills=[...],             # List of SkillMatch objects
        missing_skills=[...],             # Skills to develop
        matched_percentage=75.0
    ),
    feedback_result=FeedbackResult(
        gap_analysis="...",
        recommendations=[...],
        priority_skills=[...],
        next_steps="..."
    ),
    learning_path=LearningPath(
        title="...",
        milestones=[...],
        total_hours=120,
        estimated_weeks=12
    )
)
```

---

## 🔮 Future Enhancements (Post-MVP)

### Phase 2: User Management
- User authentication & profiles
- Resume history & tracking
- Saved job applications
- Progress monitoring

### Phase 3: Database Integration
- PostgreSQL for persistence
- User data management
- Analytics dashboard
- Historical comparisons

### Phase 4: Advanced Features
- Resume optimization suggestions
- Interview preparation module
- Real-time skill market analysis
- Competitive benchmarking

### Phase 5: Deployment
- REST API for backend
- Next.js frontend
- Cloud hosting (AWS/GCP)
- Mobile app version

---

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# With coverage
python -m pytest --cov=src tests/
```

---

## 📝 Example Workflow

```python
from src.pipeline import run_pipeline
from src.config import PipelineConfig

# Configure
config = PipelineConfig(enable_feedback_generation=True)

# Run
result = run_pipeline("resume.pdf", "job_desc.txt", config)

# Get metrics
print(f"Match Score: {result.matching_result.overall_score}%")
print(f"Top Match: {result.matching_result.matched_skills[0]}")

# Get recommendations
print(result.feedback_result.recommendations)

# Get learning path
for milestone in result.learning_path.milestones:
    print(f"{milestone.title} ({milestone.estimated_hours}h)")
```

---

## 🔐 Environment Variables

```env
# LLM Configuration (choose one provider)
OPENAI_API_KEY=sk_...
GROQ_API_KEY=gr_...
GEMINI_API_KEY=AIza...

# Optional: Model preferences
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000
```

---

## 📄 Dependencies

- **PyMuPDF** (fitz) - PDF parsing
- **spaCy** - NLP pipeline
- **NLTK** - Text processing
- **Sentence Transformers** - Embeddings
- **NumPy** - Numerical operations
- **OpenAI / Groq** - LLM API clients
- **python-dotenv** - Environment variables

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional embedding models
- Enhanced abbreviation dictionary
- Specialized resume templates
- Performance optimization
- Extended test coverage

---

## 📧 Support

For issues, questions, or suggestions, please open a GitHub issue or contact the development team.

---

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ for job seekers and career developers.**
