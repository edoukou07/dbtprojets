

select
    id,
    facture_id,
    montant,
    date_paiement,
    mode_paiement,
    statut,
    reference_paiement,
    piece_justificative,
    created_at,
    updated_at
from "sigeti_node_db"."public"."paiement_factures"
where id is not null