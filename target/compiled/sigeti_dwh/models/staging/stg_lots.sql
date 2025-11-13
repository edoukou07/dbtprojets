

select
    id,
    numero,
    ilot,
    superficie,
    unite_mesure,
    prix,
    statut,
    priorite,
    viabilite,
    description,
    coordonnees,
    zone_industrielle_id,
    zone_id,
    entreprise_id,
    date_acquisition,
    date_reservation,
    delai_option,
    polygon,
    location,
    operateur_id,
    created_at,
    updated_at
from "sigeti_node_db"."public"."lots"
where id is not null