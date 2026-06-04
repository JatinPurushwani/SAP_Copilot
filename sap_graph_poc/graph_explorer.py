import json

with open(
    "knowledge/relationships.json",
    "r",
    encoding="utf-8"
) as f:
    relationships = json.load(f)

start_table = "customers"

visited = set()
queue = [start_table]

print("\nGRAPH WALK\n")

while queue:

    current = queue.pop(0)

    if current in visited:
        continue

    visited.add(current)

    print(current)

    for rel in relationships:

        if rel["from_table"] == current:

            next_table = rel["to_table"]

            if next_table not in visited:
                queue.append(next_table)

        elif rel["to_table"] == current:

            next_table = rel["from_table"]

            if next_table not in visited:
                queue.append(next_table)