# Prototype V2 (Business + UX + Engineering) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a prototype-ready end-to-end procurement analysis workflow with better UX performance and reliable automated testing.

**Architecture:** Add a workflow service layer in backend to orchestrate existing agents and produce evidence-backed results; add a new frontend workbench with modular components and lazy loading; establish backend/frontend/E2E testing baseline with CI quality gates.

**Tech Stack:** FastAPI, SQLAlchemy, Vue 3, Vite, Element Plus, pytest, Vitest, Playwright, GitHub Actions

---

### Task 1: Create analysis workflow schema and API contract

**Files:**
- Create: `/Users/ali/dev/cc-smart-procurement/backend/app/schemas/analysis.py`
- Modify: `/Users/ali/dev/cc-smart-procurement/backend/app/schemas/__init__.py`

**Step 1: Write failing schema import test**

Run: `cd /Users/ali/dev/cc-smart-procurement/backend && ./venv/bin/python -m pytest tests/schemas/test_analysis_schema.py -q`  
Expected: FAIL (module or schema not found)

**Step 2: Implement request/response schema**

- Define `AnalysisWorkflowRequest`
- Define `EvidenceItem` and `AnalysisWorkflowResponse`

**Step 3: Re-run schema test**

Run: `cd /Users/ali/dev/cc-smart-procurement/backend && ./venv/bin/python -m pytest tests/schemas/test_analysis_schema.py -q`  
Expected: PASS

**Step 4: Commit**

Run: `git add backend/app/schemas/analysis.py backend/app/schemas/__init__.py tests/schemas/test_analysis_schema.py && git commit -m "feat: add analysis workflow schemas"`

---

### Task 2: Implement workflow service orchestration

**Files:**
- Create: `/Users/ali/dev/cc-smart-procurement/backend/app/services/analysis_workflow.py`
- Create: `/Users/ali/dev/cc-smart-procurement/backend/app/services/__init__.py`
- Test: `/Users/ali/dev/cc-smart-procurement/backend/tests/services/test_analysis_workflow.py`

**Step 1: Write failing service test**

Run: `cd /Users/ali/dev/cc-smart-procurement/backend && ./venv/bin/python -m pytest tests/services/test_analysis_workflow.py -q`  
Expected: FAIL (service missing)

**Step 2: Implement minimal workflow service**

- Call requirement, price, contract analyzers.
- Build `summary`, `risk_score`, `evidence`.

**Step 3: Re-run service test**

Run: `cd /Users/ali/dev/cc-smart-procurement/backend && ./venv/bin/python -m pytest tests/services/test_analysis_workflow.py -q`  
Expected: PASS

**Step 4: Commit**

Run: `git add backend/app/services backend/tests/services/test_analysis_workflow.py && git commit -m "feat: add workflow orchestration service"`

---

### Task 3: Add analysis history model and persistence

**Files:**
- Create: `/Users/ali/dev/cc-smart-procurement/backend/app/models/analysis_history.py`
- Modify: `/Users/ali/dev/cc-smart-procurement/backend/app/models/__init__.py`
- Test: `/Users/ali/dev/cc-smart-procurement/backend/tests/models/test_analysis_history.py`

**Step 1: Write failing model test**

Run: `cd /Users/ali/dev/cc-smart-procurement/backend && ./venv/bin/python -m pytest tests/models/test_analysis_history.py -q`  
Expected: FAIL

**Step 2: Implement model fields**

- `id`, `user_id`, `template_type`, `input_payload`, `result_payload`, `risk_score`, `created_at`

**Step 3: Run model test**

Run: `cd /Users/ali/dev/cc-smart-procurement/backend && ./venv/bin/python -m pytest tests/models/test_analysis_history.py -q`  
Expected: PASS

**Step 4: Commit**

Run: `git add backend/app/models/analysis_history.py backend/app/models/__init__.py backend/tests/models/test_analysis_history.py && git commit -m "feat: add analysis history model"`

---

### Task 4: Expose analysis workflow API

**Files:**
- Create: `/Users/ali/dev/cc-smart-procurement/backend/app/api/analysis.py`
- Modify: `/Users/ali/dev/cc-smart-procurement/backend/app/main.py`
- Test: `/Users/ali/dev/cc-smart-procurement/backend/tests/api/test_analysis.py`

**Step 1: Write failing API test**

Run: `cd /Users/ali/dev/cc-smart-procurement/backend && ./venv/bin/python -m pytest tests/api/test_analysis.py -q`  
Expected: FAIL

**Step 2: Implement endpoints**

- `POST /api/analysis/workflow`
- `GET /api/analysis/history`
- `POST /api/analysis/history/{id}/reuse`

**Step 3: Re-run API test**

Run: `cd /Users/ali/dev/cc-smart-procurement/backend && ./venv/bin/python -m pytest tests/api/test_analysis.py -q`  
Expected: PASS

**Step 4: Commit**

Run: `git add backend/app/api/analysis.py backend/app/main.py backend/tests/api/test_analysis.py && git commit -m "feat: add analysis workflow APIs"`

---

### Task 5: Add frontend API methods and state composables

**Files:**
- Modify: `/Users/ali/dev/cc-smart-procurement/frontend/src/api/index.js`
- Create: `/Users/ali/dev/cc-smart-procurement/frontend/src/composables/useAnalysisWorkflow.js`
- Create: `/Users/ali/dev/cc-smart-procurement/frontend/src/composables/useDraftCache.js`
- Test: `/Users/ali/dev/cc-smart-procurement/frontend/src/composables/__tests__/useAnalysisWorkflow.spec.js`

**Step 1: Write failing composable tests**

Run: `cd /Users/ali/dev/cc-smart-procurement/frontend && npm run test -- useAnalysisWorkflow.spec.js`  
Expected: FAIL

**Step 2: Implement composables**

- Request execution state (`idle/loading/success/error`)
- Draft cache save/load/clear
- Error normalization

**Step 3: Re-run composable tests**

Run: `cd /Users/ali/dev/cc-smart-procurement/frontend && npm run test -- useAnalysisWorkflow.spec.js`  
Expected: PASS

**Step 4: Commit**

Run: `git add frontend/src/api/index.js frontend/src/composables && git commit -m "feat: add analysis workflow composables"`

---

### Task 6: Build analysis workbench page

**Files:**
- Create: `/Users/ali/dev/cc-smart-procurement/frontend/src/views/AnalysisWorkbench.vue`
- Create: `/Users/ali/dev/cc-smart-procurement/frontend/src/components/analysis/InputPanel.vue`
- Create: `/Users/ali/dev/cc-smart-procurement/frontend/src/components/analysis/ResultPanel.vue`
- Create: `/Users/ali/dev/cc-smart-procurement/frontend/src/components/analysis/EvidencePanel.vue`
- Modify: `/Users/ali/dev/cc-smart-procurement/frontend/src/router/index.js`

**Step 1: Add route and basic page skeleton**

Run: `cd /Users/ali/dev/cc-smart-procurement/frontend && npm run build`  
Expected: PASS

**Step 2: Connect page with workflow composable**

- submit input
- render summary
- render evidence panels

**Step 3: Add history list and reuse action**

Run: `cd /Users/ali/dev/cc-smart-procurement/frontend && npm run build`  
Expected: PASS

**Step 4: Commit**

Run: `git add frontend/src/views/AnalysisWorkbench.vue frontend/src/components/analysis frontend/src/router/index.js && git commit -m "feat: add analysis workbench UI"`

---

### Task 7: Refactor heavy pages into modular components

**Files:**
- Modify: `/Users/ali/dev/cc-smart-procurement/frontend/src/views/Requirements.vue`
- Modify: `/Users/ali/dev/cc-smart-procurement/frontend/src/views/Contract.vue`
- Modify: `/Users/ali/dev/cc-smart-procurement/frontend/src/views/Price.vue`
- Create: `/Users/ali/dev/cc-smart-procurement/frontend/src/components/requirements/*`
- Create: `/Users/ali/dev/cc-smart-procurement/frontend/src/components/contract/*`
- Create: `/Users/ali/dev/cc-smart-procurement/frontend/src/components/price/*`

**Step 1: Extract Requirements subcomponents**

Run: `cd /Users/ali/dev/cc-smart-procurement/frontend && npm run build`  
Expected: PASS

**Step 2: Extract Contract and Price subcomponents**

Run: `cd /Users/ali/dev/cc-smart-procurement/frontend && npm run build`  
Expected: PASS

**Step 3: Verify no route behavior regression manually**

Run: `cd /Users/ali/dev/cc-smart-procurement/frontend && npm run dev`  
Expected: major flows still work

**Step 4: Commit**

Run: `git add frontend/src/views frontend/src/components/requirements frontend/src/components/contract frontend/src/components/price && git commit -m "refactor: split large pages into domain components"`

---

### Task 8: Add unified state and error components

**Files:**
- Create: `/Users/ali/dev/cc-smart-procurement/frontend/src/components/common/StateBlock.vue`
- Modify: `/Users/ali/dev/cc-smart-procurement/frontend/src/api/index.js`
- Modify: `/Users/ali/dev/cc-smart-procurement/frontend/src/views/*.vue`

**Step 1: Implement reusable state block**

- loading/empty/error/unauthorized

**Step 2: Replace ad-hoc state handling in key pages**

Run: `cd /Users/ali/dev/cc-smart-procurement/frontend && npm run build`  
Expected: PASS

**Step 3: Commit**

Run: `git add frontend/src/components/common/StateBlock.vue frontend/src/api/index.js frontend/src/views && git commit -m "feat: unify UI states and error handling"`

---

### Task 9: Add backend pytest baseline

**Files:**
- Create: `/Users/ali/dev/cc-smart-procurement/backend/tests/conftest.py`
- Create: `/Users/ali/dev/cc-smart-procurement/backend/tests/api/test_auth.py`
- Create: `/Users/ali/dev/cc-smart-procurement/backend/tests/api/test_requirements.py`
- Create: `/Users/ali/dev/cc-smart-procurement/backend/tests/api/test_price.py`
- Create: `/Users/ali/dev/cc-smart-procurement/backend/tests/api/test_contract.py`
- Modify: `/Users/ali/dev/cc-smart-procurement/backend/requirements.txt`

**Step 1: Add pytest dependencies**

Run: `cd /Users/ali/dev/cc-smart-procurement/backend && ./venv/bin/pip install pytest pytest-asyncio httpx`  
Expected: install success

**Step 2: Implement smoke tests for each API domain**

**Step 3: Run backend test suite**

Run: `cd /Users/ali/dev/cc-smart-procurement/backend && ./venv/bin/python -m pytest -q`  
Expected: PASS

**Step 4: Commit**

Run: `git add backend/requirements.txt backend/tests && git commit -m "test: add backend pytest baseline"`

---

### Task 10: Add frontend unit test baseline

**Files:**
- Modify: `/Users/ali/dev/cc-smart-procurement/frontend/package.json`
- Create: `/Users/ali/dev/cc-smart-procurement/frontend/vitest.config.js`
- Create: `/Users/ali/dev/cc-smart-procurement/frontend/src/components/analysis/__tests__/ResultPanel.spec.js`
- Create: `/Users/ali/dev/cc-smart-procurement/frontend/src/composables/__tests__/useDraftCache.spec.js`

**Step 1: Install vitest stack**

Run: `cd /Users/ali/dev/cc-smart-procurement/frontend && npm install -D vitest @vue/test-utils jsdom`  
Expected: install success

**Step 2: Add test scripts**

- `test`, `test:run`

**Step 3: Run frontend unit tests**

Run: `cd /Users/ali/dev/cc-smart-procurement/frontend && npm run test:run`  
Expected: PASS

**Step 4: Commit**

Run: `git add frontend/package.json frontend/vitest.config.js frontend/src/components/analysis/__tests__ frontend/src/composables/__tests__ && git commit -m "test: add frontend unit test baseline"`

---

### Task 11: Stabilize Playwright smoke tests

**Files:**
- Modify: `/Users/ali/dev/cc-smart-procurement/test_full.py`
- Create: `/Users/ali/dev/cc-smart-procurement/frontend/tests/e2e/analysis-workflow.spec.ts`
- Create: `/Users/ali/dev/cc-smart-procurement/frontend/playwright.config.ts`

**Step 1: Convert key manual flows into deterministic E2E scripts**

**Step 2: Add CI-friendly headless run command**

Run: `cd /Users/ali/dev/cc-smart-procurement/frontend && npx playwright test --grep "smoke"`  
Expected: PASS

**Step 3: Commit**

Run: `git add test_full.py frontend/tests/e2e frontend/playwright.config.ts && git commit -m "test: add playwright smoke suites"`

---

### Task 12: Add CI quality gates

**Files:**
- Create: `/Users/ali/dev/cc-smart-procurement/.github/workflows/ci.yml`
- Modify: `/Users/ali/dev/cc-smart-procurement/README.md`

**Step 1: Configure pipeline**

- Backend lint/test
- Frontend build/test
- Optional smoke E2E

**Step 2: Verify workflow syntax**

Run: `cd /Users/ali/dev/cc-smart-procurement && rg -n "name: CI|jobs:" .github/workflows/ci.yml`  
Expected: workflow exists with required jobs

**Step 3: Commit**

Run: `git add .github/workflows/ci.yml README.md && git commit -m "ci: add baseline quality gates"`

---

## Phase Verification Checklist

### Verify Phase A

Run:

```bash
cd /Users/ali/dev/cc-smart-procurement/backend
./venv/bin/python -m pytest tests/api/test_analysis.py -q
```

Expected:
- API returns `summary`, `risk_score`, `evidence`, `history_id`.

### Verify Phase B

Run:

```bash
cd /Users/ali/dev/cc-smart-procurement/frontend
npm run build
```

Expected:
- Build passes.
- Workbench route loads.
- Heavy pages still function after refactor.

### Verify Phase C

Run:

```bash
cd /Users/ali/dev/cc-smart-procurement/backend
./venv/bin/python -m pytest -q
cd /Users/ali/dev/cc-smart-procurement/frontend
npm run test:run
```

Expected:
- Backend tests PASS.
- Frontend unit tests PASS.
- CI pipeline can reproduce these checks.

---

Plan complete and saved to `/Users/ali/dev/cc-smart-procurement/docs/plans/2026-02-18-prototype-v2-implementation-plan.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
