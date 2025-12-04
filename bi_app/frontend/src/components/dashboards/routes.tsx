/**
 * Dashboard Routes Configuration
 * Central routing setup for all dashboard components
 */

import React from 'react';
import { Route, Routes } from 'react-router-dom';
import ImplantationSuiviDashboard from './ImplantationSuiviDashboard';
import IndemnisationsDashboard from './IndemnisationsDashboard';
import EmploisCreesDashboard from './EmploisCreesDashboard';
import CreancesAgeesDashboard from './CreancesAgeesDashboard';

export interface DashboardRoute {
  path: string;
  label: string;
  icon: string;
  component: React.ComponentType<any>;
  description: string;
}

export const DASHBOARD_ROUTES: DashboardRoute[] = [
  {
    path: '/dashboards/implantation-suivi',
    label: 'Suivi des Implantations',
    icon: '📊',
    component: ImplantationSuiviDashboard,
    description: 'Analyse du suivi des implantations par zone et période',
  },
  {
    path: '/dashboards/indemnisations',
    label: 'Indemnisations',
    icon: '💰',
    component: IndemnisationsDashboard,
    description: 'Analyse des indemnisations par zone et statut',
  },
  {
    path: '/dashboards/emplois-crees',
    label: 'Emplois Créés',
    icon: '👥',
    component: EmploisCreesDashboard,
    description: 'Analyse des emplois créés par type et demande',
  },
  {
    path: '/dashboards/creances-agees',
    label: 'Créances Âgées',
    icon: '⏰',
    component: CreancesAgeesDashboard,
    description: 'Analyse des créances âgées par ancienneté et risque',
  },
];

interface DashboardRoutesProps {
  basePath?: string;
}

/**
 * DashboardRoutes Component
 * Renders all dashboard routes using React Router
 */
export const DashboardRoutes: React.FC<DashboardRoutesProps> = ({ basePath = '/dashboards' }) => {
  return (
    <Routes>
      {DASHBOARD_ROUTES.map((route) => (
        <Route
          key={route.path}
          path={route.path.replace(basePath, '').replace(/^\//, '')}
          element={<route.component />}
        />
      ))}
    </Routes>
  );
};

export default DashboardRoutes;
