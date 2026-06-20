import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Upload, FileText, AlertCircle, RefreshCw, CheckCircle2 } from 'lucide-react';

function ResumeUpload() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    setError(null);
    if (selectedFile.type !== 'application/pdf' && !selectedFile.name.endsWith('.pdf')) {
      setError('Please upload a PDF file only.');
      setFile(null);
      return;
    }
    // Limit to 5MB
    if (selectedFile.size > 5 * 1024 * 1024) {
      setError('File size exceeds the limit of 5MB.');
      setFile(null);
      return;
    }
    setFile(selectedFile);
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);
    
    try {
      // Call resume upload API
      const response = await api.uploadResume(file);
      
      // Store extracted info in localStorage
      localStorage.setItem('extractedResume', JSON.stringify(response));
      
      // Navigate to analysis page
      navigate('/analysis');
    } catch (err) {
      console.error(err);
      let errMsg = err.response?.data?.detail || 'An error occurred during resume extraction. Please try again.';
      if (err.response?.status === 502 || err.code === 'ERR_NETWORK') {
        errMsg = 'Backend server is not running. Start it first with: python backend/main.py (wait for "Application startup complete"), then retry.';
      }
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const clearFile = () => {
    setFile(null);
    setError(null);
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-2xl mx-auto flex flex-col gap-8 animate-fade-in">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight">Upload Resume</h2>
        <p className="text-cyber-muted">
          Upload your resume in PDF format. Our NLP service will parse your profile to formulate specialized interview questions.
        </p>
      </div>

      <div className="glass-card p-8 rounded-3xl relative overflow-hidden">
        {/* Radial light glow behind upload */}
        <div className="absolute -top-24 -left-24 h-48 w-48 rounded-full bg-cyber-primary/10 blur-3xl"></div>
        <div className="absolute -bottom-24 -right-24 h-48 w-48 rounded-full bg-cyber-secondary/10 blur-3xl"></div>

        <form onSubmit={handleUploadSubmit} className="flex flex-col gap-6 relative z-10">
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept=".pdf"
            onChange={handleChange}
            disabled={loading}
          />

          {/* Drag & Drop Area */}
          {!file ? (
            <div
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              onClick={triggerFileInput}
              className={`border-2 border-dashed rounded-2xl p-12 flex flex-col items-center justify-center gap-4 cursor-pointer transition-all duration-300 ${
                dragActive 
                  ? 'border-cyber-primary bg-cyber-primary/5 shadow-[0_0_15px_rgba(99,102,241,0.15)] scale-[1.01]' 
                  : 'border-white/10 bg-white/[0.02] hover:border-white/20 hover:bg-white/[0.04]'
              }`}
            >
              <div className="h-14 w-14 rounded-full bg-white/5 flex items-center justify-center text-cyber-muted group-hover:text-cyber-text transition-colors">
                <Upload className="h-6 w-6" />
              </div>
              <div className="text-center">
                <p className="text-sm font-semibold">Drag & drop your resume here, or <span className="text-cyber-primary underline hover:text-cyber-primary/95">browse</span></p>
                <p className="text-xs text-cyber-muted mt-1.5">PDF format only (Max 5MB)</p>
              </div>
            </div>
          ) : (
            /* Selected File Card */
            <div className="border border-cyber-primary/30 bg-cyber-primary/5 rounded-2xl p-6 flex items-center justify-between gap-4 animate-float-slow">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-xl bg-cyber-primary/20 flex items-center justify-center text-cyber-primary">
                  <FileText className="h-6 w-6" />
                </div>
                <div className="flex flex-col">
                  <span className="text-sm font-semibold text-white max-w-[280px] sm:max-w-[380px] truncate">{file.name}</span>
                  <span className="text-xs text-cyber-muted mt-0.5">{formatBytes(file.size)}</span>
                </div>
              </div>
              <button
                type="button"
                onClick={clearFile}
                className="text-xs text-cyber-danger bg-cyber-danger/10 border border-cyber-danger/20 hover:bg-cyber-danger/20 transition-all rounded-lg px-3 py-1.5 font-medium"
                disabled={loading}
              >
                Remove
              </button>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="flex items-center gap-3 border border-cyber-danger/30 bg-cyber-danger/5 text-cyber-danger rounded-xl p-4 text-sm">
              <AlertCircle className="h-5 w-5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Submit Action */}
          <div className="flex items-center justify-end mt-4">
            <button
              type="submit"
              className="btn-primary flex items-center justify-center gap-2 w-full sm:w-auto"
              disabled={!file || loading}
            >
              {loading ? (
                <>
                  <RefreshCw className="h-5 w-5 animate-spin" />
                  Extracting Resume Content...
                </>
              ) : (
                <>
                  <CheckCircle2 className="h-5 w-5" />
                  Analyze Profile
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ResumeUpload;
