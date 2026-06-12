#!/usr/bin/env python3
"""
Test Gemini API Integration
Tests the LLM feedback generation with Gemini API
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_gemini_integration():
    """Test Gemini API integration"""
    
    print("\n" + "="*60)
    print("🧪 Testing Gemini API Integration")
    print("="*60)
    
    # Test 1: Check environment setup
    print("\n[1] Checking environment setup...")
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print(f"✅ GEMINI_API_KEY found: {gemini_key[:20]}...")
    else:
        print("❌ GEMINI_API_KEY not found in environment")
        print("   Please set GEMINI_API_KEY environment variable")
        return False
    
    # Test 2: Check library installation
    print("\n[2] Checking google-generativeai installation...")
    try:
        import google.generativeai as genai
        print("✅ google-generativeai is installed")
    except ImportError:
        print("❌ google-generativeai not installed")
        print("   Run: pip install google-generativeai")
        return False
    
    # Test 3: Initialize config
    print("\n[3] Testing LLMConfig with Gemini...")
    try:
        from src.config.config import LLMConfig
        config = LLMConfig(provider="gemini", model="gemini-1.5-flash")
        print(f"✅ LLMConfig initialized successfully")
        print(f"   Provider: {config.provider}")
        print(f"   Model: {config.model}")
        print(f"   Temperature: {config.temperature}")
        print(f"   Max tokens: {config.max_tokens}")
    except Exception as e:
        print(f"❌ Failed to initialize LLMConfig: {e}")
        return False
    
    # Test 4: Initialize LLMFeedbackGenerator
    print("\n[4] Testing LLMFeedbackGenerator with Gemini...")
    try:
        from src.pipeline.llm_feedback import LLMFeedbackGenerator
        generator = LLMFeedbackGenerator(config)
        print("✅ LLMFeedbackGenerator initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize LLMFeedbackGenerator: {e}")
        return False
    
    # Test 5: Test simple LLM call
    print("\n[5] Testing simple LLM call...")
    try:
        response = generator._call_llm("What is Python? (Keep answer to 1 sentence)")
        if response and not response.startswith("Error"):
            print("✅ LLM call successful!")
            print(f"   Response: {response[:100]}...")
        else:
            print(f"❌ LLM returned error: {response}")
            return False
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        return False
    
    # Test 6: Test with MatchingResult
    print("\n[6] Testing feedback generation with sample data...")
    try:
        from src.pipeline.semantic_matcher import MatchingResult, SkillMatch
        
        # Create sample matching result
        sample_match = MatchingResult(
            overall_score=75.0,
            matched_percentage=75.0,
            matched_skills=[
                SkillMatch("Python", "Python", 0.99, "perfect"),
                SkillMatch("FastAPI", "REST APIs", 0.85, "strong"),
            ],
            missing_skills=["AWS", "Docker", "Kubernetes", "Machine Learning"],
            unmatched_job_skills=["AWS", "Docker"]
        )
        
        feedback = generator.generate_feedback(
            matching_result=sample_match,
            resume_text="Senior Python developer with 7 years experience using FastAPI",
            job_description="Senior Python Engineer needed. Must have AWS and Docker experience. ML background preferred."
        )
        
        print("✅ Feedback generation successful!")
        print(f"\n   Gap Analysis: {feedback.gap_analysis[:150]}...")
        print(f"\n   Recommendations ({len(feedback.recommendations)} items):")
        for i, rec in enumerate(feedback.recommendations[:2], 1):
            print(f"      {i}. {rec[:80]}...")
        print(f"\n   Priority Skills: {feedback.priority_skills}")
        print(f"\n   Next Steps: {feedback.next_steps[:150]}...")
        
    except Exception as e:
        print(f"❌ Feedback generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 7: Summary
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\n✨ Gemini API Integration is working correctly!")
    print("   You can now use it in production:")
    print("   - Backend API: /api/analyze endpoint")
    print("   - Learning paths: /api/learning-path/adaptive endpoint")
    print("   - AI feedback: Generated automatically\n")
    
    return True

if __name__ == "__main__":
    success = test_gemini_integration()
    sys.exit(0 if success else 1)
