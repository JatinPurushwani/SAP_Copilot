# Billing Document

Table: billing_documents

Purpose:
Stores invoices generated from sales orders.

Columns:
- id
- company_id
- invoice_number
- sales_order_id
- customer_id
- invoice_date
- due_date
- total_amount
- currency
- status

Relationships:

billing_documents.sales_order_id
    →
sales_orders.id

billing_documents.customer_id
    →
customers.id

Related Concepts:
- Revenue
- Customer
- Sales Order

Questions Supported:
- Revenue reporting
- Invoice aging
- Customer billing analysis
