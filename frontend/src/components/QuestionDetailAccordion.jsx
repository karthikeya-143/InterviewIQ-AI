import React from 'react';
import { ChevronDown, ChevronUp, Info } from 'lucide-react';
import FeedbackList from './FeedbackList';

function getScoreColor(score) {
  if (score >= 8.0) return 'text-cyber-success bg-cyber-success/10 border-cyber-success/20';
  if (score >= 5.5) return 'text-cyber-warning bg-cyber-warning/10 border-cyber-warning/20';
  return 'text-cyber-danger bg-cyber-danger/10 border-cyber-danger/20';
}

/**
 * Expandable per-question review card for Results and Dashboard pages.
 */
function QuestionDetailAccordion({ question, candidateAnswer, evaluation, isExpanded, onToggle }) {
  const qEval = evaluation;

  return (
    <div
      className={`glass-card rounded-2xl overflow-hidden border transition-all duration-300 ${
        isExpanded ? 'border-cyber-primary/45 shadow-[0_4px_25px_rgba(99,102,241,0.08)]' : 'border-white/5 hover:border-white/10'
      }`}
    >
      <div
        onClick={onToggle}
        className="flex items-center justify-between p-6 cursor-pointer select-none gap-4"
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && onToggle()}
      >
        <div className="flex items-center gap-4 min-w-0">
          <span className="h-8 w-8 rounded-lg bg-white/5 flex items-center justify-center font-mono text-sm font-bold text-cyber-muted shrink-0">
            {question.id}
          </span>
          <div className="flex flex-col min-w-0 gap-1.5">
            <span className="text-[10px] text-cyber-muted uppercase font-mono font-bold tracking-wide">
              {question.category}
            </span>
            <h4 className="font-semibold text-white truncate text-sm sm:text-base pr-4">
              {question.question}
            </h4>
          </div>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          {qEval ? (
            <span className={`text-xs px-2.5 py-1 rounded-lg border font-bold ${getScoreColor(qEval.technical_score)}`}>
              Score: {qEval.technical_score}
            </span>
          ) : (
            <span className="text-xs px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 text-cyber-muted font-semibold">
              Skipped
            </span>
          )}
          {isExpanded ? <ChevronUp className="h-5 w-5 text-cyber-muted" /> : <ChevronDown className="h-5 w-5 text-cyber-muted" />}
        </div>
      </div>

      {isExpanded && (
        <div className="border-t border-white/5 bg-cyber-bg/20 p-6 flex flex-col gap-6 animate-fade-in">
          <div className="flex flex-col gap-2">
            <span className="text-xs font-mono font-bold text-cyber-muted uppercase tracking-wider">Your Response:</span>
            <div className="bg-cyber-bg/40 border border-white/5 rounded-xl p-4 text-sm text-white leading-relaxed">
              {candidateAnswer || 'No response provided.'}
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <span className="text-xs font-mono font-bold text-cyber-primary uppercase tracking-wider">Expert Reference Answer:</span>
            <div className="bg-cyber-primary/5 border border-cyber-primary/10 rounded-xl p-4 text-sm text-cyber-text leading-relaxed">
              {qEval?.reference_answer || question.reference_answer || 'Reference answer not available.'}
            </div>
          </div>

          {qEval && (
            <>
              <div className="flex gap-4 text-xs">
                <span className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5">
                  Similarity: <strong className="text-cyber-accent">{Math.round((qEval.similarity_score || 0) * 100)}%</strong>
                </span>
                <span className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5">
                  Technical: <strong className="text-cyber-success">{qEval.technical_score}/10</strong>
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 bg-white/[0.01] border border-white/5 p-4 rounded-xl">
                <FeedbackList title="Strengths" items={qEval.strengths} variant="strengths" />
                <FeedbackList title="Weaknesses" items={qEval.weaknesses} variant="weaknesses" />
                <FeedbackList title="Suggestions" items={qEval.suggestions} variant="suggestions" />
              </div>
            </>
          )}

          {!qEval && (
            <div className="flex items-center gap-3 bg-white/5 p-4 rounded-xl text-xs text-cyber-muted">
              <Info className="h-4 w-4 text-cyber-primary shrink-0" />
              <span>This question was skipped. Submit a voice or text answer to see semantic score breakdown.</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default QuestionDetailAccordion;
