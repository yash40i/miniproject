"""
Semantic matching module for Resume-Insight AI.
Identifies conceptual matches between resume and job description using cosine similarity.
"""

import numpy as np
import json
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass

from src.config.config import SemanticMatchingConfig, LLMConfig
from src.pipeline.embeddings import EmbeddingGenerator
from src.pipeline.knowledge_graph import ProbabilisticCluster


@dataclass
class SkillMatch:
    """Represents a matched skill between resume and job description."""
    resume_skill: str
    job_skill: str
    similarity_score: float
    match_strength: str  # "high", "medium", "low"


@dataclass
class MatchingResult:
    """Overall semantic matching result."""
    overall_score: float
    matched_skills: List[SkillMatch]
    missing_skills: List[str]
    matched_percentage: float
    detailed_scores: Dict[str, float]


class SemanticMatcher:
    """
    Performs semantic matching between resume and job description.
    Identifies conceptual synonyms and calculates matching scores.
    """
    
    def __init__(self, config: SemanticMatchingConfig = None, llm_config: Optional[LLMConfig] = None):
        """
        Initialize semantic matcher.
        
        Args:
            config: SemanticMatchingConfig object
            llm_config: Optional LLMConfig for skill extraction
        """
        self.config = config or SemanticMatchingConfig()
        self.llm_config = llm_config
        self.embedding_gen = EmbeddingGenerator()
        
        self.llm_client = None
        if self.llm_config:
            self._initialize_llm_client()
            
    def _initialize_llm_client(self):
        """Initialize LLM client for skill extraction."""
        if not self.llm_config:
            return
        provider = self.llm_config.provider.lower()
        try:
            if provider == "groq":
                from groq import Groq
                self.llm_client = Groq(api_key=self.llm_config.api_key, timeout=240.0)
            elif provider == "openai":
                from openai import OpenAI
                self.llm_client = OpenAI(api_key=self.llm_config.api_key, timeout=240.0)
        except Exception as e:
            print(f"Warning: Could not initialize LLM client in SemanticMatcher: {e}")
    
    def match(
        self,
        resume_text: str,
        job_description: str
    ) -> MatchingResult:
        """
        Perform semantic matching between resume and job description.
        
        Args:
            resume_text: Cleaned resume text
            job_description: Cleaned job description text
            
        Returns:
            MatchingResult with scores and matches
        """
        # Extract and chunk text into skills/concepts
        resume_chunks = self._extract_chunks(resume_text, is_job=False)
        job_chunks = self._extract_chunks(job_description, is_job=True)
        
        # Generate embeddings
        resume_embeddings = self.embedding_gen.embed(resume_chunks)
        job_embeddings = self.embedding_gen.embed(job_chunks)
        
        # Calculate similarity matrix
        similarity_matrix = self.embedding_gen.batch_similarity(
            resume_embeddings,
            job_embeddings
        )
        
        # Find matches
        matches = self._find_matches(
            resume_chunks,
            job_chunks,
            similarity_matrix
        )
        
        # Identify missing skills
        matched_job_indices = set(match[1] for match in matches)
        missing_skills = [
            job_chunks[i] for i in range(len(job_chunks))
            if i not in matched_job_indices
        ]
        
        # Augment missing skills using ProbabilisticCluster
        cluster = ProbabilisticCluster()
        companions = cluster.get_companion_skills(missing_skills, threshold=0.7)
        matched_resume_skills_lower = {chunk.lower() for chunk in resume_chunks}
        missing_skills_lower = {s.lower() for s in missing_skills}
        for comp in companions:
            comp_name = comp["skill"]
            if comp_name.lower() not in matched_resume_skills_lower and comp_name.lower() not in missing_skills_lower:
                missing_skills.append(comp_name)
                print(f"   -> Probabilistic Grouping: Added companion skill '{comp_name}' (P={comp['probability']:.2f})")
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(matches)
        matched_percentage = (len(matches) / len(job_chunks)) * 100 if job_chunks else 0
        
        # Create SkillMatch objects
        skill_matches = [
            SkillMatch(
                resume_skill=resume_chunks[resume_idx],
                job_skill=job_chunks[job_idx],
                similarity_score=score,
                match_strength=self._get_match_strength(score)
            )
            for resume_idx, job_idx, score in matches
        ]
        
        return MatchingResult(
            overall_score=overall_score,
            matched_skills=skill_matches,
            missing_skills=missing_skills,
            matched_percentage=matched_percentage,
            detailed_scores={
                "num_resume_chunks": len(resume_chunks),
                "num_job_chunks": len(job_chunks),
                "num_matches": len(matches),
            }
        )
    
    def _extract_chunks_with_llm(self, text: str, is_job: bool) -> List[str]:
        """Extract high-quality list of skills using Groq/OpenAI."""
        if not self.llm_client:
            return []
            
        role = "job description" if is_job else "resume"
        prompt = f"""
You are an expert technical recruiter. Analyze the following {role} text and extract a clean list of concrete technical skills, programming languages, tools, architectures, and professional competencies.
Do NOT extract general sentences, filler text, or corporate fluff (e.g. do NOT extract "our clients' needs are constantly evolving", "we focus on professional development", "talented individuals").
Only extract specific, recognizable skills (e.g. "Python", "Docker", "Machine Learning", "Software Engineering", "AWS", "Communication").

Text:
{text}

Response Format:
You MUST return ONLY a JSON list of strings, with no markdown code blocks, no additional explanation, and no extra characters:
["Skill 1", "Skill 2", "Skill 3"]
"""
        try:
            response = self.llm_client.chat.completions.create(
                model=self.llm_config.model or "llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=400,
            )
            content = response.choices[0].message.content.strip()
            
            if content.startswith("```"):
                lines = content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                content = "\n".join(lines).strip()
                
            skills = json.loads(content)
            if isinstance(skills, list):
                result = [str(s).strip() for s in skills if s and str(s).strip()]
                print(f"DEBUG: Successfully extracted {len(result)} skills from {role} via Groq!")
                return result
        except Exception as e:
            print(f"Error extracting skills using LLM: {e}")
            
        return []

    def _extract_chunks(self, text: str, is_job: bool = False) -> List[str]:
        """
        Extract skill-like chunks from text.
        If LLM is available, use LLM for precise skill extraction.
        
        Args:
            text: Input text
            is_job: Boolean flag indicating if text is from a job description
            
        Returns:
            List of extracted chunks
        """
        if self.llm_client:
            llm_skills = self._extract_chunks_with_llm(text, is_job)
            if llm_skills:
                return llm_skills

        # Heuristic fallback if LLM is unavailable or fails
        text = text.replace('\n', ' ')
        
        # Split by common delimiters
        chunks = []
        for delimiter in ['.', ';', ',', '\n']:
            text = text.replace(delimiter, ' | ')
        
        for chunk in text.split('|'):
            chunk = chunk.strip()
            # Keep chunks between 3 and chunk_size characters
            if 3 <= len(chunk) <= self.config.chunk_size:
                chunks.append(chunk)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_chunks = []
        for chunk in chunks:
            if chunk.lower() not in seen:
                seen.add(chunk.lower())
                unique_chunks.append(chunk)
        
        return unique_chunks
    
    def _find_matches(
        self,
        resume_chunks: List[str],
        job_chunks: List[str],
        similarity_matrix: np.ndarray
    ) -> List[Tuple[int, int, float]]:
        """
        Find best matches between resume and job chunks.
        
        Args:
            resume_chunks: Resume chunks
            job_chunks: Job chunks
            similarity_matrix: Similarity scores (resume x job)
            
        Returns:
            List of (resume_idx, job_idx, score) tuples
        """
        matches = []
        matched_job_indices = set()
        
        # For each job requirement, find best resume match
        for job_idx in range(len(job_chunks)):
            job_similarities = similarity_matrix[:, job_idx]
            
            # Find best match
            best_resume_idx = np.argmax(job_similarities)
            best_score = job_similarities[best_resume_idx]
            
            # Only include if above threshold
            if best_score >= self.config.similarity_threshold:
                matches.append((best_resume_idx, job_idx, best_score))
                matched_job_indices.add(job_idx)
        
        # Sort by score descending
        matches.sort(key=lambda x: x[2], reverse=True)
        
        # Return top-k matches
        return matches[:self.config.top_k_matches]
    
    def _calculate_overall_score(self, matches: List[Tuple[int, int, float]]) -> float:
        """
        Calculate overall matching score (0-100).
        
        Args:
            matches: List of (resume_idx, job_idx, score) tuples
            
        Returns:
            Overall score as percentage
        """
        if not matches:
            return 0.0
        
        # Average of match scores, converted to 0-100 scale
        avg_similarity = np.mean([score for _, _, score in matches])
        return float(avg_similarity * 100)
    
    def _get_match_strength(self, score: float) -> str:
        """
        Classify match strength based on similarity score.
        
        Args:
            score: Similarity score (0-1)
            
        Returns:
            Match strength category
        """
        if score >= 0.85:
            return "high"
        elif score >= 0.65:
            return "medium"
        else:
            return "low"


def match_resume_to_job(resume_text: str, job_description: str) -> MatchingResult:
    """
    Convenience function to match resume to job description.
    
    Args:
        resume_text: Cleaned resume text
        job_description: Cleaned job description text
        
    Returns:
        MatchingResult object
    """
    matcher = SemanticMatcher()
    return matcher.match(resume_text, job_description)
