import json

concepts = {
    "Revenue": {
        "table": "billing_documents",
        "column": "total_amount",
        "aggregation": "SUM"
    },

    "Customer": {
        "table": "customers",
        "column": "customer_name"
    },

    "Vendor": {
        "table": "vendors"
    },

    "Invoice": {
        "table": "invoices"
    },

    "Sales Order": {
        "table": "sales_orders"
    },

    "Material": {
        "table": "materials"
    },

    "Employee": {
        "table": "employees"
    },

    "Purchase Order": {
        "table": "purchase_orders"
    }
}

with open(
    "knowledge/business_concepts.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        concepts,
        f,
        indent=2
    )

print(
    f"Generated {len(concepts)} concepts"
)