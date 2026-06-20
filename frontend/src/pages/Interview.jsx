import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import useInterviewSession from '../hooks/useInterviewSession';
import FeedbackList from '../components/FeedbackList';
import {
  Mic, Square, RefreshCw, Send, ChevronRight, AlertCircle,
  Volume2, Edit3, CheckCircle, Keyboard, SkipForward,
} from 'lucide-react';

function Interview() {
  const session = useInterviewSession();
  const [questions, setQuestions] = useState([]);
  const [sessionId, setSessionId] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answerMode, setAnswerMode] = useState('voice');

  const [isRecording, setIsRecording] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isEditingTranscript, setIsEditingTranscript] = useState(false);
  const [usedFallback, setUsedFallback] = useState(false);

  const [evaluating, setEvaluating] = useState(false);
  const [evalResult, setEvalResult] = useState(null);
  const [skipping, setSkipping] = useState(false);
  const [error, setError] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const navigate = useNavigate();

  useEffect(() => {
    const savedSessionId = session.getSessionId();
    const savedQuestions = session.getQuestions();

    if (savedSessionId && savedQuestions.length) {
      setSessionId(savedSessionId);
      setQuestions(savedQuestions);
      setCurrentIndex(session.getCurrentIndex());
    } else {
      navigate('/upload');
    }
  }, [navigate, session.getSessionId, session.getQuestions, session.getCurrentIndex]);

  const resetQuestionState = () => {
    setTranscript('');
    setEvalResult(null);
    setError(null);
    setUsedFallback(false);
    setIsEditingTranscript(false);
  };

  const startRecording = async () => {
    setError(null);
    setTranscript('');
    setEvalResult(null);
    setUsedFallback(false);
    audioChunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'audio/webm' });

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        handleTranscription(blob);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) {
      console.error(err);
      setError('Microphone access denied. Switch to Text Answer mode below.');
      setAnswerMode('text');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
      setIsRecording(false);
    }
  };

  const handleTranscription = async (blob) => {
    setTranscribing(true);
    setError(null);
    try {
      const activeQuestion = questions[currentIndex]?.question;
      const response = await api.transcribeAudio(blob, activeQuestion);
      setTranscript(response.transcript);
      setUsedFallback(response.used_fallback || false);
    } catch (err) {
      console.error(err);
      setError('Transcription failed. Edit your answer in the text area below or type it manually.');
      setAnswerMode('text');
    } finally {
      setTranscribing(false);
    }
  };

  const handleEvaluate = async () => {
    if (!transcript.trim()) return;

    setEvaluating(true);
    setError(null);

    try {
      const activeQuestion = questions[currentIndex];
      const response = await api.evaluateAnswer(sessionId, activeQuestion.id, transcript);

      setEvalResult(response);
      session.saveAnswer(activeQuestion.id, transcript);
      session.saveEvaluation(activeQuestion.id, response);
    } catch (err) {
      console.error(err);
      setError('Evaluation failed. Please try submitting again.');
    } finally {
      setEvaluating(false);
    }
  };

  const handleSkip = async () => {
    setSkipping(true);
    setError(null);
    try {
      const activeQuestion = questions[currentIndex];
      await api.skipQuestion(sessionId, activeQuestion.id);

      session.saveAnswer(activeQuestion.id, 'No response provided.');
      session.saveEvaluation(activeQuestion.id, {
        technical_score: 0,
        similarity_score: 0,
        strengths: ['No answer submitted.'],
        weaknesses: ['Candidate skipped this question.'],
        suggestions: ['Answer all questions to receive comprehensive evaluations.'],
      });

      handleNext();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to skip question.');
    } finally {
      setSkipping(false);
    }
  };

  const handleNext = () => {
    const nextIndex = currentIndex + 1;
    if (nextIndex < questions.length) {
      setCurrentIndex(nextIndex);
      localStorage.setItem('currentQuestionIndex', nextIndex.toString());
      resetQuestionState();
    } else {
      navigate('/results');
    }
  };

  const activeQuestion = questions[currentIndex];
  const totalQuestions = questions.length;

  if (!activeQuestion) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <RefreshCw className="h-8 w-8 text-cyber-primary animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-8 animate-fade-in pb-12">
      <div className="flex justify-between items-center bg-white/5 border border-white/10 rounded-2xl px-6 py-4">
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono uppercase bg-cyber-primary/20 border border-cyber-primary/30 text-cyber-primary px-3 py-1 rounded-lg font-bold">
            Question {currentIndex + 1} of {totalQuestions}
          </span>
          <span className="text-xs text-cyber-muted font-medium bg-white/5 px-2.5 py-1 rounded-lg">
            {activeQuestion.category}
          </span>
        </div>
        <div className="w-24 bg-white/10 h-2 rounded-full overflow-hidden">
          <div
            className="bg-cyber-primary h-full transition-all duration-300"
            style={{ width: `${((currentIndex + 1) / totalQuestions) * 100}%` }}
          />
        </div>
      </div>

      <div className="glass-card p-8 rounded-3xl border-l-4 border-l-cyber-primary relative overflow-hidden">
        <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-white leading-snug">
          {activeQuestion.question}
        </h3>
      </div>

      {/* Answer mode toggle */}
      {!evalResult && (
        <div className="flex gap-2 justify-center">
          <button
            onClick={() => setAnswerMode('voice')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
              answerMode === 'voice'
                ? 'bg-cyber-primary/20 border border-cyber-primary/40 text-cyber-primary'
                : 'bg-white/5 border border-white/10 text-cyber-muted hover:text-white'
            }`}
          >
            <Mic className="h-3.5 w-3.5" /> Voice Answer
          </button>
          <button
            onClick={() => setAnswerMode('text')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
              answerMode === 'text'
                ? 'bg-cyber-primary/20 border border-cyber-primary/40 text-cyber-primary'
                : 'bg-white/5 border border-white/10 text-cyber-muted hover:text-white'
            }`}
          >
            <Keyboard className="h-3.5 w-3.5" /> Text Answer
          </button>
        </div>
      )}

      <div className="glass-card p-8 rounded-3xl flex flex-col gap-6 items-center text-center relative">
        {/* Voice mode */}
        {answerMode === 'voice' && !transcript && !transcribing && !evalResult && (
          <div className="flex flex-col items-center gap-4 py-6">
            {!isRecording ? (
              <button
                onClick={startRecording}
                className="h-20 w-20 rounded-full bg-cyber-primary/10 border border-cyber-primary/30 hover:border-cyber-primary hover:bg-cyber-primary/20 text-cyber-primary flex items-center justify-center transition-all duration-300 shadow-[0_0_15px_rgba(99,102,241,0.2)] hover:scale-105"
              >
                <Mic className="h-8 w-8 animate-pulse" />
              </button>
            ) : (
              <button
                onClick={stopRecording}
                className="h-20 w-20 rounded-full bg-cyber-danger/10 border border-cyber-danger/30 hover:border-cyber-danger hover:bg-cyber-danger/20 text-cyber-danger flex items-center justify-center transition-all duration-300"
              >
                <Square className="h-8 w-8" />
              </button>
            )}
            <div className="flex flex-col gap-1">
              <span className="text-sm font-semibold">
                {isRecording ? 'Recording... Click STOP when done.' : 'Click to start voice recording'}
              </span>
              <span className="text-xs text-cyber-muted">WebM format. Speak clearly.</span>
            </div>
            {isRecording && (
              <div className="flex items-center justify-center gap-1 h-8 mt-2">
                {[...Array(8)].map((_, i) => (
                  <div key={i} className="bar bar-active" />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Text mode — always show textarea before evaluation */}
        {answerMode === 'text' && !evalResult && !transcribing && (
          <div className="w-full flex flex-col gap-4 text-left">
            <div className="flex items-center gap-2 text-xs font-semibold text-cyber-muted uppercase tracking-wider">
              <Keyboard className="h-3.5 w-3.5 text-cyber-primary" />
              Type Your Answer
            </div>
            <textarea
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder="Write your answer here in 2–4 sentences..."
              className="w-full h-36 bg-cyber-bg/70 border border-cyber-primary/40 rounded-xl p-4 text-sm text-cyber-text focus:outline-none focus:ring-1 focus:ring-cyber-primary"
            />
            {!evaluating && (
              <div className="flex justify-end gap-3">
                <button
                  onClick={handleEvaluate}
                  disabled={!transcript.trim()}
                  className="btn-primary py-2 px-5 text-xs flex items-center gap-1.5 disabled:opacity-40"
                >
                  <Send className="h-3.5 w-3.5" />
                  Evaluate Answer
                </button>
              </div>
            )}
          </div>
        )}

        {transcribing && (
          <div className="flex flex-col items-center gap-4 py-8">
            <RefreshCw className="h-10 w-10 text-cyber-primary animate-spin" />
            <span className="text-sm font-semibold">Transcribing Answer...</span>
            <span className="text-xs text-cyber-muted">Whisper is processing your audio</span>
          </div>
        )}

        {transcript && !evalResult && answerMode === 'voice' && (
          <div className="w-full flex flex-col gap-4 text-left border border-white/10 bg-cyber-bg/40 rounded-2xl p-6">
            <div className="flex items-center justify-between border-b border-white/5 pb-3">
              <div className="flex items-center gap-2 text-xs font-semibold text-cyber-muted uppercase tracking-wider">
                <Volume2 className="h-3.5 w-3.5 text-cyber-primary" />
                Response Transcript
              </div>
              <button
                onClick={() => setIsEditingTranscript(!isEditingTranscript)}
                className="text-xs flex items-center gap-1.5 hover:text-cyber-primary text-cyber-muted transition-colors"
              >
                <Edit3 className="h-3.5 w-3.5" />
                {isEditingTranscript ? 'Done Editing' : 'Edit Response'}
              </button>
            </div>

            {usedFallback && (
              <div className="text-xs text-cyber-warning bg-cyber-warning/10 border border-cyber-warning/20 rounded-lg px-3 py-2">
                Whisper model unavailable — a placeholder transcript was generated. Please edit before submitting.
              </div>
            )}

            {isEditingTranscript ? (
              <textarea
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
                className="w-full h-32 bg-cyber-bg/70 border border-cyber-primary/40 rounded-xl p-3 text-sm text-cyber-text focus:outline-none focus:ring-1 focus:ring-cyber-primary"
              />
            ) : (
              <p className="text-sm leading-relaxed text-white whitespace-pre-wrap">{transcript}</p>
            )}

            {!evaluating && (
              <div className="flex justify-end gap-3 mt-2 border-t border-white/5 pt-4">
                <button
                  onClick={() => { setTranscript(''); setUsedFallback(false); }}
                  className="btn-secondary py-2 px-4 text-xs"
                >
                  Record Again
                </button>
                <button
                  onClick={handleEvaluate}
                  className="btn-primary py-2 px-5 text-xs flex items-center gap-1.5"
                >
                  <Send className="h-3.5 w-3.5" />
                  Evaluate Answer
                </button>
              </div>
            )}
          </div>
        )}

        {evaluating && (
          <div className="flex flex-col items-center gap-4 py-6 w-full">
            <RefreshCw className="h-8 w-8 text-cyber-primary animate-spin" />
            <span className="text-sm text-cyber-muted">Comparing semantics using Sentence-BERT...</span>
          </div>
        )}

        {evalResult && (
          <div className="w-full flex flex-col gap-6 text-left border border-cyber-success/20 bg-cyber-success/5 rounded-2xl p-6">
            <div className="flex justify-between items-center border-b border-cyber-success/10 pb-3">
              <div className="flex items-center gap-2 text-cyber-success font-semibold text-sm">
                <CheckCircle className="h-5 w-5" /> Evaluation Completed
              </div>
              <div className="flex items-baseline gap-1 bg-cyber-success/15 border border-cyber-success/30 px-3.5 py-1.5 rounded-xl">
                <span className="text-xl font-bold text-cyber-success">{evalResult.technical_score}</span>
                <span className="text-xs text-cyber-success/80">/10</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <FeedbackList title="Strengths" items={evalResult.strengths} variant="strengths" />
              <FeedbackList title="Weaknesses" items={evalResult.weaknesses} variant="weaknesses" />
              <FeedbackList title="Suggestions" items={evalResult.suggestions} variant="suggestions" />
            </div>

            <div className="flex justify-between border-t border-white/5 pt-4">
              <button
                onClick={handleNext}
                className="btn-primary py-2.5 px-6 text-sm bg-gradient-to-r from-cyber-primary to-indigo-600 flex items-center gap-1.5"
              >
                {currentIndex + 1 < totalQuestions ? 'Next Question' : 'View Interview Review'}
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}

        {/* Skip — available before evaluation */}
        {!evalResult && !evaluating && !transcribing && (
          <button
            onClick={handleSkip}
            disabled={skipping}
            className="text-xs text-cyber-muted hover:text-cyber-warning flex items-center gap-1.5 transition-colors"
          >
            <SkipForward className="h-3.5 w-3.5" />
            {skipping ? 'Skipping...' : 'Skip this question'}
          </button>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-3 border border-cyber-danger/30 bg-cyber-danger/5 text-cyber-danger rounded-xl p-4 text-sm">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}

export default Interview;
