#!/usr/bin/env python3
# Test psycopg (v3) connection directly

import sys
print(f"Python: {sys.version}")

try:
    import psycopg
    print(f"psycopg version: {psycopg.__version__}")
except Exception as e:
    print(f"Failed to import psycopg: {e}")
    sys.exit(1)

# Try connecting
try:
    print("\nConnecting to PostgreSQL with psycopg v3...")
    conn = psycopg.connect(
        "postgresql://postgres:postgres@localhost:5432/sigeti_node_db"
    )
    print("SUCCESS: Connected!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    result = cursor.fetchone()
    print(f"Version: {result}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"FAILED: {type(e).__name__}")
    print(f"Message: {e}")
    import traceback
    traceback.print_exc()
