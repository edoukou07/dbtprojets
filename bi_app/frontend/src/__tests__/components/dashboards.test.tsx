/**
 * Dashboard Components Unit Tests
 * Testing suite for React dashboard components and hooks
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';

// Mock API module
jest.mock('../../services/api', () => ({
  get: jest.fn(),
  post: jest.fn(),
}));

describe('Dashboard Components', () => {
  // ===== LoadingSpinner Tests =====
  describe('LoadingSpinner', () => {
    it('should render with default message', () => {
      const { LoadingSpinner } = require('../../components/common/LoadingSpinner');
      render(<LoadingSpinner />);
      expect(screen.getByText('Chargement en cours...')).toBeInTheDocument();
    });

    it('should render custom message', () => {
      const { LoadingSpinner } = require('../../components/common/LoadingSpinner');
      render(<LoadingSpinner message="Récupération des données..." />);
      expect(screen.getByText('Récupération des données...')).toBeInTheDocument();
    });

    it('should apply correct size class', () => {
      const { LoadingSpinner } = require('../../components/common/LoadingSpinner');
      const { container } = render(<LoadingSpinner size="large" />);
      expect(container.querySelector('.spinner-large')).toBeInTheDocument();
    });
  });

  // ===== ErrorAlert Tests =====
  describe('ErrorAlert', () => {
    it('should render error message', () => {
      const { ErrorAlert } = require('../../components/common/ErrorAlert');
      render(<ErrorAlert error="Test error message" />);
      expect(screen.getByText('Test error message')).toBeInTheDocument();
    });

    it('should call onRetry when retry button clicked', () => {
      const { ErrorAlert } = require('../../components/common/ErrorAlert');
      const onRetry = jest.fn();
      render(<ErrorAlert error="Test error" onRetry={onRetry} />);

      fireEvent.click(screen.getByText('🔄 Réessayer'));
      expect(onRetry).toHaveBeenCalled();
    });

    it('should dismiss on dismiss button click', () => {
      const { ErrorAlert } = require('../../components/common/ErrorAlert');
      const { container } = render(<ErrorAlert error="Test error" />);

      const dismissButton = container.querySelector('.dismiss-button');
      fireEvent.click(dismissButton!);

      expect(screen.queryByText('Test error')).not.toBeInTheDocument();
    });

    it('should display status code if provided', () => {
      const { ErrorAlert } = require('../../components/common/ErrorAlert');
      render(<ErrorAlert error={{ message: 'Error', status: 404 }} />);
      expect(screen.getByText('(404)')).toBeInTheDocument();
    });
  });

  // ===== SummaryCards Tests =====
  describe('SummaryCards', () => {
    const mockCards = [
      { title: 'Total', value: 1000, format: 'number' as const },
      { title: 'Amount', value: 5000, format: 'currency' as const },
      { title: 'Percentage', value: 85.5, format: 'percentage' as const },
    ];

    it('should render all cards', () => {
      const { SummaryCards } = require('../../components/common/SummaryCards');
      render(<SummaryCards cards={mockCards} />);

      expect(screen.getByText('Total')).toBeInTheDocument();
      expect(screen.getByText('Amount')).toBeInTheDocument();
      expect(screen.getByText('Percentage')).toBeInTheDocument();
    });

    it('should format currency values correctly', () => {
      const { SummaryCards } = require('../../components/common/SummaryCards');
      render(<SummaryCards cards={mockCards} />);

      const currencyText = screen.getByText((content, element) => {
        return content.includes('5') && content.includes('XOF');
      });
      expect(currencyText).toBeInTheDocument();
    });

    it('should show loading state', () => {
      const { SummaryCards } = require('../../components/common/SummaryCards');
      const { container } = render(<SummaryCards cards={mockCards} loading={true} />);

      expect(container.querySelector('.skeleton')).toBeInTheDocument();
    });

    it('should apply custom grid columns', () => {
      const { SummaryCards } = require('../../components/common/SummaryCards');
      const { container } = render(
        <SummaryCards cards={mockCards} columns={2} />
      );

      const grid = container.querySelector('.summary-cards-grid') as HTMLElement;
      expect(grid.style.gridTemplateColumns).toContain('2');
    });
  });

  // ===== FilterPanel Tests =====
  describe('FilterPanel', () => {
    const mockFilters = { zone_id: '', status: '' };
    const mockConfig = {
      zone_id: {
        type: 'select' as const,
        label: 'Zone',
        options: [
          { value: 1, label: 'Zone 1' },
          { value: 2, label: 'Zone 2' },
        ],
      },
      status: {
        type: 'select' as const,
        label: 'Status',
        options: [
          { value: 'active', label: 'Active' },
          { value: 'inactive', label: 'Inactive' },
        ],
      },
    };

    it('should render filter toggle button', () => {
      const { FilterPanel } = require('../../components/common/FilterPanel');
      render(
        <FilterPanel
          filters={mockFilters}
          onFilterChange={jest.fn()}
          onClearFilters={jest.fn()}
          filterConfig={mockConfig}
        />
      );

      expect(screen.getByRole('button', { name: /Filtres/i })).toBeInTheDocument();
    });

    it('should expand/collapse on toggle click', () => {
      const { FilterPanel } = require('../../components/common/FilterPanel');
      const { container } = render(
        <FilterPanel
          filters={mockFilters}
          onFilterChange={jest.fn()}
          onClearFilters={jest.fn()}
          filterConfig={mockConfig}
        />
      );

      const toggle = screen.getByRole('button', { name: /Filtres/i });
      const filterContent = container.querySelector('.filter-content');

      expect(filterContent).toBeInTheDocument();
      fireEvent.click(toggle);
      expect(filterContent).not.toBeVisible();
    });

    it('should call onFilterChange when filter value changes', () => {
      const { FilterPanel } = require('../../components/common/FilterPanel');
      const onFilterChange = jest.fn();

      render(
        <FilterPanel
          filters={mockFilters}
          onFilterChange={onFilterChange}
          onClearFilters={jest.fn()}
          filterConfig={mockConfig}
        />
      );

      const selects = screen.getAllByRole('combobox');
      fireEvent.change(selects[0], { target: { value: '1' } });

      expect(onFilterChange).toHaveBeenCalledWith('zone_id', '1');
    });

    it('should show active filter badge', () => {
      const { FilterPanel } = require('../../components/common/FilterPanel');
      render(
        <FilterPanel
          filters={{ zone_id: '1', status: '' }}
          onFilterChange={jest.fn()}
          onClearFilters={jest.fn()}
          filterConfig={mockConfig}
        />
      );

      expect(screen.getByText('1')).toBeInTheDocument();
    });
  });

  // ===== DashboardTable Tests =====
  describe('DashboardTable', () => {
    const mockColumns = [
      { key: 'id', label: 'ID', sortable: true },
      { key: 'name', label: 'Name', sortable: false },
      { key: 'amount', label: 'Amount', type: 'currency' as const },
    ];

    const mockData = [
      { id: 1, name: 'Item 1', amount: 1000 },
      { id: 2, name: 'Item 2', amount: 2000 },
    ];

    it('should render table with data', () => {
      const { DashboardTable } = require('../../components/common/DashboardTable');
      render(<DashboardTable columns={mockColumns} data={mockData} />);

      expect(screen.getByText('Item 1')).toBeInTheDocument();
      expect(screen.getByText('Item 2')).toBeInTheDocument();
    });

    it('should show loading state', () => {
      const { DashboardTable } = require('../../components/common/DashboardTable');
      render(
        <DashboardTable
          columns={mockColumns}
          data={[]}
          loading={true}
        />
      );

      expect(screen.getByText(/Chargement/)).toBeInTheDocument();
    });

    it('should show empty message when no data', () => {
      const { DashboardTable } = require('../../components/common/DashboardTable');
      render(
        <DashboardTable
          columns={mockColumns}
          data={[]}
          emptyMessage="Pas de données"
        />
      );

      expect(screen.getByText('Pas de données')).toBeInTheDocument();
    });

    it('should call onSortChange when sortable column clicked', () => {
      const { DashboardTable } = require('../../components/common/DashboardTable');
      const onSortChange = jest.fn();

      const { container } = render(
        <DashboardTable
          columns={mockColumns}
          data={mockData}
          onSortChange={onSortChange}
        />
      );

      const sortableHeader = container.querySelector('th.sortable');
      fireEvent.click(sortableHeader!);

      expect(onSortChange).toHaveBeenCalled();
    });

    it('should render pagination controls', () => {
      const { DashboardTable } = require('../../components/common/DashboardTable');
      const pagination = {
        current_page: 1,
        total_pages: 5,
        total_count: 50,
        page_size: 10,
      };

      render(
        <DashboardTable
          columns={mockColumns}
          data={mockData}
          pagination={pagination}
          onPageChange={jest.fn()}
        />
      );

      expect(screen.getByText('Affichage 1 à 2 sur 50 résultats')).toBeInTheDocument();
    });
  });

  // ===== DashboardNavigation Tests =====
  describe('DashboardNavigation', () => {
    it('should render dashboard tabs', () => {
      const { DashboardNavigation } = require('../../components/dashboards/DashboardNavigation');
      render(
        <BrowserRouter>
          <DashboardNavigation variant="tabs" />
        </BrowserRouter>
      );

      expect(screen.getByText('Suivi des Implantations')).toBeInTheDocument();
      expect(screen.getByText('Indemnisations')).toBeInTheDocument();
      expect(screen.getByText('Emplois Créés')).toBeInTheDocument();
      expect(screen.getByText('Créances Âgées')).toBeInTheDocument();
    });

    it('should render sidebar variant', () => {
      const { DashboardNavigation } = require('../../components/dashboards/DashboardNavigation');
      const { container } = render(
        <BrowserRouter>
          <DashboardNavigation variant="sidebar" />
        </BrowserRouter>
      );

      expect(container.querySelector('.dashboard-sidebar')).toBeInTheDocument();
    });

    it('should render breadcrumb variant', () => {
      const { DashboardNavigation } = require('../../components/dashboards/DashboardNavigation');
      const { container } = render(
        <BrowserRouter>
          <DashboardNavigation variant="breadcrumb" />
        </BrowserRouter>
      );

      expect(container.querySelector('.dashboard-breadcrumb')).toBeInTheDocument();
    });

    it('should highlight active tab', () => {
      const { DashboardNavigation } = require('../../components/dashboards/DashboardNavigation');
      const { container } = render(
        <BrowserRouter>
          <DashboardNavigation variant="tabs" />
        </BrowserRouter>
      );

      const activeTab = container.querySelector('.dashboard-tab.active');
      expect(activeTab).toBeInTheDocument();
    });
  });

  // ===== Integration Tests =====
  describe('Dashboard Integration', () => {
    it('should render complete dashboard with all components', () => {
      const { ImplantationSuiviDashboard } = require('../../components/dashboards/ImplantationSuiviDashboard');
      render(
        <BrowserRouter>
          <ImplantationSuiviDashboard />
        </BrowserRouter>
      );

      expect(screen.getByText('Suivi des Implantations')).toBeInTheDocument();
    });
  });
});
