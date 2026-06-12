# OpenAI Setup Guide - For Resume-Insight AI

## Quick Start (5 minutes)

### Step 1: Get OpenAI API Key
1. Go to https://platform.openai.com/api/keys
2. Sign up or log in with your OpenAI account
3. Click "Create new secret key"
4. Copy the API key (save it somewhere safe!)

**Note:** OpenAI API is NOT free. You'll need to:
- Add a payment method to your account
- Start with free trial credits (if available)
- Pay per token used (~$0.15-$2 per 1M input tokens depending on model)

### Step 2: Add to .env File
Open `.env` file in your project root and add/replace:

```env
OPENAI_API_KEY=sk_paste_your_key_here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
```

### Step 3: Restart Backend
The backend will automatically detect the new provider and use OpenAI.

---

## Configuration Options

### Available OpenAI Models

| Model | Speed | Cost | Context | Quality |
|-------|-------|------|---------|---------|
| **gpt-4o** | ⚡⚡ Medium | 💰💰💰 Expensive | 128k | ⭐⭐⭐⭐⭐ Best |
| **gpt-4o-mini** | ⚡⚡⚡ Fast | 💰 Low | 128k | ⭐⭐⭐⭐ Good |
| **gpt-4-turbo** | ⚡⚡ Medium | 💰💰 Medium | 128k | ⭐⭐⭐⭐⭐ Best |
| **gpt-3.5-turbo** | ⚡⚡⚡ Fast | 💰 Low | 16k | ⭐⭐⭐ Good |

**Recommended:** `gpt-4o-mini` (best balance of cost, speed, and quality)

### Update .env File

```env
# Option 1: Fast & Cheap
OPENAI_API_KEY=sk_your_key_here
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo

# Option 2: Balanced (Recommended)
OPENAI_API_KEY=sk_your_key_here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini

# Option 3: Best Quality
OPENAI_API_KEY=sk_your_key_here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
```

---

## How to Switch Between Providers

### Switch to OpenAI
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk_your_key_here
```

### Switch Back to Groq (Free)
```env
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
GROQ_API_KEY=gsk_your_key_here
```

### Switch to Gemini (Free)
```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_key_here
```

---

## Environment Variables Reference

```env
# LLM Provider Selection
LLM_PROVIDER=openai              # Options: openai, groq, gemini
LLM_MODEL=gpt-4o-mini          # Specific model to use

# API Keys (only needed for your chosen provider)
OPENAI_API_KEY=sk_xxx          # Required if LLM_PROVIDER=openai
GROQ_API_KEY=gsk_xxx           # Required if LLM_PROVIDER=groq
GOOGLE_API_KEY=xxx             # Required if LLM_PROVIDER=gemini

# LLM Parameters (optional)
LLM_TEMPERATURE=0.7            # 0.0-2.0, lower = deterministic
LLM_MAX_TOKENS=1000            # Max response length
```

---

## Cost Estimation

### Example Analysis Costs

**Using GPT-4o-mini** (Recommended):
- 1 Resume Analysis: ~$0.001 - $0.003
- 100 Analyses: ~$0.10 - $0.30
- 1000 Analyses: ~$1.00 - $3.00

**Using GPT-4o** (Best Quality):
- 1 Resume Analysis: ~$0.01 - $0.05
- 100 Analyses: ~$1.00 - $5.00
- 1000 Analyses: ~$10 - $50

**Using Groq** (Free):
- Unlimited analyses at no cost

---

## Verify Your Setup

### Check Connection
```bash
python -c "
from src.config.config import PipelineConfig
config = PipelineConfig()
print(f'✓ Provider: {config.llm_config.provider}')
print(f'✓ Model: {config.llm_config.model}')
print(f'✓ API Key: {config.llm_config.api_key[:20]}...')
"
```

### Test API Call
```bash
python -c "
from src.pipeline.llm_feedback import LLMFeedbackGenerator
from src.config.config import DEFAULT_CONFIG

gen = LLMFeedbackGenerator(DEFAULT_CONFIG.llm_config)
response = gen._call_llm('Say \"OpenAI is working!\" in one sentence.')
print(response)
"
```

---

## Troubleshooting

### Error: "LLM API key not found"
**Solution:** Make sure your API key is in `.env` file with the correct name:
```env
OPENAI_API_KEY=sk_your_actual_key_here
```

### Error: "Invalid API key"
**Solution:** 
- Verify your key is correct on https://platform.openai.com/api/keys
- Make sure you have an active payment method
- Try regenerating the key

### High Costs
**Solution:** 
- Use GPT-4o-mini instead of GPT-4o
- Switch to Groq (free alternative)
- Reduce `LLM_MAX_TOKENS` in .env

### Slow Responses
**Solution:**
- Use GPT-3.5-turbo for faster (but slightly lower quality) responses
- Use Groq for instant responses

---

## Cost Monitoring

To monitor your OpenAI usage:
1. Go to https://platform.openai.com/account/billing/overview
2. Check "Usage" section for current month's costs
3. Set usage limits in "Billing → Usage limits" to prevent overspending

---

## Comparison: Groq vs OpenAI

| Feature | Groq | OpenAI |
|---------|------|--------|
| **Cost** | 🟢 FREE | 🔴 Paid |
| **Speed** | 🟢 Instant | 🟡 Fast |
| **Quality** | 🟡 Good | 🟢 Excellent |
| **Best For** | Budget projects | Production apps |
| **Rate Limits** | Generous | Based on plan |

---

## Questions?

- OpenAI Docs: https://platform.openai.com/docs
- API Status: https://status.openai.com
- Pricing: https://openai.com/pricing
