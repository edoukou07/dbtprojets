/**
 * API Service for Compliance Compliance Dashboard
 * Endpoints from dwh_marts_compliance (Conventions Validation, Approval Delays)
 */

import api from './api';

const COMPLIANCE_COMPLIANCE_BASE = '/compliance-compliance';

export const complianceComplianceAPI = {
  // Dashboard Summary
  getDashboardSummary: (annee = new Date().getFullYear()) =>
    api.get(`${COMPLIANCE_COMPLIANCE_BASE}/dashboard_summary/`, { params: { annee } }),

  // ===== Conventions Validation =====
  getConventionsSummary: (annee = new Date().getFullYear()) =>
    api.get(`${COMPLIANCE_COMPLIANCE_BASE}/conventions_summary/`, { params: { annee } }),

  getConventionsTrends: () =>
    api.get(`${COMPLIANCE_COMPLIANCE_BASE}/conventions_trends/`),

  getConventionsByStatus: () =>
    api.get(`${COMPLIANCE_COMPLIANCE_BASE}/conventions_by_status/`),

  // ===== Approval Delays =====
  getApprovalDelaysSummary: (annee = new Date().getFullYear()) =>
    api.get(`${COMPLIANCE_COMPLIANCE_BASE}/approval_delays_summary/`, { params: { annee } }),

  getApprovalDelaysTrends: () =>
    api.get(`${COMPLIANCE_COMPLIANCE_BASE}/approval_delays_trends/`),

  getApprovalDelaysByStatus: () =>
    api.get(`${COMPLIANCE_COMPLIANCE_BASE}/approval_delays_by_status/`),

  getApprovalDelaysByEtape: () =>
    api.get(`${COMPLIANCE_COMPLIANCE_BASE}/approval_delays_by_etape/`),
};

export default complianceComplianceAPI;
