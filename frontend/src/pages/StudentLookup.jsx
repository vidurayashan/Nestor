import React, { useState } from 'react';
import { Search, FileText, Video, AlertCircle, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { lookupSubmission, gradeSubmission, listSubmissions } from '../api';

export default function StudentLookup({ assignment }) {
  const [studentId, setStudentId] = useState('');
  const [submission, setSubmission] = useState(null);
  const [loading, setLoading] = useState(false);
  const [grading, setGrading] = useState(false);
  const [error, setError] = useState(null);
  const [gradingOptions, setGradingOptions] = useState({
    video_processing_mode: 'transcript_only',
    frame_sampling_method: 'interval',
    frame_interval: 25
  });
  const navigate = useNavigate();

  const handleLookup = async () => {
    if (!assignment || !studentId.trim()) return;

    setLoading(true);
    setError(null);
    setSubmission(null);

    try {
      const response = await lookupSubmission(assignment.id, studentId.trim());
      setSubmission(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Submission not found');
    } finally {
      setLoading(false);
    }
  };

  const handleGrade = async () => {
    if (!submission) return;

    setGrading(true);
    setError(null);

    try {
      // Find the actual submission ID
      const submissionsResponse = await listSubmissions(assignment.id);
      const fullSubmission = submissionsResponse.data.find(
        s => s.student_id === submission.student_id
      );

      if (!fullSubmission) {
        throw new Error('Submission ID not found');
      }

      await gradeSubmission(fullSubmission.id, gradingOptions);
      
      // Navigate to review page
      navigate(`/review/${fullSubmission.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to grade submission');
    } finally {
      setGrading(false);
    }
  };

  if (!assignment) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">Please create an assignment first</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-3xl font-bold text-gray-900 mb-6">Student Lookup</h2>

      {/* Search */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex space-x-2">
          <input
            type="text"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleLookup()}
            placeholder="Enter student ID..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleLookup}
            disabled={loading || !studentId.trim()}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 flex items-center space-x-2"
          >
            <Search className="h-5 w-5" />
            <span>{loading ? 'Searching...' : 'Lookup'}</span>
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6 flex items-start space-x-2">
          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
          <span className="text-red-800">{error}</span>
        </div>
      )}

      {/* Submission Info */}
      {submission && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="text-xl font-semibold mb-4">
            Submission Found: {submission.student_id}
          </h3>

          <div className="space-y-3">
            {/* Report */}
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <div className="flex items-center space-x-3">
                <FileText className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="font-medium">
                    {submission.report_filename || 'No report'}
                  </p>
                  {submission.report_page_count && (
                    <p className="text-sm text-gray-600">
                      {submission.report_page_count} pages
                    </p>
                  )}
                </div>
              </div>
              {submission.report_filename ? (
                <Check className="h-5 w-5 text-green-600" />
              ) : (
                <AlertCircle className="h-5 w-5 text-red-600" />
              )}
            </div>

            {/* Video */}
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <div className="flex items-center space-x-3">
                <Video className="h-5 w-5 text-purple-600" />
                <div>
                  <p className="font-medium">
                    {submission.video_filename || 'No video'}
                  </p>
                  {submission.video_duration && (
                    <p className="text-sm text-gray-600">
                      {Math.round(submission.video_duration)}s
                    </p>
                  )}
                </div>
              </div>
              {submission.video_filename ? (
                <Check className="h-5 w-5 text-green-600" />
              ) : (
                <AlertCircle className="h-5 w-5 text-yellow-600" />
              )}
            </div>

            {/* Missing files warning */}
            {submission.missing_files.length > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                <p className="text-sm text-yellow-800">
                  Missing expected files: {submission.missing_files.join(', ')}
                </p>
              </div>
            )}

            {/* Status */}
            <div className="pt-2">
              <span className="text-sm font-medium text-gray-700">Status: </span>
              <span className={`text-sm font-semibold ${
                submission.status === 'finalized' ? 'text-green-600' :
                submission.status === 'pending_review' ? 'text-blue-600' :
                'text-gray-600'
              }`}>
                {submission.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Grading Options */}
      {submission && submission.status === 'unprocessed' && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Grading Options</h3>

          <div className="space-y-4">
            {/* Video processing mode */}
            {submission.video_filename && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Video Processing Mode
                  </label>
                  <select
                    value={gradingOptions.video_processing_mode}
                    onChange={(e) => setGradingOptions({
                      ...gradingOptions,
                      video_processing_mode: e.target.value
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="transcript_only">Transcript Only</option>
                    <option value="transcript_and_frames">Transcript + Frames</option>
                  </select>
                </div>

                {gradingOptions.video_processing_mode === 'transcript_and_frames' && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Frame Sampling Method
                      </label>
                      <select
                        value={gradingOptions.frame_sampling_method}
                        onChange={(e) => setGradingOptions({
                          ...gradingOptions,
                          frame_sampling_method: e.target.value
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      >
                        <option value="interval">Fixed Interval</option>
                        <option value="scene_change">Scene Change Detection</option>
                      </select>
                    </div>

                    {gradingOptions.frame_sampling_method === 'interval' && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Frame Interval (seconds)
                        </label>
                        <input
                          type="number"
                          min="10"
                          max="60"
                          value={gradingOptions.frame_interval}
                          onChange={(e) => setGradingOptions({
                            ...gradingOptions,
                            frame_interval: parseInt(e.target.value)
                          })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        />
                      </div>
                    )}
                  </>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* Confirm and Grade */}
      {submission && submission.status === 'unprocessed' && (
        <button
          onClick={handleGrade}
          disabled={grading}
          className="w-full bg-green-600 text-white py-3 px-6 rounded-md hover:bg-green-700 disabled:bg-gray-400 text-lg font-medium"
        >
          {grading ? 'Grading in progress...' : 'Confirm and Mark This Submission'}
        </button>
      )}

      {submission && submission.status === 'pending_review' && (
        <button
          onClick={async () => {
            const submissionsResponse = await listSubmissions(assignment.id);
            const fullSubmission = submissionsResponse.data.find(
              s => s.student_id === submission.student_id
            );
            navigate(`/review/${fullSubmission.id}`);
          }}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 text-lg font-medium"
        >
          Go to Review
        </button>
      )}
    </div>
  );
}
