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
