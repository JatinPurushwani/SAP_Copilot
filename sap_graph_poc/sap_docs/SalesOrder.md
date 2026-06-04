# Sales Order

Table: sales_orders

Purpose:
Stores customer sales transactions.

Columns:
- id
- company_id
- sales_order_number
- customer_id
- so_date
- requested_delivery_date
- currency
- total_amount
- status

Relationships:

sales_orders.customer_id
    →
customers.id

sales_orders.id
    →
billing_documents.sales_order_id

Related Concepts:
- Customer
- Revenue
- Billing Document

Questions Supported:
- Sales trends
- Open orders
- Order status analysis
