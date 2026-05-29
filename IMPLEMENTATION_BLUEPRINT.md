# IMPLEMENTATION BLUEPRINT
## SAP Intelligence Platform — Concrete Development Roadmap

**Status:** Derived from Production Gap Analysis + Second-Pass Architecture Review  
**Purpose:** Convert identified gaps into actionable development work  
**Audience:** Development team, technical leads  
**Level of Detail:** Specific enough to begin implementation; strategic enough to maintain direction

---

## OVERVIEW: THE REDIRECT

This document translates the 10 critical gaps identified in PROD_GAP_ANALYSIS.md into concrete development work.

**The Strategic Redirect:**
- Current: Multi-AI chatbot (cloud-deployed, generic DB access)
- Target: On-premise SAP intelligence platform (OData-based, semantically-aware, dashboard-first)
- Method: Reuse 40% of foundation; refactor 40%; replace 20%; defer complex features

**Success Criteria:**
- Can query customer's SAP system via OData
- Dashboard shows business data with explanation
- Authorization prevents unauthorized access
- System can be deployed on-premise
- Team has clear understanding of direction before continuing

---

## SECTION 1: IMMEDIATE ACTIONS (Next 7 Days)

**These are decision-making and validation activities. No feature development.**

### 1.1 SAP Expertise & Validation Review [Gaps 1, 7]

**Problem:** Team is making assumptions about SAP without validation

**Action:**
- [ ] Internal SAP expertise assessment: Does team have SAP S/4HANA implementation experience?
- [ ] If no internal expertise: Schedule validation review with customer's SAP team OR SAP implementation partner
- [ ] Validate: OData query patterns for financial data
- [ ] Validate: CDS View architecture and variation between customers
- [ ] Validate: Authorization object handling (ACTVT, company code, cost center)
- [ ] Validate: Field naming conventions (BAPI naming vs CDS naming vs custom naming)
- [ ] Get: Reference documentation for customer's SAP system
- [ ] Get: Customer SAP business process documentation

**Why:** Every wrong assumption about SAP will result in rework later. Better to validate now.

**Output:** SAP expertise validation checklist; SAP assumptions document signed off by customer SAP team

---

### 1.2 SAP Discovery Inventory Request [Gap 1]

**Problem:** Before semantic layer can be built, team must know what CDS Views are available

**Action:**
- [ ] Request from customer SAP team: Complete CDS View inventory
  - CDS View names
  - OData service names
  - Available fields for each CDS View
  - Field descriptions and business meanings
  - Any customer-specific CDS Views (Z_* or Y_*)
  - Any deprecated or test CDS Views to exclude

- [ ] Request: Key CDS Views for financial domain
  - Revenue/Sales: C_SalesOrdersMatched, custom views
  - Expenses: C_GeneralLedger, custom expense views
  - AR/AP: C_AccountsReceivable, C_AccountsPayable, custom views
  - Cash/Bank: C_BankAccount, custom cash views

- [ ] Request: Authorization structure
  - Which authorization objects control CDS View access (ACTVT, etc.)
  - How company codes are enforced
  - How cost centers are enforced
  - Any department-level access controls

**Why:** Cannot proceed with metadata registry without knowing what exists in customer's SAP.

**Output:** SAP CDS inventory spreadsheet; OData service list; Authorization object mappings

---

### 1.3 Customer Business Stakeholder Interview [Gaps 2, 3, 4, 8]

**Problem:** Product vision is not validated against real customer needs; business terminology is assumed, not discovered

**Action:**
- [ ] Schedule 2-hour call with customer (Finance Manager, Controller, or CFO)
- [ ] Ask: "What are the top 10 questions you ask your SAP system daily?"
- [ ] Ask: "What data are you currently exporting to Excel for analysis?"
- [ ] Ask: "What business metrics are you tracking manually?"
- [ ] Ask: "What reports do you run most frequently?"
- [ ] Ask: "What authorization rules are critical to enforce?"
- [ ] Ask: "If we mapped CDS View [X] to business term 'Revenue', is that correct for your business?"
- [ ] Ask: "Which users need to see which data? (by role, not by name)"
- [ ] Ask: "What KPIs do you care about most? (top 5)"

**Why:** Semantic layer must be grounded in real customer business language and real business problems.

**Output:** Customer business requirements document with business terminology, top 10 questions, KPI list, authorization rules

---

### 1.4 Deployment Model Confirmation [Gap 5, 9]

**Problem:** Product vision (on-prem + local LLM) conflicts with implementation (cloud)

**Action:**
- [ ] Leadership confirms: V1 deployment model (on-prem Docker + cloud AI, or full local?)
- [ ] Leadership confirms: AI strategy (cloud AI in V1; local LLM in V1.5/V2?)
- [ ] Leadership confirms: Go/no-go on redesign vs pivoting to cloud SaaS

**Why:** Architecture decisions cascade from this. Cannot proceed without clarity.

**Output:** Written decision on deployment and AI strategy; signed off by leadership

---

### 1.5 Team Skillset Assessment [All gaps]

**Problem:** Team may lack SAP and enterprise software experience

**Action:**
- [ ] Assess: Who has SAP experience?
- [ ] Assess: Who has enterprise software experience?
- [ ] Assess: Who will own OData integration?
- [ ] Assess: Who will own semantic layer?
- [ ] Assess: Who will own authorization?

**Why:** Identify training needs; allocate people to specialties

**Output:** Team skillset matrix; identified gaps; training plan

---

### 1.6 Technical Validation: SAP Connectivity [Gap 1]

**Problem:** Don't know if basic SAP OData access is possible with customer's setup

**Action:**
- [ ] Request: OData service endpoint from customer's SAP
- [ ] Request: Test credentials
- [ ] Build: Hello-world OData client (list available CDS Views)
- [ ] Test: Can we connect? Do we get metadata?
- [ ] Document: OData authentication (certificate? OAuth? API key?)

**Why:** If OData connectivity doesn't work, entire strategy fails. Validate immediately.

**Output:** Working proof-of-concept OData client; connectivity documentation

---

## SECTION 2: PHASE 0 — DISCOVERY (Weeks 1-2)

**SAP discovery and metadata registry. Must be completed before semantic layer design.**

### 2.1 SAP Metadata Registry [Solves Gap 1]

**Problem:** Team is making assumptions about which CDS Views exist and what fields they contain

**What to Build:**

A metadata registry that catalogs SAP's actual CDS Views and OData services:

**Database Schema:**

```sql
-- Store discovered CDS Views
CREATE TABLE IF NOT EXISTS sap_cds_views (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id TEXT NOT NULL,
  cds_view_name TEXT NOT NULL,  -- "C_SalesOrdersMatched"
  odata_service TEXT,  -- "C_SalesOrdersMatched_SRV"
  description TEXT,  -- "Sales orders matched with billing"
  is_custom BOOLEAN DEFAULT false,  -- true if Z_* or Y_*
  discovered_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(customer_id, cds_view_name)
);

-- Store fields within each CDS View
CREATE TABLE IF NOT EXISTS sap_cds_fields (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cds_view_id UUID REFERENCES sap_cds_views(id),
  field_name TEXT NOT NULL,  -- "CompanyCode", "Amount"
  field_type TEXT,  -- "String", "Decimal", "Date"
  is_key BOOLEAN DEFAULT false,  -- true if key field
  is_filterable BOOLEAN DEFAULT true,
  description TEXT,  -- "Company code for document"
  sample_value TEXT,  -- "1000"
  discovered_at TIMESTAMPTZ DEFAULT NOW()
);

-- Store relationships between CDS Views
CREATE TABLE IF NOT EXISTS sap_cds_relationships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_cds_view_id UUID REFERENCES sap_cds_views(id),
  target_cds_view_id UUID REFERENCES sap_cds_views(id),
  relationship_name TEXT,  -- "C_SalesOrdersMatched.to_BilledRevenueRecognition"
  description TEXT,
  discovered_at TIMESTAMPTZ DEFAULT NOW()
);

-- Store OData services
CREATE TABLE IF NOT EXISTS sap_odata_services (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id TEXT NOT NULL,
  service_name TEXT NOT NULL,  -- "C_SalesOrdersMatched_SRV"
  cds_view_id UUID REFERENCES sap_cds_views(id),
  endpoint_path TEXT,  -- "/sap/opu/odata/sap/C_SALESORDERSMATCHED_SRV"
  discovered_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(customer_id, service_name)
);

-- Store initial business glossary (from customer input)
CREATE TABLE IF NOT EXISTS sap_business_glossary (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id TEXT NOT NULL,
  business_term TEXT NOT NULL,  -- "Revenue", "Expense"
  business_definition TEXT,  -- "Amount recognized as income"
  primary_cds_view_id UUID REFERENCES sap_cds_views(id),  -- Discovered mapping
  validation_status TEXT DEFAULT 'PENDING',  -- "PENDING", "VALIDATED", "INCORRECT"
  validated_by TEXT,  -- customer SAP expert
  validated_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Discovery Service:**

```javascript
// backend/services/sap-metadata.service.js

class SAPMetadataRegistry {
  constructor(database, odataClient) {
    this.db = database;
    this.odata = odataClient;
  }

  // Import discovered CDS Views from SAP metadata
  async importCDSViews(customerId, cdsViewList) {
    // cdsViewList = [{name, description, is_custom}, ...]
    for (const view of cdsViewList) {
      await this.db
        .from('sap_cds_views')
        .upsert({
          customer_id: customerId,
          cds_view_name: view.name,
          description: view.description,
          is_custom: view.is_custom,
        }, { onConflict: 'customer_id,cds_view_name' });
    }
  }

  // Import field metadata for a CDS View
  async importCDSViewFields(customerId, cdsViewName, fieldList) {
    // fieldList = [{name, type, is_key, description}, ...]
    const view = await this.db
      .from('sap_cds_views')
      .select('id')
      .eq('customer_id', customerId)
      .eq('cds_view_name', cdsViewName)
      .single();

    for (const field of fieldList) {
      await this.db
        .from('sap_cds_fields')
        .insert({
          cds_view_id: view.id,
          field_name: field.name,
          field_type: field.type,
          is_key: field.is_key,
          description: field.description,
        });
    }
  }

  // Import discovered relationships
  async importRelationships(customerId, relationshipList) {
    // relationshipList = [{source, target, name}, ...]
    for (const rel of relationshipList) {
      const source = await this.getCDSViewId(customerId, rel.source);
      const target = await this.getCDSViewId(customerId, rel.target);

      if (source && target) {
        await this.db
          .from('sap_cds_relationships')
          .insert({
            source_cds_view_id: source,
            target_cds_view_id: target,
            relationship_name: rel.name,
          });
      }
    }
  }

  // Store business glossary item (from customer interview)
  async recordBusinessGlossaryItem(customerId, businessTerm, definition, primaryCDSViewName) {
    const view = await this.db
      .from('sap_cds_views')
      .select('id')
      .eq('customer_id', customerId)
      .eq('cds_view_name', primaryCDSViewName)
      .single();

    await this.db
      .from('sap_business_glossary')
      .insert({
        customer_id: customerId,
        business_term: businessTerm,
        business_definition: definition,
        primary_cds_view_id: view?.id,
        validation_status: 'PENDING',
      });
  }

  // Validate business glossary item (customer confirms mapping)
  async validateGlossaryItem(customerId, businessTerm, validated) {
    await this.db
      .from('sap_business_glossary')
      .update({
        validation_status: validated ? 'VALIDATED' : 'INCORRECT',
        validated_at: new Date(),
      })
      .eq('customer_id', customerId)
      .eq('business_term', businessTerm);
  }

  // Generate discovery report
  async generateDiscoveryReport(customerId) {
    const views = await this.db
      .from('sap_cds_views')
      .select('*')
      .eq('customer_id', customerId);

    const glossary = await this.db
      .from('sap_business_glossary')
      .select('*')
      .eq('customer_id', customerId);

    return {
      customer_id: customerId,
      cds_views_discovered: views.length,
      business_terms_identified: glossary.length,
      validated_terms: glossary.filter(g => g.validation_status === 'VALIDATED').length,
      pending_validation: glossary.filter(g => g.validation_status === 'PENDING').length,
      incorrect_mappings: glossary.filter(g => g.validation_status === 'INCORRECT').length,
    };
  }
}
```

**Workflow:**

```
1. Customer SAP team provides CDS View inventory
   → Import into sap_cds_views table

2. Query each CDS View for field metadata
   → Import into sap_cds_fields table

3. Customer business team interviews
   → Create business_glossary items
   → Map business terms to discovered CDS Views

4. Validation workshop with customer
   → "Is 'Revenue' = C_SalesOrdersMatched?"
   → "Is 'Expense' = C_GeneralLedger with filter GL account 6xxx?"
   → Mark as VALIDATED or INCORRECT

5. Deliver discovery report
   → "Here's what we found; here's what you confirmed"
   → Ready to build semantic layer
```

**Timeline:** 4 business days

**Definition of Done:**
- [ ] CDS Views catalog created and populated
- [ ] Field metadata for each CDS View documented
- [ ] Relationships between CDS Views discovered
- [ ] Business glossary created for customer's top 10 business terms
- [ ] Customer has validated 8+ glossary items
- [ ] Discovery report generated
- [ ] Tests pass

---

## SECTION 3: PHASE 1 — FOUNDATION (Weeks 3-4)

**Core SAP integration and semantic layer foundation. Nothing else works without this.**

### 3.1 SAP OData Client [Solves Gap 1]

**Problem:** Product cannot connect to SAP; has no way to query CDS Views

**What to Build:**

A production-ready OData client with:
- Secure connection handling (certificate, OAuth, or API key)
- Metadata discovery (list CDS Views from customer's SAP)
- Query execution (parameterized OData queries)
- Error handling (SAP-specific error responses)
- Result caching (metadata cache; query result cache with TTL)
- Pagination (for large result sets)

**Architecture:**

```javascript
// backend/services/sap/odata-client.js

class ODataClient {
  constructor(sapConfig) {
    this.baseUrl = sapConfig.odata_endpoint;
    this.auth = sapConfig.auth;  // certificate, oauth, or api key
    this.metadataCache = new Map();  // CDS View metadata
  }

  // List available CDS Views from SAP metadata
  async discoverCDSViews() {
    // Query $metadata endpoint
    // Parse XML response
    // Extract entity sets (CDS Views)
    // Cache for 1 hour
  }

  // Execute parameterized OData query
  async queryCDSView(cdsViewName, filters, selects) {
    // Build OData $filter syntax
    // Ensure all filters are parameterized (no SQL injection)
    // Handle pagination if needed
    // Execute query
    // Parse response
    // Return results + metadata
  }

  // Handle common SAP errors
  async handleSAPError(error) {
    if (error.is_timeout) return "SAP_TIMEOUT";
    if (error.is_auth_fail) return "SAP_AUTH_FAILED";
    if (error.is_invalid_filter) return "SAP_INVALID_FILTER";
    // ... more patterns
  }
}

module.exports = ODataClient;
```

**Usage:**

```javascript
// backend/services/chat.service.js

const odata = new ODataClient(sapConfig);

// Discover CDS Views
const views = await odata.discoverCDSViews();
// Returns: ["C_GeneralLedger", "C_SalesOrdersMatched", "C_AccountsReceivable", ...]

// Query a CDS View
const result = await odata.queryCDSView(
  "C_SalesOrdersMatched",
  { CompanyCode: "1000", PostingDate: ">= 2026-07-01" },
  ["CompanyCode", "DocumentNumber", "Amount"]
);
// Returns: { rows: [...], metadata: { cds_view, filters_applied, row_count } }
```

**What to Keep from Current Code:**
- Error handling patterns (from chatCleanup.service.js)
- HTTP client setup (from provider services)
- Configuration structure (from models.js)

**What to Remove:**
- Generic business DB tool (toolProcessor.service.js for SQL) — keep tool architecture, replace SQL with OData
- Multi-provider AI dispatch (keep one provider)

**Dependencies:**
- SAP connectivity credentials
- Test SAP system with CDS Views
- OData endpoint URL

**Timeline:** 5 business days

**Definition of Done:**
- [ ] Can list CDS Views from customer SAP
- [ ] Can execute a query (e.g., "get GL entries for company 1000")
- [ ] Can handle pagination (1000+ rows)
- [ ] Errors are caught and classified
- [ ] Metadata cached for performance
- [ ] Unit tests pass

---

### 3.2 Semantic Layer Foundation [Solves Gap 2]

**IMPORTANT CAVEAT:**

All CDS Views, field mappings, KPI definitions, and business relationships shown in this blueprint are illustrative examples only.

Actual semantic layer mappings must be derived through:
1. SAP metadata discovery (Phase 0, Section 2.1)
2. Customer business glossary validation (Phase 0, Section 2.1)
3. Customer SAP team review

**Do NOT hardcode example mappings into production systems.**

The semantic layer must be metadata-driven and configuration-driven. Business terms, CDS View mappings, calculations, and field definitions must be stored in the database and loaded from customer configuration files — never hardcoded in application logic.

---

**Problem:** Product has no way to translate "revenue" to a CDS View query

**What to Build:**

Database schema + management layer for semantic definitions:

**Database Schema:**

```sql
-- Store business term definitions per customer
CREATE TABLE IF NOT EXISTS semantic_definitions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id TEXT NOT NULL,
  business_term TEXT NOT NULL,  -- "Revenue", "Expense", "AR_Aging", etc.
  
  -- Definition
  definition TEXT,  -- "Amount recognized as income from sales"
  
  -- CDS View mapping
  primary_cds_view TEXT NOT NULL,  -- "C_SalesOrdersMatched"
  supporting_cds_views TEXT[] DEFAULT '{}',  -- ["C_GeneralLedger"]
  
  -- Filters (applied automatically)
  filters JSONB DEFAULT '[]',  -- [{field: "Status", op: "!=", value: "REVERSED"}]
  
  -- Calculation
  calculation TEXT,  -- "SUM(Amount)"
  
  -- Metadata
  is_custom BOOLEAN DEFAULT false,  -- true if customer-specific
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(customer_id, business_term)
);

-- Store per-customer term instances (what they actually queried)
CREATE TABLE IF NOT EXISTS semantic_queries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id TEXT NOT NULL,
  user_id UUID REFERENCES users(id),
  business_term TEXT NOT NULL,  -- what they asked for
  cds_views_used TEXT[] NOT NULL,  -- which CDS Views we queried
  filters_applied JSONB NOT NULL,  -- what filters we applied
  result_count INTEGER,
  query_timestamp TIMESTAMPTZ DEFAULT NOW(),
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Backend Service:**

```javascript
// backend/services/semantic-layer.service.js

class SemanticLayer {
  constructor(database) {
    this.db = database;
    this.definitionCache = new Map();  // {customer_id -> {term -> definition}}
  }

  // Load semantic definitions for a customer
  async loadDefinitions(customerId) {
    if (this.definitionCache.has(customerId)) {
      return this.definitionCache.get(customerId);
    }

    const definitions = await this.db
      .from('semantic_definitions')
      .select('*')
      .eq('customer_id', customerId);

    const dict = {};
    definitions.forEach(def => {
      dict[def.business_term] = def;
    });

    this.definitionCache.set(customerId, dict);
    return dict;
  }

  // Resolve a business term to a CDS View query
  async resolveBusinessTerm(customerId, businessTerm) {
    const definitions = await this.loadDefinitions(customerId);
    const definition = definitions[businessTerm.toUpperCase()];

    if (!definition) {
      throw new Error(`Unknown business term: ${businessTerm}`);
    }

    return {
      cds_view: definition.primary_cds_view,
      supporting_views: definition.supporting_cds_views,
      filters: definition.filters,
      calculation: definition.calculation,
      definition: definition.definition,
    };
  }

  // Log what was queried (for audit + improvement)
  async logQuery(customerId, userId, businessTerm, cdsViewsUsed, filtersApplied, resultCount) {
    await this.db
      .from('semantic_queries')
      .insert({
        customer_id: customerId,
        user_id: userId,
        business_term: businessTerm,
        cds_views_used: cdsViewsUsed,
        filters_applied: filtersApplied,
        result_count: resultCount,
      });
  }

  // Seed semantic layer for new customer (admin function)
  async seedDefinitions(customerId, definitions) {
    // definitions = [{ business_term: "Revenue", cds_view: "...", ... }]
    await this.db
      .from('semantic_definitions')
      .insert(definitions.map(d => ({
        ...d,
        customer_id: customerId,
      })));

    this.definitionCache.delete(customerId);  // invalidate cache
  }
}
```

**Integration with Chat Controller:**

```javascript
// backend/controllers/chat.controller.js (modified)

const sendMessage = async (req, res) => {
  const { message, customerId } = req.body;

  // OLD (broken): Try to parse SQL from AI
  // NEW: Extract business term from query

  const semanticLayer = new SemanticLayer(supabase);

  // Resolve business term to CDS View
  const resolution = await semanticLayer.resolveBusinessTerm(
    customerId,
    message  // "What's our revenue?" -> extract "Revenue" term
  );

  // Query SAP via OData
  const results = await odata.queryCDSView(
    resolution.cds_view,
    resolution.filters,
    ["*"]
  );

  // Apply calculation
  const answer = calculateResult(results, resolution.calculation);

  // Log for audit
  await semanticLayer.logQuery(
    customerId,
    user.id,
    "Revenue",
    [resolution.cds_view],
    resolution.filters,
    results.length
  );

  res.json({ answer, explanation: resolution });
};
```

**What to Keep from Current Code:**
- Database structure (extend, don't replace)
- Service architecture (add SemanticLayer as new service)

**Dependencies:**
- Customer must define their business terms (workshops, documentation)
- OData client (from Section 2.1)
- Database migration scripts

**Timeline:** 4 business days

**Definition of Done:**
- [ ] Semantic definitions table created
- [ ] Can store and retrieve business term definitions
- [ ] Can resolve "Revenue" to C_SalesOrdersMatched
- [ ] SemanticLayer service integrated into chat flow
- [ ] Cache is working (repeated queries don't re-query DB)
- [ ] Audit logging works
- [ ] Tests pass

---

### 3.3 Initial Dashboard Shells [Solves Gap 3]

**Problem:** Chat-first interface will fail to drive adoption; enterprises expect dashboards

**What to Build:**

Empty dashboard components (no data yet; just structure):

**Frontend Architecture:**

```jsx
// frontend/src/pages/DashboardPage.jsx

import React, { useState } from 'react';
import ExecutiveDashboard from './dashboards/ExecutiveDashboard';
import FinanceDashboard from './dashboards/FinanceDashboard';
import ProcurementDashboard from './dashboards/ProcurementDashboard';
import ChatCopilot from '../components/ChatCopilot';

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('executive');
  const [chatOpen, setChatOpen] = useState(true);

  return (
    <div className="dashboard-container">
      {/* Left side: Dashboard */}
      <div className="dashboard-main">
        <nav className="dashboard-tabs">
          <button 
            className={activeTab === 'executive' ? 'active' : ''}
            onClick={() => setActiveTab('executive')}
          >
            Executive Overview
          </button>
          <button 
            className={activeTab === 'finance' ? 'active' : ''}
            onClick={() => setActiveTab('finance')}
          >
            Finance Details
          </button>
          <button 
            className={activeTab === 'procurement' ? 'active' : ''}
            onClick={() => setActiveTab('procurement')}
          >
            Procurement
          </button>
        </nav>

        <div className="dashboard-content">
          {activeTab === 'executive' && <ExecutiveDashboard />}
          {activeTab === 'finance' && <FinanceDashboard />}
          {activeTab === 'procurement' && <ProcurementDashboard />}
        </div>
      </div>

      {/* Right side: Chat panel */}
      {chatOpen && (
        <div className="chat-copilot-panel">
          <button 
            className="close-button"
            onClick={() => setChatOpen(false)}
          >
            ×
          </button>
          <ChatCopilot context={`Asking about ${activeTab} data`} />
        </div>
      )}
    </div>
  );
}
```

**Dashboard Components (Empty Shells):**

```jsx
// frontend/src/pages/dashboards/ExecutiveDashboard.jsx

export default function ExecutiveDashboard() {
  return (
    <div className="dashboard">
      <h1>Executive Overview</h1>
      
      <div className="metric-grid">
        <div className="metric-card">
          <h3>Revenue (Q3 2026)</h3>
          <div className="metric-value">--</div>
          <p className="metric-source">[Loading from SAP...]</p>
        </div>

        <div className="metric-card">
          <h3>Total Spending</h3>
          <div className="metric-value">--</div>
          <p className="metric-source">[Loading from SAP...]</p>
        </div>

        <div className="metric-card">
          <h3>Headcount</h3>
          <div className="metric-value">--</div>
          <p className="metric-source">[Loading from SAP...]</p>
        </div>
      </div>

      <div className="chart-section">
        <h2>Revenue Trend</h2>
        <div className="chart-placeholder">
          [Chart will appear here]
        </div>
      </div>
    </div>
  );
}
```

**What to Keep from Current Code:**
- React component architecture
- Auth context and routing
- Styling framework

**What to Change:**
- Move chat from primary to secondary position (right panel)
- Reorganize navigation (dashboard tabs, not "Chat" route)
- Keep chat accessible but not dominant

**Timeline:** 3 business days

**Definition of Done:**
- [ ] Dashboard layout created (dashboard-main + chat-copilot-panel)
- [ ] Three dashboard tabs (Executive, Finance, Procurement)
- [ ] Empty metric cards with placeholders
- [ ] Chat copilot panel on right side
- [ ] Navigation between tabs works
- [ ] Responsive layout (mobile consideration)
- [ ] Tests pass (component rendering)

---

## SECTION 4: PHASE 2 — AUTHORIZATION & AUDIT (Weeks 5-6)

**Role-based access control and compliance-grade audit logging. Critical for enterprise.**

### 4.1 Role-Based Authorization Layer [Solves Gap 4]

**Problem:** Product has no authorization; all logged-in users see all data

**What to Build:**

Authorization enforcement at query level (not UI level):

**Database Schema:**

```sql
-- Role definitions (mapped from SAP)
CREATE TABLE IF NOT EXISTS roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id TEXT NOT NULL,
  role_name TEXT NOT NULL,  -- "Finance Manager", "Procurement Manager", etc.
  
  -- Capabilities: which semantic terms this role can access
  capabilities JSONB NOT NULL,  -- ["Revenue", "Expense", "AR", "AP"]
  
  -- Default filters applied to all queries by this role
  default_filters JSONB DEFAULT '{}',  -- {company_code: "1000", cost_center: user.cost_center}
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(customer_id, role_name)
);

-- User role assignments
CREATE TABLE IF NOT EXISTS user_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
  customer_id TEXT NOT NULL,
  
  -- Additional context for this role assignment
  cost_center TEXT,  -- "CC_100", "CC_200", etc.
  company_code TEXT,  -- "1000", "2000"
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(user_id, customer_id)
);

-- Authorization audit log (separate from query audit)
CREATE TABLE IF NOT EXISTS auth_audit (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  customer_id TEXT NOT NULL,
  
  action TEXT NOT NULL,  -- "QUERY_ALLOWED", "QUERY_DENIED", "ROLE_ASSIGNED"
  business_term TEXT,  -- what they tried to access
  reason TEXT,  -- "User has Finance Manager role", "User lacks Procurement capability"
  
  timestamp TIMESTAMPTZ DEFAULT NOW()
);
```

**Authorization Service:**

```javascript
// backend/services/authorization.service.js

class AuthorizationService {
  constructor(database) {
    this.db = database;
    this.roleCache = new Map();  // {customer_id -> {role_name -> role}}
  }

  // Check if user can access a business term
  async canAccessBusinessTerm(userId, customerId, businessTerm) {
    // Get user's role
    const userRole = await this.db
      .from('user_roles')
      .select('*, roles(*)')
      .eq('user_id', userId)
      .eq('customer_id', customerId)
      .single();

    if (!userRole) {
      await this.logAuthAudit(userId, customerId, 'QUERY_DENIED', businessTerm, 'No role assigned');
      return { allowed: false, reason: 'No role assigned' };
    }

    // Check if role has capability
    const capabilities = userRole.roles.capabilities;
    const termUpper = businessTerm.toUpperCase();

    if (!capabilities.includes(termUpper)) {
      await this.logAuthAudit(userId, customerId, 'QUERY_DENIED', businessTerm, 
        `Role ${userRole.roles.role_name} does not have capability ${businessTerm}`);
      return { allowed: false, reason: 'Insufficient permissions' };
    }

    await this.logAuthAudit(userId, customerId, 'QUERY_ALLOWED', businessTerm, 
      `User has ${userRole.roles.role_name} role`);

    return { 
      allowed: true, 
      role: userRole.roles.role_name,
      defaultFilters: {
        ...userRole.roles.default_filters,
        cost_center: userRole.cost_center,
        company_code: userRole.company_code,
      }
    };
  }

  // Apply role-based filters to a query
  async applyRoleFilters(userId, customerId, proposedFilters) {
    const userRole = await this.db
      .from('user_roles')
      .select('*')
      .eq('user_id', userId)
      .eq('customer_id', customerId)
      .single();

    if (!userRole) {
      throw new Error('User has no role assignment');
    }

    // Merge user-requested filters with role-enforced filters
    const enforced = {
      company_code: userRole.company_code,  // Cannot override
      cost_center: userRole.cost_center,    // Cannot override
      ...proposedFilters,  // User can add more specific filters
    };

    return enforced;
  }

  // Log authorization decision
  async logAuthAudit(userId, customerId, action, businessTerm, reason) {
    await this.db
      .from('auth_audit')
      .insert({
        user_id: userId,
        customer_id: customerId,
        action,
        business_term: businessTerm,
        reason,
      });
  }

  // Admin: Assign role to user
  async assignRole(userId, customerId, roleId, costCenter, companyCode) {
    await this.db
      .from('user_roles')
      .upsert({
        user_id: userId,
        customer_id: customerId,
        role_id: roleId,
        cost_center: costCenter,
        company_code: companyCode,
      });

    await this.logAuthAudit(userId, customerId, 'ROLE_ASSIGNED', null, `Assigned role ${roleId}`);
  }
}
```

**Integration with Chat Controller:**

```javascript
// backend/controllers/chat.controller.js (modified)

const sendMessage = async (req, res) => {
  const { message, customerId } = req.body;
  const user = req.user;

  const auth = new AuthorizationService(supabase);

  // Step 1: Can user access this business term?
  const extracted = extractBusinessTerm(message);  // "Revenue" from "What's our revenue?"
  
  const access = await auth.canAccessBusinessTerm(user.id, customerId, extracted.businessTerm);
  if (!access.allowed) {
    return res.status(403).json({ 
      error: `Access denied: ${access.reason}`,
      audit_logged: true,
    });
  }

  // Step 2: Resolve semantic definition
  const semantic = new SemanticLayer(supabase);
  const definition = await semantic.resolveBusinessTerm(customerId, extracted.businessTerm);

  // Step 3: Apply role-based filters
  const userFilters = await auth.applyRoleFilters(user.id, customerId, extracted.filters);

  // Step 4: Query SAP (only if authorized)
  const odata = new ODataClient(sapConfig);
  const results = await odata.queryCDSView(
    definition.cds_view,
    userFilters,  // Includes company_code and cost_center
    ["*"]
  );

  // ... rest of flow
};
```

**What to Keep from Current Code:**
- Middleware auth structure
- JWT validation pattern

**Dependencies:**
- Customer must define roles and which capabilities each role has
- Semantic layer (from Section 2.2)
- Audit infrastructure (see Section 3.2)

**Timeline:** 5 business days

**Definition of Done:**
- [ ] Role and user_role tables created
- [ ] AuthorizationService implemented
- [ ] Authorization check integrated into chat flow
- [ ] Role-based filters applied to queries
- [ ] Auth audit logging works
- [ ] Tests verify authorization blocks unauthorized access
- [ ] Tests verify authorized access succeeds

---

### 4.2 Compliance-Grade Audit Logging [Solves Gap 7]

**Problem:** Product has no audit trail; cannot prove who accessed what

**What to Build:**

Immutable audit log for compliance (SOX, GDPR):

**Database Schema:**

```sql
-- Core audit trail (immutable)
CREATE TABLE IF NOT EXISTS audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Identifiers (immutable)
  customer_id TEXT NOT NULL,
  user_id UUID REFERENCES users(id),
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- What happened
  action TEXT NOT NULL,  -- "QUERY", "AUTH_DENIED", "ROLE_ASSIGNED"
  business_term TEXT,  -- what they asked for
  
  -- Query details (if applicable)
  cds_views_queried TEXT[] DEFAULT '{}',
  filters_applied JSONB,
  result_row_count INTEGER,
  result_checksum TEXT,  -- for replay verification
  
  -- Execution details
  response_time_ms INTEGER,
  had_error BOOLEAN DEFAULT false,
  error_message TEXT,
  
  -- Data retention
  retention_until TIMESTAMPTZ,  -- when this log expires
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Authorization decisions (for compliance review)
CREATE TABLE IF NOT EXISTS auth_audit (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id TEXT NOT NULL,
  user_id UUID REFERENCES users(id),
  
  action TEXT NOT NULL,  -- "ALLOWED", "DENIED"
  business_term TEXT,
  reason TEXT,  -- why allowed or denied
  
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Data access patterns (for compliance trends)
CREATE TABLE IF NOT EXISTS data_access_summary (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id TEXT NOT NULL,
  
  -- Day-level aggregation
  access_date DATE NOT NULL,
  business_term TEXT NOT NULL,
  access_count INTEGER,
  unique_users INTEGER,
  total_rows_accessed BIGINT,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(customer_id, access_date, business_term)
);
```

**Audit Service:**

```javascript
// backend/services/audit.service.js

class AuditService {
  constructor(database) {
    this.db = database;
    this.retentionDays = 365;  // Keep logs for 1 year
  }

  // Log a query (core audit trail)
  async logQuery(customerId, userId, businessTerm, cdsViewsQueried, filtersApplied, resultCount, responseTimeMs, hadError, errorMsg) {
    const retentionUntil = new Date();
    retentionUntil.setDate(retentionUntil.getDate() + this.retentionDays);

    const checksum = this.calculateChecksum({ businessTerm, cdsViewsQueried, resultCount });

    await this.db
      .from('audit_log')
      .insert({
        customer_id: customerId,
        user_id: userId,
        action: 'QUERY',
        business_term: businessTerm,
        cds_views_queried: cdsViewsQueried,
        filters_applied: filtersApplied,
        result_row_count: resultCount,
        result_checksum: checksum,
        response_time_ms: responseTimeMs,
        had_error: hadError,
        error_message: errorMsg,
        retention_until: retentionUntil,
      });

    // Update daily summary
    await this.updateAccessSummary(customerId, businessTerm, 1, resultCount);
  }

  // Log authorization decision
  async logAuthDecision(customerId, userId, allowed, businessTerm, reason) {
    await this.db
      .from('auth_audit')
      .insert({
        customer_id: customerId,
        user_id: userId,
        action: allowed ? 'ALLOWED' : 'DENIED',
        business_term: businessTerm,
        reason,
      });
  }

  // Query audit log (for compliance review)
  async getAuditTrail(customerId, startDate, endDate, filters = {}) {
    let query = this.db
      .from('audit_log')
      .select('*')
      .eq('customer_id', customerId)
      .gte('timestamp', startDate)
      .lte('timestamp', endDate);

    if (filters.userId) query = query.eq('user_id', filters.userId);
    if (filters.businessTerm) query = query.eq('business_term', filters.businessTerm);
    if (filters.hadError !== undefined) query = query.eq('had_error', filters.hadError);

    return await query.order('timestamp', { ascending: true });
  }

  // Generate compliance report
  async generateComplianceReport(customerId, year) {
    const accessSummary = await this.db
      .from('data_access_summary')
      .select('*')
      .eq('customer_id', customerId)
      .gte('access_date', `${year}-01-01`)
      .lte('access_date', `${year}-12-31`)
      .order('access_date');

    const authSummary = await this.db
      .from('auth_audit')
      .select('action, COUNT(*)', { count: 'exact' })
      .eq('customer_id', customerId)
      .gte('timestamp', `${year}-01-01`)
      .lte('timestamp', `${year}-12-31`)
      .groupBy('action');

    return {
      year,
      data_access: accessSummary,
      auth_decisions: authSummary,
      generated_at: new Date().toISOString(),
    };
  }

  // Cleanup expired logs (retention policy)
  async cleanupExpiredLogs() {
    const now = new Date();
    await this.db
      .from('audit_log')
      .delete()
      .lte('retention_until', now);
  }

  calculateChecksum(data) {
    const crypto = require('crypto');
    return crypto
      .createHash('sha256')
      .update(JSON.stringify(data))
      .digest('hex');
  }

  async updateAccessSummary(customerId, businessTerm, accessCount, rowsAccessed) {
    const today = new Date().toISOString().split('T')[0];
    
    await this.db
      .from('data_access_summary')
      .upsert({
        customer_id: customerId,
        access_date: today,
        business_term: businessTerm,
        access_count: accessCount,
        total_rows_accessed: rowsAccessed,
      }, { onConflict: 'customer_id,access_date,business_term' });
  }
}
```

**Integration with Chat Controller:**

```javascript
// backend/controllers/chat.controller.js (modified)

const sendMessage = async (req, res) => {
  const startTime = Date.now();
  const { message, customerId } = req.body;
  const user = req.user;

  const audit = new AuditService(supabase);

  try {
    // ... query execution logic ...

    const responseTime = Date.now() - startTime;
    
    // Log successful query
    await audit.logQuery(
      customerId,
      user.id,
      businessTerm,
      cdsViewsQueried,
      filtersApplied,
      resultCount,
      responseTime,
      false,
      null
    );

    res.json({ answer, explanation });
  } catch (error) {
    const responseTime = Date.now() - startTime;

    // Log failed query
    await audit.logQuery(
      customerId,
      user.id,
      businessTerm,
      [],  // Don't log which views (didn't get far)
      {},  // Don't log filters
      0,
      responseTime,
      true,
      error.message
    );

    res.status(500).json({ error: error.message });
  }
};
```

**Admin Endpoint for Compliance Review:**

```javascript
// backend/routes/admin.routes.js (add endpoint)

router.get('/compliance-report/:customerId/:year', requireAdmin, async (req, res) => {
  const { customerId, year } = req.params;
  const audit = new AuditService(supabase);

  const report = await audit.generateComplianceReport(customerId, parseInt(year));
  res.json(report);
});

router.get('/audit-trail/:customerId', requireAdmin, async (req, res) => {
  const { customerId } = req.params;
  const { startDate, endDate, userId } = req.query;

  const audit = new AuditService(supabase);
  const trail = await audit.getAuditTrail(
    customerId,
    new Date(startDate),
    new Date(endDate),
    { userId }
  );

  res.json(trail);
});
```

**What to Keep from Current Code:**
- Query logging pattern (analytics service)
- Database structure (extend)

**Dependencies:**
- None (can be built independently)

**Timeline:** 4 business days

**Definition of Done:**
- [ ] Audit tables created
- [ ] AuditService implemented
- [ ] Logging integrated into chat flow
- [ ] Compliance report generation works
- [ ] Can query audit trail by date/user/term
- [ ] Retention policy implemented
- [ ] Tests pass

---

## SECTION 5: PHASE 3 — EXPLAINABILITY & CONFIGURATION (Weeks 7-8)

**Data lineage tracking and per-customer configuration framework.**

### 5.1 Explainability Layer [Solves Gap 6]

**Problem:** User gets answer but cannot verify it came from the right source

**What to Build:**

Complete data lineage and result explanation:

**Response Structure:**

```javascript
// Every response includes explanation
{
  answer: "$47.2M",
  
  // Data lineage
  explanation: {
    business_term: "Revenue",
    definition: "Amount recognized as income from sales",
    
    // Which CDS Views were queried
    sources: [
      {
        cds_view: "C_SalesOrdersMatched",
        rows_returned: 1200,
        row_sample: [
          { document_number: "SO-001", amount: 50000 },
          { document_number: "SO-002", amount: 75000 },
          // ...
        ]
      },
      {
        cds_view: "C_GeneralLedger",
        rows_returned: 340,
        row_sample: [
          // ...
        ]
      }
    ],
    
    // Which filters were applied (user-requested)
    user_filters: [
      { field: "posting_date", op: ">=", value: "2026-07-01" },
      { field: "posting_date", op: "<=", value: "2026-09-30" }
    ],
    
    // Which filters were applied (system-enforced)
    system_filters: [
      { field: "company_code", op: "=", value: "1000", reason: "user's company code" },
      { field: "document_status", op: "!=", value: "REVERSED", reason: "filter out reversals" }
    ],
    
    // Calculation explanation
    calculation: {
      raw_sum: 2500000,
      reversals_excluded: -150000,
      adjustments: -9500,
      final_total: 2340500,
      rounding_adjustment: 0,
    },
    
    // Confidence and verification
    confidence: "HIGH",
    can_replay: true,  // User can re-run exact query in SAP
    verify_in_sap: "Query C_SalesOrdersMatched with same filters in SAP GL",
    
    // Metadata
    queried_at: "2026-05-29T14:32:15Z",
    execution_time_ms: 245,
    rows_examined: 3400,
  }
}
```

**Service Implementation:**

```javascript
// backend/services/explainability.service.js

class ExplainabilityService {
  constructor(semanticLayer, odata) {
    this.semantic = semanticLayer;
    this.odata = odata;
  }

  // Build complete explanation for a query
  async buildExplanation(customerId, businessTerm, cdsViewsQueried, filtersApplied, results, executionTimeMs) {
    // Get semantic definition
    const definition = await this.semantic.resolveBusinessTerm(customerId, businessTerm);

    // Extract what user asked for vs what system enforced
    const { userFilters, systemFilters } = this.separateFilters(filtersApplied);

    // Get sample rows from results
    const rowSample = results.slice(0, 3).map(row => 
      Object.entries(row).reduce((acc, [k, v]) => {
        // Only include key columns (document_number, amount, date)
        if (['DOCUMENT_NUMBER', 'AMOUNT', 'POSTING_DATE', 'COMPANY_CODE'].includes(k)) {
          acc[k] = v;
        }
        return acc;
      }, {})
    );

    // Build calculation explanation (if applicable)
    const calculationExplanation = this.explainCalculation(definition.calculation, results);

    return {
      business_term: businessTerm,
      definition: definition.definition,
      
      sources: cdsViewsQueried.map(view => ({
        cds_view: view,
        rows_returned: results.length,
        row_sample: rowSample,
      })),
      
      user_filters: userFilters,
      system_filters: systemFilters,
      
      calculation: calculationExplanation,
      
      confidence: this.calculateConfidence(results.length),
      can_replay: true,
      verify_in_sap: this.buildSAPVerificationSteps(definition, filtersApplied),
      
      queried_at: new Date().toISOString(),
      execution_time_ms: executionTimeMs,
      rows_examined: results.length,
    };
  }

  // Separate user-requested filters from system-enforced filters
  separateFilters(filtersApplied) {
    // System-enforced: company_code, cost_center, department
    const systemFilters = [];
    const userFilters = [];

    Object.entries(filtersApplied).forEach(([key, value]) => {
      if (['company_code', 'cost_center', 'department'].includes(key)) {
        systemFilters.push({
          field: key,
          op: '=',
          value,
          reason: `system-enforced (${key} restriction)`
        });
      } else {
        userFilters.push({
          field: key,
          op: 'varies',  // Would parse from OData query
          value
        });
      }
    });

    return { userFilters, systemFilters };
  }

  // Explain calculation (if it's a metric like Days Sales Outstanding)
  explainCalculation(calculation, results) {
    // If calculation is simple SUM
    if (calculation === 'SUM(Amount)') {
      const total = results.reduce((sum, row) => sum + (row.AMOUNT || 0), 0);
      return {
        raw_sum: total,
        reversals_excluded: 0,  // Could parse this from filters
        adjustments: 0,
        final_total: total,
      };
    }

    // For complex calculations, return the formula
    return {
      formula: calculation,
      note: 'Complex calculation; refer to semantic definition'
    };
  }

  // Calculate confidence in answer
  calculateConfidence(rowCount) {
    if (rowCount === 0) return 'MEDIUM';  // No data; maybe expected?
    if (rowCount > 1000) return 'HIGH';   // Large dataset
    if (rowCount > 100) return 'HIGH';
    if (rowCount > 10) return 'MEDIUM';
    return 'LOW';  // Very few rows
  }

  // Build step-by-step verification in SAP
  buildSAPVerificationSteps(definition, filtersApplied) {
    return `
1. Open SAP Fiori app for ${definition.primary_cds_view}
2. Apply filters:
   ${Object.entries(filtersApplied).map(([k, v]) => `   - ${k} = ${v}`).join('\n')}
3. View results
4. Compare totals to this report
    `.trim();
  }
}
```

**Integration:**

```javascript
// backend/controllers/chat.controller.js (modified)

const sendMessage = async (req, res) => {
  // ... query execution ...

  const explainability = new ExplainabilityService(semantic, odata);

  const explanation = await explainability.buildExplanation(
    customerId,
    businessTerm,
    cdsViewsQueried,
    filtersApplied,
    results,
    responseTimeMs
  );

  res.json({
    answer: finalAnswer,
    explanation,
  });
};
```

**Timeline:** 4 business days

**Definition of Done:**
- [ ] ExplainabilityService implemented
- [ ] Response structure includes full explanation
- [ ] Row samples are included
- [ ] Filter separation (user vs system) works
- [ ] Calculation explanation works
- [ ] SAP verification steps are generated
- [ ] Tests pass

---

### 5.2 Customer Configuration Framework (V1 Focused) [Solves Gap 8]

**Problem:** Cannot support Customer #2 without hardcoding their custom configurations

**Important:** V1 focuses on supporting ONE customer successfully. We optimize for Customer #1's success, not Customer #50's infrastructure.

**What to Build (V1 Scope):**

Configuration system for Customer #1:

**Database Schema (Simplified for V1):**

```sql
-- Customer-specific configuration
CREATE TABLE IF NOT EXISTS customer_config (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id TEXT UNIQUE NOT NULL,
  
  -- Basic customer info
  sap_system_id TEXT,
  company_codes TEXT[] NOT NULL,
  cost_centers TEXT[] DEFAULT '{}',
  
  -- SAP connectivity
  odata_endpoint TEXT NOT NULL,
  auth_type TEXT,
  
  -- Created
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Customer's semantic layer (from metadata registry discovery)
CREATE TABLE IF NOT EXISTS customer_semantics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id TEXT NOT NULL,
  
  -- Semantic definitions (loaded from metadata registry + customer glossary)
  definitions JSONB NOT NULL,  -- [{business_term, cds_view, filters, ...}]
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Customer's roles
CREATE TABLE IF NOT EXISTS customer_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id TEXT NOT NULL,
  role_name TEXT NOT NULL,
  capabilities JSONB NOT NULL,  -- ["Revenue", "Expense", ...]
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(customer_id, role_name)
);
```

**Configuration Service (V1):**

```javascript
// backend/services/customer-config.service.js

class CustomerConfigService {
  constructor(database, metadataRegistry) {
    this.db = database;
    this.metadata = metadataRegistry;
    this.configCache = new Map();
  }

  // Load customer configuration
  async loadCustomerConfig(customerId) {
    if (this.configCache.has(customerId)) {
      return this.configCache.get(customerId);
    }

    const config = await this.db
      .from('customer_config')
      .select('*')
      .eq('customer_id', customerId)
      .single();

    const semantics = await this.db
      .from('customer_semantics')
      .select('definitions')
      .eq('customer_id', customerId)
      .single();

    const roles = await this.db
      .from('customer_roles')
      .select('*')
      .eq('customer_id', customerId);

    const fullConfig = {
      customer: config,
      semantics: semantics?.definitions || [],
      roles: roles.reduce((acc, role) => {
        acc[role.role_name] = role.capabilities;
        return acc;
      }, {}),
    };

    this.configCache.set(customerId, fullConfig);
    return fullConfig;
  }

  // Setup customer (from metadata registry + glossary)
  async setupCustomer(customerId, customerData) {
    // Step 1: Store config
    await this.db
      .from('customer_config')
      .insert({
        customer_id: customerId,
        sap_system_id: customerData.sap_system_id,
        company_codes: customerData.company_codes,
        odata_endpoint: customerData.odata_endpoint,
      });

    // Step 2: Store semantics (from metadata registry discovery)
    const semantics = await this.metadata.generateSemanticDefinitions(customerId);
    await this.db
      .from('customer_semantics')
      .insert({
        customer_id: customerId,
        definitions: semantics,
      });

    // Step 3: Store roles
    for (const role of customerData.roles) {
      await this.db
        .from('customer_roles')
        .insert({
          customer_id: customerId,
          role_name: role.role_name,
          capabilities: role.capabilities,
        });
    }

    this.configCache.delete(customerId);
    console.log(`✓ Customer ${customerId} configuration loaded`);
  }
}
```

**V1 Implementation Reality:**

For Customer #1, the workflow is:
1. Run SAP metadata discovery (Phase 0)
2. Customer validates business glossary
3. Admin runs setupCustomer() once
4. System is configured

For Customer #2 (future):
- Repeat process with their metadata and glossary
- Possibly export/import if similarity exists
- But assume custom work needed

**V1 Does NOT include:**
- Advanced onboarding engines
- Sophisticated customer lifecycle tooling
- Versioned configuration platforms
- Multi-customer metadata sharing
- Automatic customer migration tools
- Customer self-service portals

**These are V2+ features.** Focus on Customer #1's success first.

**Why:** Premature optimization for Customer #50 delays Customer #1 launch. Better to ship Customer #1, then learn what Customer #2 needs.

**Timeline:** 2 business days (greatly simplified from original)

**Definition of Done:**
- [ ] Configuration tables created
- [ ] CustomerConfigService implemented
- [ ] Can load full customer config
- [ ] Onboarding endpoint works
- [ ] Can update semantic definitions (versioned)
- [ ] Configuration caching works
- [ ] Tests pass

---

## SECTION 6: PHASE 4 — DEPLOYMENT (Week 9)

**Docker containerization and on-premise deployment setup.**

### 6.1 Docker Containerization [Solves Gap 5]

**What to Build:**

Docker containers for on-premise deployment:

**Dockerfile (Backend):**

```dockerfile
# backend/Dockerfile

FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (production only)
RUN npm ci --only=production

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:5000/api/health', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Start application
CMD ["npm", "run", "start"]
```

**Dockerfile (Frontend):**

```dockerfile
# frontend/Dockerfile

FROM node:18-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Build React app
RUN npm run build

# Production image
FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html

# Nginx config for SPA
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - NODE_ENV=production
      - PORT=5000
      - JWT_SECRET=${JWT_SECRET}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - FRONTEND_URL=http://localhost:3000
      - LOG_LEVEL=info
    depends_on:
      - postgres
      - redis
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://localhost:5000/api
    depends_on:
      - backend
    restart: always

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=sap_intelligence
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
      - ./database/migration_add_message_embeddings.sql:/docker-entrypoint-initdb.d/02-migrations.sql
    ports:
      - "5432:5432"
    restart: always

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: always

volumes:
  postgres_data:
  redis_data:
```

**Deployment Instructions:**

```markdown
# ON-PREMISE DEPLOYMENT

## Prerequisites
- Docker and Docker Compose installed
- SAP OData endpoint accessible from deployment environment
- SSL certificate for HTTPS

## Steps

1. Clone repository
   git clone <repo>
   cd sap-intelligence-platform

2. Create .env file
   cp .env.example .env
   # Edit with customer's values:
   # - JWT_SECRET
   # - SAP OData endpoint
   # - SUPABASE_URL (if using managed) or local PostgreSQL

3. Start services
   docker-compose up -d

4. Verify deployment
   curl http://localhost:5000/api/health

5. Access dashboard
   Open browser: http://localhost:3000

6. Configure customer
   POST /api/admin/onboard-customer with customer config

7. Verify SAP connectivity
   POST /api/sap/test-connection

8. Setup SSL (production)
   Use nginx reverse proxy with Let's Encrypt

9. Backup
   docker exec postgres pg_dump -U postgres sap_intelligence > backup.sql

10. Upgrade
    git pull
    docker-compose down
    docker-compose up --build
```

**Timeline:** 3 business days

**Definition of Done:**
- [ ] Backend Dockerfile builds and runs
- [ ] Frontend Dockerfile builds and runs
- [ ] docker-compose.yml works end-to-end
- [ ] Health checks pass
- [ ] Can deploy locally; can deploy to customer machine
- [ ] Documentation complete

---

## SECTION 7: PHASE 5 — VALIDATION & ITERATION (Weeks 12+)

**Integration testing, performance validation, and fixes.**

### 7.1 Integration Testing

**Test coverage needed:**

```javascript
// Test: End-to-end query flow
describe('End-to-End Query Flow', () => {
  it('should execute complete query from user input to response', async () => {
    // 1. User asks: "What's our Q3 revenue?"
    const query = "What's our Q3 revenue?";
    
    // 2. Extract business term: "Revenue"
    const term = extractBusinessTerm(query);
    expect(term).toBe("Revenue");
    
    // 3. Check authorization
    const authorized = await authService.canAccessBusinessTerm(user.id, customerId, term);
    expect(authorized.allowed).toBe(true);
    
    // 4. Resolve semantic definition
    const definition = await semanticLayer.resolveBusinessTerm(customerId, term);
    expect(definition.cds_view).toBe("C_SalesOrdersMatched");
    
    // 5. Apply role-based filters
    const filters = await authService.applyRoleFilters(user.id, customerId, {});
    expect(filters.company_code).toBe("1000");
    
    // 6. Query SAP
    const results = await odata.queryCDSView(definition.cds_view, filters, ["*"]);
    expect(results.length).toBeGreaterThan(0);
    
    // 7. Build explanation
    const explanation = await explainability.buildExplanation(
      customerId, term, [definition.cds_view], filters, results, 100
    );
    expect(explanation.sources).toBeDefined();
    
    // 8. Log to audit
    await audit.logQuery(user.id, customerId, term, [definition.cds_view], filters, results.length, 100, false, null);
    
    // 9. Verify audit log
    const auditTrail = await audit.getAuditTrail(customerId, startDate, endDate);
    expect(auditTrail.some(log => log.business_term === "Revenue")).toBe(true);
  });
});

// Test: Authorization blocking
describe('Authorization Blocking', () => {
  it('should deny query for unauthorized business term', async () => {
    const user = { role: "Procurement Manager" };  // Cannot see Finance terms
    
    const result = await authService.canAccessBusinessTerm(user.id, customerId, "AR_Aging");
    expect(result.allowed).toBe(false);
    
    // Verify auth audit log
    const authLog = await audit.db.from('auth_audit').select('*').eq('action', 'DENIED').limit(1);
    expect(authLog.length).toBeGreaterThan(0);
  });
});

// Test: Semantic layer resolution
describe('Semantic Layer Resolution', () => {
  it('should resolve customer-specific semantic definitions', async () => {
    // Customer A
    const revA = await semantic.resolveBusinessTerm("CustomerA", "Revenue");
    expect(revA.cds_view).toBe("C_SalesOrdersMatched");
    
    // Customer B (different custom view)
    const revB = await semantic.resolveBusinessTerm("CustomerB", "Revenue");
    expect(revB.cds_view).toBe("Z_RevenueCustom");
  });
});

// Test: Explainability
describe('Explainability', () => {
  it('should provide complete lineage for query results', async () => {
    const results = [{ AMOUNT: 50000 }, { AMOUNT: 75000 }];
    
    const explanation = await explainability.buildExplanation(
      customerId,
      "Revenue",
      ["C_SalesOrdersMatched"],
      { company_code: "1000" },
      results,
      150
    );
    
    expect(explanation.sources[0].cds_view).toBe("C_SalesOrdersMatched");
    expect(explanation.system_filters.length).toBeGreaterThan(0);
    expect(explanation.row_sample.length).toBeGreaterThan(0);
  });
});
```

**Timeline:** 5 business days

---

### 7.2 Performance Validation

**What to test:**

```javascript
// Performance: Query response time
describe('Performance', () => {
  it('should respond to queries in < 5 seconds', async () => {
    const start = Date.now();
    const result = await sendQuery("What's our Q3 revenue?");
    const duration = Date.now() - start;
    
    expect(duration).toBeLessThan(5000);
  });

  it('should handle 20 concurrent users', async () => {
    const promises = [];
    for (let i = 0; i < 20; i++) {
      promises.push(sendQuery(`Query ${i}`));
    }
    
    const results = await Promise.allSettled(promises);
    const successful = results.filter(r => r.status === 'fulfilled').length;
    
    expect(successful).toBeGreaterThan(18);  // 90% success rate
  });

  it('should handle large result sets (10k+ rows)', async () => {
    // Query that returns many rows
    const result = await odata.queryCDSView("C_SalesOrdersMatched", {}, ["*"]);
    expect(result.length).toBeGreaterThan(10000);
    
    // Should handle pagination
    expect(result).toBeDefined();
  });
});
```

**Timeline:** 3 business days

---

## SECTION 8: V1 NON-GOALS — WHAT WE ARE EXPLICITLY NOT BUILDING

The following capabilities are intentionally excluded from V1. This document does not preclude them for V2+; they are simply out of scope for achieving reliable first customer deployment.

### 8.1 SAP Write-Back Actions

**Why excluded:** V1 is read-only intelligence. Writing to SAP introduces data integrity risk and requires extensive testing.

**When to reconsider:** After successful read-only deployments at 2-3 customers; if demand for write operations is clear.

---

### 8.2 Autonomous Agents

**Why excluded:** Autonomous agents (agents that execute decisions without human review) require extensive safety testing and governance.

**Current approach:** AI acts as copilot (advisor), not autonomous actor. Humans make decisions.

**When to reconsider:** After establishing audit trail + explainability + governance; requires separate GRC review.

---

### 8.3 Multi-Agent Systems

**Why excluded:** Multiple agents introduce orchestration complexity and failure modes.

**Current approach:** Single copilot agent per user session. Sequential reasoning, not multi-agent reasoning.

**When to reconsider:** After proving single-agent reliability at scale.

---

### 8.4 Self-Learning Systems

**Why excluded:** Systems that learn and modify their behavior require extensive validation, audit trails, and governance.

**Current approach:** Static semantic layer + static AI models. All learning is through explicit configuration updates, reviewed and approved.

**When to reconsider:** After establishing strong governance framework; requires data science + compliance team.

---

### 8.5 Automatic Model Retraining

**Why excluded:** Automatic retraining introduces risk of model degradation without human oversight.

**Current approach:** Use proven pre-trained models. If fine-tuning is needed, it is manual and reviewed.

**When to reconsider:** After V1 validates which models need retraining; requires model monitoring + retraining governance.

---

### 8.6 Advanced Workflow Automation

**Why excluded:** Sophisticated workflows (multi-step approvals, conditional routing, etc.) add complexity.

**Current approach:** Simple linear queries. Approvals (if needed) are explicit checkpoints, not automated routing.

**When to reconsider:** After Customer #1 identifies specific workflow needs.

---

### 8.7 Customer-to-Customer Multi-Tenancy

**Why excluded:** Sharing metadata, semantic layers, or configurations across customers creates security and customization risks.

**Current approach:** Per-customer deployment or strict per-customer data isolation. No cross-customer data sharing.

**When to reconsider:** After operating successfully with 5+ customers; requires strong isolation patterns.

---

### 8.8 Predictive AI Systems

**Why excluded:** Predictions (forecasts, anomaly detection, recommendations) require statistical validation and risk assessment.

**Current approach:** Descriptive analytics only. "What is our revenue?" not "What will revenue be?"

**When to reconsider:** After descriptive analytics is battle-tested; requires data scientist + governance.

---

### 8.9 Agent Swarms / Autonomous Swarms

**Why excluded:** Agent swarms (multiple agents coordinating) is advanced orchestration with high complexity and risk.

**Current approach:** Single copilot. No swarm coordination.

**When to reconsider:** Far future; only if clear business case emerges.

---

### 8.10 Autonomous Business Decision Making

**Why excluded:** The system cannot make business decisions autonomously. Humans always decide.

**Current approach:** System provides information and insights. Humans make decisions based on that information.

**Why permanent:** This is a design principle, not a V1 limitation. Autonomous decision-making in financial systems creates liability and compliance risks.

---

## SECTION 9: CRITICAL PATH & DEPENDENCIES (Updated)

**What must be built before what:**

```
Week 1-2: Product Validation (Immediate Actions)
├─ SAP expertise review
├─ Customer business interviews
├─ Deployment model confirmation
└─ Team skillset assessment

Week 1-2: SAP Discovery (Parallel with validation)
├─ Request CDS View inventory from customer
├─ Request authorization structure
└─ Run discovery interviews

Week 3-4: Phase 0 — Metadata Registry (depends on discovery data)
├─ Build metadata registry
├─ Import CDS Views
├─ Import field metadata
└─ Validate business glossary with customer

Week 5-6: Phase 1 — Foundation (depends on metadata registry)
├─ SAP OData Client (depends on discovery)
├─ Semantic Layer (depends on metadata registry + glossary)
└─ Initial Dashboard Shells (independent)

Week 7-8: Phase 2 — Authorization & Audit (depends on foundation)
├─ RBAC Layer (depends on OData + Semantic)
├─ Audit Logging (independent)
└─ Explainability (depends on above)

Week 9-10: Phase 3 — Configuration & Explainability (depends on above)
├─ Explainability Layer (depends on audit)
├─ Customer Configuration (depends on all above)
└─ Configuration endpoints

Week 11: Phase 4 — Deployment (depends on all above)
└─ Docker containerization

Week 12+: Validation (depends on deployment)
├─ Integration testing
├─ Performance validation
└─ Fixes based on findings
```

**Critical dependencies:**
1. **SAP metadata discovery MUST happen first** — Cannot build OData client without knowing what CDS Views exist
2. **Metadata registry MUST exist before semantic layer** — Semantic definitions must be based on discovered reality, not assumptions
3. **OData client MUST work before anything else** — No queries can execute without working SAP connectivity

---

## SECTION 10: SUCCESS CRITERIA BY PHASE

### Phase 0 (End of Week 2)

- [ ] CDS Views catalog created and populated
- [ ] Field metadata documented
- [ ] Business glossary created (8+ items)
- [ ] Customer validated business term mappings
- [ ] Discovery report generated
- [ ] Tests pass

### Phase 1 (End of Week 4)

- [ ] Can list CDS Views from customer SAP
- [ ] Can execute parameterized OData queries
- [ ] Semantic layer stores business term definitions
- [ ] Dashboard shells render with placeholder data
- [ ] Integration tests for OData client pass

### Phase 2 (End of Week 6)

- [ ] Authorization checks prevent unauthorized access
- [ ] Audit logs record every query
- [ ] Auth denied queries are logged
- [ ] Explainability provides lineage
- [ ] Tests verify RBAC enforcement

### Phase 3 (End of Week 8)

- [ ] Per-customer configurations can be loaded
- [ ] Can onboard new customer without code changes
- [ ] Semantic definitions are customer-specific
- [ ] Tests pass

### Phase 4 (End of Week 9)

- [ ] Docker images build successfully
- [ ] docker-compose.yml deploys locally
- [ ] Can deploy to customer server
- [ ] Health checks pass
- [ ] Documentation complete

### Phase 5+ (Ongoing, Week 12+)

- [ ] 95% query success rate
- [ ] 99% of queries respond in < 5 seconds
- [ ] Zero authorization violations
- [ ] Audit trail 100% complete
- [ ] No data loss on deploy/restart

---

## SECTION 11: TEAM STRUCTURE & SKILLSET NEEDS

**Recommended team composition:**

| Role | Responsibilities | Days/Week | Critical? |
|------|---|---|---|
| SAP Architect | OData client, semantic layer validation, CDS View knowledge | 5 | 🔴 YES |
| Backend Lead | Architecture, integration, deployment | 5 | 🔴 YES |
| Frontend Lead | Dashboard, UI/UX, responsiveness | 4 | 🟡 MEDIUM |
| Database/DevOps | Schema, Docker, migrations, on-prem setup | 3 | 🟡 MEDIUM |
| QA/Test | Integration tests, performance testing, validation | 3 | 🟡 MEDIUM |

**Technical Validation Requirements:** If team lacks SAP expertise, internal expert review or customer SAP team validation is required for Weeks 1-2 (discovery phase).

---

## SECTION 12: RISK MITIGATION

**If things go wrong:**

### Risk: SAP Connectivity Fails

**Mitigation:**
- Day 7: Build hello-world OData client and test against customer SAP
- If fails: Pivot immediately; notify leadership

### Risk: Semantic Layer Design Is Wrong

**Mitigation:**
- Week 2: Customer stakeholder review of semantic definitions
- If wrong: Iterate; don't proceed to Phase 2 until validated

### Risk: Authorization Implementation Allows Data Leakage

**Mitigation:**
- Week 4: Security audit of authorization logic
- Write tests that verify authorization blocks unauthorized access
- If fails: Fix before proceeding to Phase 4

### Risk: Docker Deployment Fails

**Mitigation:**
- Week 7: Test deployment locally before deploying anywhere
- Have rollback procedure (git checkout, redeploy)

---

## SECTION 13: FILE STRUCTURE AFTER IMPLEMENTATION

```
backend/
├── services/
│   ├── sap/
│   │   └── odata-client.js              [New - Phase 1]
│   │   └── odata-cache.js               [New - Phase 1]
│   ├── semantic-layer.service.js        [New - Phase 1]
│   ├── authorization.service.js         [New - Phase 2]
│   ├── audit.service.js                 [New - Phase 2]
│   ├── explainability.service.js        [New - Phase 3]
│   ├── customer-config.service.js       [New - Phase 3]
│   ├── chat.service.js                  [Refactor - remove generic DB]
│   └── [existing services unchanged]
│
├── routes/
│   ├── sap.routes.js                    [New - Phase 1]
│   ├── dashboard.routes.js              [New - Phase 1]
│   ├── admin.routes.js                  [Refactor - add endpoints]
│   └── [existing routes mostly unchanged]
│
├── middleware/
│   ├── authorization.js                 [New - Phase 2]
│   └── [existing middleware unchanged]
│
├── Dockerfile                           [New - Phase 4]
└── docker-compose.yml                   [New - Phase 4]

frontend/
├── src/
│   ├── pages/
│   │   ├── DashboardPage.jsx            [New - Phase 1]
│   │   ├── dashboards/
│   │   │   ├── ExecutiveDashboard.jsx   [New - Phase 1]
│   │   │   ├── FinanceDashboard.jsx     [New - Phase 1]
│   │   │   └── ProcurementDashboard.jsx [New - Phase 1]
│   │   └── [existing pages unchanged]
│   │
│   └── [components restructured for dashboard-first]
│
├── Dockerfile                           [New - Phase 4]
└── nginx.conf                           [New - Phase 4]

database/
├── schema.sql                           [Extend - add new tables]
├── migrations/
│   ├── 01-semantic-layer.sql            [New - Phase 1]
│   ├── 02-authorization-rbac.sql        [New - Phase 2]
│   ├── 03-audit-logging.sql             [New - Phase 2]
│   ├── 04-customer-config.sql           [New - Phase 3]
│   └── 05-explainability.sql            [New - Phase 3]
└── [existing schemas mostly kept]

docker-compose.yml                       [New - Phase 4]
.env.example                             [Update - add new env vars]
DEPLOYMENT_GUIDE.md                      [New - Phase 4]
SEMANTIC_LAYER_GUIDE.md                  [New - Phase 1]
```

---

**Document Complete**

This blueprint translates the Production Gap Analysis findings into concrete development work. Every section is traceable to a gap identified in the gap analysis.

**Next steps:** Leadership reviews and validates direction. Team begins Phase 1 work.
