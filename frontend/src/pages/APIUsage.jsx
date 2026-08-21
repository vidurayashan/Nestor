import React, { useState, useEffect } from 'react';
import { DollarSign, Activity, AlertCircle } from 'lucide-react';
import { getAPIUsage } from '../api';

export default function APIUsage({ assignment }) {
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (assignment) {
      loadUsage();
    }
  }, [assignment]);

  const loadUsage = async () => {
    setLoading(true);
    try {
      const response = await getAPIUsage(assignment.id);
      setUsage(response.data);
    } catch (error) {
      console.error('Failed to load API usage:', error);
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

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading usage data...</p>
      </div>
    );
  }

  if (!usage) {
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold text-gray-900 mb-6">API Usage & Costs</h2>

      {/* Summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total API Calls</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {usage.total_calls}
              </p>
            </div>
            <Activity className="h-12 w-12 text-blue-600 opacity-50" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Tokens</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {usage.total_tokens.toLocaleString()}
              </p>
            </div>
            <Activity className="h-12 w-12 text-purple-600 opacity-50" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Estimated Cost</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                ${usage.total_cost_usd.toFixed(2)}
              </p>
            </div>
            <DollarSign className="h-12 w-12 text-green-600 opacity-50" />
          </div>
        </div>
      </div>

      {/* Breakdown by operation */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Breakdown by Operation
          </h3>
        </div>

        <div className="divide-y divide-gray-200">
          {Object.entries(usage.by_operation).map(([operation, data]) => (
            <div key={operation} className="px-6 py-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">
                    {operation.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </p>
                  <p className="text-sm text-gray-600">
                    {data.calls} {data.calls === 1 ? 'call' : 'calls'}
                  </p>
                </div>

                <div className="flex items-center space-x-8 text-right">
                  <div>
                    <p className="text-sm text-gray-600">Tokens</p>
                    <p className="font-semibold text-gray-900">
                      {data.tokens.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Cost</p>
                    <p className="font-semibold text-gray-900">
                      ${data.cost_usd.toFixed(2)}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Info */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-md p-4">
        <h4 className="font-medium text-blue-900 mb-2">About Cost Estimates</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Costs are estimated based on OpenAI's pricing (subject to change)</li>
          <li>• GPT-4o: ~$2.50/1M input tokens, ~$10/1M output tokens</li>
          <li>• Whisper: ~$0.006/minute of audio</li>
          <li>• Using frames significantly increases cost due to vision API usage</li>
        </ul>
      </div>
    </div>
  );
}
