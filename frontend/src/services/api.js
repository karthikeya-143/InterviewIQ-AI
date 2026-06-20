import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  uploadResume: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  startInterview: async (skills, projects, technologies, education = [], certifications = []) => {
    const response = await apiClient.post('/interview/start', {
      skills,
      projects,
      technologies,
      education,
      certifications,
    });
    return response.data;
  },

  transcribeAudio: async (audioBlob, questionText) => {
    const formData = new FormData();
    formData.append('file', audioBlob, 'response_audio.webm');
    if (questionText) {
      formData.append('question_text', questionText);
    }

    const response = await apiClient.post('/interview/transcribe', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  evaluateAnswer: async (sessionId, questionId, candidateAnswer) => {
    const response = await apiClient.post('/interview/evaluate', {
      session_id: sessionId,
      question_id: questionId,
      candidate_answer: candidateAnswer,
    });
    return response.data;
  },

  skipQuestion: async (sessionId, questionId) => {
    const response = await apiClient.post('/interview/skip', {
      session_id: sessionId,
      question_id: questionId,
    });
    return response.data;
  },

  getReport: async (sessionId) => {
    const response = await apiClient.post('/interview/report', {
      session_id: sessionId,
    });
    return response.data;
  },
};
