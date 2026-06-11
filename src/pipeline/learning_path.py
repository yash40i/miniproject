"""
Learning path generation module for Resume-Insight AI.
Creates structured, sequential milestone roadmaps from LLM recommendations.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

from src.pipeline.llm_feedback import FeedbackResult


@dataclass
class Milestone:
    """Represents a single learning milestone."""
    id: int
    title: str
    description: str
    skills: List[str]
    resources: List[Dict[str, str]]
    estimated_hours: int
    difficulty: str  # beginner, intermediate, advanced
    prerequisites: List[int] = field(default_factory=list)
    start_date: Optional[datetime] = None
    target_completion: Optional[datetime] = None


@dataclass
class LearningPath:
    """Complete learning roadmap."""
    title: str
    description: str
    total_hours: int
    estimated_weeks: int
    milestones: List[Milestone]
    priority_skills: List[str]
    resources: Dict[str, List[str]]
    created_date: datetime = field(default_factory=datetime.now)


class LearningPathGenerator:
    """
    Generates structured learning paths from feedback.
    Creates sequential milestones with realistic timelines.
    """
    
    # Resource database
    RESOURCE_DATABASE = {
        "Python": [
            {
                "title": "Python Official Tutorial",
                "url": "https://docs.python.org/3/tutorial/",
                "type": "Official Docs",
                "hours": 20
            },
            {
                "title": "Real Python - Comprehensive Guides",
                "url": "https://realpython.com",
                "type": "Online Course",
                "hours": 40
            },
        ],
        "Machine Learning": [
            {
                "title": "Scikit-learn Documentation",
                "url": "https://scikit-learn.org",
                "type": "Official Docs",
                "hours": 15
            },
            {
                "title": "Andrew Ng's ML Specialization",
                "url": "https://www.coursera.org/specializations/machine-learning-introduction",
                "type": "Online Course",
                "hours": 50
            },
        ],
        "Deep Learning": [
            {
                "title": "Fast.ai Practical Deep Learning",
                "url": "https://course.fast.ai",
                "type": "Online Course",
                "hours": 40
            },
            {
                "title": "TensorFlow Official Tutorials",
                "url": "https://www.tensorflow.org/tutorials",
                "type": "Official Docs",
                "hours": 30
            },
        ],
        "Data Visualization": [
            {
                "title": "Matplotlib Documentation",
                "url": "https://matplotlib.org",
                "type": "Official Docs",
                "hours": 10
            },
            {
                "title": "Plotly Interactive Visualization",
                "url": "https://plotly.com/python/",
                "type": "Official Docs",
                "hours": 12
            },
        ],
        "SQL": [
            {
                "title": "SQLTutorial.org",
                "url": "https://www.sqltutorial.org",
                "type": "Tutorial",
                "hours": 15
            },
            {
                "title": "LeetCode SQL Problems",
                "url": "https://leetcode.com/problemset/database/",
                "type": "Practice",
                "hours": 20
            },
        ],
    }
    
    def __init__(self):
        """Initialize learning path generator."""
        pass
    
    def generate_path(
        self,
        feedback: FeedbackResult,
        priority_skills: List[str],
        weeks_available: int = 12
    ) -> LearningPath:
        """
        Generate a complete learning path.
        
        Args:
            feedback: FeedbackResult from LLM
            priority_skills: List of priority skills to focus on
            weeks_available: Time frame for learning (default 12 weeks)
            
        Returns:
            LearningPath object
        """
        
        # Create milestones for each priority skill
        milestones = []
        total_hours = 0
        
        for idx, skill in enumerate(priority_skills):
            milestone = self._create_milestone(
                skill_name=skill,
                milestone_id=idx + 1,
                difficulty=self._estimate_difficulty(skill)
            )
            milestones.append(milestone)
            total_hours += milestone.estimated_hours
        
        # Set realistic timelines
        milestones = self._schedule_milestones(milestones, weeks_available)
        
        # Calculate estimated weeks
        estimated_weeks = max(
            int((total_hours + 20) / 15),  # Assuming 15 hours/week
            weeks_available
        )
        
        # Compile resources
        resources = self._compile_resources(priority_skills)
        
        learning_path = LearningPath(
            title=f"Personalized Learning Path - {len(priority_skills)} Priority Skills",
            description=self._generate_description(priority_skills, estimated_weeks),
            total_hours=total_hours,
            estimated_weeks=estimated_weeks,
            milestones=milestones,
            priority_skills=priority_skills,
            resources=resources,
        )
        
        return learning_path
    
    def _create_milestone(
        self,
        skill_name: str,
        milestone_id: int,
        difficulty: str
    ) -> Milestone:
        """
        Create a single learning milestone.
        
        Args:
            skill_name: Name of the skill
            milestone_id: Unique milestone ID
            difficulty: Difficulty level
            
        Returns:
            Milestone object
        """
        
        # Get resources for this skill
        resources = self._get_skill_resources(skill_name)
        
        # Estimate hours based on difficulty
        hours_map = {
            "beginner": 15,
            "intermediate": 25,
            "advanced": 40,
        }
        estimated_hours = hours_map.get(difficulty, 20)
        
        milestone = Milestone(
            id=milestone_id,
            title=f"Master {skill_name}",
            description=f"Develop practical proficiency in {skill_name}",
            skills=[skill_name],
            resources=resources,
            estimated_hours=estimated_hours,
            difficulty=difficulty,
            prerequisites=self._determine_prerequisites(skill_name),
        )
        
        return milestone
    
    def _get_skill_resources(self, skill_name: str) -> List[Dict[str, str]]:
        """Get curated resources for a skill."""
        if skill_name in self.RESOURCE_DATABASE:
            return self.RESOURCE_DATABASE[skill_name]
        else:
            # Generic resource
            return [
                {
                    "title": f"{skill_name} Official Documentation",
                    "type": "Documentation",
                    "hours": 10
                }
            ]
    
    def _schedule_milestones(
        self,
        milestones: List[Milestone],
        weeks_available: int
    ) -> List[Milestone]:
        """
        Schedule milestones with realistic timelines.
        
        Args:
            milestones: List of milestones
            weeks_available: Available weeks
            
        Returns:
            Updated milestones with scheduling
        """
        
        start_date = datetime.now() + timedelta(days=1)
        hours_per_week = 15
        
        for idx, milestone in enumerate(milestones):
            milestone.start_date = start_date + timedelta(
                weeks=int((idx * milestone.estimated_hours) / hours_per_week)
            )
            milestone.target_completion = milestone.start_date + timedelta(
                weeks=max(1, int(milestone.estimated_hours / hours_per_week))
            )
        
        return milestones
    
    def _estimate_difficulty(self, skill_name: str) -> str:
        """Estimate difficulty of a skill."""
        advanced_skills = [
            "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
            "Advanced Python", "Distributed Systems"
        ]
        intermediate_skills = [
            "SQL", "Data Visualization", "API Development", "Cloud Computing"
        ]
        
        skill_lower = skill_name.lower()
        
        for advanced in advanced_skills:
            if advanced.lower() in skill_lower:
                return "advanced"
        
        for intermediate in intermediate_skills:
            if intermediate.lower() in skill_lower:
                return "intermediate"
        
        return "beginner"
    
    def _determine_prerequisites(self, skill_name: str) -> List[int]:
        """Determine prerequisites for a skill."""
        prerequisites = {
            "Machine Learning": ["Python"],
            "Deep Learning": ["Machine Learning", "Python"],
            "Computer Vision": ["Deep Learning", "Python"],
            "NLP": ["Machine Learning", "Python"],
        }
        
        # Simplified: return empty list for now
        # In production, would map to milestone IDs
        return []
    
    def _compile_resources(self, priority_skills: List[str]) -> Dict[str, List[str]]:
        """Compile all resources for priority skills."""
        resources = {}
        
        for skill in priority_skills:
            if skill in self.RESOURCE_DATABASE:
                resources[skill] = [
                    r["title"] for r in self.RESOURCE_DATABASE[skill]
                ]
        
        return resources
    
    def _generate_description(self, skills: List[str], weeks: int) -> str:
        """Generate learning path description."""
        skills_str = ", ".join(skills)
        return (
            f"A structured {weeks}-week learning roadmap focused on mastering: {skills_str}. "
            f"Includes curated resources, realistic timelines, and actionable milestones."
        )


def generate_learning_path(
    feedback: FeedbackResult,
    priority_skills: List[str],
    weeks_available: int = 12
) -> LearningPath:
    """
    Convenience function to generate learning path.
    
    Args:
        feedback: FeedbackResult from LLM
        priority_skills: List of priority skills
        weeks_available: Time available for learning
        
    Returns:
        LearningPath object
    """
    generator = LearningPathGenerator()
    return generator.generate_path(feedback, priority_skills, weeks_available)
