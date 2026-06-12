"""
Test script for Resume-Insight AI pipeline with sample data.
Runs end-to-end testing without requiring PDF or LLM API.
"""

import sys
from pathlib import Path
import json

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import PipelineConfig, TextCleaningConfig, EmbeddingConfig, SemanticMatchingConfig
from src.pipeline.text_cleaner import TextCleaner
from src.pipeline.embeddings import EmbeddingGenerator
from src.pipeline.semantic_matcher import SemanticMatcher
from src.pipeline.learning_path import LearningPathGenerator
from src.utils import setup_logging, load_job_description, extract_skills_from_text


def load_sample_data():
    """Load sample resume and job description."""
    samples_dir = Path(__file__).parent
    
    resume_path = samples_dir / "sample_resume.txt"
    job_path = samples_dir / "sample_job_description.txt"
    
    with open(resume_path, 'r') as f:
        resume_text = f.read()
    
    with open(job_path, 'r') as f:
        job_description = f.read()
    
    return resume_text, job_description


def test_text_cleaning():
    """Test Stage 2: Text Cleaning."""
    print("\n" + "="*80)
    print("STAGE 2: TEXT CLEANING & NORMALIZATION")
    print("="*80)
    
    resume_text, job_description = load_sample_data()
    
    config = TextCleaningConfig(
        remove_urls=True,
        remove_emails=True,
        expand_abbreviations=True,
        lowercase=True,
    )
    
    cleaner = TextCleaner(config)
    
    print("\n[TEXT] Original Resume (first 300 chars):")
    print(resume_text[:300] + "...")
    
    cleaned_resume = cleaner.clean(resume_text)
    
    print("\n[CLEANED] Cleaned Resume (first 300 chars):")
    print(cleaned_resume[:300] + "...")
    
    print(f"\n[STATS] Text Cleaning Results:")
    print(f"   Original length: {len(resume_text)} characters")
    print(f"   Cleaned length: {len(cleaned_resume)} characters")
    print(f"   Reduction: {((len(resume_text) - len(cleaned_resume)) / len(resume_text) * 100):.1f}%")
    
    return cleaned_resume, cleaner.clean(job_description)


def test_embeddings(cleaned_resume, cleaned_job):
    """Test Stage 3: Embedding Generation."""
    print("\n" + "="*80)
    print("STAGE 3: EMBEDDING GENERATION")
    print("="*80)
    
    print("\n[WAIT] Generating embeddings (this may take 30-60 seconds on first run)...")
    
    gen = EmbeddingGenerator(EmbeddingConfig(device="cpu"))
    
    print(f"[MODEL] Model Information:")
    model_info = gen.get_model_info()
    print(f"   Model: {model_info['model_name']}")
    print(f"   Dimension: {model_info['embedding_dim']}")
    print(f"   Device: {model_info['device']}")
    print(f"   Normalization: {model_info['normalize']}")
    
    # Generate embeddings for key sections
    resume_sections = [
        s.strip() for s in cleaned_resume.split('\n\n') if len(s.strip()) > 50
    ][:5]  # First 5 sections
    
    job_sections = [
        s.strip() for s in cleaned_job.split('\n\n') if len(s.strip()) > 50
    ][:5]
    
    print(f"\n[PROCESS] Embedding {len(resume_sections)} resume sections + {len(job_sections)} job sections...")
    
    resume_embeddings = gen.embed(resume_sections)
    job_embeddings = gen.embed(job_sections)
    
    print(f"\n[SUCCESS] Embeddings Generated:")
    print(f"   Resume embeddings shape: {resume_embeddings.shape}")
    print(f"   Job embeddings shape: {job_embeddings.shape}")
    
    # Calculate sample similarity
    sample_sim = gen.similarity(resume_embeddings[0], job_embeddings[0])
    print(f"\n[METRIC] Sample Similarity (resume[0] vs job[0]): {sample_sim:.4f}")
    
    return gen, resume_sections, job_sections, resume_embeddings, job_embeddings


def test_semantic_matching(cleaned_resume, cleaned_job):
    """Test Stage 4: Semantic Matching."""
    print("\n" + "="*80)
    print("STAGE 4: SEMANTIC MATCHING")
    print("="*80)
    
    matcher = SemanticMatcher()
    
    print("\n[PROCESS] Running semantic matching...")
    result = matcher.match(cleaned_resume, cleaned_job)
    
    print(f"\n[RESULTS] Matching Results:")
    print(f"   Overall Score: {result.overall_score:.1f}%")
    print(f"   Match Coverage: {result.matched_percentage:.1f}%")
    print(f"   Matched Skills: {len(result.matched_skills)}")
    print(f"   Missing Skills: {len(result.missing_skills)}")
    
    # Display top matches
    print(f"\n[MATCHES] Top 5 Matched Skills:")
    for i, match in enumerate(result.matched_skills[:5], 1):
        print(f"   {i}. Resume: '{match.resume_skill}'")
        print(f"      -> Job: '{match.job_skill}'")
        print(f"      Similarity: {match.similarity_score:.3f} ({match.match_strength})")
    
    # Display some missing skills
    if result.missing_skills:
        print(f"\n[GAPS] Sample Missing Skills (5 of {len(result.missing_skills)}):")
        for skill in result.missing_skills[:5]:
            print(f"   * {skill}")
    
    return result


def test_learning_path_generation(missing_skills):
    """Test Stage 6: Learning Path Generation."""
    print("\n" + "="*80)
    print("STAGE 6: LEARNING PATH GENERATION")
    print("="*80)
    
    if not missing_skills:
        print("\n[WARNING] No missing skills to create learning path for.")
        return None
    
    # Create mock feedback for learning path
    from src.pipeline.llm_feedback import FeedbackResult
    
    feedback = FeedbackResult(
        gap_analysis="Resume shows strong ML foundation but lacks some advanced skills.",
        recommendations=[
            "Deepen knowledge of Kubernetes for production ML deployment",
            "Explore advanced MLOps practices and model monitoring",
            "Study large language model fine-tuning techniques",
        ],
        priority_skills=missing_skills[:3],
        next_steps="Start with online courses covering priority skills."
    )
    
    print("\n[PROCESS] Generating learning path...")
    
    gen = LearningPathGenerator()
    learning_path = gen.generate_path(feedback, feedback.priority_skills, weeks_available=12)
    
    print(f"\n[SUCCESS] Learning Path Generated:")
    print(f"   Title: {learning_path.title}")
    print(f"   Total Hours: {learning_path.total_hours}")
    print(f"   Estimated Weeks: {learning_path.estimated_weeks}")
    print(f"   Milestones: {len(learning_path.milestones)}")
    
    print(f"\n[ROADMAP] Milestones:")
    for milestone in learning_path.milestones:
        print(f"   {milestone.id}. {milestone.title}")
        print(f"      Duration: {milestone.estimated_hours} hours")
        print(f"      Difficulty: {milestone.difficulty}")
        if milestone.resources:
            print(f"      Resources: {len(milestone.resources)} available")
    
    return learning_path


def generate_full_report(match_result):
    """Generate comprehensive analysis report."""
    print("\n" + "="*80)
    print("FINAL ANALYSIS REPORT")
    print("="*80)
    
    report = []
    
    report.append("\n[METRICS] SEMANTIC MATCHING RESULTS")
    report.append("-" * 80)
    report.append(f"Overall Match Score: {match_result.overall_score:.1f}%")
    report.append(f"Coverage: {match_result.matched_percentage:.1f}%")
    report.append(f"Matched Skills: {len(match_result.matched_skills)}")
    report.append(f"Missing Skills: {len(match_result.missing_skills)}")
    report.append("")
    
    # Top Matches
    if match_result.matched_skills:
        report.append("[SUCCESS] Top Matched Skills (showing top 5):")
        for match in match_result.matched_skills[:5]:
            report.append(
                f"   * {match.resume_skill} <-> {match.job_skill} "
                f"[{match.similarity_score:.2f}, {match.match_strength}]"
            )
    report.append("")
    
    # Missing Skills
    if match_result.missing_skills:
        report.append("[ACTION] Skills to Develop (showing top 8):")
        for skill in match_result.missing_skills[:8]:
            report.append(f"   * {skill}")
    report.append("")
    
    # Interpretation
    score = match_result.overall_score
    if score >= 85:
        interpretation = "EXCELLENT match! Your profile aligns very well with the job requirements."
    elif score >= 70:
        interpretation = "GOOD match with some skill gaps to address."
    elif score >= 55:
        interpretation = "MODERATE match. Significant skill development recommended."
    else:
        interpretation = "REQUIRES FOCUS. Major skill gaps need to be addressed."
    
    report.append(f"[INSIGHT] INTERPRETATION")
    report.append("-" * 80)
    report.append(interpretation)
    report.append("")
    
    return "\n".join(report)


def main():
    """Run complete test suite."""
    print("\n" + "="*80)
    print("     RESUME-INSIGHT AI - PIPELINE TEST WITH SAMPLE DATA")
    print("="*80 + "\n")
    
    try:
        # Stage 1: Load Data
        print("STAGE 1: LOADING SAMPLE DATA")
        print("="*80)
        resume_text, job_description = load_sample_data()
        print(f"[OK] Loaded resume ({len(resume_text)} chars)")
        print(f"[OK] Loaded job description ({len(job_description)} chars)")
        
        # Stage 2: Text Cleaning
        cleaned_resume, cleaned_job = test_text_cleaning()
        
        # Stage 3: Embeddings
        gen, resume_sections, job_sections, resume_emb, job_emb = test_embeddings(
            cleaned_resume, cleaned_job
        )
        
        # Stage 4: Semantic Matching
        match_result = test_semantic_matching(cleaned_resume, cleaned_job)
        
        # Stage 5: Learning Path
        learning_path = test_learning_path_generation(match_result.missing_skills)
        
        # Final Report
        report = generate_full_report(match_result)
        print(report)
        
        print("\n" + "="*80)
        print("[SUCCESS] PIPELINE TEST COMPLETED!")
        print("="*80)
        
        # Save results
        results = {
            "match_score": float(match_result.overall_score),
            "matched_skills_count": len(match_result.matched_skills),
            "missing_skills_count": len(match_result.missing_skills),
            "top_matches": [
                {
                    "resume": m.resume_skill,
                    "job": m.job_skill,
                    "similarity": float(m.similarity_score)
                }
                for m in match_result.matched_skills[:5]
            ],
            "missing_skills_sample": match_result.missing_skills[:8],
        }
        
        output_path = Path(__file__).parent / "test_results.json"
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n[SAVED] Results saved to: {output_path}")
        print("\n[OK] Test completed! Pipeline is working correctly.\n")
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
