/**
 * SummaryCards Component
 * Displays metric cards with formatted values
 */

import React from 'react';
import { SummaryCard } from '../../types/dashboards.types';

interface SummaryCardsProps {
  cards: SummaryCard[];
  loading?: boolean;
  columns?: number;
}

const SummaryCards: React.FC<SummaryCardsProps> = ({
  cards,
  loading = false,
  columns = 4,
}) => {
  const formatValue = (card: SummaryCard): string => {
    switch (card.format) {
      case 'currency':
        return new Intl.NumberFormat('fr-FR', {
          style: 'currency',
          currency: 'XOF',
          minimumFractionDigits: 0,
        }).format(typeof card.value === 'string' ? parseFloat(card.value) : card.value);

      case 'percentage':
        return `${typeof card.value === 'string' ? card.value : card.value.toFixed(1)}%`;

      case 'number':
      default:
        return typeof card.value === 'string'
          ? card.value
          : new Intl.NumberFormat('fr-FR').format(card.value);
    }
  };

  return (
    <div className="summary-cards-container">
      <div className="summary-cards-grid" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
        {cards.map((card, index) => (
          <div key={`${card.title}-${index}`} className="summary-card">
            <div className="card-content">
              <h3 className="card-title">{card.title}</h3>
              {loading ? (
                <div className="card-value skeleton">
                  <span className="spinner" />
                </div>
              ) : (
                <div className="card-value">
                  <span className="value-text">{formatValue(card)}</span>
                  {card.unit && <span className="value-unit">{card.unit}</span>}
                </div>
              )}
              {card.change && (
                <div className={`card-change ${card.change > 0 ? 'positive' : 'negative'}`}>
                  <span className="change-arrow">{card.change > 0 ? '↑' : '↓'}</span>
                  <span className="change-value">{Math.abs(card.change)}%</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SummaryCards;
