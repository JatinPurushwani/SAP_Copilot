import json


QUESTION = "Show revenue by customer"


with open(
    "knowledge/business_terms.json",
    "r",
    encoding="utf-8"
) as f:
    business_terms = json.load(f)

with open(
    "knowledge/relationships.json",
    "r",
    encoding="utf-8"
) as f:
    relationships = json.load(f)


question_lower = QUESTION.lower()

matched_terms = {}

for term, metadata in business_terms.items():

    if term.lower() in question_lower:
        matched_terms[term] = metadata


print("\n" + "=" * 60)
print("MATCHED BUSINESS TERMS")
print("=" * 60)

for term, metadata in matched_terms.items():
    print(f"\n{term}")
    print(json.dumps(metadata, indent=2))


print("\n" + "=" * 60)
print("RELEVANT RELATIONSHIPS")
print("=" * 60)

relevant_tables = set()

for _, metadata in matched_terms.items():

    if "table" in metadata:
        relevant_tables.add(metadata["table"])


for rel in relationships:

    if (
        rel["from_table"] in relevant_tables
        or rel["to_table"] in relevant_tables
    ):
        print(
            rel["join_condition"]
        )