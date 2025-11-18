
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'dwh_facts' AND table_name = 'fait_collectes'
ORDER BY ordinal_position;
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'dwh_facts' AND table_name = 'fait_factures'
ORDER BY ordinal_position;
