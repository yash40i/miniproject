"""
Unit and integration tests for ResumeGenerator and PDF compilation.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add backend directory to python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

load_dotenv(os.path.join(backend_dir, ".env"))

from src.pipeline.resume_generator import ResumeGenerator
from src.config.config import LLMConfig


def test_pdf_generation():
    """Verify that structured resume JSON compiles to a non-empty PDF file"""
    print("\n--- Testing PDF Generation ---")
    
    # Sample resume data matching the schema
    sample_data = {
        "personal_info": {
            "name": "Jane Developer",
            "email": "jane.dev@example.com",
            "phone": "+1 (555) 019-2834",
            "location": "New York, NY",
            "linkedin": "linkedin.com/in/janedev",
            "github": "github.com/janedev",
            "website": "janedev.io"
        },
        "summary": "Innovative Senior Frontend Engineer with 5+ years of experience designing and building high-performance web applications using React, Next.js, and TypeScript. Proven track record of improving site speed by 40% and leading cross-functional teams.",
        "skills": {
            "languages": ["JavaScript", "TypeScript", "Python", "SQL", "HTML5", "CSS3"],
            "frameworks_libraries": ["React", "Next.js", "Redux Toolkit", "Tailwind CSS", "FastAPI"],
            "tools_databases": ["Git", "Docker", "Webpack", "PostgreSQL", "MongoDB", "AWS"],
            "other_skills": ["CI/CD", "Agile/Scrum", "RESTful APIs", "System Design"]
        },
        "experience": [
            {
                "company": "Enterprise Tech Solutions",
                "position": "Senior Frontend Engineer",
                "duration": "Mar 2022 - Present",
                "location": "New York, NY",
                "bullets": [
                    "Architected and migrated legacy dashboard to Next.js, improving Core Web Vitals score by 35% and user engagement by 15%.",
                    "Mentored 4 junior developers and established frontend coding guidelines and unit testing standards.",
                    "Collaborated with backend engineering team to integrate FastAPI REST services securely."
                ]
            },
            {
                "company": "StartUp Digital Inc.",
                "position": "Software Engineer",
                "duration": "Jun 2020 - Feb 2022",
                "location": "Boston, MA",
                "bullets": [
                    "Designed and implemented full-stack admin portal using React and Node.js/Express.",
                    "Optimized SQL queries and database indexes, reducing page load times by 20%."
                ]
            }
        ],
        "education": [
            {
                "institution": "Boston University",
                "degree": "B.S. in Computer Science",
                "duration": "2016 - 2020",
                "location": "Boston, MA"
            }
        ],
        "projects": [
            {
                "title": "Open Source UI Components",
                "duration": "2023",
                "description": "Created and published a modern, accessible UI library using Tailwind CSS and Radix UI with over 1k downloads."
            }
        ]
    }
    
    output_path = os.path.join(backend_dir, "tests", "test_output_resume.pdf")
    
    # Ensure tests directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Initialize generator
    generator = ResumeGenerator()
    
    # Compile
    try:
        generator.generate_resume_pdf(sample_data, output_path)
        print(f"PDF successfully compiled at: {output_path}")
        
        # Verify file exists and has size
        assert os.path.exists(output_path), "PDF file does not exist!"
        assert os.path.getsize(output_path) > 0, "PDF file is empty!"
        print(f"Success! PDF size: {os.path.getsize(output_path)} bytes")
        
        # Clean up
        if os.path.exists(output_path):
            os.remove(output_path)
            print("Temporary test PDF cleaned up.")
            
    except Exception as e:
        print(f"Failed PDF generation test: {e}")
        raise e


def test_llm_rewrite():
    """Verify that ResumeGenerator successfully queries LLM and parses JSON response"""
    print("\n--- Testing LLM Rewrite (Live integration check) ---")
    
    llm_config = LLMConfig()
    if not llm_config.api_key:
        print("Skipping LLM rewrite test: GROQ_API_KEY / LLM API Key is not set in environment.")
        return
        
    generator = ResumeGenerator(llm_config)
    
    dummy_resume = """
    John Smith
    john.smith@email.com | 123-456-7890
    
    Experience:
    Software Engineer at WebShop (2022 - Present)
    - Built features using Javascript and React.
    
    Skills: React, JavaScript, HTML, CSS
    """
    
    dummy_jd = """
    We are looking for a Software Engineer who has experience with React, TypeScript, and FastAPI.
    You will develop high-quality backend services and build modern user interfaces.
    """
    
    dummy_matching = {
        "missing_skills": ["TypeScript", "FastAPI"]
    }
    
    try:
        adapted_json = generator.generate_matched_resume_json(
            resume_text=dummy_resume,
            job_description=dummy_jd,
            matching_result=dummy_matching
        )
        
        print("Successfully generated adapted resume JSON from LLM!")
        print(json.dumps(adapted_json, indent=2))
        
        # Check required keys
        for key in ["personal_info", "skills", "experience", "education"]:
            assert key in adapted_json, f"Missing key '{key}' in rewritten resume JSON"
            
        print("Success! JSON schema validated.")
    except Exception as e:
        print(f"Failed LLM rewrite test: {e}")
        raise e


if __name__ == "__main__":
    test_pdf_generation()
    test_llm_rewrite()
