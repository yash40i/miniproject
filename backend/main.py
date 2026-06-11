"""
FastAPI backend for Resume-Insight AI
Exposes the ML pipeline as REST API endpoints
With persistent PostgreSQL/SQLite database support
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import uuid
import json
from pathlib import Path
import tempfile
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Import pipeline components
from src.pipeline import run_pipeline, ResumePipeline
from src.config import PipelineConfig
from src.utils import validate_pdf_file

# Import database
from src.database import init_db, get_db, Analysis, MatchingResult, Feedback, LearningPath, SessionLocal, User

# Import authentication
from src.auth import hash_password, verify_password, create_access_token, verify_token, generate_password_reset_token, create_password_reset_link, verify_password_reset_token
from src.schemas import UserRegister, UserLogin, Token, UserResponse, AnalysisStatus, ForgotPasswordRequest, ForgotPasswordResponse, ResetPasswordRequest, ResetPasswordResponse, VerifyResetTokenRequest, VerifyResetTokenResponse, GoogleAuthRequest, GoogleAuthResponse

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
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
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
            user_id=current_user.id,
            job_description=job_description,
            status="processing",
            created_at=datetime.utcnow()
        )
        db.add(db_analysis)
        db.commit()
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


async def run_analysis_background(
    analysis_id: str,
    resume_path: str,
    job_description: str
):
    """
    Background task to run full pipeline analysis
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting analysis {analysis_id}")
        
        # Run pipeline
        result = run_pipeline(resume_path, job_description, pipeline_config)
        
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
        
        # Save matching result to database
        matching_result_db = MatchingResult(
            analysis_id=analysis_id,
            overall_score=float(result.matching_result.overall_score),
            matched_percentage=float(result.matching_result.matched_percentage),
            matched_skills=matched_skills_data,
            missing_skills=result.matching_result.missing_skills
        )
        db.add(matching_result_db)
        
        # Prepare and save feedback
        if result.feedback_result:
            feedback_db = Feedback(
                analysis_id=analysis_id,
                gap_analysis=result.feedback_result.gap_analysis,
                recommendations=result.feedback_result.recommendations,
                priority_skills=result.feedback_result.priority_skills,
                next_steps=result.feedback_result.next_steps
            )
            db.add(feedback_db)
        
        # Prepare and save learning path
        if result.learning_path:
            milestones_data = [
                {
                    "id": m.id,
                    "title": m.title,
                    "description": m.description,
                    "estimated_hours": m.estimated_hours,
                    "difficulty": m.difficulty,
                    "resources": m.resources
                }
                for m in result.learning_path.milestones
            ]
            
            learning_path_db = LearningPath(
                analysis_id=analysis_id,
                title=result.learning_path.title,
                total_hours=result.learning_path.total_hours,
                estimated_weeks=result.learning_path.estimated_weeks,
                milestones=milestones_data
            )
            db.add(learning_path_db)
        
        # Update analysis status
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis:
            analysis.status = "completed"
            analysis.completed_at = datetime.utcnow()
        
        db.commit()
        logger.info(f"Analysis {analysis_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error in background analysis {analysis_id}: {str(e)}")
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
    current_user: User = Depends(get_current_user),
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
    
    # Verify user ownership
    if analysis.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to access this analysis"
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
            "missing_skills": analysis.matching_result.missing_skills
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


@app.delete("/api/results/{analysis_id}")
async def delete_analysis(
    analysis_id: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
