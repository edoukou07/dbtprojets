/**
 * DashboardNavigation Component
 * Navigation menu for dashboard selection
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { DASHBOARD_ROUTES } from './routes';

interface DashboardNavigationProps {
  variant?: 'sidebar' | 'breadcrumb' | 'tabs';
  collapsible?: boolean;
}

const DashboardNavigation: React.FC<DashboardNavigationProps> = ({
  variant = 'tabs',
  collapsible = false,
}) => {
  const location = useLocation();
  const [isExpanded, setIsExpanded] = React.useState(!collapsible);

  const isActive = (path: string) => location.pathname === path;

  if (variant === 'sidebar') {
    return (
      <nav className="dashboard-sidebar">
        <div className="sidebar-header">
          <h2>Tableaux de Bord</h2>
          {collapsible && (
            <button
              className="sidebar-toggle"
              onClick={() => setIsExpanded(!isExpanded)}
              aria-expanded={isExpanded}
            >
              {isExpanded ? '←' : '→'}
            </button>
          )}
        </div>

        <ul className={`sidebar-menu ${isExpanded ? 'expanded' : 'collapsed'}`}>
          {DASHBOARD_ROUTES.map((route) => (
            <li key={route.path}>
              <Link
                to={route.path}
                className={`sidebar-link ${isActive(route.path) ? 'active' : ''}`}
                title={route.description}
              >
                <span className="menu-icon">{route.icon}</span>
                {isExpanded && <span className="menu-label">{route.label}</span>}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    );
  }

  if (variant === 'breadcrumb') {
    const activeRoute = DASHBOARD_ROUTES.find((r) => isActive(r.path));
    return (
      <nav className="dashboard-breadcrumb" aria-label="Breadcrumb">
        <ol>
          <li>
            <Link to="/dashboards">Tableaux de Bord</Link>
          </li>
          {activeRoute && (
            <li>
              <span className="breadcrumb-divider">/</span>
              <span className="breadcrumb-current">{activeRoute.label}</span>
            </li>
          )}
        </ol>
      </nav>
    );
  }

  // Default: tabs variant
  return (
    <nav className="dashboard-tabs" role="navigation" aria-label="Dashboards">
      <div className="tabs-container">
        {DASHBOARD_ROUTES.map((route) => (
          <Link
            key={route.path}
            to={route.path}
            className={`dashboard-tab ${isActive(route.path) ? 'active' : ''}`}
            title={route.description}
          >
            <span className="tab-icon">{route.icon}</span>
            <span className="tab-label">{route.label}</span>
          </Link>
        ))}
      </div>
    </nav>
  );
};

export default DashboardNavigation;
