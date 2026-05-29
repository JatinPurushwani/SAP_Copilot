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

# Takeover & Risk Mitigation Strategy
## Multi-AI Chat Platform — 90 Day Ownership Stabilization Plan

---

## DAY 1-3: Verify Current State

### Immediate Validation

**Goal:** Confirm the system is actually in the state described.

Tasks:
1. ✓ Run full test suite
   ```bash
   npm test              # Should pass all 198 unit tests
   npm run lint          # Should have 0 errors
   npm run typecheck     # Should have 0 errors
   ```

2. ✓ Verify database schema matches reality
   - Export schema from Supabase SQL Editor
   - Compare to `schema_export.sql`
   - **Look specifically for:** `uploaded_files_rag.topic_id` FK constraint

3. ✓ Test production flow
   - Start backend locally
   - Start frontend locally
   - Send chat message → verify end-to-end response
   - Check Sentry dashboard for errors

4. ✓ Check provider connectivity
   - Test each configured AI model
   - Record which are working / failing
   - Note any rate limit issues

5. ✓ Audit environment variables
   - List all secrets used in `.env`
   - Verify each is set in production (Vercel)
   - Check Sentry DSN is active

### Success Criteria
- All tests pass
- Chat endpoint responds in <2s
- No Sentry errors in last 24h
- All configured models accessible

---

## DAY 4-7: Document Actual State

### What You'll Discover

**Create a "Deployment Runbook"** with:

1. **Actual Database Schema**
   ```sql
   -- Save output of:
   \d+ uploaded_files_rag
   \d+ message_embeddings
   \d+ query_cache
   ```

2. **Actual Model Configuration**
   ```json
   {
     "models": {
       "gemini-flash": { "works": true, "rate_limit": "1500/min" },
       "groq-mixtral": { "works": true, "rate_limit": "30/min" },
       ...
     }
   }
   ```

3. **Actual Secret Requirements**
   ```
   Required for operation:
   - JWT_SECRET (✓ set)
   - SUPABASE_URL (✓ set)
   - SUPABASE_SERVICE_KEY (✓ set)
   
   Optional features:
   - DEEPSEEK_API_KEY (for v4-pro)
   - BIZ_SUPABASE_* (for business DB)
   ```

4. **Deployment Checklist**
   - [ ] Supabase schema deployed
   - [ ] Message embeddings migration applied (if accurate mode)
   - [ ] Delete topic cascade RPC deployed
   - [ ] Sentry DSN set in Vercel
   - [ ] All provider API keys in Vercel Secrets
   - [ ] FRONTEND_URL matches domain

### Deliverable
- Markdown runbook: `DEPLOYMENT_RUNBOOK.md`
- Secrets inventory spreadsheet
- Model support matrix

---

## WEEK 2: Stabilize Critical Paths

### Priority 1: Token Quota System

**Risk:** Users can't use system if quota enforcement is broken.

**Validation:**
```bash
# Test in development:
1. Create user with 100 token quota
2. Send message that uses 50 tokens
3. Verify user.used_tokens = 50
4. Send message that would use 60 tokens
5. Verify 429 error returned
6. Verify user.used_tokens still 50 (not double-deducted)
```

**Write test:**
```javascript
// backend/__tests__/unit/tokenQuotaE2E.test.js
it('should enforce per-user token quota', async () => {
  // Create user with 100 token quota
  // Send message costing 50 tokens
  // Verify deducted
  // Verify balance correct
});
```

### Priority 2: Artifact Cleanup

**Risk:** Users delete chat but files remain → disk bloat + clutter.

**Validation:**
```bash
# Test in development:
1. Create new chat (topic_id = null)
2. AI generates code block
3. Artifact saved to uploaded_files_rag (should have topic_id)
4. Delete chat
5. Verify artifact deleted immediately (not after 24h)
6. Verify sidebar refreshes (no stale entries)
```

**Write test:**
```javascript
// backend/__tests__/integration/artifactLifecycle.test.js
it('should delete artifacts when topic is deleted', async () => {
  // Create chat, generate artifact
  // Delete topic
  // Verify uploaded_files_rag rows deleted
});
```

### Priority 3: Streaming Reliability

**Risk:** SSE stream drops → user loses partial response.

**Validation:**
```bash
# Test in development:
1. Send streaming request
2. Simulate network interruption (DevTools throttle)
3. Check if response is partially saved
4. Restart and verify chat history has what was saved
```

**Add logging:**
```javascript
// In chat.routes.js SSE handler
res.on('error', (err) => {
  console.error('[SSE] Stream error:', err.message);
  Sentry.captureException(err);
});

res.on('close', () => {
  console.log('[SSE] Stream closed, bytes sent:', res.bytesWritten);
});
```

### Deliverable
- 3 new integration tests
- Logging added to critical paths
- Token quota validated in staging

---

## WEEK 3: Add Observability

### Implement Structured Logging

**Goal:** When something breaks, you can trace it.

```javascript
// Create backend/utils/logger.js
class Logger {
  log(category, message, metadata = {}) {
    console.log(JSON.stringify({
      timestamp: new Date().toISOString(),
      category,
      message,
      ...metadata
    }));
  }
}
```

**Use in critical paths:**
```javascript
// In chat.controller.js
logger.log('CACHE', 'Semantic cache check', {
  query: compressedQuery.slice(0, 100),
  similarity: cached.similarity,
  cacheHit: true
});

logger.log('DISPATCH', 'AI dispatch starting', {
  modelId,
  messageCount: aiMessages.length,
  estimatedTokens
});

logger.log('TOOL_LOOP', 'Tool round complete', {
  round,
  toolCalled: !!toolResult,
  tokensUsed,
  duration: Date.now() - roundStart
});
```

### Set Up Alerts

**In Sentry Dashboard:**
1. Alert on error rate > 5%
2. Alert on response time > 5s
3. Alert on specific error: "QUERY_DB failed"
4. Daily digest email

### Deliverable
- Structured logging in 5+ critical paths
- Sentry alerts configured
- Log aggregation dashboard (if using DataDog, CloudWatch, etc.)

---

## WEEK 4: Performance Baseline

### Establish Metrics

**What to measure:**
```javascript
// Add to analytics.service.js
const PERFORMANCE_TARGETS = {
  cache_hit_rate: 0.15,           // 15% of queries hit semantic cache
  avg_response_time: 2500,        // 2.5s average
  p95_response_time: 5000,        // 95th percentile = 5s
  tool_loop_rounds_avg: 2.5,      // Average 2-3 database queries per chat
  embedding_cache_hit_rate: 0.6,  // 60% of embeddings from cache
};
```

**Collect metrics:**
```javascript
// In chat.controller.js, at end:
await logAnalytics({
  responseTimeMs: Date.now() - startTime,
  cacheHit,
  toolLoopsUsed: toolRounds,
  embeddingCacheHits,
  tokensUsed,
});
```

**Report monthly:**
```
Performance Report — January 2026
- Cache hit rate: 12% (target: 15%)
- Avg response time: 2.3s (target: 2.5s) ✓
- P95 response time: 4.8s (target: 5s) ✓
- Tool loops: avg 2.1 rounds (target: 2.5) ✓
```

### Load Testing

**Setup:**
```bash
# Use Apache Bench or k6
# Simulate 100 concurrent users
# 10 requests each
ab -n 1000 -c 100 http://localhost:5000/api/chat/message
```

**Monitor:**
- Supabase connection pool
- Vercel cold starts
- Error rate under load
- Semantic cache effectiveness

### Deliverable
- Performance baseline established
- Metrics dashboard created
- Load test script in repo

---

## MONTH 2: Architectural Decisions

### Decision 1: Tool Calling System

**Current:** Regex-based tag matching
- Fragile: Any format change breaks extraction
- Not native: Claude/Gemini have built-in function calling

**Options:**

A. **Keep as-is** (Minimal work)
   - Pros: Works, no migration needed
   - Cons: Brittle, poor error handling
   - Recommend: NO

B. **Add native function calling** (Medium work)
   - Pros: Robust, matches provider APIs
   - Cons: Per-provider code, testing complexity
   - Recommend: YES if scaling

C. **Hybrid: Regex fallback + native** (High work)
   - Pros: Best compatibility
   - Cons: Duplicate logic
   - Recommend: ONLY if mixing providers

**Recommendation:** If <100K messages/month: keep regex. If >500K: migrate to native.

### Decision 2: Business Database

**Current:** Optional, separate Supabase instance

**Questions:**
- Is it being used in production?
- How many teams use it?
- How critical are results (e.g., financial data)?

**If used heavily:**
- [ ] Add SQL parameterization (prevent injection)
- [ ] Add query whitelisting (what tables can be queried)
- [ ] Add audit logging (who queried what, when)
- [ ] Add result validation (schema matching)

**If rarely used:**
- [ ] Remove from base system
- [ ] Make it optional extension
- [ ] Reduce maintenance burden

### Decision 3: Approval Gates

**Current:** Available in code but not used in main flow

**Should you integrate?**
- YES if: Compliance required, safety-critical operations
- NO if: Speed > safety, consumer product, low stakes

**If integrating:**
```javascript
// Require approval for sensitive operations:
const agent = new SmartAgent({
  approvalHandler: new HumanApprovalHandler(),
  requireApprovalFor: ['delete_data', 'large_spend_queries']
});
```

### Deliverable
- Architecture Decision Record (ADR) for each
- Cost/benefit analysis
- Implementation plan for chosen paths

---

## MONTH 3: Scale Preparation

### Pre-Scale Audit

Before scaling to 100 users / 1000 messages/day:

**Database:**
- [ ] Indexes exist on all vector columns
- [ ] Query plans analyzed (EXPLAIN)
- [ ] Message archival strategy documented
- [ ] Backup schedule tested

**API Layer:**
- [ ] Rate limiting per-user (not just global)
- [ ] Circuit breaker for provider failures
- [ ] Fallback models configured
- [ ] Cache eviction policy tuned

**Embedding Cache:**
- [ ] LRU eviction working (max 5000 entries)
- [ ] TTL cleanup running (every 15 min)
- [ ] Hit rate >60% for typical users
- [ ] Memory stable over time

**Provider Costs:**
- [ ] Track spend per model
- [ ] Alert if daily spend > threshold
- [ ] Fallback to cheaper models if needed
- [ ] Cost per message calculated

### Load Testing Results

Expected results at 10 QPS:
```
Response Times:
  p50: 1.2s
  p95: 3.5s
  p99: 6.8s
  
Error Rate: <0.5%

Concurrent Users: 100+

Token Spend: Varies by model, track in Sentry
```

### Deliverable
- Pre-scale audit checklist (✓ all items)
- Load test results document
- Scaling operations runbook
- Cost projection for 10x growth

---

## RED FLAGS TO INVESTIGATE IMMEDIATELY

If you see these, the system may be in trouble:

1. **Token accounting skipped**
   - Users charged wrong amount
   - Quota system unreliable
   - → Fix immediately, audit all user balances

2. **Artifact deletion failing silently**
   - Files accumulate after delete
   - Sidebar shows ghosts
   - → Check uploaded_files_rag cascading delete works

3. **Semantic cache always missing**
   - Every query hits API
   - embedding cache LRU not evicting
   - → Check embedding cache is actually caching

4. **Tool loop hanging / timeout**
   - Requests >30s on Vercel
   - Partial responses
   - → Cap iterations at 5, add timeout handler

5. **Provider downtime cascading**
   - One provider fails → whole chat fails
   - No fallback
   - → Implement provider failover

6. **Sentry silent**
   - Errors not being captured
   - Production issues invisible
   - → Verify Sentry integration, check DSN

---

## OWNERSHIP SUCCESS CRITERIA (90 Days)

### Week 1 ✓
- [ ] Understand current state
- [ ] Run all tests successfully
- [ ] Identify one improvement

### Week 2-4 ✓
- [ ] Stabilize critical paths (token quota, artifacts)
- [ ] Add observability (logging, Sentry alerts)
- [ ] Performance baseline established

### Month 2 ✓
- [ ] Make architectural decisions (tool calling, BizDB, approval gates)
- [ ] Begin implementation of chosen paths
- [ ] Document rationale

### Month 3 ✓
- [ ] Pre-scale validation complete
- [ ] Can confidently handle 10x growth
- [ ] Team trained on runbooks
- [ ] Handoff documentation updated

### Month 4+ ⭐
- [ ] System scaled to planned size
- [ ] Zero unplanned downtime
- [ ] New features shipping safely
- [ ] Operating costs understood and optimized

---

## Reference: Architecture Layers

When something breaks, know which layer:

```
┌─────────────────────────────────────────────┐
│ PRESENTATION (Frontend - React)              │ 
│ - Chat UI, theme, auth UI                   │ 
│ Risk: CSS bugs, state bugs, slow rendering  │
└────────────────┬────────────────────────────┘
                 │ HTTPS
┌────────────────▼────────────────────────────┐
│ API (Express - Routes + Controllers)        │
│ - /api/chat/message, /api/auth, etc.        │
│ Risk: Token quota bugs, streaming bugs      │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ BUSINESS LOGIC (Services Layer)             │
│ - Token budget, RAG, cache, context build   │
│ Risk: Complex logic bugs, race conditions   │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ PROVIDERS (AI + Tools)                      │
│ - Gemini, Groq, Mistral, DB queries         │
│ Risk: Provider rate limits, API changes     │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ DATA (Supabase - PostgreSQL + pgvector)    │
│ - Users, topics, messages, embeddings       │
│ Risk: Constraint violations, slow queries   │
└─────────────────────────────────────────────┘
```

When troubleshooting: isolate which layer, then debug within.

---

## Handoff Checklist

Before declaring success:

- [ ] Can start backend/frontend locally in 5 min
- [ ] Can run all tests successfully
- [ ] Understand data flow (message → response)
- [ ] Know where each configuration option lives
- [ ] Can add new AI model
- [ ] Can debug token quota issue
- [ ] Can explain why semantic cache is enabled, exact cache is disabled
- [ ] Can identify and fix the artifact deletion bug (if present)
- [ ] Know what each service does (35+ services)
- [ ] Can explain tool loop iteration & token trimming
- [ ] Can read Sentry dashboard and find issue
- [ ] Can make safe production deployment
- [ ] Know the 3 hardest things (tool loop, artifacts, memory modes)
- [ ] Can guide new developer onboarding

---

## Final Notes

This codebase is **production-ready but complex**. 

Success comes from:
1. **Respect the complexity** — Don't oversimplify
2. **Instrument everything** — Logging + monitoring save time
3. **Test before deploying** — Catch issues locally
4. **Document decisions** — Future you will thank present you
5. **Plan for scale** — Identify bottlenecks early

**You've got this.** The system is well-built. Your job is to understand it, stabilize it, and grow it safely.

---

Good luck on the journey. 🚀
