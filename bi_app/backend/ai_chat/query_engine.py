"""
Moteur de requêtes intelligent pour le chatbot BI
Supporte deux modes:
1. Mode RULE-BASED (gratuit) : Templates SQL prédéfinis avec règles métier
2. Mode AI (OpenAI) : Text-to-SQL avec GPT-4

Base de données: sigeti_node_db
Schémas datamarts:
- dwh_marts_financier.mart_performance_financiere
- dwh_marts_occupation.mart_occupation_zones
- dwh_marts_clients.mart_portefeuille_clients
- dwh_marts_operationnel.mart_kpi_operationnels

Règles métier intégrées:
- Seuils d'alerte (impayés > 30%, occupation < 50%)
- Validations temporelles (années valides, périodes cohérentes)
- Agrégations intelligentes (TOP N, filtres dynamiques)
- Détection d'anomalies (valeurs nulles, données manquantes)
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TextNormalizer:
    """Normalise le texte pour améliorer la compréhension du langage naturel"""
    
    # Dictionnaire de synonymes et abréviations
    SYNONYMS = {
        # Chiffre d'affaires
        'ca': 'chiffre d\'affaires',
        'chiffre affaires': 'chiffre d\'affaires',
        'revenus': 'chiffre d\'affaires',
        'ventes': 'chiffre d\'affaires',
        'recettes': 'chiffre d\'affaires',
        
        # Paiements
        'impayé': 'non payé',
        'impayés': 'non payé',
        'en retard': 'non payé',
        'dette': 'non payé',
        'dettes': 'non payé',
        
        'payé': 'paye',
        'payés': 'paye',
        'encaissé': 'paye',
        'recouvré': 'paye',
        
        # Occupation
        'taux occupation': 'occupation',
        'taux d\'occupation': 'occupation',
        'remplissage': 'occupation',
        'utilisation': 'occupation',
        
        # Zones
        'zone': 'zones',
        'secteur': 'zones',
        'secteurs': 'zones',
        'site': 'zones',
        'sites': 'zones',
        
        # Clients
        'client': 'clients',
        'entreprise': 'clients',
        'entreprises': 'clients',
        'société': 'clients',
        'sociétés': 'clients',
        
        # Temporel
        'mois en cours': 'ce mois',
        'ce mois ci': 'ce mois',
        'mois actuel': 'ce mois',
        'année en cours': 'cette année',
        'année actuelle': 'cette année',
        'trimestre en cours': 'ce trimestre',
        'trimestre actuel': 'ce trimestre',
        
        # Comparaisons
        'meilleur': 'top',
        'meilleurs': 'top',
        'premier': 'top',
        'premiers': 'top',
        'principal': 'top',
        'principaux': 'top',
        
        'pire': 'worst',
        'pires': 'worst',
        'dernier': 'worst',
        'derniers': 'worst',
        'moins bon': 'worst',
        
        # Actions
        'montre': 'affiche',
        'montre moi': 'affiche',
        'donne': 'affiche',
        'donne moi': 'affiche',
        'liste': 'affiche',
        'afficher': 'affiche',
    }
    
    # Mots de comparaison
    COMPARISON_WORDS = {
        'supérieur': '>',
        'superieur': '>',
        'plus grand': '>',
        'au dessus': '>',
        'au-dessus': '>',
        'dépassant': '>',
        
        'inférieur': '<',
        'inferieur': '<',
        'plus petit': '<',
        'en dessous': '<',
        'en-dessous': '<',
        'moins de': '<',
        'sous': '<',
        
        'égal': '=',
        'egal': '=',
    }
    
    @classmethod
    def normalize(cls, text: str) -> str:
        """Normalise un texte en appliquant synonymes et transformations"""
        text = text.lower().strip()
        
        # Remplacer les synonymes
        for synonym, standard in cls.SYNONYMS.items():
            text = re.sub(r'\b' + re.escape(synonym) + r'\b', standard, text)
        
        # Gérer les négations
        text = cls._handle_negations(text)
        
        # Normaliser les comparaisons
        for comp_word, comp_symbol in cls.COMPARISON_WORDS.items():
            text = text.replace(comp_word, comp_symbol)
        
        return text
    
    @classmethod
    def _handle_negations(cls, text: str) -> str:
        """Transforme les négations en filtres positifs"""
        negation_patterns = [
            (r'ne\s+(\w+)\s+pas', r'non_\1'),
            (r'n\'(\w+)\s+pas', r'non_\1'),
            (r'pas\s+de\s+(\w+)', r'non_\1'),
            (r'sans\s+(\w+)', r'non_\1'),
            (r'qui ne (dépassent|dépasse)', 'inférieur'),
        ]
        
        for pattern, replacement in negation_patterns:
            text = re.sub(pattern, replacement, text)
        
        return text
    
    @classmethod
    def extract_comparison(cls, text: str) -> Optional[Tuple[str, float]]:
        """Extrait les comparaisons numériques du texte"""
        # Patterns: "supérieur à 50", "> 1000", "plus de 30%"
        patterns = [
            r'(>|<|=|>=|<=)\s*(\d+\.?\d*)',
            r'(supérieur|inférieur|égal)\s+à?\s*(\d+\.?\d*)',
            r'(plus|moins)\s+de\s+(\d+\.?\d*)',
            r'dépassant\s+(\d+\.?\d*)',
            r'sous\s+(\d+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                operator = match.group(1) if len(match.groups()) > 1 else '>'
                value = float(match.group(2) if len(match.groups()) > 1 else match.group(1))
                
                # Normaliser l'opérateur
                operator_map = {
                    'supérieur': '>',
                    'superieur': '>',
                    'plus': '>',
                    'dépassant': '>',
                    'inférieur': '<',
                    'inferieur': '<',
                    'moins': '<',
                    'sous': '<',
                    'égal': '=',
                    'egal': '=',
                }
                
                operator = operator_map.get(operator, operator)
                return (operator, value)
        
        return None


class QueryPattern:
    """Définit un pattern de question avec son template SQL"""
    
    def __init__(self, patterns: List[str], sql_template: str, description: str, 
                 params_extractor=None, category: str = "general"):
        self.patterns = [p.lower() for p in patterns]
        self.sql_template = sql_template
        self.description = description
        self.params_extractor = params_extractor
        self.category = category
    
    def matches(self, question: str) -> bool:
        """Vérifie si la question correspond à ce pattern"""
        question_lower = question.lower()
        return any(pattern in question_lower for pattern in self.patterns)
    
    def extract_params(self, question: str) -> Dict:
        """Extrait les paramètres de la question"""
        if self.params_extractor:
            return self.params_extractor(question)
        return {}


class RuleBasedQueryEngine:
    """Moteur de requêtes basé sur des règles (gratuit)"""
    
    def __init__(self):
        self.patterns = self._init_patterns()
        self.normalizer = TextNormalizer()
    
    def _init_patterns(self) -> List[QueryPattern]:
        """Initialise les patterns de questions supportées"""
        
        patterns = [
            # === FINANCIER ===
            QueryPattern(
                patterns=[
                    "ca total", "chiffre d'affaires total", "chiffre affaires total",
                    "revenus total", "ventes total", "recettes total",
                    "affiche ca", "montre ca", "donne ca", "quel est le ca"
                ],
                sql_template="""
                    SELECT SUM(montant_total_facture) as ca_total, 
                           SUM(montant_paye) as ca_paye, 
                           SUM(montant_impaye) as ca_impaye,
                           AVG(taux_paiement_pct) as taux_paiement
                    FROM dwh_marts_financier.mart_performance_financiere
                    WHERE annee = {annee}
                """,
                description="Chiffre d'affaires total de l'année",
                params_extractor=self._extract_year,
                category="financier"
            ),
            
            QueryPattern(
                patterns=[
                    "ca par mois", "évolution mensuelle", "ca mensuel",
                    "chiffre affaires mensuel", "revenus par mois",
                    "ventes mensuelles", "ca mois par mois"
                ],
                sql_template="""
                    SELECT mois, 
                           SUM(montant_total_facture) as ca_facture, 
                           SUM(montant_paye) as ca_paye, 
                           SUM(montant_impaye) as ca_impaye, 
                           AVG(taux_paiement_pct) as taux_paiement
                    FROM dwh_marts_financier.mart_performance_financiere
                    WHERE annee = {annee}
                    GROUP BY mois
                    ORDER BY mois
                """,
                description="Évolution mensuelle du CA",
                params_extractor=self._extract_year,
                category="financier"
            ),
            
            QueryPattern(
                patterns=["taux de recouvrement", "recouvrement", "taux paiement"],
                sql_template="""
                    SELECT AVG(taux_paiement_pct) as taux_paiement_moyen,
                           AVG(taux_recouvrement_moyen) as taux_recouvrement_moyen,
                           SUM(montant_paye) as total_paye,
                           SUM(montant_impaye) as total_impaye
                    FROM dwh_marts_financier.mart_performance_financiere
                    WHERE annee = {annee}
                """,
                description="Taux de recouvrement global",
                params_extractor=self._extract_year,
                category="financier"
            ),
            
            QueryPattern(
                patterns=["créances", "impayés", "factures impayées"],
                sql_template="""
                    SELECT raison_sociale, nom_zone,
                           SUM(montant_impaye) as total_impaye,
                           SUM(nombre_factures) as nb_factures
                    FROM dwh_marts_financier.mart_performance_financiere
                    WHERE montant_impaye > 0 AND annee = {annee}
                    GROUP BY raison_sociale, nom_zone
                    ORDER BY total_impaye DESC
                    LIMIT 20
                """,
                description="Top 20 clients avec créances impayées",
                params_extractor=self._extract_year,
                category="financier"
            ),
            
            QueryPattern(
                patterns=["performance par zone", "ca par zone"],
                sql_template="""
                    SELECT nom_zone,
                           SUM(montant_total_facture) as ca_total,
                           SUM(montant_paye) as ca_paye,
                           AVG(taux_paiement_pct) as taux_paiement
                    FROM dwh_marts_financier.mart_performance_financiere
                    WHERE annee = {annee}
                    GROUP BY nom_zone
                    ORDER BY ca_total DESC NULLS LAST
                """,
                description="Performance financière par zone",
                params_extractor=self._extract_year,
                category="financier"
            ),
            
            # === OCCUPATION ===
            QueryPattern(
                patterns=[
                    "taux d'occupation", "occupation zones", "taux occupation",
                    "remplissage zones", "utilisation zones", "affiche occupation",
                    "montre occupation", "occupation des zones"
                ],
                sql_template="""
                    SELECT nom_zone, 
                           nombre_total_lots,
                           lots_disponibles,
                           lots_attribues,
                           taux_occupation_pct,
                           taux_viabilisation_pct
                    FROM dwh_marts_occupation.mart_occupation_zones
                    ORDER BY taux_occupation_pct DESC NULLS LAST
                """,
                description="Taux d'occupation par zone",
                category="occupation"
            ),
            
            QueryPattern(
                patterns=[
                    "lots disponibles", "parcelles disponibles", "disponibilité",
                    "lots libres", "parcelles libres", "places disponibles",
                    "combien de lots disponibles"
                ],
                sql_template="""
                    SELECT nom_zone, 
                           lots_disponibles,
                           superficie_disponible,
                           valeur_lots_disponibles,
                           taux_occupation_pct
                    FROM dwh_marts_occupation.mart_occupation_zones
                    WHERE lots_disponibles > 0
                    ORDER BY lots_disponibles DESC NULLS LAST
                """,
                description="Zones avec lots disponibles",
                category="occupation"
            ),
            
            QueryPattern(
                patterns=["demandes attribution", "demandes en cours"],
                sql_template="""
                    SELECT nom_zone,
                           nombre_demandes_attribution,
                           demandes_approuvees,
                           demandes_rejetees,
                           demandes_en_attente,
                           taux_approbation_pct,
                           delai_moyen_traitement
                    FROM dwh_marts_occupation.mart_occupation_zones
                    WHERE nombre_demandes_attribution > 0
                    ORDER BY demandes_en_attente DESC
                """,
                description="État des demandes d'attribution",
                category="occupation"
            ),
            
            # === CLIENTS / ENTREPRISES ===
            QueryPattern(
                patterns=["nombre entreprises", "combien d'entreprises", "total clients"],
                sql_template="""
                    SELECT COUNT(*) as nombre_entreprises,
                           COUNT(CASE WHEN nombre_lots_attribues > 0 THEN 1 END) as avec_lots,
                           SUM(chiffre_affaires_total) as ca_total
                    FROM dwh_marts_clients.mart_portefeuille_clients
                """,
                description="Nombre total d'entreprises clientes",
                category="clients"
            ),
            
            QueryPattern(
                patterns=["top clients", "meilleurs clients", "top 10 clients"],
                sql_template="""
                    SELECT raison_sociale,
                           secteur_activite,
                           chiffre_affaires_total,
                           nombre_lots_attribues,
                           taux_paiement_pct,
                           segment_client
                    FROM dwh_marts_clients.mart_portefeuille_clients
                    WHERE chiffre_affaires_total IS NOT NULL
                    ORDER BY chiffre_affaires_total DESC NULLS LAST
                    LIMIT 10
                """,
                description="Top 10 clients par CA",
                category="clients"
            ),
            
            QueryPattern(
                patterns=["clients par secteur", "répartition secteurs"],
                sql_template="""
                    SELECT secteur_activite,
                           COUNT(*) as nombre_clients,
                           SUM(chiffre_affaires_total) as ca_total,
                           AVG(taux_paiement_pct) as taux_paiement_moyen
                    FROM dwh_marts_clients.mart_portefeuille_clients
                    GROUP BY secteur_activite
                    ORDER BY ca_total DESC NULLS LAST
                """,
                description="Répartition des clients par secteur",
                category="clients"
            ),
            
            QueryPattern(
                patterns=["clients à risque", "mauvais payeurs"],
                sql_template="""
                    SELECT raison_sociale,
                           secteur_activite,
                           nombre_factures_retard,
                           ca_impaye,
                           taux_paiement_pct,
                           niveau_risque
                    FROM dwh_marts_clients.mart_portefeuille_clients
                    WHERE niveau_risque IN ('Élevé', 'Critique') OR taux_paiement_pct < 70
                    ORDER BY ca_impaye DESC
                    LIMIT 20
                """,
                description="Clients à risque",
                category="clients"
            ),
            
            # === OPÉRATIONNEL / KPI ===
            QueryPattern(
                patterns=["kpi", "indicateurs", "kpi opérationnels"],
                sql_template="""
                    SELECT annee,
                           nombre_collectes,
                           taux_recouvrement_global_pct,
                           nombre_demandes,
                           taux_approbation_pct,
                           delai_moyen_attribution_jours,
                           nombre_factures_emises,
                           delai_moyen_paiement_jours
                    FROM dwh_marts_operationnel.mart_kpi_operationnels
                    WHERE annee = {annee}
                    ORDER BY trimestre
                """,
                description="KPI opérationnels de l'année",
                params_extractor=self._extract_year,
                category="operationnel"
            ),
            
            QueryPattern(
                patterns=["collectes", "état collectes"],
                sql_template="""
                    SELECT annee, nom_mois,
                           nombre_collectes,
                           collectes_cloturees,
                           collectes_ouvertes,
                           taux_cloture_pct,
                           montant_total_recouvre,
                           taux_recouvrement_moyen
                    FROM dwh_marts_operationnel.mart_kpi_operationnels
                    WHERE annee = {annee}
                    ORDER BY annee, nom_mois
                """,
                description="État des collectes",
                params_extractor=self._extract_year,
                category="operationnel"
            ),
            
            # === GÉNÉRAL / DASHBOARD ===
            QueryPattern(
                patterns=["résumé", "dashboard", "vue d'ensemble", "synthèse"],
                sql_template="""
                    SELECT 
                        (SELECT COUNT(*) FROM dwh_marts_clients.mart_portefeuille_clients) as nb_clients,
                        (SELECT SUM(montant_total_facture) FROM dwh_marts_financier.mart_performance_financiere WHERE annee = {annee}) as ca_total,
                        (SELECT AVG(taux_occupation_pct) FROM dwh_marts_occupation.mart_occupation_zones) as taux_occupation_moyen,
                        (SELECT SUM(lots_disponibles) FROM dwh_marts_occupation.mart_occupation_zones) as lots_disponibles
                """,
                description="Résumé général du système",
                params_extractor=self._extract_year,
                category="general"
            ),
            
            # === PATTERNS AVEC COMPARAISONS ===
            QueryPattern(
                patterns=["zones avec occupation >", "zones occupation supérieur", "zones dépassant"],
                sql_template="""
                    SELECT nom_zone, 
                           taux_occupation_pct,
                           lots_attribues,
                           lots_disponibles,
                           nombre_total_lots
                    FROM dwh_marts_occupation.mart_occupation_zones
                    WHERE taux_occupation_pct > {seuil}
                    ORDER BY taux_occupation_pct DESC
                """,
                description="Zones avec taux d'occupation élevé",
                params_extractor=self._extract_threshold,
                category="occupation"
            ),
            
            QueryPattern(
                patterns=["zones avec occupation <", "zones occupation inférieur", "zones sous", "zones faible occupation"],
                sql_template="""
                    SELECT nom_zone, 
                           taux_occupation_pct,
                           lots_attribues,
                           lots_disponibles,
                           superficie_disponible
                    FROM dwh_marts_occupation.mart_occupation_zones
                    WHERE taux_occupation_pct < {seuil}
                    ORDER BY taux_occupation_pct ASC
                """,
                description="Zones avec faible taux d'occupation",
                params_extractor=self._extract_threshold,
                category="occupation"
            ),
            
            # === TOP / WORST PATTERNS ===
            QueryPattern(
                patterns=["top zones", "meilleures zones", "zones les plus occupées"],
                sql_template="""
                    SELECT nom_zone, 
                           taux_occupation_pct,
                           lots_attribues,
                           nombre_total_lots
                    FROM dwh_marts_occupation.mart_occupation_zones
                    ORDER BY taux_occupation_pct DESC NULLS LAST
                    LIMIT {limit}
                """,
                description="Top zones par occupation",
                params_extractor=self._extract_top_limit,
                category="occupation"
            ),
            
            QueryPattern(
                patterns=["pires zones", "zones les moins occupées", "worst zones"],
                sql_template="""
                    SELECT nom_zone, 
                           taux_occupation_pct,
                           lots_disponibles,
                           nombre_total_lots
                    FROM dwh_marts_occupation.mart_occupation_zones
                    ORDER BY taux_occupation_pct ASC
                    LIMIT {limit}
                """,
                description="Zones avec plus faible occupation",
                params_extractor=self._extract_top_limit,
                category="occupation"
            ),
        ]
        
        return patterns
    
    def _extract_year(self, question: str) -> Dict:
        """Extrait l'année de la question"""
        # Cherche une année (2020-2099)
        year_match = re.search(r'20\d{2}', question)
        if year_match:
            return {"annee": int(year_match.group())}
        return {"annee": datetime.now().year}
    
    def _extract_threshold(self, question: str) -> Dict:
        """Extrait un seuil de comparaison"""
        comparison = self.normalizer.extract_comparison(question)
        if comparison:
            operator, value = comparison
            return {"seuil": value}
        # Valeur par défaut
        return {"seuil": 50}
    
    def _extract_top_limit(self, question: str) -> Dict:
        """Extrait la limite pour les TOP queries"""
        # Cherche "top X", "X meilleurs", etc.
        limit_match = re.search(r'\b(\d+)\s*(meilleurs|premiers|top|pires|derniers)', question.lower())
        if not limit_match:
            limit_match = re.search(r'\b(top|meilleurs|premiers)\s*(\d+)', question.lower())
        
        if limit_match:
            # Le nombre peut être dans le groupe 1 ou 2
            for group in limit_match.groups():
                if group and group.isdigit():
                    return {"limit": int(group)}
        
        return {"limit": 10}  # Valeur par défaut
    
    def find_matching_pattern(self, question: str) -> Optional[QueryPattern]:
        """Trouve le pattern correspondant à la question (avec normalisation)"""
        # Normaliser la question avant de chercher
        normalized_question = self.normalizer.normalize(question)
        logger.info(f"Question normalisée: '{question}' → '{normalized_question}'")
        
        for pattern in self.patterns:
            if pattern.matches(normalized_question):
                logger.info(f"Pattern trouvé: {pattern.description}")
                return pattern
        return None
    
    def generate_sql(self, question: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Génère la requête SQL pour la question
        Returns: (sql, description, category) ou (None, None, None)
        """
        pattern = self.find_matching_pattern(question)
        if not pattern:
            return None, None, None
        
        params = pattern.extract_params(question)
        sql = pattern.sql_template.format(**params)
        
        return sql.strip(), pattern.description, pattern.category
    
    def get_suggestions(self) -> List[str]:
        """Retourne des exemples de questions suggérées"""
        suggestions = []
        categories_seen = set()
        
        for pattern in self.patterns:
            if pattern.category not in categories_seen:
                # Prendre la première question de chaque catégorie
                suggestions.append(pattern.patterns[0])
                categories_seen.add(pattern.category)
                
                if len(suggestions) >= 8:  # Limite à 8 suggestions
                    break
        
        return suggestions


class OpenAIQueryEngine:
    """Moteur de requêtes basé sur OpenAI GPT-4 (optionnel)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.enabled = api_key is not None
        
        if self.enabled:
            try:
                import openai
                self.client = openai.OpenAI(api_key=api_key)
                logger.info("OpenAI Query Engine initialisé")
            except ImportError:
                logger.warning("Module openai non installé. Mode AI désactivé.")
                self.enabled = False
            except Exception as e:
                logger.error(f"Erreur initialisation OpenAI: {e}")
                self.enabled = False
    
    def get_database_schema(self) -> str:
        """Retourne le schéma de la base de données pour le prompt"""
        return """
        Base de données: sigeti_node_db (PostgreSQL)
        
        SCHÉMA dwh_marts_financier.mart_performance_financiere:
        - annee, mois, trimestre
        - raison_sociale, domaine_activite_id, nom_zone
        - nombre_factures, montant_total_facture, montant_paye, montant_impaye
        - delai_moyen_paiement, taux_paiement_pct
        - nombre_collectes, montant_total_a_recouvrer, montant_total_recouvre, taux_recouvrement_moyen
        
        SCHÉMA dwh_marts_occupation.mart_occupation_zones:
        - zone_id, nom_zone
        - nombre_total_lots, lots_disponibles, lots_attribues, lots_reserves
        - superficie_totale, superficie_disponible, superficie_attribuee
        - taux_occupation_pct, taux_viabilisation_pct
        - nombre_demandes_attribution, demandes_approuvees, demandes_rejetees, demandes_en_attente
        - delai_moyen_traitement, taux_approbation_pct
        - valeur_totale_lots, valeur_lots_disponibles
        
        SCHÉMA dwh_marts_clients.mart_portefeuille_clients:
        - entreprise_id, raison_sociale, forme_juridique, registre_commerce
        - telephone, email, secteur_activite
        - nombre_factures, chiffre_affaires_total, ca_paye, ca_impaye
        - delai_moyen_paiement, nombre_factures_retard, taux_paiement_pct
        - nombre_demandes, demandes_approuvees
        - superficie_totale_attribuee, nombre_lots_attribues
        - segment_client, niveau_risque
        
        SCHÉMA dwh_marts_operationnel.mart_kpi_operationnels:
        - annee, trimestre, nom_mois
        - nombre_collectes, collectes_cloturees, collectes_ouvertes, taux_cloture_pct
        - taux_recouvrement_moyen, duree_moyenne_collecte_jours, taux_recouvrement_global_pct
        - nombre_demandes, demandes_approuvees, demandes_rejetees, demandes_en_attente
        - delai_moyen_attribution_jours, taux_approbation_pct
        - nombre_factures_emises, factures_payees, delai_moyen_paiement_jours
        - montant_total_a_recouvrer, montant_total_recouvre
        - montant_total_facture, montant_paye
        """
    
    def generate_sql(self, question: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Génère la requête SQL avec OpenAI
        Returns: (sql, description) ou (None, None)
        """
        if not self.enabled:
            return None, None
        
        try:
            prompt = f"""Tu es un expert SQL pour PostgreSQL. 
Génère une requête SQL pour répondre à la question suivante.
Utilise UNIQUEMENT les tables et colonnes du schéma ci-dessous.
Limite les résultats à 100 lignes maximum avec LIMIT.

{self.get_database_schema()}

Question: {question}

Réponds UNIQUEMENT avec du SQL valide, sans explication."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Modèle plus récent et économique
                messages=[
                    {"role": "system", "content": "Tu es un expert SQL. Réponds uniquement avec du code SQL, sans markdown ni explication."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=500
            )
            
            sql = response.choices[0].message.content.strip()
            # Nettoyer les marqueurs markdown si présents
            sql = sql.replace("```sql", "").replace("```", "").strip()
            
            return sql, f"Requête générée par IA: {question}"
            
        except Exception as e:
            logger.error(f"Erreur génération SQL OpenAI: {e}")
            return None, None


class HybridQueryEngine:
    """Moteur hybride: essaie les règles d'abord, puis OpenAI si disponible"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.rule_engine = RuleBasedQueryEngine()
        self.ai_engine = OpenAIQueryEngine(openai_api_key)
    
    def generate_sql(self, question: str, prefer_ai: bool = False) -> Tuple[Optional[str], Optional[str], Optional[str], str]:
        """
        Génère SQL avec le moteur approprié
        Returns: (sql, description, category, engine_used)
        engine_used: "rule-based" ou "ai"
        """
        # Si préférence AI et disponible, essayer d'abord l'IA
        if prefer_ai and self.ai_engine.enabled:
            sql, desc = self.ai_engine.generate_sql(question)
            if sql:
                return sql, desc, None, "ai"  # AI n'a pas de catégorie
        
        # Essayer les règles
        sql, desc, category = self.rule_engine.generate_sql(question)
        if sql:
            return sql, desc, category, "rule-based"
        
        # Fallback sur AI si pas de règle trouvée
        if self.ai_engine.enabled:
            sql, desc = self.ai_engine.generate_sql(question)
            if sql:
                return sql, desc, None, "ai"
        
        return None, None, None, "none"
    
    def get_capabilities(self) -> Dict:
        """Retourne les capacités du moteur"""
        return {
            "rule_based": {
                "enabled": True,
                "patterns_count": len(self.rule_engine.patterns)
            },
            "ai": {
                "enabled": self.ai_engine.enabled
            }
        }
