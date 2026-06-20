import React from 'react';

/**
 * Fixed watermark — repeated diagonal text + corner author badge.
 */
function Watermark() {
  const tiles = Array.from({ length: 12 }, (_, i) => i);

  return (
    <div
      className="watermark fixed inset-0 z-[9999] pointer-events-none select-none overflow-hidden"
      aria-hidden="true"
    >
      <div className="watermark-grid">
        {tiles.map((i) => (
          <span key={i} className="watermark-text">
            Karthikeya
          </span>
        ))}
      </div>

      <div className="watermark-badge">
        <span className="watermark-badge-label">Developed by</span>
        <span className="watermark-badge-name">Karthikeya</span>
      </div>
    </div>
  );
}

export default Watermark;
