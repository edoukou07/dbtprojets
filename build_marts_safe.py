#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Configure encoding BEFORE any imports
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Now import psycopg2
try:
    import psycopg2
    from psycopg2 import sql
    print("[INFO] psycopg2 imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import psycopg2: {e}")
    sys.exit(1)

def connect_db():
    """Connect to PostgreSQL with error handling"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='sigeti_node_db',
            user='postgres',
            password='sigeti'
        )
        print("[SUCCESS] Connected to PostgreSQL")
        return conn
    except psycopg2.OperationalError as e:
        print(f"[ERROR] Connection failed: {str(e, errors='replace')}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error during connection: {type(e).__name__}: {str(e, errors='replace')}")
        return None

def build_marts():
    """Build marts from SQL directly"""
    conn = connect_db()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        print("\n[INFO] Dropping existing mart_portefeuille_clients...")
        try:
            cur.execute("DROP TABLE IF EXISTS dwh.mart_portefeuille_clients CASCADE")
            conn.commit()
            print("[SUCCESS] Table dropped")
        except Exception as e:
            print(f"[WARNING] Drop failed (may not exist): {str(e, errors='replace')}")
            conn.rollback()
        
        print("\n[INFO] Creating mart_portefeuille_clients...")
        
        # Read SQL from file
        sql_file = r"C:\Users\hynco\Desktop\DWH_SIG\models\marts\clients\mart_portefeuille_clients.sql"
        try:
            with open(sql_file, 'r', encoding='utf-8', errors='replace') as f:
                sql_content = f.read()
            print(f"[SUCCESS] SQL file loaded ({len(sql_content)} bytes)")
        except Exception as e:
            print(f"[ERROR] Failed to read SQL file: {e}")
            return False
        
        # Wrap in CREATE TABLE AS
        full_sql = f"CREATE TABLE dwh.mart_portefeuille_clients AS {sql_content}"
        
        try:
            cur.execute(full_sql)
            conn.commit()
            print("[SUCCESS] mart_portefeuille_clients created")
        except Exception as e:
            print(f"[ERROR] Failed to create table: {str(e, errors='replace')}")
            conn.rollback()
            return False
        
        # Verify
        print("\n[INFO] Verifying table...")
        try:
            cur.execute("""
                SELECT 
                    COUNT(DISTINCT entreprise_id) as total_clients,
                    SUM(COALESCE(ca_total, 0)) as ca_total
                FROM dwh.mart_portefeuille_clients
            """)
            result = cur.fetchone()
            if result:
                total_clients, ca_total = result
                print(f"[SUCCESS] Total Clients: {total_clients}")
                print(f"[SUCCESS] CA Total: {ca_total:,.2f} FCFA")
        except Exception as e:
            print(f"[ERROR] Verification failed: {str(e, errors='replace')}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[FATAL] Unexpected error: {type(e).__name__}: {str(e, errors='replace')}")
        try:
            conn.close()
        except:
            pass
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Building DWH marts with error handling")
    print("=" * 60)
    
    success = build_marts()
    
    print("\n" + "=" * 60)
    if success:
        print("COMPLETED SUCCESSFULLY")
    else:
        print("FAILED - See errors above")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
