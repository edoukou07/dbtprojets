
ALTER DATABASE sigeti_node_db SET lc_messages = 'en_US.UTF-8';
ALTER DATABASE sigeti_node_db SET client_encoding = 'UTF8';
SELECT datname, encoding, datcollate FROM pg_database WHERE datname = 'sigeti_node_db';
