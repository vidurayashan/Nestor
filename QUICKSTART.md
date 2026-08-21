# Quick Start Guide

Get the AI Co-Marking App running in 5 minutes.

## Prerequisites Check

```bash
# Check Python
python --version  # Need 3.10+

# Check Node
node --version    # Need 18+

# Check ffmpeg
ffmpeg -version   # Should show version info
```

If anything is missing, see README.md for installation instructions.

## Setup (First Time Only)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

### 2. Frontend Setup

```bash
cd ../frontend
npm install
```

## Running (Every Time)

### Terminal 1: Start Backend

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```

Wait for: `Uvicorn running on http://0.0.0.0:8000`

### Terminal 2: Start Frontend

```bash
cd frontend
npm run dev
```

Wait for: `Local: http://localhost:5173/`

### Open in Browser

Go to: **http://localhost:5173**

## First Use Tutorial

### Step 1: Create Assignment (2 min)

1. Click "Setup Assignment"
2. Fill in:
   - Name: `Test Assignment`
   - Brief: `Testing the system`
   - Rubric: Copy from `uploads/BUS1004_Assessment1_Rubric_802b.md`
   - Check: Report ✓, Video (optional)
3. Click "Create Assignment"

### Step 2: Upload Sample Cohort (1 min)

1. Create a test zip:
   ```
   test_cohort/
   ├── 12345678_TestStudent/
   │   ├── report.pdf
   │   └── video.mp4 (optional)
   ```
2. Upload the zip
3. Wait for extraction confirmation

### Step 3: Mark One Student (2 min)

1. Go to "Student Lookup"
2. Enter: `12345678`
3. Check files are detected
4. Select "Transcript Only" (faster for testing)
5. Click "Confirm and Mark"
6. Wait ~30-60 seconds

### Step 4: Review Results

1. Go to "Review Queue"
2. Click on the student
3. See AI suggestions
4. Adjust if needed
5. Click "Finalize"

### Step 5: Export

1. Go to "Export"
2. Click "Download CSV"
3. Check the marks file

## Tips

- **Start small**: Test with 1-2 students first
- **Use transcript-only**: Much faster and cheaper for testing
- **Check API usage**: Monitor costs in "API Usage" page
- **Batch processing**: Use 5-10 at a time for production

## Troubleshooting

### "Connection refused" error
- Backend not running. Start it in Terminal 1.

### "API key not found"
- Edit `backend/.env` and add your OpenAI key.

### Video processing fails
- Install ffmpeg: `brew install ffmpeg` (macOS) or `sudo apt install ffmpeg` (Linux)

### Frontend won't load
- Check Terminal 2 for errors
- Try: `cd frontend && npm install` again

## Next Steps

Read the full README.md for:
- Rubric format details
- Batch processing workflows
- Cost optimization
- Backup procedures
