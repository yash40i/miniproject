# 🚀 Gemini API Quick Reference

## ⚡ 30-Second Setup

```bash
# 1. Get API key from: https://makersuite.google.com/app/apikey
# 2. Create .env file in project root with:
GEMINI_API_KEY=AIzaSyD...your_key_here...

# 3. Done! System will use Gemini automatically
```

---

## 📝 .env Configuration

```bash
# Choose your provider (options: openai, groq, gemini)
# Default: groq (FREE!)
# To use Gemini, ensure GEMINI_API_KEY is set:

GEMINI_API_KEY=AIzaSyD...your_key_here...

# Optional: specify provider explicitly
# LLM_PROVIDER=gemini
```

---

## ✅ Verify Gemini Works

### Test 1: Check Environment
```python
import os
print(os.getenv("GEMINI_API_KEY"))  # Should print your key
```

### Test 2: Initialize Config
```python
from src.config.config import LLMConfig

config = LLMConfig(provider="gemini", model="gemini-1.5-flash")
print("Gemini config loaded:", config)
```

### Test 3: Test API Endpoint
```bash
# Start backend: python -m uvicorn backend.main:app --reload
# Then call:
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Python developer with 5 years experience",
    "job_description": "Senior Python Engineer at Google"
  }'
```

Response will include:
```json
{
  "analysis_id": "uuid",
  "matched_percentage": 85,
  "feedback": {
    "gap_analysis": "...",
    "recommendations": [...],
    "priority_skills": [...]
  }
}
```

---

## 📊 Model Comparison

| Feature | Gemini Flash | Gemini Pro | Groq |
|---------|--------------|------------|------|
| Speed | ⚡⚡⚡ Fast | ⚡⚡ Medium | ⚡⚡⚡ Fast |
| Cost | $ Cheap | $$ Medium | FREE |
| Quality | ★★★★ Good | ★★★★★ Best | ★★★★ Good |
| Best For | MVP, Dev | Production | Always |

---

## 🔧 Switch Providers Easily

### Currently Using Groq?
Switch to Gemini:
```python
# Before
config = LLMConfig(provider="groq")

# After
config = LLMConfig(provider="gemini")
```

All endpoints work automatically with either provider!

---

## 💻 Full Integration Example

```python
from src.config.config import LLMConfig, PipelineConfig
from src.pipeline.pipeline import ResumePipeline

# Configure for Gemini
llm_config = LLMConfig(
    provider="gemini",
    model="gemini-1.5-flash",  # Fast and cheap
    temperature=0.7,
    max_tokens=1000
)

pipeline_config = PipelineConfig(llm_config=llm_config)

# Use in pipeline
pipeline = ResumePipeline(pipeline_config)

result = pipeline.run(
    resume_text="Python developer...",
    job_description="Senior Python role..."
)

print(result.feedback.gap_analysis)
```

---

## 🎯 Common Tasks

### Task 1: Analyze Resume with Gemini
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Senior Python dev with 8 years AWS experience",
    "job_description": "Lead Python Engineer role"
  }'
```

### Task 2: Get Dynamic Learning Path
```bash
# First get analysis_id from analyze endpoint
# Then:
curl -X POST "http://localhost:8000/api/learning-path/adaptive" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": "returned-from-analyze",
    "user_profile": {
      "experience_level": "intermediate",
      "learning_style": "hands-on",
      "availability_hours_per_week": 15,
      "budget": "free"
    }
  }'
```

### Task 3: Track Learning Progress
```bash
curl -X POST "http://localhost:8000/api/learning-path/{analysis_id}/milestone-progress" \
  -H "Content-Type: application/json" \
  -d '{
    "milestone_id": 1,
    "progress_percentage": 50,
    "is_completed": false
  }'
```

---

## ⚠️ Security Best Practices

✅ **DO:**
- Keep API keys in `.env` file
- Add `.env` to `.gitignore`
- Use environment variables
- Rotate keys periodically

❌ **DON'T:**
- Commit `.env` to git
- Hardcode API keys in source
- Share keys in messages/emails
- Use same key across projects

---

## 🐛 Quick Troubleshooting

| Error | Fix |
|-------|-----|
| `GEMINI_API_KEY not found` | Check `.env` file exists with correct key |
| `API key invalid` | Regenerate key at [makersuite.google.com](https://makersuite.google.com/app/apikey) |
| `Module not found: google` | Run `pip install google-generativeai` |
| `Rate limited (429)` | Free tier: ~60 req/min. Upgrade or retry |
| `Slow responses` | Use `gemini-1.5-flash` instead of `gemini-1.5-pro` |

---

## 📚 Detailed Documentation

For complete setup guide, see: [GEMINI_SETUP.md](GEMINI_SETUP.md)

For API reference, see: [DYNAMIC_LEARNING_PATH.md](DYNAMIC_LEARNING_PATH.md)

---

## 💡 Pro Tips

1. **Use Flash for MVP** - Fast, cheap, good enough for development
2. **Test with free tier** - Generous limits for testing
3. **Monitor usage** - Check [Google AI Studio](https://makersuite.google.com)
4. **Rotate providers** - Easy to switch between Groq/Gemini/OpenAI
5. **Combine with Groq** - Use Groq for free, Gemini for advanced analysis

---

## 🚀 Ready to Go!

You now have:
- ✅ Gemini API integrated
- ✅ Secure API key management
- ✅ Full LLM feedback generation
- ✅ Dynamic adaptive learning paths
- ✅ Multiple provider support

**Next step:** Get your Gemini API key and test!

See [GEMINI_SETUP.md](GEMINI_SETUP.md) for complete instructions.
