import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Cpu, FileText, Mic, BarChart2 } from 'lucide-react';

function Navbar() {
  const location = useLocation();

  const isActive = (path) =>
    location.pathname === path
      ? 'text-cyber-primary border-cyber-primary font-semibold'
      : 'text-cyber-muted hover:text-cyber-text border-transparent';

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-cyber-bg/70 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl h-16 items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2 group">
          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-cyber-primary to-cyber-secondary shadow-[0_0_15px_rgba(99,102,241,0.4)] group-hover:scale-105 transition-all duration-300">
            <Cpu className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-300 bg-clip-text text-transparent">
            InterviewIQ <span className="text-cyber-primary glow-text-primary">AI</span>
          </span>
        </Link>

        <nav className="hidden md:flex gap-6 h-full items-center">
          <Link to="/" className={`flex items-center gap-1.5 border-b-2 py-5 text-sm transition-all duration-200 ${isActive('/')}`}>
            Home
          </Link>
          <Link to="/upload" className={`flex items-center gap-1.5 border-b-2 py-5 text-sm transition-all duration-200 ${isActive('/upload')} ${isActive('/analysis')}`}>
            <FileText className="h-4 w-4" />
            Resume
          </Link>
          <Link to="/interview" className={`flex items-center gap-1.5 border-b-2 py-5 text-sm transition-all duration-200 ${isActive('/interview')}`}>
            <Mic className="h-4 w-4" />
            Interview
          </Link>
          <Link to="/results" className={`flex items-center gap-1.5 border-b-2 py-5 text-sm transition-all duration-200 ${isActive('/results')}`}>
            Review
          </Link>
          <Link to="/dashboard" className={`flex items-center gap-1.5 border-b-2 py-5 text-sm transition-all duration-200 ${isActive('/dashboard')}`}>
            <BarChart2 className="h-4 w-4" />
            Report
          </Link>
        </nav>

        <div className="flex items-center gap-4">
          <span className="hidden sm:inline-flex items-center gap-1 rounded-full bg-cyber-primary/10 border border-cyber-primary/20 px-3 py-1 text-xs text-cyber-primary">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyber-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-cyber-primary"></span>
            </span>
            Local Engine Active
          </span>
        </div>
      </div>
    </header>
  );
}

export default Navbar;
