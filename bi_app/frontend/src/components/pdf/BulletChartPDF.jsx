import React from 'react';
import { View, Text, StyleSheet } from '@react-pdf/renderer';

const styles = StyleSheet.create({
  container: {
    marginBottom: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  label: {
    fontSize: 9,
    fontWeight: 'bold',
    color: '#374151',
  },
  value: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#111827',
  },
  barContainer: {
    position: 'relative',
    height: 24,
    backgroundColor: '#f3f4f6',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 4,
  },
  backgroundZones: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    flexDirection: 'row',
  },
  zone: {
    height: '100%',
  },
  valueBar: {
    position: 'absolute',
    top: 0,
    left: 0,
    height: '100%',
    borderRadius: 4,
  },
  targetMarker: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    width: 2,
    backgroundColor: '#2563eb',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    fontSize: 7,
    color: '#6b7280',
  },
  targetLabel: {
    color: '#2563eb',
    fontWeight: 'bold',
  },
  description: {
    fontSize: 7,
    color: '#6b7280',
    marginTop: 4,
    marginLeft: 4,
  },
});

export default function BulletChartPDF({ 
  label, 
  value, 
  threshold, 
  warning, 
  target, 
  max,
  unit = '%' // Unité personnalisée, par défaut '%'
}) {
  const percentage = (value / max) * 100;
  const thresholdPercentage = (threshold / max) * 100;
  const warningPercentage = (warning / max) * 100;
  const targetPercentage = (target / max) * 100;
  
  const getColor = () => {
    if (value >= threshold) return '#ef4444'; // Rouge
    if (value >= warning) return '#f59e0b'; // Orange
    return '#10b981'; // Vert
  };
  
  const getStatusIcon = () => {
    if (value >= threshold) return '🔴';
    if (value >= warning) return '🟠';
    return '🟢';
  };
  
  const color = getColor();
  const statusIcon = getStatusIcon();
  
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.label}>
          {statusIcon} {label}
        </Text>
        <Text style={styles.value}>{value.toFixed(1)}{unit}</Text>
      </View>
      
      <View style={styles.barContainer}>
        {/* Zones de couleur en arrière-plan */}
        <View style={styles.backgroundZones}>
          <View style={[styles.zone, { 
            width: `${warningPercentage}%`, 
            backgroundColor: '#dcfce7' 
          }]} />
          <View style={[styles.zone, { 
            width: `${thresholdPercentage - warningPercentage}%`, 
            backgroundColor: '#fef3c7' 
          }]} />
          <View style={[styles.zone, { 
            width: `${100 - thresholdPercentage}%`, 
            backgroundColor: '#fee2e2' 
          }]} />
        </View>
        
        {/* Barre de valeur */}
        <View style={[styles.valueBar, {
          width: `${percentage}%`,
          backgroundColor: color,
        }]} />
        
        {/* Marqueur cible */}
        <View style={[styles.targetMarker, {
          left: `${targetPercentage}%`,
        }]} />
      </View>
      
      <View style={styles.footer}>
        <Text>0</Text>
        <Text style={styles.targetLabel}>Cible: {target}%</Text>
        <Text>{max}%</Text>
      </View>
    </View>
  );
}

