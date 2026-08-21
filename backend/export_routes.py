from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
import io

from database import get_db
from models import Assignment, Submission
from export_service import (
    export_marks_csv,
    export_marks_xlsx,
    export_student_feedback,
    export_all_feedback
)

router = APIRouter()


@router.get("/assignments/{assignment_id}/export/marks-csv")
async def export_csv(assignment_id: int, db: Session = Depends(get_db)):
    """Export marks as CSV"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    csv_data = export_marks_csv(assignment, db)
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={assignment.name.replace(' ', '_')}_marks.csv"
        }
    )


@router.get("/assignments/{assignment_id}/export/marks-xlsx")
async def export_excel(assignment_id: int, db: Session = Depends(get_db)):
    """Export marks as Excel"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    xlsx_data = export_marks_xlsx(assignment, db)
    
    return Response(
        content=xlsx_data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={assignment.name.replace(' ', '_')}_marks.xlsx"
        }
    )


@router.get("/submissions/{submission_id}/export/feedback")
async def export_single_feedback(submission_id: int, db: Session = Depends(get_db)):
    """Export feedback for a single student"""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    feedback = export_student_feedback(submission, db)
    
    return Response(
        content=feedback,
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename={submission.student_id}_feedback.txt"
        }
    )


@router.get("/assignments/{assignment_id}/export/all-feedback")
async def export_all_feedbacks(assignment_id: int, db: Session = Depends(get_db)):
    """Export feedback for all finalized students"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    feedback = export_all_feedback(assignment, db)
    
    return Response(
        content=feedback,
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename={assignment.name.replace(' ', '_')}_all_feedback.txt"
        }
    )
