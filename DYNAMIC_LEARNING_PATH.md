# Dynamic Learning Path System

## Overview

The Resume-Insight AI system now includes a fully **dynamic and adaptive learning path generation** system that personalizes learning recommendations based on individual user profiles, learning styles, and constraints.

## Key Features

### 1. **Adaptive Learning Paths**
Generates personalized learning roadmaps that adjust to:
- **Experience Level**: Beginner, Intermediate, or Advanced
- **Learning Style**: Visual, Hands-on, Theory, or Mixed
- **Time Availability**: Customizable hours per week
- **Budget Constraints**: Free, Limited, or Flexible
- **Resource Preferences**: Preferred resource types (docs, tutorials, courses, practice, etc.)

### 2. **Dynamic Milestone Generation**
Each milestone includes:
- **Personalized Descriptions**: Generated using LLM (Groq/OpenAI) based on user context
- **Success Criteria**: Measurable learning outcomes
- **Hands-on Projects**: Real-world project suggestions
- **Adaptive Difficulty**: Adjusts based on user experience level
- **Contextual Resources**: Filtered and ranked by user preferences

### 3. **Progress Tracking**
- Track progress on individual milestones (0-100%)
- Automatic calculation of overall learning path progress
- Mark milestones as completed
- Historical progress tracking

### 4. **Next Action Recommendations**
- Dynamically generated suggestions for next learning steps
- Context-aware recommendations based on completed milestones
- LLM-powered actionable next steps with time estimates

### 5. **Personalized Resource Recommendations**
- Intelligent resource ranking based on learning style
- Budget-conscious filtering
- Type preference matching
- Free vs. paid resource prioritization

## Data Models

### UserProfile
```python
@dataclass
class UserProfile:
    experience_level: str  # "beginner", "intermediate", "advanced"
    learning_style: str    # "visual", "hands-on", "theory", "mixed"
    availability_hours_per_week: int = 15
    preferred_resource_types: List[str] = []  # e.g., ["Course", "Practice", "Tutorial"]
    budget: str = "free"   # "free", "limited", "flexible"
    timezone: Optional[str] = None
    preferred_languages: List[str] = []
```

### Enhanced Milestone
```python
@dataclass
class Milestone:
    id: int
    title: str
    description: str        # Now dynamically generated
    skills: List[str]
    resources: List[Dict]   # Personalized and ranked
    estimated_hours: int
    difficulty: str
    prerequisites: List[int]
    start_date: Optional[datetime]
    target_completion: Optional[datetime]
    success_criteria: List[str]      # NEW: Measurable outcomes
    projects: List[Dict[str, str]]   # NEW: Hands-on projects
    progress_percentage: int = 0     # NEW: Track progress
    is_completed: bool = False
```

### Enhanced LearningPath
```python
@dataclass
class LearningPath:
    title: str
    description: str        # Dynamically generated
    total_hours: int
    estimated_weeks: int
    milestones: List[Milestone]
    priority_skills: List[str]
    resources: Dict[str, List[str]]
    created_date: datetime
    user_profile: Optional[UserProfile] = None  # NEW
    overall_progress: int = 0                    # NEW: 0-100%
    adaptivity_score: float = 0.0                # NEW: How well adapted
    recommendation_engine_used: str = "static"   # NEW: "static", "llm", "hybrid"
```

## API Endpoints

### 1. Generate Adaptive Learning Path
```http
POST /api/learning-path/adaptive

Request:
{
  "analysis_id": "uuid",
  "user_profile": {
    "experience_level": "intermediate",
    "learning_style": "hands-on",
    "availability_hours_per_week": 20,
    "preferred_resource_types": ["Course", "Practice"],
    "budget": "free"
  }
}

Response:
{
  "analysis_id": "uuid",
  "learning_path": {
    "title": "Personalized Learning Path",
    "description": "Dynamic description based on user and job context",
    "total_hours": 150,
    "estimated_weeks": 10,
    "overall_progress": 0,
    "adaptivity_score": 0.85,
    "recommendation_engine": "llm",
    "milestones": [
      {
        "id": 1,
        "title": "Master Python",
        "description": "Dynamic, personalized description",
        "skills": ["Python"],
        "estimated_hours": 40,
        "difficulty": "beginner",
        "start_date": "2024-01-15",
        "target_completion": "2024-02-15",
        "success_criteria": [
          "Write 10+ standalone Python scripts",
          "Understand and use Python data types",
          "Create functions and use modules"
        ],
        "projects": [
          {
            "title": "Build a CLI Todo Application",
            "description": "Create a command-line todo manager"
          }
        ],
        "resources": [
          {
            "title": "Python Official Documentation",
            "url": "https://docs.python.org/3/",
            "type": "Official Docs",
            "hours": 15,
            "free": true
          }
        ],
        "progress_percentage": 0
      }
    ],
    "priority_skills": ["Python", "JavaScript", "React"]
  }
}
```

### 2. Update Milestone Progress
```http
POST /api/learning-path/{analysis_id}/milestone-progress

Request:
{
  "milestone_id": 1,
  "progress_percentage": 50,
  "is_completed": false
}

Response:
{
  "analysis_id": "uuid",
  "milestone_id": 1,
  "progress_percentage": 50,
  "is_completed": false,
  "overall_progress": 25,
  "message": "Milestone progress updated successfully"
}
```

### 3. Get Next Actions
```http
GET /api/learning-path/{analysis_id}/next-actions?current_milestone_id=1

Response:
{
  "analysis_id": "uuid",
  "current_milestone_id": 1,
  "next_actions": [
    {
      "action": "Build a small project applying the skills",
      "reason": "Consolidate knowledge through practical application",
      "time_estimate": "5-10 hours"
    },
    {
      "action": "Participate in coding communities or challenges",
      "reason": "Learn from others and get feedback",
      "time_estimate": "2-3 hours/week"
    }
  ]
}
```

### 4. Get Personalized Resources
```http
GET /api/learning-path/{analysis_id}/personalized-resources?skill_name=Python&difficulty=intermediate&learning_style=hands-on

Response:
{
  "skill": "Python",
  "difficulty": "intermediate",
  "learning_style": "hands-on",
  "resources": [
    {
      "title": "Real Python - Comprehensive Guides",
      "url": "https://realpython.com",
      "type": "Tutorial",
      "hours": 40,
      "difficulty": "intermediate",
      "free": true
    },
    {
      "title": "LeetCode Python Problems",
      "url": "https://leetcode.com/...",
      "type": "Practice",
      "hours": 20,
      "difficulty": "intermediate",
      "free": true
    }
  ]
}
```

### 5. Get Success Criteria
```http
GET /api/learning-path/{analysis_id}/success-criteria?milestone_id=1

Response:
{
  "milestone_id": 1,
  "title": "Master Python",
  "skills": ["Python"],
  "success_criteria": [
    "Write and execute 10+ standalone Python scripts",
    "Understand and use Python data types and control structures",
    "Create functions and use modules effectively",
    "Debug basic Python errors independently"
  ],
  "projects": [
    {
      "title": "Build a CLI Todo Application",
      "description": "Create a command-line todo manager with basic CRUD operations"
    }
  ]
}
```

## Core Methods

### LearningPathGenerator

#### `generate_adaptive_path()`
```python
def generate_adaptive_path(
    feedback: FeedbackResult,
    priority_skills: List[str],
    user_profile: UserProfile,
    weeks_available: int = 12,
    resume_context: str = None,
    job_context: str = None
) -> LearningPath:
    """Generate fully adaptive learning path"""
```

#### `_adapt_milestone_to_profile()`
```python
def _adapt_milestone_to_profile(
    milestone: Milestone,
    user_profile: UserProfile,
    resume_context: str = None,
    job_context: str = None
) -> Milestone:
    """Adapt a milestone to user profile"""
```

#### `_calculate_adaptivity_score()`
```python
def _calculate_adaptivity_score(
    path: LearningPath,
    user_profile: UserProfile
) -> float:
    """Calculate how well path is adapted (0-1)"""
```

#### `update_milestone_progress()`
```python
def update_milestone_progress(
    learning_path: LearningPath,
    milestone_id: int,
    progress_percentage: int,
    is_completed: bool = False
) -> LearningPath:
    """Track progress on milestones"""
```

#### `generate_next_actions()`
```python
def generate_next_actions(
    learning_path: LearningPath,
    current_milestone_id: int
) -> List[Dict[str, str]]:
    """Generate dynamic next action recommendations"""
```

#### `_generate_success_criteria()`
```python
def _generate_success_criteria(
    skill_name: str,
    difficulty: str,
    user_level: str
) -> List[str]:
    """Generate measurable success criteria"""
```

#### `_generate_projects()`
```python
def _generate_projects(
    skill_name: str,
    difficulty: str
) -> List[Dict[str, str]]:
    """Generate hands-on projects"""
```

## Dynamic Features Explained

### 1. Difficulty Adaptation
- **Beginner users + Advanced milestone** → Adjusts to intermediate, adds 50% more time
- **Advanced users + Beginner milestone** → Reduces time by 30%
- Ensures milestones match actual capability level

### 2. Resource Filtering
- **Budget = "free"** → Prioritizes free resources
- **Preferred types** → Ranks resources by user preference
- **Learning style** → Selects resources matching preferred style
- **Type priority** → Official Docs > Tutorials > Courses > Practice > Projects

### 3. Adaptivity Scoring
Calculated as (0-1):
- **Resource matching**: Do resources match preferred types? (30%)
- **Budget alignment**: Are resources within budget? (20%)
- **Time availability**: Do hours fit availability? (30%)
- **Learning style**: Does path match preferred style? (20%)

### 4. Success Criteria Generation
Examples for Python:
- **Beginner**: Write 10+ scripts, understand data types, use modules
- **Intermediate**: Build full application, OOP principles, unit tests
- **Advanced**: Optimize code, async/await, contribute to open source

### 5. Project Suggestions
Real-world projects matched to skill and difficulty:
- **Python + Beginner**: CLI Todo App, Web Scraper
- **JavaScript + Intermediate**: Real-time Chat, E-commerce Frontend
- **React + Advanced**: Collaborative Editor, Data Dashboard

## Integration with Pipeline

### In `backend/main.py`:

The adaptive path generation is integrated into the analysis background task:

```python
async def run_analysis_background(analysis_id, resume_path, job_description):
    # ... existing analysis code ...
    
    # For dynamic path generation
    llm_config = LLMConfig()
    lp_generator = LearningPathGenerator(config=llm_config)
    
    # Generate with dynamic descriptions
    for milestone in path.milestones:
        dynamic_desc = lp_generator.generate_dynamic_milestone_description(
            skill_name=milestone.skills[0],
            difficulty=milestone.difficulty,
            resume_text=resume_text,
            job_description=job_description
        )
```

## Usage Example

### Backend Usage
```python
from src.pipeline.learning_path import LearningPathGenerator, UserProfile

# Initialize generator with LLM support
llm_config = LLMConfig()
generator = LearningPathGenerator(config=llm_config)

# Create user profile
user_profile = UserProfile(
    experience_level="intermediate",
    learning_style="hands-on",
    availability_hours_per_week=15,
    preferred_resource_types=["Course", "Practice"],
    budget="free"
)

# Generate adaptive path
adaptive_path = generator.generate_adaptive_path(
    feedback=feedback_result,
    priority_skills=["Python", "React", "SQL"],
    user_profile=user_profile,
    resume_context=resume_text,
    job_context=job_description
)

# Track progress
adaptive_path = generator.update_milestone_progress(
    adaptive_path,
    milestone_id=1,
    progress_percentage=75
)

# Get next actions
next_actions = generator.generate_next_actions(
    adaptive_path,
    current_milestone_id=1
)
```

### Frontend Usage
```typescript
// Generate adaptive path
const response = await fetch('/api/learning-path/adaptive', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: JSON.stringify({
    analysis_id: analysisId,
    user_profile: {
      experience_level: 'intermediate',
      learning_style: 'hands-on',
      availability_hours_per_week: 20,
      preferred_resource_types: ['Course', 'Practice'],
      budget: 'free'
    }
  })
});

// Update progress
await fetch(`/api/learning-path/${analysisId}/milestone-progress`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: JSON.stringify({
    milestone_id: 1,
    progress_percentage: 50,
    is_completed: false
  })
});

// Get next actions
const nextActions = await fetch(
  `/api/learning-path/${analysisId}/next-actions?current_milestone_id=1`,
  { headers: { 'Authorization': `Bearer ${token}` } }
).then(r => r.json());
```

## Configuration

### Environment Variables
```env
# Learning path generation
ENABLE_LEARNING_PATH_GENERATION=true
LEARNING_PATH_LLM_PROVIDER=groq  # or openai
LEARNING_PATH_LLM_MODEL=llama-3.1-8b-instant

# Default availability
DEFAULT_HOURS_PER_WEEK=15
DEFAULT_DIFFICULTY=intermediate
```

### Customization

To customize success criteria or projects, modify the dictionaries in:
- `_generate_success_criteria()` method
- `_generate_projects()` method

Example adding custom criteria:
```python
criteria_templates = {
    "YourSkill": {
        "beginner": ["Criterion 1", "Criterion 2"],
        "intermediate": ["Criterion 3", "Criterion 4"],
        "advanced": ["Criterion 5", "Criterion 6"]
    }
}
```

## Performance Considerations

- **LLM Calls**: Dynamic descriptions are cached per milestone
- **Database**: Milestones stored as JSON for flexibility
- **Scalability**: Adaptive generation scales to any number of skills
- **Response Time**: Typical adaptive path generation takes 2-5 seconds

## Future Enhancements

1. **ML-based Recommendation Engine**: Learn from user behavior
2. **Peer Learning Integration**: Compare progress with similar learners
3. **Spaced Repetition**: Automatic review scheduling
4. **Skill Level Assessment**: Pre-tests to determine actual capability
5. **Community Resources**: Integrate user-submitted resources
6. **Gamification**: Points, badges, streaks for motivation
7. **Live Mentor Matching**: Connect with experts for guidance
8. **Career Path Recommendations**: Suggest related skills for career growth

## Support

For issues or questions about the dynamic learning path system:
1. Check the [README.md](README.md) for general setup
2. Review [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for production considerations
3. See [WORKFLOW_VERIFICATION.md](WORKFLOW_VERIFICATION.md) for testing
