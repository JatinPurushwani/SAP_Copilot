# SAP INTELLIGENCE PLATFORM
## Pre-Sales Alignment Brief

**Date:** 3rd June 2026  
**Audience:** Pre-Sales Leadership, Business Development  
**Purpose:** Discussion about product and strategy

---

## PRODUCT VISION

### What We Are Building

An **on-premise SAP Intelligence Platform** that enables business users to access enterprise insights through:

1. **Dashboards** — Pre-built executive views (revenue trends, spending analysis, headcount metrics)
2. **Natural-Language Assistant** — "Show revenue by customer" instead of learning SQL or SAP navigation
3. **Enterprise Controls** — Role-based access (Finance sees AR/AP; Procurement sees Purchase Orders; Executives see summaries)

### Why This Matters

Enterprise customers have SAP systems that contain valuable business data, but accessing that data today requires:
- Logging into SAP and navigating complex menus
- Understanding technical field names and table structures
- Exporting to Excel and manually analyzing
- Waiting for IT/Finance to build custom reports

**Our solution eliminates this friction.** Business users ask questions in their language; the system retrieves SAP data and presents it on dashboards.

---

## CURRENT PRODUCT STATE

### What Exists Today

We have built a **solid platform foundation** with:

✅ **Secure Backend**  
REST API, authentication, user management, and session handling. Enterprise-grade error tracking and monitoring.

✅ **Frontend Interface**  
Responsive web application supporting chat-based queries, document uploads, and file search.

✅ **Cost Controls**  
Token accounting system that tracks AI usage and enforces per-user budgets. Enables accurate cost attribution.

✅ **Quality & Reliability**  
198 automated tests with continuous integration, error monitoring, and audit logging infrastructure.

### What Does NOT Exist Yet

- ❌ Business terminology layer (We need business-scenarios)
- ❌ Enterprise access control (no role-based authorization)
- ❌ On-premise deployment (currently cloud-only)

**This is intentional.** We validated that the current direction (cloud SaaS chatbot) did not match the intended product (on-premise SAP intelligence platform). Rather than build in the wrong direction, we are pausing to clarify strategy and gather requirements.

---

## TARGET PRODUCT STATE

### For First Deployment

The platform will be able to:

1. **Connect to SAP** — Query live data via OData services
2. **Translate Business Language** — "Revenue" → C_SalesOrdersMatched CDS View with appropriate filters
3. **Show Pre-Built Dashboards** — Revenue, Spending, Headcount, AR Aging (customer-specific variations)
4. **Enforce Access Control** — Finance users see financial data; Procurement users see purchase data; based on SAP roles
5. **Provide Transparency** — "This number comes from [CDS View], filtered by [Company Code], calculated as [formula]"
6. **Run On-Premise** — Docker containers deployed on customer's infrastructure

### Business Value

| Capability | Business Impact |
|---|---|
| Natural-language queries | Eliminates training; self-service insights |
| Pre-built dashboards | Faster decision-making; less manual analysis |
| Real-time SAP data | Decisions based on current state, not historical exports |
| Explainable answers | Finance teams can audit and trust results |
| On-premise deployment | Data stays within customer's infrastructure |
| Role-based access | Regulatory compliance; prevents unauthorized access |

---

## KEY BUSINESS BENEFITS

**For Finance Teams:**
- Answer questions about revenue, spending, receivables, payables in seconds
- Drill from executive summary to detailed transactions
- Verify data sources for audit purposes

**For Procurement Teams:**
- Track spend by vendor, category, purchase order status
- Identify cost-saving opportunities
- Answer "Where are we spending?" without Excel exports

**For Executives:**
- Pre-built KPI dashboards (revenue, EBITDA, headcount, cash flow)
- Ask follow-up questions ("Why is Q3 revenue down?") without waiting for IT
- Get transparent answers (see sources and calculations)

**For IT/Finance Leaders:**
- On-premise deployment (data doesn't leave infrastructure)
- Role-based security (aligned with SAP permissions)
- Audit trails (full query history for compliance)
- Cost controls (usage-based billing for AI services)

---

## CURRENT PROGRESS

### What We Have Accomplished

✅ **Foundation Built** — Backend, frontend, database, and infrastructure are production-quality and tested.

✅ **Direction Clarified** — Gap analysis completed; roadmap established and documented.

✅ **Strategy Validated** — Leadership and team aligned on on-premise SAP platform as target product.

### What We Are Planning

🔄 **Planned Discovery Activities** — We will work with SAP experts and business stakeholders to understand:
- Which SAP data is accessible via OData
- What business terms and metrics matter most
- How authorization should work (role mappings, company codes, cost centers)

🔄 **Implementation Planning** — Detailed roadmap created with phases and success criteria.

### What Comes Next

📋 **Build SAP Integration** — Create the connection to customer's SAP system.

📋 **Develop Dashboards** — Build pre-built executive, finance, and operational views.

📋 **Implement Access Control** — Enforce role-based permissions tied to SAP structure.

📋 **Deploy On-Premise** — Package as Docker containers for customer deployment.

---

## UPCOMING PRIORITIES

| What | Why It Matters | Status |
|---|---|---|
| SAP connectivity validation | Confirms technical feasibility; foundation for everything else | Discovery phase planned |
| Business glossary definition | Enables natural-language queries; core differentiator | Requirements validation phase planned |
| Dashboard design | Required for enterprise adoption; dashboards drive usage more than chat | Design phase planned |
| Access control implementation | Required for compliance; prevents unauthorized data access | Development phase planned |

---

## RISKS AND DEPENDENCIES

### What Could Delay Us

| Risk | Impact | Mitigation |
|---|---|---|
| SAP system complexity | OData connectivity may require custom configuration | Planning early engagement with SAP experts; building flexibility into discovery |
| Business requirements discovery | Taking longer to define metrics and terminology | Planning structured discovery process; early stakeholder engagement |
| Authorization complexity | SAP role model may be more nuanced than expected | Planning to understand requirements before implementation |

### What Organizations Must Provide

- SAP system access for integration testing
- Business stakeholder availability for planned requirements interviews
- SAP expert to validate technical approach
- Confirmation of deployment preferences (on-premise, infrastructure, AI model choice)

---

## SUGGESTED CUSTOMER CONVERSATION POINTS

### Opening

"We are building an on-premise intelligence platform that lets your business users ask questions about your SAP data in plain English and get answers on dashboards—without needing SAP expertise or IT support."

### Why Now

"Many enterprises struggle with SAP data access: only power users can navigate SAP effectively, business teams resort to manual Excel analysis, and real-time decisions are hard. We solve that."

### What You Get

"Dashboards for your key metrics. Natural-language questions answered in seconds. Role-based access so each team sees their relevant data. Everything runs on your infrastructure—your data never leaves."

### Discovery Approach

"We plan discovery workshops with your SAP team and business stakeholders to understand your specific SAP structure and business metrics. This ensures we build exactly what you need."

### How We Are Different

"Unlike generic dashboarding tools, we understand SAP deeply. We translate your business language directly to your SAP CDS Views. Results are explainable and auditable."

### Next Step

"Let's plan discovery workshops with your SAP team and business stakeholders. We'll confirm technical feasibility, understand your KPIs, and build a scoped roadmap."

---
