import api from './api';

/**
 * RH (Ressources Humaines) API endpoints
 * Manages agent productivity and HR metrics
 */
export const rhAPI = {
  /**
   * Get all agents with productivity metrics and summary
   * @returns {Promise} - List of agents with metrics + summary stats
   */
  getAgentsProductivite: () => api.get('/rh/agents_productivite/'),

  /**
   * Get top performing agents by specific metric
   * @param {number} limit - Number of top agents to return (default: 10)
   * @param {string} metric - Metric to rank by: 'montant_recouvre', 'taux_recouvrement', 'nombre_collectes', 'taux_cloture'
   * @returns {Promise} - Top agents by selected metric
   */
  getTopAgents: (limit = 10, metric = 'montant_recouvre') => 
    api.get('/rh/top_agents/', { params: { limit, metric } }),

  /**
   * Get performance analysis grouped by agent type
   * @returns {Promise} - Performance metrics by agent type
   */
  getPerformanceByType: () => api.get('/rh/performance_by_type/'),

  /**
   * Get detailed collectes analysis
   * @returns {Promise} - Distribution and efficiency metrics
   */
  getCollectesAnalysis: () => api.get('/rh/collectes_analysis/'),

  /**
   * Get detailed information for a specific agent
   * @param {number} agentId - ID of the agent
   * @returns {Promise} - Detailed agent productivity info
   */
  getAgentDetails: (agentId) => api.get('/rh/agent_details/', { params: { agent_id: agentId } }),

  /**
   * Get efficiency metrics across all agents
   * @returns {Promise} - Global efficiency metrics and performance levels
   */
  getEfficiencyMetrics: () => api.get('/rh/efficiency_metrics/'),
};

export default rhAPI;
