from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import shutil
import json

from database import get_db
from models import (
    Assignment, Submission, Grade, APIUsage,
    SubmissionStatus, VideoProcessingMode, FrameSamplingMethod
)
from schemas import (
    AssignmentCreate, AssignmentResponse,
    SubmissionFileInfo, SubmissionResponse, SubmissionWithGrades,
    GradeResponse, GradeUpdate,
    GradingRequest, BatchGradingRequest,
    APIUsageResponse, APIUsageSummary
)
from rubric_parser import parse_rubric_markdown, validate_rubric_structure
from cohort_extraction import (
    extract_cohort_zip, scan_submissions, get_submission_stats
)
from file_processors import process_report, get_video_duration
from grading_service import GradingService
from config import settings

router = APIRouter()


# Assignment endpoints
@router.post("/assignments", response_model=AssignmentResponse)
async def create_assignment(
    assignment: AssignmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new assignment with rubric parsing"""
    # Parse rubric
    try:
        rubric_json = parse_rubric_markdown(assignment.rubric_markdown)
        is_valid, errors = validate_rubric_structure(rubric_json)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail={"errors": errors})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse rubric: {str(e)}")
    
    # Create assignment
    db_assignment = Assignment(
        name=assignment.name,
        brief=assignment.brief,
        rubric_markdown=assignment.rubric_markdown,
        rubric_json=rubric_json.dict(),
        expected_files=assignment.expected_files
    )
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    
    return db_assignment


@router.get("/assignments", response_model=List[AssignmentResponse])
async def list_assignments(db: Session = Depends(get_db)):
    """List all assignments"""
    return db.query(Assignment).all()


@router.get("/assignments/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """Get assignment by ID"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.post("/assignments/{assignment_id}/upload-cohort")
async def upload_cohort(
    assignment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and extract cohort zip file"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Save uploaded zip
    cohort_dir = settings.upload_dir / f"assignment_{assignment_id}"
    cohort_dir.mkdir(parents=True, exist_ok=True)
    
    zip_path = cohort_dir / "cohort.zip"
    with open(zip_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Extract zip
    extracted_path = cohort_dir / "extracted"
    extract_cohort_zip(zip_path, extracted_path)
    
    # Scan for submissions
    submissions = scan_submissions(extracted_path)
    
    # Create submission records
    created_count = 0
    for sub_data in submissions:
        # Check if already exists
        existing = db.query(Submission).filter(
            Submission.assignment_id == assignment_id,
            Submission.student_id == sub_data.student_id
        ).first()
        
        if existing:
            continue
        
        # Get report metadata
        report_page_count = None
        if sub_data.report_file:
            try:
                processed = process_report(sub_data.report_file)
                report_page_count = processed.page_count
            except:
                pass
        
        # Get video duration
        video_duration = None
        if sub_data.video_file:
            video_duration = get_video_duration(sub_data.video_file)
        
        submission = Submission(
            assignment_id=assignment_id,
            student_id=sub_data.student_id,
            folder_path=str(sub_data.folder_path),
            report_filename=sub_data.report_file.name if sub_data.report_file else None,
            report_path=str(sub_data.report_file) if sub_data.report_file else None,
            report_page_count=report_page_count,
            video_filename=sub_data.video_file.name if sub_data.video_file else None,
            video_path=str(sub_data.video_file) if sub_data.video_file else None,
            video_duration=video_duration,
            status=SubmissionStatus.UNPROCESSED
        )
        db.add(submission)
        created_count += 1
    
    assignment.cohort_zip_path = str(zip_path)
    db.commit()
    
    return {
        "message": f"Extracted {created_count} submissions",
        "total_found": len(submissions)
    }


# Submission endpoints
@router.get("/assignments/{assignment_id}/submissions", response_model=List[SubmissionResponse])
async def list_submissions(
    assignment_id: int,
    status: Optional[SubmissionStatus] = None,
    db: Session = Depends(get_db)
):
    """List submissions for an assignment"""
    query = db.query(Submission).filter(Submission.assignment_id == assignment_id)
    
    if status:
        query = query.filter(Submission.status == status)
    
    return query.all()


@router.get("/submissions/{student_id}", response_model=SubmissionFileInfo)
async def lookup_submission(
    assignment_id: int,
    student_id: str,
    db: Session = Depends(get_db)
):
    """Look up submission by student ID"""
    submission = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.student_id == student_id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Get assignment expected files
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    expected = assignment.expected_files
    
    # Check for missing files
    missing = []
    if expected.get("report") and not submission.report_filename:
        missing.append("report")
    if expected.get("video") and not submission.video_filename:
        missing.append("video")
    
    return SubmissionFileInfo(
        student_id=submission.student_id,
        report_filename=submission.report_filename,
        report_page_count=submission.report_page_count,
        video_filename=submission.video_filename,
        video_duration=submission.video_duration,
        missing_files=missing,
        status=submission.status
    )


# Grading endpoints
@router.post("/submissions/{submission_id}/grade")
async def grade_submission(
    submission_id: int,
    request: GradingRequest,
    db: Session = Depends(get_db)
):
    """Grade a single submission"""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
    
    service = GradingService(db)
    
    try:
        grades = service.grade_submission(
            submission,
            assignment,
            request.video_processing_mode,
            request.frame_sampling_method,
            request.frame_interval
        )
        
        return {
            "message": "Grading complete",
            "student_id": submission.student_id,
            "grades_count": len(grades)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assignments/{assignment_id}/batch-grade")
async def batch_grade(
    assignment_id: int,
    request: BatchGradingRequest,
    db: Session = Depends(get_db)
):
    """Grade a batch of submissions"""
    service = GradingService(db)
    
    try:
        processed = service.batch_grade_submissions(
            assignment_id,
            request.batch_size,
            request.video_processing_mode,
            request.frame_sampling_method,
            request.frame_interval
        )
        
        return {
            "message": f"Batch grading complete",
            "processed_count": len(processed),
            "student_ids": [s.student_id for s in processed]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Review endpoints
@router.get("/submissions/{submission_id}/grades", response_model=SubmissionWithGrades)
async def get_submission_grades(
    submission_id: int,
    db: Session = Depends(get_db)
):
    """Get submission with all grades for review"""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    grades = db.query(Grade).filter(Grade.submission_id == submission_id).all()
    
    total = sum(g.final_mark for g in grades)
    max_total = sum(g.max_marks for g in grades)
    
    return SubmissionWithGrades(
        submission=submission,
        grades=grades,
        total_marks=total,
        max_total_marks=max_total
    )


@router.patch("/grades/{grade_id}")
async def update_grade(
    grade_id: int,
    update: GradeUpdate,
    db: Session = Depends(get_db)
):
    """Update a grade's final mark and comment"""
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    
    grade.final_mark = update.final_mark
    grade.final_comment = update.final_comment
    grade.is_modified = (
        grade.final_mark != grade.ai_suggested_mark or
        grade.final_comment != grade.ai_suggested_comment
    )
    
    db.commit()
    db.refresh(grade)
    
    return grade


@router.post("/submissions/{submission_id}/finalize")
async def finalize_submission(
    submission_id: int,
    db: Session = Depends(get_db)
):
    """Finalize a submission (lock in marks)"""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    submission.status = SubmissionStatus.FINALIZED
    db.commit()
    
    return {"message": "Submission finalized"}


@router.post("/submissions/{submission_id}/reopen")
async def reopen_submission(
    submission_id: int,
    db: Session = Depends(get_db)
):
    """Reopen a finalized submission for editing"""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    submission.status = SubmissionStatus.PENDING_REVIEW
    db.commit()
    
    return {"message": "Submission reopened"}


# API usage tracking
@router.get("/assignments/{assignment_id}/api-usage", response_model=APIUsageSummary)
async def get_api_usage(
    assignment_id: int,
    db: Session = Depends(get_db)
):
    """Get API usage summary for an assignment"""
    # Get all submissions for this assignment
    submission_ids = [
        s.id for s in db.query(Submission.id).filter(
            Submission.assignment_id == assignment_id
        ).all()
    ]
    
    # Get usage records
    usage_records = db.query(APIUsage).filter(
        APIUsage.submission_id.in_(submission_ids)
    ).all()
    
    total_calls = len(usage_records)
    total_tokens = sum(u.total_tokens or 0 for u in usage_records)
    total_cost = sum(u.estimated_cost_usd or 0 for u in usage_records)
    
    # Break down by operation
    by_operation = {}
    for record in usage_records:
        op = record.operation
        if op not in by_operation:
            by_operation[op] = {
                "calls": 0,
                "tokens": 0,
                "cost_usd": 0
            }
        by_operation[op]["calls"] += 1
        by_operation[op]["tokens"] += record.total_tokens or 0
        by_operation[op]["cost_usd"] += record.estimated_cost_usd or 0
    
    return APIUsageSummary(
        total_calls=total_calls,
        total_tokens=total_tokens,
        total_cost_usd=total_cost,
        by_operation=by_operation
    )
