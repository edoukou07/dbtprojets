/**
 * Dashboard App Integration Example
 * Shows how to integrate all dashboard components into the main React app
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import DashboardNavigation from './components/dashboards/DashboardNavigation';
import { DashboardRoutes } from './components/dashboards/routes';
import './styles/dashboards.css';

/**
 * Minimal App Integration
 * Use this if you want to add dashboards to an existing app
 */
export const DashboardsMinimalApp: React.FC = () => {
  return (
    <Router>
      <div className="app-container">
        <DashboardNavigation variant="tabs" />
        <DashboardRoutes />
      </div>
    </Router>
  );
};

/**
 * Full App Integration with Layout
 * Use this for a complete dashboard application
 */
export const DashboardsFullApp: React.FC = () => {
  return (
    <Router>
      <div className="app-layout">
        {/* Header */}
        <header className="app-header">
          <div className="header-content">
            <h1>📊 Tableaux de Bord - Système de Suivi RH</h1>
            <p>Analyse et suivi des indicateurs clés</p>
          </div>
        </header>

        {/* Main Content */}
        <div className="app-main">
          {/* Sidebar Navigation */}
          <aside className="app-sidebar">
            <DashboardNavigation variant="sidebar" collapsible={true} />
          </aside>

          {/* Dashboard Content */}
          <main className="app-content">
            {/* Breadcrumb Navigation */}
            <nav className="breadcrumb-nav">
              <DashboardNavigation variant="breadcrumb" />
            </nav>

            {/* Dashboard Routes */}
            <Routes>
              <Route path="/dashboards/*" element={<DashboardRoutes />} />
              {/* Default redirect */}
              <Route path="/" element={<DashboardRoutes />} />
            </Routes>
          </main>
        </div>

        {/* Footer */}
        <footer className="app-footer">
          <p>© 2024 Système de Suivi RH. Tous droits réservés.</p>
        </footer>
      </div>
    </Router>
  );
};

/**
 * App Styles for Complete Integration
 */
export const AppStyles = `
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
      Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background: #f5f5f5;
    color: #1a1a1a;
  }

  .app-layout {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  .app-header {
    background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%);
    color: white;
    padding: 2rem;
    box-shadow: 0 2px 8px rgba(0, 102, 204, 0.2);
  }

  .header-content h1 {
    margin-bottom: 0.5rem;
    font-size: 1.8rem;
  }

  .header-content p {
    opacity: 0.9;
    font-size: 0.95rem;
  }

  .app-main {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  .app-sidebar {
    width: 250px;
    background: white;
    border-right: 1px solid #e0e0e0;
    overflow-y: auto;
    transition: width 0.3s ease;
  }

  .app-sidebar::-webkit-scrollbar {
    width: 8px;
  }

  .app-sidebar::-webkit-scrollbar-track {
    background: #f1f1f1;
  }

  .app-sidebar::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
  }

  .app-sidebar::-webkit-scrollbar-thumb:hover {
    background: #555;
  }

  .app-content {
    flex: 1;
    overflow-y: auto;
    padding: 0;
  }

  .breadcrumb-nav {
    padding: 1rem 2rem;
    background: white;
    border-bottom: 1px solid #e0e0e0;
    position: sticky;
    top: 0;
    z-index: 10;
  }

  .app-footer {
    background: #f5f5f5;
    border-top: 1px solid #e0e0e0;
    padding: 1rem 2rem;
    text-align: center;
    color: #666;
    font-size: 0.85rem;
  }

  /* Scrollbar Styling */
  .app-content::-webkit-scrollbar {
    width: 10px;
  }

  .app-content::-webkit-scrollbar-track {
    background: #f1f1f1;
  }

  .app-content::-webkit-scrollbar-thumb {
    background: #999;
    border-radius: 5px;
  }

  .app-content::-webkit-scrollbar-thumb:hover {
    background: #666;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .app-main {
      flex-direction: column;
    }

    .app-sidebar {
      width: 100%;
      border-right: none;
      border-bottom: 1px solid #e0e0e0;
      max-height: 60px;
      overflow-x: auto;
      overflow-y: hidden;
    }

    .app-header {
      padding: 1rem;
    }

    .header-content h1 {
      font-size: 1.3rem;
    }

    .header-content p {
      display: none;
    }
  }
`;

/**
 * Usage Instructions:
 * 
 * 1. Minimal Integration (Just add to existing app):
 *    ```
 *    import { DashboardsMinimalApp } from './DashboardsApp';
 *    export default DashboardsMinimalApp;
 *    ```
 * 
 * 2. Full Integration (Complete dashboard app):
 *    ```
 *    import { DashboardsFullApp } from './DashboardsApp';
 *    export default DashboardsFullApp;
 *    ```
 * 
 * 3. Add to existing React app:
 *    ```
 *    import { DashboardRoutes } from './components/dashboards/routes';
 *    import { DashboardNavigation } from './components/dashboards/DashboardNavigation';
 *    import './styles/dashboards.css';
 *    
 *    // In your App.tsx:
 *    <Routes>
 *      <Route path="/dashboards/*" element={<DashboardRoutes />} />
 *    </Routes>
 *    ```
 */

export default DashboardsFullApp;
