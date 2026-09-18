# Transparent Domains Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Allow one ComboCode goal to be visible from multiple transparent domains without duplicating the goal.

**Architecture:** Preserve `category` as the primary category and add optional `domains: list[str]`. Centralize membership logic in the knowledge engine so both search and archive filtering inherit the behavior automatically. Mark Opera internal URLs as also belonging to `Browser · Opera`.

**Tech Stack:** Python 3, unittest, JSON data packs.

**Spec:** `docs/superpowers/specs/2026-09-18-transparent-domains-design.md`

## Global Constraints

- Preserve existing `category` behavior for goals with no `domains`.
- Do not duplicate goals or change goal IDs.
- Do not change search scoring.
- Keep `Browser url's` as the primary category of browser internal URLs.

---

### Task 1: Engine support for transparent domains

**Files:**
- Modify: `combocode/engine.py`
- Test: `tests/test_engine.py`

**Interfaces:**
- Consumes: goal dictionaries with scalar `category` and optional `domains` list.
- Produces: category membership used by `categories()` and `search()`.

- [ ] **Step 1: Write failing tests**

Add tests that create a goal with `category="Browser url's"` and `domains=["Browser · Opera"]`, then assert it is returned by both category filters and both category names appear in `categories()`.

- [ ] **Step 2: Run tests and confirm RED**

Run: `python -m unittest tests.test_engine -v`

Expected: the transparent-domain assertions fail because filtering currently checks only `goal['category']`.

- [ ] **Step 3: Implement minimal engine support**

Add a small helper that returns unique domain memberships from primary `category` plus optional `domains`. Use it in `categories()`, in the category filter inside `search()`, and include the extra domains in the index blob.

- [ ] **Step 4: Run engine tests and confirm GREEN**

Run: `python -m unittest tests.test_engine -v`

Expected: all engine tests pass.

### Task 2: Mindlink Opera internal URLs to Opera

**Files:**
- Modify: `combocode/data/packs/browser_internal_urls.json`
- Test: `tests/test_browser_internal_urls.py`

**Interfaces:**
- Consumes: transparent-domain support from Task 1.
- Produces: every internal Opera URL is visible under both `Browser url's` and `Browser · Opera`.

- [ ] **Step 1: Write failing regression test**

Load the full packs and assert that searching `shortcut` with category `Browser · Opera` contains route `opera://settings/keyboardShortcuts`.

- [ ] **Step 2: Run regression test and confirm RED**

Run: `python -m unittest tests.test_browser_internal_urls.BrowserInternalPackTests -v`

Expected: the regression fails until the pack declares the additional domain.

- [ ] **Step 3: Add the explicit domain mapping**

Add `"domains": ["Browser · Opera"]` to each goal in `browser_internal_urls.json`.

- [ ] **Step 4: Run focused tests and full suite**

Run:
`python -m unittest tests.test_browser_internal_urls -v`
`python -m unittest discover -s tests -v`

Expected: all tests pass.

### Task 3: Verify Windows build

**Files:**
- No production changes.

**Interfaces:**
- Consumes: committed engine and data-pack changes.
- Produces: CI evidence that the Windows executable still builds.

- [ ] **Step 1: Push/commit changes through the normal GitHub workflow**
- [ ] **Step 2: Verify the Test step succeeds**
- [ ] **Step 3: Verify Build EXE succeeds**
- [ ] **Step 4: Verify artifact upload succeeds**
