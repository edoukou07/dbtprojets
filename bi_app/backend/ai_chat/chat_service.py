"""
Service de chat IA pour exécuter les requêtes et formater les réponses
Intègre les règles métier pour analyse intelligente et recommandations
"""

from django.db import connection
from typing import Dict, List, Optional
import logging
from decimal import Decimal
from datetime import datetime, date
from .business_rules import BusinessRules

logger = logging.getLogger(__name__)


class ChatService:
    """Service principal pour le chatbot"""
    
    def __init__(self, query_engine):
        self.query_engine = query_engine
        self.conversation_context = []  # Historique pour suggestions contextuelles
        self.business_rules = BusinessRules()  # Règles métier
    
    def execute_query(self, sql: str, max_rows: int = 100) -> Dict:
        """
        Exécute une requête SQL en lecture seule
        
        Returns:
            {
                'success': bool,
                'data': List[Dict],
                'columns': List[str],
                'row_count': int,
                'error': str (optionnel)
            }
        """
        result = {
            'success': False,
            'data': [],
            'columns': [],
            'row_count': 0
        }
        
        try:
            # Validation: uniquement SELECT
            if not sql.strip().upper().startswith('SELECT'):
                result['error'] = "Seules les requêtes SELECT sont autorisées"
                return result
            
            # Ajouter LIMIT si pas présent
            if 'LIMIT' not in sql.upper():
                sql += f" LIMIT {max_rows}"
            
            with connection.cursor() as cursor:
                cursor.execute(sql)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                
                # Convertir en liste de dicts
                data = []
                for row in rows:
                    row_dict = {}
                    for i, value in enumerate(row):
                        # Conversion des types Python
                        if isinstance(value, Decimal):
                            row_dict[columns[i]] = float(value)
                        elif isinstance(value, (datetime, date)):
                            row_dict[columns[i]] = value.isoformat()
                        else:
                            row_dict[columns[i]] = value
                    data.append(row_dict)
                
                result['success'] = True
                result['data'] = data
                result['columns'] = columns
                result['row_count'] = len(data)
                
        except Exception as e:
            logger.error(f"Erreur exécution SQL: {e}")
            error_msg = str(e)
            
            # Messages d'erreur conviviaux
            if 'does not exist' in error_msg.lower():
                if 'column' in error_msg.lower():
                    result['error'] = "📊 Cette information n'est pas disponible dans les données actuelles. Essayez une autre question ou reformulez votre demande."
                elif 'table' in error_msg.lower() or 'relation' in error_msg.lower():
                    result['error'] = "📊 Les données demandées ne sont pas encore disponibles dans le système."
                else:
                    result['error'] = "📊 Information non disponible. Veuillez reformuler votre question."
            elif 'permission denied' in error_msg.lower():
                result['error'] = "🔒 Accès non autorisé à cette ressource."
            elif 'syntax error' in error_msg.lower():
                result['error'] = "❓ Je n'ai pas bien compris votre question. Pouvez-vous la reformuler différemment ?"
            else:
                result['error'] = "⚠️ Une erreur s'est produite. Essayez de reformuler votre question."
        
        return result
    
    def format_response(self, question: str, query_result: Dict, 
                       execution_result: Dict) -> Dict:
        """
        Formate la réponse complète pour le frontend
        
        Args:
            question: Question de l'utilisateur
            query_result: Résultat du query_engine
            execution_result: Résultat de execute_query
        
        Returns:
            {
                'question': str,
                'answer': str (texte),
                'data': List[Dict],
                'visualization': Dict (config pour graphiques),
                'method': 'rules' | 'ai',
                'success': bool
            }
        """
        response = {
            'question': question,
            'answer': '',
            'data': [],
            'visualization': None,
            'method': query_result.get('method'),
            'success': False,
            'sql': query_result.get('sql'),  # Pour debug
            'category': query_result.get('category')
        }
        
        if not execution_result['success']:
            response['answer'] = f"❌ Erreur: {execution_result.get('error', 'Erreur inconnue')}"
            return response
        
        data = execution_result['data']
        row_count = execution_result['row_count']
        
        # Générer la réponse texte
        response['answer'] = self._generate_text_answer(
            question, 
            query_result.get('description'),
            data, 
            row_count,
            query_result.get('category')
        )
        
        response['data'] = data
        response['success'] = True
        
        # Suggérer une visualisation si pertinent
        response['visualization'] = self._suggest_visualization(
            data, 
            execution_result['columns'],
            query_result.get('category')
        )
        
        # Générer des suggestions contextuelles
        response['contextual_suggestions'] = self._generate_contextual_suggestions(
            question,
            query_result.get('category'),
            data,
            row_count
        )
        
        # Appliquer les règles métier pour insights et alertes
        response['business_insights'] = self.business_rules.generate_insights(
            data, 
            query_result.get('category')
        )
        
        # Détecter les anomalies dans les données (contextuel selon catégorie)
        anomalies = self.business_rules.detect_anomalies(data, query_result.get('category'))
        if anomalies:
            response['anomalies'] = anomalies
            critical_anomalies = [a for a in anomalies if a['severity'] == 'error']
            if critical_anomalies:
                logger.warning(f"⚠️ {len(critical_anomalies)} anomalies critiques détectées")
        
        # Mettre à jour le contexte de conversation
        self.conversation_context.append({
            'question': question,
            'category': query_result.get('category'),
            'has_data': row_count > 0
        })
        # Garder seulement les 5 dernières questions
        if len(self.conversation_context) > 5:
            self.conversation_context.pop(0)
        
        return response
    
    def _generate_text_answer(self, question: str, description: str, 
                             data: List[Dict], row_count: int, 
                             category: str) -> str:
        """Génère une réponse textuelle"""
        
        if row_count == 0:
            return "🔍 Aucun résultat trouvé pour cette question."
        
        # Introduction
        answer = f"✅ **{description}**\n\n"
        
        # Résumé selon la catégorie
        if category == 'financier':
            answer += self._summarize_financial(data, row_count)
        elif category == 'occupation':
            answer += self._summarize_occupation(data, row_count)
        elif category == 'clients':
            answer += self._summarize_clients(data, row_count)
        else:
            answer += f"📊 {row_count} résultat(s) trouvé(s).\n"
        
        return answer
    
    def _summarize_financial(self, data: List[Dict], row_count: int) -> str:
        """Résumé pour données financières"""
        logger.info(f"[FINANCIAL] row_count={row_count}, data={data}")
        summary = ""
        
        if row_count == 1:
            row = data[0]
            logger.info(f"[FINANCIAL] Processing row: {row}")
            logger.info(f"[FINANCIAL] Row keys: {list(row.keys())}")
            
            if 'ca_total' in row:
                logger.info(f"[FINANCIAL] Found ca_total: {row.get('ca_total')}")
                summary += f"💰 CA Total: **{self._format_currency(row.get('ca_total'))}**\n"
            if 'ca_paye' in row:
                logger.info(f"[FINANCIAL] Found ca_paye: {row.get('ca_paye')}")
                summary += f"✅ CA Payé: **{self._format_currency(row.get('ca_paye'))}**\n"
            if 'ca_impaye' in row:
                logger.info(f"[FINANCIAL] Found ca_impaye: {row.get('ca_impaye')}")
                summary += f"⚠️ CA Impayé: **{self._format_currency(row.get('ca_impaye'))}**\n"
            if 'taux_moyen' in row:
                summary += f"📈 Taux moyen: **{row.get('taux_moyen', 0):.1f}%**\n"
            if 'taux_paiement' in row:
                summary += f"📈 Taux paiement: **{row.get('taux_paiement', 0):.1f}%**\n"
        else:
            summary += f"📊 {row_count} périodes analysées.\n"
        
        logger.info(f"[FINANCIAL] Generated summary: {summary}")
        return summary
    
    def _summarize_occupation(self, data: List[Dict], row_count: int) -> str:
        """Résumé pour données d'occupation"""
        summary = f"🏭 {row_count} zone(s) trouvée(s).\n\n"
        
        if row_count > 0 and 'taux_occupation' in data[0]:
            avg_occupation = sum(r.get('taux_occupation', 0) for r in data) / row_count
            summary += f"📊 Taux d'occupation moyen: **{avg_occupation:.1f}%**\n"
        
        return summary
    
    def _summarize_clients(self, data: List[Dict], row_count: int) -> str:
        """Résumé pour données clients"""
        return f"👥 {row_count} entreprise(s) trouvée(s).\n"
    
    def _format_currency(self, amount) -> str:
        """Formate un montant en FCFA"""
        if amount is None:
            return "0 FCFA"
        
        amount = float(amount)
        if amount >= 1_000_000:
            return f"{amount/1_000_000:.2f}M FCFA"
        elif amount >= 1_000:
            return f"{amount/1_000:.0f}K FCFA"
        else:
            return f"{amount:.0f} FCFA"
    
    def _format_value(self, value) -> str:
        """Formate une valeur générique"""
        if value is None:
            return "N/A"
        if isinstance(value, (int, float)):
            if value >= 1_000_000:
                return f"{value/1_000_000:.2f}M"
            elif value >= 1_000:
                return f"{value/1_000:.1f}K"
            else:
                return f"{value:.0f}"
        return str(value)
    
    def _generate_contextual_suggestions(self, question: str, category: str, 
                                         data: List[Dict], row_count: int) -> List[Dict]:
        """Génère des suggestions contextuelles basées sur la réponse actuelle"""
        suggestions = []
        
        if row_count == 0:
            # Aucun résultat - suggérer des questions plus générales
            if category == 'financier':
                suggestions.append({
                    'text': 'Quel est le CA total ?',
                    'icon': '💰',
                    'reason': 'Vue d\'ensemble financière'
                })
                suggestions.append({
                    'text': 'Quels sont les impayés ?',
                    'icon': '⚠️',
                    'reason': 'Analyse des créances'
                })
            elif category == 'occupation':
                suggestions.append({
                    'text': 'Quelles sont les zones disponibles ?',
                    'icon': '📍',
                    'reason': 'Disponibilité des zones'
                })
            elif category == 'clients':
                suggestions.append({
                    'text': 'Top 10 clients',
                    'icon': '👥',
                    'reason': 'Principaux clients'
                })
            return suggestions
        
        # Suggestions basées sur la catégorie et les données
        if category == 'financier':
            # Si on a montré le CA total, suggérer détails
            if row_count == 1 and any('ca_total' in str(k).lower() for row in data for k in row.keys()):
                suggestions.append({
                    'text': 'Répartition du CA par zone',
                    'icon': '📊',
                    'reason': 'Détail géographique'
                })
                suggestions.append({
                    'text': 'Evolution du CA sur 6 mois',
                    'icon': '📈',
                    'reason': 'Tendance temporelle'
                })
                suggestions.append({
                    'text': 'Taux de paiement par secteur',
                    'icon': '💳',
                    'reason': 'Analyse sectorielle'
                })
            # Si on a montré une liste de zones/clients
            elif row_count > 1:
                suggestions.append({
                    'text': 'Comparer avec le mois précédent',
                    'icon': '🔄',
                    'reason': 'Evolution temporelle'
                })
                suggestions.append({
                    'text': 'Filtrer montants > 100M',
                    'icon': '🔍',
                    'reason': 'Focus montants importants'
                })
        
        elif category == 'occupation':
            if row_count > 1:
                suggestions.append({
                    'text': 'Zones avec taux > 80%',
                    'icon': '📈',
                    'reason': 'Zones à forte occupation'
                })
                suggestions.append({
                    'text': 'Zones avec lots disponibles',
                    'icon': '🏗️',
                    'reason': 'Opportunités disponibles'
                })
            suggestions.append({
                'text': 'Evolution occupation sur 12 mois',
                'icon': '📊',
                'reason': 'Tendance annuelle'
            })
        
        elif category == 'clients':
            if row_count > 1:
                # On a une liste de clients
                suggestions.append({
                    'text': 'Clients par secteur d\'activité',
                    'icon': '🏢',
                    'reason': 'Segmentation sectorielle'
                })
                suggestions.append({
                    'text': 'Clients avec CA > 50M',
                    'icon': '💎',
                    'reason': 'Clients premium'
                })
            suggestions.append({
                'text': 'Nouveaux clients ce mois',
                'icon': '🆕',
                'reason': 'Acquisition récente'
            })
        
        # Suggestions cross-catégorie basées sur l'historique
        if len(self.conversation_context) >= 2:
            prev_categories = [ctx.get('category') for ctx in self.conversation_context[-2:]]
            
            # Si on parle de finances, suggérer occupation
            if 'financier' in prev_categories and category == 'financier':
                suggestions.append({
                    'text': 'Occupation des zones',
                    'icon': '🏗️',
                    'reason': 'Vue opérationnelle'
                })
            
            # Si on parle d'occupation, suggérer finances
            elif 'occupation' in prev_categories and category == 'occupation':
                suggestions.append({
                    'text': 'CA par zone',
                    'icon': '💰',
                    'reason': 'Performance financière'
                })
        
        # Limiter à 4 suggestions
        return suggestions[:4]
    
    def _suggest_visualization(self, data: List[Dict], columns: List[str], 
                               category: str) -> Optional[Dict]:
        """Suggère un type de visualisation selon les données"""
        
        if not data or len(data) == 0:
            return None
        
        logger.info(f"[VIZ] Analysing {len(data)} rows with columns: {columns}")
        
        # Détecter les colonnes numériques et textuelles
        # Vérifier plusieurs lignes pour gérer les valeurs null
        numeric_cols = []
        text_cols = []
        date_cols = []
        
        # Analyser toutes les lignes pour détecter le type réel
        column_types = {col: {'numeric': 0, 'text': 0, 'null': 0} for col in columns}
        
        for row in data[:min(len(data), 10)]:  # Analyser jusqu'à 10 lignes
            for col in columns:
                value = row.get(col)
                col_lower = col.lower()
                
                if value is None:
                    column_types[col]['null'] += 1
                elif isinstance(value, (int, float)):
                    column_types[col]['numeric'] += 1
                elif isinstance(value, str):
                    column_types[col]['text'] += 1
        
        # Classifier les colonnes selon le type dominant
        for col in columns:
            col_lower = col.lower()
            stats = column_types[col]
            
            # Détecter colonnes temporelles par le nom
            if any(word in col_lower for word in ['mois', 'date', 'annee', 'trimestre', 'nom_mois', 'year', 'month']):
                date_cols.append(col)
                text_cols.append(col)
            # Si majoritairement numérique (ignorer les null)
            elif stats['numeric'] > 0 and stats['numeric'] >= stats['text']:
                numeric_cols.append(col)
            # Si majoritairement texte
            elif stats['text'] > 0:
                text_cols.append(col)
            # Si que des null mais nom suggère numérique
            elif stats['null'] > 0 and any(word in col_lower for word in ['montant', 'ca', 'total', 'nombre', 'taux', 'pct', 'valeur', 'prix']):
                numeric_cols.append(col)  # On l'ajoute quand même pour éviter "pas de viz"
        
        logger.info(f"[VIZ] numeric_cols: {numeric_cols}, text_cols: {text_cols}, date_cols: {date_cols}")
        
        # Si toutes les valeurs numériques sont null, afficher quand même un tableau
        has_valid_numeric_data = False
        if numeric_cols:
            for col in numeric_cols:
                for row in data[:5]:
                    if row.get(col) is not None:
                        has_valid_numeric_data = True
                        break
                if has_valid_numeric_data:
                    break
        
        # Pas de données numériques valides → Table simple
        if len(numeric_cols) == 0 or not has_valid_numeric_data:
            logger.info("[VIZ] No valid numeric data, showing table")
            return {
                'type': 'table',
                'columns': columns[:6]
            }
        
        # 1 seule ligne → KPI cards
        if len(data) == 1:
            first_row = data[0]
            kpis = []
            for col in numeric_cols[:4]:
                kpis.append({
                    'label': col.replace('_', ' ').title(),
                    'value': self._format_value(first_row.get(col))
                })
            logger.info(f"[VIZ] Single row → KPI with {len(kpis)} cards")
            return {
                'type': 'kpi',
                'kpis': kpis
            }
        
        # Pas de colonne texte → Utiliser l'index ou la première colonne
        if len(text_cols) == 0:
            # Créer une colonne index virtuelle
            logger.info("[VIZ] No text columns, using row index")
            if len(data) <= 15:
                return {
                    'type': 'bar',
                    'x_axis': columns[0],  # Première colonne même si numérique
                    'y_axis': numeric_cols[0],
                    'title': f"Répartition de {numeric_cols[0].replace('_', ' ').title()}"
                }
            else:
                return {
                    'type': 'table',
                    'columns': columns[:6]
                }
        
        # Plusieurs lignes avec colonnes texte et numérique
        if len(data) <= 15:
            # Peu de données → Bar chart
            viz = {
                'type': 'bar',
                'x_axis': text_cols[0],
                'y_axis': numeric_cols[0],
                'title': f"{numeric_cols[0].replace('_', ' ').title()} par {text_cols[0].replace('_', ' ').title()}"
            }
            logger.info(f"[VIZ] ≤15 rows → Bar chart: {viz}")
            return viz
        else:
            # Beaucoup de données
            if len(date_cols) > 0:
                # Si colonne temporelle → Line chart
                viz = {
                    'type': 'line',
                    'x_axis': date_cols[0],
                    'y_axis': numeric_cols[0],
                    'title': f"Évolution de {numeric_cols[0].replace('_', ' ').title()}"
                }
                logger.info(f"[VIZ] >15 rows with date → Line chart: {viz}")
                return viz
            else:
                # Sinon → Bar chart (limité) ou Table
                if len(data) <= 30:
                    viz = {
                        'type': 'bar',
                        'x_axis': text_cols[0],
                        'y_axis': numeric_cols[0],
                        'title': f"{numeric_cols[0].replace('_', ' ').title()} par {text_cols[0].replace('_', ' ').title()}"
                    }
                    logger.info(f"[VIZ] 16-30 rows → Bar chart: {viz}")
                    return viz
                else:
                    viz = {
                        'type': 'table',
                        'columns': columns[:6]
                    }
                    logger.info(f"[VIZ] >30 rows → Table")
                    return viz
        
        return None
    
    def process_chat_message(self, question: str, prefer_ai: bool = False) -> Dict:
        """
        Point d'entrée principal pour traiter un message de chat
        
        Args:
            question: Question de l'utilisateur
            prefer_ai: Préférer l'IA si disponible
        
        Returns:
            Réponse complète formatée
        """
        # 1. Générer la requête SQL
        sql, description, category, engine = self.query_engine.generate_sql(question, prefer_ai)
        
        if not sql:
            return {
                'question': question,
                'answer': 'Désolé, je n\'ai pas compris votre question. Essayez une des suggestions ci-dessous.',
                'success': False,
                'engine': 'none',
                'data': [],
                'visualization': None
            }
        
        # 2. Exécuter la requête
        execution_result = self.execute_query(sql)
        
        # 3. Formater la réponse
        response = self.format_response(
            question, 
            {'sql': sql, 'description': description, 'category': category, 'engine': engine}, 
            execution_result
        )
        
        return response
