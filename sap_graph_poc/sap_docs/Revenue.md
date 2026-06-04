# Revenue

Business Concept

Definition:
Revenue is derived from billing_documents.total_amount.

Calculation:

SUM(billing_documents.total_amount)

Relationships:

Revenue
    →
Billing Document

Billing Document
    →
Sales Order

Sales Order
    →
Customer

Questions Supported:
- Revenue by customer
- Revenue by country
- Revenue trends
- Top customers