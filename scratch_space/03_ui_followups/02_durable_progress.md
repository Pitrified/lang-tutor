---
status: discarded
---

# Phase 2 - durable progress

Deferred on 2026-11-03 (`00_start.md` Q4): the permanent progress store is not done in this folder.
The plan below stays as the starting point for a later folder.

## Overview

Keep each learner's progress across a server restart. Today `SessionProgressService` holds every
`UserLemmaProgress` in memory, so weighted selection forgets a learner on restart. Context:
[`00_start.md`](00_start.md), item 2; the store is `00_start.md` Q4.

## Plan

- Replace `SessionProgressService` behind the same interface (`for_user`, `recorder`) with a
  store chosen in Q4, its path from the params (`paths`).
- Load a user's progress on first use and write each recorded result.
- Tests for a restart: record, rebuild the service, read back.
- Update the module docstring and `docs/guides/` with where progress lives and the Render
  caveat.

## Out of scope

- Durable users (`UserService`), unless Q4 picks a hosted database.
- A settings page or per-user known languages.

## Done when

- Progress survives a restart of `make serve`.
- `make check` passes.
