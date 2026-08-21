import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Save, Lock, Unlock, ArrowLeft } from 'lucide-react';
import { getSubmissionGrades, updateGrade, finalizeSubmission, reopenSubmission } from '../api';

export default function SubmissionReview() {
  const { submissionId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editedGrades, setEditedGrades] = useState({});

  useEffect(() => {
    loadSubmission();
  }, [submissionId]);

  const loadSubmission = async () => {
    try {
      const response = await getSubmissionGrades(submissionId);
      setData(response.data);
      
      // Initialize edited grades
      const initial = {};
      response.data.grades.forEach(grade => {
        initial[grade.id] = {
          final_mark: grade.final_mark,
          final_comment: grade.final_comment
        };
      });
      setEditedGrades(initial);
    } catch (error) {
      console.error('Failed to load submission:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGradeChange = (gradeId, field, value) => {
    setEditedGrades({
      ...editedGrades,
      [gradeId]: {
        ...editedGrades[gradeId],
        [field]: value
      }
    });
  };

  const handleSave = async (gradeId) => {
    setSaving(true);
    try {
      await updateGrade(gradeId, editedGrades[gradeId]);
      await loadSubmission(); // Reload to get updated data
    } catch (error) {
      console.error('Failed to save grade:', error);
      alert('Failed to save changes');
    } finally {
      setSaving(false);
    }
  };

  const handleFinalize = async () => {
    if (!confirm('Finalize this submission? This will lock in all marks.')) {
      return;
    }

    try {
      await finalizeSubmission(submissionId);
      await loadSubmission();
    } catch (error) {
      console.error('Failed to finalize:', error);
      alert('Failed to finalize submission');
    }
  };

  const handleReopen = async () => {
    if (!confirm('Reopen this submission for editing?')) {
      return;
    }

    try {
      await reopenSubmission(submissionId);
      await loadSubmission();
    } catch (error) {
      console.error('Failed to reopen:', error);
      alert('Failed to reopen submission');
    }
  };

  const calculateTotal = () => {
    return Object.entries(editedGrades).reduce((sum, [gradeId, grade]) => {
      return sum + parseFloat(grade.final_mark || 0);
    }, 0);
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading submission...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Submission not found</p>
      </div>
    );
  }

  const isFinalized = data.submission.status === 'finalized';
  const totalMarks = calculateTotal();

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/review')}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-5 w-5" />
          <span>Back to Queue</span>
        </button>

        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">
              Review: {data.submission.student_id}
            </h2>
            <p className="text-gray-600 mt-1">
              Total: <span className="font-bold text-xl">{totalMarks.toFixed(2)}</span> / {data.max_total_marks}
            </p>
          </div>

          <div className="flex items-center space-x-2">
            {isFinalized ? (
              <button
                onClick={handleReopen}
                className="flex items-center space-x-2 px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700"
              >
                <Unlock className="h-5 w-5" />
                <span>Reopen</span>
              </button>
            ) : (
              <button
                onClick={handleFinalize}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                <Lock className="h-5 w-5" />
                <span>Finalize</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Files info */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center space-x-6 text-sm">
          {data.submission.report_filename && (
            <span className="text-gray-700">
              Report: <span className="font-medium">{data.submission.report_filename}</span>
              {data.submission.report_page_count && (
                <span className="text-gray-500"> ({data.submission.report_page_count} pages)</span>
              )}
            </span>
          )}
          {data.submission.video_filename && (
            <span className="text-gray-700">
              Video: <span className="font-medium">{data.submission.video_filename}</span>
              {data.submission.video_duration && (
                <span className="text-gray-500"> ({Math.round(data.submission.video_duration)}s)</span>
              )}
            </span>
          )}
        </div>
      </div>

      {/* Grades */}
      <div className="space-y-6">
        {data.grades.map((grade) => {
          const edited = editedGrades[grade.id];
          const hasChanges = 
            edited.final_mark !== grade.final_mark ||
            edited.final_comment !== grade.final_comment;

          return (
            <div key={grade.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {grade.criterion_name}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {grade.sub_question}
                  </p>
                </div>
                <div className="text-right ml-4">
                  <p className="text-sm text-gray-600">Max marks</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {grade.max_marks}
                  </p>
                </div>
              </div>

              {/* AI suggestion (read-only reference) */}
              <div className="bg-blue-50 border border-blue-200 rounded p-4 mb-4">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs font-medium text-blue-800 uppercase">
                    AI Suggestion ({grade.ai_source})
                  </p>
                  <p className="text-lg font-bold text-blue-900">
                    {grade.ai_suggested_mark}
                  </p>
                </div>
                <p className="text-sm text-blue-900">
                  {grade.ai_suggested_comment}
                </p>
              </div>

              {/* Editable final grade */}
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Final Mark
                  </label>
                  <input
                    type="number"
                    step="0.25"
                    min="0"
                    max={grade.max_marks}
                    value={edited.final_mark}
                    onChange={(e) => handleGradeChange(grade.id, 'final_mark', parseFloat(e.target.value))}
                    disabled={isFinalized}
                    className="w-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Final Comment
                  </label>
                  <textarea
                    value={edited.final_comment}
                    onChange={(e) => handleGradeChange(grade.id, 'final_comment', e.target.value)}
                    rows={4}
                    disabled={isFinalized}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                  />
                </div>

                {!isFinalized && hasChanges && (
                  <button
                    onClick={() => handleSave(grade.id)}
                    disabled={saving}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    <Save className="h-4 w-4" />
                    <span>{saving ? 'Saving...' : 'Save Changes'}</span>
                  </button>
                )}

                {grade.is_modified && (
                  <p className="text-xs text-gray-500 italic">
                    Modified from AI suggestion
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary bar */}
      <div className="sticky bottom-0 bg-white border-t-2 border-gray-200 shadow-lg rounded-t-lg p-4 mt-8">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Running Total</p>
            <p className="text-2xl font-bold text-gray-900">
              {totalMarks.toFixed(2)} / {data.max_total_marks}
            </p>
          </div>

          {!isFinalized && (
            <button
              onClick={handleFinalize}
              className="flex items-center space-x-2 px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 text-lg font-medium"
            >
              <Lock className="h-5 w-5" />
              <span>Finalize Submission</span>
            </button>
          )}

          {isFinalized && (
            <div className="flex items-center space-x-2 text-green-600">
              <Lock className="h-5 w-5" />
              <span className="font-medium">Finalized</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
