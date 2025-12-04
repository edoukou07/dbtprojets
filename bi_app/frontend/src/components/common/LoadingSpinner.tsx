/**
 * LoadingSpinner Component
 * Simple loading indicator
 */

import React from 'react';

interface LoadingSpinnerProps {
  message?: string;
  size?: 'small' | 'medium' | 'large';
  fullScreen?: boolean;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = 'Chargement en cours...',
  size = 'medium',
  fullScreen = false,
}) => {
  const containerClass = fullScreen ? 'loading-spinner-fullscreen' : 'loading-spinner-inline';

  return (
    <div className={`loading-spinner-container ${containerClass}`}>
      <div className={`loading-spinner spinner-${size}`}>
        <div className="spinner-circle"></div>
      </div>
      {message && <p className="loading-message">{message}</p>}
    </div>
  );
};

export default LoadingSpinner;
