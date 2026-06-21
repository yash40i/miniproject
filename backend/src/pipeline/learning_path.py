"""
Learning path generation module for Resume-Insight AI.
Creates structured, sequential milestone roadmaps from LLM recommendations.
Enhanced with Groq API for dynamic, personalized responses.
Features adaptive learning paths based on user profile and progress.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

from src.pipeline.llm_feedback import FeedbackResult
from src.config.config import LLMConfig
from src.pipeline.knowledge_graph import SkillDAG, ProbabilisticCluster


@dataclass
class Resource:
    """Represents a single learning resource."""
    title: str
    url: str
    type: str  # Official Docs, Tutorial, Course, Practice, etc.
    hours: int
    difficulty: str  # beginner, intermediate, advanced
    free: bool
    rating: Optional[float] = None  # 1-5 stars
    description: Optional[str] = None


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
    success_criteria: List[str] = field(default_factory=list)  # Measurable outcomes
    projects: List[Dict[str, str]] = field(default_factory=list)  # Hands-on projects
    progress_percentage: int = 0  # Track user progress
    is_completed: bool = False


@dataclass
class UserProfile:
    """User learning profile for personalization."""
    experience_level: str  # beginner, intermediate, advanced
    learning_style: str  # visual, hands-on, theory, mixed
    availability_hours_per_week: int = 15
    preferred_resource_types: List[str] = field(default_factory=list)
    budget: str = "free"  # free, limited, flexible
    timezone: Optional[str] = None
    preferred_languages: List[str] = field(default_factory=list)


@dataclass
class LearningPath:
    """Complete learning roadmap with dynamic adaptation."""
    title: str
    description: str
    total_hours: int
    estimated_weeks: int
    milestones: List[Milestone]
    priority_skills: List[str]
    resources: Dict[str, List[str]]
    created_date: datetime = field(default_factory=datetime.now)
    user_profile: Optional[UserProfile] = None
    overall_progress: int = 0  # Percentage completed
    adaptivity_score: float = 0.0  # How much it adapts to user preferences
    recommendation_engine_used: str = "static"  # static, llm, hybrid


class LearningPathGenerator:
    """
    Generates structured learning paths from feedback.
    Creates sequential milestones with realistic timelines.
    """
    
    # Comprehensive resource database with multiple sources per skill
    RESOURCE_DATABASE = {
        "Python": [
            {
                "title": "Python Official Documentation",
                "url": "https://docs.python.org/3/",
                "type": "Official Docs",
                "hours": 15,
                "difficulty": "beginner",
                "free": True
            },
            {
                "title": "Real Python - Comprehensive Guides",
                "url": "https://realpython.com",
                "type": "Tutorial",
                "hours": 40,
                "difficulty": "beginner",
                "free": True
            },
            {
                "title": "Python for Everybody (Coursera)",
                "url": "https://www.coursera.org/learn/python-for-everybody",
                "type": "Course",
                "hours": 30,
                "difficulty": "beginner",
                "free": True
            },
            {
                "title": "Complete Python Bootcamp (Udemy)",
                "url": "https://www.udemy.com/course/complete-python-bootcamp/",
                "type": "Course",
                "hours": 50,
                "difficulty": "beginner",
                "free": False
            },
            {
                "title": "LeetCode Python Problems",
                "url": "https://leetcode.com/problemset/all/?topicSlugs=python",
                "type": "Practice",
                "hours": 20,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "HackerRank Python Challenges",
                "url": "https://www.hackerrank.com/domains/python",
                "type": "Practice",
                "hours": 15,
                "difficulty": "beginner",
                "free": True
            },
        ],
        "JavaScript": [
            {
                "title": "MDN JavaScript Guide",
                "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
                "type": "Official Docs",
                "hours": 20,
                "difficulty": "beginner",
                "free": True
            },
            {
                "title": "JavaScript.info Comprehensive Tutorial",
                "url": "https://javascript.info",
                "type": "Tutorial",
                "hours": 30,
                "difficulty": "beginner",
                "free": True
            },
            {
                "title": "The Complete JavaScript Course 2024",
                "url": "https://www.udemy.com/course/the-complete-javascript-course/",
                "type": "Course",
                "hours": 60,
                "difficulty": "beginner",
                "free": False
            },
            {
                "title": "FreeCodeCamp JavaScript",
                "url": "https://www.freecodecamp.org/learn/javascript/",
                "type": "Course",
                "hours": 40,
                "difficulty": "beginner",
                "free": True
            },
            {
                "title": "LeetCode JavaScript Problems",
                "url": "https://leetcode.com/problemset/all/?topicSlugs=javascript",
                "type": "Practice",
                "hours": 25,
                "difficulty": "intermediate",
                "free": True
            },
        ],
        "React": [
            {
                "title": "React Official Documentation",
                "url": "https://react.dev",
                "type": "Official Docs",
                "hours": 15,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "React - The Complete Guide 2024",
                "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/",
                "type": "Course",
                "hours": 50,
                "difficulty": "intermediate",
                "free": False
            },
            {
                "title": "FreeCodeCamp React Course",
                "url": "https://www.freecodecamp.org/learn/front-end-development-libraries/react/",
                "type": "Course",
                "hours": 30,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "React Router Official Guide",
                "url": "https://reactrouter.com",
                "type": "Official Docs",
                "hours": 8,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "Build Real Projects with React",
                "url": "https://www.freecodecamp.org/news/create-a-portfolio-website-using-html-css-javascript-tutorial/",
                "type": "Project",
                "hours": 20,
                "difficulty": "intermediate",
                "free": True
            },
        ],
        "SQL": [
            {
                "title": "SQLTutorial.org - Comprehensive Guide",
                "url": "https://www.sqltutorial.org",
                "type": "Tutorial",
                "hours": 12,
                "difficulty": "beginner",
                "free": True
            },
            {
                "title": "W3Schools SQL Tutorial",
                "url": "https://www.w3schools.com/sql/",
                "type": "Tutorial",
                "hours": 10,
                "difficulty": "beginner",
                "free": True
            },
            {
                "title": "Mode Analytics SQL Tutorial",
                "url": "https://mode.com/sql-tutorial/",
                "type": "Tutorial",
                "hours": 15,
                "difficulty": "beginner",
                "free": True
            },
            {
                "title": "LeetCode Database Problems",
                "url": "https://leetcode.com/problemset/database/",
                "type": "Practice",
                "hours": 25,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "HackerRank SQL Challenges",
                "url": "https://www.hackerrank.com/domains/sql",
                "type": "Practice",
                "hours": 20,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "Stanford Databases Course",
                "url": "https://www.edx.org/course/databases-3",
                "type": "Course",
                "hours": 40,
                "difficulty": "intermediate",
                "free": True
            },
        ],
        "Machine Learning": [
            {
                "title": "Scikit-learn Official Documentation",
                "url": "https://scikit-learn.org",
                "type": "Official Docs",
                "hours": 12,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "Andrew Ng's Machine Learning Specialization",
                "url": "https://www.coursera.org/specializations/machine-learning-introduction",
                "type": "Course",
                "hours": 60,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "Google's Machine Learning Crash Course",
                "url": "https://developers.google.com/machine-learning/crash-course",
                "type": "Course",
                "hours": 30,
                "difficulty": "beginner",
                "free": True
            },
            {
                "title": "Fast.ai Practical Deep Learning",
                "url": "https://course.fast.ai",
                "type": "Course",
                "hours": 40,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "Kaggle Machine Learning Competitions",
                "url": "https://www.kaggle.com/competitions",
                "type": "Practice",
                "hours": 50,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "ML Mastery Blog Tutorials",
                "url": "https://machinelearningmastery.com",
                "type": "Tutorial",
                "hours": 35,
                "difficulty": "intermediate",
                "free": True
            },
        ],
        "Deep Learning": [
            {
                "title": "TensorFlow Official Tutorials",
                "url": "https://www.tensorflow.org/tutorials",
                "type": "Official Docs",
                "hours": 25,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "Fast.ai Practical Deep Learning",
                "url": "https://course.fast.ai",
                "type": "Course",
                "hours": 40,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "Deep Learning Specialization (Coursera)",
                "url": "https://www.coursera.org/specializations/deep-learning",
                "type": "Course",
                "hours": 70,
                "difficulty": "advanced",
                "free": True
            },
            {
                "title": "PyTorch Official Tutorials",
                "url": "https://pytorch.org/tutorials/",
                "type": "Official Docs",
                "hours": 20,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "Distill.pub - Deep Learning Explanations",
                "url": "https://distill.pub",
                "type": "Article",
                "hours": 15,
                "difficulty": "advanced",
                "free": True
            },
        ],
        "Node.js": [
            {
                "title": "Node.js Official Documentation",
                "url": "https://nodejs.org/en/docs/",
                "type": "Official Docs",
                "hours": 15,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "The Complete Node.js Developer Course",
                "url": "https://www.udemy.com/course/the-complete-nodejs-developer-course-2/",
                "type": "Course",
                "hours": 50,
                "difficulty": "intermediate",
                "free": False
            },
            {
                "title": "Express.js Guide",
                "url": "https://expressjs.com/",
                "type": "Official Docs",
                "hours": 12,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "FreeCodeCamp Node.js & Express",
                "url": "https://www.freecodecamp.org/learn/back-end-development-and-apis/",
                "type": "Course",
                "hours": 30,
                "difficulty": "intermediate",
                "free": True
            },
        ],
        "Docker": [
            {
                "title": "Docker Official Documentation",
                "url": "https://docs.docker.com/",
                "type": "Official Docs",
                "hours": 10,
                "difficulty": "beginner",
                "free": True
            },
            {
                "title": "Docker Deep Dive Course",
                "url": "https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/",
                "type": "Course",
                "hours": 40,
                "difficulty": "intermediate",
                "free": False
            },
            {
                "title": "FreeCodeCamp Docker Tutorial",
                "url": "https://www.freecodecamp.org/news/docker-tutorial-for-beginners/",
                "type": "Tutorial",
                "hours": 15,
                "difficulty": "beginner",
                "free": True
            },
            {
                "title": "Play with Docker Playground",
                "url": "https://www.play-with-docker.com/",
                "type": "Hands-on Lab",
                "hours": 8,
                "difficulty": "beginner",
                "free": True
            },
        ],
        "AWS": [
            {
                "title": "AWS Official Tutorials",
                "url": "https://aws.amazon.com/getting-started/",
                "type": "Official Docs",
                "hours": 20,
                "difficulty": "beginner",
                "free": True
            },
            {
                "title": "AWS Certified Cloud Practitioner Course",
                "url": "https://www.udemy.com/course/aws-certified-cloud-practitioner-new/",
                "type": "Course",
                "hours": 30,
                "difficulty": "beginner",
                "free": False
            },
            {
                "title": "FreeCodeCamp AWS Course",
                "url": "https://www.freecodecamp.org/news/pass-the-aws-cloud-practitioner-exam-with-this-free-10-hour-course/",
                "type": "Course",
                "hours": 40,
                "difficulty": "beginner",
                "free": True
            },
            {
                "title": "A Cloud Guru - AWS Courses",
                "url": "https://www.pluralsight.com/cloud-guru/courses/aws",
                "type": "Course",
                "hours": 50,
                "difficulty": "intermediate",
                "free": False
            },
        ],
        "Data Visualization": [
            {
                "title": "Matplotlib Official Tutorial",
                "url": "https://matplotlib.org/stable/tutorials/",
                "type": "Official Docs",
                "hours": 12,
                "difficulty": "beginner",
                "free": True
            },
            {
                "title": "Plotly Interactive Visualization",
                "url": "https://plotly.com/python/",
                "type": "Official Docs",
                "hours": 10,
                "difficulty": "beginner",
                "free": True
            },
            {
                "title": "Seaborn Statistical Data Visualization",
                "url": "https://seaborn.pydata.org/",
                "type": "Official Docs",
                "hours": 8,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "Data Visualization with D3.js",
                "url": "https://d3js.org/",
                "type": "Official Docs",
                "hours": 25,
                "difficulty": "advanced",
                "free": True
            },
        ],
        "Git & Version Control": [
            {
                "title": "Git Official Documentation",
                "url": "https://git-scm.com/doc",
                "type": "Official Docs",
                "hours": 8,
                "difficulty": "beginner",
                "free": True
            },
            {
                "title": "GitHub Learning Lab",
                "url": "https://lab.github.com/",
                "type": "Interactive Tutorial",
                "hours": 10,
                "difficulty": "beginner",
                "free": True
            },
            {
                "title": "Atlassian Git Tutorials",
                "url": "https://www.atlassian.com/git/tutorials",
                "type": "Tutorial",
                "hours": 12,
                "difficulty": "beginner",
                "free": True
            },
        ],
        "TypeScript": [
            {
                "title": "TypeScript Official Handbook",
                "url": "https://www.typescriptlang.org/docs/",
                "type": "Official Docs",
                "hours": 15,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "Complete TypeScript Course",
                "url": "https://www.udemy.com/course/learn-typescript/",
                "type": "Course",
                "hours": 30,
                "difficulty": "intermediate",
                "free": False
            },
            {
                "title": "TypeScript for JavaScript Developers",
                "url": "https://www.freecodecamp.org/learn/front-end-development-libraries/typescript/",
                "type": "Course",
                "hours": 20,
                "difficulty": "intermediate",
                "free": True
            },
        ],
        "REST APIs": [
            {
                "title": "RESTful API Design Best Practices",
                "url": "https://restfulapi.net/",
                "type": "Guide",
                "hours": 10,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "FastAPI Official Documentation",
                "url": "https://fastapi.tiangolo.com/",
                "type": "Official Docs",
                "hours": 15,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "Build REST APIs with Flask",
                "url": "https://flask.palletsprojects.com/",
                "type": "Official Docs",
                "hours": 12,
                "difficulty": "intermediate",
                "free": True
            },
        ],
        "NLP": [
            {
                "title": "Hugging Face NLP Course",
                "url": "https://huggingface.co/course",
                "type": "Course",
                "hours": 40,
                "difficulty": "advanced",
                "free": True
            },
            {
                "title": "spaCy Official Tutorial",
                "url": "https://spacy.io/usage",
                "type": "Official Docs",
                "hours": 15,
                "difficulty": "intermediate",
                "free": True
            },
            {
                "title": "NLTK Natural Language Processing",
                "url": "https://www.nltk.org/",
                "type": "Official Docs",
                "hours": 12,
                "difficulty": "intermediate",
                "free": True
            },
        ],
    }
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize learning path generator with optional LLM config for dynamic generation."""
        self.config = config
        self.llm_client = None
        
        if self.config:
            self._initialize_llm_client()
            
        self.skill_dag = SkillDAG()
        self.market_cluster = ProbabilisticCluster()
    
    def _initialize_llm_client(self):
        """Initialize Groq or OpenAI client for dynamic generation."""
        if not self.config:
            return
        
        provider = self.config.provider.lower()
        
        try:
            if provider == "groq":
                from groq import Groq
                self.llm_client = Groq(api_key=self.config.api_key, timeout=240.0)
            elif provider == "openai":
                from openai import OpenAI
                self.llm_client = OpenAI(api_key=self.config.api_key, timeout=240.0)
        except ImportError as e:
            print(f"Warning: Could not initialize {provider} client: {e}")
            self.llm_client = None
    
    def _is_skill_in_resume(self, skill_name: str, resume_text: Optional[str]) -> bool:
        if not resume_text:
            return False
        canonical = self.skill_dag.find_canonical_name(skill_name)
        if not canonical:
            return skill_name.lower() in resume_text.lower()
        return (canonical.lower() in resume_text.lower() or 
                skill_name.lower() in resume_text.lower())

    def generate_path(
        self,
        feedback: FeedbackResult,
        priority_skills: List[str],
        weeks_available: int = 12,
        resume_text: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> LearningPath:
        """
        Generate a complete learning path.
        
        Args:
            feedback: FeedbackResult from LLM
            priority_skills: List of priority skills to focus on
            weeks_available: Time frame for learning (default 12 weeks)
            resume_text: Optional candidate resume text
            job_description: Optional job description text
            
        Returns:
            LearningPath object
        """
        
        # 1. Expand priority_skills to include DAG prerequisites and topological sort
        expanded_skills = self.skill_dag.get_all_required_skills(priority_skills)
        
        # 2. Add companion (market cluster) skills based on conditional probabilities
        companion_skills = self.market_cluster.get_companion_skills(expanded_skills, threshold=0.6)
        # Append only new skills not already in the list (case‑insensitive)
        existing = {s.lower() for s in expanded_skills}
        for comp in companion_skills:
            comp_name = comp["skill"]
            if comp_name.lower() not in existing:
                expanded_skills.append(comp_name)
                existing.add(comp_name.lower())

        # 3. Filter out skills already present in candidate's resume
        skills_to_learn = []
        for skill in expanded_skills:
            # Skip if candidate already has this skill and it wasn't explicitly requested
            if self._is_skill_in_resume(skill, resume_text) and skill not in priority_skills:
                continue
            skills_to_learn.append(skill)
            
        # Fallback to priority_skills if filtering removed everything
        if not skills_to_learn:
            skills_to_learn = priority_skills.copy()

        # Create milestones for each skill in skills_to_learn
        milestones = []
        total_hours = 0
        
        for idx, skill in enumerate(skills_to_learn):
            milestone = self._create_milestone(
                skill_name=skill,
                milestone_id=idx + 1,
                difficulty=self._estimate_difficulty(skill),
                resume_text=resume_text,
                job_description=job_description,
                skills_list=skills_to_learn
            )
            milestones.append(milestone)
            total_hours += milestone.estimated_hours
        
        # Set realistic timelines (topological order is preserved)
        milestones = self._schedule_milestones(milestones, weeks_available)
        
        # Calculate estimated weeks
        estimated_weeks = max(
            int((total_hours + 20) / 15),  # Assuming 15 hours/week
            weeks_available
        )
        
        # Compile resources for the learning skills
        resources = self._compile_resources(skills_to_learn)
        
        learning_path = LearningPath(
            title=f"Personalized Learning Path - {len(skills_to_learn)} Skills to Learn",
            description=self._generate_description(skills_to_learn, estimated_weeks),
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
        difficulty: str,
        resume_text: Optional[str] = None,
        job_description: Optional[str] = None,
        skills_list: Optional[List[str]] = None
    ) -> Milestone:
        """
        Create a single learning milestone.
        
        Args:
            skill_name: Name of the skill
            milestone_id: Unique milestone ID
            difficulty: Difficulty level
            resume_text: Optional candidate resume text
            job_description: Optional job description text
            skills_list: Optional list of all skills to learn
            
        Returns:
            Milestone object
        """
        
        # Get resources for this skill (filtered by difficulty)
        resources = self._get_skill_resources(
            skill_name,
            difficulty,
            resume_text=resume_text,
            job_description=job_description
        )
        
        # Calculate estimated hours from resources
        estimated_hours = sum(r.get("hours", 20) for r in resources[:3])
        if estimated_hours == 0:
            hours_map = {
                "beginner": 15,
                "intermediate": 25,
                "advanced": 40,
            }
            estimated_hours = hours_map.get(difficulty, 20)
        
        # Create detailed milestone description
        description = self._create_milestone_description(skill_name, difficulty)

        # Append Groq research summary for the skill (ONLY if use_llm is explicitly True, normally batched)
        if self.llm_client:
            try:
                research = self.research_skill(skill_name, difficulty)
                if research.get('summary'):
                    description += f"\n\n*Research Summary:* {research['summary']}"
                if research.get('structural_role'):
                    description += f"\n*Industry Role:* {research['structural_role']}"
                # Merge Groq-sourced learning assets into resources
                for asset in research.get('learning_assets', []):
                    resources.append({
                        "title": asset.get("title", ""),
                        "url": asset.get("url", ""),
                        "type": asset.get("type", "Resource"),
                        "hours": 10,
                        "difficulty": difficulty,
                        "free": True,
                    })
            except Exception as e:
                print(f"Error fetching research summary: {e}")
        
        # Suggest companion skills based on conditional probabilities
        try:
            companions = self.market_cluster.get_companion_skills([skill_name], threshold=0.6)
            if companions:
                comp_strs = [f"{c['skill']} (P={c['probability']*100:.0f}%)" for c in companions[:3]]
                description += f" \n\n*Suggested companion skills in this market cluster: {', '.join(comp_strs)}.*"
        except Exception as e:
            print(f"Error appending companion skills: {e}")
        
        # Determine prerequisites
        if skills_list:
            prereqs = self._determine_prerequisites(skill_name, skills_list)
        else:
            prereqs = []
            
        milestone = Milestone(
            id=milestone_id,
            title=f"Master {skill_name}",
            description=description,
            skills=[skill_name],
            resources=resources,
            estimated_hours=estimated_hours,
            difficulty=difficulty,
            prerequisites=prereqs,
        )
        
        return milestone
    
    def _get_skill_resources_with_llm(
        self,
        skill_name: str,
        difficulty: str = "beginner",
        resume_text: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate high-quality online courses/resources using Groq API."""
        if not self.llm_client:
            return []
            
        difficulty = difficulty or "beginner"
        
        job_str = f"The learner is targeting this job description: {job_description[:300]}...\n" if job_description else ""
        resume_str = f"The learner's resume context: {resume_text[:300]}...\n" if resume_text else ""
        
        prompt = f"""
You are an expert technical career advisor and educator. Your task is to recommend exactly 3 high-quality online courses, tutorials, or official documentations to help a learner master the skill "{skill_name}" at the "{difficulty}" level.

{job_str}{resume_str}
For each of the 3 recommended resources, you MUST provide:
1. title: The actual name of the course or tutorial (e.g. "React - The Complete Guide (Academind)")
2. url: A real, valid web link (or high-quality search link on platforms like Udemy, Coursera, FreeCodeCamp, Pluralsight, or official docs, e.g. "https://www.coursera.org/search?query=react")
3. type: The resource type (one of: "Course", "Tutorial", "Official Docs", "Practice", "Hands-on Lab")
4. hours: Estimated number of hours to complete (as an integer, e.g., 20)
5. difficulty: "{difficulty}"
6. free: A boolean (true if free, false if paid)

Response Format:
You must return ONLY a JSON array containing the 3 objects, with no markdown code block formatting, no extra explanation text, and no wrapper. Example:
[
  {{
    "title": "React Official Documentation",
    "url": "https://react.dev",
    "type": "Official Docs",
    "hours": 10,
    "difficulty": "{difficulty}",
    "free": true
  }}
]
"""
        try:
            response = self.llm_client.chat.completions.create(
                model=self.config.model if self.config else "llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=500,
            )
            content = response.choices[0].message.content.strip()
            
            # Clean up potential markdown formatting (e.g. ```json ... ```)
            if content.startswith("```"):
                lines = content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                content = "\n".join(lines).strip()
                
            resources = json.loads(content)
            if isinstance(resources, list) and len(resources) > 0:
                # Ensure all elements have required keys
                validated_resources = []
                for res in resources[:4]:
                    if isinstance(res, dict) and "title" in res and "url" in res:
                        validated_resources.append({
                            "title": str(res.get("title")),
                            "url": str(res.get("url")),
                            "type": str(res.get("type", "Course")),
                            "hours": int(res.get("hours", 20)),
                            "difficulty": str(res.get("difficulty", difficulty)),
                            "free": bool(res.get("free", True))
                        })
                if validated_resources:
                    print(f"DEBUG: Successfully generated dynamic resources for {skill_name} via Groq!")
                    return validated_resources
        except Exception as e:
            print(f"Error generating resources via LLM: {e}")
            
        return []

    async def research_skill(
        self,
        skill_name: str,
        difficulty: str = "beginner",
        resume_text: Optional[str] = None,
        job_description: Optional[str] = None,
    ) -> Dict[str, any]:
        """Use LLM to generate structured research output for a skill.

        Returns JSON with:
        - summary: 3‑sentence high‑level conceptual summary.
        - role: description of the tool/skill's structural role in industry.
        - assets: list of three curated live learning assets (title, url, type, hours, free).
        """
        if not self.llm_client:
            # Fallback static response
            return {
                "summary": f"{skill_name} is a key technology used in modern applications.",
                "role": f"It serves as the core component for building scalable systems.",
                "assets": [],
            }
        # Build prompt for research
        prompt = f"""
You are an educational researcher. For the skill **{skill_name}** at difficulty **{difficulty}**, provide the following JSON **without any markdown**:

{{
  "summary": "<3‑sentence high‑level conceptual summary of the missing tool>",
  "role": "<exact structural role it plays in industry architectures>",
  "assets": [
    {{"title": "<asset 1 title>", "url": "<link>", "type": "<Course|Tutorial|Official Docs>", "hours": <int>, "free": <true|false>}},
    {{"title": "<asset 2 title>", "url": "<link>", "type": "<...>", "hours": <int>, "free": <true|false>}},
    {{"title": "<asset 3 title>", "url": "<link>", "type": "<...>", "hours": <int>, "free": <true|false>}}
  ]
}}

Make sure the assets are **live**, high‑star GitHub repos, up‑to‑date official docs, or recent tutorials (2023‑2026). Use real URLs.
"""
        try:
            response = self.llm_client.chat.completions.create(
                model=self.config.model if self.config else "llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=800,
            )
            content = response.choices[0].message.content.strip()
            # Strip possible markdown fences
            if content.startswith("```"):
                lines = content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                content = "\n".join(lines).strip()
            result = json.loads(content)
            # Validate structure
            if not isinstance(result, dict) or "summary" not in result or "role" not in result or "assets" not in result:
                raise ValueError("Invalid research output")
            return result
        except Exception as e:
            print(f"Error in research_skill LLM call: {e}")
            return {"summary": "", "role": "", "assets": []}

    def _get_skill_resources(
        self,
        skill_name: str,
        difficulty: str = None,
        resume_text: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Get curated resources for a skill, filtered by difficulty if specified.
        If LLM is available, use dynamic Groq recommendations.
        
        Args:
            skill_name: Name of the skill
            difficulty: Optional difficulty level to filter by
            resume_text: Optional candidate resume text
            job_description: Optional job description text
            
        Returns:
            List of resource dictionaries with title, URL, type, hours, free flag
        """
        # Try dynamic LLM recommendations first
        if self.llm_client:
            llm_resources = self._get_skill_resources_with_llm(
                skill_name,
                difficulty,
                resume_text=resume_text,
                job_description=job_description
            )
            if llm_resources:
                return llm_resources

        if skill_name in self.RESOURCE_DATABASE:
            resources = self.RESOURCE_DATABASE[skill_name]
            
            # Filter by difficulty if specified and appropriate
            if difficulty:
                difficulty_resources = [r for r in resources if r.get("difficulty") == difficulty]
                if difficulty_resources:
                    resources = difficulty_resources
            
            # Sort by free resources first, then by type preference
            type_priority = {
                "Official Docs": 1,
                "Tutorial": 2,
                "Course": 3,
                "Practice": 4,
                "Hands-on Lab": 5,
                "Project": 6,
                "Article": 7,
                "Interactive Tutorial": 8,
                "Guide": 9,
            }
            
            resources = sorted(
                resources,
                key=lambda r: (not r.get("free", False), type_priority.get(r.get("type", ""), 10))
            )
            
            # Limit to top 4 resources
            return resources[:4]
        else:
            # Generic fallback resource
            return [
                {
                    "title": f"{skill_name} Official Documentation",
                    "url": f"https://www.{skill_name.lower().replace(' ', '')}.org",
                    "type": "Documentation",
                    "hours": 12,
                    "difficulty": difficulty or "beginner",
                    "free": True
                },
                {
                    "title": f"Learn {skill_name} - Udemy",
                    "url": "https://www.udemy.com",
                    "type": "Course",
                    "hours": 30,
                    "difficulty": difficulty or "intermediate",
                    "free": False
                }
            ]
    
    def _create_milestone_description(self, skill_name: str, difficulty: str) -> str:
        """
        Create a detailed milestone description based on skill and difficulty.
        
        Args:
            skill_name: Name of the skill
            difficulty: Difficulty level
            
        Returns:
            Detailed milestone description
        """
        skill_descriptions = {
            "Python": {
                "beginner": "Learn Python fundamentals including syntax, data types, control flow, and functions. Build ability to write clean, readable code.",
                "intermediate": "Master Python libraries (NumPy, Pandas), OOP principles, and advanced data structures. Focus on practical problem-solving.",
                "advanced": "Deep dive into Python performance optimization, async programming, and framework development.",
            },
            "JavaScript": {
                "beginner": "Master JavaScript fundamentals: variables, functions, DOM manipulation, and ES6+ features. Build interactive web experiences.",
                "intermediate": "Learn asynchronous programming, API integration, frameworks (React/Vue), and debugging techniques.",
                "advanced": "Explore advanced patterns, performance optimization, and building scalable JavaScript applications.",
            },
            "React": {
                "beginner": "Understand React fundamentals: components, JSX, props, and state management. Build static to interactive UIs.",
                "intermediate": "Master hooks, context API, routing, and form handling. Build production-ready React applications.",
                "advanced": "Learn performance optimization, custom hooks, and advanced state management patterns.",
            },
            "SQL": {
                "beginner": "Learn relational database concepts and SQL basics: SELECT, WHERE, JOIN, GROUP BY, ORDER BY.",
                "intermediate": "Master complex queries, indexing, optimization, and database design principles.",
                "advanced": "Expert-level query optimization, window functions, and advanced database architecture.",
            },
            "Docker": {
                "beginner": "Understand containerization concepts, Docker basics, images, and containers. Build simple applications.",
                "intermediate": "Master Docker Compose, networking, volumes, and multi-container applications.",
                "advanced": "Learn Kubernetes, orchestration, and production deployment strategies.",
            },
            "AWS": {
                "beginner": "Learn AWS fundamentals: EC2, S3, RDS, and core services. Understand cloud computing concepts.",
                "intermediate": "Master IAM, VPC, auto-scaling, and deploying applications on AWS.",
                "advanced": "Expert-level architecture, optimization, security, and compliance on AWS.",
            },
        }
        
        # Get specific description or create generic one
        if skill_name in skill_descriptions and difficulty in skill_descriptions[skill_name]:
            return skill_descriptions[skill_name][difficulty]
        
        # Generic descriptions
        generic_descriptions = {
            "beginner": f"Learn the fundamentals of {skill_name}. Build a solid foundation and understand core concepts.",
            "intermediate": f"Develop practical proficiency in {skill_name}. Apply knowledge to real-world problems and projects.",
            "advanced": f"Master advanced concepts in {skill_name}. Develop expertise-level skills and best practices.",
        }
        
        return generic_descriptions.get(difficulty, f"Develop comprehensive skills in {skill_name}.")
    
    def _schedule_milestones(
        self,
        milestones: List[Milestone],
        weeks_available: int
    ) -> List[Milestone]:
        """
        Schedule milestones with intelligent sequencing based on difficulty and dependencies.
        
        Args:
            milestones: List of milestones
            weeks_available: Available weeks
            
        Returns:
            Updated milestones with scheduling
        """
        
        # Sort by difficulty: beginner -> intermediate -> advanced
        difficulty_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
        sorted_milestones = sorted(
            milestones,
            key=lambda m: difficulty_order.get(m.difficulty, 1)
        )
        
        start_date = datetime.now() + timedelta(days=1)
        hours_per_week = 15  # Conservative estimate
        cumulative_hours = 0
        
        for milestone in sorted_milestones:
            # Start date based on cumulative hours
            weeks_into_path = cumulative_hours / hours_per_week
            milestone.start_date = start_date + timedelta(weeks=int(weeks_into_path))
            
            # Target completion based on milestone hours
            weeks_to_complete = max(1, int(milestone.estimated_hours / hours_per_week))
            milestone.target_completion = milestone.start_date + timedelta(
                weeks=weeks_to_complete
            )
            
            cumulative_hours += milestone.estimated_hours
        
        return milestones
    
    def _estimate_difficulty(self, skill_name: str) -> str:
        """
        Estimate difficulty of a skill based on complexity.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Difficulty level: beginner, intermediate, or advanced
        """
        advanced_skills = [
            "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
            "Advanced Python", "Distributed Systems", "Kubernetes", "TensorFlow",
            "PyTorch", "Advanced Algorithms", "System Design", "Big Data",
            "Scala", "Spark", "Advanced C++", "Advanced Java"
        ]
        intermediate_skills = [
            "SQL", "Data Visualization", "API Development", "Cloud Computing",
            "Docker", "AWS", "GCP", "Azure", "React", "Vue", "Angular",
            "Node.js", "Express", "TypeScript", "Git", "REST APIs",
            "Microservices", "Databases", "MongoDB", "PostgreSQL"
        ]
        
        skill_lower = skill_name.lower()
        
        # Check advanced skills
        for advanced in advanced_skills:
            if advanced.lower() in skill_lower or skill_lower in advanced.lower():
                return "advanced"
        
        # Check intermediate skills
        for intermediate in intermediate_skills:
            if intermediate.lower() in skill_lower or skill_lower in intermediate.lower():
                return "intermediate"
        
        return "beginner"
    
    def _determine_prerequisites(self, skill_name: str, skills_list: Optional[List[str]] = None) -> List[int]:
        """
        Determine prerequisites for a skill within the context of the generated milestones.
        
        Args:
            skill_name: Name of the skill
            skills_list: Optional list of all skills to learn
            
        Returns:
            List of prerequisite milestone IDs
        """
        if not skills_list:
            return []
            
        canonical = self.skill_dag.find_canonical_name(skill_name)
        if not canonical:
            return []
            
        direct_deps = self.skill_dag.get_direct_dependencies(canonical)
        prereq_ids = []
        
        for dep in direct_deps:
            dep_canonical = self.skill_dag.find_canonical_name(dep) or dep
            for idx, skill in enumerate(skills_list):
                skill_canonical = self.skill_dag.find_canonical_name(skill) or skill
                if skill_canonical.lower() == dep_canonical.lower():
                    prereq_ids.append(idx + 1)
                    break
                    
        return sorted(list(set(prereq_ids)))
    
    def _compile_resources(self, priority_skills: List[str]) -> Dict[str, List[str]]:
        """
        Compile all resources for priority skills with detailed information.
        
        Args:
            priority_skills: List of priority skills
            
        Returns:
            Dictionary mapping skills to resource information
        """
        resources = {}
        
        for skill in priority_skills:
            skill_resources = []
            if skill in self.RESOURCE_DATABASE:
                for resource in self.RESOURCE_DATABASE[skill][:3]:  # Top 3 resources per skill
                    resource_info = f"{resource['title']} ({resource['type']}, {resource['hours']}h"
                    if resource.get('free'):
                        resource_info += ", Free"
                    resource_info += ")"
                    skill_resources.append(resource_info)
            
            if skill_resources:
                resources[skill] = skill_resources
        
        return resources
    
    def _generate_description(self, skills: List[str], weeks: int) -> str:
        """
        Generate a detailed learning path description.
        
        Args:
            skills: List of skills to learn
            weeks: Estimated weeks to complete
            
        Returns:
            Detailed description string
        """
        if not skills:
            return f"A {weeks}-week learning roadmap with structured milestones and curated resources."
        
        skills_str = ", ".join(skills[:-1]) + f", and {skills[-1]}" if len(skills) > 1 else skills[0]
        
        return (
            f"A personalized {weeks}-week learning roadmap focused on mastering: {skills_str}. "
            f"Each milestone includes carefully curated resources (tutorials, courses, practice platforms), "
            f"realistic timelines, and actionable learning objectives. Start with foundations and progressively "
            f"build toward advanced proficiency with hands-on projects and real-world applications."
        )
    
    def generate_dynamic_milestone_title(
        self,
        skill_name: str,
        difficulty: str,
        context: str = None
    ) -> str:
        """
        Generate a dynamic, contextual milestone title using LLM.
        
        Args:
            skill_name: Skill name
            difficulty: Difficulty level
            context: Optional context (resume, job description)
            
        Returns:
            Dynamic milestone title
        """
        if not self.llm_client:
            return f"Master {skill_name} - {difficulty.capitalize()} Level"
        
        prompt = f"""
Generate a SHORT (5-8 words), COMPELLING milestone title for learning {skill_name} at {difficulty} level.

Requirements:
- Action-oriented and motivating
- Include the skill name
- Show progression/achievement
- Professional and specific

{f'Context: {context[:100]}...' if context else ''}

Just provide the title, nothing else:"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.config.model if self.config else "llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=30,
            )
            title = response.choices[0].message.content.strip()
            # Clean up any quotes or extra formatting
            title = title.strip('"\'')
            return title if title else f"Master {skill_name}"
        except Exception as e:
            print(f"Error generating dynamic title: {e}")
            return f"Master {skill_name} - {difficulty.capitalize()} Level"
    
    def generate_learning_style_adjustments(
        self,
        skill_name: str,
        learning_style: str,
        difficulty: str
    ) -> Dict[str, Any]:
        """
        Generate learning style-specific adjustments and recommendations.
        
        Args:
            skill_name: Skill to learn
            learning_style: Type (visual, hands-on, theory, mixed)
            difficulty: Difficulty level
            
        Returns:
            Dict with resource recommendations, tips, and approaches
        """
        style_adjustments = {
            "visual": {
                "recommended_resources": ["tutorials with diagrams", "video courses", "flowcharts", "visual documentation"],
                "approach": "Focus on understanding through visualization and visual examples",
                "tips": ["Draw diagrams to understand concepts", "Use mind maps", "Watch video tutorials", "Look for visual documentation"]
            },
            "hands-on": {
                "recommended_resources": ["coding exercises", "interactive tutorials", "labs", "projects"],
                "approach": "Learn by doing - build things as you learn",
                "tips": ["Start with small projects", "Practice coding daily", "Build incrementally", "Get feedback on your code"]
            },
            "theory": {
                "recommended_resources": ["comprehensive guides", "academic resources", "whitepapers", "official documentation"],
                "approach": "Understand concepts deeply before implementation",
                "tips": ["Study foundational concepts", "Understand the 'why'", "Read specifications", "Take detailed notes"]
            },
            "mixed": {
                "recommended_resources": ["combination of all types", "structured courses", "interactive books", "hybrid platforms"],
                "approach": "Combine visual, hands-on, and theoretical learning",
                "tips": ["Alternate between theory and practice", "Use multiple resources", "Combine different learning methods"]
            }
        }
        
        adjustments = style_adjustments.get(learning_style, style_adjustments["mixed"])
        
        # Add LLM enhancement
        if self.llm_client:
            llm_tips = self.generate_skill_learning_tips(skill_name, difficulty, f"Prefers {learning_style} learning")
            if llm_tips:
                adjustments["llm_personalized_tips"] = llm_tips
        
        return adjustments
    
    def generate_adaptive_difficulty_recommendation(
        self,
        base_difficulty: str,
        user_experience: str,
        skill_complexity: float = 0.5
    ) -> Dict[str, Any]:
        """
        Generate adaptive difficulty recommendations based on user profile.
        
        Args:
            base_difficulty: Original difficulty level
            user_experience: User's experience level
            skill_complexity: Relative complexity (0-1) of the skill
            
        Returns:
            Dict with recommended difficulty and adjustments
        """
        difficulty_adjustments = {
            "beginner": {"time_multiplier": 1.5, "resource_depth": "foundational"},
            "intermediate": {"time_multiplier": 1.0, "resource_depth": "practical"},
            "advanced": {"time_multiplier": 0.7, "resource_depth": "deep"}
        }
        
        experience_levels = ["beginner", "intermediate", "advanced"]
        difficulty_levels = ["beginner", "intermediate", "advanced"]
        
        base_idx = difficulty_levels.index(base_difficulty)
        exp_idx = experience_levels.index(user_experience)
        
        # Adjust difficulty based on experience
        recommended_idx = max(0, min(len(difficulty_levels) - 1, base_idx + (exp_idx - 1)))
        recommended_difficulty = difficulty_levels[recommended_idx]
        
        # Calculate time adjustment
        time_multiplier = difficulty_adjustments[recommended_difficulty]["time_multiplier"]
        if user_experience == "advanced" and base_difficulty != "advanced":
            time_multiplier *= 0.8  # Advanced users move faster
        elif user_experience == "beginner" and base_difficulty != "beginner":
            time_multiplier *= 1.3  # Beginners need more time
        
        return {
            "recommended_difficulty": recommended_difficulty,
            "time_multiplier": round(time_multiplier, 2),
            "resource_depth": difficulty_adjustments[recommended_difficulty]["resource_depth"],
            "explanation": f"Based on your {user_experience} level, {recommended_difficulty} content is recommended"
        }
    
    # ============================================================================
    # DYNAMIC GENERATION METHODS USING GROQ API
    # ============================================================================
    
    def generate_dynamic_milestone_description(
        self,
        skill_name: str,
        difficulty: str,
        resume_text: str = None,
        job_description: str = None
    ) -> str:
        """
        Generate a dynamic, personalized milestone description using Groq API.
        
        Args:
            skill_name: Name of the skill
            difficulty: Difficulty level
            resume_text: Optional resume text for personalization
            job_description: Optional job description for context
            
        Returns:
            Dynamic milestone description
        """
        if not self.llm_client:
            # Fallback to static description
            return self._create_milestone_description(skill_name, difficulty)
        
        context = f"Difficulty: {difficulty}"
        if resume_text:
            context += f"\nResume Preview: {resume_text[:200]}..."
        if job_description:
            context += f"\nJob Role Focus: {job_description[:200]}..."
        
        prompt = f"""
Create a personalized, motivating milestone description for learning {skill_name} at {difficulty} level.

{context}

Requirements:
- 2-3 sentences
- Specific learning objectives
- Real-world application context
- Motivating and practical tone
- Include concrete skills to acquire

Milestone Description:"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.config.model if self.config else "llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150,
            )
            description = response.choices[0].message.content.strip()
            return description if description else self._create_milestone_description(skill_name, difficulty)
        except Exception as e:
            print(f"Error generating dynamic description: {e}")
            return self._create_milestone_description(skill_name, difficulty)
    
    def generate_dynamic_learning_path_description(
        self,
        skills: List[str],
        weeks: int,
        resume_text: str = None,
        job_description: str = None,
        overall_match: float = None
    ) -> str:
        """
        Generate a dynamic, personalized learning path description using Groq.
        
        Args:
            skills: Priority skills to learn
            weeks: Estimated weeks
            resume_text: Optional resume context
            job_description: Optional job context
            overall_match: Optional match score
            
        Returns:
            Dynamic learning path description
        """
        if not self.llm_client or not skills:
            return self._generate_description(skills, weeks)
        
        skills_str = ", ".join(skills)
        context = f"Target skills: {skills_str}\nEstimated timeframe: {weeks} weeks"
        
        if overall_match:
            context += f"\nCurrent job match: {overall_match:.1f}%"
        if resume_text:
            context += f"\nCandidate summary: {resume_text[:150]}..."
        if job_description:
            context += f"\nTarget role: {job_description[:150]}..."
        
        prompt = f"""
Create an engaging, personalized learning path description that motivates the learner.

{context}

Requirements:
- 3-4 sentences
- Explain the strategic value of learning these skills
- Include expected outcomes and benefits
- Mention progression from basics to advanced
- Professional and encouraging tone

Learning Path Description:"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.config.model if self.config else "llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=250,
            )
            description = response.choices[0].message.content.strip()
            return description if description else self._generate_description(skills, weeks)
        except Exception as e:
            print(f"Error generating dynamic path description: {e}")
            return self._generate_description(skills, weeks)
    
    def generate_personalized_resource_recommendations(
        self,
        skill_name: str,
        difficulty: str,
        learning_style: str = None
    ) -> List[Dict[str, str]]:
        """
        Generate personalized resource recommendations using Groq.
        
        Args:
            skill_name: Skill to find resources for
            difficulty: Difficulty level
            learning_style: Optional learning style (visual, hands-on, theory, etc.)
            
        Returns:
            List of personalized resource recommendations
        """
        # First get base resources from database
        base_resources = self._get_skill_resources(skill_name, difficulty)
        
        if not self.llm_client or not base_resources:
            return base_resources
        
        resources_text = json.dumps(base_resources, indent=2)
        learning_style_prompt = f"\nLearner profile: Prefers {learning_style} learning" if learning_style else ""
        
        prompt = f"""
Given these resources for learning {skill_name} at {difficulty} level:
{resources_text}

{learning_style_prompt}

Analyze and rank these resources by effectiveness. Provide:
1. Top 2 most recommended resources (by title and type)
2. Brief reason why each is effective (1 sentence each)
3. Suggested learning order

Format as JSON:
{{
  "recommended": [
    {{"title": "...", "type": "...", "reason": "..."}},
    {{"title": "...", "type": "...", "reason": "..."}}
  ],
  "learning_order": ["first resource type", "second resource type"]
}}"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.config.model if self.config else "llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=300,
            )
            response_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    recommendations_json = json.loads(response_text[json_start:json_end])
                    if "recommended" in recommendations_json:
                        return base_resources  # Return enhanced with Groq insights
            except:
                pass
            
            return base_resources
        except Exception as e:
            print(f"Error generating personalized resources: {e}")
            return base_resources
    
    def research_skill(self, skill_name: str, difficulty: str) -> Dict[str, Any]:
        """
        Use Groq LLM to research a skill and return structured JSON:
        - summary: 3-sentence conceptual summary
        - structural_role: its role in industry architectures
        - learning_assets: 3 curated, live learning links
        Falls back to empty dict when no LLM client is available.
        """
        if not self.llm_client:
            return {}

        prompt = f"""You are an educational researcher. For the skill "{skill_name}" at {difficulty} level, return ONLY valid JSON (no markdown fences) with these keys:
{{
  "summary": "<3-sentence high-level conceptual summary of {skill_name}>",
  "structural_role": "<1-2 sentences on the exact structural role {skill_name} plays in modern industry architectures>",
  "learning_assets": [
    {{"title": "...", "url": "...", "type": "..."}},
    {{"title": "...", "url": "...", "type": "..."}},
    {{"title": "...", "url": "...", "type": "..."}}
  ]
}}
Use only real, currently live URLs from official docs, GitHub, or reputable course platforms. Current year is 2026."""

        try:
            response = self.llm_client.chat.completions.create(
                model=self.config.model if self.config else "llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=400,
            )
            text = response.choices[0].message.content.strip()
            # Extract JSON from response
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(text[json_start:json_end])
        except Exception as e:
            print(f"research_skill error for {skill_name}: {e}")

        return {}
    
    # ============================================================================
    # ADVANCED DYNAMIC FEATURES FOR ADAPTIVE LEARNING PATHS
    # ============================================================================
    
    def generate_adaptive_path(
        self,
        feedback: FeedbackResult,
        priority_skills: List[str],
        user_profile: UserProfile,
        weeks_available: int = 12,
        resume_context: str = None,
        job_context: str = None
    ) -> LearningPath:
        """
        Generate an adaptive learning path based on user profile and context.
        
        Args:
            feedback: FeedbackResult from LLM analysis
            priority_skills: List of skills to prioritize
            user_profile: User's learning profile (experience, style, availability)
            weeks_available: Available weeks to complete path
            resume_context: Optional resume text for personalization
            job_context: Optional job description for context
            
        Returns:
            Fully adaptive LearningPath with personalized milestones
        """
        # Generate base path without iterative LLM calls to save rate limits
        temp_client = self.llm_client
        self.llm_client = None
        try:
            path = self.generate_path(
                feedback, 
                priority_skills, 
                weeks_available, 
                resume_text=resume_context, 
                job_description=job_context
            )
        finally:
            self.llm_client = temp_client
        
        # Adapt based on user profile
        path.user_profile = user_profile
        path.adaptivity_score = self._calculate_adaptivity_score(path, user_profile)
        path.recommendation_engine_used = "llm" if self.llm_client else "hybrid"
        
        # BATCH LLM GENERATION: Fetch all dynamic content in ONE call
        if self.llm_client:
            # Get actual skills from the generated milestones to ensure LLM generates data for all of them
            actual_skills = [m.skills[0] for m in path.milestones if m.skills]
            if not actual_skills:
                actual_skills = priority_skills
                
            batched_data = self._batch_generate_adaptive_path_llm(
                actual_skills, user_profile, job_context, resume_context
            )
        else:
            batched_data = {}
            
        # Adjust milestones based on batched data & user profile
        adapted_milestones = []
        for milestone in path.milestones:
            adapted_milestone = self._adapt_milestone_with_batch(
                milestone,
                user_profile,
                batched_data
            )
            adapted_milestones.append(adapted_milestone)
        
        path.milestones = adapted_milestones
        
        # Regenerate times based on availability
        path.milestones = self._reschedule_by_availability(
            path.milestones,
            user_profile.availability_hours_per_week
        )
        
        # Update path description with dynamic content
        if self.llm_client and batched_data:
            path.description = "A fully personalized, adaptive learning roadmap tailored to your experience, preferred learning style, and specific career goals."
        
        return path
        
    def _batch_generate_adaptive_path_llm(self, priority_skills: List[str], user_profile: UserProfile, job_context: str, resume_context: str) -> Dict[str, Any]:
        """One giant LLM call to get research, resources, and projects for ALL skills."""
        if not self.llm_client:
            return {}
            
        skills_str = ", ".join(priority_skills)
        prompt = f"""
You are an expert career advisor and technical educator building a highly customized, adaptive learning path.
The learner wants to master the following skills: {skills_str}.
User Profile: Experience: {user_profile.experience_level}, Style: {user_profile.learning_style}, Budget: {user_profile.budget}.
Job Context: {job_context[:300] if job_context else 'N/A'}
Resume Context: {resume_context[:300] if resume_context else 'N/A'}

For each skill in the list, provide:
1. "description": A dynamic, encouraging milestone description (3-4 sentences).
2. "difficulty": Estimated difficulty level (beginner, intermediate, advanced) based on their experience.
3. "estimated_hours": Integer hours to complete.
4. "resources": A list of exactly 3 curated learning resources (courses, docs) formatted with title, url, type, hours, free. Make sure urls are real or high-quality search links.
5. "projects": A list of 1-2 hands-on projects to practice the skill.
6. "success_criteria": A list of 2-3 measurable outcomes.

Respond ONLY with a valid JSON object where the keys are the exact skill names.
Example format:
{{
  "Python": {{
    "title": "Mastering Python",
    "description": "...",
    "difficulty": "intermediate",
    "estimated_hours": 20,
    "resources": [
      {{"title": "...", "url": "...", "type": "Course", "hours": 10, "free": true}}
    ],
    "projects": [
      {{"title": "...", "description": "..."}}
    ],
    "success_criteria": ["...", "..."]
  }}
}}
"""
        try:
            completion = self.llm_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a senior technical educator. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                model=self.config.model,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            response_text = completion.choices[0].message.content
            return json.loads(response_text)
        except Exception as e:
            print(f"Error in batch generation: {e}")
            return {}

    def _adapt_milestone_with_batch(
        self,
        milestone: Milestone,
        user_profile: UserProfile,
        batched_data: Dict[str, Any]
    ) -> Milestone:
        """Adapt a milestone using the batched LLM data."""
        adapted = milestone
        skill_name = adapted.skills[0] if adapted.skills else "General"
        
        # Check if we have batched LLM data for this skill
        data = batched_data.get(skill_name, {})
        
        if data:
            if "title" in data: adapted.title = data["title"]
            if "description" in data: adapted.description = data["description"]
            if "difficulty" in data: adapted.difficulty = data["difficulty"]
            if "estimated_hours" in data: adapted.estimated_hours = int(data["estimated_hours"])
            if "resources" in data and data["resources"]: adapted.resources = data["resources"]
            if "projects" in data and data["projects"]: adapted.projects = data["projects"]
            if "success_criteria" in data and data["success_criteria"]: adapted.success_criteria = data["success_criteria"]
        else:
            # Fallback scaling if LLM fails
            adapted.estimated_hours = int(adapted.estimated_hours * 1.2)
            
        # Filter resources by user preferences (if budget strict or preferred types)
        if user_profile.preferred_resource_types:
            filtered_resources = [
                r for r in adapted.resources
                if r.get("type") in user_profile.preferred_resource_types
            ]
            if filtered_resources:
                adapted.resources = filtered_resources
                
        if user_profile.budget == "free":
            adapted.resources = [r for r in adapted.resources if r.get("free", False)]
            
        return adapted    
    def _adapt_milestone_to_profile(
        self,
        milestone: Milestone,
        user_profile: UserProfile,
        resume_context: str = None,
        job_context: str = None
    ) -> Milestone:
        """
        Adapt a milestone to match user's learning profile and preferences.
        
        Args:
            milestone: Original milestone
            user_profile: User learning profile
            resume_context: Resume text for personalization
            job_context: Job description for context
            
        Returns:
            Adapted milestone with personalized content
        """
        adapted = milestone
        skill_name = adapted.skills[0] if adapted.skills else "General"
        
        # Generate dynamic, contextual title
        adapted.title = self.generate_dynamic_milestone_title(
            skill_name,
            adapted.difficulty,
            job_context or resume_context
        )
        
        # Apply adaptive difficulty recommendations
        difficulty_rec = self.generate_adaptive_difficulty_recommendation(
            adapted.difficulty,
            user_profile.experience_level,
            skill_complexity=0.6
        )
        adapted.difficulty = difficulty_rec["recommended_difficulty"]
        adapted.estimated_hours = int(adapted.estimated_hours * difficulty_rec["time_multiplier"])
        
        # Filter resources by user preferences
        if user_profile.preferred_resource_types:
            adapted.resources = [
                r for r in adapted.resources
                if r.get("type") in user_profile.preferred_resource_types
            ] or adapted.resources[:3]  # Fallback if no matches
        
        # Filter free resources if budget is "free"
        if user_profile.budget == "free":
            adapted.resources = [r for r in adapted.resources if r.get("free", False)] or adapted.resources[:2]
        
        # Add learning style-specific resources via LLM if available
        if self.llm_client and user_profile.learning_style:
            adapted.resources = self.generate_personalized_resource_recommendations(
                skill_name,
                adapted.difficulty,
                user_profile.learning_style
            ) or adapted.resources
        
        # Add learning style adjustments for context
        style_adjustments = self.generate_learning_style_adjustments(
            skill_name,
            user_profile.learning_style,
            adapted.difficulty
        )
        # Store as metadata for frontend
        adapted.resources.append({
            "title": "💡 Learning Style Tips",
            "url": "",
            "type": "learning_tips",
            "description": "\n".join(style_adjustments.get("tips", []))
        })
        
        # Add success criteria dynamically with job context
        adapted.success_criteria = self._generate_success_criteria(
            skill_name,
            adapted.difficulty,
            user_profile.experience_level,
            job_context
        )
        
        # Add hands-on projects
        adapted.projects = self._generate_projects(
            adapted.skills[0] if adapted.skills else "General",
            adapted.difficulty
        )
        
        # Generate dynamic description if LLM available
        if self.llm_client:
            adapted.description = self.generate_dynamic_milestone_description(
                adapted.skills[0] if adapted.skills else "General",
                adapted.difficulty,
                resume_context,
                job_context
            )
        
        return adapted
    
    def _calculate_adaptivity_score(self, path: LearningPath, user_profile: UserProfile) -> float:
        """
        Calculate how well the path is adapted to user preferences (0-1).
        
        Args:
            path: Learning path
            user_profile: User profile
            
        Returns:
            Adaptivity score from 0 to 1
        """
        score = 0.5  # Base score
        
        # Check if resources match learning style preference
        if user_profile.preferred_resource_types:
            matching = 0
            total = 0
            for milestone in path.milestones:
                for resource in milestone.resources:
                    total += 1
                    if resource.get("type") in user_profile.preferred_resource_types:
                        matching += 1
            
            if total > 0:
                score += (matching / total) * 0.3
        
        # Check budget alignment
        if user_profile.budget == "free":
            free_resources = sum(
                1 for milestone in path.milestones
                for resource in milestone.resources
                if resource.get("free", False)
            )
            total_resources = sum(len(m.resources) for m in path.milestones)
            if total_resources > 0:
                score += (free_resources / total_resources) * 0.2
        else:
            score += 0.2  # Full score if budget is flexible
        
        # Check if total hours fit availability
        weekly_hours_needed = path.total_hours / (path.estimated_weeks or 1)
        if weekly_hours_needed <= user_profile.availability_hours_per_week:
            score += 0.3
        
        return min(1.0, score)
    
    def _reschedule_by_availability(
        self,
        milestones: List[Milestone],
        availability_hours_per_week: int
    ) -> List[Milestone]:
        """
        Reschedule milestones based on actual user availability.
        
        Args:
            milestones: List of milestones
            availability_hours_per_week: Hours available per week
            
        Returns:
            Rescheduled milestones
        """
        start_date = datetime.now() + timedelta(days=1)
        cumulative_hours = 0
        
        for milestone in milestones:
            weeks_into_path = cumulative_hours / max(availability_hours_per_week, 1)
            milestone.start_date = start_date + timedelta(weeks=int(weeks_into_path))
            
            weeks_to_complete = max(1, int(milestone.estimated_hours / max(availability_hours_per_week, 1)))
            milestone.target_completion = milestone.start_date + timedelta(weeks=weeks_to_complete)
            
            cumulative_hours += milestone.estimated_hours
        
        return milestones
    
    def _generate_success_criteria(
        self,
        skill_name: str,
        difficulty: str,
        user_level: str,
        job_context: str = None
    ) -> List[str]:
        """
        Generate measurable success criteria for a milestone (with LLM enhancement).
        
        Args:
            skill_name: Skill name
            difficulty: Difficulty level
            user_level: User's experience level
            job_context: Optional job description for context
            
        Returns:
            List of success criteria
        """
        criteria_templates = {
            "Python": {
                "beginner": [
                    "Write and execute 10+ standalone Python scripts",
                    "Understand and use Python data types and control structures",
                    "Create functions and use modules effectively",
                    "Debug basic Python errors independently"
                ],
                "intermediate": [
                    "Build a full Python application with OOP principles",
                    "Use NumPy/Pandas effectively for data manipulation",
                    "Implement design patterns and best practices",
                    "Write unit tests for your code"
                ],
                "advanced": [
                    "Optimize Python code for performance",
                    "Implement async/await patterns",
                    "Contribute to open-source Python projects",
                    "Design scalable Python systems"
                ]
            },
            "JavaScript": {
                "beginner": [
                    "Build interactive web pages with vanilla JavaScript",
                    "Understand DOM manipulation and events",
                    "Use ES6+ features in daily coding",
                    "Create JavaScript applications with 500+ lines of code"
                ],
                "intermediate": [
                    "Build a full-stack web application",
                    "Use async/await and promises effectively",
                    "Implement complex state management",
                    "Optimize JavaScript performance"
                ],
                "advanced": [
                    "Build performant applications at scale",
                    "Contribute to JavaScript frameworks",
                    "Implement complex architectural patterns",
                    "Optimize bundle size and performance"
                ]
            },
            "React": {
                "beginner": [
                    "Build 3+ React components with hooks",
                    "Manage component state and props correctly",
                    "Handle form inputs and submissions",
                    "Understand React lifecycle and rendering"
                ],
                "intermediate": [
                    "Build production-ready React applications",
                    "Implement complex state management (Redux/Context)",
                    "Optimize component performance",
                    "Implement routing and lazy loading"
                ],
                "advanced": [
                    "Design scalable React architectures",
                    "Create reusable component libraries",
                    "Implement advanced patterns (render props, compounds)",
                    "Mentor other React developers"
                ]
            }
        }
        
        # Return skill-specific criteria if available
        base_criteria = criteria_templates.get(skill_name, {}).get(difficulty, None)
        if base_criteria is None:
            # Generate generic criteria
            base_criteria = self._get_generic_success_criteria(skill_name, difficulty)
        
        # Enhance with LLM if available and job context is provided
        if self.llm_client and job_context:
            enhanced_criteria = self._enhance_success_criteria_with_llm(
                skill_name,
                difficulty,
                base_criteria,
                job_context
            )
            if enhanced_criteria:
                return enhanced_criteria
        
        return base_criteria
    
    def _get_generic_success_criteria(self, skill_name: str, difficulty: str) -> List[str]:
        """Generate generic success criteria for any skill."""
        generic = {
            "beginner": [
                f"Complete all foundational tutorials for {skill_name}",
                f"Build 2-3 small projects using {skill_name}",
                f"Solve 20+ practice problems in {skill_name}",
                f"Understand and explain core concepts of {skill_name}"
            ],
            "intermediate": [
                f"Build a complete application with {skill_name}",
                f"Implement best practices and design patterns",
                f"Solve complex problems using {skill_name}",
                f"Review and contribute to open-source {skill_name} projects"
            ],
            "advanced": [
                f"Build production-grade {skill_name} solutions",
                f"Optimize performance and scalability",
                f"Mentor others in {skill_name}",
                f"Contribute significantly to {skill_name} ecosystem"
            ]
        }
        return generic.get(difficulty, generic["intermediate"])
    
    def _enhance_success_criteria_with_llm(
        self,
        skill_name: str,
        difficulty: str,
        base_criteria: List[str],
        job_context: str
    ) -> List[str]:
        """
        Enhance success criteria using LLM to be more job-specific.
        
        Args:
            skill_name: Skill name
            difficulty: Difficulty level
            base_criteria: Original criteria
            job_context: Job description for context
            
        Returns:
            Enhanced, job-specific success criteria
        """
        base_text = "\n".join([f"- {c}" for c in base_criteria])
        
        prompt = f"""
Given these base success criteria for mastering {skill_name} at {difficulty} level:
{base_text}

And this job context:
{job_context[:300]}...

Generate 4-5 MORE SPECIFIC, JOB-RELEVANT success criteria that:
1. Are measurable and verifiable
2. Directly relate to the job requirements
3. Include hands-on deliverables
4. Show practical competency
5. Are achievable within the timeframe

Format as a numbered list:"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.config.model if self.config else "llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300,
            )
            response_text = response.choices[0].message.content.strip()
            
            # Extract numbered criteria
            criteria = []
            for line in response_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering and formatting
                    clean = line.lstrip('0123456789.-) ').strip()
                    if clean:
                        criteria.append(clean)
            
            return criteria if criteria else base_criteria
        except Exception as e:
            print(f"Error enhancing criteria with LLM: {e}")
            return base_criteria
    
    def _generate_projects(self, skill_name: str, difficulty: str, user_context: str = None) -> List[Dict[str, str]]:
        """
        Generate hands-on projects for a skill (static base + dynamic enhancement via LLM).
        
        Args:
            skill_name: Skill name
            difficulty: Difficulty level
            user_context: Optional user background for personalization
            
        Returns:
            List of project suggestions with descriptions
        """
        # Base static projects
        base_projects = {
            "Python": {
                "beginner": [
                    {"title": "Build a CLI Todo Application", "description": "Create a command-line todo manager with basic CRUD operations"},
                    {"title": "Web Scraper Project", "description": "Scrape data from a website and store it in a database"},
                ],
                "intermediate": [
                    {"title": "Data Analysis Project", "description": "Analyze real-world dataset using Pandas and Matplotlib"},
                    {"title": "REST API with Flask", "description": "Build a complete REST API with authentication and database"},
                ],
                "advanced": [
                    {"title": "ML Model Pipeline", "description": "Build end-to-end machine learning pipeline with model training and deployment"},
                    {"title": "Async Web Scraper", "description": "Create high-performance async scraper with caching and error handling"},
                ]
            },
            "JavaScript": {
                "beginner": [
                    {"title": "Interactive Todo App", "description": "Build a todo app with local storage and DOM manipulation"},
                    {"title": "Weather App", "description": "Fetch weather data from API and display dynamically"},
                ],
                "intermediate": [
                    {"title": "Real-time Chat App", "description": "Build a chat application with WebSockets"},
                    {"title": "E-commerce Frontend", "description": "Create a product browsing and shopping cart system"},
                ],
                "advanced": [
                    {"title": "Full-stack Web Application", "description": "Build complete web app with backend, database, and deployment"},
                    {"title": "Browser-based IDE", "description": "Create a code editor with syntax highlighting and execution"},
                ]
            },
            "React": {
                "beginner": [
                    {"title": "Personal Portfolio", "description": "Build a portfolio website using React"},
                    {"title": "Recipe Search App", "description": "Search and display recipes from an API"},
                ],
                "intermediate": [
                    {"title": "E-commerce Platform", "description": "Full e-commerce app with cart, checkout, and payments"},
                    {"title": "Social Media Feed", "description": "Build a feed app with real-time updates"},
                ],
                "advanced": [
                    {"title": "Collaborative Editor", "description": "Build a real-time collaborative document editor"},
                    {"title": "Data Dashboard", "description": "Create an interactive data visualization dashboard"},
                ]
            }
        }
        
        # Get base projects
        if skill_name in base_projects and difficulty in base_projects[skill_name]:
            projects = base_projects[skill_name][difficulty]
        else:
            projects = [
                {"title": f"Beginner {skill_name} Project", "description": f"Start with a simple project to apply {skill_name} fundamentals"},
                {"title": f"Intermediate {skill_name} Project", "description": f"Build a more complex project combining multiple {skill_name} concepts"},
            ]
        
        # Enhance with LLM if available
        if self.llm_client and user_context:
            return self._enhance_projects_with_llm(skill_name, difficulty, projects, user_context)
        
        return projects
    
    def _enhance_projects_with_llm(
        self,
        skill_name: str,
        difficulty: str,
        base_projects: List[Dict[str, str]],
        user_context: str
    ) -> List[Dict[str, str]]:
        """
        Enhance project suggestions using LLM for more relevance to user context.
        
        Args:
            skill_name: Skill name
            difficulty: Difficulty level
            base_projects: Original project list
            user_context: User background/context
            
        Returns:
            Enhanced project list with context-aware descriptions
        """
        base_projects_text = json.dumps(base_projects, indent=2)
        
        prompt = f"""
Given these base projects for learning {skill_name}:
{base_projects_text}

User context: {user_context}

Enhance these projects with MORE SPECIFIC, PRACTICAL project ideas that better fit the user's context.
Generate 2-3 alternative project suggestions that are:
1. Directly relevant to their background/goals
2. Progressively challenging
3. Portfolio-worthy outcomes
4. Include real-world applications

Format as JSON array:
[
  {{"title": "...", "description": "...", "real_world_value": "..."}},
  ...
]"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.config.model if self.config else "llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=400,
            )
            response_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON
            try:
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                if json_start >= 0 and json_end > json_start:
                    enhanced_projects = json.loads(response_text[json_start:json_end])
                    # Merge with base projects
                    combined = base_projects + [
                        {k: v for k, v in p.items() if k in ['title', 'description']}
                        for p in enhanced_projects
                    ]
                    return combined[:3]  # Return top 3
            except:
                pass
        except Exception as e:
            print(f"Error enhancing projects with LLM: {e}")
        
        return base_projects
    
    def update_milestone_progress(
        self,
        learning_path: LearningPath,
        milestone_id: int,
        progress_percentage: int,
        is_completed: bool = False
    ) -> LearningPath:
        """
        Update progress on a specific milestone and overall path.
        
        Args:
            learning_path: The learning path to update
            milestone_id: ID of the milestone to update
            progress_percentage: Progress from 0-100
            is_completed: Whether milestone is completed
            
        Returns:
            Updated learning path
        """
        for milestone in learning_path.milestones:
            if milestone.id == milestone_id:
                milestone.progress_percentage = min(100, max(0, progress_percentage))
                milestone.is_completed = is_completed or progress_percentage >= 100
                break
        
        # Calculate overall progress
        total_progress = sum(m.progress_percentage for m in learning_path.milestones)
        learning_path.overall_progress = int(total_progress / len(learning_path.milestones)) if learning_path.milestones else 0
        
        return learning_path
    
    def generate_next_actions(
        self,
        learning_path: LearningPath,
        current_milestone_id: int
    ) -> List[Dict[str, str]]:
        """
        Generate dynamic next action recommendations based on current progress.
        
        Args:
            learning_path: Current learning path
            current_milestone_id: Current milestone ID
            
        Returns:
            List of next action recommendations
        """
        actions = []
        
        for milestone in learning_path.milestones:
            if milestone.id == current_milestone_id:
                # Generate recommendations for next steps
                if self.llm_client:
                    try:
                        prompt = f"""
Based on the learner completing {milestone.title} in {milestone.skills[0] if milestone.skills else 'their skill'},
provide 3 specific, actionable next steps to consolidate learning and move forward.

Milestone: {milestone.title}
Skills: {', '.join(milestone.skills)}
Resources completed: {len(milestone.resources)} resources

Format as JSON:
{{
  "actions": [
    {{"action": "specific action 1", "reason": "why this helps", "time_estimate": "X hours"}},
    {{"action": "specific action 2", "reason": "why this helps", "time_estimate": "X hours"}},
    {{"action": "specific action 3", "reason": "why this helps", "time_estimate": "X hours"}}
  ]
}}"""
                        response = self.llm_client.chat.completions.create(
                            model=self.config.model if self.config else "llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.7,
                            max_tokens=400,
                        )
                        response_text = response.choices[0].message.content.strip()
                        
                        try:
                            json_start = response_text.find('{')
                            json_end = response_text.rfind('}') + 1
                            if json_start >= 0 and json_end > json_start:
                                actions_json = json.loads(response_text[json_start:json_end])
                                if "actions" in actions_json:
                                    return actions_json["actions"]
                        except:
                            pass
                    except Exception as e:
                        print(f"Error generating next actions: {e}")
                
                # Fallback to generic actions
                actions = [
                    {
                        "action": "Build a small project applying the skills",
                        "reason": "Consolidate knowledge through practical application",
                        "time_estimate": "5-10 hours"
                    },
                    {
                        "action": "Review and refactor previous projects",
                        "reason": "Improve code quality and best practices",
                        "time_estimate": "3-5 hours"
                    },
                    {
                        "action": "Participate in coding communities or challenges",
                        "reason": "Learn from others and get feedback",
                        "time_estimate": "2-3 hours/week"
                    }
                ]
                break
        
        return actions
    
    def generate_skill_learning_tips(
        self,
        skill_name: str,
        difficulty: str,
        background: str = None
    ) -> str:
        """
        Generate personalized learning tips for a skill using Groq.
        
        Args:
            skill_name: Skill to learn
            difficulty: Difficulty level
            background: Optional background/experience level
            
        Returns:
            Personalized learning tips
        """
        if not self.llm_client:
            return ""
        
        context = f"Skill: {skill_name}, Difficulty: {difficulty}"
        if background:
            context += f"\nBackground: {background}"
        
        prompt = f"""
Provide 3-4 specific, actionable learning tips for mastering {skill_name} at {difficulty} level.

{context}

Requirements:
- Practical and immediately applicable
- Address common pitfalls
- Include time management strategies
- Mention best practices

Format as a short paragraph with clear, numbered tips."""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.config.model if self.config else "llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200,
            )
            tips = response.choices[0].message.content.strip()
            return tips
        except Exception as e:
            print(f"Error generating learning tips: {e}")
            return ""


def generate_learning_path(
    feedback: FeedbackResult,
    priority_skills: List[str],
    weeks_available: int = 12,
    config: Optional[LLMConfig] = None
) -> LearningPath:
    """
    Convenience function to generate learning path with optional dynamic generation.
    
    Args:
        feedback: FeedbackResult from LLM
        priority_skills: List of priority skills
        weeks_available: Time available for learning
        config: Optional LLMConfig for dynamic generation
        
    Returns:
        LearningPath object
    """
    generator = LearningPathGenerator(config)
    return generator.generate_path(feedback, priority_skills, weeks_available)
