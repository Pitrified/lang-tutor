# Content source (where lemmas come from)

`lang-tutor` reads lemma content through a single seam, `ContentSource`, with two
interchangeable implementations. The transport is chosen by configuration, so
the rest of the app (exercises, lemma browsing) never knows whether content
arrives over HTTP or from an in-process read.

```python
from lang_tools.lexicon import CardQuery

from lang_tutor.content import get_content_source

source = get_content_source()
cards = source.get_cards(CardQuery(language="pt", max_cefr="B1", single_word=True))
card = source.get_card(lemma_id, translation_languages=["en", "it"])
meanings = source.get_sense_cards(lemma_id)  # one card per sense, best first
page = source.get_lemma_page(language="pt", query="cas", limit=50, offset=0)
lemma = source.get_lemma_by_id(lemma_id)
```

Every read is bounded. The full corpus holds 324k lemmas (149k en, 46k pt), so
nothing here returns a whole language.

## Drill cards

The exercises are built from `lang_tools.lexicon.LemmaCard`, the learner-facing
view `lang-tools` serves. The thin `Lemma` carries no meaning, so a card adds
what a drill needs, taken from the lemma's **best sense** (its most frequent
meaning):

- `cefr_level` and `sense_frequency` of that sense;
- `gloss`: the concept's definition in the requested gloss language;
- `translations`: language -> the concept's other lemmas, most frequent first
  (the lemma's own language lists its synonyms);
- `examples`: the concept's example sentences in the lemma's language.

A `CardQuery` filters the sample on the `lang-tools` side. The filters are:

- language;
- CEFR window;
- topic, part of speech;
- exact or minimum length;
- accented only;
- single word (one lowercase alphabetic token, so no proper nouns or
  compounds);
- requires a translation or an example;
- excluded ids.

The order is random (seedable) or by frequency, and a query returns at most 500
cards.

## The learner and look-alikes

`LearnerParams` holds the learner profile: the language being learned
(`LANG_TUTOR_TARGET_LANGUAGE`, default `pt`) and the languages they already know
(`LANG_TUTOR_KNOWN_LANGUAGES`, comma-separated, default `en,it`). Every card read
passes the known languages, so each card carries its **look-alikes** in them
(`LemmaCard.lookalikes`, phase 11 in `lang-tools`). A pt word then falls in one of
three cases:

- **A trap:** a false friend of a known word (pt *esquisito* / en *exquisite*).
  `card.is_trap` is true, and the hint carries an English note.
- **Free:** a cognate of a known word (pt *nação* / it *nazione*).
  `card.has_cognate` is true.
- **Neither.**

The look-alike edges are pairwise, and this view is a read-time union over the
known languages, so adding a language to the list needs no other change.

How the tutor uses them:

- **Selection** gives a trap a mild bonus (`trap_factor` 1.3, worth practising) and
  a cognate a mild damping (`cognate_factor` 0.7, free vocabulary).
- **Pair matching** adds up to one false-friend decoy to the right column: en
  *exquisite* next to pt *esquisito*. It matches nothing, and tapping it for its
  look-alike shows the trap note.
- **The lemma page** shows a "Looks like" box, with false friends as warnings and
  cognates as "same meaning".

## How a round is built

`lang_tutor.progress.draw_cards` asks the source for a random window of four
times the round size and weights it with the user's progress (`select_lemmas`):

- unseen and error-heavy lemmas come up more;
- easier bands get a mild bonus;
- recent ones decay;
- lemmas flagged useless are excluded on the server side.

Each exercise reports its lemma results through its progress callback to
`SessionProgressService`. That record lives **in memory** per server process;
durable progress is a separate follow-up.

| Exercise | Card query |
| -------- | ---------- |
| Pair matching | single words of 3+ letters with a translation in the target language; two cards never share a right-hand word |
| Wordle | single words of the chosen length |
| Diacritic typing | accented single words of 3+ letters; gloss and translation as hints |
| Sentence reconstruction | lemmas with an example sentence; the round uses an example that contains the lemma |

All of them default to `max_cefr="B1"`. Example sentences exist for en (about
33k concepts) and it (about 1.4k), plus a small curated set for pt, es and fr.
English has no accented lemmas, so diacritic typing answers `400` there.

## The two sources

| Source | Class | When to use |
| ------ | ----- | ----------- |
| HTTP (default) | `HttpContentSource` | Deployed topology: `lang-tools` runs as a service and `lang-tutor` consumes it over HTTP, never storing content locally. |
| In-process | `InProcessContentSource` | Local/dev without running the service. Reads the `lang-tools` lemma store directly (requires the content materialised on disk via git-lfs). |

Both return the same `lang_tools.lexicon` models (`LemmaCard`, `Lemma` with its
computed fields `id`, `has_accent`, `length`, ...), so they are drop-in
interchangeable.

## Configuration

Selection lives in `ContentParams`, driven by environment variables:

| Variable | Default | Meaning |
| -------- | ------- | ------- |
| `LANG_TOOLS_CONTENT_SOURCE` | `http` | `http` or `in_process`. |
| `LANG_TOOLS_BASE_URL` | `http://localhost:8010` | Base URL of the `lang-tools` service (used when source is `http`). |

```bash
# Default: consume the running lang-tools service
export LANG_TOOLS_CONTENT_SOURCE=http
export LANG_TOOLS_BASE_URL=http://127.0.0.1:8010

# Dev without the service: read the lang-tools store in-process
export LANG_TOOLS_CONTENT_SOURCE=in_process
```

To run the HTTP path locally, start the `lang-tools` read service first (see the
`lang-tools` "Running the read service" guide), then point
`LANG_TOOLS_BASE_URL` at it.

## Error handling

`HttpContentSource` maps a `404` on `get_lemma_by_id` and `get_card` to `None`
(consistent with the in-process store). Any other non-2xx response, or a
transport failure, raises `ContentServiceError`.

Over HTTP a `CardQuery` travels as the query string of `GET /api/v1/cards`. Only
non-default fields are sent, and list fields repeat the key
(`translation_languages=en&translation_languages=it`). A lemma page reads its
total from the `X-Total-Count` header of `GET /api/v1/lemmas`.

## Overriding in tests

`set_content_source()` swaps the process-wide source (or pass `None` to clear
the cache so the next call rebuilds from params):

```python
from lang_tutor.content import factory
from lang_tutor.content.in_process import InProcessContentSource

factory.set_content_source(InProcessContentSource())
```
