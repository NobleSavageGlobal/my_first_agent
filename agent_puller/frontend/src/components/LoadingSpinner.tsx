import React from 'react';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  message?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  message,
}) => {
  return (
    <div className="loading-spinner">
      <div className={`spinner spinner-${size}`}></div>
      {message && <span className="loading-message">{message}</span>}
    </div>
  );
};

export default LoadingSpinner;
