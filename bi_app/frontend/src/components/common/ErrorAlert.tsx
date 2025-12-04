/**
 * ErrorAlert Component
 * Error message display with retry functionality
 */

import React from 'react';
import { ApiError } from '../../types/dashboards.types';

interface ErrorAlertProps {
  error: ApiError | string;
  onRetry?: () => void;
  onDismiss?: () => void;
  severity?: 'error' | 'warning' | 'info';
}

const ErrorAlert: React.FC<ErrorAlertProps> = ({
  error,
  onRetry,
  onDismiss,
  severity = 'error',
}) => {
  const [dismissed, setDismissed] = React.useState(false);

  if (dismissed) {
    return null;
  }

  const errorMessage =
    typeof error === 'string'
      ? error
      : error.message || 'Une erreur est survenue';

  const errorDetails =
    typeof error === 'object' && error.details
      ? error.details
      : null;

  const statusCode =
    typeof error === 'object' && error.status
      ? error.status
      : null;

  const handleDismiss = () => {
    setDismissed(true);
    onDismiss?.();
  };

  return (
    <div className={`error-alert alert-${severity}`}>
      <div className="alert-content">
        <div className="alert-header">
          <span className="alert-icon">
            {severity === 'error' && '❌'}
            {severity === 'warning' && '⚠️'}
            {severity === 'info' && 'ℹ️'}
          </span>
          <span className="alert-title">
            {severity === 'error' && 'Erreur'}
            {severity === 'warning' && 'Avertissement'}
            {severity === 'info' && 'Information'}
          </span>
          {statusCode && <span className="alert-status">({statusCode})</span>}
        </div>

        <p className="alert-message">{errorMessage}</p>

        {errorDetails && (
          <details className="alert-details">
            <summary>Détails</summary>
            <pre>{JSON.stringify(errorDetails, null, 2)}</pre>
          </details>
        )}
      </div>

      <div className="alert-actions">
        {onRetry && (
          <button
            className="alert-button retry-button"
            onClick={onRetry}
            title="Réessayer"
          >
            🔄 Réessayer
          </button>
        )}
        <button
          className="alert-button dismiss-button"
          onClick={handleDismiss}
          title="Fermer l'alerte"
        >
          ✕
        </button>
      </div>
    </div>
  );
};

export default ErrorAlert;
