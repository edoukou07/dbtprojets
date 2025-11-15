import React, { useState, useEffect } from 'react';
import { BookOpen, Search, Filter, Code, MessageSquare } from 'lucide-react';
import axios from 'axios';

const RulesViewer = () => {
  const [rules, setRules] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [expandedRules, setExpandedRules] = useState(new Set());

  useEffect(() => {
    fetchRules();
  }, [selectedCategory]);

  const fetchRules = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const url = selectedCategory === 'all' 
        ? 'http://127.0.0.1:8000/api/ai/rules/'
        : `http://127.0.0.1:8000/api/ai/rules/?category=${selectedCategory}`;
      
      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setRules(response.data.rules || []);
      setCategories(response.data.categories || []);
    } catch (error) {
      console.error('Erreur chargement règles:', error);
    } finally {
      setLoading(false);
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

  const filteredRules = rules.filter(rule => {
    if (!searchQuery) return true;
    const search = searchQuery.toLowerCase();
    return (
      rule.description.toLowerCase().includes(search) ||
      rule.patterns.some(p => p.toLowerCase().includes(search)) ||
      rule.category.toLowerCase().includes(search)
    );
  });

  const getCategoryColor = (category) => {
    const colors = {
      financier: 'bg-green-100 text-green-800 border-green-300',
      occupation: 'bg-blue-100 text-blue-800 border-blue-300',
      clients: 'bg-purple-100 text-purple-800 border-purple-300',
      operationnel: 'bg-orange-100 text-orange-800 border-orange-300'
    };
    return colors[category] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getCategoryIcon = (category) => {
    const icons = {
      financier: '💰',
      occupation: '🏭',
      clients: '👥',
      operationnel: '📊'
    };
    return icons[category] || '📋';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <BookOpen className="w-8 h-8 text-indigo-600" />
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Règles du Chatbot</h2>
              <p className="text-sm text-gray-500">
                {filteredRules.length} règle(s) chargée(s)
              </p>
            </div>
          </div>
        </div>

        {/* Filtres */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Recherche */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher une règle..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          {/* Filtre par catégorie */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent appearance-none bg-white"
            >
              <option value="all">Toutes les catégories</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>
                  {getCategoryIcon(cat)} {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Liste des règles */}
      {loading ? (
        <div className="bg-white rounded-lg shadow-sm p-8 text-center">
          <div className="animate-spin w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-500">Chargement des règles...</p>
        </div>
      ) : filteredRules.length === 0 ? (
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
                        <div key={pIndex} className="bg-white px-3 py-2 rounded border border-gray-200">
                          <code className="text-sm text-gray-700">{pattern}</code>
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
  );
};

export default RulesViewer;
