"""
LLM-based feedback generation module for Resume-Insight AI.
Generates human-readable prescriptive feedback based on semantic matching results.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import json
import numpy as np

from src.config.config import LLMConfig
from src.pipeline.semantic_matcher import MatchingResult


@dataclass
class FeedbackResult:
    """Structured feedback from LLM."""
    gap_analysis: str
    recommendations: list
    priority_skills: list
    next_steps: str


def _convert_to_serializable(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, dict):
        return {k: _convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_convert_to_serializable(item) for item in obj]
    elif hasattr(obj, '__dataclass_fields__'):
        return {k: _convert_to_serializable(v) for k, v in asdict(obj).items()}
    return obj


class LLMFeedbackGenerator:
    """
    Generates prescriptive feedback using LLM APIs.
    Supports OpenAI, Groq, and Gemini providers.
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM feedback generator.
        
        Args:
            config: LLMConfig object
        """
        self.config = config
        
        if not config:
            raise ValueError(
                "LLMConfig required. Set LLM_CONFIG in environment or pass config."
            )
        
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """Initialize LLM client based on provider."""
        provider = self.config.provider.lower()
        
        if provider == "openai":
            try:
                from openai import OpenAI
                return OpenAI(api_key=self.config.api_key)
            except ImportError:
                raise ImportError("Install openai: pip install openai")
        
        elif provider == "groq":
            try:
                from groq import Groq
                return Groq(api_key=self.config.api_key)
            except ImportError:
                raise ImportError("Install groq: pip install groq")
        
        elif provider == "gemini":
            try:
                import anthropic
                return anthropic.Anthropic(api_key=self.config.api_key)
            except ImportError:
                raise ImportError("Install anthropic: pip install anthropic")
        
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def generate_feedback(
        self,
        matching_result: MatchingResult,
        resume_text: str,
        job_description: str
    ) -> FeedbackResult:
        """
        Generate comprehensive feedback based on matching results.
        
        Args:
            matching_result: MatchingResult from semantic matching
            resume_text: Original resume text
            job_description: Original job description text
            
        Returns:
            FeedbackResult with structured feedback
        """
        
        # Prepare context for LLM
        context = self._prepare_context(matching_result, resume_text, job_description)
        
        # Generate gap analysis
        gap_analysis = self._generate_gap_analysis(context)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(context, gap_analysis)
        
        # Identify priority skills
        priority_skills = self._identify_priority_skills(context, matching_result)
        
        # Generate next steps
        next_steps = self._generate_next_steps(priority_skills)
        
        return FeedbackResult(
            gap_analysis=gap_analysis,
            recommendations=recommendations,
            priority_skills=priority_skills,
            next_steps=next_steps
        )
    
    def _prepare_context(
        self,
        matching_result: MatchingResult,
        resume_text: str,
        job_description: str
    ) -> Dict[str, Any]:
        """Prepare context dictionary for LLM prompts."""
        
        matched_pairs = [
            {
                "resume": match.resume_skill,
                "job": match.job_skill,
                "similarity": match.similarity_score,
                "strength": match.match_strength
            }
            for match in matching_result.matched_skills
        ]
        
        return {
            "overall_score": matching_result.overall_score,
            "matched_percentage": matching_result.matched_percentage,
            "matched_skills": matched_pairs,
            "missing_skills": matching_result.missing_skills,
            "num_matched": len(matching_result.matched_skills),
            "num_missing": len(matching_result.missing_skills),
        }
    
    def _generate_gap_analysis(self, context: Dict[str, Any]) -> str:
        """
        Generate gap analysis using LLM.
        
        Args:
            context: Prepared context dictionary
            
        Returns:
            Gap analysis text
        """
        # Convert numpy types to Python types for JSON serialization
        context_serializable = _convert_to_serializable(context)
        
        prompt = f"""
        Based on the following resume-to-job matching analysis, provide a concise gap analysis:
        
        Overall Match Score: {context_serializable['overall_score']:.1f}%
        Matched Skills: {context_serializable['num_matched']} out of {context_serializable['num_matched'] + context_serializable['num_missing']}
        
        Skills Present:
        {json.dumps(context_serializable['matched_skills'], indent=2)}
        
        Skills Missing:
        {json.dumps(context_serializable['missing_skills'], indent=2)}
        
        Provide a brief (2-3 sentences) gap analysis highlighting the key differences.
        """
        
        response = self._call_llm(prompt)
        return response
    
    def _generate_recommendations(
        self,
        context: Dict[str, Any],
        gap_analysis: str
    ) -> list:
        """
        Generate specific recommendations using LLM.
        
        Args:
            context: Prepared context dictionary
            gap_analysis: Previously generated gap analysis
            
        Returns:
            List of recommendations
        """
        # Convert numpy types to Python types for JSON serialization
        context_serializable = _convert_to_serializable(context)
        
        prompt = f"""
        Based on this gap analysis and missing skills, provide 5 specific, actionable recommendations:
        
        Gap Analysis: {gap_analysis}
        
        Missing Skills to Acquire:
        {json.dumps(context_serializable['missing_skills'][:10], indent=2)}
        
        Return as a JSON array of strings. Each recommendation should be specific and measurable.
        Example format: ["Learn TensorFlow by completing the official tutorial", ...]
        """
        
        response = self._call_llm(prompt)
        
        try:
            recommendations = json.loads(response)
            return recommendations[:5]
        except:
            # Fallback to simple string parsing if JSON parsing fails
            lines = response.split('\n')
            recommendations = [line.strip('- ') for line in lines if line.strip()]
            return recommendations[:5]
    
    def _identify_priority_skills(
        self,
        context: Dict[str, Any],
        matching_result: MatchingResult
    ) -> list:
        """
        Identify priority skills to focus on.
        
        Args:
            context: Prepared context dictionary
            matching_result: MatchingResult object
            
        Returns:
            List of priority skills
        """
        
        if not matching_result.missing_skills:
            return []
        
        prompt = f"""
        From these missing skills, identify the top 3 PRIORITY skills that would have the most impact
        on resume competitiveness for this job.
        
        Missing Skills:
        {json.dumps(matching_result.missing_skills[:15], indent=2)}
        
        Return as a JSON array of strings, ordered by priority.
        Example: ["Python", "Machine Learning", "SQL"]
        """
        
        response = self._call_llm(prompt)
        
        try:
            priority_skills = json.loads(response)
            return priority_skills[:3]
        except:
            return matching_result.missing_skills[:3]
    
    def _generate_next_steps(self, priority_skills: list) -> str:
        """
        Generate actionable next steps.
        
        Args:
            priority_skills: List of priority skills
            
        Returns:
            Next steps text
        """
        
        skills_text = ", ".join(priority_skills) if priority_skills else "the identified skill gaps"
        
        prompt = f"""
        Create a concise actionable plan (3-4 sentences) to start learning these skills immediately:
        
        Priority Skills: {skills_text}
        
        Focus on concrete, free or low-cost resources and realistic timelines.
        """
        
        response = self._call_llm(prompt)
        return response
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call LLM API with given prompt.
        
        Args:
            prompt: Prompt text
            
        Returns:
            LLM response text
        """
        
        provider = self.config.provider.lower()
        
        try:
            if provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )
                return response.choices[0].message.content
            
            elif provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )
                return response.choices[0].message.content
            
            elif provider == "gemini":
                # Placeholder for Gemini API
                raise NotImplementedError("Gemini provider not yet implemented")
            
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return f"Error generating feedback: {str(e)}"


def generate_feedback(
    matching_result: MatchingResult,
    resume_text: str,
    job_description: str,
    config: Optional[LLMConfig] = None
) -> FeedbackResult:
    """
    Convenience function to generate feedback.
    
    Args:
        matching_result: MatchingResult from semantic matching
        resume_text: Original resume text
        job_description: Original job description text
        config: Optional LLMConfig
        
    Returns:
        FeedbackResult with structured feedback
    """
    if config is None:
        from src.config.config import DEFAULT_CONFIG
        config = DEFAULT_CONFIG.llm_config
    
    generator = LLMFeedbackGenerator(config)
    return generator.generate_feedback(matching_result, resume_text, job_description)
