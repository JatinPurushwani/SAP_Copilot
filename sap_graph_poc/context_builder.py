import json


QUESTION = "Show revenue by customer"


# ==========================================
# LOAD FILES
# ==========================================

with open(
    "knowledge/business_concepts.json",
    "r",
    encoding="utf-8"
) as f:
    business_concepts = json.load(f)

with open(
    "knowledge/relationships.json",
    "r",
    encoding="utf-8"
) as f:
    relationships = json.load(f)


# ==========================================
# FIND MATCHING CONCEPTS
# ==========================================

question_lower = QUESTION.lower()

matched_concepts = {}

for concept, metadata in business_concepts.items():

    concept_words = concept.lower().split()

    if any(
        word in question_lower
        for word in concept_words
    ):
        matched_concepts[concept] = metadata


# ==========================================
# FIND RELEVANT TABLES
# ==========================================

relevant_tables = set()

for concept, metadata in matched_concepts.items():

    table = metadata.get("table")

    if table:
        relevant_tables.add(table)


# ==========================================
# FIND RELEVANT RELATIONSHIPS
# ==========================================

relevant_relationships = []

for rel in relationships:

    if (
        rel["from_table"] in relevant_tables
        or rel["to_table"] in relevant_tables
    ):
        relevant_relationships.append(rel)


# ==========================================
# OUTPUT
# ==========================================

print("\n" + "=" * 60)
print("QUESTION")
print("=" * 60)
print(QUESTION)

print("\n" + "=" * 60)
print("BUSINESS CONCEPTS")
print("=" * 60)

for concept, metadata in matched_concepts.items():

    print(f"\n{concept}")

    print(
        json.dumps(
            metadata,
            indent=2
        )
    )

print("\n" + "=" * 60)
print("RELEVANT TABLES")
print("=" * 60)

for table in sorted(relevant_tables):
    print(table)

print("\n" + "=" * 60)
print("RELEVANT RELATIONSHIPS")
print("=" * 60)

for rel in relevant_relationships:

    print(
        rel["join_condition"]
    )