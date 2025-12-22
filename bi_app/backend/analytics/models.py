"""
Models for SIGETI BI Analytics
These models map to existing DWH mart views/tables (read-only)
"""
from django.db import models


class MartPerformanceFinanciere(models.Model):
    """Mart Financier - Performance financière et recouvrement"""
    
    annee = models.IntegerField()
    mois = models.IntegerField(null=True, blank=True)
    trimestre = models.IntegerField(null=True, blank=True)
    raison_sociale = models.CharField(max_length=255, null=True, blank=True)
    domaine_activite_id = models.IntegerField(null=True, blank=True)
    nom_zone = models.CharField(max_length=255, null=True, blank=True)
    
    # Métriques de facturation
    nombre_factures = models.IntegerField(null=True, blank=True)
    montant_total_facture = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    montant_paye = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    montant_impaye = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    delai_moyen_paiement = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    taux_paiement_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Métriques de recouvrement
    nombre_collectes = models.IntegerField(null=True, blank=True)
    montant_total_a_recouvrer = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    montant_total_recouvre = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    taux_recouvrement_moyen = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        managed = False  # Django won't create/modify this table
        db_table = '"dwh_marts_financier"."mart_performance_financiere"'
        ordering = ['-annee', '-mois']


class MartOccupationZones(models.Model):
    """Mart Occupation - Taux d'occupation et disponibilité des lots"""
    
    zone_id = models.IntegerField(primary_key=True)
    nom_zone = models.CharField(max_length=255)
    
    # Comptage des lots
    nombre_total_lots = models.IntegerField(null=True, blank=True)
    lots_disponibles = models.IntegerField(null=True, blank=True)
    lots_attribues = models.IntegerField(null=True, blank=True)
    lots_reserves = models.IntegerField(null=True, blank=True)
    
    # Surfaces
    superficie_totale = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    superficie_disponible = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    superficie_attribuee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Taux
    taux_occupation_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    taux_viabilisation_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Valeur
    valeur_totale_lots = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valeur_lots_disponibles = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Viabilité
    lots_viabilises = models.IntegerField(null=True, blank=True)
    
    # Attributions
    nombre_demandes_attribution = models.IntegerField(null=True, blank=True)
    demandes_approuvees = models.IntegerField(null=True, blank=True)
    demandes_rejetees = models.IntegerField(null=True, blank=True)
    demandes_en_attente = models.IntegerField(null=True, blank=True)
    delai_moyen_traitement = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    taux_approbation_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = '"dwh_marts_occupation"."mart_occupation_zones"'


class MartPortefeuilleClients(models.Model):
    """Mart Clients - Portefeuille et segmentation"""
    
    entreprise_id = models.IntegerField(primary_key=True)
    raison_sociale = models.CharField(max_length=255)
    forme_juridique = models.CharField(max_length=100, null=True, blank=True)
    registre_commerce = models.CharField(max_length=100, null=True, blank=True)
    telephone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    secteur_activite = models.CharField(max_length=255, null=True, blank=True)
    
    # Facturation
    nombre_factures = models.IntegerField(null=True, blank=True)
    chiffre_affaires_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    ca_paye = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    ca_impaye = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Comportement
    delai_moyen_paiement = models.DurationField(null=True, blank=True)
    nombre_factures_retard = models.IntegerField(null=True, blank=True)
    taux_paiement_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Attributions
    nombre_demandes = models.IntegerField(null=True, blank=True)
    demandes_approuvees = models.IntegerField(null=True, blank=True)
    superficie_totale_attribuee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    nombre_lots_attribues = models.IntegerField(null=True, blank=True)
    
    # Segmentation
    segment_client = models.CharField(max_length=50, null=True, blank=True)
    niveau_risque = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = '"dwh_marts_clients"."mart_portefeuille_clients"'
        ordering = ['-chiffre_affaires_total']


class MartKPIOperationnels(models.Model):
    """Mart Opérationnel - Indicateurs de performance opérationnelle"""
    
    annee = models.IntegerField()
    trimestre = models.IntegerField(null=True, blank=True)
    nom_mois = models.CharField(max_length=20, null=True, blank=True)
    
    # Performance collectes
    nombre_collectes = models.IntegerField(null=True, blank=True)
    collectes_cloturees = models.IntegerField(null=True, blank=True)
    collectes_ouvertes = models.IntegerField(null=True, blank=True)
    taux_recouvrement_moyen = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    duree_moyenne_collecte_jours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    taux_cloture_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    taux_recouvrement_global_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Performance attributions
    nombre_demandes = models.IntegerField(null=True, blank=True)
    demandes_approuvees = models.IntegerField(null=True, blank=True)
    demandes_rejetees = models.IntegerField(null=True, blank=True)
    demandes_en_attente = models.IntegerField(null=True, blank=True)
    delai_moyen_attribution_jours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    taux_approbation_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Performance facturation
    nombre_factures_emises = models.IntegerField(null=True, blank=True)
    factures_payees = models.IntegerField(null=True, blank=True)
    delai_moyen_paiement_jours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Volumes financiers
    montant_total_a_recouvrer = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    montant_total_recouvre = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    montant_total_facture = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    montant_paye = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = '"dwh_marts_operationnel"."mart_kpi_operationnels"'
        ordering = ['-annee', 'trimestre']
        # Indiquer à Django de ne pas chercher de PK (row_number utilisé en interne)
        # Django va utiliser toutes les colonnes comme identifiant unique
        get_latest_by = ['-annee', '-trimestre']


class Alert(models.Model):
    """Système d'alertes pour les seuils critiques"""
    
    ALERT_TYPES = [
        ('taux_recouvrement', 'Taux de Recouvrement Critique'),
        ('facture_impayee', 'Facture Impayée Ancienne'),
        ('client_inactif', 'Client Inactif'),
        ('occupation_faible', 'Taux d\'Occupation Faible'),
        ('objectif_non_atteint', 'Objectif Non Atteint'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Faible'),
        ('medium', 'Moyen'),
        ('high', 'Élevé'),
        ('critical', 'Critique'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acquittée'),
        ('resolved', 'Résolue'),
        ('dismissed', 'Ignorée'),
    ]
    
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Données contextuelles (JSON)
    context_data = models.JSONField(null=True, blank=True)
    
    # Métadonnées
    threshold_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Utilisateur (optionnel)
    acknowledged_by = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        managed = True
        db_table = 'bi_alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['alert_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_severity_display()} - {self.title}"


class AlertThreshold(models.Model):
    """Configuration des seuils d'alerte"""
    
    alert_type = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    
    # Seuils
    threshold_value = models.DecimalField(max_digits=10, decimal_places=2)
    threshold_operator = models.CharField(
        max_length=10,
        choices=[
            ('<', 'Inférieur à'),
            ('>', 'Supérieur à'),
            ('<=', 'Inférieur ou égal à'),
            ('>=', 'Supérieur ou égal à'),
            ('==', 'Égal à'),
        ],
        default='<'
    )
    
    # Fréquence de vérification (en minutes)
    check_interval = models.IntegerField(default=60)
    
    # Notification
    send_email = models.BooleanField(default=False)
    email_recipients = models.TextField(null=True, blank=True, help_text="Liste d'emails séparés par des virgules")
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_checked = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        managed = True
        db_table = 'bi_alert_thresholds'
        ordering = ['alert_type']
    
    def __str__(self):
        return f"{self.alert_type} {self.threshold_operator} {self.threshold_value}"


class ReportSchedule(models.Model):
    """Schedule for report generation and dispatch by email"""

    DASHBOARD_CHOICES = [
        ('dashboard', 'Tableau de bord'),
        ('financier', 'Performance Financière'),
        ('occupation', 'Occupation Zones'),
        ('clients', 'Portefeuille Clients'),
        ('operationnel', 'KPI Opérationnels'),
        ('alerts', 'Alerts Analytics'),
    ]

    RECURRENCE_TYPE_CHOICES = [
        ('none', 'Aucune (envoi unique)'),
        ('minute', 'Par minute'),
        ('hour', 'Par heure'),
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
        ('yearly', 'Annuel'),
        ('custom', 'Personnalisé'),
    ]

    name = models.CharField(max_length=255)
    dashboard = models.CharField(max_length=50, choices=DASHBOARD_CHOICES, null=True, blank=True)  # Deprecated, kept for backward compatibility
    dashboards = models.JSONField(default=list, help_text="Liste des dashboards à inclure dans le rapport")
    scheduled_at = models.DateTimeField()
    recipients = models.TextField(null=True, blank=True, help_text="Emails séparés par des virgules")
    created_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    pdfs_data = models.JSONField(default=dict, blank=True, help_text="Dictionnaire stockant les chemins des PDFs générés: {dashboard_name: file_path}")

    # Recurrence fields
    is_recurring = models.BooleanField(default=False, help_text="Indique si le rapport est récurrent")
    recurrence_type = models.CharField(max_length=20, choices=RECURRENCE_TYPE_CHOICES, default='none', help_text="Type de récurrence")
    recurrence_interval = models.IntegerField(null=True, blank=True, help_text="Intervalle (ex: toutes les 5 minutes, toutes les 3 heures)")
    recurrence_minute = models.IntegerField(null=True, blank=True, help_text="Minute précise (0-59) pour certaines récurrences")
    recurrence_hour = models.IntegerField(null=True, blank=True, help_text="Heure précise (0-23)")
    recurrence_days_of_week = models.JSONField(default=list, blank=True, help_text="Jours de la semaine [0-6] où 0=lundi pour récurrence hebdomadaire")
    recurrence_day_of_month = models.IntegerField(null=True, blank=True, help_text="Jour du mois (1-31) ou -1 pour dernier jour")
    recurrence_week_of_month = models.IntegerField(null=True, blank=True, help_text="Semaine du mois (1-4) pour 'premier lundi'")
    recurrence_month = models.IntegerField(null=True, blank=True, help_text="Mois (1-12) pour récurrence annuelle")
    recurrence_workdays_only = models.BooleanField(default=False, help_text="Uniquement jours ouvrables")
    recurrence_hour_range_start = models.TimeField(null=True, blank=True, help_text="Début de plage horaire")
    recurrence_hour_range_end = models.TimeField(null=True, blank=True, help_text="Fin de plage horaire")
    recurrence_hour_range_interval = models.IntegerField(null=True, blank=True, help_text="Intervalle dans la plage (en minutes)")
    recurrence_end_date = models.DateTimeField(null=True, blank=True, help_text="Date de fin optionnelle")
    parent_schedule = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='occurrences', help_text="Référence au rapport parent pour les occurrences")
    occurrence_number = models.IntegerField(default=1, help_text="Numéro d'occurrence dans la série")

    class Meta:
        managed = True
        db_table = 'bi_report_schedules'

    def get_dashboards_list(self):
        """Retourne la liste des dashboards, avec fallback sur l'ancien champ dashboard si dashboards est vide"""
        if self.dashboards and len(self.dashboards) > 0:
            return self.dashboards
        elif self.dashboard:
            return [self.dashboard]
        return []

    def __str__(self):
        dashboards_str = ', '.join(self.get_dashboards_list()) if self.get_dashboards_list() else 'Aucun'
        return f"Report {self.name} -> {dashboards_str} @ {self.scheduled_at}"


class UserDashboardPermission(models.Model):
    """Model to manage user access to specific dashboards"""
    
    DASHBOARD_CHOICES = [
        ('dashboard', 'Tableau de bord'),
        ('financier', 'Performance Financière'),
        ('occupation', 'Occupation Zones'),
        ('portefeuille', 'Portefeuille Clients'),
        ('operationnel', 'KPI Opérationnels'),
    ]
    
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='dashboard_permissions')
    dashboard = models.CharField(max_length=50, choices=DASHBOARD_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        managed = True
        db_table = 'bi_user_dashboard_permissions'
        unique_together = ('user', 'dashboard')
    
    def __str__(self):
        return f"{self.user.username} -> {self.get_dashboard_display()}"


class MartImplantationSuivi(models.Model):
    """Mart Implantation - Suivi des implantations par zone"""
    
    zone_id = models.IntegerField()
    annee = models.IntegerField()
    mois = models.IntegerField()
    nombre_implantations = models.IntegerField(null=True, blank=True)
    nombre_etapes = models.IntegerField(null=True, blank=True)
    etapes_terminees = models.IntegerField(null=True, blank=True)
    etapes_en_retard = models.IntegerField(null=True, blank=True)
    taux_completude_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = '"dwh_marts_implantation"."mart_implantation_suivi"'
        ordering = ['-annee', '-mois']


class MartIndemnisations(models.Model):
    """Mart Indemnisations - Suivi des indemnisations par zone et statut"""
    
    zone_id = models.IntegerField()
    zone_name = models.CharField(max_length=255, null=True, blank=True)
    annee = models.IntegerField()
    mois = models.IntegerField()
    annee_mois = models.CharField(max_length=10, null=True, blank=True)
    statut = models.CharField(max_length=100, null=True, blank=True)
    
    # Volumes
    nombre_indemnisations = models.IntegerField(null=True, blank=True)
    nombre_beneficiaires = models.IntegerField(null=True, blank=True)
    
    # Montants
    montant_total_restant = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    montant_moyen = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = '"dwh_marts_financier"."mart_indemnisations"'
        ordering = ['-annee', '-mois']


class MartEmploisCrees(models.Model):
    """Mart Emplois Créés - Suivi des emplois créés par zone et type"""
    
    zone_id = models.IntegerField()
    annee = models.IntegerField()
    mois = models.IntegerField()
    nombre_emplois_crees = models.IntegerField(null=True, blank=True)
    nombre_cdi = models.IntegerField(null=True, blank=True)
    nombre_cdd = models.IntegerField(null=True, blank=True)
    montant_salaires = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = '"dwh_marts_rh"."mart_emplois_crees"'
        ordering = ['-annee', '-mois']


class MartCreancesAgees(models.Model):
    """Mart Créances Âgées - Suivi des factures impayées par ancienneté"""
    
    zone_id = models.IntegerField()
    annee = models.IntegerField()
    mois = models.IntegerField()
    nombre_creances = models.IntegerField(null=True, blank=True)
    montant_creances = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    montant_recouvre = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    taux_recouvrement_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = '"dwh_marts_financier"."mart_creances_agees"'
        ordering = ['-annee', '-mois']


class MartSuiviImpenses(models.Model):
    """Mart Suivi Impenses - Tableau de bord complet des dossiers d'impenses"""
    
    # Identification
    impense_key = models.TextField(primary_key=True)
    impense_id = models.IntegerField()
    numero_dossier = models.CharField(max_length=255)
    
    # Lot et Zone
    lot_id = models.IntegerField(null=True, blank=True)
    lot_numero = models.CharField(max_length=100, null=True, blank=True)
    lot_superficie_m2 = models.FloatField(null=True, blank=True)
    lot_prix = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    lot_statut = models.CharField(max_length=50, null=True, blank=True)
    lot_viabilite = models.BooleanField(null=True, blank=True)
    zone_industrielle_id = models.IntegerField(null=True, blank=True)
    zone_industrielle_code = models.CharField(max_length=50, null=True, blank=True)
    zone_industrielle_libelle = models.CharField(max_length=255, null=True, blank=True)
    zone_industrielle_adresse = models.TextField(null=True, blank=True)
    
    # Entreprise
    entreprise_id = models.IntegerField(null=True, blank=True)
    nom_operateur = models.TextField(null=True, blank=True)
    nom_entreprise = models.CharField(max_length=255, null=True, blank=True)
    secteur_activite = models.CharField(max_length=100, null=True, blank=True)
    
    # Statut et Phase
    statut_actuel = models.TextField(null=True, blank=True)
    statut_libelle = models.TextField(null=True, blank=True)
    phase_actuelle = models.IntegerField(null=True, blank=True)
    phase_actuelle_libelle = models.TextField(null=True, blank=True)
    type_demande = models.TextField(null=True, blank=True)
    motif_cession = models.TextField(null=True, blank=True)
    
    # Décisions
    decision_verification = models.CharField(max_length=50, null=True, blank=True)
    resultat_analyse = models.CharField(max_length=50, null=True, blank=True)
    a_decision_verification = models.BooleanField(null=True, blank=True)
    a_resultat_analyse = models.BooleanField(null=True, blank=True)
    est_analyse = models.BooleanField(null=True, blank=True)
    est_cloture = models.BooleanField(null=True, blank=True)
    
    # Dates clés
    date_creation = models.DateTimeField(null=True, blank=True)
    date_emission = models.DateTimeField(null=True, blank=True)
    date_transmission = models.DateTimeField(null=True, blank=True)
    date_analyse = models.DateTimeField(null=True, blank=True)
    date_premiere_action = models.DateTimeField(null=True, blank=True)
    date_derniere_action = models.DateTimeField(null=True, blank=True)
    
    # Indicateurs temporels
    semaine_creation = models.FloatField(null=True, blank=True)
    mois_creation = models.TextField(null=True, blank=True)
    trimestre_creation = models.TextField(null=True, blank=True)
    jour_semaine_creation = models.FloatField(null=True, blank=True)
    est_weekend_creation = models.BooleanField(null=True, blank=True)
    anciennete_dossier_jours = models.FloatField(null=True, blank=True)
    
    # Durées
    duree_totale_jours = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    duree_totale_heures = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    temps_phase1_heures = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    temps_phase2_heures = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    temps_phase3_heures = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    temps_phase4_heures = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    temps_phase5_heures = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    temps_phase6_heures = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    phase_la_plus_longue = models.TextField(null=True, blank=True)
    
    # Métriques workflow
    nb_actions_total = models.BigIntegerField(null=True, blank=True)
    nb_types_actions = models.BigIntegerField(null=True, blank=True)
    nb_agents_impliques = models.BigIntegerField(null=True, blank=True)
    nb_roles_impliques = models.BigIntegerField(null=True, blank=True)
    nb_validations = models.BigIntegerField(null=True, blank=True)
    nb_rejets = models.BigIntegerField(null=True, blank=True)
    nb_corrections = models.BigIntegerField(null=True, blank=True)
    nb_clotures = models.BigIntegerField(null=True, blank=True)
    derniere_phase_atteinte = models.IntegerField(null=True, blank=True)
    
    # Actions spécifiques
    nb_retours = models.BigIntegerField(null=True, blank=True)
    nb_soumissions = models.BigIntegerField(null=True, blank=True)
    nb_documents_uploades = models.BigIntegerField(null=True, blank=True)
    nb_invalidations_recevabilite = models.BigIntegerField(null=True, blank=True)
    nb_validations_recevabilite = models.BigIntegerField(null=True, blank=True)
    nb_allers_retours = models.BigIntegerField(null=True, blank=True)
    
    # Interventions par rôle
    nb_interventions_admin = models.BigIntegerField(null=True, blank=True)
    nb_interventions_operateur = models.BigIntegerField(null=True, blank=True)
    nb_interventions_utilisateur = models.BigIntegerField(null=True, blank=True)
    ratio_admin_operateur = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Agent principal
    agent_principal_id = models.IntegerField(null=True, blank=True)
    agent_principal_role = models.TextField(null=True, blank=True)
    nb_actions_agent_principal = models.BigIntegerField(null=True, blank=True)
    
    # Délais
    delai_moyen_reponse_heures = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    delai_max_reponse_heures = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    
    # Performance
    taux_rejet_pct = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    taux_correction_pct = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    taux_first_pass_pct = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    efficacite_actions_par_jour = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    jours_depuis_derniere_action = models.FloatField(null=True, blank=True)
    
    # Qualité
    a_documents_complets = models.BooleanField(null=True, blank=True)
    recevabilite_validee = models.BooleanField(null=True, blank=True)
    
    # Prédiction
    duree_estimee_restante_jours = models.IntegerField(null=True, blank=True)
    date_estimee_cloture = models.DateField(null=True, blank=True)
    complexite_score = models.IntegerField(null=True, blank=True)
    
    # Alertes
    est_inactif = models.BooleanField(null=True, blank=True)
    est_en_retard = models.BooleanField(null=True, blank=True)
    a_rejets_multiples = models.BooleanField(null=True, blank=True)
    a_corrections_excessives = models.BooleanField(null=True, blank=True)
    risque_abandon = models.BooleanField(null=True, blank=True)
    score_sante_dossier = models.IntegerField(null=True, blank=True)
    niveau_alerte = models.TextField(null=True, blank=True)
    
    # SLA
    sla_phase1_respecte = models.BooleanField(null=True, blank=True)
    sla_phase2_respecte = models.BooleanField(null=True, blank=True)
    sla_phase3_respecte = models.BooleanField(null=True, blank=True)
    nb_sla_depasses = models.IntegerField(null=True, blank=True)
    taux_conformite_sla_pct = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    
    # Metadata
    dbt_created_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = '"dwh_marts_operationnel"."mart_suivi_impenses"'
        ordering = ['-date_creation']
