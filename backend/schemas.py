from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from models import SubmissionStatus, VideoProcessingMode, FrameSamplingMethod


# Rubric structures
class BandComment(BaseModel):
    score: float
    comment: str


class SubCriterion(BaseModel):
    question: str
    bands: List[BandComment]


class Criterion(BaseModel):
    name: str
    max_marks: float
    sub_criteria: List[SubCriterion]


class RubricStructure(BaseModel):
    criteria: List[Criterion]


# Assignment schemas
class AssignmentCreate(BaseModel):
    name: str
    brief: str
    rubric_markdown: str
    expected_files: Dict[str, bool] = Field(
        example={"report": True, "video": False}
    )


class AssignmentResponse(BaseModel):
    id: int
    name: str
    brief: str
    rubric_markdown: str
    rubric_json: RubricStructure
    expected_files: Dict[str, bool]
    cohort_zip_path: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Submission schemas
class SubmissionFileInfo(BaseModel):
    student_id: str
    report_filename: Optional[str]
    report_page_count: Optional[int]
    video_filename: Optional[str]
    video_duration: Optional[float]
    missing_files: List[str]
    status: SubmissionStatus


class SubmissionResponse(BaseModel):
    id: int
    assignment_id: int
    student_id: str
    folder_path: str
    report_filename: Optional[str]
    report_path: Optional[str]
    report_page_count: Optional[int]
    video_filename: Optional[str]
    video_path: Optional[str]
    video_duration: Optional[float]
    status: SubmissionStatus
    video_processing_mode: Optional[VideoProcessingMode]
    processing_error: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Grading schemas
class GradeResponse(BaseModel):
    id: int
    criterion_name: str
    sub_question: str
    max_marks: float
    ai_suggested_mark: float
    ai_suggested_comment: str
    ai_source: str
    final_mark: float
    final_comment: str
    is_modified: bool
    
    class Config:
        from_attributes = True


class GradeUpdate(BaseModel):
    final_mark: float
    final_comment: str


class SubmissionWithGrades(BaseModel):
    submission: SubmissionResponse
    grades: List[GradeResponse]
    total_marks: float
    max_total_marks: float


# Grading request
class GradingRequest(BaseModel):
    video_processing_mode: VideoProcessingMode = VideoProcessingMode.TRANSCRIPT_ONLY
    frame_sampling_method: FrameSamplingMethod = FrameSamplingMethod.INTERVAL
    frame_interval: int = 25  # seconds


class BatchGradingRequest(BaseModel):
    batch_size: int = Field(ge=1, le=50)
    video_processing_mode: VideoProcessingMode = VideoProcessingMode.TRANSCRIPT_ONLY
    frame_sampling_method: FrameSamplingMethod = FrameSamplingMethod.INTERVAL
    frame_interval: int = 25


# API Usage
class APIUsageResponse(BaseModel):
    id: int
    api_type: str
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]
    estimated_cost_usd: Optional[float]
    operation: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class APIUsageSummary(BaseModel):
    total_calls: int
    total_tokens: int
    total_cost_usd: float
    by_operation: Dict[str, Dict[str, Any]]
