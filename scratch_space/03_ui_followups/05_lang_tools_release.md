---
status: done
---

# Phase 5 - lang-tools release

## Overview

One lang-tools tag for the code changes this folder needs, and one pin bump here:
- the import fix: `lang_tools.lexicon` imports fastapi-tools through the params; the fix
  imports `WebappParams` lazily (`00_start.md` Q7, a);
- the code of lang-tools' `12_card_senses` (phase 3, Q11): the two build rules and the
  best-sense override.

Context: [`00_start.md`](00_start.md), item 5.

## Plan

- In lang-tools, import `WebappParams` lazily, so `lang_tools.lexicon` loads without the `webapp`
  extra, with a test that imports it without fastapi-tools.
- Tag the release; bump the pin in lang-tutor's `pyproject.toml` and `uv.lock`.
- Check lang-tools' `docs/library/frozen_api.md` for anything the release changes.

## Out of scope

- Data for tag installs: lang-tools `10_data_for_tag_installs`.

## Done when

- `from lang_tools.lexicon import LemmaCard` works on a clean install without the `webapp` extra.
- lang-tutor runs on the new tag, and `make check` passes in both repos.
