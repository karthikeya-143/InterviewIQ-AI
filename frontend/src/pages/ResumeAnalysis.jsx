import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';
import { Award, Code, BookOpen, Shield, Play, ArrowLeft, Loader2, Sparkles } from 'lucide-react';

function ResumeAnalysis() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch parsed resume from localStorage
    const savedData = localStorage.getItem('extractedResume');
    if (savedData) {
      try {
        setData(JSON.parse(savedData));
      } catch (e) {
        console.error('Failed to parse saved resume:', e);
        setError('Failed to load resume details. Please upload again.');
      }
    } else {
      navigate('/upload');
    }
  }, [navigate]);

  const handleStartInterview = async () => {
    if (!data) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Call start interview API
      const response = await api.startInterview(
        data.skills,
        data.projects,
        data.technologies,
        data.education || [],
        data.certifications || []
      );
      
      // Store session data in localStorage
      localStorage.setItem('interviewSessionId', response.session_id);
      localStorage.setItem('interviewQuestions', JSON.stringify(response.questions));
      localStorage.setItem('currentQuestionIndex', '0');
      // Reset answers database in local session
      localStorage.removeItem('candidateAnswers');
      localStorage.removeItem('questionEvaluations');
      
      // Navigate to interview session room
      navigate('/interview');
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to initialize the interview coach. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!data) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 text-cyber-primary animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex flex-col gap-2">
          <h2 className="text-3xl font-bold tracking-tight">Profile Extraction Results</h2>
          <p className="text-cyber-muted">Review the parsed credentials before launching your mock interview session.</p>
        </div>
        <Link 
          to="/upload" 
          className="btn-secondary flex items-center justify-center gap-2 py-2.5 px-4 text-sm"
        >
          <ArrowLeft className="h-4 w-4" />
          Re-Upload
        </Link>
      </div>

      {/* Main Extracted Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Left Column: Skills & Tech */}
        <div className="flex flex-col gap-8">
          {/* Technical Skills Card */}
          <div className="glass-card p-6 rounded-2xl flex flex-col gap-4">
            <div className="flex items-center gap-3 border-b border-white/5 pb-3">
              <Code className="h-5 w-5 text-cyber-primary" />
              <h3 className="text-lg font-bold">Technical Skills</h3>
            </div>
            
            {data.skills.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {data.skills.map((skill, index) => (
                  <span 
                    key={index}
                    className="bg-cyber-primary/10 border border-cyber-primary/25 text-cyber-primary rounded-lg px-3 py-1.5 text-xs font-semibold"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            ) : (
              <span className="text-sm text-cyber-muted italic">No core technical skills identified.</span>
            )}
          </div>

          {/* Technologies Card */}
          <div className="glass-card p-6 rounded-2xl flex flex-col gap-4">
            <div className="flex items-center gap-3 border-b border-white/5 pb-3">
              <Sparkles className="h-5 w-5 text-cyber-accent" />
              <h3 className="text-lg font-bold">Technologies & Tools</h3>
            </div>
            
            {data.technologies.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {data.technologies.map((tech, index) => (
                  <span 
                    key={index}
                    className="bg-cyber-accent/10 border border-cyber-accent/25 text-cyber-accent rounded-lg px-3 py-1.5 text-xs font-semibold"
                  >
                    {tech}
                  </span>
                ))}
              </div>
            ) : (
              <span className="text-sm text-cyber-muted italic">No tools or infrastructure technologies identified.</span>
            )}
          </div>

          {/* Education Card */}
          <div className="glass-card p-6 rounded-2xl flex flex-col gap-4">
            <div className="flex items-center gap-3 border-b border-white/5 pb-3">
              <BookOpen className="h-5 w-5 text-cyber-secondary" />
              <h3 className="text-lg font-bold">Education</h3>
            </div>
            
            {data.education.length > 0 ? (
              <ul className="flex flex-col gap-3">
                {data.education.map((edu, index) => (
                  <li key={index} className="text-sm border-l-2 border-cyber-secondary/50 pl-3 py-0.5">
                    {edu}
                  </li>
                ))}
              </ul>
            ) : (
              <span className="text-sm text-cyber-muted italic">No educational markers identified.</span>
            )}
          </div>
        </div>

        {/* Right Column: Projects & Certifications */}
        <div className="flex flex-col gap-8">
          {/* Projects Card */}
          <div className="glass-card p-6 rounded-2xl flex flex-col gap-4">
            <div className="flex items-center gap-3 border-b border-white/5 pb-3">
              <Award className="h-5 w-5 text-cyber-success" />
              <h3 className="text-lg font-bold">Extracted Projects</h3>
            </div>
            
            {data.projects.length > 0 ? (
              <ul className="flex flex-col gap-4">
                {data.projects.map((proj, index) => (
                  <li key={index} className="flex flex-col border border-white/5 bg-white/[0.02] rounded-xl p-3.5 gap-1 hover:bg-white/[0.04] transition-colors">
                    <span className="text-sm font-semibold text-white">{proj}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <span className="text-sm text-cyber-muted italic">No distinct projects detected in resume structure.</span>
            )}
          </div>

          {/* Certifications Card */}
          <div className="glass-card p-6 rounded-2xl flex flex-col gap-4">
            <div className="flex items-center gap-3 border-b border-white/5 pb-3">
              <Shield className="h-5 w-5 text-cyber-warning" />
              <h3 className="text-lg font-bold">Certifications</h3>
            </div>
            
            {data.certifications.length > 0 ? (
              <ul className="flex flex-col gap-2.5">
                {data.certifications.map((cert, index) => (
                  <li key={index} className="text-sm flex items-center gap-2">
                    <div className="h-1.5 w-1.5 rounded-full bg-cyber-warning"></div>
                    <span className="text-cyber-text/90">{cert}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <span className="text-sm text-cyber-muted italic">No professional certifications identified.</span>
            )}
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="flex items-center gap-3 border border-cyber-danger/30 bg-cyber-danger/5 text-cyber-danger rounded-xl p-4 text-sm">
          <span>{error}</span>
        </div>
      )}

      {/* Action Footer */}
      <div className="flex justify-end items-center mt-4">
        <button
          onClick={handleStartInterview}
          disabled={loading}
          className="btn-primary flex items-center justify-center gap-2 py-4 px-10 rounded-2xl font-bold text-base bg-gradient-to-r from-cyber-primary to-indigo-600 shadow-[0_0_20px_rgba(99,102,241,0.5)]"
        >
          {loading ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              Compiling Local Engine...
            </>
          ) : (
            <>
              <Play className="h-5 w-5" />
              Generate 10 Interview Questions
            </>
          )}
        </button>
      </div>
    </div>
  );
}

export default ResumeAnalysis;
