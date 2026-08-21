from sqlalchemy import (
    Column, Integer, String, Float, Text, JSON, ForeignKey, 
    DateTime, Boolean, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class SubmissionStatus(str, enum.Enum):
    UNPROCESSED = "unprocessed"
    PROCESSING = "processing"
    PENDING_REVIEW = "pending_review"
    FINALIZED = "finalized"


class VideoProcessingMode(str, enum.Enum):
    TRANSCRIPT_ONLY = "transcript_only"
    TRANSCRIPT_AND_FRAMES = "transcript_and_frames"


class FrameSamplingMethod(str, enum.Enum):
    INTERVAL = "interval"
    SCENE_CHANGE = "scene_change"


class Assignment(Base):
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brief = Column(Text, nullable=False)
    rubric_markdown = Column(Text, nullable=False)
    rubric_json = Column(JSON, nullable=False)  # Parsed rubric structure
    expected_files = Column(JSON, nullable=False)  # {"report": true, "video": false}
    cohort_zip_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    submissions = relationship("Submission", back_populates="assignment")


class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(String, nullable=False, index=True)
    folder_path = Column(String, nullable=False)
    
    # File metadata
    report_filename = Column(String, nullable=True)
    report_path = Column(String, nullable=True)
    report_page_count = Column(Integer, nullable=True)
    video_filename = Column(String, nullable=True)
    video_path = Column(String, nullable=True)
    video_duration = Column(Float, nullable=True)  # seconds
    
    # Status tracking
    status = Column(SQLEnum(SubmissionStatus), default=SubmissionStatus.UNPROCESSED)
    
    # Processing metadata
    video_processing_mode = Column(SQLEnum(VideoProcessingMode), nullable=True)
    frame_sampling_method = Column(SQLEnum(FrameSamplingMethod), nullable=True)
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    processing_error = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    assignment = relationship("Assignment", back_populates="submissions")
    grades = relationship("Grade", back_populates="submission", cascade="all, delete-orphan")
    api_usage = relationship("APIUsage", back_populates="submission", cascade="all, delete-orphan")


class Grade(Base):
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    
    criterion_name = Column(String, nullable=False)
    sub_question = Column(Text, nullable=False)
    max_marks = Column(Float, nullable=False)
    
    # AI suggested values
    ai_suggested_mark = Column(Float, nullable=False)
    ai_suggested_comment = Column(Text, nullable=False)
    ai_source = Column(String, nullable=False)  # "report", "video", "both"
    
    # Lecturer finalized values (initially same as AI suggested)
    final_mark = Column(Float, nullable=False)
    final_comment = Column(Text, nullable=False)
    
    # Metadata
    is_modified = Column(Boolean, default=False)  # Track if lecturer changed AI suggestion
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    submission = relationship("Submission", back_populates="grades")


class APIUsage(Base):
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=True)
    
    # API call details
    api_type = Column(String, nullable=False)  # "whisper", "gpt-4o", "gpt-4o-vision"
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    
    # Cost tracking (optional, can be calculated from tokens)
    estimated_cost_usd = Column(Float, nullable=True)
    
    # Context
    operation = Column(String, nullable=False)  # "video_transcription", "report_grading", "video_grading"
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    submission = relationship("Submission", back_populates="api_usage")
