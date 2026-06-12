#!/usr/bin/env python3
"""
Setup Gemini API Configuration
Helps configure the Gemini API key securely
"""

import os
import sys
from pathlib import Path

def setup_gemini():
    """Guide user through Gemini setup"""
    
    print("\n" + "="*70)
    print("🔧 GEMINI API SETUP WIZARD")
    print("="*70)
    
    # Step 1: Check if .env exists
    env_path = Path(".env")
    print("\n[Step 1] Checking .env file...")
    
    if env_path.exists():
        print(f"✓ .env file found at: {env_path.absolute()}")
        
        # Check if GEMINI_API_KEY already configured
        with open(env_path, "r") as f:
            content = f.read()
            if "GEMINI_API_KEY" in content:
                print("✓ GEMINI_API_KEY already in .env file")
                # Check if it has a value
                for line in content.split("\n"):
                    if line.startswith("GEMINI_API_KEY="):
                        if len(line) > 20:  # Has some value
                            print(f"  Value: {line.split('=')[1][:20]}...")
                        else:
                            print("  ⚠️  Value is empty!")
                        break
            else:
                print("⚠️  GEMINI_API_KEY not found in .env")
    else:
        print("✗ .env file not found")
        print("  Creating new .env file...")
        
        # Create new .env file
        env_content = """# Resume-Insight AI - Environment Configuration

# Google Gemini API Key
# Get your key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=AIzaSyD...your_key_here...

# (Optional) Other LLM providers
# GROQ_API_KEY=gsk_...
# OPENAI_API_KEY=sk-...
"""
        with open(env_path, "w") as f:
            f.write(env_content)
        print(f"✓ Created .env file at: {env_path.absolute()}")
    
    # Step 2: Show current status
    print("\n[Step 2] Current Configuration Status:")
    print("-" * 70)
    
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY not set in environment")
        print("\nTo configure:")
        print("  1. Go to: https://makersuite.google.com/app/apikey")
        print("  2. Click 'Create API Key'")
        print("  3. Copy the key (starts with 'AIzaSyD...')")
        print("  4. Edit .env file and set:")
        print("     GEMINI_API_KEY=AIzaSyD...your_key...")
        print("  5. Restart your terminal or IDE")
        print("  6. Run this script again")
    else:
        print("✓ GEMINI_API_KEY is configured")
        print(f"  Value: {os.getenv('GEMINI_API_KEY')[:30]}...")
    
    # Step 3: Test setup
    print("\n[Step 3] Testing Setup:")
    print("-" * 70)
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("⏭️  Skipping test - API key not configured")
        print("\n📋 Next Steps:")
        print("  1. Configure GEMINI_API_KEY in .env file")
        print("  2. Run: python setup_gemini.py")
        print("  3. Or run: python test_gemini_integration.py")
        return False
    
    # Try to import and test
    try:
        import google.generativeai as genai
        print("✓ google-generativeai library installed")
        
        genai.configure(api_key=api_key)
        print("✓ Gemini API configured")
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, what is Python in one sentence?", stream=False)
        print("✓ API call successful!")
        print(f"  Response: {response.text[:100]}...")
        
    except ImportError:
        print("❌ google-generativeai not installed")
        print("  Run: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "="*70)
    print("✅ SETUP COMPLETE!")
    print("="*70)
    print("\nYour Gemini API is configured and working!")
    print("\n📖 Next Steps:")
    print("  1. Run tests: python test_gemini_integration.py")
    print("  2. Or test via API: http://localhost:8000/api/analyze")
    print("  3. Or update frontend: npm run dev (in frontend/)")
    
    return True

if __name__ == "__main__":
    setup_gemini()
