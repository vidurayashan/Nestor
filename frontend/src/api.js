import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Assignments
export const createAssignment = (data) => api.post('/assignments', data);
export const listAssignments = () => api.get('/assignments');
export const getAssignment = (id) => api.get(`/assignments/${id}`);
export const uploadCohort = (assignmentId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post(`/assignments/${assignmentId}/upload-cohort`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// Submissions
export const listSubmissions = (assignmentId, status = null) => {
  const params = status ? { status } : {};
  return api.get(`/assignments/${assignmentId}/submissions`, { params });
};
export const lookupSubmission = (assignmentId, studentId) => 
  api.get(`/submissions/${studentId}`, { params: { assignment_id: assignmentId } });

// Grading
export const gradeSubmission = (submissionId, options) =>
  api.post(`/submissions/${submissionId}/grade`, options);
export const batchGrade = (assignmentId, options) =>
  api.post(`/assignments/${assignmentId}/batch-grade`, options);

// Review
export const getSubmissionGrades = (submissionId) =>
  api.get(`/submissions/${submissionId}/grades`);
export const updateGrade = (gradeId, data) =>
  api.patch(`/grades/${gradeId}`, data);
export const finalizeSubmission = (submissionId) =>
  api.post(`/submissions/${submissionId}/finalize`);
export const reopenSubmission = (submissionId) =>
  api.post(`/submissions/${submissionId}/reopen`);

// API Usage
export const getAPIUsage = (assignmentId) =>
  api.get(`/assignments/${assignmentId}/api-usage`);

export default api;
