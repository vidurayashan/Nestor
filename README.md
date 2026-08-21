# AI Co-Marking App for University Assessments

A local, single-user web application that helps university lecturers co-mark student assignments (reports + videos) against structured rubrics using OpenAI's GPT-4o and Whisper APIs.

## Features

- **Assignment Setup**: Upload rubrics (markdown), define expected files, extract cohort submissions
- **Intelligent Grading**: AI-assisted marking using GPT-4o with vision for reports and videos
- **Review Workflow**: Lecturer reviews and adjusts AI suggestions before finalizing
- **Batch Processing**: Process multiple submissions in configurable batches
- **Cost Control**: Configurable video processing modes, API usage tracking
- **Export**: CSV/Excel marks export, formatted feedback export

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, SQLite
- **Frontend**: React, Vite, Tailwind CSS
- **AI**: OpenAI GPT-4o (vision), Whisper
- **File Processing**: pdfplumber, python-docx, ffmpeg

## Prerequisites

- Python 3.10 or higher
- Node.js 18+ and npm
- ffmpeg (for video processing)
- OpenAI API key

### Installing ffmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html and add to PATH.

## Installation

### 1. Clone and Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=sqlite:///./comarking.db
UPLOAD_DIR=./uploads
```

### 2. Setup Frontend

```bash
cd ../frontend

# Install dependencies
npm install
```

## Running the Application

### Start Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

### Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Frontend runs at: http://localhost:5173

## Usage Guide

### 1. Create an Assignment

1. Navigate to "Setup Assignment"
2. Fill in:
   - Assignment name (e.g., "BUS1004 Assessment 1")
   - Assignment brief (context for the AI)
   - Rubric in markdown format (see format below)
   - Expected files (report and/or video)
3. Click "Create Assignment"

### 2. Upload Cohort

1. Prepare a zip file containing student submissions
2. Folder structure should include student IDs (auto-detected patterns):
   - `12345678_StudentName/` folders, OR
   - `s12345678/` folders, OR
   - Files named with student IDs
3. Upload the zip file
4. App extracts and matches student IDs automatically

### 3. Mark Submissions

**Option A: Single Student**
1. Go to "Student Lookup"
2. Enter student ID
3. Review detected files
4. Choose video processing options
5. Click "Confirm and Mark"

**Option B: Batch Mode**
1. Go to "Batch Grading"
2. Set batch size (e.g., 5)
3. Configure video processing mode:
   - **Transcript Only**: Faster, cheaper
   - **Transcript + Frames**: More thorough, sees diagrams
4. Click "Start Batch"

### 4. Review and Finalize

1. Go to "Review Queue"
2. Click on a submission in "Pending Review"
3. Review AI suggestions (blue boxes)
4. Edit marks and comments as needed
5. Click "Finalize" to lock in marks

### 5. Export Results

1. Go to "Export"
2. Download marks as CSV or Excel
3. Download formatted feedback for students

## Rubric Format

Rubrics must be in this exact markdown format:

```markdown
## Criterion Name (X marks)

**Question text for this criterion**

(score) Band comment for this score
(score) Band comment for this score
(0) Lowest band comment

## Another Criterion (Y marks)

**First question**

(score) Band comment
...

**Second question (if multiple sub-criteria)**

(score) Band comment
...
```

**Example:**

```markdown
## Business Problem & Context (3 marks)

**Does the student identify a specific, complex, and well-contextualised real-world business problem?**

(3) Excellent identification of a specific, complex business problem, with strong industry context and clear relevance.
(2.5) Good identification of a specific, complex business problem, with strong industry context and clear relevance.
(2) You have identified a relevant business problem with reasonable specificity and context.
(1) The business problem is adequately defined but leans towards a generic example.
(0) A clear, specific business problem has not been established.
```

## Video Processing Modes

### Transcript Only
- Extracts audio from video
- Transcribes using Whisper
- Grades based on transcript + report
- **Best for**: prompt engineering demonstrations, verbal explanations
- **Cost**: Lower (~$0.01-0.02 per video)

### Transcript + Frames
- Everything in Transcript Only, PLUS
- Samples frames from video (every 20-30 seconds or scene changes)
- GPT-4o vision analyzes frames for diagrams, demonstrations
- **Best for**: checking hand-drawn diagrams, visual demonstrations
- **Cost**: Higher (~$0.10-0.30 per video depending on length)

## Cost Management

- API usage tracked per submission
- View costs in "API Usage" page
- Batch size limits prevent runaway costs
- Choose processing mode per batch
- Estimated costs (2024 pricing):
  - Whisper: ~$0.006/minute of audio
  - GPT-4o text: ~$0.01-0.05 per report
  - GPT-4o vision: +$0.05-0.20 per video with frames

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.10+)
- Activate virtual environment
- Check .env file has valid OPENAI_API_KEY
- Check port 8000 is not in use

### Frontend won't start
- Check Node version: `node --version` (need 18+)
- Run `npm install` again
- Check port 5173 is not in use

### Video processing fails
- Ensure ffmpeg is installed: `ffmpeg -version`
- Check video file format (mp4, mov, avi supported)
- Check file isn't corrupted

### Rubric parsing errors
- Verify markdown format exactly matches expected structure
- Check that all scores are numbers
- Ensure each criterion has at least one question and band

### OpenAI API errors
- Check API key is valid and has credits
- Check internet connection
- Rate limits: space out large batches if hitting limits

## Database Backup

The SQLite database is a single file: `backend/comarking.db`

**To backup:**
```bash
cp backend/comarking.db backend/comarking_backup_$(date +%Y%m%d).db
```

**To restore:**
```bash
cp backend/comarking_backup_YYYYMMDD.db backend/comarking.db
```

## Security Notes

- **Local only**: Not designed for internet deployment
- **Single user**: No authentication system
- **API key**: Store in .env, never commit to git
- **Student data**: Keep backups secure, comply with privacy laws

## File Structure

```
.
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── models.py            # Database models
│   ├── routes.py            # API endpoints
│   ├── schemas.py           # Pydantic schemas
│   ├── rubric_parser.py     # Markdown rubric parser
│   ├── cohort_extraction.py # Zip processing
│   ├── file_processors.py   # PDF/docx/video processing
│   ├── openai_client.py     # OpenAI API integration
│   ├── grading_service.py   # Grading orchestration
│   ├── export_service.py    # Export functionality
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main app component
│   │   ├── api.js           # API client
│   │   └── pages/           # Page components
│   └── package.json         # Node dependencies
└── README.md
```

## License

For internal university use only.

## Support

For issues or questions, contact the development team.
