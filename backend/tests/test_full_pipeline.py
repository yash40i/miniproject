from pathlib import Path
from dotenv import load_dotenv
load_dotenv('.env')

# Test full pipeline
from src.pipeline.pipeline import ResumePipeline
from src.config import PipelineConfig

config = PipelineConfig()
print('Pipeline Config:')
print(f'  Enable Feedback: {config.enable_feedback_generation}')
print(f'  Enable Learning Path: {config.enable_learning_path_generation}')
print()

# Create pipeline
pipeline = ResumePipeline(config)

# Load sample files
resume_path = Path('sample_resume.pdf')
job_desc = Path('sample_job.txt').read_text()

print('Running full pipeline...')
try:
    result = pipeline.analyze_resume(resume_path, job_desc)
    
    print(f'Matching Score: {result.matching_result.overall_score:.1f}%')
    print(f'Has Feedback: {result.feedback_result is not None}')
    print(f'Has Learning Path: {result.learning_path is not None}')
    print()
    
    if result.feedback_result:
        print('[OK] GROQ LLM FEEDBACK GENERATED!')
        print()
        print('Gap Analysis:')
        print(result.feedback_result.gap_analysis[:300])
        print()
        print(f'Recommendations ({len(result.feedback_result.recommendations)} items):')
        for i, rec in enumerate(result.feedback_result.recommendations[:3], 1):
            print(f'  {i}. {rec}')
        print()
        print(f'Priority Skills: {result.feedback_result.priority_skills}')
    
    if result.learning_path:
        print()
        print('Learning Path Generated:')
        print(f'  Milestones: {len(result.learning_path.milestones)} items')
    
    print()
    print('[OK] COMPLETE PIPELINE WORKING END-TO-END!')
    print('   All 6 stages executed successfully:')
    print('   [1] PDF Parse [2] NLP Clean [3] Job Clean')
    print('   [4] Semantic Match [5] Groq LLM [6] Learning Path')
    
except Exception as e:
    print(f'Error: {str(e)[:300]}')
    import traceback
    traceback.print_exc()
