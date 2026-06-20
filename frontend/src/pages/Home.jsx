import React from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight, FileText, Cpu, Mic, Award, Sparkles,
  Brain, Shield, BarChart2, Layers,
} from 'lucide-react';

function Home() {
  const techStack = [
    'React.js', 'Tailwind CSS', 'FastAPI', 'Whisper',
    'Sentence-BERT', 'Flan-T5', 'PyTorch', 'pdfplumber',
  ];

  return (
    <div className="flex flex-col gap-16 md:gap-24 animate-fade-in">
      {/* Hero Section */}
      <section className="flex flex-col items-center text-center gap-6 max-w-4xl mx-auto py-8">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyber-primary/10 border border-cyber-primary/20 text-cyber-primary text-xs font-semibold uppercase tracking-wider animate-float-slow">
          <Sparkles className="h-3.5 w-3.5" /> Next-Generation Mock Interviews
        </div>

        <h1 className="text-4xl font-extrabold tracking-tight sm:text-6xl bg-gradient-to-b from-white via-slate-100 to-slate-400 bg-clip-text text-transparent leading-none">
          Master Your Technical Interviews with{' '}
          <span className="bg-gradient-to-r from-cyber-primary via-indigo-400 to-cyber-accent bg-clip-text text-transparent glow-text-primary">
            InterviewIQ AI
          </span>
        </h1>

        <p className="text-lg md:text-xl text-cyber-muted max-w-2xl mt-2 leading-relaxed">
          Upload your resume to generate customized questions, record your answers via speech, and receive instant AI-driven semantic evaluation powered by Whisper and Sentence-BERT.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 mt-6">
          <Link to="/upload" className="btn-primary flex items-center justify-center gap-2 px-8 py-4 group">
            Start Mock Interview
            <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
          </Link>
          <Link to="/upload" className="btn-secondary flex items-center justify-center gap-2 px-8 py-4">
            Upload Resume
          </Link>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="glass-card glass-card-hover p-8 rounded-2xl flex flex-col gap-4">
          <div className="h-12 w-12 rounded-xl bg-cyber-primary/10 border border-cyber-primary/20 flex items-center justify-center text-cyber-primary">
            <FileText className="h-6 w-6" />
          </div>
          <h3 className="text-xl font-bold">1. Resume Analysis</h3>
          <p className="text-cyber-muted text-sm leading-relaxed">
            Extracts skills, certifications, education, and projects from your PDF resume using a customized parsing utility.
          </p>
        </div>

        <div className="glass-card glass-card-hover p-8 rounded-2xl flex flex-col gap-4">
          <div className="h-12 w-12 rounded-xl bg-cyber-secondary/10 border border-cyber-secondary/20 flex items-center justify-center text-cyber-secondary">
            <Mic className="h-6 w-6" />
          </div>
          <h3 className="text-xl font-bold">2. Speech-to-Text</h3>
          <p className="text-cyber-muted text-sm leading-relaxed">
            Accepts real audio answers from your microphone, processing speech to high-fidelity text transcripts using Whisper.
          </p>
        </div>

        <div className="glass-card glass-card-hover p-8 rounded-2xl flex flex-col gap-4">
          <div className="h-12 w-12 rounded-xl bg-cyber-accent/10 border border-cyber-accent/20 flex items-center justify-center text-cyber-accent">
            <Cpu className="h-6 w-6" />
          </div>
          <h3 className="text-xl font-bold">3. Semantic Evaluation</h3>
          <p className="text-cyber-muted text-sm leading-relaxed">
            Calculates cosine similarity embeddings between candidate answers and reference answers using Sentence-BERT to generate feedback.
          </p>
        </div>
      </section>

      {/* Project Highlights — replaces pipeline section */}
      <section className="glass-card p-8 md:p-12 rounded-3xl flex flex-col gap-10">
        <div className="flex flex-col gap-3 text-center max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold tracking-tight">Built for Real Interview Prep</h2>
          <p className="text-cyber-muted leading-relaxed">
            InterviewIQ AI runs entirely on free, open-source models —
            no cloud APIs, no login, and no data stored permanently.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="flex flex-col gap-3 p-5 rounded-2xl bg-white/[0.03] border border-white/5">
            <Brain className="h-6 w-6 text-cyber-primary" />
            <h4 className="font-bold text-sm">10 Smart Questions</h4>
            <p className="text-xs text-cyber-muted leading-relaxed">
              5 Technical, 3 Project-based, and 2 HR questions tailored to your resume profile.
            </p>
          </div>

          <div className="flex flex-col gap-3 p-5 rounded-2xl bg-white/[0.03] border border-white/5">
            <Layers className="h-6 w-6 text-cyber-accent" />
            <h4 className="font-bold text-sm">Reference Answers</h4>
            <p className="text-xs text-cyber-muted leading-relaxed">
              Every question comes with an expert-grade reference answer for fair, objective scoring.
            </p>
          </div>

          <div className="flex flex-col gap-3 p-5 rounded-2xl bg-white/[0.03] border border-white/5">
            <Shield className="h-6 w-6 text-cyber-success" />
            <h4 className="font-bold text-sm">100% Local & Private</h4>
            <p className="text-xs text-cyber-muted leading-relaxed">
              All AI models run on your machine. Your resume and answers never leave your system.
            </p>
          </div>

          <div className="flex flex-col gap-3 p-5 rounded-2xl bg-white/[0.03] border border-white/5">
            <BarChart2 className="h-6 w-6 text-cyber-secondary" />
            <h4 className="font-bold text-sm">Detailed Report</h4>
            <p className="text-xs text-cyber-muted leading-relaxed">
              Get an overall score, per-question feedback, strengths, weaknesses, and improvement tips.
            </p>
          </div>
        </div>

        <div className="flex flex-col gap-4 items-center">
          <span className="text-xs font-mono text-cyber-muted uppercase tracking-wider">Technology Stack</span>
          <div className="flex flex-wrap justify-center gap-2">
            {techStack.map((tech) => (
              <span
                key={tech}
                className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-cyber-primary/10 border border-cyber-primary/20 text-cyber-primary"
              >
                {tech}
              </span>
            ))}
          </div>
        </div>

        <div className="flex justify-center pt-2">
          <Link to="/upload" className="btn-primary flex items-center gap-2 px-8 py-3">
            <Award className="h-4 w-4" />
            Begin Your Mock Interview
          </Link>
        </div>
      </section>
    </div>
  );
}

export default Home;
