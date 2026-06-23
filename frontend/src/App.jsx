import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Watermark from './components/Watermark';
import Home from './pages/Home';
import ResumeUpload from './pages/ResumeUpload';
import ResumeAnalysis from './pages/ResumeAnalysis';
import Interview from './pages/Interview';
import Results from './pages/Results';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen relative">
        <Watermark />
        <Navbar />
        <main className="flex-1 w-full mx-auto max-w-7xl px-4 py-8 sm:px-6 md:py-12">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/upload" element={<ResumeUpload />} />
            <Route path="/analysis" element={<ResumeAnalysis />} />
            <Route path="/interview" element={<Interview />} />
            <Route path="/results" element={<Results />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </main>

        <footer className="w-full border-t border-white/5 py-6 bg-cyber-bg/50">
          <div className="mx-auto max-w-7xl px-6 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-cyber-muted">
            <p>Copyright © 2026 InterviewIQ AI. All rights reserved.</p>
            <p>Developed by <span className="text-cyber-primary font-semibold">Karthikeya</span></p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
