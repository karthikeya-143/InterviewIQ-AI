import React from 'react';

/**
 * Reusable feedback list for strengths, weaknesses, or suggestions.
 */
function FeedbackList({ title, items, variant = 'default' }) {
  const styles = {
    strengths: 'text-cyber-success/80',
    weaknesses: 'text-cyber-warning/80',
    suggestions: 'text-cyber-muted',
    default: 'text-cyber-muted',
  };

  const bulletStyles = {
    strengths: 'text-cyber-success',
    weaknesses: 'text-cyber-warning',
    suggestions: 'text-cyber-primary',
    default: 'text-cyber-primary',
  };

  if (!items?.length) return null;

  return (
    <div className="flex flex-col gap-2">
      <span className={`text-xs font-semibold uppercase ${styles[variant] || styles.default}`}>
        {title}
      </span>
      <ul className="flex flex-col gap-1.5 text-xs text-cyber-text/90">
        {items.map((item, i) => (
          <li key={i} className="flex items-start gap-2">
            <span className={`${bulletStyles[variant] || bulletStyles.default} mt-0.5`}>•</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default FeedbackList;
