#!/usr/bin/env python
"""
End-to-end test of Resume-Insight AI pipeline
"""
import requests
import json
import time

def main():
    # Read the sample data
    print("=" * 70)
    print("RESUME-INSIGHT AI - END-TO-END TEST")
    print("=" * 70)
    
    with open('examples/test_resume.pdf', 'rb') as f:
        resume_data = f.read()
    
    with open('examples/sample_job_description.txt', 'r') as f:
        job_desc = f.read()
    
    # Upload and analyze
    print("\n[STEP 1] Uploading resume and job description...")
    print(f"  Resume: {len(resume_data)} bytes")
    print(f"  Job Description: {len(job_desc)} characters")
    
    # Prepare form data for multipart upload
    files = {'file': ('test_resume.pdf', resume_data)}
    data = {'job_description': job_desc}
    
    response = requests.post(
        'http://localhost:8000/api/analyze',
        files=files,
        data=data,
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"✗ Error: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    analysis_id = result.get('analysis_id')
    print(f"✓ Analysis started!")
    print(f"  Analysis ID: {analysis_id}")
    print(f"  Status: {result.get('status')}")
    
    # Poll for results
    print("\n[STEP 2] Polling for results...")
    max_wait = 120
    start_time = time.time()
    poll_count = 0
    
    while time.time() - start_time < max_wait:
        poll_count += 1
        result = requests.get(f'http://localhost:8000/api/results/{analysis_id}', timeout=30).json()
        status = result.get('status')
        elapsed = time.time() - start_time
        print(f"  [{elapsed:.1f}s] Poll #{poll_count}: {status}")
        
        if status == 'completed':
            print(f"\n✓ Analysis completed!")
            display_results(result, analysis_id)
            break
        elif status == 'failed':
            print(f"\n✗ Analysis failed: {result.get('error')}")
            break
        
        time.sleep(2)
    else:
        print(f"\n✗ Analysis timeout after {max_wait} seconds")

def display_results(result, analysis_id):
    """Display formatted analysis results"""
    matching = result.get('matching_result', {})
    feedback = result.get('feedback', {})
    learning = result.get('learning_path', {})
    
    print("\n" + "=" * 70)
    print("ANALYSIS RESULTS")
    print("=" * 70)
    
    print(f"\n[MATCH SCORE]")
    print(f"  Overall Match: {matching.get('overall_score', 0):.1f}%")
    print(f"  Matched Percentage: {matching.get('matched_percentage', 0):.1f}%")
    print(f"  Matched Skills: {len(matching.get('matched_skills', []))}")
    print(f"  Missing Skills: {len(matching.get('missing_skills', []))}")
    
    print(f"\n[TOP MATCHED SKILLS]")
    for i, skill in enumerate(matching.get('matched_skills', [])[:5], 1):
        print(f"  {i}. {skill['resume_skill']:20} → {skill['job_skill']:20} ({skill['similarity_score']:.0%})")
    
    if matching.get('missing_skills'):
        print(f"\n[MISSING SKILLS (First 5)]")
        for i, skill in enumerate(matching.get('missing_skills', [])[:5], 1):
            print(f"  {i}. {skill}")
    
    if feedback:
        print(f"\n[FEEDBACK]")
        if feedback.get('gap_analysis'):
            print(f"  Gap Analysis: {feedback['gap_analysis'][:100]}...")
        if feedback.get('priority_skills'):
            print(f"  Priority Skills: {', '.join(feedback['priority_skills'][:3])}")
    
    if learning:
        print(f"\n[LEARNING PATH]")
        print(f"  Title: {learning.get('title')}")
        print(f"  Total Hours: {learning.get('total_hours')}")
        print(f"  Estimated Weeks: {learning.get('estimated_weeks')}")
        print(f"  Milestones: {len(learning.get('milestones', []))}")
    
    print(f"\n[LINKS]")
    print(f"  Frontend: http://localhost:3000/results/{analysis_id}")
    print(f"  API: http://localhost:8000/api/results/{analysis_id}")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
