import React from 'react';
import { View, Text, Svg, Line, G, Defs, ClipPath, Rect, Path } from '@react-pdf/renderer';

export default function SectorBarChartPDF({ 
  data, 
  width = 500, 
  height = 300,
  style 
}) {
  if (!data || data.length === 0) {
    return (
      <View style={[{ width, height, justifyContent: 'center', alignItems: 'center' }, style]}>
        <Text style={{ fontSize: 12, color: '#6b7280' }}>Aucune donnée disponible</Text>
      </View>
    );
  }

  // Calculer les valeurs max pour les deux séries
  const maxClients = Math.max(...data.map(item => item.nombre_clients || 0));
  const maxCA = Math.max(...data.map(item => item.ca_total || 0));
  const maxValue = Math.max(maxClients, maxCA);
  
  // Dimensions basées sur la structure Recharts fournie
  const padding = 5; // Padding pour éviter le débordement
  const yAxisLabelWidth = 160; // Largeur pour les labels Y (encore réduite pour pousser vers la gauche)
  const chartAreaX = yAxisLabelWidth + padding; // Position X du début de la zone de graphique
  const chartAreaWidth = width - chartAreaX - padding; // Largeur de la zone de graphique (avec padding)
  const chartAreaHeight = height - 60; // Hauteur de la zone de graphique (336 dans Recharts)
  const chartAreaY = 5; // Position Y du début de la zone de graphique
  const xAxisY = chartAreaY + chartAreaHeight; // Position Y de l'axe X (341 dans Recharts)
  const xAxisHeight = 30; // Hauteur pour l'axe X et ses labels
  const legendHeight = 20; // Hauteur pour la légende
  
  // Dimensions des barres (basées sur le SVG: barres de 10px de haut)
  const barHeight = 10;
  const totalBars = data.length;
  const spacingBetweenBars = 14; // Espacement entre les deux séries de barres (clients et CA)
  
  // Calculer les positions verticales basées sur le SVG Recharts
  // Les lignes horizontales de la grille sont espacées de ~30.54px (336 / 11 secteurs)
  const gridLineSpacing = chartAreaHeight / (totalBars + 1);
  
  // Positions des lignes horizontales de la grille (au centre de chaque paire de barres)
  const horizontalGridLines = [];
  for (let i = 0; i <= totalBars + 1; i++) {
    if (i === 0) {
      horizontalGridLines.push(chartAreaY); // y=5
    } else if (i === totalBars + 1) {
      horizontalGridLines.push(xAxisY); // y=341
    } else {
      // Positions calculées comme dans Recharts: 20.27, 50.81, 81.36, etc.
      const yPos = chartAreaY + (i * gridLineSpacing);
      horizontalGridLines.push(yPos);
    }
  }
  
  // Couleurs des barres
  const clientsColor = '#0ea5e9'; // Bleu pour "Nombre de clients"
  const caColor = '#10b981'; // Vert pour "CA Total"
  
  // Calculer les graduations pour l'axe X (5 graduations)
  const tickCount = 5;
  const ticks = Array.from({ length: tickCount }, (_, i) => {
    const value = (maxValue / (tickCount - 1)) * i;
    return Math.round(value);
  });
  
  // Positions des ticks de l'axe X
  const tickPositions = ticks.map((_, i) => {
    return chartAreaX + (i / (tickCount - 1)) * chartAreaWidth;
  });
  
  // Positions verticales des barres (basées sur le SVG exact)
  // Barres clients: y=8.05, 38.6, 69.14, etc. (environ 12px avant la ligne de grille)
  // Barres CA: y=22.05, 52.6, 83.14, etc. (environ 2px après la ligne de grille)
  const barPositionsClients = horizontalGridLines.slice(1, -1).map((gridY) => {
    return gridY - 12; // Positionner 12px avant la ligne de grille
  });
  
  const barPositionsCA = horizontalGridLines.slice(1, -1).map((gridY) => {
    return gridY + 2; // Positionner 2px après la ligne de grille
  });

  return (
    <View style={[{ width, height: chartAreaY + chartAreaHeight + xAxisHeight + legendHeight }, style]}>
      {/* Conteneur SVG principal (recharts-surface) */}
      <Svg 
        style={{ 
          position: 'relative',
          width: width,
          height: chartAreaY + chartAreaHeight + xAxisHeight
        }}
        viewBox={`0 0 ${width} ${chartAreaY + chartAreaHeight + xAxisHeight}`}
      >
        {/* Defs avec ClipPath */}
        <Defs>
          <ClipPath id="recharts-sector-clip">
            <Rect 
              x={chartAreaX} 
              y={chartAreaY} 
              width={chartAreaWidth} 
              height={chartAreaHeight} 
            />
          </ClipPath>
        </Defs>
        
        {/* Groupe recharts-cartesian-grid */}
        <G>
          {/* Groupe recharts-cartesian-grid-horizontal */}
          <G>
            {/* Lignes horizontales de la grille (stroke-dasharray="3 3", stroke="#ccc") */}
            {horizontalGridLines.map((yPosition, index) => {
              // Créer des segments pointillés manuellement
              const dashLength = 3;
              const gapLength = 3;
              const segments = [];
              let currentX = chartAreaX;
              while (currentX < chartAreaX + chartAreaWidth) {
                segments.push(
                  <Line
                    key={`h-${index}-seg-${segments.length}`}
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
          
          {/* Groupe recharts-cartesian-grid-vertical */}
          <G>
            {/* Lignes verticales de la grille (alignées avec les ticks de l'axe X) */}
            {tickPositions.map((xPosition, i) => {
              // Créer des segments pointillés manuellement (stroke-dasharray="3 3")
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
        </G>
        
        {/* Groupe recharts-cartesian-axis recharts-xAxis (axe X) */}
        <G>
          {/* Ligne d'axe X (orientation="bottom") - ligne horizontale en bas */}
          <Line
            x1={chartAreaX}
            y1={xAxisY}
            x2={chartAreaX + chartAreaWidth}
            y2={xAxisY}
            stroke="#666"
            strokeWidth={1}
          />
          
          {/* Groupe recharts-cartesian-axis-ticks */}
          <G>
            {/* Ticks de l'axe X */}
            {ticks.map((tick, i) => {
              const xPosition = tickPositions[i];
              return (
                <G key={i}>
                  {/* Ligne de tick (petite marque verticale vers le bas) */}
                  <Line
                    x1={xPosition}
                    y1={xAxisY + 6}
                    x2={xPosition}
                    y2={xAxisY}
                    stroke="#666"
                    strokeWidth={1}
                  />
                </G>
              );
            })}
          </G>
        </G>
        
        {/* Groupe recharts-cartesian-axis recharts-yAxis (axe Y) */}
        <G>
          {/* Ligne d'axe Y (orientation="left") - ligne verticale à gauche */}
          <Line
            x1={chartAreaX}
            y1={chartAreaY}
            x2={chartAreaX}
            y2={xAxisY}
            stroke="#666"
            strokeWidth={1}
          />
          
          {/* Groupe recharts-cartesian-axis-ticks */}
          <G>
            {/* Ticks de l'axe Y (marques horizontales vers la gauche) */}
            {horizontalGridLines.slice(1, -1).map((yPosition, index) => {
              return (
                <G key={index}>
                  {/* Ligne de tick (petite marque horizontale vers la gauche) */}
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
        </G>
        
        {/* Groupe recharts-layer recharts-bar - Nombre de clients */}
        <G clipPath="url(#recharts-sector-clip)">
          {/* Groupe recharts-bar-rectangles */}
          <G>
            {data.map((item, index) => {
              const value = item.nombre_clients || 0;
              const barLength = maxValue > 0 ? (value / maxValue) * chartAreaWidth : 0;
              const barY = barPositionsClients[index];
              const barX = chartAreaX;
              
              // Créer un path avec coins arrondis à droite (radius="0,8,8,0")
              // Pour les très petites barres, utiliser un radius proportionnel
              const radius = barLength < 16 ? Math.min(barLength / 2, 8) : 8;
              const path = barLength < 16 
                ? `M${barX},${barY}L${barX + barLength},${barY}L${barX + barLength},${barY + barHeight}L${barX},${barY + barHeight}Z`
                : `M${barX},${barY}L${barX + barLength - radius},${barY}A${radius},${radius},0,0,1,${barX + barLength},${barY + radius}L${barX + barLength},${barY + barHeight - radius}A${radius},${radius},0,0,1,${barX + barLength - radius},${barY + barHeight}L${barX},${barY + barHeight}Z`;
              
              return (
                <G key={`clients-${index}`}>
                  <Path
                    d={path}
                    fill={clientsColor}
                  />
                </G>
              );
            })}
          </G>
        </G>
        
        {/* Groupe recharts-layer recharts-bar - CA Total */}
        <G clipPath="url(#recharts-sector-clip)">
          {/* Groupe recharts-bar-rectangles */}
          <G>
            {data.map((item, index) => {
              const value = item.ca_total || 0;
              const barLength = maxValue > 0 ? (value / maxValue) * chartAreaWidth : 0;
              const barY = barPositionsCA[index];
              const barX = chartAreaX;
              
              // Créer un path avec coins arrondis à droite (radius="0,8,8,0")
              // Pour les très petites barres, utiliser un radius proportionnel
              const radius = barLength < 16 ? Math.min(barLength / 2, 8) : 8;
              const path = barLength < 16 
                ? `M${barX},${barY}L${barX + barLength},${barY}L${barX + barLength},${barY + barHeight}L${barX},${barY + barHeight}Z`
                : `M${barX},${barY}L${barX + barLength - radius},${barY}A${radius},${radius},0,0,1,${barX + barLength},${barY + radius}L${barX + barLength},${barY + barHeight - radius}A${radius},${radius},0,0,1,${barX + barLength - radius},${barY + barHeight}L${barX},${barY + barHeight}Z`;
              
              return (
                <G key={`ca-${index}`}>
                  <Path
                    d={path}
                    fill={caColor}
                  />
                </G>
              );
            })}
          </G>
        </G>
      </Svg>
      
      {/* Labels Y - Secteurs d'activité (en dehors du SVG) */}
      <View style={{ 
        position: 'absolute', 
        left: 0, 
        top: chartAreaY, 
        width: yAxisLabelWidth, 
        height: chartAreaHeight 
      }}>
        {data.map((item, index) => {
          const yPosition = horizontalGridLines[index + 1]; // Utiliser les lignes de grille (sans les bords)
          const secteurName = String(item.secteur_activite || '');
          
          // Diviser le nom en plusieurs lignes si nécessaire (max 3 lignes comme dans Recharts)
          const words = secteurName.split(' ');
          const lines = [];
          let currentLine = '';
          
          words.forEach((word, i) => {
            if ((currentLine + word).length <= 25 && lines.length < 3) {
              currentLine += (currentLine ? ' ' : '') + word;
            } else {
              if (currentLine) lines.push(currentLine);
              currentLine = word;
            }
          });
          if (currentLine && lines.length < 3) lines.push(currentLine);
          
          return (
            <View 
              key={index}
              style={{ 
                position: 'absolute',
                top: yPosition - (lines.length * 6),
                width: '100%',
                height: lines.length * 12,
                justifyContent: 'center',
                alignItems: 'flex-end',
                paddingRight: 8
              }}
            >
              {lines.map((line, lineIndex) => (
                <Text 
                  key={lineIndex}
                  style={{ 
                    fontSize: 8, 
                    color: '#666', 
                    textAlign: 'right',
                    lineHeight: 1.2
                  }}
                >
                  {line}
                </Text>
              ))}
            </View>
          );
        })}
      </View>
      
      {/* Labels X - Valeurs numériques (en dehors du SVG) */}
      <View style={{ 
        position: 'absolute', 
        left: chartAreaX, 
        top: xAxisY + 8, 
        width: chartAreaWidth, 
        height: xAxisHeight - 8 
      }}>
        {ticks.map((tick, i) => {
          const xPosition = tickPositions[i] - chartAreaX;
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
                minWidth: 30
              }}>
                {tick.toLocaleString('fr-FR')}
              </Text>
            </View>
          );
        })}
      </View>
      
      {/* Légende (recharts-legend-wrapper) */}
      <View style={{
        position: 'absolute',
        left: 5,
        bottom: 5,
        width: width - 10,
        height: legendHeight,
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        {/* Item 1: Nombre de clients */}
        <View style={{
          flexDirection: 'row',
          alignItems: 'center',
          marginRight: 10
        }}>
          <Svg width={14} height={14} viewBox="0 0 32 32" style={{ marginRight: 4 }}>
            <Path
              d="M0,4h32v24h-32z"
              fill={clientsColor}
            />
          </Svg>
          <Text style={{
            fontSize: 8,
            color: clientsColor
          }}>
            Nombre de clients
          </Text>
        </View>
        
        {/* Item 2: CA Total */}
        <View style={{
          flexDirection: 'row',
          alignItems: 'center',
          marginRight: 10
        }}>
          <Svg width={14} height={14} viewBox="0 0 32 32" style={{ marginRight: 4 }}>
            <Path
              d="M0,4h32v24h-32z"
              fill={caColor}
            />
          </Svg>
          <Text style={{
            fontSize: 8,
            color: caColor
          }}>
            CA Total
          </Text>
        </View>
      </View>
    </View>
  );
}
