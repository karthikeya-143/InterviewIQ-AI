/**
 * Shared hook for reading/writing interview session data in localStorage.
 * Functions are memoized so they are safe to use in useEffect dependency arrays.
 */
import { useCallback, useMemo } from 'react';

export function useInterviewSession() {
  const getSessionId = useCallback(
    () => localStorage.getItem('interviewSessionId') || '',
    []
  );

  const getQuestions = useCallback(() => {
    const raw = localStorage.getItem('interviewQuestions');
    return raw ? JSON.parse(raw) : [];
  }, []);

  const getCandidateAnswers = useCallback(() => {
    const raw = localStorage.getItem('candidateAnswers');
    return raw ? JSON.parse(raw) : {};
  }, []);

  const getEvaluations = useCallback(() => {
    const raw = localStorage.getItem('questionEvaluations');
    return raw ? JSON.parse(raw) : {};
  }, []);

  const getCurrentIndex = useCallback(() => {
    const raw = localStorage.getItem('currentQuestionIndex');
    return raw ? parseInt(raw, 10) : 0;
  }, []);

  const saveAnswer = useCallback((questionId, transcript) => {
    const raw = localStorage.getItem('candidateAnswers');
    const saved = raw ? JSON.parse(raw) : {};
    saved[questionId] = transcript;
    localStorage.setItem('candidateAnswers', JSON.stringify(saved));
  }, []);

  const saveEvaluation = useCallback((questionId, evaluation) => {
    const raw = localStorage.getItem('questionEvaluations');
    const saved = raw ? JSON.parse(raw) : {};
    saved[questionId] = evaluation;
    localStorage.setItem('questionEvaluations', JSON.stringify(saved));
  }, []);

  const clearSession = useCallback(() => {
    [
      'interviewSessionId',
      'interviewQuestions',
      'currentQuestionIndex',
      'candidateAnswers',
      'questionEvaluations',
      'extractedResume',
    ].forEach((key) => localStorage.removeItem(key));
  }, []);

  return useMemo(
    () => ({
      getSessionId,
      getQuestions,
      getCandidateAnswers,
      getEvaluations,
      getCurrentIndex,
      saveAnswer,
      saveEvaluation,
      clearSession,
    }),
    [
      getSessionId,
      getQuestions,
      getCandidateAnswers,
      getEvaluations,
      getCurrentIndex,
      saveAnswer,
      saveEvaluation,
      clearSession,
    ]
  );
}

export default useInterviewSession;
