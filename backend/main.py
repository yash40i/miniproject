"""
FastAPI backend for Resume-Insight AI
Exposes the ML pipeline as REST API endpoints
With persistent PostgreSQL/SQLite database support
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import uuid
import json
import os
from pathlib import Path
import tempfile
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Import pipeline components
from src.pipeline import run_pipeline, ResumePipeline
from src.pipeline.learning_path import LearningPathGenerator
from src.config import PipelineConfig, LLMConfig
from src.utils import validate_pdf_file

# Import database
from src.database import init_db, get_db, Analysis, MatchingResult, Feedback, LearningPath, SessionLocal, User

# Import authentication
from src.auth import hash_password, verify_password, create_access_token, verify_token, generate_password_reset_token, create_password_reset_link, verify_password_reset_token
from src.schemas import UserRegister, UserLogin, Token, UserResponse, AnalysisStatus, ForgotPasswordRequest, ForgotPasswordResponse, ResetPasswordRequest, ResetPasswordResponse, VerifyResetTokenRequest, VerifyResetTokenResponse, GoogleAuthRequest, GoogleAuthResponse, UserUpdateRequest, ChangePasswordRequest, ChangePasswordResponse, UserProfileResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Initialize FastAPI app
app = FastAPI(
    title="Resume-Insight AI API",
    description="Semantic resume analysis and learning path generation",
    version="1.0.0"
)

# Configure CORS - MUST be before adding middleware
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3003",
    "http://localhost:3004",
    "http://localhost:3005",
    "http://localhost:3006",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3003",
    "http://127.0.0.1:3004",
    "http://127.0.0.1:3005",
    "http://127.0.0.1:3006",
    "http://127.0.0.1:8000",
    # Production Vercel frontend
    "https://miniproject103qwertyu.vercel.app",
]

# Read CORS origins from environment (e.g. CORS_ORIGINS=https://your-app.vercel.app)
cors_origins_str = os.getenv("CORS_ORIGINS")
if cors_origins_str:
    for origin in cors_origins_str.split(","):
        origin = origin.strip()
        if origin and origin not in origins:
            origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.(vercel\.app|railway\.app)",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)



# Security scheme
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Dependency to get authenticated user from JWT token"""
    token = credentials.credentials
    token_data = verify_token(token)
    
    if token_data is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = db.query(User).filter(User.id == token_data["user_id"]).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)), db: Session = Depends(get_db)) -> Optional[User]:
    """Dependency to optionally get authenticated user from JWT token"""
    if not credentials:
        return None
    token = credentials.credentials
    token_data = verify_token(token)
    if token_data is None:
        return None
    return db.query(User).filter(User.id == token_data["user_id"]).first()

# Request/Response models
class AnalysisRequest(BaseModel):
    """Request model for resume analysis"""
    job_description: str
    generate_feedback: bool = True
    generate_learning_path: bool = True


class SkillMatchResponse(BaseModel):
    """Response model for skill match"""
    resume_skill: str
    job_skill: str
    similarity_score: float
    match_strength: str


class MatchingResultResponse(BaseModel):
    """Response model for matching results"""
    overall_score: float
    matched_percentage: float
    matched_skills: List[SkillMatchResponse]
    missing_skills: List[str]


class AnalysisResponse(BaseModel):
    """Complete analysis response"""
    analysis_id: str
    status: str  # "completed", "processing", "failed"
    matching_result: Optional[MatchingResultResponse] = None
    feedback: Optional[dict] = None
    learning_path: Optional[dict] = None
    error: Optional[str] = None


# Pipeline configuration
pipeline_config = PipelineConfig()


@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "name": "Resume-Insight AI API",
        "version": "1.0.0",
        "description": "Semantic resume analysis engine",
        "endpoints": {
            "analyze": "POST /api/analyze",
            "get_result": "GET /api/results/{analysis_id}",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Resume-Insight AI API"
    }


@app.post("/auth/signup", response_model=Token)
async def signup(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - **email**: User email (must be unique)
    - **password**: User password (will be hashed)
    - **full_name**: Optional full name
    
    Returns access token for authentication
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        hashed_pwd = hash_password(user_data.password)
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_pwd,
            full_name=user_data.full_name
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create JWT token
        access_token = create_access_token(data={"user_id": str(new_user.id)})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")


@app.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and get access token
    
    - **email**: User email
    - **password**: User password
    
    Returns access token for authentication
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == credentials.email).first()
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not user.is_active:
            raise HTTPException(status_code=403, detail="User account is inactive")
        
        # Create JWT token
        access_token = create_access_token(data={"user_id": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    return current_user


@app.post("/auth/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Request password reset link
    
    - **email**: User email address
    
    Returns confirmation message
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        
        # For security, always return success even if user doesn't exist
        if not user:
            return ForgotPasswordResponse(
                message="If an account exists with this email, a password reset link will be sent shortly.",
                email=request.email
            )
        
        # Generate reset token
        reset_token = generate_password_reset_token(request.email)
        
        # Store token in database with expiration (1 hour)
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(minutes=60)
        db.commit()
        
        # In production, send email with reset link
        # For now, log it or return in dev mode
        reset_link = create_password_reset_link(reset_token)
        logger.info(f"Password reset link for {request.email}: {reset_link}")
        
        return ForgotPasswordResponse(
            message="If an account exists with this email, a password reset link will be sent shortly.",
            email=request.email
        )
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process password reset request")


@app.post("/auth/verify-reset-token", response_model=VerifyResetTokenResponse)
async def verify_reset_token(request: VerifyResetTokenRequest, db: Session = Depends(get_db)):
    """
    Verify if a password reset token is valid
    
    - **token**: Password reset token from email link
    
    Returns validity status
    """
    try:
        # Find user with this token
        user = db.query(User).filter(User.password_reset_token == request.token).first()
        
        if not user:
            return VerifyResetTokenResponse(
                valid=False,
                message="Invalid or expired reset token"
            )
        
        # Check if token has expired
        if user.password_reset_expires < datetime.utcnow():
            # Clear expired token
            user.password_reset_token = None
            user.password_reset_expires = None
            db.commit()
            return VerifyResetTokenResponse(
                valid=False,
                message="Reset token has expired. Please request a new one."
            )
        
        return VerifyResetTokenResponse(
            valid=True,
            email=user.email,
            message="Reset token is valid"
        )
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to verify reset token")


@app.post("/auth/google", response_model=Token)
async def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Google OAuth authentication endpoint
    
    - **token**: Google ID token from frontend
    - **email**: User email from token
    - **name**: User name from token
    
    Returns access token for authentication
    """
    try:
        if not request.email:
            raise HTTPException(status_code=400, detail="Email is required for Google auth")
        
        # Check if user already exists
        user = db.query(User).filter(User.email == request.email).first()
        
        if not user:
            # Create new user from Google auth
            new_user = User(
                email=request.email,
                full_name=request.name,
                google_email=request.email,
                oauth_provider="google",
                # Set a random password for OAuth users (they won't use it)
                hashed_password=hash_password(str(uuid.uuid4()))
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            user = new_user
            logger.info(f"New Google user created: {request.email}")
        else:
            # Update existing user with Google info if not already set
            if not user.google_email:
                user.google_email = request.email
                user.oauth_provider = "google"
                db.commit()
        
        # Create JWT token
        access_token = create_access_token(data={"user_id": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google auth error: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Google authentication failed: {str(e)}")


@app.post("/auth/reset-password", response_model=ResetPasswordResponse)
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset password using valid token
    
    - **token**: Password reset token
    - **new_password**: New password
    - **confirm_password**: Password confirmation
    
    Returns success message
    """
    try:
        # Validate passwords match
        if request.new_password != request.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        # Find user with this token
        user = db.query(User).filter(User.password_reset_token == request.token).first()
        
        if not user:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        # Check if token has expired
        if user.password_reset_expires < datetime.utcnow():
            user.password_reset_token = None
            user.password_reset_expires = None
            db.commit()
            raise HTTPException(status_code=400, detail="Reset token has expired. Please request a new one.")
        
        # Update password
        user.hashed_password = hash_password(request.new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        db.commit()
        
        return ResetPasswordResponse(
            message="Password has been successfully reset. You can now login with your new password.",
            email=user.email
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to reset password")


# ============================================================================
# PROFILE MANAGEMENT ENDPOINTS
# ============================================================================

@app.put("/auth/profile", response_model=UserProfileResponse)
async def update_profile(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile information
    
    - **full_name**: Update user's full name
    - **email**: Update user's email (must be unique)
    
    Returns updated user profile
    """
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if email is being changed and if it's already taken
        if request.email and request.email != user.email:
            existing = db.query(User).filter(User.email == request.email).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already in use")
            user.email = request.email
        
        # Update full name
        if request.full_name is not None:
            user.full_name = request.full_name
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        return UserProfileResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update profile")


@app.post("/auth/change-password", response_model=ChangePasswordResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password (requires current password)
    
    - **current_password**: User's current password
    - **new_password**: New password to set
    - **confirm_password**: Confirmation of new password
    
    Returns success message
    """
    try:
        # Validate passwords match
        if request.new_password != request.confirm_password:
            raise HTTPException(status_code=400, detail="New passwords do not match")
        
        # Verify current password
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not verify_password(request.current_password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        
        # Check that new password is different from current
        if verify_password(request.new_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="New password must be different from current password")
        
        # Update password
        user.hashed_password = hash_password(request.new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        
        return ChangePasswordResponse(
            message="Password has been successfully changed",
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to change password")


@app.get("/auth/profile", response_model=UserProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile information"""
    try:
        return UserProfileResponse(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            is_active=current_user.is_active,
            created_at=current_user.created_at.isoformat(),
            updated_at=current_user.updated_at.isoformat()
        )
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    """
    Analyze resume against job description
    
    - **file**: Resume PDF file (multipart/form-data)
    - **job_description**: Job description text (URL encoded form data)
    
    Returns analysis_id for checking results later
    """
    
    # Generate unique analysis ID
    analysis_id = str(uuid.uuid4())
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_path = temp_file.name
        
        # Validate file
        if not temp_path.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Create analysis record in database
        db_analysis = Analysis(
            id=analysis_id,
            user_id=None,  # Guest analysis
            job_description=job_description,
            status="processing",
            created_at=datetime.utcnow()
        )
        
        # DEBUG: Verify analysis object before saving
        logger.info(f"[DEBUG] Creating analysis:")
        logger.info(f"  - analysis_id: {analysis_id}")
        logger.info(f"  - user_id: {db_analysis.user_id} (type: {type(db_analysis.user_id).__name__})")
        logger.info(f"  - job_description length: {len(job_description)}")
        logger.info(f"  - status: {db_analysis.status}")
        
        db.add(db_analysis)
        db.commit()
        
        logger.info(f"[DEBUG] Analysis saved successfully! ID: {analysis_id}")
        db.refresh(db_analysis)
        
        # Run analysis in background
        background_tasks.add_task(
            run_analysis_background,
            analysis_id=analysis_id,
            resume_path=temp_path,
            job_description=job_description
        )
        
        return {
            "analysis_id": analysis_id,
            "status": "processing",
            "message": "Analysis started. Check results using analysis_id."
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume: {str(e)}"
        )


def run_analysis_background(
    analysis_id: str,
    resume_path: str,
    job_description: str
):
    """
    Background task to run full pipeline analysis with dynamic Groq responses
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting analysis {analysis_id}")
        
        # Parse resume to store text in DB
        resume_raw_text = ""
        try:
            from src.pipeline.pdf_parser import parse_resume
            parsed = parse_resume(resume_path)
            resume_raw_text = parsed.text
            logger.info(f"Parsed raw resume text length: {len(resume_raw_text)}")
        except Exception as e:
            logger.error(f"Error parsing resume for raw text: {e}")
            
        # DEBUG: Log job description before pipeline
        logger.info(f"[DEBUG] Job description before pipeline:")
        logger.info(f"  - Length: {len(job_description)}")
        logger.info(f"  - First 100 chars: {job_description[:100]}")
        logger.info(f"  - Last 100 chars: {job_description[-100:]}")
        
        # Run pipeline
        result = run_pipeline(resume_path, job_description, pipeline_config)
        
        # Initialize LLM config for dynamic generation
        try:
            llm_config = LLMConfig()
            lp_generator = LearningPathGenerator(config=llm_config)
        except:
            # Fallback without dynamic generation
            llm_config = None
            lp_generator = LearningPathGenerator()
        
        # Read resume text for context
        try:
            from PyPDF2 import PdfReader
            pdf_reader = PdfReader(resume_path)
            resume_text = "".join(page.extract_text() for page in pdf_reader.pages)[:300]
        except:
            resume_text = None
        
        # DEBUG: Log matching result before saving
        logger.info(f"[DEBUG] Matching result:")
        logger.info(f"  - Overall score: {result.matching_result.overall_score}")
        logger.info(f"  - Matched skills count: {len(result.matching_result.matched_skills)}")
        logger.info(f"  - Missing skills count: {len(result.matching_result.missing_skills)}")
        if result.matching_result.matched_skills:
            logger.info(f"  - First matched skill: {result.matching_result.matched_skills[0]}")
        
        # Prepare matching result
        matched_skills_data = [
            {
                "resume_skill": m.resume_skill,
                "job_skill": m.job_skill,
                "similarity_score": float(m.similarity_score),
                "match_strength": m.match_strength
            }
            for m in result.matching_result.matched_skills
        ]
        logger.info(f"[DEBUG] Prepared {len(matched_skills_data)} matched skills for database")
        
        # Save matching result to database
        matching_result_db = MatchingResult(
            analysis_id=analysis_id,
            overall_score=float(result.matching_result.overall_score),
            matched_percentage=float(result.matching_result.matched_percentage),
            matched_skills=matched_skills_data,
            missing_skills=result.matching_result.missing_skills,
            skill_node_map=result.skill_node_map.to_dict() if result.skill_node_map else None
        )
        db.add(matching_result_db)
        
        # Prepare and save feedback (always create, even if empty)
        feedback_db = Feedback(
            analysis_id=analysis_id,
            gap_analysis=result.feedback_result.gap_analysis if result.feedback_result else "Analysis complete. Review the matched and missing skills above.",
            recommendations=result.feedback_result.recommendations if result.feedback_result else [],
            priority_skills=result.feedback_result.priority_skills if result.feedback_result else result.matching_result.missing_skills[:3],
            next_steps=result.feedback_result.next_steps if result.feedback_result else "Begin with the priority skills identified in the learning path."
        )
        db.add(feedback_db)
        logger.info(f"Feedback record created for {analysis_id}")
        
        # Prepare and save learning path with dynamic generation
        if result.learning_path:
            milestones_data = []
            
            for idx, m in enumerate(result.learning_path.milestones):
                # Generate dynamic description if possible
                dynamic_description = m.description
                if lp_generator and llm_config:
                    try:
                        dynamic_description = lp_generator.generate_dynamic_milestone_description(
                            skill_name=m.skills[0] if m.skills else f"Skill {idx+1}",
                            difficulty=m.difficulty,
                            resume_text=resume_text,
                            job_description=job_description[:200]
                        )
                        logger.info(f"Generated dynamic description for {m.skills[0] if m.skills else f'Skill {idx+1}'}")
                    except Exception as e:
                        logger.warning(f"Failed to generate dynamic description: {e}")
                        dynamic_description = m.description
                
                milestone_dict = {
                    "id": m.id,
                    "title": m.title,
                    "description": dynamic_description,
                    "estimated_hours": m.estimated_hours,
                    "difficulty": m.difficulty,
                    "resources": m.resources
                }
                milestones_data.append(milestone_dict)
            
            # Generate dynamic learning path description if possible
            path_description = result.learning_path.description
            if lp_generator and llm_config:
                try:
                    path_description = lp_generator.generate_dynamic_learning_path_description(
                        skills=result.learning_path.priority_skills,
                        weeks=result.learning_path.estimated_weeks,
                        resume_text=resume_text,
                        job_description=job_description[:200],
                        overall_match=result.matching_result.overall_score
                    )
                    logger.info("Generated dynamic learning path description")
                except Exception as e:
                    logger.warning(f"Failed to generate dynamic path description: {e}")
                    path_description = result.learning_path.description
            
            learning_path_db = LearningPath(
                analysis_id=analysis_id,
                title=result.learning_path.title,
                total_hours=result.learning_path.total_hours,
                estimated_weeks=result.learning_path.estimated_weeks,
                milestones=milestones_data
            )
            db.add(learning_path_db)
            logger.info(f"Learning path with {len(milestones_data)} milestones created")
        
        # Update analysis status
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis:
            analysis.status = "completed"
            analysis.completed_at = datetime.utcnow()
            analysis.resume_text = resume_raw_text
        
        db.commit()
        logger.info(f"Analysis {analysis_id} completed successfully with dynamic Groq responses")
        
    except Exception as e:
        logger.error(f"Error in background analysis {analysis_id}: {str(e)}", exc_info=True)
        # Update analysis with error status
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                analysis.status = "failed"
                analysis.error = str(e)
            db.commit()
        except:
            pass
    finally:
        # Clean up temp file
        Path(resume_path).unlink(missing_ok=True)
        db.close()


@app.get("/api/results/{analysis_id}")
async def get_analysis_results(
    analysis_id: str, 
    db: Session = Depends(get_db)
):
    """
    Get analysis results by ID
    
    Returns status and results when available
    """
    
    # Query analysis from database
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis {analysis_id} not found"
        )
    
    # Prepare response
    response = {
        "analysis_id": analysis_id,
        "status": analysis.status,
        "matching_result": None,
        "feedback": None,
        "learning_path": None,
        "error": analysis.error
    }
    
    # Include matching result if available
    if analysis.matching_result:
        response["matching_result"] = {
            "overall_score": analysis.matching_result.overall_score,
            "matched_percentage": analysis.matching_result.matched_percentage,
            "matched_skills": analysis.matching_result.matched_skills,
            "missing_skills": analysis.matching_result.missing_skills,
            "skill_node_map": analysis.matching_result.skill_node_map
        }
    
    # Include feedback if available
    if analysis.feedback:
        response["feedback"] = {
            "gap_analysis": analysis.feedback.gap_analysis,
            "recommendations": analysis.feedback.recommendations,
            "priority_skills": analysis.feedback.priority_skills,
            "next_steps": analysis.feedback.next_steps
        }
    
    # Include learning path if available
    if analysis.learning_path:
        response["learning_path"] = {
            "title": analysis.learning_path.title,
            "total_hours": analysis.learning_path.total_hours,
            "estimated_weeks": analysis.learning_path.estimated_weeks,
            "milestones": analysis.learning_path.milestones
        }
    
    # Include adapted resume if available
    response["adapted_resume_json"] = analysis.adapted_resume_json

    return response


@app.post("/api/text-analysis")
async def analyze_text_resume(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze text resume (not PDF) against job description
    
    - **job_description**: Job description text
    - **resume_text**: Resume text content
    """
    
    analysis_id = str(uuid.uuid4())
    
    # Create initial analysis record
    db_analysis = Analysis(
        id=analysis_id,
        user_id=current_user.id,
        job_description=request.job_description,
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(db_analysis)
    db.commit()
    return {
        "analysis_id": analysis_id,
        "status": "pending",
        "message": "Text analysis endpoint - coming soon"
    }


class CourseRecommendationRequest(BaseModel):
    """Request model for course recommendations directly from a job description"""
    job_description: str
    experience_level: Optional[str] = "intermediate"  # beginner, intermediate, advanced


@app.post("/api/recommend-courses")
async def recommend_courses_for_job(request: CourseRecommendationRequest):
    """
    Recommend courses directly based on a job description using Groq LLM.
    Identifies key skills required and lists courses for each skill.
    """
    try:
        # Load Groq API Key and Config
        llm_config = LLMConfig()
        if not llm_config.api_key:
            raise HTTPException(status_code=500, detail="Groq API key not configured")
        
        # Initialize Groq client
        from groq import Groq
        client = Groq(api_key=llm_config.api_key, timeout=240.0)
        
        prompt = f"""
You are an expert technical recruiter and career coach.
Analyze the following job description and identify the top 4 key technical skills required to land this job.
For each skill, recommend exactly 3 high-quality online courses, tutorials, or official documentations for a learner at the "{request.experience_level}" level.

Job Description:
\"\"\"{request.job_description}\"\"\"

For each course, provide:
1. title: Course name
2. platform: Course host/creator (e.g. Coursera, Udemy, FreeCodeCamp, Pluralsight, official docs)
3. url: A realistic, search or direct link on the platform (e.g., "https://www.coursera.org/search?query=kubernetes")
4. hours: Estimated number of hours to complete
5. free: true if free, false if paid

Response Format:
You MUST return ONLY a JSON object matching this schema, with no markdown code blocks, no additional explanation, and no extra characters:
{{
  "job_title_estimate": "Estimated job title from description",
  "skills": [
    {{
      "name": "Skill Name",
      "reason": "Why this skill is crucial for this job",
      "courses": [
        {{
          "title": "Course Title",
          "platform": "Platform Name",
          "url": "URL",
          "hours": 15,
          "free": true
        }}
      ]
    }}
  ]
}}
"""
        response = client.chat.completions.create(
            model=llm_config.model or "llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1000,
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
            
        recommendations = json.loads(content)
        return recommendations
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error from Groq response: {e}")
        raise HTTPException(
            status_code=502,
            detail="Failed to generate a valid structured course recommendation from LLM"
        )
    except Exception as e:
        logger.error(f"Error in recommend_courses: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to recommend courses: {str(e)}"
        )


@app.delete("/api/results/{analysis_id}")
async def delete_analysis(
    analysis_id: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an analysis and associated results"""
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    db.delete(analysis)
    db.commit()
    
    return {"message": "Analysis deleted successfully"}


# ============================================================================
# DYNAMIC LEARNING PATH MANAGEMENT ENDPOINTS
# ============================================================================

class UserProfileRequest(BaseModel):
    """User learning profile for personalization"""
    experience_level: str  # beginner, intermediate, advanced
    learning_style: str  # visual, hands-on, theory, mixed
    availability_hours_per_week: int = 15
    preferred_resource_types: Optional[List[str]] = None
    budget: str = "free"  # free, limited, flexible


class MilestoneProgressRequest(BaseModel):
    """Request to update milestone progress"""
    milestone_id: int
    progress_percentage: int
    is_completed: bool = False


class DynamicLearningPathRequest(BaseModel):
    """Request for adaptive learning path generation"""
    analysis_id: str
    user_profile: UserProfileRequest


@app.post("/api/learning-path/adaptive")
async def generate_adaptive_learning_path(
    request: DynamicLearningPathRequest,
    db: Session = Depends(get_db)
):
    """
    Generate an adaptive learning path based on user profile.
    
    Uses the analysis results and personalizes based on:
    - Learning style (visual, hands-on, theory)
    - Experience level
    - Available time per week
    - Budget constraints
    - Preferred resource types
    
    Note: Authentication is optional for demo purposes
    """
    try:
        # Get the analysis (no auth required for demo)
        analysis = db.query(Analysis).filter(
            Analysis.id == request.analysis_id
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get feedback and matching result
        feedback = db.query(Feedback).filter(Feedback.analysis_id == request.analysis_id).first()
        matching = db.query(MatchingResult).filter(MatchingResult.analysis_id == request.analysis_id).first()
        
        if not feedback or not matching:
            raise HTTPException(status_code=400, detail="Analysis must be completed before generating adaptive path")
        
        # Initialize LLM config for dynamic generation
        try:
            llm_config = LLMConfig()
            lp_generator = LearningPathGenerator(config=llm_config)
        except:
            lp_generator = LearningPathGenerator()
        
        # Convert user profile request to UserProfile dataclass
        from src.pipeline.learning_path import UserProfile
        user_profile = UserProfile(
            experience_level=request.user_profile.experience_level,
            learning_style=request.user_profile.learning_style,
            availability_hours_per_week=request.user_profile.availability_hours_per_week,
            preferred_resource_types=request.user_profile.preferred_resource_types or [],
            budget=request.user_profile.budget
        )
        
        # Generate adaptive path
        adaptive_path = lp_generator.generate_adaptive_path(
            feedback=feedback,  # This needs to be converted from DB
            priority_skills=feedback.priority_skills,
            user_profile=user_profile,
            weeks_available=12,
            job_context=analysis.job_description
        )
        
        return {
            "analysis_id": request.analysis_id,
            "learning_path": {
                "title": adaptive_path.title,
                "description": adaptive_path.description,
                "total_hours": adaptive_path.total_hours,
                "estimated_weeks": adaptive_path.estimated_weeks,
                "overall_progress": adaptive_path.overall_progress,
                "adaptivity_score": round(adaptive_path.adaptivity_score, 2),
                "recommendation_engine": adaptive_path.recommendation_engine_used,
                "milestones": [
                    {
                        "id": m.id,
                        "title": m.title,
                        "description": m.description,
                        "skills": m.skills,
                        "estimated_hours": m.estimated_hours,
                        "difficulty": m.difficulty,
                        "start_date": m.start_date.isoformat() if m.start_date else None,
                        "target_completion": m.target_completion.isoformat() if m.target_completion else None,
                        "success_criteria": m.success_criteria,
                        "projects": m.projects,
                        "resources": m.resources,
                        "is_completed": m.is_completed,
                    }
                    for m in adaptive_path.milestones
                ],
                "priority_skills": adaptive_path.priority_skills
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating adaptive learning path: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating path: {str(e)}")


@app.post("/api/learning-path/{analysis_id}/milestone-progress")
async def update_milestone_progress(
    analysis_id: str,
    update: MilestoneProgressRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Update progress on a specific milestone.
    
    - **analysis_id**: Analysis ID
    - **milestone_id**: ID of the milestone to update
    - **progress_percentage**: Progress from 0-100
    - **is_completed**: Whether milestone is completed
    """
    try:
        # Verify ownership (if user logged in, check user_id, else just check existence)
        query = db.query(Analysis).filter(Analysis.id == analysis_id)
        if current_user:
            query = query.filter(Analysis.user_id == current_user.id)
            
        analysis = query.first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found or permission denied")
        
        # Get learning path
        learning_path_db = db.query(LearningPath).filter(LearningPath.analysis_id == analysis_id).first()
        if not learning_path_db:
            raise HTTPException(status_code=404, detail="Learning path not found")
        
        # Update milestone progress
        milestones = list(learning_path_db.milestones)
        for milestone in milestones:
            if milestone.get("id") == update.milestone_id:
                milestone["progress_percentage"] = min(100, max(0, update.progress_percentage))
                milestone["is_completed"] = update.is_completed or update.progress_percentage >= 100
                break
        
        # Calculate overall progress
        total_progress = sum(m.get("progress_percentage", 0) for m in milestones)
        overall_progress = int(total_progress / len(milestones)) if milestones else 0
        
        # Update database
        learning_path_db.milestones = milestones
        learning_path_db.overall_progress = overall_progress
        
        # Update User Streak if logged in
        if current_user:
            now = datetime.utcnow()
            if current_user.last_active_date:
                # Calculate days between now and last active date (ignoring time)
                delta_days = (now.date() - current_user.last_active_date.date()).days
                
                if delta_days == 1:
                    # Consecutive day!
                    current_user.current_streak += 1
                elif delta_days > 1:
                    # Streak broken
                    current_user.current_streak = 1
            else:
                # First time tracking streak
                current_user.current_streak = 1
                
            # Update longest streak
            if current_user.current_streak > current_user.longest_streak:
                current_user.longest_streak = current_user.current_streak
                
            current_user.last_active_date = now
            
        db.commit()
        
        return {
            "analysis_id": analysis_id,
            "milestone_id": update.milestone_id,
            "progress_percentage": update.progress_percentage,
            "is_completed": update.is_completed,
            "overall_progress": overall_progress,
            "current_streak": current_user.current_streak if current_user else 0,
            "message": "Milestone progress updated successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating milestone progress: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error updating progress: {str(e)}")


@app.get("/api/learning-path/{analysis_id}/next-actions")
async def get_next_actions(
    analysis_id: str,
    current_milestone_id: int = 1,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dynamic next action recommendations based on current progress.
    
    - **analysis_id**: Analysis ID
    - **current_milestone_id**: Current milestone ID (default: 1)
    
    Returns personalized next steps to consolidate learning
    """
    try:
        # Verify ownership
        analysis = db.query(Analysis).filter(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Initialize LLM generator
        try:
            llm_config = LLMConfig()
            lp_generator = LearningPathGenerator(config=llm_config)
        except:
            lp_generator = LearningPathGenerator()
        
        # Get learning path
        learning_path_db = db.query(LearningPath).filter(LearningPath.analysis_id == analysis_id).first()
        if not learning_path_db:
            raise HTTPException(status_code=404, detail="Learning path not found")
        
        # Convert DB learning path to dataclass format (simplified)
        from src.pipeline.learning_path import LearningPath, Milestone
        milestones = []
        for m_data in learning_path_db.milestones:
            milestone = Milestone(
                id=m_data.get("id", 1),
                title=m_data.get("title", ""),
                description=m_data.get("description", ""),
                skills=m_data.get("skills", []),
                resources=m_data.get("resources", []),
                estimated_hours=m_data.get("estimated_hours", 20),
                difficulty=m_data.get("difficulty", "beginner")
            )
            milestones.append(milestone)
        
        learning_path = LearningPath(
            title=learning_path_db.title,
            description="",
            total_hours=learning_path_db.total_hours,
            estimated_weeks=learning_path_db.estimated_weeks,
            milestones=milestones,
            priority_skills=[],
            resources={}
        )
        
        # Generate next actions
        next_actions = lp_generator.generate_next_actions(learning_path, current_milestone_id)
        
        return {
            "analysis_id": analysis_id,
            "current_milestone_id": current_milestone_id,
            "next_actions": next_actions
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating next actions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating actions: {str(e)}")


@app.get("/api/learning-path/{analysis_id}/personalized-resources")
async def get_personalized_resources(
    analysis_id: str,
    skill_name: str,
    difficulty: str = "intermediate",
    learning_style: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized resource recommendations for a specific skill.
    
    - **analysis_id**: Analysis ID (for verification)
    - **skill_name**: Skill to get resources for
    - **difficulty**: Difficulty level (beginner, intermediate, advanced)
    - **learning_style**: Optional learning style preference
    
    Returns ranked resources based on learner preferences
    """
    try:
        # Verify ownership
        analysis = db.query(Analysis).filter(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Initialize LLM generator
        try:
            llm_config = LLMConfig()
            lp_generator = LearningPathGenerator(config=llm_config)
        except:
            lp_generator = LearningPathGenerator()
        
        # Get personalized resources
        resources = lp_generator.generate_personalized_resource_recommendations(
            skill_name=skill_name,
            difficulty=difficulty,
            learning_style=learning_style
        )
        
        return {
            "skill": skill_name,
            "difficulty": difficulty,
            "learning_style": learning_style,
            "resources": resources
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting personalized resources: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching resources: {str(e)}")


@app.get("/api/learning-path/{analysis_id}/success-criteria")
async def get_success_criteria(
    analysis_id: str,
    milestone_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get measurable success criteria for a milestone.
    
    - **analysis_id**: Analysis ID
    - **milestone_id**: Milestone ID
    
    Returns specific, measurable outcomes for the milestone
    """
    try:
        # Verify ownership
        analysis = db.query(Analysis).filter(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get learning path
        learning_path_db = db.query(LearningPath).filter(LearningPath.analysis_id == analysis_id).first()
        if not learning_path_db:
            raise HTTPException(status_code=404, detail="Learning path not found")
        
        # Find milestone
        milestone_data = None
        for m in learning_path_db.milestones:
            if m.get("id") == milestone_id:
                milestone_data = m
                break
        
        if not milestone_data:
            raise HTTPException(status_code=404, detail="Milestone not found")
        
        return {
            "milestone_id": milestone_id,
            "title": milestone_data.get("title", ""),
            "skills": milestone_data.get("skills", []),
            "success_criteria": milestone_data.get("success_criteria", []),
            "projects": milestone_data.get("projects", [])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting success criteria: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching criteria: {str(e)}")
    """Delete analysis result"""
    
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis {analysis_id} not found"
        )
    
    # Verify user ownership
    if analysis.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to delete this analysis"
        )
    
    db.delete(analysis)
    db.commit()
    
    return {
        "message": f"Analysis {analysis_id} deleted successfully"
    }


@app.get("/api/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's analysis statistics"""
    
    user_analyses = db.query(Analysis).filter(Analysis.user_id == current_user.id)
    total = user_analyses.count()
    completed = user_analyses.filter(Analysis.status == "completed").count()
    processing = user_analyses.filter(Analysis.status == "processing").count()
    failed = user_analyses.filter(Analysis.status == "failed").count()
    
    return {
        "total_analyses": total,
        "completed": completed,
        "processing": processing,
        "failed": failed
    }


@app.post("/api/results/{analysis_id}/generate-match-resume")
async def generate_match_resume(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Generate a 100% matched resume JSON against the job description using LLM
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    if not analysis.resume_text:
        raise HTTPException(
            status_code=400, 
            detail="Original resume text not found. Cannot generate matched resume."
        )
        
    if not analysis.matching_result:
        raise HTTPException(
            status_code=400,
            detail="Matching results not ready. Please wait for analysis to complete."
        )
        
    # Check if already generated to save LLM tokens/costs
    if analysis.adapted_resume_json:
        return {
            "status": "success",
            "message": "Resume already adapted previously",
            "adapted_resume": analysis.adapted_resume_json
        }
        
    # Prepare matching result info
    matching_data = {
        "overall_score": analysis.matching_result.overall_score,
        "matched_skills": [
            {
                "resume_skill": m.get("resume_skill", "") if isinstance(m, dict) else getattr(m, "resume_skill", ""),
                "job_skill": m.get("job_skill", "") if isinstance(m, dict) else getattr(m, "job_skill", ""),
                "similarity_score": m.get("similarity_score", 0.0) if isinstance(m, dict) else getattr(m, "similarity_score", 0.0)
            }
            for m in (analysis.matching_result.matched_skills or [])
        ],
        "missing_skills": analysis.matching_result.missing_skills or []
    }
    
    try:
        from src.pipeline.resume_generator import ResumeGenerator
        from src.config.config import LLMConfig
        
        llm_config = LLMConfig()
        generator = ResumeGenerator(llm_config)
        
        adapted_json = generator.generate_matched_resume_json(
            resume_text=analysis.resume_text,
            job_description=analysis.job_description,
            matching_result=matching_data
        )
        
        analysis.adapted_resume_json = adapted_json
        db.commit()
        
        return {
            "status": "success",
            "message": "Resume successfully adapted to 100% match",
            "adapted_resume": adapted_json
        }
    except Exception as e:
        logger.error(f"Error in generate_match_resume: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate matched resume: {str(e)}")


@app.get("/api/results/{analysis_id}/download-match-resume")
async def download_match_resume(
    analysis_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generate and download the 100% matched resume as PDF
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    if not analysis.adapted_resume_json:
        raise HTTPException(
            status_code=400,
            detail="Resume has not been adapted yet. Please call the generate endpoint first."
        )
        
    try:
        from src.pipeline.resume_generator import ResumeGenerator
        import tempfile
        
        # Create a temp file path
        fd, temp_pdf_path = tempfile.mkstemp(suffix=".pdf", prefix="adapted_resume_")
        os.close(fd)
        
        generator = ResumeGenerator()
        generator.generate_resume_pdf(analysis.adapted_resume_json, temp_pdf_path)
        
        # Clean up the file after serving
        background_tasks.add_task(os.unlink, temp_pdf_path)
        
        candidate_name = analysis.adapted_resume_json.get("personal_info", {}).get("name", "Adapted")
        clean_name = "".join(c for c in candidate_name if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
        filename = f"{clean_name}_100_Match_Resume.pdf"
        
        return FileResponse(
            path=temp_pdf_path,
            media_type="application/pdf",
            filename=filename
        )
    except Exception as e:
        logger.error(f"Error downloading matched resume: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to compile PDF resume: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
