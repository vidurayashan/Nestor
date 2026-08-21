from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import tempfile

from models import (
    Assignment, Submission, Grade, APIUsage,
    SubmissionStatus, VideoProcessingMode, FrameSamplingMethod
)
from file_processors import (
    process_report, extract_audio_from_video,
    sample_video_frames_interval, sample_video_frames_scene_change,
    get_video_duration
)
from openai_client import transcribe_audio, grade_with_gpt, estimate_cost


class GradingService:
    """Orchestrates the grading pipeline for submissions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def grade_submission(
        self,
        submission: Submission,
        assignment: Assignment,
        video_mode: VideoProcessingMode = VideoProcessingMode.TRANSCRIPT_ONLY,
        frame_method: FrameSamplingMethod = FrameSamplingMethod.INTERVAL,
        frame_interval: int = 25
    ) -> List[Grade]:
        """
        Run the complete grading pipeline for a submission.
        Returns list of Grade objects.
        """
        
        # Update status
        submission.status = SubmissionStatus.PROCESSING
        submission.processing_started_at = datetime.utcnow()
        submission.video_processing_mode = video_mode
        submission.frame_sampling_method = frame_method
        submission.processing_error = None
        self.db.commit()
        
        try:
            # Parse rubric
            from rubric_parser import parse_rubric_markdown
            rubric = parse_rubric_markdown(assignment.rubric_markdown)
            
            # Process report
            report_text = ""
            report_images = []
            
            if submission.report_path:
                print(f"Processing report: {submission.report_path}")
                processed_report = process_report(Path(submission.report_path))
                report_text = processed_report.text
                report_images = processed_report.images
                print(f"Extracted {len(report_text)} chars, {len(report_images)} images from report")
            
            # Process video
            video_transcript = None
            video_frames = []
            
            if submission.video_path:
                print(f"Processing video: {submission.video_path}")
                video_path = Path(submission.video_path)
                
                # Extract audio and transcribe
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_audio:
                    tmp_audio_path = Path(tmp_audio.name)
                
                try:
                    extract_audio_from_video(video_path, tmp_audio_path)
                    print("Transcribing audio...")
                    video_transcript, whisper_usage = transcribe_audio(tmp_audio_path)
                    print(f"Transcription complete: {len(video_transcript)} chars")
                    
                    # Log Whisper usage
                    self.log_api_usage(
                        submission.id,
                        "whisper",
                        whisper_usage,
                        "video_transcription"
                    )
                finally:
                    # Clean up temp audio file
                    if tmp_audio_path.exists():
                        tmp_audio_path.unlink()
                
                # Extract frames if requested
                if video_mode == VideoProcessingMode.TRANSCRIPT_AND_FRAMES:
                    print("Extracting video frames...")
                    if frame_method == FrameSamplingMethod.SCENE_CHANGE:
                        video_frames = sample_video_frames_scene_change(video_path)
                    else:
                        video_frames = sample_video_frames_interval(video_path, interval=frame_interval)
                    print(f"Extracted {len(video_frames)} frames")
            
            # Grade with GPT
            print("Sending to GPT for grading...")
            grades_data, gpt_usage = grade_with_gpt(
                criteria=rubric.criteria,
                report_text=report_text,
                report_images=report_images,
                video_transcript=video_transcript,
                video_frames=video_frames,
                assignment_brief=assignment.brief
            )
            
            # Log GPT usage
            api_type = "gpt-4o-vision" if (report_images or video_frames) else "gpt-4o"
            self.log_api_usage(
                submission.id,
                api_type,
                gpt_usage,
                "submission_grading"
            )
            
            print(f"Received {len(grades_data)} grades from GPT")
            
            # Create Grade records
            grades = []
            for grade_data in grades_data:
                grade = Grade(
                    submission_id=submission.id,
                    criterion_name=grade_data["criterion_name"],
                    sub_question=grade_data["sub_question"],
                    max_marks=grade_data["max_marks"],
                    ai_suggested_mark=grade_data["suggested_mark"],
                    ai_suggested_comment=grade_data["suggested_comment"],
                    ai_source=grade_data.get("source", "report"),
                    final_mark=grade_data["suggested_mark"],  # Initially same as suggested
                    final_comment=grade_data["suggested_comment"],
                    is_modified=False
                )
                self.db.add(grade)
                grades.append(grade)
            
            # Update submission status
            submission.status = SubmissionStatus.PENDING_REVIEW
            submission.processing_completed_at = datetime.utcnow()
            self.db.commit()
            
            print(f"Grading complete for {submission.student_id}")
            return grades
            
        except Exception as e:
            # Log error
            submission.status = SubmissionStatus.UNPROCESSED
            submission.processing_error = str(e)
            self.db.commit()
            print(f"Error grading submission {submission.student_id}: {e}")
            raise
    
    def log_api_usage(
        self,
        submission_id: int,
        api_type: str,
        usage: Dict[str, int],
        operation: str
    ):
        """Log API usage for cost tracking"""
        estimated_cost = estimate_cost(usage, api_type)
        
        api_usage = APIUsage(
            submission_id=submission_id,
            api_type=api_type,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
            estimated_cost_usd=estimated_cost,
            operation=operation
        )
        self.db.add(api_usage)
        self.db.commit()
    
    def batch_grade_submissions(
        self,
        assignment_id: int,
        batch_size: int,
        video_mode: VideoProcessingMode,
        frame_method: FrameSamplingMethod,
        frame_interval: int
    ) -> List[Submission]:
        """
        Grade a batch of unprocessed submissions.
        Returns list of processed submissions.
        """
        # Get assignment
        assignment = self.db.query(Assignment).filter(
            Assignment.id == assignment_id
        ).first()
        
        if not assignment:
            raise ValueError(f"Assignment {assignment_id} not found")
        
        # Get unprocessed submissions
        submissions = self.db.query(Submission).filter(
            Submission.assignment_id == assignment_id,
            Submission.status == SubmissionStatus.UNPROCESSED
        ).limit(batch_size).all()
        
        processed = []
        
        for submission in submissions:
            try:
                print(f"\n=== Grading {submission.student_id} ===")
                self.grade_submission(
                    submission,
                    assignment,
                    video_mode,
                    frame_method,
                    frame_interval
                )
                processed.append(submission)
            except Exception as e:
                print(f"Failed to grade {submission.student_id}: {e}")
                # Continue with next submission (resilient to individual failures)
                continue
        
        return processed
