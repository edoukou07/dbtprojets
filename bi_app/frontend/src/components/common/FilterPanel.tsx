/**
 * FilterPanel Component
 * Reusable filter form for dashboards
 */

import React, { useState } from 'react';

interface FilterOption {
  value: string | number;
  label: string;
}

interface FilterConfig {
  [key: string]: {
    type: 'select' | 'range' | 'text' | 'date';
    label: string;
    options?: FilterOption[];
    min?: number;
    max?: number;
    step?: number;
  };
}

interface FilterPanelProps {
  filters: { [key: string]: any };
  onFilterChange: (key: string, value: any) => void;
  onClearFilters: () => void;
  filterConfig: FilterConfig;
  showReset?: boolean;
}

const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  onFilterChange,
  onClearFilters,
  filterConfig,
  showReset = true,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleInputChange = (key: string, value: any) => {
    onFilterChange(key, value || undefined);
  };

  const handleClear = () => {
    onClearFilters();
    setIsExpanded(false);
  };

  const activeFiltersCount = Object.values(filters).filter((v) => v !== undefined && v !== '').length;

  return (
    <div className="filter-panel">
      <div className="filter-header">
        <button
          className="filter-toggle"
          onClick={() => setIsExpanded(!isExpanded)}
          aria-expanded={isExpanded}
        >
          <span className="filter-icon">🔍</span>
          <span className="filter-label">Filtres</span>
          {activeFiltersCount > 0 && (
            <span className="active-badge">{activeFiltersCount}</span>
          )}
        </button>
      </div>

      {isExpanded && (
        <div className="filter-content">
          <div className="filter-form">
            {Object.entries(filterConfig).map(([key, config]) => (
              <div key={key} className="filter-group">
                <label htmlFor={`filter-${key}`} className="filter-label">
                  {config.label}
                </label>

                {config.type === 'select' && (
                  <select
                    id={`filter-${key}`}
                    value={filters[key] ?? ''}
                    onChange={(e) => handleInputChange(key, e.target.value || undefined)}
                    className="filter-input select-input"
                  >
                    <option value="">Tous</option>
                    {config.options?.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                )}

                {config.type === 'range' && (
                  <div className="range-inputs">
                    <input
                      type="number"
                      id={`filter-${key}-min`}
                      placeholder="Min"
                      min={config.min}
                      max={config.max}
                      step={config.step || 1}
                      className="filter-input range-input"
                      onChange={(e) =>
                        handleInputChange(`${key}_min`, e.target.value ? parseInt(e.target.value) : undefined)
                      }
                    />
                    <span className="range-separator">-</span>
                    <input
                      type="number"
                      id={`filter-${key}-max`}
                      placeholder="Max"
                      min={config.min}
                      max={config.max}
                      step={config.step || 1}
                      className="filter-input range-input"
                      onChange={(e) =>
                        handleInputChange(`${key}_max`, e.target.value ? parseInt(e.target.value) : undefined)
                      }
                    />
                  </div>
                )}

                {config.type === 'text' && (
                  <input
                    type="text"
                    id={`filter-${key}`}
                    placeholder={`Rechercher ${config.label.toLowerCase()}...`}
                    value={filters[key] ?? ''}
                    onChange={(e) => handleInputChange(key, e.target.value || undefined)}
                    className="filter-input text-input"
                  />
                )}

                {config.type === 'date' && (
                  <input
                    type="date"
                    id={`filter-${key}`}
                    value={filters[key] ?? ''}
                    onChange={(e) => handleInputChange(key, e.target.value || undefined)}
                    className="filter-input date-input"
                  />
                )}
              </div>
            ))}
          </div>

          <div className="filter-actions">
            {showReset && activeFiltersCount > 0 && (
              <button
                className="filter-button reset-button"
                onClick={handleClear}
                title="Réinitialiser les filtres"
              >
                Réinitialiser
              </button>
            )}
            <button
              className="filter-button close-button"
              onClick={() => setIsExpanded(false)}
            >
              Fermer
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FilterPanel;
