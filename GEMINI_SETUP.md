# 🔧 Google Gemini API Setup Guide

## ⚠️ Important Security Note

**NEVER commit API keys to version control!** Always use environment variables (`.env` files).

---

## 📋 Step 1: Get Your Gemini API Key

### Option A: Free Gemini API (Recommended for Development)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key (starts with `AIzaSyD...`)

### Option B: Paid Gemini API (Google Cloud Console)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Generative AI API
4. Create an API key under "Credentials"

**Pricing:** Gemini 1.5 Flash is very affordable (~$0.075 per 1M input tokens, ~$0.30 per 1M output tokens)

---

## 🔐 Step 2: Store API Key Securely

### Option A: Environment Variable (.env file)

1. **Create `.env` file** in project root:
```bash
# .env file - DO NOT COMMIT THIS
GEMINI_API_KEY=AIzaSyD...your_actual_key_here...
```

2. **Add to `.gitignore`** (already done):
```gitignore
.env
.env.local
*.key
```

3. **.env is auto-loaded** by `python-dotenv` in the config module

### Option B: System Environment Variable

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY = "AIzaSyD...your_key..."
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=AIzaSyD...your_key...
```

**Mac/Linux:**
```bash
export GEMINI_API_KEY="AIzaSyD...your_key..."
```

---

## 💻 Step 3: Configure Resume-Insight AI to Use Gemini

### Option A: Use Environment Variable (Recommended)

1. Set the `GEMINI_API_KEY` environment variable (from Step 2)
2. Create/update `.env` file:
```
GEMINI_API_KEY=AIzaSyD...your_key...
LLM_PROVIDER=gemini
```

3. The system automatically loads these on startup

### Option B: Set in Code (Not Recommended)

```python
from src.config.config import LLMConfig, PipelineConfig

# Direct configuration
llm_config = LLMConfig(
    provider="gemini",
    model="gemini-1.5-flash",  # or "gemini-1.5-pro"
    api_key="AIzaSyD...your_key...",
    temperature=0.7,
    max_tokens=1000
)

pipeline_config = PipelineConfig(llm_config=llm_config)
```

---

## 📊 Gemini Model Options

### Available Models

| Model | Speed | Cost | Use Case |
|-------|-------|------|----------|
| **gemini-1.5-flash** | ⚡ Fast | 💰 Cheap | Quick feedback, MVP |
| **gemini-1.5-pro** | 🐢 Slower | 💵 More | Complex analysis, high quality |

### Default Configuration

```python
# Current default in config.py
LLMConfig(
    provider="gemini",
    model="gemini-1.5-flash",  # Fast and economical
    temperature=0.7,           # Creative but focused
    max_tokens=1000            # Sufficient for feedback
)
```

### Switching Models

Update in code:
```python
llm_config = LLMConfig(
    provider="gemini",
    model="gemini-1.5-pro",  # Switch to pro model
    api_key=api_key
)
```

Or in `.env`:
```
# Not configurable via .env currently, requires code change
```

---

## 🚀 Step 4: Test Gemini Integration

### Test 1: Direct API Call

```python
from src.config.config import LLMConfig
from src.pipeline.llm_feedback import LLMFeedbackGenerator

# Initialize with Gemini
config = LLMConfig(
    provider="gemini",
    model="gemini-1.5-flash",
    api_key="your_api_key_here"
)

generator = LLMFeedbackGenerator(config)

# Test with a simple prompt
response = generator._call_llm("What is Python?")
print(response)
```

### Test 2: Full Feedback Generation

```python
from src.pipeline.semantic_matcher import MatchingResult, SkillMatch
from src.pipeline.llm_feedback import generate_feedback
from src.config.config import LLMConfig

# Create sample matching result
sample_match = MatchingResult(
    overall_score=75.0,
    matched_percentage=75.0,
    matched_skills=[
        SkillMatch("Python", "Python", 0.99, "perfect"),
    ],
    missing_skills=["AWS", "Docker", "Kubernetes"],
    unmatched_job_skills=["AWS", "Docker"]
)

# Generate feedback with Gemini
config = LLMConfig(provider="gemini", model="gemini-1.5-flash")
feedback = generate_feedback(
    matching_result=sample_match,
    resume_text="Python developer with 5 years experience",
    job_description="Senior Python Engineer with AWS experience",
    config=config
)

print(feedback)
```

### Test 3: Via API Endpoint

```bash
# Make sure backend is running
# Then call the analyze endpoint which uses LLMFeedbackGenerator

curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Python developer",
    "job_description": "Senior Python role"
  }'
```

---

## 📚 Available Gemini Models Reference

### As of June 2024

```
// Latest and Recommended
gemini-1.5-pro        // Best quality, good speed, higher cost
gemini-1.5-flash      // Fast, good quality, cheap (RECOMMENDED)

// Legacy (still available)
gemini-1.0-pro        // Older pro model
gemini-pro-vision     // Vision capabilities
```

---

## 🐛 Troubleshooting

### Error: "GEMINI_API_KEY not found"

**Problem:** API key not set correctly
```
Error: LLM API key not found. Set GEMINI_API_KEY environment variable.
```

**Solution:**
1. Check `.env` file exists in project root
2. Verify key starts with `AIzaSyD...`
3. Restart your terminal/IDE
4. Test with:
   ```python
   import os
   print(os.getenv("GEMINI_API_KEY"))  # Should print your key
   ```

### Error: "API Key not valid"

**Problem:** Invalid or expired API key
```
Error: API key invalid
```

**Solution:**
1. Generate new key at [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Update `.env` file
3. Verify billing is enabled (optional, free tier available)

### Error: "import google.generativeai failed"

**Problem:** Library not installed
```
ModuleNotFoundError: No module named 'google'
```

**Solution:**
```bash
pip install google-generativeai
# Or install all dependencies
pip install -r requirements.txt
```

### Slow Responses

**Problem:** Gemini API slow
**Solution:** 
- Use `gemini-1.5-flash` instead of `gemini-1.5-pro`
- Reduce `max_tokens` in config
- Check internet connection

### Rate Limiting

**Problem:** "429 Too Many Requests"
**Solution:**
- Free tier has rate limits: ~60 requests per minute
- Upgrade to paid, or add retry logic

---

## 💰 Cost Comparison (as of June 2024)

### Resume-Insight Typical Usage

Assuming 1 resume analysis = ~500 input tokens + ~200 output tokens:

| Provider | Per Analysis | 100 Analyses | Notes |
|----------|-------------|--------------|-------|
| **Groq** | FREE | FREE | Fastest, unlimited* |
| **Gemini Flash** | ~$0.00004 | ~$0.004 | Very cheap |
| **Gemini Pro** | ~$0.0003 | ~$0.03 | Better quality |
| **OpenAI GPT-3.5** | ~$0.0008 | ~$0.08 | Reliable |
| **OpenAI GPT-4** | ~$0.03 | ~$3.00 | Premium |

*Groq has generous free tier, essentially unlimited for development

---

## 🔄 Switching Between Providers

### To Switch from Groq to Gemini

1. **Update `.env`:**
```
# Old
GROQ_API_KEY=gsk_...

# New
GEMINI_API_KEY=AIzaSyD...
```

2. **Or in code:**
```python
from src.config.config import LLMConfig

# Old: Groq
groq_config = LLMConfig(provider="groq", model="llama-3.1-8b-instant")

# New: Gemini
gemini_config = LLMConfig(provider="gemini", model="gemini-1.5-flash")
```

3. **No code changes needed** - system auto-switches based on config

---

## 📖 System Architecture

```
┌─────────────────────────────────────────┐
│    Resume-Insight AI Frontend/API       │
└────────────────┬────────────────────────┘
                 │
         ┌───────▼────────┐
         │ LLMConfig      │
         │ (config.py)    │
         └───────┬────────┘
                 │
      ┌──────────┼──────────┐
      │          │          │
   Groq      Gemini     OpenAI
   ────      ──────     ──────
   (Free)    ($$$)      ($$$$)
```

### How It Works

1. **Config Module** loads API key from environment
2. **LLMFeedbackGenerator** initializes correct client
3. **Pipeline** calls LLM for feedback/recommendations
4. **API Endpoints** return results to frontend

---

## ✅ Verification Checklist

- [ ] Created `.env` file with `GEMINI_API_KEY=AIzaSyD...`
- [ ] Added `.env` to `.gitignore`
- [ ] Set `LLM_PROVIDER=gemini` in `.env`
- [ ] Installed `google-generativeai` (`pip install -r requirements.txt`)
- [ ] Tested with `python -c "import google.generativeai"`
- [ ] Called test endpoint: `curl http://localhost:8000/api/analyze`
- [ ] Verified response includes LLM-generated feedback

---

## 🎯 Next Steps

1. **Use Gemini** in your resume analysis:
   ```bash
   # API will automatically use Gemini based on config
   curl -X POST "http://localhost:8000/api/analyze" \
     -H "Content-Type: application/json" \
     -d '{"resume_text": "...", "job_description": "..."}'
   ```

2. **Monitor costs** on [Google AI Studio Dashboard](https://makersuite.google.com)

3. **Optimize prompts** for best results with Gemini

4. **Scale as needed** - Gemini can handle 1M requests/month at free tier

---

## 📞 Support

- **Google Generative AI Docs:** https://ai.google.dev
- **Gemini API Guide:** https://ai.google.dev/tutorials
- **Pricing:** https://ai.google.dev/pricing
- **Free API Key:** https://makersuite.google.com/app/apikey
