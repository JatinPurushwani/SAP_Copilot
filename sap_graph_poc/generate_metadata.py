import json
from pathlib import Path

import psycopg2


# =====================================================
# DATABASE CONFIG
# =====================================================

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "niche_ai_pg",
    "user": "postgres",
    "password": "@Jppostgres84588"
}


# =====================================================
# OUTPUT DIRECTORY
# =====================================================

OUTPUT_DIR = Path("knowledge")
OUTPUT_DIR.mkdir(exist_ok=True)


# =====================================================
# CONNECT
# =====================================================

print("Connecting to PostgreSQL...")

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

print("Connected.")


# =====================================================
# EXTRACT TABLES + COLUMNS
# =====================================================

print("Extracting tables and columns...")

cur.execute(
    """
    SELECT
        table_name,
        column_name,
        data_type,
        is_nullable
    FROM information_schema.columns
    WHERE table_schema = 'public'
    ORDER BY table_name, ordinal_position
    """
)

column_rows = cur.fetchall()

tables = {}

for table_name, column_name, data_type, is_nullable in column_rows:

    if table_name not in tables:
        tables[table_name] = {
            "object": table_name,
            "columns": []
        }

    tables[table_name]["columns"].append(
        {
            "name": column_name,
            "data_type": data_type,
            "nullable": is_nullable == "YES"
        }
    )


# =====================================================
# PRIMARY KEYS
# =====================================================

print("Extracting primary keys...")

cur.execute(
    """
    SELECT
        tc.table_name,
        kcu.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    WHERE tc.constraint_type = 'PRIMARY KEY'
      AND tc.table_schema = 'public'
    """
)

pk_rows = cur.fetchall()

primary_keys = {}

for table_name, column_name in pk_rows:
    primary_keys.setdefault(table_name, []).append(column_name)


# =====================================================
# FOREIGN KEYS
# =====================================================

print("Extracting foreign keys...")

cur.execute(
    """
    SELECT
        tc.table_name,
        kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage ccu
        ON ccu.constraint_name = tc.constraint_name
        AND ccu.table_schema = tc.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY'
      AND tc.table_schema = 'public'
    ORDER BY tc.table_name
    """
)

fk_rows = cur.fetchall()

relationships = []

for (
    table_name,
    column_name,
    foreign_table_name,
    foreign_column_name
) in fk_rows:

    relationships.append(
        {
            "from_table": table_name,
            "from_column": column_name,
            "to_table": foreign_table_name,
            "to_column": foreign_column_name,
            "join_condition": (
                f"{table_name}.{column_name} = "
                f"{foreign_table_name}.{foreign_column_name}"
            )
        }
    )


# =====================================================
# SCHEMA METADATA
# =====================================================

print("Building schema metadata...")

schema_metadata = {}

for table_name, table_info in tables.items():

    schema_metadata[table_name] = {
        "table_name": table_name,
        "primary_keys": primary_keys.get(table_name, []),
        "column_count": len(table_info["columns"]),
        "columns": [
            col["name"]
            for col in table_info["columns"]
        ]
    }


# =====================================================
# WRITE sap_objects.json
# =====================================================

print("Writing sap_objects.json...")

with open(
    OUTPUT_DIR / "sap_objects.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        list(tables.values()),
        f,
        indent=2,
        ensure_ascii=False
    )


# =====================================================
# WRITE relationships.json
# =====================================================

print("Writing relationships.json...")

with open(
    OUTPUT_DIR / "relationships.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        relationships,
        f,
        indent=2,
        ensure_ascii=False
    )


# =====================================================
# WRITE schema_metadata.json
# =====================================================

print("Writing schema_metadata.json...")

with open(
    OUTPUT_DIR / "schema_metadata.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        schema_metadata,
        f,
        indent=2,
        ensure_ascii=False
    )


# =====================================================
# SUMMARY
# =====================================================

print()
print("=" * 60)
print("METADATA GENERATION COMPLETE")
print("=" * 60)

print(f"Tables Found        : {len(tables)}")
print(f"Relationships Found : {len(relationships)}")

print()
print("Generated Files:")

for file in OUTPUT_DIR.glob("*.json"):
    print(f"- {file.name}")

print()

cur.close()
conn.close()

print("Database connection closed.")