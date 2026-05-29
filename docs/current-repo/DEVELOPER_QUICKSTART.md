> ℹ️ **DOCUMENT STATUS: CURRENT REPOSITORY**
>
> This document describes the **Multi-AI Chat Platform** — the current production system.
>
> It is **kept for reference** because:
> - The current system remains in production
> - Developers continue to work on this codebase
> - The architecture documented here is real and running
>
> **If you're working on:**
> - Current chatbot system → This document is your reference
> - Future SAP platform → See [IMPLEMENTATION_BLUEPRINT.md](../../IMPLEMENTATION_BLUEPRINT.md)
> - Understanding the strategic shift → See [PROD_GAP_ANALYSIS.md](../../PROD_GAP_ANALYSIS.md)
>
> ---

# Developer Quick Start Guide
## Multi-AI Chat Platform — 30 Minute Onboarding

This guide gets you productive in 30 minutes. For deep architectural details, see `docs/current-repo/FORENSIC_ANALYSIS.md`.

---

## The System in 60 Seconds

**What:** Unified chat interface to 15 AI models + business database integration.

**How:** User sends message → backend processes (compress, cache, RAG, DB query) → dispatch to AI → stream response back.

**Stack:** React (frontend) + Express (backend) + Supabase (database) + Vercel (deployed).

---

## Get Running in 10 Minutes

### 1. Backend Setup (3 min)

```bash
cd backend
npm install
cp .env.example .env
```

Edit `.env`:
```
JWT_SECRET=your-secret-min-32-chars-very-important
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
FRONTEND_URL=http://localhost:3000
GEMINI_API_KEY=AIzaSy...  # At least one provider API key
```

```bash
npm run dev
# Should print: "Listening on http://localhost:5000"
```

### 2. Frontend Setup (3 min)

```bash
cd frontend
npm install
cp .env.example .env.local
```

Edit `.env.local`:
```
REACT_APP_API_URL=http://localhost:5000/api
```

```bash
npm start
# Should open http://localhost:3000
```

### 3. Verify It Works (2 min)

- Visit http://localhost:3000
- Click "Login with Email" or "Anonymous Mode"
- Send a message
- Should get a response

Done! ✓

---

## The Three Most Important Files

### 1. `backend/controllers/chat.controller.js`
**What:** The brain of the chat pipeline.

**What happens here:**
1. Compress user query (remove filler words)
2. Check semantic cache
3. Inject RAG context (uploaded files)
4. Inject history context (last 5 messages)
5. Dispatch to AI provider
6. Handle tool calls (if AI asks for data)
7. Save to database
8. Log analytics

**When to edit:** Changing chat behavior (history size, RAG threshold, token budgets)

### 2. `backend/services/tokenBudget.service.js`
**What:** Budget allocation for prompts.

**Key function:** `createPromptBudget(modelConfig)`
```javascript
{
  maxPromptTokens: 8000,      // Total budget
  systemTokens: 1500,         // For system prompt
  historyTokens: 2000,        // For conversation history
  ragTokens: 1500,            // For uploaded file context
  fileTokens: 1000,           // For file references
  queryTokens: 500            // For user query
}
```

**When to edit:** Changing token allocation priorities

### 3. `backend/services/rag.service.js`
**What:** Semantic search + embeddings.

**Key functions:**
- `embedText(text)` — convert to vector
- `buildRAGContext()` — find similar docs + inject

**When to edit:** Changing search threshold (0.92 semantic cache vs 0.4 RAG)

---

## Common Tasks

### Add a New AI Model

1. Edit `backend/config/models.js`:
```javascript
'my-model-id': {
  label: 'My Model Display Name',
  provider: 'provider-name',        // 'gemini', 'groq', 'custom'
  apiKey: process.env.MY_API_KEY,
  model: 'actual-model-name',       // What the API calls it
  paid: true,
  maxTokens: 8000,
}
```

2. If provider is new, create `backend/services/ai/my-provider.service.js`

3. Frontend auto-discovers models from `/api/chat/models`

### Add a Tool (AI can use)

1. Define regex matcher in `backend/services/toolProcessor.service.js`:
```javascript
const findMyToolMatch = (reply) => reply.match(/\[MY_TOOL:([^\]]+)\]/);
```

2. Add handler in `processToolCall()`:
```javascript
const match = findMyToolMatch(reply);
if (match) {
  const result = await executeMyTool(match[1]);
  // Format result and inject
}
```

3. Update system prompt to mention tool:
```
You have access to [MY_TOOL:param=value]
```

### Change How History is Included

File: `backend/services/context.service.js`

Key function: `buildContextMessages(topicId, limit = 5)`

Edit the `limit` parameter or the query logic.

### Debug Why Cache Isn't Working

Cache has TWO types:

| Type | How It Works | Threshold |
|------|---|---|
| Exact (DISABLED) | Hash of exact query | 1.0 (100% match) |
| Semantic | Vector similarity | 0.92 (92% match) |

If your query isn't hitting cache:
1. Is it semantically similar to a recent query? (Try rephrasing)
2. Is the model the same?
3. Check logs for "Cache miss" message

### Run Tests

```bash
npm test                  # All unit + integration tests
npm run test:watch       # Watch mode
npm run test:real        # Real API tests (need .env + backend running)
```

---

## Architecture Map (Simple)

```
User Input
    ↓
[middleware: auth, CSRF, sanitize]
    ↓
[chat.controller.js: orchestration]
    ├─ compress.service.js
    ├─ cache.service.js (semantic)
    ├─ rag.service.js
    ├─ context.service.js
    ├─ dispatcher.service.js → AI provider
    ├─ toolLoop.service.js (if AI asks for data)
    └─ tokenBudget.service.js
        ↓
[Save to DB: Supabase]
        ↓
Response to User
```

---

## Key Concepts

### Memory Modes
- **summarized:** Compress old history, no cross-chat memory
- **accurate:** Full history + search past conversations (slower)

### Token Budgets
- User has `total_tokens` quota (e.g., 1,000,000)
- Per message deducted from quota
- If `remaining <= 0` → 429 error
- Dynamic budgets adjust based on conversation length

### Tool Loop
- AI generates tool calls like `[QUERY_DB] SELECT ... [/QUERY_DB]`
- Backend extracts, executes, returns results
- AI sees results, refines answer or calls more tools
- Max 5-10 iterations to prevent infinite loops

### RAG (Retrieval-Augmented Generation)
- User uploads file → chunked + embedded
- On new query: embed query → vector search → inject top results
- Threshold: 0.4 (semantic similarity)
- Used only if `ragEnabled: true` in request

---

## Debugging Checklist

### Frontend shows "Cannot connect to API"
- ✓ Backend running? (`npm run dev` in `backend/`)
- ✓ FRONTEND_URL correct in backend `.env`?
- ✓ CORS enabled? (Check browser console for CORS error)

### Chat response empty
- ✓ API key configured? Check `backend/.env`
- ✓ Provider service exists? Check `services/ai/`
- ✓ Check Sentry for errors

### Token quota exhausted
- ✓ Check user's `total_tokens` in database
- ✓ Look at `used_tokens` column
- ✓ Reset via admin dashboard

### Tool loop hanging
- ✓ Check backend logs for "Tool Round X/10"
- ✓ Likely hitting max iterations
- ✓ Check DB schema and AI response format

### Artifacts not deleting
- ✓ Verify `topic_id` is set when artifact created
- ✓ Check `uploaded_files_rag.topic_id` FK constraint
- ✓ Look at `history.controller.js` deletion logic

---

## Environment Vars Cheat Sheet

### Required
```
JWT_SECRET=...                    # Min 32 chars, must be strong
SUPABASE_URL=...                  # Your Supabase project URL
SUPABASE_SERVICE_KEY=...          # Service role key (keep secret!)
FRONTEND_URL=...                  # Where frontend is deployed
```

### At Least One Provider
```
GEMINI_API_KEY=...                # Free tier available
GROQ_API_KEY=...                  # Free tier available
```

### Optional But Useful
```
SENTRY_DSN=...                    # Error tracking
BIZ_SUPABASE_URL=...              # Separate DB for business data
BIZ_SUPABASE_SERVICE_KEY=...
```

### Tuning (Advanced)
```
CHAT_MAX_DB_QUERIES=12            # Max DB queries per request
CHAT_MAX_CONSECUTIVE_ZERO_RESULTS=4
CHAT_TOOL_RESERVE_RATIO=0.15      # Reserve 15% of tokens for tools
CHAT_SEMANTIC_CACHE_THRESHOLD=0.92 # How similar for cache hit
```

---

## Common Error Messages

| Error | Cause | Fix |
|-------|-------|---|
| "Unknown model: xyz" | Model not in `config/models.js` | Add to models registry |
| "429 Too many requests" | Rate limited | Wait or increase limit in `chat.routes.js` |
| "Cannot execute tool" | Tool regex didn't match | Check AI response format matches regex |
| "Artifact not found" | `topic_id` null | Ensure saved after `done` event |
| "CORS error" | FRONTEND_URL mismatch | Match deployment URL exactly |
| "JWT invalid" | Token expired or wrong secret | Re-login or check JWT_SECRET |

---

## Quick Reference: Services by Purpose

| What I Want | File to Edit |
|---|---|
| Change token budgets | `tokenBudget.service.js` |
| Add a model | `config/models.js` |
| Add a tool | `toolProcessor.service.js` |
| Change RAG threshold | `rag.service.js` |
| Change history length | `context.service.js` |
| Change cache behavior | `cache.service.js` |
| Handle new provider | `services/ai/` + `dispatcher.service.js` |
| Fix tool loop | `toolLoop.service.js` |
| Change prompt | `chat.controller.js` |
| Add memory strategy | `memory.service.js` + export from `chat.service.js` |

---

## Testing Your Changes

### Unit Test
```bash
npm test -- __tests__/unit/tokenBudget.test.js
```

### Manual Test
1. Start backend: `npm run dev`
2. Start frontend: `npm start`
3. Send message in UI
4. Check backend logs for your changes

### Integration Test
```bash
npm run test:real
# (Requires .env with real API keys + backend running)
```

---

## When You're Stuck

### Where to Look

1. **Test files** — Show actual usage patterns
   - `backend/__tests__/unit/*.test.js`
   - `backend/__tests__/integration-real/*.test.js`

2. **Comments in code** — Explain design decisions
   - Search for `EVIDENCE:` or `NOTE:`

3. **FORENSIC_ANALYSIS.md** — Full architectural deep dive

4. **GUIDE.md** — Implementation patterns

5. **Sentry dashboard** — Real production errors

### If Still Stuck

1. Check Supabase schema matches `schema_export.sql` (not `schema.sql`)
2. Verify all .env vars are set
3. Look at backend stdout for detailed error traces
4. Add `console.log()` statements and watch the logs
5. Check browser DevTools Network tab for API responses

---

## What NOT To Change (Without Deep Thought)

- ✗ `tokenBudget.service.js` budget formulas (tokens are tracked)
- ✗ `rag.service.js` embedding dimension (1536 is standard)
- ✗ Tool tag formats in prompts (regex matchers depend on exact format)
- ✗ Database schema (breaking changes = migration headaches)
- ✗ JWT_SECRET after users are created (invalidates all tokens)

---

## Next Steps

1. **Read:** `FORENSIC_ANALYSIS.md` (deep dive on architecture)
2. **Explore:** Run tests to see actual usage
3. **Build:** Pick a small feature (add model, add tool) and implement
4. **Deploy:** Follow Vercel docs to push your changes
5. **Monitor:** Use Sentry + logs to track production issues

---

**Good luck! 🚀**
