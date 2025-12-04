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

  // ===== Conventions by Enterprise Dimensions (Phase 1) =====
  getConventionsByDomaine: (annee = new Date().getFullYear()) =>
    api.get(`${COMPLIANCE_COMPLIANCE_BASE}/conventions_by_domaine/`, { params: { annee } }),

  getConventionsByCategorieDomaine: (annee = new Date().getFullYear()) =>
    api.get(`${COMPLIANCE_COMPLIANCE_BASE}/conventions_by_categorie_domaine/`, { params: { annee } }),

  getConventionsByFormeJuridique: (annee = new Date().getFullYear()) =>
    api.get(`${COMPLIANCE_COMPLIANCE_BASE}/conventions_by_forme_juridique/`, { params: { annee } }),

  getConventionsByEntreprise: (annee = new Date().getFullYear(), limit = 20) =>
    api.get(`${COMPLIANCE_COMPLIANCE_BASE}/conventions_by_entreprise/`, { params: { annee, limit } }),

  // ===== Approval Delays =====
  getApprovalDelaysSummary: (annee = new Date().getFullYear()) =>
    api.get(`${COMPLIANCE_COMPLIANCE_BASE}/approval_delays_summary/`, { params: { annee } }),

  getApprovalDelaysTrends: () =>
    api.get(`${COMPLIANCE_COMPLIANCE_BASE}/approval_delays_trends/`),

  getApprovalDelaysByStatus: () =>
    api.get(`${COMPLIANCE_COMPLIANCE_BASE}/approval_delays_by_status/`),

  getApprovalDelaysByEtape: () =>
    api.get(`${COMPLIANCE_COMPLIANCE_BASE}/approval_delays_by_etape/`),

  // ===== Approval Delays by Enterprise Dimensions (Phase 1) =====
  getApprovalDelaysByDomaine: (annee = new Date().getFullYear()) =>
    api.get(`${COMPLIANCE_COMPLIANCE_BASE}/approval_delays_by_domaine/`, { params: { annee } }),

  getApprovalDelaysByFormeJuridique: (annee = new Date().getFullYear()) =>
    api.get(`${COMPLIANCE_COMPLIANCE_BASE}/approval_delays_by_forme_juridique/`, { params: { annee } }),
};

export default complianceComplianceAPI;
