import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="sigeti_node_db",
    user="postgres",
    password="postgres"
)

print("=" * 100)
print("VALIDATION DES MARTS ENRICHIS - PHASE 1")
print("=" * 100)

# 1. Vérifier mart_conventions_validation
print("\n1. MART_CONVENTIONS_VALIDATION - Nouvelles Dimensions")
print("-" * 100)

query1 = """
SELECT 
    annee_mois,
    raison_sociale,
    forme_juridique,
    libelle_domaine,
    categorie_domaine,
    statut,
    nombre_conventions,
    taux_validation_pct,
    delai_moyen_traitement_jours
FROM dwh_marts_compliance.mart_conventions_validation
ORDER BY annee_mois DESC, nombre_conventions DESC
LIMIT 5;
"""

df1 = pd.read_sql(query1, conn)
print(df1.to_string(index=False))

print(f"\n✓ Total lignes: {len(df1)}")
print(f"✓ Dimensions entreprise ajoutées: raison_sociale, forme_juridique, libelle_domaine, categorie_domaine")

# 2. Vérifier mart_delai_approbation
print("\n\n2. MART_DELAI_APPROBATION - Nouvelles Dimensions")
print("-" * 100)

query2 = """
SELECT 
    annee_mois,
    raison_sociale,
    forme_juridique,
    libelle_domaine,
    categorie_domaine,
    statut,
    nombre_conventions,
    delai_moyen_traitement_jours,
    jours_attente_moyen
FROM dwh_marts_compliance.mart_delai_approbation
ORDER BY annee_mois DESC, nombre_conventions DESC
LIMIT 5;
"""

df2 = pd.read_sql(query2, conn)
print(df2.to_string(index=False))

print(f"\n✓ Total lignes: {len(df2)}")
print(f"✓ Dimensions entreprise ajoutées: raison_sociale, forme_juridique, libelle_domaine, categorie_domaine")

# 3. Vérifier la dimension domaines
print("\n\n3. DIM_DOMAINES_ACTIVITES_CONVENTIONS")
print("-" * 100)

query3 = """
SELECT 
    libelle_domaine,
    categorie_domaine
FROM dwh_dimensions.dim_domaines_activites_conventions
ORDER BY categorie_domaine, libelle_domaine;
"""

df3 = pd.read_sql(query3, conn)
print(df3.to_string(index=False))

print(f"\n✓ Total domaines uniques: {len(df3)}")

# 4. Nouvelles analyses possibles
print("\n\n4. NOUVELLES ANALYSES POSSIBLES AVEC PHASE 1")
print("-" * 100)

# Taux de validation par catégorie de domaine
query4 = """
SELECT 
    categorie_domaine,
    SUM(nombre_conventions) as total_conventions,
    ROUND(AVG(taux_validation_pct), 2) as taux_validation_moyen,
    ROUND(AVG(delai_moyen_traitement_jours), 1) as delai_moyen_jours
FROM dwh_marts_compliance.mart_conventions_validation
GROUP BY categorie_domaine
ORDER BY total_conventions DESC;
"""

df4 = pd.read_sql(query4, conn)
print("\n📊 TAUX DE VALIDATION PAR CATÉGORIE DE DOMAINE:")
print(df4.to_string(index=False))

# Délai par forme juridique
query5 = """
SELECT 
    forme_juridique,
    SUM(nombre_conventions) as total_conventions,
    ROUND(AVG(delai_moyen_traitement_jours), 1) as delai_moyen_jours
FROM dwh_marts_compliance.mart_delai_approbation
WHERE forme_juridique IS NOT NULL
GROUP BY forme_juridique
ORDER BY total_conventions DESC;
"""

df5 = pd.read_sql(query5, conn)
print("\n⏱️ DÉLAI MOYEN PAR FORME JURIDIQUE:")
print(df5.to_string(index=False))

print("\n" + "=" * 100)
print("RÉSUMÉ DES AMÉLIORATIONS - PHASE 1")
print("=" * 100)
print("""
✅ DIMENSIONS AJOUTÉES:
  - raison_sociale (nom entreprise)
  - forme_juridique (SARL, EURL, etc.)
  - libelle_domaine (domaine d'activité détaillé)
  - categorie_domaine (catégorie agrégée: INDUSTRIE, SERVICES, etc.)

✅ NOUVELLES VISUALISATIONS POSSIBLES:
  1. Taux de validation par domaine d'activité
  2. Délai moyen de traitement par secteur
  3. Distribution des conventions par forme juridique
  4. Performance par catégorie de domaine

📊 PROCHAINES ÉTAPES (non réalisées - colonnes manquantes dans source):
  ⚠️ montant_convention - nécessite ALTER TABLE conventions
  ⚠️ date_limite_reponse - nécessite ALTER TABLE conventions
  ⚠️ raison_rejet - nécessite ALTER TABLE conventions
  ⚠️ approuve_par - nécessite ALTER TABLE conventions
  ⚠️ entreprise_id, zone_industrielle_id - nécessitent relations métier

RECOMMANDATION: Demander à l'équipe métier/dev d'ajouter ces colonnes à la table source
""")

print("=" * 100)

conn.close()
