import React from 'react';
import { View, Text } from '@react-pdf/renderer';

export default function BarChartPDF({ 
  data, 
  dataKey, 
  labelKey, 
  color = '#0ea5e9', 
  width = 500, 
  height = 300,
  horizontal = false,
  style 
}) {
  if (!data || data.length === 0) {
    return (
      <View style={[{ width, height, justifyContent: 'center', alignItems: 'center' }, style]}>
        <Text style={{ fontSize: 12, color: '#6b7280' }}>Aucune donnée disponible</Text>
      </View>
    );
  }

  const maxValue = Math.max(...data.map(item => item[dataKey] || 0));
  const barWidth = horizontal ? 20 : (width - 100) / data.length;
  const chartHeight = height - 60;
  const chartWidth = width - 100;

  return (
    <View style={[{ width, height }, style]}>
      {horizontal ? (
        // Graphique horizontal
        <View style={{ flexDirection: 'row', height: chartHeight }}>
          {/* Labels Y */}
          <View style={{ width: 80, marginRight: 10 }}>
            {data.map((item, index) => (
              <View key={index} style={{ 
                height: barWidth + 4, 
                justifyContent: 'center',
                marginBottom: 2
              }}>
                <Text style={{ fontSize: 9, color: '#374151', textAlign: 'right' }}>
                  {String(item[labelKey] || '').substring(0, 15)}
                </Text>
              </View>
            ))}
          </View>
          
          {/* Barres */}
          <View style={{ flex: 1, justifyContent: 'space-between' }}>
            {data.map((item, index) => {
              const value = item[dataKey] || 0;
              const barLength = maxValue > 0 ? (value / maxValue) * chartWidth : 0;
              
              return (
                <View key={index} style={{ 
                  flexDirection: 'row', 
                  alignItems: 'center',
                  marginBottom: 2,
                  height: barWidth
                }}>
                  <View style={{
                    width: barLength,
                    height: barWidth,
                    backgroundColor: color,
                    borderRadius: 2,
                  }} />
                  <Text style={{ 
                    fontSize: 9, 
                    color: '#374151', 
                    marginLeft: 6,
                    minWidth: 40
                  }}>
                    {value.toLocaleString('fr-FR')}
                  </Text>
                </View>
              );
            })}
          </View>
        </View>
      ) : (
        // Graphique vertical
        <View>
          {/* Barres */}
          <View style={{ 
            flexDirection: 'row', 
            alignItems: 'flex-end', 
            height: chartHeight,
            paddingBottom: 20,
            paddingLeft: 10
          }}>
            {data.map((item, index) => {
              const value = item[dataKey] || 0;
              const barHeight = maxValue > 0 ? (value / maxValue) * chartHeight : 0;
              
              return (
                <View key={index} style={{ 
                  flex: 1, 
                  alignItems: 'center',
                  marginHorizontal: 2
                }}>
                  <View style={{
                    width: barWidth * 0.8,
                    height: barHeight,
                    backgroundColor: color,
                    borderRadius: 2,
                    marginBottom: 4,
                  }} />
                  <Text style={{ 
                    fontSize: 8, 
                    color: '#374151',
                    textAlign: 'center',
                  }}>
                    {String(item[labelKey] || '').substring(0, 10)}
                  </Text>
                </View>
              );
            })}
          </View>
          
          {/* Axe Y */}
          <View style={{ 
            height: 20, 
            paddingLeft: 90,
            flexDirection: 'row',
            justifyContent: 'space-between'
          }}>
            <Text style={{ fontSize: 8, color: '#6b7280' }}>0</Text>
            <Text style={{ fontSize: 8, color: '#6b7280' }}>
              {maxValue.toLocaleString('fr-FR')}
            </Text>
          </View>
        </View>
      )}
    </View>
  );
}

