import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { listSubmissions } from '../api';

export default function ReviewQueue({ assignment }) {
  const [submissions, setSubmissions] = useState([]);
  const [filter, setFilter] = useState('pending_review');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (assignment) {
      loadSubmissions();
    }
  }, [assignment, filter]);

  const loadSubmissions = async () => {
    setLoading(true);
    try {
      const response = await listSubmissions(
        assignment.id,
        filter === 'all' ? null : filter
      );
      setSubmissions(response.data);
    } catch (error) {
      console.error('Failed to load submissions:', error);
    } finally {
      setLoading(false);
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

  const getStatusIcon = (status) => {
    switch (status) {
      case 'finalized':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'pending_review':
        return <Clock className="h-5 w-5 text-blue-600" />;
      case 'processing':
        return <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600" />;
      default:
        return <FileText className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'finalized':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'pending_review':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'processing':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <h2 className="text-3xl font-bold text-gray-900 mb-6">Review Queue</h2>

      {/* Filter */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700">Filter:</label>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-md"
          >
            <option value="pending_review">Pending Review</option>
            <option value="finalized">Finalized</option>
            <option value="unprocessed">Unprocessed</option>
            <option value="all">All</option>
          </select>
          <span className="text-sm text-gray-600">
            ({submissions.length} {submissions.length === 1 ? 'submission' : 'submissions'})
          </span>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading submissions...</p>
        </div>
      )}

      {/* Submissions list */}
      {!loading && submissions.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No submissions found for this filter</p>
        </div>
      )}

      {!loading && submissions.length > 0 && (
        <div className="space-y-3">
          {submissions.map((submission) => (
            <div
              key={submission.id}
              className="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-4 cursor-pointer"
              onClick={() => {
                if (submission.status !== 'unprocessed') {
                  navigate(`/review/${submission.id}`);
                }
              }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  {getStatusIcon(submission.status)}
                  
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {submission.student_id}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {submission.report_filename && (
                        <span>Report: {submission.report_filename}</span>
                      )}
                      {submission.video_filename && (
                        <span className="ml-2">• Video: {submission.video_filename}</span>
                      )}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  {submission.processing_error && (
                    <span className="text-xs text-red-600" title={submission.processing_error}>
                      Error
                    </span>
                  )}
                  
                  <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(submission.status)}`}>
                    {submission.status.replace('_', ' ').toUpperCase()}
                  </span>

                  {submission.status !== 'unprocessed' && (
                    <button
                      className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                    >
                      Review →
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
