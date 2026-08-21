import React from 'react';
import { Download, FileText, FileSpreadsheet, AlertCircle } from 'lucide-react';

export default function Export({ assignment }) {
  if (!assignment) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">Please create an assignment first</p>
      </div>
    );
  }

  const handleExport = (endpoint) => {
    window.open(`/api${endpoint}`, '_blank');
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-3xl font-bold text-gray-900 mb-6">Export</h2>

      <div className="space-y-4">
        {/* Marks exports */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Export Marks</h3>
          <p className="text-sm text-gray-600 mb-4">
            Export finalized marks for all students in this assignment.
          </p>
          
          <div className="flex space-x-3">
            <button
              onClick={() => handleExport(`/assignments/${assignment.id}/export/marks-csv`)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              <FileText className="h-5 w-5" />
              <span>Download CSV</span>
            </button>
            
            <button
              onClick={() => handleExport(`/assignments/${assignment.id}/export/marks-xlsx`)}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              <FileSpreadsheet className="h-5 w-5" />
              <span>Download Excel</span>
            </button>
          </div>
        </div>

        {/* Feedback export */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Export Feedback</h3>
          <p className="text-sm text-gray-600 mb-4">
            Export formatted feedback comments for all finalized students.
          </p>
          
          <button
            onClick={() => handleExport(`/assignments/${assignment.id}/export/all-feedback`)}
            className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
          >
            <Download className="h-5 w-5" />
            <span>Download All Feedback (TXT)</span>
          </button>
        </div>
      </div>

      <div className="mt-6 bg-gray-50 border border-gray-200 rounded-md p-4">
        <h4 className="font-medium text-gray-900 mb-2">Export Notes</h4>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>• Only finalized submissions are included in exports</li>
          <li>• CSV/Excel files contain student IDs and marks per criterion</li>
          <li>• Feedback files contain full comments formatted for students</li>
          <li>• Individual feedback can be exported from each submission's review page</li>
        </ul>
      </div>
    </div>
  );
}
