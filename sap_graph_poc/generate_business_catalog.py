import json
from pathlib import Path

knowledge_dir = Path("knowledge")

with open(
    knowledge_dir / "schema_metadata.json",
    "r",
    encoding="utf-8"
) as f:
    schema = json.load(f)

catalog = {}

for table_name in schema.keys():

    business_name = (
        table_name
        .replace("_", " ")
        .title()
    )

    catalog[business_name] = {
        "table": table_name
    }

with open(
    knowledge_dir / "business_catalog.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        catalog,
        f,
        indent=2,
        ensure_ascii=False
    )

print(
    f"Generated {len(catalog)} business entities"
)