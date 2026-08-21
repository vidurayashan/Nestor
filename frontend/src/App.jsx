import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { Home, FileText, Users, BarChart3, Download } from 'lucide-react';
import AssignmentSetup from './pages/AssignmentSetup';
import StudentLookup from './pages/StudentLookup';
import BatchGrading from './pages/BatchGrading';
import ReviewQueue from './pages/ReviewQueue';
import SubmissionReview from './pages/SubmissionReview';
import APIUsage from './pages/APIUsage';
import Export from './pages/Export';
import { listAssignments } from './api';

function App() {
  const [assignments, setAssignments] = useState([]);
  const [currentAssignment, setCurrentAssignment] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadAssignments();
  }, []);

  const loadAssignments = async () => {
    try {
      const response = await listAssignments();
      setAssignments(response.data);
      if (response.data.length > 0 && !currentAssignment) {
        setCurrentAssignment(response.data[0]);
      }
    } catch (error) {
      console.error('Failed to load assignments:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <FileText className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">
                AI Co-Marking
              </h1>
            </div>
            
            {/* Assignment selector */}
            {assignments.length > 0 && (
              <div className="flex items-center space-x-2">
                <label className="text-sm font-medium text-gray-700">
                  Assignment:
                </label>
                <select
                  value={currentAssignment?.id || ''}
                  onChange={(e) => {
                    const selected = assignments.find(
                      a => a.id === parseInt(e.target.value)
                    );
                    setCurrentAssignment(selected);
                  }}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {assignments.map(a => (
                    <option key={a.id} value={a.id}>{a.name}</option>
                  ))}
                </select>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar Navigation */}
        <nav className="w-64 bg-white shadow-sm min-h-screen">
          <div className="p-4 space-y-2">
            <NavLink to="/" icon={Home} label="Setup Assignment" />
            <NavLink to="/lookup" icon={Users} label="Student Lookup" />
            <NavLink to="/batch" icon={FileText} label="Batch Grading" />
            <NavLink to="/review" icon={FileText} label="Review Queue" />
            <NavLink to="/usage" icon={BarChart3} label="API Usage" />
            <NavLink to="/export" icon={Download} label="Export" />
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 p-8">
          <Routes>
            <Route 
              path="/" 
              element={
                <AssignmentSetup 
                  onAssignmentCreated={loadAssignments}
                  currentAssignment={currentAssignment}
                />
              } 
            />
            <Route 
              path="/lookup" 
              element={<StudentLookup assignment={currentAssignment} />} 
            />
            <Route 
              path="/batch" 
              element={<BatchGrading assignment={currentAssignment} />} 
            />
            <Route 
              path="/review" 
              element={<ReviewQueue assignment={currentAssignment} />} 
            />
            <Route 
              path="/review/:submissionId" 
              element={<SubmissionReview />} 
            />
            <Route 
              path="/usage" 
              element={<APIUsage assignment={currentAssignment} />} 
            />
            <Route 
              path="/export" 
              element={<Export assignment={currentAssignment} />} 
            />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function NavLink({ to, icon: Icon, label }) {
  return (
    <Link
      to={to}
      className="flex items-center space-x-3 px-4 py-2 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-md transition-colors"
    >
      <Icon className="h-5 w-5" />
      <span>{label}</span>
    </Link>
  );
}

export default App;
