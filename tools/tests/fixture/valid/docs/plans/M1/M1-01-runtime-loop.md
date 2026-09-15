# M1-01 — Runtime loop
**Status:** in progress
**Milestone:** M1
**Branch:** feat/M1-01-runtime-loop
**Design docs:** `docs/design/product-design.md §2.1a`
**ADRs:**
**Depends on:** M0-01

## Sessions
- 2026-09-15T09:00Z — claude-code — feat/M1-01-runtime-loop

## Objective
Run one instance end to end.

## Current state
- Validator green on the example instance.

## Approach
Load, step, render.

## Tasks
- [x] T1 — Loader. **Verify:** `pytest tests/test_loader.py`
- [ ] T2 — Step function. **Verify:** `pytest tests/test_step.py`

## Progress notes
- 2026-09-15 — loader done; step function next.

## Verification log
- T1: `pytest tests/test_loader.py` → `3 passed`
