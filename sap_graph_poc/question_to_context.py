import json

QUESTION = "Show revenue by customer"


with open(
    "knowledge/business_concepts.json",
    "r",
    encoding="utf-8"
) as f:
    concepts = json.load(f)

question_lower = QUESTION.lower()

matches = {}

for concept, metadata in concepts.items():

    if concept.lower() in question_lower:

        matches[concept] = metadata


print("\n" + "=" * 60)
print("QUESTION")
print("=" * 60)
print(QUESTION)

print("\n" + "=" * 60)
print("MATCHED CONCEPTS")
print("=" * 60)

for concept, metadata in matches.items():

    print(f"\n{concept}")

    print(
        json.dumps(
            metadata,
            indent=2
        )
    )


print("\n" + "=" * 60)
print("CONTEXT FOR LLM")
print("=" * 60)

for concept, metadata in matches.items():

    if "table" in metadata:

        print(
            f"{concept} maps to table "
            f"{metadata['table']}"
        )

    if "column" in metadata:

        print(
            f"{concept} uses column "
            f"{metadata['column']}"
        )

    if "aggregation" in metadata:

        print(
            f"Aggregation: "
            f"{metadata['aggregation']}"
        )