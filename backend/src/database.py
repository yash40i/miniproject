"""
Database configuration and models for Resume-Insight AI
Using SQLAlchemy ORM with SQLite for development
"""

from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, JSON, ForeignKey, Text, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database URL - SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./analysis.db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Set to True for SQL query logging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class User(Base):
    """User account model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Password reset fields
    password_reset_token = Column(String(255), nullable=True, unique=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    # OAuth fields
    google_id = Column(String(255), nullable=True, unique=True)
    google_email = Column(String(255), nullable=True)
    oauth_provider = Column(String(50), nullable=True)  # google, github, etc.

    # Gamification
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_active_date = Column(DateTime, nullable=True)

    # Relationships
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")


class Analysis(Base):
    """Main analysis record"""
    __tablename__ = "analyses"

    id = Column(String(36), primary_key=True, index=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    job_description = Column(Text, nullable=False)
    status = Column(String(20), default="processing", index=True)  # processing, completed, failed
    error = Column(Text, nullable=True)
    resume_text = Column(Text, nullable=True)
    adapted_resume_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="analyses")
    matching_result = relationship("MatchingResult", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    learning_path = relationship("LearningPath", back_populates="analysis", uselist=False, cascade="all, delete-orphan")


class MatchingResult(Base):
    """Skill matching results"""
    __tablename__ = "matching_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String(36), ForeignKey("analyses.id"), unique=True, nullable=False)
    overall_score = Column(Float, nullable=False)
    matched_percentage = Column(Float, nullable=False)
    matched_skills = Column(JSON, nullable=False)  # List of matched skills
    missing_skills = Column(JSON, nullable=False)  # List of missing skills
    skill_node_map = Column(JSON, nullable=True)   # Vector-Gap node activation map

    # Relationship
    analysis = relationship("Analysis", back_populates="matching_result")


class Feedback(Base):
    """LLM-generated feedback"""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String(36), ForeignKey("analyses.id"), unique=True, nullable=False)
    gap_analysis = Column(Text, nullable=True)
    recommendations = Column(JSON, nullable=False)  # List of recommendations
    priority_skills = Column(JSON, nullable=False)  # List of priority skills
    next_steps = Column(JSON, nullable=False)  # List of next steps

    # Relationship
    analysis = relationship("Analysis", back_populates="feedback")


class LearningPath(Base):
    """Personalized learning path"""
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String(36), ForeignKey("analyses.id"), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    total_hours = Column(Integer, nullable=False)
    estimated_weeks = Column(Integer, nullable=False)
    milestones = Column(JSON, nullable=False)  # List of milestone objects
    user_profile = Column(JSON, nullable=True)
    overall_progress = Column(Integer, default=0)
    adaptivity_score = Column(Float, default=0.0)
    recommendation_engine_used = Column(String(50), default="static")

    # Relationship
    analysis = relationship("Analysis", back_populates="learning_path")


def get_db():
    """Dependency for FastAPI to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables and run migrations if columns are missing"""
    Base.metadata.create_all(bind=engine)
    
    # Run manual migration check for sqlite
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('analyses')]
        columns_mr = [col['name'] for col in inspector.get_columns('matching_results')]
        columns_lp = [col['name'] for col in inspector.get_columns('learning_paths')]
        columns_users = [col['name'] for col in inspector.get_columns('users')]
        
        with engine.begin() as conn:
            # Enable WAL mode for SQLite to support concurrent reads during writes
            if "sqlite" in str(engine.url):
                conn.execute(text("PRAGMA journal_mode=WAL"))
                print("Database: Enabled WAL mode")
                
            if 'resume_text' not in columns:
                conn.execute(text("ALTER TABLE analyses ADD COLUMN resume_text TEXT"))
                print("Migration: Added resume_text column to analyses")
            if 'adapted_resume_json' not in columns:
                conn.execute(text("ALTER TABLE analyses ADD COLUMN adapted_resume_json TEXT"))
                print("Migration: Added adapted_resume_json column to analyses")
            if 'skill_node_map' not in columns_mr:
                conn.execute(text("ALTER TABLE matching_results ADD COLUMN skill_node_map TEXT"))
                print("Migration: Added skill_node_map column to matching_results")
                
            # Migrations for learning_paths table
            if 'user_profile' not in columns_lp:
                conn.execute(text("ALTER TABLE learning_paths ADD COLUMN user_profile TEXT"))
                print("Migration: Added user_profile column to learning_paths")
            if 'overall_progress' not in columns_lp:
                conn.execute(text("ALTER TABLE learning_paths ADD COLUMN overall_progress INTEGER DEFAULT 0"))
                print("Migration: Added overall_progress column to learning_paths")
            if 'adaptivity_score' not in columns_lp:
                conn.execute(text("ALTER TABLE learning_paths ADD COLUMN adaptivity_score FLOAT DEFAULT 0.0"))
                print("Migration: Added adaptivity_score column to learning_paths")
            if 'recommendation_engine_used' not in columns_lp:
                conn.execute(text("ALTER TABLE learning_paths ADD COLUMN recommendation_engine_used VARCHAR(50) DEFAULT 'static'"))
                print("Migration: Added recommendation_engine_used column to learning_paths")
                
            # Migrations for users table
            if 'current_streak' not in columns_users:
                conn.execute(text("ALTER TABLE users ADD COLUMN current_streak INTEGER DEFAULT 0"))
                print("Migration: Added current_streak column to users")
            if 'longest_streak' not in columns_users:
                conn.execute(text("ALTER TABLE users ADD COLUMN longest_streak INTEGER DEFAULT 0"))
                print("Migration: Added longest_streak column to users")
            if 'last_active_date' not in columns_users:
                conn.execute(text("ALTER TABLE users ADD COLUMN last_active_date DATETIME"))
                print("Migration: Added last_active_date column to users")
    except Exception as e:
        print(f"Database migration warning: {e}")
        
    print("Database initialized successfully")


if __name__ == "__main__":
    init_db()
