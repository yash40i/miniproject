"""
Main pipeline orchestrator for Resume-Insight AI.
Coordinates all stages of the resume analysis pipeline.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
import json

from src.config.config import PipelineConfig
from src.pipeline.pdf_parser import parse_resume
from src.pipeline.text_cleaner import clean_text, TextCleaner
from src.pipeline.embeddings import EmbeddingGenerator
from src.pipeline.semantic_matcher import SemanticMatcher, MatchingResult
from src.pipeline.llm_feedback import LLMFeedbackGenerator, FeedbackResult
from src.pipeline.learning_path import LearningPathGenerator, LearningPath


@dataclass
class AnalysisResult:
    """Complete analysis result from the pipeline."""
    matching_result: MatchingResult
    feedback_result: Optional[FeedbackResult]
    learning_path: Optional[LearningPath]
    metadata: Dict[str, Any]


class ResumePipeline:
    """
    Orchestrates the complete Resume-Insight AI pipeline.
    Coordinates parsing, cleaning, embedding, matching, feedback, and learning path generation.
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize the pipeline.
        
        Args:
            config: PipelineConfig object (uses defaults if None)
        """
        self.config = config or PipelineConfig()
        
        # Initialize components
        self.text_cleaner = TextCleaner(self.config.text_cleaning_config)
        self.embedding_gen = EmbeddingGenerator(self.config.embedding_config)
        self.semantic_matcher = SemanticMatcher(self.config.semantic_matching_config)
        
        # Initialize optional components
        if self.config.llm_config:
            self.feedback_gen = LLMFeedbackGenerator(self.config.llm_config)
        else:
            self.feedback_gen = None
        
        self.learning_path_gen = LearningPathGenerator()
    
    def analyze_resume(
        self,
        resume_path: str,
        job_description: str,
        generate_feedback: bool = True,
        generate_learning_path: bool = True
    ) -> AnalysisResult:
        """
        Execute complete resume analysis pipeline.
        
        Args:
            resume_path: Path to PDF resume
            job_description: Plain text job description
            generate_feedback: Whether to generate LLM feedback
            generate_learning_path: Whether to generate learning path
            
        Returns:
            AnalysisResult with all analysis outputs
        """
        
        print("[1/6] Parsing PDF resume...")
        parsed_resume = parse_resume(resume_path)
        resume_raw_text = parsed_resume.text
        
        print("[2/6] Cleaning resume text...")
        resume_cleaned = self.text_cleaner.clean(resume_raw_text)
        
        print("[3/6] Cleaning job description...")
        job_cleaned = self.text_cleaner.clean(job_description)
        
        print("[4/6] Generating semantic matches...")
        matching_result = self.semantic_matcher.match(resume_cleaned, job_cleaned)
        
        print(f"   → Match Score: {matching_result.overall_score:.1f}%")
        print(f"   → Matched Skills: {len(matching_result.matched_skills)}")
        print(f"   → Missing Skills: {len(matching_result.missing_skills)}")
        
        feedback_result = None
        learning_path = None
        
        if generate_feedback and self.config.enable_feedback_generation and self.feedback_gen:
            print("[5/6] Generating LLM feedback...")
            try:
                feedback_result = self.feedback_gen.generate_feedback(
                    matching_result,
                    resume_cleaned,
                    job_cleaned
                )
            except Exception as e:
                print(f"   ⚠️  Feedback generation skipped: {str(e)}")
        
        if generate_learning_path and self.config.enable_learning_path_generation:
            print("[6/6] Generating learning path...")
            if feedback_result and feedback_result.priority_skills:
                learning_path = self.learning_path_gen.generate_path(
                    feedback_result,
                    feedback_result.priority_skills,
                    weeks_available=12
                )
            elif matching_result.missing_skills:
                # Create learning path from missing skills
                learning_path = self.learning_path_gen.generate_path(
                    feedback_result,
                    matching_result.missing_skills[:3],
                    weeks_available=12
                )
        
        metadata = {
            "resume_file": resume_path,
            "pages_analyzed": parsed_resume.num_pages,
            "embedding_model": self.config.embedding_config.model_name,
            "embedding_dim": self.embedding_gen.embedding_dim,
        }
        
        return AnalysisResult(
            matching_result=matching_result,
            feedback_result=feedback_result,
            learning_path=learning_path,
            metadata=metadata
        )
    
    def format_report(self, result: AnalysisResult) -> str:
        """
        Format analysis result as human-readable report.
        
        Args:
            result: AnalysisResult object
            
        Returns:
            Formatted report string
        """
        
        report = []
        report.append("=" * 80)
        report.append("RESUME-INSIGHT AI - ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Matching Results
        report.append("📊 SEMANTIC MATCHING RESULTS")
        report.append("-" * 80)
        report.append(f"Overall Match Score: {result.matching_result.overall_score:.1f}%")
        report.append(f"Coverage: {result.matching_result.matched_percentage:.1f}%")
        report.append(f"Matched Skills: {len(result.matching_result.matched_skills)}")
        report.append(f"Missing Skills: {len(result.matching_result.missing_skills)}")
        report.append("")
        
        # Top Matches
        if result.matching_result.matched_skills:
            report.append("Top Matched Skills:")
            for match in result.matching_result.matched_skills[:5]:
                report.append(
                    f"  • {match.resume_skill} ↔ {match.job_skill} "
                    f"(Similarity: {match.similarity_score:.2f}, {match.match_strength})"
                )
        report.append("")
        
        # Missing Skills
        if result.matching_result.missing_skills:
            report.append("Skills to Develop:")
            for skill in result.matching_result.missing_skills[:5]:
                report.append(f"  • {skill}")
        report.append("")
        
        # LLM Feedback
        if result.feedback_result:
            report.append("💡 PERSONALIZED FEEDBACK")
            report.append("-" * 80)
            report.append("")
            report.append("Gap Analysis:")
            report.append(result.feedback_result.gap_analysis)
            report.append("")
            
            if result.feedback_result.recommendations:
                report.append("Recommendations:")
                for i, rec in enumerate(result.feedback_result.recommendations, 1):
                    report.append(f"  {i}. {rec}")
            report.append("")
            
            if result.feedback_result.priority_skills:
                report.append("Priority Skills to Focus On:")
                for skill in result.feedback_result.priority_skills:
                    report.append(f"  • {skill}")
            report.append("")
            
            if result.feedback_result.next_steps:
                report.append("Next Steps:")
                report.append(result.feedback_result.next_steps)
            report.append("")
        
        # Learning Path
        if result.learning_path:
            report.append("🎯 LEARNING ROADMAP")
            report.append("-" * 80)
            report.append(f"Title: {result.learning_path.title}")
            report.append(f"Estimated Duration: {result.learning_path.estimated_weeks} weeks")
            report.append(f"Total Learning Hours: {result.learning_path.total_hours} hours")
            report.append("")
            
            report.append("Milestones:")
            for milestone in result.learning_path.milestones:
                report.append(
                    f"  {milestone.id}. {milestone.title} "
                    f"({milestone.estimated_hours}h, {milestone.difficulty})"
                )
                if milestone.start_date:
                    report.append(
                        f"     Start: {milestone.start_date.strftime('%Y-%m-%d')} | "
                        f"Target: {milestone.target_completion.strftime('%Y-%m-%d')}"
                    )
            report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)


def run_pipeline(
    resume_path: str,
    job_description: str,
    config: Optional[PipelineConfig] = None
) -> AnalysisResult:
    """
    Convenience function to run the complete pipeline.
    
    Args:
        resume_path: Path to resume PDF
        job_description: Job description text
        config: Optional PipelineConfig
        
    Returns:
        AnalysisResult object
    """
    pipeline = ResumePipeline(config)
    return pipeline.analyze_resume(resume_path, job_description)
