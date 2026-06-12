# 🌐 Browser Verification Guide - Dynamic Learning Path

## ✅ Servers Running

- **Frontend**: http://localhost:3000 ✅
- **Backend API**: http://localhost:8000 ✅
- **API Documentation**: http://localhost:8000/docs (when fully loaded)

---

## 📋 Step-by-Step Verification

### Step 1: Access the Main Application
Open your browser and go to:
```
http://localhost:3000
```

You'll see the Resume-Insight AI interface with:
- Resume upload area
- Job description input
- "Analyze Resume" button

### Step 2: Test the API Directly (Without Frontend)

You can test the new dynamic learning path endpoints using curl or Postman.

#### Option A: Using the API Documentation UI
1. Open: http://localhost:8000/docs
2. Scroll to find these new endpoints:
   - `POST /api/learning-path/adaptive`
   - `POST /api/learning-path/{analysis_id}/milestone-progress`
   - `GET /api/learning-path/{analysis_id}/next-actions`
   - `GET /api/learning-path/{analysis_id}/personalized-resources`
   - `GET /api/learning-path/{analysis_id}/success-criteria`

3. Click "Try it out" to test each endpoint

#### Option B: Using Curl Commands

##### 1. First, analyze a resume to get an analysis_id
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"resume_text": "Python developer with 5 years experience", "job_description": "Senior Python Developer"}'
```

Expected response:
```json
{
  "analysis_id": "uuid-here",
  "matched_skills": [...],
  "missing_skills": [...],
  "semantic_match_percentage": 85
}
```

##### 2. Generate an Adaptive Learning Path
```bash
curl -X POST "http://localhost:8000/api/learning-path/adaptive" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": "YOUR_ANALYSIS_ID_HERE",
    "user_profile": {
      "experience_level": "intermediate",
      "learning_style": "hands-on",
      "availability_hours_per_week": 15,
      "preferred_resource_types": ["Course", "Practice"],
      "budget": "free"
    }
  }'
```

Expected response:
```json
{
  "analysis_id": "uuid",
  "learning_path": {
    "title": "Personalized Learning Path",
    "adaptivity_score": 0.88,
    "overall_progress": 0,
    "total_hours": 150,
    "milestones": [
      {
        "id": 1,
        "title": "Master Python",
        "difficulty": "intermediate",
        "success_criteria": ["Write 10+ scripts", ...],
        "projects": [...],
        "resources": [...],
        "progress_percentage": 0
      }
    ]
  }
}
```

##### 3. Track Progress on a Milestone
```bash
curl -X POST "http://localhost:8000/api/learning-path/YOUR_ANALYSIS_ID/milestone-progress" \
  -H "Content-Type: application/json" \
  -d '{
    "milestone_id": 1,
    "progress_percentage": 50,
    "is_completed": false
  }'
```

##### 4. Get Next Action Recommendations
```bash
curl -X GET "http://localhost:8000/api/learning-path/YOUR_ANALYSIS_ID/next-actions?current_milestone_id=1"
```

Expected response:
```json
{
  "next_actions": [
    {
      "action": "Complete Python fundamentals course",
      "reason": "Foundation for all Python-related milestones",
      "estimated_hours": 20,
      "priority": "high"
    }
  ]
}
```

##### 5. Get Personalized Resources
```bash
curl -X GET "http://localhost:8000/api/learning-path/YOUR_ANALYSIS_ID/personalized-resources?skill_name=Python&difficulty=intermediate&learning_style=hands-on"
```

Expected response:
```json
{
  "resources": [
    {
      "title": "Real Python",
      "url": "https://realpython.com",
      "type": "Tutorial",
      "free": true,
      "match_percentage": 95
    }
  ]
}
```

---

## 🧪 Complete Workflow Test

Here's a complete workflow to test everything:

### 1. Upload and Analyze
Go to http://localhost:3000 and:
1. Click the upload area to select a PDF resume
2. Paste a job description
3. Click "Analyze Resume"

### 2. View Results
The system will show:
- Semantic matching percentage
- Matched skills (in green)
- Missing skills (gaps to fill)

### 3. Request Adaptive Learning Path (via API)
Use the curl command from Step 2 above with the analysis_id returned

### 4. Track Progress (via API)
Update your progress on milestones as you learn

### 5. Get Recommendations (via API)
Get AI-powered next steps based on current progress

---

## 📊 Sample Test Data

If you don't have real files, use this sample data:

### Sample Resume
```
JOHN DOE
john@example.com | GitHub: johndoe

EXPERIENCE
Senior Python Developer (2020-2024) - Tech Corp
- Built scalable web applications using FastAPI
- Implemented machine learning pipelines
- Led team of 3 developers

Python Developer (2018-2020) - StartupXYZ
- Developed REST APIs
- Database optimization
- Code reviews and mentoring

SKILLS
- Python (Advanced)
- FastAPI, Django
- PostgreSQL, MongoDB
- Docker, Kubernetes
- AWS
- Git, CI/CD
- Machine Learning basics
```

### Sample Job Description
```
SENIOR PYTHON DEVELOPER - REMOTE

We're looking for an experienced Python developer to:
- Design and build scalable backend services
- Work with AWS and cloud technologies
- Implement advanced ML features
- Lead architecture decisions
- Mentor junior developers

Required:
- 5+ years Python experience
- Production experience with FastAPI or Django
- AWS or cloud platform experience
- Database design and optimization
- System design and architecture

Nice to have:
- Machine Learning experience
- Kubernetes and container orchestration
- Microservices architecture
- GraphQL
```

---

## 🔍 Key Features to Verify

When you generate an adaptive learning path, verify these features:

### ✅ Adaptivity Score
Look for the `adaptivity_score` field (0-1):
- 0.8+ = Excellent fit
- 0.6-0.8 = Good fit
- 0.4-0.6 = Moderate fit
- <0.4 = Needs adjustment

### ✅ Personalized Milestones
Check that milestones include:
- [ ] Success criteria (measurable outcomes)
- [ ] Projects (hands-on suggestions)
- [ ] Resources (filtered by preference)
- [ ] Difficulty level (adjusted to user)
- [ ] Time estimates (based on availability)

### ✅ Resource Filtering
Verify resources are:
- [ ] Ranked by match score
- [ ] Filtered by budget (free/paid)
- [ ] Filtered by learning style (visual/hands-on)
- [ ] Filtered by resource type

### ✅ Progress Tracking
Check that progress can be:
- [ ] Updated per milestone (0-100%)
- [ ] Calculated overall (0-100%)
- [ ] Marked as completed
- [ ] Tracked over time

### ✅ AI Recommendations
Verify next actions include:
- [ ] Specific recommendations
- [ ] Reason for recommendation
- [ ] Time estimates
- [ ] Priority level

---

## 🛠️ Troubleshooting

### Backend Not Responding
```bash
# Check if backend is running
curl http://localhost:8000/docs

# If not, restart it:
# Kill the backend terminal (Ctrl+C)
# Run: python -m uvicorn backend.main:app --reload --port 8000
```

### Frontend Not Loading
```bash
# Check if frontend is running
# Look at the terminal running "npm run dev"

# If not, restart it:
# Kill the frontend terminal (Ctrl+C)
# Run: cd frontend && npm run dev
```

### API Returns Error
Common issues:
1. **Missing analysis_id**: Get one by calling /api/analyze first
2. **Invalid user_profile**: Check field names and value formats
3. **CORS issues**: Should be handled automatically

---

## 📚 Documentation References

For more details, see:
- **[DYNAMIC_LEARNING_PATH.md](../DYNAMIC_LEARNING_PATH.md)** - Complete API reference
- **[DYNAMIC_LEARNING_PATH_QUICKSTART.md](../DYNAMIC_LEARNING_PATH_QUICKSTART.md)** - Quick start guide
- **[DYNAMIC_LEARNING_PATH_README.md](../DYNAMIC_LEARNING_PATH_README.md)** - Executive summary

---

## 🎯 What You're Testing

The dynamic learning path system provides:

1. **Personalization**
   - Adapts to user experience level
   - Respects learning style preferences
   - Considers time availability
   - Honors budget constraints

2. **Adaptivity**
   - Scores how well the path fits the user (0-1)
   - Adjusts difficulty dynamically
   - Ranks resources by preference

3. **Progress**
   - Tracks milestone completion
   - Calculates overall progress
   - Stores historical data

4. **Guidance**
   - AI-powered recommendations
   - Context-aware next actions
   - Measurable success criteria

---

## ✨ Example Response Walkthrough

Here's what a complete adaptive learning path response looks like:

```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "learning_path": {
    "title": "Personalized Learning Path - 3 Priority Skills",
    "description": "Dynamic path tailored for intermediate developer...",
    "total_hours": 150,
    "estimated_weeks": 10,
    "overall_progress": 0,
    "adaptivity_score": 0.88,
    "recommendation_engine": "llm",
    "milestones": [
      {
        "id": 1,
        "title": "Master Python Advanced Concepts",
        "description": "Deep dive into Python...",
        "skills": ["Python"],
        "estimated_hours": 50,
        "difficulty": "intermediate",
        "start_date": "2024-06-12",
        "target_completion": "2024-07-24",
        "success_criteria": [
          "Write 10+ advanced Python scripts",
          "Understand decorators and metaclasses",
          "Implement design patterns",
          "Optimize code performance"
        ],
        "projects": [
          {
            "title": "Build an Advanced CLI Framework",
            "description": "Create a production-ready CLI tool",
            "skills": ["Python", "Architecture"],
            "difficulty": "intermediate"
          }
        ],
        "resources": [
          {
            "title": "Real Python - Advanced Python",
            "url": "https://realpython.com/courses/",
            "type": "Course",
            "hours": 30,
            "free": false,
            "match_score": 0.95
          },
          {
            "title": "Python Design Patterns",
            "url": "https://refactoring.guru/design-patterns/python",
            "type": "Tutorial",
            "hours": 20,
            "free": true,
            "match_score": 0.92
          }
        ],
        "progress_percentage": 0,
        "is_completed": false
      }
    ]
  }
}
```

---

## 🎉 You're All Set!

Your dynamic learning path system is now:
- ✅ Running on localhost:3000 (frontend)
- ✅ Running on localhost:8000 (backend)
- ✅ Ready for comprehensive testing
- ✅ Fully documented and tested

Start by uploading a resume and job description, then use the API endpoints to test the dynamic personalization features!
