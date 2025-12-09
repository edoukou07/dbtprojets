import React from 'react';
import { Document, Page, Text, View, StyleSheet } from '@react-pdf/renderer';

// Styles pour le document PDF
const styles = StyleSheet.create({
  page: {
    padding: 30,
    fontSize: 10,
    fontFamily: 'Helvetica',
    backgroundColor: '#f9fafb',
  },
  header: {
    marginBottom: 20,
    paddingBottom: 15,
    borderBottom: '2 solid #e5e7eb',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 12,
    color: '#4b5563',
  },
  section: {
    marginBottom: 25,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 12,
    paddingBottom: 8,
    borderBottom: '1 solid #e5e7eb',
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 10,
    justifyContent: 'space-between',
  },
  kpiCard: {
    width: '23.5%',
    backgroundColor: '#ffffff',
    padding: 12,
    borderRadius: 8,
    border: '1 solid #e5e7eb',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    marginBottom: 10,
  },
  kpiTitle: {
    fontSize: 8,
    color: '#6b7280',
    marginBottom: 6,
    fontWeight: 'medium',
  },
  kpiValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 4,
    flexWrap: 'wrap',
  },
  kpiSubtitle: {
    fontSize: 7,
    color: '#9ca3af',
    lineHeight: 1.2,
  },
  alertsPanel: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 20,
    border: '1 solid #e5e7eb',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  alertsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
    paddingBottom: 10,
    borderBottom: '1 solid #e5e7eb',
  },
  alertsTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#111827',
    flexDirection: 'row',
    alignItems: 'center',
  },
  alertBadge: {
    backgroundColor: '#fee2e2',
    color: '#dc2626',
    padding: '2 8',
    borderRadius: 12,
    fontSize: 8,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  alertItem: {
    padding: 10,
    marginBottom: 8,
    borderRadius: 6,
    borderLeft: '4 solid',
  },
  alertTitle: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 4,
  },
  alertMessage: {
    fontSize: 8,
    color: '#6b7280',
    marginBottom: 4,
  },
  alertMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 4,
  },
  alertSeverity: {
    fontSize: 7,
    padding: '2 6',
    borderRadius: 4,
    fontWeight: 'bold',
  },
  alertDate: {
    fontSize: 7,
    color: '#9ca3af',
  },
  emptyState: {
    padding: 20,
    textAlign: 'center',
    color: '#6b7280',
    fontSize: 10,
  },
});

// Couleurs pour les icônes des sections
const SECTION_COLORS = {
  financier: '#3b82f6', // blue
  occupation: '#6366f1', // indigo
  operationnel: '#8b5cf6', // purple
};

// Couleurs pour les cartes KPI
const CARD_COLORS = {
  blue: { bg: '#eff6ff', icon: '#3b82f6', border: '#3b82f6' },
  green: { bg: '#ecfdf5', icon: '#10b981', border: '#10b981' },
  orange: { bg: '#fff7ed', icon: '#f59e0b', border: '#f59e0b' },
  purple: { bg: '#f5f3ff', icon: '#8b5cf6', border: '#8b5cf6' },
  indigo: { bg: '#eef2ff', icon: '#6366f1', border: '#6366f1' },
};

// Couleurs pour les alertes
const ALERT_COLORS = {
  critical: { bg: '#fef2f2', border: '#dc2626', text: '#991b1b', badge: '#fee2e2' },
  high: { bg: '#fff7ed', border: '#f59e0b', text: '#92400e', badge: '#fef3c7' },
  medium: { bg: '#fefce8', border: '#eab308', text: '#854d0e', badge: '#fef9c3' },
  low: { bg: '#eff6ff', border: '#3b82f6', text: '#1e40af', badge: '#dbeafe' },
};

const formatCurrency = (value) => {
  if (!value && value !== 0) return '0 FCFA';
  // Utiliser des espaces comme séparateurs de milliers
  const formatted = new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
    useGrouping: true,
  }).format(value);
  // S'assurer qu'on utilise des espaces et non des caractères spéciaux
  return formatted.replace(/\u202F/g, ' ').replace(/,/g, ' ') + ' FCFA';
};

const formatPercent = (value) => {
  if (!value && value !== 0) return '0%';
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(numValue)) return '0%';
  return numValue.toFixed(1) + '%';
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Composant pour une carte KPI
const KPICard = ({ title, value, subtitle, color = 'blue' }) => {
  return (
    <View style={styles.kpiCard}>
      <Text style={styles.kpiTitle}>{title}</Text>
      <Text style={[styles.kpiValue, { flexWrap: 'wrap' }]}>{value}</Text>
      {subtitle && (
        <Text style={styles.kpiSubtitle} wrap>
          {subtitle}
        </Text>
      )}
    </View>
  );
};

// Composant pour une alerte
const AlertItem = ({ alert }) => {
  const severity = alert.severity || 'low';
  const colors = ALERT_COLORS[severity] || ALERT_COLORS.low;
  const statusLabels = {
    active: 'Active',
    acknowledged: 'Acquittée',
    resolved: 'Résolue',
    dismissed: 'Ignorée',
  };
  const severityLabels = {
    critical: 'Critique',
    high: 'Élevée',
    medium: 'Moyenne',
    low: 'Faible',
  };

  return (
    <View style={[styles.alertItem, {
      backgroundColor: colors.bg,
      borderLeftColor: colors.border,
    }]}>
      <Text style={styles.alertTitle}>{alert.title}</Text>
      <Text style={styles.alertMessage}>{alert.message}</Text>
      <View style={styles.alertMeta}>
        <View style={[styles.alertSeverity, {
          backgroundColor: colors.badge,
          color: colors.text,
        }]}>
          <Text>{severityLabels[severity] || severity}</Text>
        </View>
        <Text style={styles.alertDate}>{formatDate(alert.created_at)}</Text>
      </View>
    </View>
  );
};

export default function DashboardPDF({ 
  financierData,
  occupationData,
  clientsData,
  operationnelData
}) {
  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* En-tête */}
        <View style={styles.header}>
          <Text style={styles.title}>Tableau de Bord Général</Text>
          <Text style={styles.subtitle}>Synthèse des performances SIGETI</Text>
          <Text style={[styles.subtitle, { marginTop: 5, fontSize: 9, color: '#6b7280' }]}>
            Généré le {new Date().toLocaleDateString('fr-FR', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </Text>
        </View>

        {/* Performance Financière */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Performance Financière</Text>
          <View style={styles.grid}>
            <KPICard
              title="CA Facturé"
              value={formatCurrency(financierData?.ca_total)}
              subtitle="Chiffre d'affaires total"
              color="blue"
            />
            <KPICard
              title="CA Payé"
              value={formatCurrency(financierData?.ca_paye)}
              subtitle="Encaissements"
              color="green"
            />
            <KPICard
              title="Créances"
              value={formatCurrency(financierData?.ca_impaye)}
              subtitle="Montant impayé"
              color="orange"
            />
            <KPICard
              title="Taux de Paiement"
              value={formatPercent(financierData?.taux_paiement_moyen)}
              subtitle="Performance recouvrement"
              color="purple"
            />
          </View>
        </View>

        {/* Occupation des Zones */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Occupation des Zones</Text>
          <View style={styles.grid}>
            <KPICard
              title="Total Lots"
              value={occupationData?.total_lots?.toLocaleString('fr-FR') || '0'}
              subtitle="Capacité totale"
              color="indigo"
            />
            <KPICard
              title="Lots Disponibles"
              value={occupationData?.lots_disponibles?.toLocaleString('fr-FR') || '0'}
              subtitle="Offre disponible"
              color="green"
            />
            <KPICard
              title="Lots Attribués"
              value={occupationData?.lots_attribues?.toLocaleString('fr-FR') || '0'}
              subtitle="Lots occupés"
              color="blue"
            />
            <KPICard
              title="Taux d'Occupation"
              value={formatPercent(occupationData?.taux_occupation_moyen)}
              subtitle="Performance occupation"
              color="purple"
            />
          </View>
        </View>

        {/* Performance Opérationnelle */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Performance Opérationnelle</Text>
          <View style={styles.grid}>
            <KPICard
              title="Collectes"
              value={operationnelData?.total_collectes?.toLocaleString('fr-FR') || '0'}
              subtitle="Campagnes de recouvrement"
              color="indigo"
            />
            <KPICard
              title="Demandes"
              value={operationnelData?.total_demandes?.toLocaleString('fr-FR') || '0'}
              subtitle="Attributions"
              color="blue"
            />
            <KPICard
              title="Taux Approbation"
              value={formatPercent(operationnelData?.taux_approbation_moyen)}
              subtitle="Qualité des dossiers"
              color="green"
            />
            <KPICard
              title="Taux Recouvrement"
              value={formatPercent(operationnelData?.taux_recouvrement_moyen)}
              subtitle="Efficacité collecte"
              color="purple"
            />
          </View>
        </View>
      </Page>
    </Document>
  );
}
