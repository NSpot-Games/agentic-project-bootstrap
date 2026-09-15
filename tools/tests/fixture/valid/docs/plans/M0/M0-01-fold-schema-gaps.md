# M0-01 — Fold schema gaps
**Status:** done
**Milestone:** M0
**Branch:** feat/M0-01-fold-schema-gaps
**Design docs:** `docs/design/product-design.md §2.1`
**ADRs:** 0001
**Depends on:**

## Sessions
- 2026-09-10T09:00Z — claude-code — feat/M0-01-fold-schema-gaps

## Objective
Fold the ten gaps found by the example instance into the data model.

## Current state
- Example instance exists; validator reports ten missing fields.

## Approach
Add the fields, re-run the validator.

## Tasks
- [x] T1 — Add fields. **Verify:** `python tools/validate.py`

## Progress notes
- 2026-09-10 — all fields added, validator green.

## Verification log
- T1: `python tools/validate.py` → `0 errors`
