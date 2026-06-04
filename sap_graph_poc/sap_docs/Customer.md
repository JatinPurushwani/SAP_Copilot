# Customer

Table: customers

Purpose:
Stores customer master data.

Columns:
- id
- company_id
- customer_code
- customer_name
- customer_type
- country
- credit_limit
- payment_terms
- tax_id

Relationships:

customers.id
    →
sales_orders.customer_id

Related Business Concepts:
- Revenue
- Sales Order
- Billing Document

Questions Supported:
- Top customers by revenue
- Customers by country
- Customer credit analysis