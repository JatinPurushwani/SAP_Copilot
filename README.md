# Multi-AI Chat Platform & SAP Intelligence Platform Evolution

## 🎯 Quick Context

This repository is evolving from a **Multi-AI Chat Platform** into a **SAP Enterprise Intelligence Platform**.

**Current State:** Production chatbot system (198 unit tests, Vercel deployed, Supabase-backed)  
**Future Direction:** On-premise SAP S/4HANA intelligence platform with dashboard-first UX and AI copilot  
**Timeline:** Phase 0-5 over 12+ weeks (see [IMPLEMENTATION_BLUEPRINT.md](IMPLEMENTATION_BLUEPRINT.md))

---

## 🚀 Getting Started (Choose Your Path)

### Path A: Understanding the Current Repository

**"I need to work on the existing chatbot system"**

1. Read → [docs/current-repo/DEVELOPER_QUICKSTART.md](docs/current-repo/DEVELOPER_QUICKSTART.md) (10 min setup)
2. Reference → [docs/current-repo/GUIDE.md](docs/current-repo/GUIDE.md) (deployment)
3. Deep dive → [docs/current-repo/TECH_DOC.md](docs/current-repo/TECH_DOC.md) (architecture)

### Path B: Understanding the Future Product

**"I need to understand the SAP platform direction"**

1. Read → [PROD_GAP_ANALYSIS.md](PROD_GAP_ANALYSIS.md) (strategic context: why we're pivoting)
2. Read → [IMPLEMENTATION_BLUEPRINT.md](IMPLEMENTATION_BLUEPRINT.md) (detailed roadmap)
3. Start → Implementation Phase 0 activities

### Path C: New Developer - Uncertain Where To Start

1. You're reading this ← Start here
2. Read → [PROD_GAP_ANALYSIS.md](PROD_GAP_ANALYSIS.md) (3 min: understand the story)
3. Decide: Are you working on current repo or future product?
4. Follow Path A or Path B above

### Path D: Deep Technical Questions

**"I need architecture details"**

**Current Repository:**
→ [docs/current-repo/FORENSIC_ANALYSIS.md](docs/current-repo/FORENSIC_ANALYSIS.md) (51KB complete reconstruction)

**Future Product:**
→ [IMPLEMENTATION_BLUEPRINT.md](IMPLEMENTATION_BLUEPRINT.md) (code examples, database schemas, service definitions)

---

## 📚 Complete Documentation Map

### Strategic Documents (Root Level)

| Document | Purpose | Read When | Time |
|----------|---------|-----------|------|
| [PROD_GAP_ANALYSIS.md](PROD_GAP_ANALYSIS.md) | Why are we shifting from chatbot to SAP platform? | First time understanding direction | 15 min |
| [IMPLEMENTATION_BLUEPRINT.md](IMPLEMENTATION_BLUEPRINT.md) | How will we build the SAP platform? What phases? What timeline? | Planning development work | 30 min |

### Current Repository Documentation

All located in `docs/current-repo/` — describing the Multi-AI Chat Platform that is currently production:

| Document | Purpose | Audience | Read When |
|----------|---------|----------|-----------|
| [docs/current-repo/DEVELOPER_QUICKSTART.md](docs/current-repo/DEVELOPER_QUICKSTART.md) | Get the current system running in 10 minutes | New devs working on chatbot | First day |
| [docs/current-repo/GUIDE.md](docs/current-repo/GUIDE.md) | Implement features, deploy, configure the current system | Developers building on chatbot | Daily reference |
| [docs/current-repo/TECH_DOC.md](docs/current-repo/TECH_DOC.md) | Technical architecture: services, database, deployment | Architects, senior engineers | Deep dives |
| [docs/current-repo/TESTING.md](docs/current-repo/TESTING.md) | Testing strategy, regression checklist, validation | QA, developers | Test planning |
| [docs/current-repo/FORENSIC_ANALYSIS.md](docs/current-repo/FORENSIC_ANALYSIS.md) | Complete deep-dive: 16+ services, execution flow, risks | Platform owners, architects | Understanding complexity |
| [docs/current-repo/TAKEOVER_STRATEGY.md](docs/current-repo/TAKEOVER_STRATEGY.md) | 90-day plan to own & stabilize the chatbot system | New platform owner | Operational handoff |
| [docs/current-repo/MANAGEMENT_PRESENTATION.md](docs/current-repo/MANAGEMENT_PRESENTATION.md) | Executive summary: business value, risks, monitoring | Leadership, product managers | Context |

### Archive (Historical Reference)

Located in `docs/archive/` — kept for navigation and historical context:

| Document | Purpose | Read When |
|----------|---------|-----------|
| [docs/archive/ANALYSIS_INDEX.md](docs/archive/ANALYSIS_INDEX.md) | Original index to analysis documents | Rarely; historical navigation |

---

## 🔄 Project Status

### Current System (Production)

- ✅ Chat-first UX with 15 AI models
- ✅ RAG (retrieval-augmented generation)
- ✅ Semantic caching and token budgeting
- ✅ Authentication and anonymous mode
- ✅ Admin dashboard
- ✅ Supabase + Vercel deployment

**Status:** Operational. Maintenance-focused.

### Future Direction (Development Planning)

- 🔨 SAP S/4HANA integration via OData
- 🔨 Dashboard-first UX with AI copilot sidebar
- 🔨 Semantic layer (business terms → CDS Views)
- 🔨 Role-based access control (RBAC)
- 🔨 Explainability and audit trails
- 🔨 On-premise deployment (Docker)

**Status:** Phase 0 starting. See [IMPLEMENTATION_BLUEPRINT.md](IMPLEMENTATION_BLUEPRINT.md) for roadmap.

---

## ✋ Important Notes

### Both Product Directions Are Active

This repository contains two valuable directions:
1. **Current production system** (chatbot) — stable, tested, deployed
2. **Future system** (SAP platform) — planned, under development

Both are real. Both matter. The documentation reflects both.

### Why Keep Current-Repo Documentation?

The current repository is **not being deleted or deprecated**. It remains in active maintenance until the SAP platform is mature. The documents describe real, running production code:
- 198 unit tests are actually executing
- The architecture is actually deployed on Vercel + Supabase
- Developers are actually using these guides

**Therefore:** Current-repo documentation is archived in `docs/current-repo/` not because it's outdated, but because it's **specific to the current system** and **should not be confused with the future product direction**.

### How to Avoid Confusion

- **Root level documents** = Strategic & future-facing
- **docs/current-repo/** = Current system only
- **docs/archive/** = Historical navigation
- **This README** = Explains all of the above

---

## 🤝 Getting Help

- **Architecture questions:** [docs/current-repo/TECH_DOC.md](docs/current-repo/TECH_DOC.md) (current) or [IMPLEMENTATION_BLUEPRINT.md](IMPLEMENTATION_BLUEPRINT.md) (future)
- **Testing questions:** [docs/current-repo/TESTING.md](docs/current-repo/TESTING.md)
- **Deployment questions:** [docs/current-repo/GUIDE.md](docs/current-repo/GUIDE.md) (current) or Phase 4 of [IMPLEMENTATION_BLUEPRINT.md](IMPLEMENTATION_BLUEPRINT.md) (future)
- **Why are we changing?** [PROD_GAP_ANALYSIS.md](PROD_GAP_ANALYSIS.md)

---

## Current Repository Details

### Multi-AI Chat

Unified AI chat platform with authentication, anonymous mode, file-aware chat (RAG), streaming responses, token controls, and admin analytics. Now includes a **complete LangChain + LangGraph + LangSmith equivalent** framework built from scratch.

### Current Scope

- Frontend: React (`frontend/`)
- Backend: Express API (`backend/`)
- Database: Supabase PostgreSQL + `pgvector` (`database/`)
- Deployment target: Vercel (frontend + backend)

### Core Capabilities

- Model routing via `backend/config/models.js` (current configured registry)
- Live provider model discovery for `openrouter`, `together`, `anyapi`
- Chat endpoints: `/api/chat/message` and `/api/chat/stream` (SSE)
- Authenticated and anonymous chat flows
- Semantic query cache, RAG context, history summarization, cross-chat memory
- File upload/search integration
- Admin panel (users, quotas, analytics)
- Theme toggle and finance route in frontend
- Sentry integration (frontend + backend)

### AI Framework (Custom LangChain + LangGraph + LangSmith)

Complete ecosystem of 16+ microservices providing production-ready AI orchestration:

#### Core Services
- **Document Loaders** — Load 40+ file formats (PDF, Word, Excel, Code, Images, Archives)
- **Text Splitters** — 4 intelligent chunking strategies (recursive, semantic, sliding window, line-based)
- **Vector Stores** — Multiple backends (PgVector, In-Memory, Hybrid) with unified interface
- **Output Parsers** — 5 types (JSON, Markdown, CSV, Regex, Composite)
- **Chains** — 6 types (Simple, Conditional, Parallel, Composer, Map, Loop)
- **Agents** — ReAct pattern with dynamic tool selection and multi-turn reasoning
- **Callbacks** — Lifecycle hooks for monitoring, cost tracking, metrics, errors

#### Advanced Services
- **Retrievers** — 6 search strategies (Vector, BM25, Hybrid, Metadata, Reranker, Chained)
- **Prompt Templates** — 8 types (Basic, FewShot, Chat, Conditional, Formatted, Role, Loop, Composer)
- **Memory** — 6 in-process strategies (Buffer, Summary, Entity, TokenBuffer, Window, Combined) + cross-chat RAG memory (`embedAndStoreMessage`, `searchMemory`)
- **Graph Workflows** — DAG-based execution with conditional routing and state management
- **Human-in-the-Loop** — Approval checkpoints with state snapshots and audit trails
- **Loop Management** — Cycle control (RefinementLoop, QueryLoop, ValidationLoop, PipelineLoop)

#### Orchestration & Intelligence
- **Agent Orchestrator** — SmartAgent with dynamic tool selection, auto-looping, and refinement
- **ReAct Pattern** — Structured reasoning with thought-action-observation cycles
- **Multi-Agent** — AgentOrchestrator for coordinating multiple agents

#### Observability & Analysis
- **Execution Tracer** — Complete step-by-step execution tracing with hierarchical nesting; wired into Agent and SmartAgent tool/LLM calls
- **Flow Visibility** — Variable tracking, state diffing, dependency analysis
- **Flow Analyzer** — Critical path, bottleneck detection, cycle detection, parallelization opportunities
- **Flow Visualizer** — Mermaid diagrams (sequence, flowchart, state), heat maps, dependency graphs
- **Flow Debugger** — Step-through debugging with breakpoints and variable watches
- **Flow Dashboard** — Real-time metrics and performance dashboards
- **Flow Optimizer** — Automatic optimization suggestions

---

## Quick Start

```bash
cd backend
npm install
cp .env.example .env
npm run dev
```

```bash
cd frontend
npm install
cp .env.example .env.local
npm start
```

Frontend expects `REACT_APP_API_URL`; backend expects `JWT_SECRET`, `SUPABASE_URL`, and `SUPABASE_SERVICE_KEY` at minimum.

---

## Frontend Chat Structure

- `frontend/src/pages/ChatPage.jsx` is now a thin container that wires the chat UI together.
- Session and stream orchestration live in `frontend/src/pages/hooks/useChatSession.js`.
- Draft/input handling lives in `frontend/src/pages/hooks/useChatComposer.js`.
- Chat UI is split into smaller components under `frontend/src/components/chat/` for messages, input controls, queue state, and upload progress.

## License

MIT

