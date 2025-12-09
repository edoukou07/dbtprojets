import React from 'react';
import { View, Text, Svg, Line, G, Defs, ClipPath, Rect, Path, Circle } from '@react-pdf/renderer';

export default function LineChartPDF({ 
  data, 
  dataKeys = [], // Array of { key, color, name, yAxisId }
  labelKey = 'label',
  width = 500, 
  height = 300,
  style 
}) {
  if (!data || data.length === 0 || !dataKeys || dataKeys.length === 0) {
    return (
      <View style={[{ width, height, justifyContent: 'center', alignItems: 'center' }, style]}>
        <Text style={{ fontSize: 12, color: '#6b7280' }}>Aucune donnée disponible</Text>
      </View>
    );
  }

  // Séparer les séries par yAxisId
  const leftSeries = dataKeys.filter(dk => !dk.yAxisId || dk.yAxisId === 'left');
  const rightSeries = dataKeys.filter(dk => dk.yAxisId === 'right');

  // Calculer les valeurs maximales pour chaque axe
  const maxLeftValue = Math.max(
    ...data.flatMap(item => 
      leftSeries.map(dk => item[dk.key] || 0)
    )
  );
  const maxRightValue = rightSeries.length > 0 ? Math.max(
    ...data.flatMap(item => 
      rightSeries.map(dk => item[dk.key] || 0)
    )
  ) : 0;

  // Dimensions du graphique
  const padding = 5;
  const yAxisLabelWidth = 40;
  const rightYAxisLabelWidth = rightSeries.length > 0 ? 40 : 0;
  const chartAreaX = yAxisLabelWidth + padding;
  // Distance de 6cm entre les axes Y (6cm = 170 points à 72 DPI)
  const targetChartAreaWidth = 170; // 6cm en points
  const availableWidth = width - chartAreaX - rightYAxisLabelWidth - padding - 10;
  const chartAreaWidth = Math.min(targetChartAreaWidth, availableWidth);
  const chartAreaHeight = height - 80;
  const chartAreaY = 20;
  const xAxisY = chartAreaY + chartAreaHeight;
  const xAxisHeight = 40;
  const legendHeight = 30;

  // Calculer les graduations pour l'axe Y gauche
  const tickCount = 5;
  const leftYTicks = Array.from({ length: tickCount }, (_, i) => {
    const value = (maxLeftValue / (tickCount - 1)) * i;
    return Math.round(value);
  });

  // Calculer les graduations pour l'axe Y droit
  const rightYTicks = rightSeries.length > 0 && maxRightValue > 0 ? Array.from({ length: tickCount }, (_, i) => {
    const value = (maxRightValue / (tickCount - 1)) * i;
    return Math.round(value);
  }) : [];

  // Calculer les graduations pour l'axe X
  const xTickCount = Math.min(data.length, 12);
  const xTickIndices = Array.from({ length: xTickCount }, (_, i) => {
    return Math.floor((i / (xTickCount - 1)) * (data.length - 1));
  });

  // Positions des ticks de l'axe X
  const xTickPositions = xTickIndices.map((_, i) => {
    return chartAreaX + (i / (xTickCount - 1)) * chartAreaWidth;
  });

  // Fonction pour formater les valeurs
  const formatValue = (value) => {
    if (value === 0) return '0';
    return value.toString();
  };

  // Calculer les points pour chaque série
  const seriesPoints = dataKeys.map(dataKey => {
    const isRightAxis = dataKey.yAxisId === 'right';
    const maxValue = isRightAxis ? maxRightValue : maxLeftValue;
    
    const points = data.map((item, index) => {
      const value = item[dataKey.key] || 0;
      const x = chartAreaX + (index / (data.length - 1)) * chartAreaWidth;
      const y = xAxisY - (value / maxValue) * chartAreaHeight;
      return { x, y, value };
    });
    return { ...dataKey, points, isRightAxis };
  });

  return (
    <View style={[{ width, height: chartAreaY + chartAreaHeight + xAxisHeight + legendHeight }, style]}>
      <Svg 
        style={{ 
          position: 'relative',
          width: width,
          height: chartAreaY + chartAreaHeight + xAxisHeight
        }}
        viewBox={`0 0 ${width} ${chartAreaY + chartAreaHeight + xAxisHeight}`}
      >
        <Defs>
          <ClipPath id="line-chart-clip">
            <Rect 
              x={chartAreaX} 
              y={chartAreaY} 
              width={chartAreaWidth} 
              height={chartAreaHeight} 
            />
          </ClipPath>
        </Defs>

        {/* Grille horizontale (basée sur l'axe gauche) */}
        <G>
          {leftYTicks.map((tick, i) => {
            const yPosition = chartAreaY + chartAreaHeight - (tick / maxLeftValue) * chartAreaHeight;
            const dashLength = 3;
            const gapLength = 3;
            const segments = [];
            let currentX = chartAreaX;
            while (currentX < chartAreaX + chartAreaWidth) {
              segments.push(
                <Line
                  key={`h-${i}-seg-${segments.length}`}
                  x1={currentX}
                  y1={yPosition}
                  x2={Math.min(currentX + dashLength, chartAreaX + chartAreaWidth)}
                  y2={yPosition}
                  stroke="#ccc"
                  strokeWidth={0.5}
                />
              );
              currentX += dashLength + gapLength;
            }
            return segments;
          })}
        </G>

        {/* Grille verticale */}
        <G>
          {xTickPositions.map((xPosition, i) => {
            const dashLength = 3;
            const gapLength = 3;
            const segments = [];
            let currentY = chartAreaY;
            while (currentY < xAxisY) {
              segments.push(
                <Line
                  key={`v-${i}-seg-${segments.length}`}
                  x1={xPosition}
                  y1={currentY}
                  x2={xPosition}
                  y2={Math.min(currentY + dashLength, xAxisY)}
                  stroke="#ccc"
                  strokeWidth={0.5}
                />
              );
              currentY += dashLength + gapLength;
            }
            return segments;
          })}
        </G>

        {/* Axe X */}
        <G>
          <Line
            x1={chartAreaX}
            y1={xAxisY}
            x2={chartAreaX + chartAreaWidth}
            y2={xAxisY}
            stroke="#666"
            strokeWidth={1}
          />
          {xTickPositions.map((xPosition, i) => (
            <G key={i}>
              <Line
                x1={xPosition}
                y1={xAxisY + 6}
                x2={xPosition}
                y2={xAxisY}
                stroke="#666"
                strokeWidth={1}
              />
            </G>
          ))}
        </G>

        {/* Axe Y gauche */}
        <G>
          <Line
            x1={chartAreaX}
            y1={chartAreaY}
            x2={chartAreaX}
            y2={xAxisY}
            stroke="#666"
            strokeWidth={1}
          />
          {leftYTicks.map((tick, i) => {
            const yPosition = chartAreaY + chartAreaHeight - (tick / maxLeftValue) * chartAreaHeight;
            return (
              <G key={i}>
                <Line
                  x1={chartAreaX - 6}
                  y1={yPosition}
                  x2={chartAreaX}
                  y2={yPosition}
                  stroke="#666"
                  strokeWidth={1}
                />
              </G>
            );
          })}
        </G>

        {/* Axe Y droit */}
        {rightSeries.length > 0 && (
          <G>
            <Line
              x1={chartAreaX + chartAreaWidth}
              y1={chartAreaY}
              x2={chartAreaX + chartAreaWidth}
              y2={xAxisY}
              stroke="#666"
              strokeWidth={1}
            />
            {rightYTicks.map((tick, i) => {
              const yPosition = chartAreaY + chartAreaHeight - (tick / maxRightValue) * chartAreaHeight;
              return (
                <G key={i}>
                  <Line
                    x1={chartAreaX + chartAreaWidth}
                    y1={yPosition}
                    x2={chartAreaX + chartAreaWidth + 6}
                    y2={yPosition}
                    stroke="#666"
                    strokeWidth={1}
                  />
                </G>
              );
            })}
          </G>
        )}

        {/* Lignes et points */}
        <G clipPath="url(#line-chart-clip)">
          {seriesPoints.map((series, seriesIndex) => (
            <G key={seriesIndex}>
              {/* Ligne */}
              <Path
                d={`M${series.points[0].x},${series.points[0].y}${series.points.slice(1).map(p => ` L${p.x},${p.y}`).join('')}`}
                stroke={series.color}
                strokeWidth={2}
                fill="none"
              />
              {/* Points */}
              {series.points.map((point, pointIndex) => (
                <Circle
                  key={pointIndex}
                  cx={point.x}
                  cy={point.y}
                  r={3}
                  fill={series.color}
                  stroke="#fff"
                  strokeWidth={1}
                />
              ))}
            </G>
          ))}
        </G>
      </Svg>

      {/* Labels Y gauche */}
      <View style={{ 
        position: 'absolute', 
        left: 0, 
        top: chartAreaY, 
        width: yAxisLabelWidth, 
        height: chartAreaHeight 
      }}>
        {leftYTicks.map((tick, i) => {
          const yPosition = chartAreaHeight - (tick / maxLeftValue) * chartAreaHeight;
          return (
            <View 
              key={i}
              style={{ 
                position: 'absolute',
                top: yPosition - 4,
                width: '100%',
                height: 8,
                justifyContent: 'center',
                alignItems: 'flex-end',
                paddingRight: 8
              }}
            >
              <Text style={{ 
                fontSize: 8, 
                color: '#666', 
                textAlign: 'right',
                fontFamily: 'Helvetica',
                lineHeight: 1
              }}>
                {formatValue(tick)}
              </Text>
            </View>
          );
        })}
      </View>

      {/* Labels Y droit */}
      {rightSeries.length > 0 && (
        <View style={{ 
          position: 'absolute', 
          right: 0, 
          top: chartAreaY, 
          width: rightYAxisLabelWidth, 
          height: chartAreaHeight 
        }}>
          {rightYTicks.map((tick, i) => {
            // Utiliser exactement le même calcul que pour les ticks (ligne 230)
            // Les ticks sont à: chartAreaY + chartAreaHeight - (tick / maxRightValue) * chartAreaHeight
            // Le View parent est positionné à top: chartAreaY, donc la position relative est:
            const yPosition = maxRightValue > 0 
              ? chartAreaHeight - (tick / maxRightValue) * chartAreaHeight
              : chartAreaHeight;
            return (
              <View 
                key={i}
                style={{ 
                  position: 'absolute',
                  top: yPosition - 4,
                  width: '100%',
                  height: 8,
                  justifyContent: 'center',
                  alignItems: 'flex-start',
                  paddingLeft: 8
                }}
              >
                <Text style={{ 
                  fontSize: 8, 
                  color: '#666', 
                  textAlign: 'left',
                  fontFamily: 'Helvetica',
                  lineHeight: 1
                }}>
                  {formatValue(tick)}
                </Text>
              </View>
            );
          })}
        </View>
      )}

      {/* Labels X */}
      <View style={{ 
        position: 'absolute', 
        left: chartAreaX, 
        top: xAxisY + 8, 
        width: chartAreaWidth, 
        height: xAxisHeight - 8 
      }}>
        {xTickIndices.map((dataIndex, i) => {
          const xPosition = xTickPositions[i] - chartAreaX;
          let label = String(data[dataIndex]?.[labelKey] || '');
          // Formater les trimestres (T1, T2, etc.)
          if (typeof label === 'number' || /^\d+$/.test(label)) {
            label = `T${label}`;
          }
          label = label.replace(/\//g, ' ').trim();
          return (
            <View 
              key={i}
              style={{
                position: 'absolute',
                left: xPosition,
                alignItems: 'center',
                transform: [{ translateX: -15 }]
              }}
            >
              <Text style={{ 
                fontSize: 8, 
                color: '#666',
                textAlign: 'center',
                minWidth: 30,
                fontFamily: 'Helvetica'
              }}>
                {label.substring(0, 8)}
              </Text>
            </View>
          );
        })}
      </View>

      {/* Légende */}
      <View style={{
        position: 'absolute',
        left: chartAreaX,
        bottom: 5,
        width: chartAreaWidth,
        height: legendHeight,
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        gap: 25
      }}>
        {dataKeys.map((dataKey, index) => (
          <View key={index} style={{
            flexDirection: 'row',
            alignItems: 'center',
          }}>
            <Svg width={14} height={14} viewBox="0 0 32 32" style={{ marginRight: 4 }}>
              <Line
                x1="0"
                y1="16"
                x2="32"
                y2="16"
                stroke={dataKey.color}
                strokeWidth={3}
              />
              <Circle
                cx="16"
                cy="16"
                r="4"
                fill={dataKey.color}
                stroke="#fff"
                strokeWidth={1}
              />
            </Svg>
            <Text style={{
              fontSize: 8,
              color: '#666',
              fontFamily: 'Helvetica'
            }}>
              {dataKey.name?.replace(/\//g, ' ') || ''}
            </Text>
          </View>
        ))}
      </View>
    </View>
  );
}

