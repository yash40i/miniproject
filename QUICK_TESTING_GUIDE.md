# 🧪 QUICK TESTING GUIDE

## ⚡ 5-Minute Test Everything

### Prerequisites
```bash
# Both servers should be running:
# Terminal 1: Backend
python -m uvicorn backend.main:app --reload --port 8000

# Terminal 2: Frontend  
cd frontend && npm run dev
```

---

## 🎯 Test 1: Gemini API Integration

### Option A: Automated Test (2 minutes)
```bash
# Terminal 3: Test Gemini
python test_gemini_integration.py

# Expected output:
# ============================================================
# 🧪 Testing Gemini API Integration
# ============================================================
# [1] Checking environment setup...
# ❌ GEMINI_API_KEY not found in environment
#    Please set GEMINI_API_KEY environment variable
```

### Option B: Setup Wizard (3 minutes)
```bash
python setup_gemini.py

# Walks you through:
# 1. Check environment
# 2. Check library installation
# 3. Test API connection (if key configured)
```

### Getting Gemini API Key (1 minute)
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (starts with `AIzaSyD...`)
4. Add to `.env` file:
   ```
   GEMINI_API_KEY=AIzaSyD...paste_your_key_here...
   ```
5. Restart terminals
6. Run test again

---

## 🎯 Test 2: Frontend Workflow (5 minutes)

### Step 1: Open Frontend (30 seconds)
```
Visit: http://localhost:3000
```

### Step 2: Upload & Analyze (2 minutes)
1. Click upload area or drag PDF resume
2. Paste sample job description:
   ```
   Senior Python Developer needed.
   Must have: Python, FastAPI, Docker, AWS
   Nice to have: Kubernetes, ML
   ```
3. Click "Analyze Resume"
4. Wait for results (~5 seconds)

### Step 3: View Results (1 minute)
- See "Overview" tab with:
  - Semantic matching score
  - Gap analysis
  - Recommendations
  
- See "Skill Matches" tab with:
  - Green: Matched skills
  - Yellow: Missing skills

### Step 4: Test New Learning Path Form (1.5 minutes)
1. Click "Learning Path" tab
2. Fill form:
   - Experience: Select "Intermediate"
   - Style: Select "Hands-On"
   - Time: Slide to 15 hours/week
   - Budget: Select "Free"
   - Resources: Check "Course" and "Tutorial"
3. Click "Generate Personalized Learning Path"
4. **NEW** Adaptive path displays with:
   - Adaptivity score (0.88 = excellent)
   - Success criteria
   - Project suggestions
   - Filtered resources
   - Progress tracking

---

## 🔍 What to Verify

### Backend
- [ ] `python -m uvicorn backend.main:app --reload` works
- [ ] No errors on startup
- [ ] Listens on port 8000
- [ ] Can handle `/api/analyze` requests

### Frontend
- [ ] `cd frontend && npm run dev` works
- [ ] Loads on http://localhost:3000
- [ ] No TypeScript errors
- [ ] Form submits successfully

### New Features
- [ ] UserProfileForm component displays
- [ ] Form has all 5 input types (level, style, slider, budget, resources)
- [ ] Form submission makes API call
- [ ] Adaptive path displays with score and milestones
- [ ] Success criteria show in each milestone
- [ ] Projects display
- [ ] Resources are ranked and filtered
- [ ] Edit Profile button works

### API Integration
- [ ] `/api/analyze` returns analysis_id
- [ ] `/api/learning-path/adaptive` returns personalized path
- [ ] Adaptivity score is between 0 and 1
- [ ] Milestones have success criteria and projects

---

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check Python is installed
python --version

# Check dependencies
pip list | grep groq  # Should show groq installed

# Try explicit path
python -m uvicorn backend.main:app --reload
```

### Frontend Won't Load
```bash
# Check Node is installed  
node --version

# Install dependencies
npm install

# Start dev server
npm run dev
```

### Form Not Submitting
```bash
# Check backend is running
curl http://localhost:8000/health

# Check API key in .env
echo %GEMINI_API_KEY%  (Windows)
echo $GEMINI_API_KEY   (Mac/Linux)
```

### Gemini API Errors
```bash
# Get new API key
https://makersuite.google.com/app/apikey

# Update .env with new key
GEMINI_API_KEY=AIzaSyD...your_new_key...

# Test key works
python test_gemini_integration.py
```

---

## ✅ Success Criteria

### Test is Successful If:

✅ **Gemini Test**
- Script runs without errors
- Shows "ALL TESTS PASSED" or asks for API key

✅ **Frontend Upload**
- Resume uploads successfully
- Analysis completes in <10 seconds
- Results show on screen

✅ **Learning Profile Form**
- All 5 form inputs display
- Can select options
- Can move slider
- Can toggle resources

✅ **Adaptive Path**
- Path generates in <5 seconds
- Shows adaptivity score (0-1)
- Shows 6+ milestones
- Each milestone has:
  - Title and description
  - Success criteria (✓ items)
  - Projects
  - Resources
  - Progress bar

✅ **API Communication**
- Form submission doesn't error
- Backend logs show request
- Adaptive path data is returned

---

## 📊 Sample Test Data

### Resume
```
JOHN DOE
john@example.com

EXPERIENCE
Senior Python Developer (2020-2024) - Tech Corp
- Built scalable APIs with FastAPI
- Worked with PostgreSQL and MongoDB
- Led team of 3 developers

SKILLS
- Python (Expert)
- FastAPI, Django
- PostgreSQL, MongoDB
- Docker, Git
```

### Job Description
```
SENIOR PYTHON DEVELOPER

Required:
- 5+ years Python experience
- FastAPI or Django
- Database design
- Docker

Nice to have:
- AWS or cloud experience
- Kubernetes
- Machine Learning basics
```

---

## 🎯 Expected Results

### Matching Score
- Should be ~75-85% (several matches but some gaps)

### Recommendations
- Should include AWS, Kubernetes, ML
- Should suggest practical next steps

### Learning Profile Preferences
- Intermediate level (reasonable for 5 years exp)
- Hands-on learning (practical approach)
- 15 hours/week (realistic time)
- Free resources (budget-conscious)

### Adaptive Path
- Should generate in 2-5 seconds
- Score should be 0.75+ (good fit)
- Should have 6-10 milestones
- Milestones should include:
  - AWS Basics
  - Kubernetes
  - ML Fundamentals
  - Advanced Python
  - System Design

---

## 🔄 Full Test Cycle (10 minutes)

```
Time | Task
-----|----------
0:00 | Start servers
1:00 | Open http://localhost:3000
2:00 | Upload resume + job description
3:00 | Click "Analyze Resume"
4:00 | View results (click tabs)
5:00 | Go to "Learning Path" tab
6:00 | Fill learning profile form
7:00 | Click "Generate Path"
8:00 | View adaptive path
9:00 | Check all milestones
10:00| Click "Edit Profile" to regenerate
```

---

## 📞 Getting Help

### If Something Breaks
1. Check server logs
2. Verify backend is running
3. Check `.env` for API keys
4. Restart servers
5. Clear browser cache
6. Check documentation

### Documentation Available
- **Setup:** [GEMINI_SETUP.md](GEMINI_SETUP.md)
- **API:** [DYNAMIC_LEARNING_PATH.md](DYNAMIC_LEARNING_PATH.md)
- **Testing:** [BROWSER_VERIFICATION_GUIDE.md](BROWSER_VERIFICATION_GUIDE.md)
- **Summary:** [IMPLEMENTATION_SUMMARY_COMPLETE.md](IMPLEMENTATION_SUMMARY_COMPLETE.md)

---

## 🎉 You're Ready!

Everything is set up and ready to test.

**Start with:**
1. Both servers running
2. Visit http://localhost:3000
3. Upload a resume
4. Test the new learning profile form!

Enjoy the personalized learning paths! 🚀
