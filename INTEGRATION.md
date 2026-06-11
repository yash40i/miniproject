# Resume-Insight AI - Full Stack Integration Guide

## 🎯 Project Overview

Resume-Insight AI is a full-stack application for semantic resume analysis and personalized learning path generation. The system consists of:

- **Backend**: Python FastAPI server with ML pipeline
- **Frontend**: Next.js React application
- **ML Pipeline**: PyMuPDF, spaCy, Sentence Transformers, LLM integration

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend (3000)                 │
│  ├─ Resume Upload Form                                     │
│  ├─ Results Dashboard (Matching Scores, Skills)            │
│  └─ Learning Path Viewer (Milestones, Resources)           │
└──────────────┬──────────────────────────────────────────────┘
               │ HTTP/REST
               ↓
┌──────────────────────────────────────────────────────────────┐
│              FastAPI Backend (8000)                          │
│  ├─ POST /api/analyze - Resume upload & analysis           │
│  ├─ GET /api/results/{id} - Retrieve results               │
│  ├─ DELETE /api/results/{id} - Clean up                    │
│  └─ GET /api/stats - Statistics                            │
└──────────────┬──────────────────────────────────────────────┘
               │
               ↓
┌──────────────────────────────────────────────────────────────┐
│                  ML Pipeline (Python)                        │
│  ├─ PDF Parser (PyMuPDF)                                   │
│  ├─ Text Cleaner (spaCy, NLTK)                             │
│  ├─ Embeddings (Sentence Transformers)                     │
│  ├─ Semantic Matcher (cosine similarity)                   │
│  ├─ LLM Feedback (OpenAI/Groq)                             │
│  └─ Learning Path Generator                                 │
└──────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start (Development)

### Prerequisites
- Python 3.9+
- Node.js 18+
- pip and npm

### Option 1: Manual Setup (Recommended for Development)

#### 1. Backend Setup

```bash
cd res_project

# Create and activate virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install packages directly:
pip install fastapi uvicorn python-multipart
pip install PyMuPDF spacy nltk sentence-transformers torch scikit-learn
pip install pydantic openai groq python-dotenv

# Download spaCy model
python -m spacy download en_core_web_sm

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

#### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local
# Edit .env.local if needed (default: http://localhost:8000)
```

#### 3. Run Both Services

**Terminal 1 - Backend:**
```bash
cd res_project
source venv/Scripts/activate  # Windows: venv\Scripts\activate
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd res_project/frontend
npm run dev
```

Access the app at: **http://localhost:3000**

---

### Option 2: Docker Setup (Production-like)

#### Prerequisites
- Docker and Docker Compose installed

#### Steps

```bash
cd res_project

# Create .env file for backend API keys (optional)
cp .env.example .env
# Edit .env and add your API keys if desired

# Build and start services
docker-compose up --build

# For development with auto-reload:
docker-compose up
```

Access the app at: **http://localhost:3000**

Backend API docs: **http://localhost:8000/docs**

---

## 📁 Project Structure

```
res_project/
├── src/                           # Python pipeline modules
│   ├── config/
│   │   └── config.py             # Configuration management
│   ├── pipeline/
│   │   ├── pdf_parser.py         # PDF extraction
│   │   ├── text_cleaner.py       # Text preprocessing
│   │   ├── embeddings.py         # Semantic vectors
│   │   ├── semantic_matcher.py   # Skill matching
│   │   ├── llm_feedback.py       # LLM integration
│   │   ├── learning_path.py      # Learning roadmap generation
│   │   └── pipeline.py           # Main orchestrator
│   └── utils/
│       └── helpers.py            # Utility functions
│
├── backend/
│   └── main.py                   # FastAPI application
│
├── frontend/                      # Next.js application
│   ├── app/
│   │   ├── page.tsx              # Homepage
│   │   ├── results/[id]/page.tsx # Results page
│   │   ├── layout.tsx            # Root layout
│   │   ├── globals.css           # Tailwind styles
│   │   └── providers.tsx         # Context providers
│   ├── lib/
│   │   ├── api.ts                # API client
│   │   └── store.ts              # Zustand stores
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   └── README.md
│
├── examples/
│   ├── test_pipeline_demo.py
│   ├── sample_resume.txt
│   └── sample_job_description.txt
│
├── venv/                          # Python virtual environment
├── Dockerfile.backend             # Backend container config
├── docker-compose.yml             # Multi-container orchestration
├── .env.example                   # Environment template
└── README.md                      # Main documentation
```

---

## 🔧 Configuration

### Backend (FastAPI)

**File**: `backend/main.py`

Key configuration:
- Port: `8000`
- CORS: Enabled for all origins (restrict in production)
- Background tasks: Async analysis processing
- In-memory storage: Replace with database for production

### Frontend (Next.js)

**File**: `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, change to your deployed API URL.

### Environment Variables

**Backend (`backend/` or `.env`):**
```env
OPENAI_API_KEY=your_key          # Optional - for LLM feedback
GROQ_API_KEY=your_key            # Optional - for LLM feedback
```

---

## 🎯 API Endpoints

### Health & Info

```bash
GET /health
# Response: { "status": "healthy", "service": "Resume-Insight AI API" }

GET /
# Response: Service info and endpoint documentation

GET /api/stats
# Response: { "total_analyses": 5, "completed": 3, "processing": 1, "failed": 1 }
```

### Analysis

```bash
POST /api/analyze
Content-Type: multipart/form-data

Request:
- file: Resume PDF file
- job_description: Job description text

Response:
{
  "analysis_id": "uuid-string",
  "status": "processing",
  "message": "Analysis started..."
}
```

### Results

```bash
GET /api/results/{analysis_id}

Response:
{
  "analysis_id": "uuid-string",
  "status": "completed",
  "matching_result": {
    "overall_score": 75.5,
    "matched_percentage": 41.7,
    "matched_skills": [
      {
        "resume_skill": "Python",
        "job_skill": "Python",
        "similarity_score": 0.99,
        "match_strength": "high"
      }
    ],
    "missing_skills": ["Kubernetes", "Docker", "AWS"]
  },
  "feedback": { ... },
  "learning_path": { ... }
}
```

---

## 🧪 Testing

### Test the Backend

```bash
# Run the test script
python examples/test_pipeline_demo.py

# Expected output:
# Overall match score: ~70.6%
# Matched skills: 10
# Missing skills: 14
```

### Test the Frontend

```bash
cd frontend

# Run tests
npm test

# Build for production
npm run build

# Start production server
npm run start
```

---

## 🚀 Deployment

### Docker Deployment

```bash
# Build images
docker build -f Dockerfile.backend -t resume-insight-backend .
docker build -f frontend/Dockerfile -t resume-insight-frontend ./frontend

# Run containers
docker run -p 8000:8000 resume-insight-backend
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://backend:8000 resume-insight-frontend
```

### Production Considerations

1. **Database**: Replace in-memory storage with PostgreSQL
2. **API Keys**: Use secure secret management (AWS Secrets, HashiCorp Vault)
3. **File Storage**: Use cloud storage (S3, GCS) for resume files
4. **Caching**: Add Redis for result caching
5. **Authentication**: Implement user auth with JWT or OAuth
6. **Rate Limiting**: Add rate limiting to API endpoints
7. **Monitoring**: Set up logging and monitoring (CloudWatch, DataDog)
8. **CDN**: Serve frontend assets from CDN
9. **CORS**: Restrict to specific domains
10. **HTTPS**: Enable SSL/TLS certificates

---

## 📚 Key Technologies

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend | Python | 3.9+ |
| API Framework | FastAPI | 0.100+ |
| Server | Uvicorn | 0.24+ |
| PDF Parsing | PyMuPDF | 1.27.2+ |
| NLP | spaCy | 3.8+ |
| Embeddings | Sentence-Transformers | 5.5+ |
| Deep Learning | PyTorch | 2.1+ |
| Frontend | Next.js | 15.1+ |
| UI Framework | React | 18.2+ |
| Styling | Tailwind CSS | 3.4+ |
| State Management | Zustand | 4.4+ |
| HTTP Client | Axios | 1.6+ |
| Notifications | React Toastify | 10.0+ |

---

## 🛠️ Development Workflow

### Adding Features

1. **Backend**: Add new pipeline stage in `src/pipeline/`
2. **API**: Add endpoint in `backend/main.py`
3. **Frontend**: Add page or component in `frontend/app/`
4. **Test**: Run both the test suite and manual testing

### Code Organization

- **Pipeline modules**: Isolated, testable, single responsibility
- **API handlers**: Thin wrappers around pipeline
- **Frontend components**: Reusable, typed, with hooks
- **Utilities**: Shared helpers in `src/utils/`

---

## 📖 Usage Example

### 1. Upload Resume

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@path/to/resume.pdf" \
  -F "job_description=Senior ML Engineer..."
```

### 2. Poll for Results

```bash
curl http://localhost:8000/api/results/{analysis_id}
```

### 3. View in Browser

Navigate to `http://localhost:3000/results/{analysis_id}`

---

## 🐛 Troubleshooting

### Backend Issues

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `lsof -i :8000` and kill process or use different port |
| Module not found | Ensure virtual environment is activated and packages installed |
| PDF parsing fails | Check file is valid PDF; ensure PyMuPDF installed |
| API key errors | Set OPENAI_API_KEY or GROQ_API_KEY in `.env` |

### Frontend Issues

| Issue | Solution |
|-------|----------|
| Can't connect to backend | Check backend is running; verify NEXT_PUBLIC_API_URL |
| Build errors | Delete `.next` folder; reinstall node_modules |
| Port 3000 in use | Use `npm run dev -- -p 3001` for different port |

### Docker Issues

| Issue | Solution |
|-------|----------|
| Container won't start | Check logs: `docker-compose logs service-name` |
| Port conflicts | Modify port mappings in `docker-compose.yml` |
| Volume mount issues | Ensure paths are absolute; check permissions |

---

## 📞 Support

- Check the main [README.md](README.md)
- Review FastAPI docs at `http://localhost:8000/docs`
- Check frontend [README.md](frontend/README.md)
- Review code comments and docstrings

---

## ✅ Checklist for Production Deployment

- [ ] Environment variables configured
- [ ] Database integrated (PostgreSQL)
- [ ] File storage configured (S3/GCS)
- [ ] Authentication implemented
- [ ] Rate limiting enabled
- [ ] Error logging configured
- [ ] CORS properly restricted
- [ ] HTTPS enabled
- [ ] API documentation updated
- [ ] Frontend built for production
- [ ] Load testing completed
- [ ] Security audit done

---

## 📝 License

MIT License - See LICENSE file

