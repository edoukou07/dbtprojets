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

    name = models.CharField(max_length=255)
    dashboard = models.CharField(max_length=50, choices=DASHBOARD_CHOICES)
    scheduled_at = models.DateTimeField()
    recipients = models.TextField(null=True, blank=True, help_text="Emails séparés par des virgules")
    created_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'bi_report_schedules'

    def __str__(self):
        return f"Report {self.name} -> {self.dashboard} @ {self.scheduled_at}"


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
    nom_zone = models.CharField(max_length=255, null=True, blank=True)
    annee = models.IntegerField()
    mois = models.IntegerField()
    annee_mois = models.CharField(max_length=10, null=True, blank=True)
    
    # Volumes
    nombre_implantations = models.IntegerField(null=True, blank=True)
    nombre_etapes = models.IntegerField(null=True, blank=True)
    
    # Statuts
    etapes_en_attente = models.IntegerField(null=True, blank=True)
    etapes_en_cours = models.IntegerField(null=True, blank=True)
    etapes_terminees = models.IntegerField(null=True, blank=True)
    etapes_en_retard = models.IntegerField(null=True, blank=True)
    etapes_bloquees = models.IntegerField(null=True, blank=True)
    
    # Durées
    duree_moyenne_jours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duree_max_jours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Pourcentages
    taux_completude_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pct_en_retard = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = '"dwh_marts_operationnel"."mart_implantation_suivi"'
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
    zone_name = models.CharField(max_length=255, null=True, blank=True)
    annee = models.IntegerField()
    mois = models.IntegerField()
    type_demande = models.CharField(max_length=100, null=True, blank=True)
    statut = models.CharField(max_length=100, null=True, blank=True)
    
    # Volumes
    nombre_demandes = models.IntegerField(null=True, blank=True)
    total_emplois = models.IntegerField(null=True, blank=True)
    total_emplois_expatries = models.IntegerField(null=True, blank=True)
    total_emplois_nationaux = models.IntegerField(null=True, blank=True)
    
    # Moyennes
    avg_emplois_par_demande = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Pourcentages
    pct_expatries = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pct_nationaux = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = '"dwh_marts_operationnel"."mart_emplois_crees"'
        ordering = ['-annee', '-mois']


class MartCreancesAgees(models.Model):
    """Mart Créances Âgées - Suivi des factures impayées par ancienneté"""
    
    tranche_anciennete = models.CharField(max_length=50)
    niveau_risque = models.CharField(max_length=50)
    
    # Volumes
    nombre_factures = models.IntegerField(null=True, blank=True)
    nombre_entreprises = models.IntegerField(null=True, blank=True)
    
    # Montants
    montant_total_factures = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    montant_moyen = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Délais
    delai_moyen_jours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    delai_max_jours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = '"dwh_marts_financier"."mart_creances_agees"'
        ordering = ['tranche_anciennete', 'niveau_risque']
