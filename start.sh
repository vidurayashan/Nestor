#!/bin/bash
# Quick start script for the AI Co-Marking App

echo "=========================================="
echo "AI Co-Marking App - Startup Script"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "Error: Run this script from the project root directory"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi
echo "✓ Python found: $(python3 --version)"

if ! command_exists node; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi
echo "✓ Node.js found: $(node --version)"

if ! command_exists ffmpeg; then
    echo "⚠️  Warning: ffmpeg not found. Video processing will fail."
    echo "   Install with: brew install ffmpeg (macOS) or sudo apt install ffmpeg (Linux)"
else
    echo "✓ ffmpeg found"
fi

echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env not found"
    echo "   Copying .env.example..."
    cp backend/.env.example backend/.env
    echo "   Please edit backend/.env and add your OpenAI API key"
    echo ""
    read -p "Press Enter when you've added your API key..."
fi

# Check if venv exists
if [ ! -d "backend/venv" ]; then
    echo "Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
    echo "✓ Virtual environment created"
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✓ Frontend dependencies installed"
fi

# Install/update backend dependencies
echo "Installing/updating backend dependencies..."
cd backend
source venv/bin/activate
pip install -q -r requirements.txt
cd ..
echo "✓ Backend dependencies ready"

echo ""
echo "=========================================="
echo "Starting servers..."
echo "=========================================="
echo ""

# Start backend in background
echo "Starting backend on http://localhost:8000..."
cd backend
source venv/bin/activate
python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start. Check backend.log for errors."
    exit 1
fi
echo "✓ Backend running (PID: $BACKEND_PID)"

# Start frontend in background
echo "Starting frontend on http://localhost:5173..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a bit for frontend to start
sleep 3

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Frontend failed to start. Check frontend.log for errors."
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi
echo "✓ Frontend running (PID: $FRONTEND_PID)"

echo ""
echo "=========================================="
echo "✓ Application is ready!"
echo "=========================================="
echo ""
echo "Open in browser: http://localhost:5173"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Logs:"
echo "  Backend: backend.log"
echo "  Frontend: frontend.log"
echo ""
echo "To stop the servers, press Ctrl+C or run:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Save PIDs to file
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# Wait for interrupt
trap "echo ''; echo 'Shutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .backend.pid .frontend.pid; exit" INT TERM

# Keep script running
wait
