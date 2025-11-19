#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bi_app', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from django.db import connection
cursor = connection.cursor()

# Vérifier le vrai statut 'occupé'
cursor.execute('''
SELECT DISTINCT statut::text
FROM lots
WHERE statut::text != 'disponible'
''')

occupied_status = cursor.fetchone()[0]
print(f'Statut "occupé" real value: {occupied_status!r}')

# Recalculer la mart avec le vrai statut
sql_create = f'''
DROP TABLE IF EXISTS "dwh_marts_occupation"."mart_occupation_zones_new";

CREATE TABLE "dwh_marts_occupation"."mart_occupation_zones_new" AS
with lots as (
    select 
        l.id as lot_id,
        l.numero,
        l.superficie,
        l.prix,
        l.statut,
        l.viabilite,
        l.zone_industrielle_id,
        l.entreprise_id
    from lots l
),

zones as (
    select 
        z.id as zone_id,
        z.libelle as nom_zone
    from zones_industrielles z
),

demandes_valides as (
    select distinct lot_id
    from demandes_attribution
    where statut = 'VALIDE'
),

occupation_data as (
    select
        z.zone_id,
        z.nom_zone,
        count(*) as nombre_total_lots,
        count(case when l.statut::text = 'disponible' then 1 end) as lots_disponibles,
        count(case when dv.lot_id is not null then 1 end) as lots_attribues,
        count(case when l.statut::text != 'disponible' and dv.lot_id is null then 1 end) as lots_reserves,
        sum(l.superficie) as superficie_totale,
        sum(case when l.statut::text = 'disponible' then l.superficie else 0 end) as superficie_disponible,
        sum(case when dv.lot_id is not null then l.superficie else 0 end) as superficie_attribuee,
        round(
            (count(case when dv.lot_id is not null then 1 end)::numeric / nullif(count(*), 0)::numeric * 100), 
            2
        ) as taux_occupation_pct,
        sum(l.prix) as valeur_totale_lots,
        sum(case when l.statut::text = 'disponible' then l.prix else 0 end) as valeur_lots_disponibles,
        count(case when l.viabilite = true then 1 end) as lots_viabilises,
        round(
            (count(case when l.viabilite = true then 1 end)::numeric / nullif(count(*), 0)::numeric * 100), 
            2
        ) as taux_viabilisation_pct
    from lots l
    left join zones z on l.zone_industrielle_id = z.zone_id
    left join demandes_valides dv on l.lot_id = dv.lot_id
    group by z.zone_id, z.nom_zone
)

select 
    zone_id,
    nom_zone,
    nombre_total_lots,
    lots_disponibles,
    lots_attribues,
    lots_reserves,
    superficie_totale,
    superficie_disponible,
    superficie_attribuee,
    taux_occupation_pct,
    valeur_totale_lots,
    valeur_lots_disponibles,
    lots_viabilises,
    taux_viabilisation_pct,
    null::integer as nombre_demandes_attribution,
    null::integer as demandes_approuvees,
    null::integer as demandes_rejetees,
    null::integer as demandes_en_attente,
    null::numeric as delai_moyen_traitement,
    null::numeric as taux_approbation_pct
from occupation_data
'''

cursor.execute(sql_create)

# Copier les données
cursor.execute('''
DELETE FROM "dwh_marts_occupation"."mart_occupation_zones"
''')
cursor.execute('''
INSERT INTO "dwh_marts_occupation"."mart_occupation_zones"
SELECT * FROM "dwh_marts_occupation"."mart_occupation_zones_new"
''')
cursor.execute('''
DROP TABLE "dwh_marts_occupation"."mart_occupation_zones_new"
''')

connection.commit()
print('✓ Mart recalculée avec réserves correctement comptabilisées!')

# Vérifier les résultats
cursor.execute('''
SELECT 
    nom_zone,
    nombre_total_lots,
    lots_attribues,
    lots_disponibles,
    lots_reserves,
    (lots_attribues + lots_disponibles + lots_reserves) as total_check,
    taux_occupation_pct
FROM "dwh_marts_occupation"."mart_occupation_zones"
ORDER BY nom_zone
''')

results = cursor.fetchall()
print('\n Données mises à jour:')
for nom, total, attrib, dispo, reserves, check, taux in results:
    if total > 0:
        print(f'{nom}: Total={total}, Attribués={attrib}, Disponibles={dispo}, Réservés={reserves}, Check={check}, Taux={taux}%')
