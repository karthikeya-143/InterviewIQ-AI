import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';
import useInterviewSession from '../hooks/useInterviewSession';
import QuestionDetailAccordion from '../components/QuestionDetailAccordion';
import { BarChart2, RefreshCw, AlertTriangle } from 'lucide-react';

function Results() {
  const session = useInterviewSession();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedId, setExpandedId] = useState(1);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchReport = async () => {
      const sessionId = session.getSessionId();
      if (!sessionId) {
        navigate('/upload');
        return;
      }

      setLoading(true);
      try {
        const response = await api.getReport(sessionId);
        setReport(response);
      } catch (err) {
        console.error(err);
        // Fall back to localStorage if server session expired
        const questions = session.getQuestions();
        if (questions.length) {
          setReport({
            details: questions.map((q) => ({
              id: q.id,
              question: q.question,
              category: q.category,
              candidate_answer: session.getCandidateAnswers()[q.id] || 'No response provided.',
              reference_answer: session.getEvaluations()[q.id]?.reference_answer || '',
              similarity_score: session.getEvaluations()[q.id]?.similarity_score || 0,
              technical_score: session.getEvaluations()[q.id]?.technical_score || 0,
              strengths: session.getEvaluations()[q.id]?.strengths || [],
              weaknesses: session.getEvaluations()[q.id]?.weaknesses || [],
              suggestions: session.getEvaluations()[q.id]?.suggestions || [],
            })),
          });
        } else {
          setError('No interview data found. Please complete an interview first.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [navigate, session.getSessionId, session.getQuestions, session.getCandidateAnswers, session.getEvaluations]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
        <RefreshCw className="h-10 w-10 text-cyber-primary animate-spin" />
        <span className="text-cyber-muted text-sm">Loading interview review...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-md mx-auto flex flex-col items-center text-center gap-4 py-12">
        <AlertTriangle className="h-12 w-12 text-cyber-danger" />
        <p className="text-cyber-muted text-sm">{error}</p>
        <Link to="/upload" className="btn-primary">Start New Session</Link>
      </div>
    );
  }

  const details = report?.details || [];

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-8 animate-fade-in pb-12">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex flex-col gap-2">
          <h2 className="text-3xl font-bold tracking-tight text-white">Interview Review</h2>
          <p className="text-cyber-muted">
            Review your answers alongside reference responses, similarity scores, and feedback.
          </p>
        </div>
        <Link
          to="/dashboard"
          className="btn-primary flex items-center justify-center gap-2 py-3 px-6 shadow-[0_0_15px_rgba(99,102,241,0.4)]"
        >
          <BarChart2 className="h-4 w-4" />
          View Dashboard Report
        </Link>
      </div>

      <div className="flex flex-col gap-4">
        {details.map((item) => (
          <QuestionDetailAccordion
            key={item.id}
            question={{ id: item.id, question: item.question, category: item.category, reference_answer: item.reference_answer }}
            candidateAnswer={item.candidate_answer}
            evaluation={{
              technical_score: item.technical_score,
              similarity_score: item.similarity_score,
              reference_answer: item.reference_answer,
              strengths: item.strengths,
              weaknesses: item.weaknesses,
              suggestions: item.suggestions,
            }}
            isExpanded={expandedId === item.id}
            onToggle={() => setExpandedId(expandedId === item.id ? null : item.id)}
          />
        ))}
      </div>
    </div>
  );
}

export default Results;
