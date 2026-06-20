import React from 'react';

/**
 * Circular score indicator used on the Dashboard.
 */
function ScoreRing({ score, label, size = 176, strokeClass = 'stroke-cyber-primary' }) {
  const radius = 74;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (circumference * score) / 100;
  const center = size / 2;

  return (
    <div className="relative flex items-center justify-center" style={{ height: size, width: size }}>
      <svg className="absolute w-full h-full transform -rotate-90">
        <circle
          cx={center}
          cy={center}
          r={radius}
          className="stroke-white/5 fill-transparent"
          strokeWidth="10"
        />
        <circle
          cx={center}
          cy={center}
          r={radius}
          className={`${strokeClass} fill-transparent transition-all duration-1000 ease-out`}
          strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
      </svg>
      <div className="flex flex-col items-center">
        <span className="text-4xl font-extrabold text-white">{score}</span>
        <span className="text-xs text-cyber-muted font-semibold uppercase mt-0.5">{label}</span>
      </div>
    </div>
  );
}

export default ScoreRing;
