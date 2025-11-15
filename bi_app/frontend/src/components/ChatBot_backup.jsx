import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, RefreshCw, Lightbulb, Loader2, BarChart3, Settings, MessageSquare, BookOpen, Search, Filter, Code } from 'lucide-react';
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
  const messagesEndRef = useRef(null);

  useEffect(() => {
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
      const botMessage = {
        type: 'bot',
        content: response.data.answer,
        data: response.data.data,
        visualization: response.data.visualization,
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

  const clearChat = () => {
    setMessages([{
      type: 'bot',
      content: 'Conversation réinitialisée. Comment puis-je vous aider ?',
      timestamp: new Date()
    }]);
  };

  const renderVisualization = (data, vizConfig) => {
    if (!data || !vizConfig) return null;

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
      case 'line':
        return (
          <div className="mt-3 p-4 bg-gray-50 rounded-lg border">
            <div className="flex items-center text-sm text-gray-600">
              <BarChart3 className="w-4 h-4 mr-2" />
              Graphique {vizConfig.type === 'bar' ? 'en barres' : 'linéaire'}: {vizConfig.x_axis} vs {vizConfig.y_axis}
            </div>
            <div className="text-xs text-gray-500 mt-2">
              ({data.length} points de données)
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4 flex items-center justify-between">
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

      {/* Suggestions */}
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
    </div>
  );
};

export default ChatBot;
