import csv
import io
from pathlib import Path
from typing import List
from openpyxl import Workbook
from sqlalchemy.orm import Session
from models import Assignment, Submission, Grade, SubmissionStatus


def export_marks_csv(assignment: Assignment, db: Session) -> str:
    """Export finalized marks to CSV format"""
    output = io.StringIO()
    
    # Get all finalized submissions
    submissions = db.query(Submission).filter(
        Submission.assignment_id == assignment.id,
        Submission.status == SubmissionStatus.FINALIZED
    ).all()
    
    if not submissions:
        return ""
    
    # Get all grades for these submissions
    submission_ids = [s.id for s in submissions]
    
    # Build header row
    # Get unique criteria from rubric
    from rubric_parser import parse_rubric_markdown
    rubric = parse_rubric_markdown(assignment.rubric_markdown)
    
    criteria_columns = []
    for criterion in rubric.criteria:
        for sub_crit in criterion.sub_criteria:
            criteria_columns.append(f"{criterion.name} - {sub_crit.question[:50]}")
    
    header = ["Student ID"] + criteria_columns + ["Total", "Max Total"]
    
    writer = csv.writer(output)
    writer.writerow(header)
    
    # Write data rows
    for submission in submissions:
        grades = db.query(Grade).filter(
            Grade.submission_id == submission.id
        ).order_by(Grade.id).all()
        
        row = [submission.student_id]
        
        # Add marks for each criterion
        for grade in grades:
            row.append(grade.final_mark)
        
        # Calculate totals
        total = sum(g.final_mark for g in grades)
        max_total = sum(g.max_marks for g in grades)
        
        row.extend([total, max_total])
        writer.writerow(row)
    
    return output.getvalue()


def export_marks_xlsx(assignment: Assignment, db: Session) -> bytes:
    """Export finalized marks to Excel format"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Marks"
    
    # Get all finalized submissions
    submissions = db.query(Submission).filter(
        Submission.assignment_id == assignment.id,
        Submission.status == SubmissionStatus.FINALIZED
    ).all()
    
    if not submissions:
        # Return empty workbook
        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()
    
    # Build header
    from rubric_parser import parse_rubric_markdown
    rubric = parse_rubric_markdown(assignment.rubric_markdown)
    
    criteria_columns = []
    for criterion in rubric.criteria:
        for sub_crit in criterion.sub_criteria:
            criteria_columns.append(f"{criterion.name} - {sub_crit.question[:50]}")
    
    header = ["Student ID"] + criteria_columns + ["Total", "Max Total"]
    ws.append(header)
    
    # Style header
    for cell in ws[1]:
        cell.font = cell.font.copy(bold=True)
    
    # Write data
    for submission in submissions:
        grades = db.query(Grade).filter(
            Grade.submission_id == submission.id
        ).order_by(Grade.id).all()
        
        row = [submission.student_id]
        
        for grade in grades:
            row.append(grade.final_mark)
        
        total = sum(g.final_mark for g in grades)
        max_total = sum(g.max_marks for g in grades)
        
        row.extend([total, max_total])
        ws.append(row)
    
    # Save to bytes
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output.getvalue()


def export_student_feedback(submission: Submission, db: Session) -> str:
    """Export formatted feedback for a single student"""
    grades = db.query(Grade).filter(
        Grade.submission_id == submission.id
    ).order_by(Grade.id).all()
    
    lines = []
    lines.append(f"FEEDBACK FOR STUDENT: {submission.student_id}")
    lines.append("=" * 60)
    lines.append("")
    
    total = 0
    max_total = 0
    
    for grade in grades:
        lines.append(f"{grade.criterion_name}")
        lines.append("-" * 60)
        lines.append(f"Question: {grade.sub_question}")
        lines.append(f"Mark: {grade.final_mark} / {grade.max_marks}")
        lines.append("")
        lines.append("Feedback:")
        lines.append(grade.final_comment)
        lines.append("")
        lines.append("")
        
        total += grade.final_mark
        max_total += grade.max_marks
    
    lines.append("=" * 60)
    lines.append(f"TOTAL MARK: {total} / {max_total}")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def export_all_feedback(assignment: Assignment, db: Session) -> str:
    """Export feedback for all finalized students in one file"""
    submissions = db.query(Submission).filter(
        Submission.assignment_id == assignment.id,
        Submission.status == SubmissionStatus.FINALIZED
    ).all()
    
    all_feedback = []
    
    for submission in submissions:
        feedback = export_student_feedback(submission, db)
        all_feedback.append(feedback)
        all_feedback.append("\n\n" + "=" * 60 + "\n" + "=" * 60 + "\n\n")
    
    return "\n".join(all_feedback)
