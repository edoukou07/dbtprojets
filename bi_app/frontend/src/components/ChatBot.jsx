import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, RefreshCw, Lightbulb, Loader2, BarChart3, Settings, MessageSquare, BookOpen, Search, Filter, Code, Download } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token JWT
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les erreurs 401 (non authentifié)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.warn('⚠️ Non authentifié - Redirection vers /login recommandée');
      // En mode dev, afficher un message plutôt que crasher
      if (window.location.pathname === '/chatbot') {
        alert('Vous devez vous connecter pour utiliser le chatbot.\nRedirection vers la page de connexion...');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

const ChatBot = () => {
  const [activeTab, setActiveTab] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [capabilities, setCapabilities] = useState(null);
  const [preferAI, setPreferAI] = useState(false);
  const [rules, setRules] = useState([]);
  const [rulesCategories, setRulesCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedRules, setExpandedRules] = useState(new Set());
  const [isAuthenticated, setIsAuthenticated] = useState(true); // Supposer authentifié par défaut
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Vérifier l'authentification au chargement
    const token = localStorage.getItem('access_token');
    if (!token) {
      setIsAuthenticated(false);
      console.warn('⚠️ Aucun token trouvé - Veuillez vous connecter');
    }
    
    loadSuggestions();
    loadCapabilities();
    loadRules();
    // Message de bienvenue
    setMessages([{
      type: 'bot',
      content: 'Bonjour ! Je suis votre assistant IA pour SIGETI. Je peux répondre à vos questions sur les finances, l\'occupation des zones, les clients, et bien plus. Comment puis-je vous aider ?',
      timestamp: new Date()
    }]);
  }, []);

  useEffect(() => {
    if (activeTab === 'rules' && selectedCategory !== 'all') {
      loadRules();
    }
  }, [selectedCategory]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadSuggestions = async () => {
    try {
      const response = await apiClient.get('/ai/suggestions/');
      setSuggestions(response.data.suggestions || []);
    } catch (error) {
      console.error('Erreur chargement suggestions:', error);
    }
  };

  const loadCapabilities = async () => {
    try {
      const response = await apiClient.get('/ai/capabilities/');
      setCapabilities(response.data);
    } catch (error) {
      console.error('Erreur chargement capacités:', error);
    }
  };

  const loadRules = async () => {
    try {
      const url = selectedCategory === 'all' 
        ? '/ai/rules/'
        : `/ai/rules/?category=${selectedCategory}`;
      const response = await apiClient.get(url);
      setRules(response.data.rules || []);
      setRulesCategories(response.data.categories || []);
    } catch (error) {
      console.error('Erreur chargement règles:', error);
    }
  };

  const toggleRule = (index) => {
    const newExpanded = new Set(expandedRules);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedRules(newExpanded);
  };

  const getCategoryColor = (category) => {
    const colors = {
      financier: 'bg-green-100 text-green-800 border-green-300',
      occupation: 'bg-blue-100 text-blue-800 border-blue-300',
      clients: 'bg-purple-100 text-purple-800 border-purple-300',
      operationnel: 'bg-orange-100 text-orange-800 border-orange-300',
      general: 'bg-gray-100 text-gray-800 border-gray-300'
    };
    return colors[category] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getCategoryIcon = (category) => {
    const icons = {
      financier: '💰',
      occupation: '🏭',
      clients: '👥',
      operationnel: '📊',
      general: '📋'
    };
    return icons[category] || '📋';
  };

  const filteredRules = rules.filter(rule => {
    if (!searchQuery) return true;
    const search = searchQuery.toLowerCase();
    return (
      rule.description.toLowerCase().includes(search) ||
      rule.patterns.some(p => p.toLowerCase().includes(search)) ||
      rule.category.toLowerCase().includes(search)
    );
  });

  const handleSendMessage = async (text = null) => {
    const messageText = text || input.trim();
    if (!messageText || isLoading) return;

    // Ajouter le message utilisateur
    const userMessage = {
      type: 'user',
      content: messageText,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await apiClient.post('/ai/chat/', {
        question: messageText,
        prefer_ai: preferAI
      });

      // Ajouter la réponse du bot
      console.log('📊 Response data:', response.data);
      console.log('📊 Visualization config:', response.data.visualization);
      console.log('📊 Data:', response.data.data);
      console.log('💡 Contextual suggestions:', response.data.contextual_suggestions);
      console.log('🎯 Business insights:', response.data.business_insights);
      console.log('⚠️ Anomalies:', response.data.anomalies);
      
      const botMessage = {
        type: 'bot',
        content: response.data.answer,
        data: response.data.data,
        visualization: response.data.visualization,
        contextual_suggestions: response.data.contextual_suggestions || [],
        business_insights: response.data.business_insights || [],
        anomalies: response.data.anomalies || [],
        sql: response.data.sql,
        engine: response.data.engine,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Erreur envoi message:', error);
      const errorMessage = {
        type: 'bot',
        content: 'Désolé, une erreur s\'est produite. Veuillez réessayer.',
        error: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    handleSendMessage(suggestion);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const exportToCSV = (data, filename = 'export.csv') => {
    if (!data || data.length === 0) return;
    
    const headers = Object.keys(data[0]);
    const csvContent = [
      headers.join(','),
      ...data.map(row => headers.map(header => {
        const value = row[header];
        return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
      }).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
  };

  const exportChartAsImage = (chartId, filename = 'chart.png') => {
    const svgElement = document.querySelector(`#${chartId} svg`);
    if (!svgElement) return;

    const svgData = new XMLSerializer().serializeToString(svgElement);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();

    canvas.width = svgElement.width.baseVal.value;
    canvas.height = svgElement.height.baseVal.value;

    img.onload = () => {
      ctx.fillStyle = 'white';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
      canvas.toBlob((blob) => {
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();
      });
    };

    img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
  };

  const clearChat = () => {
    setMessages([{
      type: 'bot',
      content: 'Conversation réinitialisée. Comment puis-je vous aider ?',
      timestamp: new Date()
    }]);
  };

  const renderVisualization = (data, vizConfig) => {
    console.log('🎨 renderVisualization called with:', { data, vizConfig });
    if (!data || !vizConfig) {
      console.log('🎨 No data or vizConfig, returning null');
      return null;
    }

    switch (vizConfig.type) {
      case 'kpi':
        return (
          <div className="grid grid-cols-2 gap-3 mt-3">
            {vizConfig.kpis?.map((kpi, idx) => (
              <div key={idx} className="bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-lg border border-blue-200">
                <div className="text-sm text-gray-600 mb-1">{kpi.label}</div>
                <div className="text-2xl font-bold text-blue-600">{kpi.value}</div>
              </div>
            ))}
          </div>
        );

      case 'table':
        if (!data.length) return null;
        const columns = Object.keys(data[0]);
        return (
          <div className="mt-3 overflow-x-auto">
            <table className="min-w-full bg-white border rounded-lg">
              <thead className="bg-gray-50">
                <tr>
                  {columns.map(col => (
                    <th key={col} className="px-4 py-2 text-left text-xs font-semibold text-gray-700 uppercase border-b">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.slice(0, 10).map((row, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    {columns.map(col => (
                      <td key={col} className="px-4 py-2 text-sm text-gray-800 border-b">
                        {row[col]}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {data.length > 10 && (
              <div className="text-xs text-gray-500 mt-2">
                Affichage de 10 sur {data.length} résultats
              </div>
            )}
          </div>
        );

      case 'bar':
        if (!data || !data.length) return null;
        const barColumns = Object.keys(data[0]);
        const barXAxis = vizConfig.x_axis || barColumns[0];
        const barYAxis = vizConfig.y_axis || barColumns[1];
        const barChartId = `bar-chart-${Date.now()}`;
        
        return (
          <div className="mt-3 p-4 bg-white rounded-lg border">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center text-sm text-gray-700 font-semibold">
                <BarChart3 className="w-4 h-4 mr-2" />
                {vizConfig.title || `${barYAxis} par ${barXAxis}`}
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => exportChartAsImage(barChartId, 'graphique-barres.png')}
                  className="px-3 py-1 text-xs bg-blue-50 hover:bg-blue-100 text-blue-600 rounded flex items-center transition-colors"
                  title="Exporter en PNG"
                >
                  <Download className="w-3 h-3 mr-1" />
                  PNG
                </button>
                <button
                  onClick={() => exportToCSV(data, 'donnees.csv')}
                  className="px-3 py-1 text-xs bg-green-50 hover:bg-green-100 text-green-600 rounded flex items-center transition-colors"
                  title="Exporter en CSV"
                >
                  <Download className="w-3 h-3 mr-1" />
                  CSV
                </button>
              </div>
            </div>
            <div id={barChartId}>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={data.slice(0, 15)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey={barXAxis} 
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    fontSize={12}
                  />
                  <YAxis fontSize={12} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey={barYAxis} fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            {data.length > 15 && (
              <div className="text-xs text-gray-500 mt-2">
                Affichage des 15 premiers résultats sur {data.length}
              </div>
            )}
          </div>
        );

      case 'line':
        if (!data || !data.length) return null;
        const lineColumns = Object.keys(data[0]);
        const lineXAxis = vizConfig.x_axis || lineColumns[0];
        const lineYAxis = vizConfig.y_axis || lineColumns[1];
        const lineChartId = `line-chart-${Date.now()}`;
        
        return (
          <div className="mt-3 p-4 bg-white rounded-lg border">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center text-sm text-gray-700 font-semibold">
                <BarChart3 className="w-4 h-4 mr-2" />
                {vizConfig.title || `Évolution de ${lineYAxis}`}
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => exportChartAsImage(lineChartId, 'graphique-ligne.png')}
                  className="px-3 py-1 text-xs bg-blue-50 hover:bg-blue-100 text-blue-600 rounded flex items-center transition-colors"
                  title="Exporter en PNG"
                >
                  <Download className="w-3 h-3 mr-1" />
                  PNG
                </button>
                <button
                  onClick={() => exportToCSV(data, 'donnees.csv')}
                  className="px-3 py-1 text-xs bg-green-50 hover:bg-green-100 text-green-600 rounded flex items-center transition-colors"
                  title="Exporter en CSV"
                >
                  <Download className="w-3 h-3 mr-1" />
                  CSV
                </button>
              </div>
            </div>
            <div id={lineChartId}>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={data.slice(0, 20)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey={lineXAxis}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    fontSize={12}
                  />
                  <YAxis fontSize={12} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey={lineYAxis} stroke="#3b82f6" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            {data.length > 20 && (
              <div className="text-xs text-gray-500 mt-2">
                Affichage des 20 premiers points sur {data.length}
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Avertissement si non authentifié */}
      {!isAuthenticated && (
        <div className="bg-yellow-50 border-b border-yellow-200 px-6 py-3">
          <div className="flex items-center text-sm text-yellow-800">
            <span className="mr-2">⚠️</span>
            <span>Vous n'êtes pas connecté. Veuillez vous <a href="/login" className="underline font-semibold">connecter</a> pour utiliser toutes les fonctionnalités du chatbot.</span>
          </div>
        </div>
      )}
      
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Bot className="w-6 h-6 text-blue-600 mr-2" />
            <h1 className="text-xl font-semibold text-gray-800">Assistant IA SIGETI</h1>
            {capabilities && (
              <span className="ml-3 px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-700">
                {capabilities.openai_configured ? 'IA Activée' : 'Règles uniquement'}
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPreferAI(!preferAI)}
              className={`px-3 py-1 text-xs rounded-lg flex items-center ${
                preferAI ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-600'
              }`}
              disabled={!capabilities?.openai_configured}
            >
              <Settings className="w-3 h-3 mr-1" />
              {preferAI ? 'Mode IA' : 'Mode Règles'}
            </button>
            <button
              onClick={clearChat}
              className="px-3 py-1 text-xs rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700 flex items-center"
            >
              <RefreshCw className="w-3 h-3 mr-1" />
              Nouvelle conversation
            </button>
          </div>
        </div>

        {/* Onglets */}
        <div className="flex space-x-1 border-b">
          <button
            onClick={() => setActiveTab('chat')}
            className={`px-4 py-2 text-sm font-medium flex items-center transition-colors ${
              activeTab === 'chat'
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <MessageSquare className="w-4 h-4 mr-2" />
            Conversation
          </button>
          <button
            onClick={() => setActiveTab('rules')}
            className={`px-4 py-2 text-sm font-medium flex items-center transition-colors ${
              activeTab === 'rules'
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <BookOpen className="w-4 h-4 mr-2" />
            Règles ({rules.length})
          </button>
        </div>
      </div>

      {/* Contenu selon l'onglet actif */}
      {activeTab === 'chat' ? (
        <>
          {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex items-start max-w-3xl ${msg.type === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`flex-shrink-0 ${msg.type === 'user' ? 'ml-3' : 'mr-3'}`}>
                {msg.type === 'user' ? (
                  <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                    <User className="w-5 h-5 text-white" />
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                )}
              </div>
              <div className={`rounded-lg px-4 py-3 ${
                msg.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : msg.error
                  ? 'bg-red-50 text-red-800 border border-red-200'
                  : 'bg-white border shadow-sm'
              }`}>
                <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                
                {/* Business Insights */}
                {msg.business_insights && msg.business_insights.length > 0 && (
                  <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="text-xs font-semibold text-blue-800 mb-2 flex items-center">
                      <Lightbulb className="w-3 h-3 mr-1" />
                      Analyse métier
                    </div>
                    <ul className="text-xs text-blue-900 space-y-1">
                      {msg.business_insights.map((insight, i) => (
                        <li key={i} className="flex items-start">
                          <span className="mr-2">•</span>
                          <span>{insight}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Analyse de Tendances */}
                {msg.trend_analysis && (
                  <div className="mt-3 p-4 bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg">
                    <div className="text-xs font-semibold text-purple-800 mb-3 flex items-center">
                      <BarChart3 className="w-4 h-4 mr-2" />
                      Analyse de Tendance
                    </div>
                    
                    {/* Tendance unique */}
                    {msg.trend_analysis.tendance && (
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-700">Tendance:</span>
                          <span className={`text-xs font-semibold px-2 py-1 rounded ${
                            msg.trend_analysis.tendance === 'forte_hausse' ? 'bg-green-100 text-green-800' :
                            msg.trend_analysis.tendance === 'hausse' ? 'bg-green-50 text-green-700' :
                            msg.trend_analysis.tendance === 'stable' ? 'bg-gray-100 text-gray-700' :
                            msg.trend_analysis.tendance === 'baisse' ? 'bg-orange-50 text-orange-700' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {msg.trend_analysis.tendance.replace('_', ' ').toUpperCase()}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          <div className="bg-white p-2 rounded">
                            <div className="text-gray-600">Variation totale</div>
                            <div className={`font-semibold ${
                              msg.trend_analysis.variation_totale_pct > 0 ? 'text-green-600' : 
                              msg.trend_analysis.variation_totale_pct < 0 ? 'text-red-600' : 'text-gray-600'
                            }`}>
                              {msg.trend_analysis.variation_totale_pct > 0 ? '+' : ''}
                              {msg.trend_analysis.variation_totale_pct}%
                            </div>
                          </div>
                          <div className="bg-white p-2 rounded">
                            <div className="text-gray-600">Variation moyenne</div>
                            <div className={`font-semibold ${
                              msg.trend_analysis.variation_moyenne_pct > 0 ? 'text-green-600' : 
                              msg.trend_analysis.variation_moyenne_pct < 0 ? 'text-red-600' : 'text-gray-600'
                            }`}>
                              {msg.trend_analysis.variation_moyenne_pct > 0 ? '+' : ''}
                              {msg.trend_analysis.variation_moyenne_pct}%
                            </div>
                          </div>
                          <div className="bg-white p-2 rounded">
                            <div className="text-gray-600">Prévision</div>
                            <div className="font-semibold text-blue-600">
                              {msg.trend_analysis.prevision_prochaine_periode?.toFixed(2) || 'N/A'}
                            </div>
                          </div>
                          <div className="bg-white p-2 rounded">
                            <div className="text-gray-600">Volatilité</div>
                            <div className={`font-semibold ${
                              msg.trend_analysis.volatilite === 'élevée' ? 'text-orange-600' :
                              msg.trend_analysis.volatilite === 'modérée' ? 'text-yellow-600' :
                              'text-green-600'
                            }`}>
                              {msg.trend_analysis.volatilite}
                            </div>
                          </div>
                        </div>
                        
                        {/* Insights de tendance */}
                        {msg.trend_analysis.insights && msg.trend_analysis.insights.length > 0 && (
                          <div className="mt-2 pt-2 border-t border-purple-200">
                            <div className="text-xs font-medium text-purple-700 mb-1">💡 Insights:</div>
                            <ul className="text-xs text-purple-900 space-y-1">
                              {msg.trend_analysis.insights.map((insight, i) => (
                                <li key={i} className="flex items-start">
                                  <span className="mr-1">•</span>
                                  <span>{insight}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        
                        {/* Saisonnalité */}
                        {msg.trend_analysis.saisonnalite?.detectee && (
                          <div className="mt-2 p-2 bg-purple-100 rounded text-xs">
                            <span className="font-medium">📅 Saisonnalité détectée:</span>
                            <span className="ml-2">Pic au mois {msg.trend_analysis.saisonnalite.mois_fort}, creux au mois {msg.trend_analysis.saisonnalite.mois_faible}</span>
                          </div>
                        )}
                      </div>
                    )}
                    
                    {/* Tendances groupées (par zone, client, etc.) */}
                    {msg.trend_analysis.top_5_hausse && (
                      <div className="space-y-2">
                        <div className="text-xs font-medium text-purple-700">📈 Top 5 en hausse:</div>
                        <div className="space-y-1">
                          {msg.trend_analysis.top_5_hausse.map((item, i) => (
                            <div key={i} className="flex justify-between items-center text-xs bg-green-50 p-2 rounded">
                              <span className="font-medium">{item.entite}</span>
                              <span className="text-green-700 font-semibold">
                                +{item.variation_pct}%
                              </span>
                            </div>
                          ))}
                        </div>
                        
                        {msg.trend_analysis.top_5_baisse && (
                          <>
                            <div className="text-xs font-medium text-purple-700 mt-3">📉 Top 5 en baisse:</div>
                            <div className="space-y-1">
                              {msg.trend_analysis.top_5_baisse.map((item, i) => (
                                <div key={i} className="flex justify-between items-center text-xs bg-red-50 p-2 rounded">
                                  <span className="font-medium">{item.entite}</span>
                                  <span className="text-red-700 font-semibold">
                                    {item.variation_pct}%
                                  </span>
                                </div>
                              ))}
                            </div>
                          </>
                        )}
                        
                        {/* Insights comparatifs */}
                        {msg.trend_analysis.insights && msg.trend_analysis.insights.length > 0 && (
                          <div className="mt-3 pt-2 border-t border-purple-200">
                            <div className="text-xs font-medium text-purple-700 mb-1">💡 Insights:</div>
                            <ul className="text-xs text-purple-900 space-y-1">
                              {msg.trend_analysis.insights.map((insight, i) => (
                                <li key={i}>{insight}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
                
                {/* Alertes Intelligentes */}
                {msg.alerts && msg.alerts.length > 0 && (
                  <div className="mt-3 p-4 bg-gradient-to-r from-red-50 to-orange-50 border-2 border-red-300 rounded-lg">
                    <div className="text-sm font-bold text-red-800 mb-3 flex items-center">
                      🚨 Alertes Intelligentes ({msg.alerts.length})
                    </div>
                    
                    {/* Résumé des alertes */}
                    {msg.alerts_summary && (
                      <div className="mb-3 p-2 bg-white rounded text-xs">
                        <div className="font-semibold mb-2">{msg.alerts_summary.message}</div>
                        <div className="flex gap-3 text-xs">
                          {msg.alerts_summary.critical_count > 0 && (
                            <span className="px-2 py-1 bg-red-100 text-red-800 rounded">
                              🔴 {msg.alerts_summary.critical_count} Critique(s)
                            </span>
                          )}
                          {msg.alerts_summary.warning_count > 0 && (
                            <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded">
                              ⚠️ {msg.alerts_summary.warning_count} Warning(s)
                            </span>
                          )}
                          {msg.alerts_summary.info_count > 0 && (
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                              ℹ️ {msg.alerts_summary.info_count} Info(s)
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                    
                    {/* Liste des alertes (max 5 affichées) */}
                    <div className="space-y-2">
                      {msg.alerts.slice(0, 5).map((alert, i) => (
                        <div 
                          key={i} 
                          className={`p-3 rounded-lg border-l-4 ${
                            alert.severity === 'critical' ? 'bg-red-50 border-red-500' :
                            alert.severity === 'warning' ? 'bg-orange-50 border-orange-500' :
                            'bg-blue-50 border-blue-500'
                          }`}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <span className="text-lg">{alert.icon}</span>
                              <span className="text-xs font-bold text-gray-800">{alert.title}</span>
                            </div>
                            <span className={`text-xs px-2 py-0.5 rounded ${
                              alert.severity === 'critical' ? 'bg-red-200 text-red-900' :
                              alert.severity === 'warning' ? 'bg-orange-200 text-orange-900' :
                              'bg-blue-200 text-blue-900'
                            }`}>
                              {alert.severity.toUpperCase()}
                            </span>
                          </div>
                          
                          <div className="text-xs text-gray-800 font-medium mb-1">
                            {alert.message}
                          </div>
                          
                          {alert.details && (
                            <div className="text-xs text-gray-600 mb-2">
                              {alert.details}
                            </div>
                          )}
                          
                          {alert.recommendations && alert.recommendations.length > 0 && (
                            <div className="mt-2 pt-2 border-t border-gray-200">
                              <div className="text-xs font-semibold text-gray-700 mb-1">
                                💡 Recommandations:
                              </div>
                              <ul className="text-xs text-gray-700 space-y-1">
                                {alert.recommendations.map((rec, j) => (
                                  <li key={j} className="flex items-start">
                                    <span className="mr-1">•</span>
                                    <span>{rec}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ))}
                      
                      {msg.alerts.length > 5 && (
                        <div className="text-xs text-center text-gray-600 italic pt-2 border-t">
                          + {msg.alerts.length - 5} autre(s) alerte(s) - Consultez le rapport complet
                        </div>
                      )}
                    </div>
                  </div>
                )}
                
                {/* Anomalies detectées */}
                {msg.anomalies && msg.anomalies.length > 0 && (
                  <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <div className="text-xs font-semibold text-yellow-800 mb-2 flex items-center">
                      ⚠️ Anomalies détectées ({msg.anomalies.length})
                    </div>
                    <ul className="text-xs text-yellow-900 space-y-1">
                      {msg.anomalies.slice(0, 3).map((anomaly, i) => (
                        <li key={i} className="flex items-start">
                          <span className="mr-2">{anomaly.severity === 'error' ? '🔴' : '⚠️'}</span>
                          <span>{anomaly.message}</span>
                        </li>
                      ))}
                      {msg.anomalies.length > 3 && (
                        <li className="text-yellow-700 italic">
                          + {msg.anomalies.length - 3} autre(s) anomalie(s)
                        </li>
                      )}
                    </ul>
                  </div>
                )}
                
                {msg.engine && (
                  <div className="text-xs mt-2 opacity-70">
                    Moteur: {msg.engine === 'rule-based' ? 'Règles' : 'IA'}
                  </div>
                )}
                {renderVisualization(msg.data, msg.visualization)}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-start max-w-3xl">
              <div className="mr-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
                  <Loader2 className="w-5 h-5 text-white animate-spin" />
                </div>
              </div>
              <div className="bg-white border shadow-sm rounded-lg px-4 py-3">
                <div className="text-sm text-gray-500">En train de réfléchir...</div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions contextuelles */}
      {messages.length > 1 && messages[messages.length - 1]?.contextual_suggestions?.length > 0 && (
        <div className="px-6 py-3 bg-gradient-to-r from-blue-50 to-purple-50 border-t border-blue-200">
          <div className="flex items-center text-sm font-medium text-gray-700 mb-2">
            <Lightbulb className="w-4 h-4 mr-2 text-yellow-500" />
            Questions suggérées pour approfondir:
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {messages[messages.length - 1].contextual_suggestions.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setInput(suggestion.text);
                  setTimeout(() => handleSendMessage(suggestion.text), 100);
                }}
                className="flex items-start p-3 text-left bg-white hover:bg-blue-50 rounded-lg border border-gray-200 hover:border-blue-300 transition-all shadow-sm hover:shadow"
              >
                <span className="text-2xl mr-3 flex-shrink-0">{suggestion.icon}</span>
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900">{suggestion.text}</div>
                  <div className="text-xs text-gray-500 mt-1">{suggestion.reason}</div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Suggestions initiales */}
      {suggestions.length > 0 && messages.length <= 1 && (
        <div className="px-6 py-3 bg-white border-t">
          <div className="flex items-center text-sm text-gray-600 mb-2">
            <Lightbulb className="w-4 h-4 mr-2" />
            Questions suggérées:
          </div>
          <div className="flex flex-wrap gap-2">
            {suggestions.slice(0, 6).map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => handleSuggestionClick(suggestion)}
                className="px-3 py-1.5 text-sm bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg border border-blue-200 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="px-6 py-4 bg-white border-t">
        <div className="flex items-center space-x-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Posez votre question..."
            className="flex-1 px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={() => handleSendMessage()}
            disabled={!input.trim() || isLoading}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-lg flex items-center transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
        </>
      ) : (
        renderRulesTab()
      )}
    </div>
  );

  function renderRulesTab() {
    return (
      <>
        {/* Filtres pour les règles */}
        <div className="bg-white border-b px-6 py-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Recherche */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Rechercher une règle..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Filtre par catégorie */}
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
              >
                <option value="all">Toutes les catégories</option>
                {rulesCategories.map(cat => (
                  <option key={cat} value={cat}>
                    {getCategoryIcon(cat)} {cat.charAt(0).toUpperCase() + cat.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Liste des règles */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {filteredRules.length === 0 ? (
            <div className="bg-white rounded-lg shadow-sm p-8 text-center">
              <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Aucune règle trouvée</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredRules.map((rule, index) => (
                <div
                  key={index}
                  className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
                >
                  {/* Header de la règle */}
                  <div
                    className="p-4 cursor-pointer"
                    onClick={() => toggleRule(index)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getCategoryColor(rule.category)}`}>
                            {getCategoryIcon(rule.category)} {rule.category}
                          </span>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {rule.description}
                          </h3>
                        </div>
                        
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <MessageSquare className="w-4 h-4" />
                          <span className="font-mono bg-gray-50 px-2 py-1 rounded">
                            {rule.example}
                          </span>
                        </div>
                      </div>

                      <button className="ml-4 text-gray-400 hover:text-gray-600">
                        {expandedRules.has(index) ? (
                          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                          </svg>
                        ) : (
                          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Détails expandables */}
                  {expandedRules.has(index) && (
                    <div className="border-t border-gray-200 bg-gray-50 p-4 space-y-4">
                      {/* Patterns */}
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
                          <MessageSquare className="w-4 h-4 mr-2" />
                          Questions reconnues ({rule.patterns.length})
                        </h4>
                        <div className="space-y-1">
                          {rule.patterns.map((pattern, pIndex) => (
                            <div key={pIndex} className="bg-white px-3 py-2 rounded border border-gray-200 flex items-center justify-between">
                              <code className="text-sm text-gray-700">{pattern}</code>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setActiveTab('chat');
                                  handleSuggestionClick(pattern);
                                }}
                                className="ml-2 px-3 py-1 text-xs bg-blue-50 hover:bg-blue-100 text-blue-600 rounded transition-colors"
                              >
                                Essayer
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* SQL Template */}
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
                          <Code className="w-4 h-4 mr-2" />
                          Template SQL
                        </h4>
                        <div className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
                          <pre className="text-xs font-mono whitespace-pre-wrap">
                            {rule.sql_template}
                          </pre>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </>
    );
  }
};

export default ChatBot;
