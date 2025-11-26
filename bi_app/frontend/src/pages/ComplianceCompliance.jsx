import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import complianceComplianceAPI from '../services/complianceComplianceAPI';
import './ComplianceCompliance.css';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

const ComplianceCompliance = () => {
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear());
  const [loading, setLoading] = useState(false);
  
  // Résumé du tableau de bord
  const [summary, setSummary] = useState({
    conventions_validation: {},
    approval_delays: {}
  });

  // Conventions
  const [conventionsSummary, setConventionsSummary] = useState({});
  const [conventionsTrends, setConventionsTrends] = useState([]);
  const [conventionsByStatus, setConventionsByStatus] = useState([]);

  // Délais d'approbation
  const [delaysSummary, setDelaysSummary] = useState({});
  const [delaysTrends, setDelaysTrends] = useState([]);
  const [delaysByStatus, setDelaysByStatus] = useState([]);
  const [delaysByEtape, setDelaysByEtape] = useState([]);

  useEffect(() => {
    fetchAllData();
  }, [currentYear]);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [summary, convSum, convTr, convStat, delaySum, delayTr, delayStat, delayEtape] = await Promise.all([
        complianceComplianceAPI.getDashboardSummary(currentYear),
        complianceComplianceAPI.getConventionsSummary(currentYear),
        complianceComplianceAPI.getConventionsTrends(),
        complianceComplianceAPI.getConventionsByStatus(),
        complianceComplianceAPI.getApprovalDelaysSummary(currentYear),
        complianceComplianceAPI.getApprovalDelaysTrends(),
        complianceComplianceAPI.getApprovalDelaysByStatus(),
        complianceComplianceAPI.getApprovalDelaysByEtape(),
      ]);

      setSummary(summary.data);
      setConventionsSummary(convSum.data);
      setConventionsTrends(convTr.data || []);
      setConventionsByStatus(convStat.data || []);
      setDelaysSummary(delaySum.data);
      setDelaysTrends(delayTr.data || []);
      setDelaysByStatus(delayStat.data || []);
      setDelaysByEtape(delayEtape.data || []);
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
    } finally {
      setLoading(false);
    }
  };

  const KPICard = ({ title, value, unit = '', subtext = '', icon = '📊', color = 'blue' }) => (
    <div className={`kpi-card kpi-${color}`}>
      <div className="kpi-icon">{icon}</div>
      <div className="kpi-content">
        <h4>{title}</h4>
        <div className="kpi-value">{value?.toLocaleString('fr-FR') || '0'}{unit}</div>
        {subtext && <div className="kpi-subtext">{subtext}</div>}
      </div>
    </div>
  );

  return (
    <div className="compliance-compliance-dashboard">
      <header className="dashboard-header">
        <h1>📊 Tableau de Bord Conformité</h1>
        <div className="header-controls">
          <select value={currentYear} onChange={(e) => setCurrentYear(parseInt(e.target.value))}>
            {[2024, 2025, 2026].map(year => <option key={year} value={year}>{year}</option>)}
          </select>
          <button onClick={fetchAllData} disabled={loading} className="refresh-btn">
            {loading ? 'Chargement...' : 'Actualiser'}
          </button>
        </div>
      </header>

      {loading ? (
        <div className="loading">Chargement des données du tableau de bord...</div>
      ) : (
        <>
          {/* ===== GLOBAL SUMMARY ===== */}
          <section className="dashboard-section">
            <h2>Résumé du Tableau de Bord</h2>
            <div className="kpi-grid">
              <KPICard
                title="Total Conventions"
                value={summary.conventions_validation?.total_conventions}
                icon="📋"
                color="purple"
              />
              <KPICard
                title="Taux de Validation"
                value={summary.conventions_validation?.avg_validation_rate_pct?.toFixed(2)}
                unit="%"
                icon="✅"
                color="green"
              />
              <KPICard
                title="Délai Moyen d'Approbation"
                value={summary.approval_delays?.avg_approval_days?.toFixed(1)}
                unit="j"
                icon="⏱️"
                color="orange"
              />
              <KPICard
                title="Conventions Approuvées"
                value={summary.approval_delays?.conventions_approved}
                icon="✓"
                color="green"
              />
              <KPICard
                title="Conventions Rejetées"
                value={summary.approval_delays?.conventions_rejected}
                icon="✗"
                color="red"
              />
              <KPICard
                title="En Cours"
                value={summary.approval_delays?.conventions_in_progress}
                icon="⏳"
                color="blue"
              />
            </div>
          </section>

          {/* ===== CONVENTIONS VALIDATION SECTION ===== */}
          <section className="dashboard-section">
            <h2>📋 Validation des Conventions</h2>

            <div className="section-grid">
              <div className="metric-card">
                <h3>Résumé de la Validation</h3>
                <div className="summary-stats">
                  <div className="stat-row">
                    <span>Total Conventions:</span>
                    <strong>{conventionsSummary.total_conventions?.toLocaleString('fr-FR')}</strong>
                  </div>
                  <div className="stat-row">
                    <span>Approuvées:</span>
                    <strong className="success">{conventionsSummary.conventions_approved?.toLocaleString('fr-FR')}</strong>
                  </div>
                  <div className="stat-row">
                    <span>Rejetées:</span>
                    <strong className="error">{conventionsSummary.conventions_rejected?.toLocaleString('fr-FR')}</strong>
                  </div>
                  <div className="stat-row">
                    <span>En Cours:</span>
                    <strong className="warning">{conventionsSummary.conventions_in_progress?.toLocaleString('fr-FR')}</strong>
                  </div>
                  <div className="stat-row">
                    <span>Archivées:</span>
                    <strong>{conventionsSummary.conventions_archived?.toLocaleString('fr-FR')}</strong>
                  </div>
                  <div className="stat-row">
                    <span>Taux de Validation:</span>
                    <strong className="success">{conventionsSummary.avg_validation_rate_pct?.toFixed(2)}%</strong>
                  </div>
                  <div className="stat-row">
                    <span>Taux de Rejet:</span>
                    <strong className="error">{conventionsSummary.avg_rejection_rate_pct?.toFixed(2)}%</strong>
                  </div>
                  <div className="stat-row">
                    <span>Délai Moyen:</span>
                    <strong>{conventionsSummary.avg_processing_days?.toFixed(1)} jours</strong>
                  </div>
                </div>
              </div>

              <div className="metric-card">
                <h3>Par Statut</h3>
                {conventionsByStatus.length > 0 ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={conventionsByStatus}
                        dataKey="total_conventions"
                        nameKey="statut"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        label
                      >
                        {conventionsByStatus.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="no-data">Aucune donnée</div>
                )}
              </div>
            </div>

            <div className="metric-card full-width">
              <h3>Tendances Mensuelles</h3>
              {conventionsTrends.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={conventionsTrends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="annee_mois" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="nombre_conventions" stroke="#3B82F6" name="Total" />
                    <Line type="monotone" dataKey="conventions_validees" stroke="#10B981" name="Approuvées" />
                    <Line type="monotone" dataKey="conventions_rejetees" stroke="#EF4444" name="Rejetées" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="no-data">Aucune donnée</div>
              )}
            </div>
          </section>

          {/* ===== APPROVAL DELAYS SECTION ===== */}
          <section className="dashboard-section">
            <h2>⏱️ Délais d'Approbation</h2>

            <div className="section-grid">
              <div className="metric-card">
                <h3>Résumé des Délais</h3>
                <div className="summary-stats">
                  <div className="stat-row">
                    <span>Total Suivi:</span>
                    <strong>{delaysSummary.total_conventions_tracked?.toLocaleString('fr-FR')}</strong>
                  </div>
                  <div className="stat-row">
                    <span>Délai Moyen:</span>
                    <strong>{delaysSummary.avg_approval_days?.toFixed(1)}</strong>
                  </div>
                  <div className="stat-row">
                    <span>Délai Médian:</span>
                    <strong>{delaysSummary.median_approval_days?.toFixed(1)}</strong>
                  </div>
                  <div className="stat-row">
                    <span>Délai Min:</span>
                    <strong className="success">{delaysSummary.min_approval_days?.toFixed(1)}</strong>
                  </div>
                  <div className="stat-row">
                    <span>Délai Max:</span>
                    <strong className="error">{delaysSummary.max_approval_days?.toFixed(1)}</strong>
                  </div>
                  <div className="stat-row">
                    <span>P95 Délai:</span>
                    <strong>{delaysSummary.p95_approval_days?.toFixed(1)}</strong>
                  </div>
                  <div className="stat-row">
                    <span>Approuvées:</span>
                    <strong className="success">{delaysSummary.conventions_approved?.toLocaleString('fr-FR')}</strong>
                  </div>
                  <div className="stat-row">
                    <span>Rejetées:</span>
                    <strong className="error">{delaysSummary.conventions_rejected?.toLocaleString('fr-FR')}</strong>
                  </div>
                </div>
              </div>

              <div className="metric-card">
                <h3>Par Étape Actuelle</h3>
                {delaysByEtape.length > 0 ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={delaysByEtape}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="etape_actuelle" angle={-45} textAnchor="end" height={100} />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="avg_approval_days" fill="#F59E0B" name="Délai Moyen (j)" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="no-data">Aucune donnée</div>
                )}
              </div>
            </div>

            <div className="metric-card full-width">
              <h3>Tendances des Délais</h3>
              {delaysTrends.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={delaysTrends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="annee_mois" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="avg_approval_days" stroke="#F59E0B" name="Moyenne" />
                    <Line type="monotone" dataKey="median_approval_days" stroke="#3B82F6" name="Médiane" />
                    <Line type="monotone" dataKey="p95_approval_days" stroke="#EF4444" name="P95" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="no-data">Aucune donnée</div>
              )}
            </div>

            <div className="metric-card full-width">
              <h3>Délais par Statut</h3>
              {delaysByStatus.length > 0 ? (
                <div className="table-container">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Statut</th>
                        <th>Étape</th>
                        <th>Enregistrements</th>
                        <th>Total Conventions</th>
                        <th>Délai Moyen (j)</th>
                        <th>Délai Médian (j)</th>
                        <th>Délai P95 (j)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {delaysByStatus.map((row, idx) => (
                        <tr key={idx}>
                          <td>{row.statut}</td>
                          <td>{row.etape_actuelle}</td>
                          <td>{row.records_count}</td>
                          <td>{row.total_conventions?.toLocaleString('fr-FR')}</td>
                          <td>{row.avg_approval_days?.toFixed(1)}</td>
                          <td>{row.median_approval_days?.toFixed(1)}</td>
                          <td>{row.p95_approval_days?.toFixed(1)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="no-data">Aucune donnée</div>
              )}
            </div>
          </section>
        </>
      )}
    </div>
  );
};

export default ComplianceCompliance;
