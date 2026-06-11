# Groq Setup Guide - FREE LLM

## Quick Start (5 minutes)

### Step 1: Get Groq API Key (FREE)
1. Go to https://console.groq.com
2. Sign up with email/Google/GitHub (completely FREE)
3. Click "API Keys" in the sidebar
4. Create a new API key
5. Copy it to clipboard

### Step 2: Add to .env File
Open `.env` file in your project root and paste:

```env
GROQ_API_KEY=gsk_paste_your_key_here
```

That's it! The project is configured to use Groq by default.

---

## Verify Installation

### Install Groq Package
If not already installed:
```bash
pip install groq>=0.4.0
```

### Check Your Setup
```bash
# Check if .env has your Groq key
grep GROQ_API_KEY .env

# Verify the config
python -c "from src.config import PipelineConfig; config = PipelineConfig(); print(f'Provider: {config.llm_config.provider}'); print(f'Model: {config.llm_config.model}')"
```

---

## Available Groq Models (All FREE)

| Model | Speed | Quality | Context | Best For |
|-------|-------|---------|---------|----------|
| **mixtral-8x7b-32768** | ⚡⚡⚡ Fastest | ⭐⭐⭐⭐ | 32k | Gap analysis, recommendations |
| **llama2-70b-4096** | ⚡⚡ Medium | ⭐⭐⭐⭐⭐ Best | 4k | Detailed feedback |
| **gemma-7b-it** | ⚡⚡⚡ Fastest | ⭐⭐⭐ | 8k | Quick analysis |

**Current Default:** `mixtral-8x7b-32768` (recommended)

---

## Usage in Code

Once your `.env` is set, the system automatically uses Groq:

```python
from src.pipeline import ResumePipeline

pipeline = ResumePipeline()
result = pipeline.analyze_resume(
    resume_path="resume.pdf",
    job_description="job desc text",
    generate_feedback=True,      # Uses Groq API
    generate_learning_path=True
)

print(f"Gap Analysis: {result.feedback_result.gap_analysis}")
print(f"Priority Skills: {result.feedback_result.priority_skills}")
```

---

## Testing the Setup

### Test Groq Connection
```bash
python -c "
from groq import Groq
import os

api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    print('❌ GROQ_API_KEY not set in .env')
else:
    client = Groq(api_key=api_key)
    print('✅ Groq API connection successful!')
"
```

### Full Pipeline Test
```bash
# Upload a resume and test the full workflow
python -c "
from src.pipeline import ResumePipeline

pipeline = ResumePipeline()
result = pipeline.analyze_resume(
    resume_path='examples/sample_resume.pdf',
    job_description='Sample job description'
)
print('✅ Pipeline works!')
print(f'Match Score: {result.matching_result.overall_score}%')
"
```

---

## Free Tier Limits

Groq's free tier includes:
- ✅ Unlimited API calls (fair use)
- ✅ Up to 30 requests/minute per IP
- ✅ 32k token context window
- ✅ Multiple models available
- ✅ No credit card required

Perfect for development and testing!

---

## Switching LLM Providers (if needed)

### Switch to OpenAI (Paid)
```env
OPENAI_API_KEY=sk_your_key_here
```
Then update config:
```python
LLMConfig(provider="openai", model="gpt-3.5-turbo")
```

### Switch to Gemini (Paid)
```env
GEMINI_API_KEY=AIza_your_key_here
```

---

## Troubleshooting

### Error: "GROQ_API_KEY not found"
- Make sure `.env` file exists in project root
- Check key is correctly formatted: `GROQ_API_KEY=gsk_...`
- Verify no extra spaces: `GROQ_API_KEY = value` ❌ (remove spaces)

### Error: "Install groq: pip install groq"
```bash
pip install groq>=0.4.0
```

### Rate limit exceeded
- Free tier: 30 requests/minute per IP
- Wait a minute and retry, or use batch processing

### Poor quality feedback
- Try switching to `llama2-70b-4096` model (more accurate)
- Update in `.env`: `LLM_MODEL=llama2-70b-4096`

---

## Documentation

- [Groq Console](https://console.groq.com)
- [Groq API Docs](https://console.groq.com/docs)
- [Available Models](https://console.groq.com/docs/models)

---

**Status: ✅ Ready to use!** No cost, no credit card required. Just grab a free API key and start analyzing resumes.
