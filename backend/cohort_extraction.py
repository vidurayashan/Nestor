import zipfile
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import shutil


class StudentSubmission:
    """Represents a single student's submission"""
    def __init__(self, student_id: str, folder_path: Path):
        self.student_id = student_id
        self.folder_path = folder_path
        self.report_file: Optional[Path] = None
        self.video_file: Optional[Path] = None


def extract_cohort_zip(zip_path: Path, extract_to: Path) -> Path:
    """Extract cohort zip file to specified directory"""
    extract_to.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    
    return extract_to


def extract_student_id_from_name(name: str) -> Optional[str]:
    """
    Auto-detect student ID from various naming patterns:
    - Pure numeric: "12345678"
    - With underscore: "12345678_JohnSmith"
    - With hyphen: "12345678-JohnSmith"
    - With spaces: "12345678 John Smith"
    - Letter prefix: "s12345678", "S12345678"
    """
    patterns = [
        r'^([sS]?\d{6,10})$',  # Pure numeric or with s/S prefix
        r'^([sS]?\d{6,10})[_\-\s]',  # Numeric followed by separator
        r'([sS]?\d{6,10})',  # Any numeric sequence 6-10 digits
    ]
    
    for pattern in patterns:
        match = re.search(pattern, name)
        if match:
            return match.group(1).upper()  # Normalize to uppercase
    
    return None


def find_report_file(folder: Path) -> Optional[Path]:
    """Find PDF or docx report file in folder"""
    for ext in ['.pdf', '.PDF', '.docx', '.DOCX']:
        for file in folder.glob(f'*{ext}'):
            if file.is_file():
                return file
    return None


def find_video_file(folder: Path) -> Optional[Path]:
    """Find video file in folder (mp4, mov, avi, etc.)"""
    for ext in ['.mp4', '.MP4', '.mov', '.MOV', '.avi', '.AVI', '.mkv', '.MKV']:
        for file in folder.glob(f'*{ext}'):
            if file.is_file():
                return file
    return None


def scan_submissions(extracted_path: Path) -> List[StudentSubmission]:
    """
    Scan extracted cohort directory for student submissions.
    Auto-detects student IDs from folder/file names.
    """
    submissions = []
    
    # Handle case where zip contains a single root folder
    items = list(extracted_path.iterdir())
    if len(items) == 1 and items[0].is_dir():
        search_path = items[0]
    else:
        search_path = extracted_path
    
    # Look for student folders
    for item in search_path.iterdir():
        if not item.is_dir():
            continue
        
        # Try to extract student ID from folder name
        student_id = extract_student_id_from_name(item.name)
        if not student_id:
            # Try to extract from file names inside
            for file in item.iterdir():
                if file.is_file():
                    file_student_id = extract_student_id_from_name(file.stem)
                    if file_student_id:
                        student_id = file_student_id
                        break
        
        if not student_id:
            print(f"Warning: Could not extract student ID from folder: {item.name}")
            continue
        
        submission = StudentSubmission(student_id, item)
        submission.report_file = find_report_file(item)
        submission.video_file = find_video_file(item)
        
        submissions.append(submission)
    
    return submissions


def get_submission_stats(submission: StudentSubmission) -> Dict[str, any]:
    """Get basic stats about a submission"""
    stats = {
        'student_id': submission.student_id,
        'folder_path': str(submission.folder_path),
        'has_report': submission.report_file is not None,
        'has_video': submission.video_file is not None,
        'report_filename': submission.report_file.name if submission.report_file else None,
        'video_filename': submission.video_file.name if submission.video_file else None,
    }
    return stats
