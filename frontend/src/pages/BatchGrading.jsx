import React, { useState } from 'react';
import { Play, AlertCircle, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { batchGrade } from '../api';

export default function BatchGrading({ assignment }) {
  const [batchSize, setBatchSize] = useState(5);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [options, setOptions] = useState({
    video_processing_mode: 'transcript_only',
    frame_sampling_method: 'interval',
    frame_interval: 25
  });
  const navigate = useNavigate();

  const handleBatchGrade = async () => {
    if (!assignment) return;

    setProcessing(true);
    setError(null);
    setResult(null);

    try {
      const response = await batchGrade(assignment.id, {
        batch_size: batchSize,
        ...options
      });
      
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Batch grading failed');
    } finally {
      setProcessing(false);
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
      <h2 className="text-3xl font-bold text-gray-900 mb-6">Batch Auto-Mark</h2>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4">Batch Settings</h3>

        <div className="space-y-4">
          {/* Batch size */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Batch Size
            </label>
            <input
              type="number"
              min="1"
              max="50"
              value={batchSize}
              onChange={(e) => setBatchSize(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
            <p className="text-xs text-gray-500 mt-1">
              Number of submissions to process in this batch (1-50)
            </p>
          </div>

          {/* Video processing mode */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Video Processing Mode
            </label>
            <select
              value={options.video_processing_mode}
              onChange={(e) => setOptions({
                ...options,
                video_processing_mode: e.target.value
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="transcript_only">Transcript Only (faster, cheaper)</option>
              <option value="transcript_and_frames">Transcript + Frames (more thorough)</option>
            </select>
          </div>

          {/* Frame sampling */}
          {options.video_processing_mode === 'transcript_and_frames' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Frame Sampling Method
                </label>
                <select
                  value={options.frame_sampling_method}
                  onChange={(e) => setOptions({
                    ...options,
                    frame_sampling_method: e.target.value
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="interval">Fixed Interval</option>
                  <option value="scene_change">Scene Change Detection</option>
                </select>
              </div>

              {options.frame_sampling_method === 'interval' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Frame Interval (seconds)
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="60"
                    value={options.frame_interval}
                    onChange={(e) => setOptions({
                      ...options,
                      frame_interval: parseInt(e.target.value)
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Start batch button */}
      <button
        onClick={handleBatchGrade}
        disabled={processing}
        className="w-full bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 disabled:bg-gray-400 flex items-center justify-center space-x-2 text-lg font-medium mb-6"
      >
        <Play className="h-5 w-5" />
        <span>{processing ? 'Processing batch...' : `Start Batch of ${batchSize}`}</span>
      </button>

      {/* Processing indicator */}
      {processing && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-6">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
            <span className="text-blue-800">
              Processing submissions... This may take several minutes depending on batch size.
            </span>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6 flex items-start space-x-2">
          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
          <span className="text-red-800">{error}</span>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="bg-green-50 border border-green-200 rounded-md p-6">
          <div className="flex items-start space-x-2 mb-4">
            <CheckCircle className="h-6 w-6 text-green-600 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-green-800">
                Batch Complete
              </h3>
              <p className="text-green-700">
                {result.processed_count} submissions processed and ready for review
              </p>
            </div>
          </div>

          {result.student_ids && result.student_ids.length > 0 && (
            <div className="mt-4">
              <p className="text-sm font-medium text-gray-700 mb-2">
                Processed students:
              </p>
              <div className="flex flex-wrap gap-2">
                {result.student_ids.map(id => (
                  <span
                    key={id}
                    className="px-3 py-1 bg-white border border-green-300 rounded-md text-sm"
                  >
                    {id}
                  </span>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={() => navigate('/review')}
            className="mt-4 w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700"
          >
            Go to Review Queue
          </button>
        </div>
      )}

      {/* Info box */}
      <div className="mt-6 bg-gray-50 border border-gray-200 rounded-md p-4">
        <h4 className="font-medium text-gray-900 mb-2">About Batch Processing</h4>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>• Processes only unprocessed submissions</li>
          <li>• Stops after batch size is reached</li>
          <li>• Run multiple batches to work through entire cohort</li>
          <li>• Failed submissions will be skipped (check logs)</li>
        </ul>
      </div>
    </div>
  );
}
