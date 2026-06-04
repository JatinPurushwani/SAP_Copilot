import json
from collections import deque


START_TABLE = "customers"
TARGET_TABLE = "billing_documents"


with open(
    "knowledge/relationships.json",
    "r",
    encoding="utf-8"
) as f:
    relationships = json.load(f)


graph = {}

for rel in relationships:

    from_table = rel["from_table"]
    to_table = rel["to_table"]

    graph.setdefault(from_table, [])
    graph.setdefault(to_table, [])

    graph[from_table].append(
        (to_table, rel)
    )

    graph[to_table].append(
        (from_table, rel)
    )


queue = deque()

queue.append(
    (
        START_TABLE,
        []
    )
)

visited = set()

path_found = None

while queue:

    current_table, current_path = queue.popleft()

    if current_table == TARGET_TABLE:
        path_found = current_path
        break

    if current_table in visited:
        continue

    visited.add(current_table)

    for next_table, rel in graph.get(current_table, []):

        if next_table not in visited:

            queue.append(
                (
                    next_table,
                    current_path + [rel]
                )
            )


print("\n" + "=" * 60)
print("JOIN PATH")
print("=" * 60)

if not path_found:

    print("No path found")

else:

    print(
        f"\n{START_TABLE}"
    )

    for rel in path_found:

        print(
            f"  ↓ {rel['join_condition']}"
        )

        print(
            f"{rel['to_table']}"
        )