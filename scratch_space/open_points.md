# Open points

Known problems with no plan folder yet, one section each.
To work on one, open a numbered folder for it, start its `00_start.md` from the section,
and remove the section here.
A new point gets a section: what is wrong, how big, and where it was found.
Problems in the content and the corpus are in lang-tools' `scratch_space/open_points.md`.

## An empty `exclude_part_of_speech` is dropped

lang-tutor sends only the `CardQuery` fields that differ from their defaults
(`content/http.py` `_card_params`), and an empty list encodes to no pair at all.
So a query with `exclude_part_of_speech=[]` reaches the read API as the default and still gets
no function word (0 against 123 when the API is sent `?exclude_part_of_speech=` directly).
No lang-tutor query sets it today.
The fix: send the bare key for an empty list.
Found in lang-tools' card part-of-speech filter release (v0.6.0).

## Durable per-user progress

`SessionProgressService` holds every `UserLemmaProgress` in memory, per server process.
Weighted selection works within a run, but a restart forgets every learner.
The follow-up is a durable store (a JSON file or SQLite per user) behind the same service
interface (`for_user`, `recorder`).
A plan for it is written and was deferred on 2026-11-03:
[`03_ui_followups/02_durable_progress.md`](03_ui_followups/02_durable_progress.md).
