import React, { useState } from 'react';
import { Upload, FileText, Check, AlertCircle } from 'lucide-react';
import { createAssignment, uploadCohort } from '../api';

export default function AssignmentSetup({ onAssignmentCreated, currentAssignment }) {
  const [formData, setFormData] = useState({
    name: '',
    brief: '',
    rubric_markdown: '',
    expected_files: { report: true, video: false }
  });
  const [cohortFile, setCohortFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [uploadingCohort, setUploadingCohort] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const response = await createAssignment(formData);
      setMessage({ type: 'success', text: `Assignment "${response.data.name}" created successfully!` });
      onAssignmentCreated();
      
      // Reset form
      setFormData({
        name: '',
        brief: '',
        rubric_markdown: '',
        expected_files: { report: true, video: false }
      });
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to create assignment';
      setMessage({ type: 'error', text: errorMsg });
    } finally {
      setLoading(false);
    }
  };

  const handleCohortUpload = async () => {
    if (!cohortFile || !currentAssignment) return;

    setUploadingCohort(true);
    setMessage(null);

    try {
      const response = await uploadCohort(currentAssignment.id, cohortFile);
      setMessage({ 
        type: 'success', 
        text: `Extracted ${response.data.total_found} submissions` 
      });
      setCohortFile(null);
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to upload cohort';
      setMessage({ type: 'error', text: errorMsg });
    } finally {
      setUploadingCohort(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold text-gray-900 mb-6">Assignment Setup</h2>

      {message && (
        <div className={`mb-6 p-4 rounded-md flex items-start space-x-2 ${
          message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
        }`}>
          {message.type === 'success' ? (
            <Check className="h-5 w-5 mt-0.5" />
          ) : (
            <AlertCircle className="h-5 w-5 mt-0.5" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      {/* Create Assignment Form */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h3 className="text-xl font-semibold mb-4">Create New Assignment</h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Assignment Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., BUS1004 Assessment 1"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Assignment Brief
            </label>
            <textarea
              value={formData.brief}
              onChange={(e) => setFormData({ ...formData, brief: e.target.value })}
              rows={6}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Provide context about what the assignment asks for..."
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Rubric (Markdown)
            </label>
            <textarea
              value={formData.rubric_markdown}
              onChange={(e) => setFormData({ ...formData, rubric_markdown: e.target.value })}
              rows={12}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              placeholder="## Criterion Name (X marks)&#10;&#10;**Question text**&#10;&#10;(score) Band comment&#10;..."
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Expected Files per Submission
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.expected_files.report}
                  onChange={(e) => setFormData({
                    ...formData,
                    expected_files: { ...formData.expected_files, report: e.target.checked }
                  })}
                  className="h-4 w-4 text-blue-600 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">Report (PDF or docx)</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.expected_files.video}
                  onChange={(e) => setFormData({
                    ...formData,
                    expected_files: { ...formData.expected_files, video: e.target.checked }
                  })}
                  className="h-4 w-4 text-blue-600 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">Video</span>
              </label>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
          >
            {loading ? 'Creating...' : 'Create Assignment'}
          </button>
        </form>
      </div>

      {/* Upload Cohort */}
      {currentAssignment && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold mb-4">
            Upload Cohort for: {currentAssignment.name}
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cohort Zip File
              </label>
              <div className="flex items-center space-x-2">
                <label className="flex-1 cursor-pointer">
                  <div className="border-2 border-dashed border-gray-300 rounded-md p-4 hover:border-blue-500 transition-colors">
                    <div className="flex items-center justify-center space-x-2">
                      <Upload className="h-5 w-5 text-gray-400" />
                      <span className="text-sm text-gray-600">
                        {cohortFile ? cohortFile.name : 'Click to select zip file'}
                      </span>
                    </div>
                  </div>
                  <input
                    type="file"
                    accept=".zip"
                    onChange={(e) => setCohortFile(e.target.files[0])}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            <button
              onClick={handleCohortUpload}
              disabled={!cohortFile || uploadingCohort}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400 transition-colors"
            >
              {uploadingCohort ? 'Uploading...' : 'Upload and Extract Cohort'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
