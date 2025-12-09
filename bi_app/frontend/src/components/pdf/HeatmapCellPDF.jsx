import React from 'react';
import { View, Text, StyleSheet } from '@react-pdf/renderer';

const styles = StyleSheet.create({
  cell: {
    padding: 8,
    borderRadius: 6,
    marginBottom: 8,
    minHeight: 60,
    justifyContent: 'center',
    alignItems: 'center',
  },
  zoneName: {
    fontSize: 8,
    fontWeight: 'bold',
    marginBottom: 4,
    textAlign: 'center',
  },
  riskValue: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 2,
  },
  occupation: {
    fontSize: 7,
    opacity: 0.8,
    marginTop: 2,
  },
});

export default function HeatmapCellPDF({ zone, value, occupation }) {
  const getColor = () => {
    if (value >= 80) return { bg: '#ef4444', text: '#ffffff' }; // Rouge
    if (value >= 60) return { bg: '#f59e0b', text: '#ffffff' }; // Orange
    if (value >= 40) return { bg: '#eab308', text: '#1f2937' }; // Jaune
    return { bg: '#10b981', text: '#ffffff' }; // Vert
  };
  
  const getRiskLabel = () => {
    if (value >= 80) return 'Critique';
    if (value >= 60) return 'Élevé';
    if (value >= 40) return 'Modéré';
    return 'Faible';
  };
  
  const colors = getColor();
  const occupationValue = typeof occupation === 'number' ? occupation : parseFloat(occupation) || 0;
  
  return (
    <View style={[styles.cell, {
      backgroundColor: colors.bg,
    }]}>
      <Text style={[styles.zoneName, { color: colors.text }]}>
        {zone}
      </Text>
      <Text style={[styles.riskValue, { color: colors.text }]}>
        {value.toFixed(0)}%
      </Text>
      <Text style={[styles.occupation, { color: colors.text }]}>
        Occ: {occupationValue.toFixed(0)}%
      </Text>
    </View>
  );
}

