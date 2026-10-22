"""Exercise API endpoints.

JSON API for exercise interactions (start, submit, finish).
Called by the exercise page JavaScript.

Every round is built from `lang-tools` drill cards (`LemmaCard`): a bounded
`CardQuery` per round, weighted by the user's session progress through
`draw_cards`, never a whole language. Each exercise reports its lemma results
to the session progress service, so the next draw prefers unseen and missed
lemmas. The learner's level is the request's ``max_cefr`` (B1 by default), and
every card query names the learner's known languages (`LearnerParams`), so
cards carry their look-alikes: selection favours false friends, damps cognates,
and pair matching may add a false-friend decoy.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Annotated
from typing import Any
from typing import Literal

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi_tools.schemas.auth import SessionData  # noqa: TC002
from lang_tools.lexicon import CardQuery
from lang_tools.lexicon.card import CefrLevel  # noqa: TC002 - pydantic field type
from pydantic import BaseModel
from pydantic import Field

from lang_tutor.content import get_content_source
from lang_tutor.exercises.conversational_tutor import TutorMessage
from lang_tutor.exercises.diacritic_typing import DiacriticTypingExercise
from lang_tutor.exercises.pair_matching import MissingTranslationError
from lang_tutor.exercises.pair_matching import PairMatchingExercise
from lang_tutor.exercises.sentence_reconstruction import SentenceReconstructionExercise
from lang_tutor.exercises.wordle import WordleExercise
from lang_tutor.params.lang_tutor_params import get_learner_params
from lang_tutor.progress.selection import draw_cards
from lang_tutor.webapp.core.auth import get_current_user
from lang_tutor.webapp.services.progress_service import get_progress_service
from lang_tutor.webapp.services.tutor_service import tutor_reply

if TYPE_CHECKING:
    from lang_tools.lexicon import LemmaCard

router = APIRouter(prefix="/exercises", tags=["exercises-api"])

# In-memory session state (per-user game state).
# In production this would be stored in a DB or cache.
_active_rounds: dict[str, Any] = {}
_tutor_histories: dict[str, list[TutorMessage]] = {}

#: Extra cards drawn for a pair-matching round, so a card dropped for a shared
#: translation does not shrink it.
_PAIR_SPARES = 3

#: Fewest pairs a pair-matching round is worth playing with.
_MIN_PAIRS = 2

#: False-friend decoys added to a pair-matching round's right column (phase 11).
_MAX_DECOYS = 1

#: Shortest drill word: keeps letter names and particles (fr "p") out of the
#: pair-matching and diacritic rounds.
_MIN_WORD_LENGTH = 3

#: Sentence candidates drawn per round. The query already asks for an example
#: that names the lemma; the window leaves room to pick the sentence itself.
_SENTENCE_CANDIDATES = 4


class NoRoundContentError(HTTPException):
    """A 400 raised when the corpus has nothing to build a round from."""

    def __init__(self, what: str) -> None:
        """Initialize with what the round needed.

        Args:
            what: The missing content, e.g. ``"accented lemmas for pt"``.
        """
        super().__init__(status_code=400, detail=f"No {what}.")


def _draw(user: SessionData, query: CardQuery, n: int) -> list[LemmaCard]:
    """Draw ``n`` cards for ``user``, weighted by their session progress."""
    progress = get_progress_service().for_user(user.user_id)
    return draw_cards(get_content_source(), query, progress, n)


class PairMatchingStartRequest(BaseModel):
    """Request body to start a pair matching round."""

    language: str = "pt"
    target_language: str = "en"
    num_lemmas: int = Field(default=5, ge=_MIN_PAIRS, le=10)
    max_cefr: CefrLevel | None = "B1"


class WordleStartRequest(BaseModel):
    """Request body to start a wordle game."""

    language: str = "pt"
    word_length: int = Field(default=5, ge=3, le=10)
    max_cefr: CefrLevel | None = "B1"


class WordleGuessRequest(BaseModel):
    """Request body to submit a wordle guess."""

    guess: str


class DiacriticStartRequest(BaseModel):
    """Request body to start a diacritic typing round."""

    language: str = "pt"
    hint_level: Literal["off", "show_unaccented", "show_all"] = "off"
    hint_language: str = "en"
    max_cefr: CefrLevel | None = "B1"


class DiacriticKeystrokeRequest(BaseModel):
    """Request body to submit a keystroke."""

    character: str


class ReconstructionStartRequest(BaseModel):
    """Request body to start a sentence reconstruction round."""

    language: str = "pt"
    hint_language: str = "en"
    max_cefr: CefrLevel | None = "B1"


class ReconstructionSubmitRequest(BaseModel):
    """Request body to submit a portion selection."""

    selected_portions: list[str]


class TutorMessageRequest(BaseModel):
    """Request body to send a tutor message."""

    text: str
    topic: str = ""
    language: str = "pt"


class ExerciseResponse(BaseModel):
    """Generic exercise response."""

    status: str = "ok"
    data: dict[str, Any] = Field(default_factory=dict)


@router.post("/pair-matching/start")
async def pair_matching_start(
    body: PairMatchingStartRequest,
    user: Annotated[SessionData, Depends(get_current_user)],
) -> ExerciseResponse:
    """Start a new pair matching round from drill cards."""
    query = CardQuery(
        language=body.language,
        known_languages=get_learner_params().known_languages,
        translation_languages=[body.target_language],
        require_translation=True,
        single_word=True,
        min_length=_MIN_WORD_LENGTH,
        max_cefr=body.max_cefr,
    )
    cards = _draw(user, query, body.num_lemmas + _PAIR_SPARES)
    exercise = PairMatchingExercise(
        target_language=body.target_language,
        progress_callback=get_progress_service().recorder(
            user.user_id,
            "pair_matching",
        ),
    )
    try:
        round_ = (
            exercise.start(cards, num_pairs=body.num_lemmas, max_decoys=_MAX_DECOYS)
            if cards
            else None
        )
    except MissingTranslationError:
        round_ = None
    if round_ is None or len(round_.prompt["left_lemmas"]) < _MIN_PAIRS:
        missing = f"{body.language} lemmas with a {body.target_language} pair"
        raise NoRoundContentError(missing)

    # Store round for submit calls
    round_key = f"{user.user_id}:pair_matching"
    _active_rounds[round_key] = (exercise, round_)

    return ExerciseResponse(
        status="ok",
        data={
            "left_lemmas": round_.prompt["left_lemmas"],
            "right_lemmas": round_.prompt["right_lemmas"],
        },
    )


class PairMatchingSubmitRequest(BaseModel):
    """Request body to submit a pair match."""

    left: str
    right: str


@router.post("/pair-matching/submit")
async def pair_matching_submit(
    body: PairMatchingSubmitRequest,
    user: Annotated[SessionData, Depends(get_current_user)],
) -> ExerciseResponse:
    """Submit a single pair match."""
    round_key = f"{user.user_id}:pair_matching"
    state = _active_rounds.get(round_key)
    if not state:
        raise HTTPException(status_code=400, detail="No active pair matching game.")
    exercise, round_ = state
    result = exercise.submit(round_, (body.left, body.right))
    return ExerciseResponse(
        status="ok",
        data={
            "correct": result.correct,
            "left": body.left,
            "right": body.right,
            "feedback": result.feedback,
        },
    )


@router.post("/wordle/start")
async def wordle_start(
    body: WordleStartRequest,
    user: Annotated[SessionData, Depends(get_current_user)],
) -> ExerciseResponse:
    """Start a new wordle game around a level-appropriate single word."""
    query = CardQuery(
        language=body.language,
        known_languages=get_learner_params().known_languages,
        length=body.word_length,
        single_word=True,
        max_cefr=body.max_cefr,
    )
    cards = _draw(user, query, 1)
    if not cards:
        missing = f"{body.word_length}-letter words for {body.language}"
        raise NoRoundContentError(missing)
    exercise = WordleExercise(
        progress_callback=get_progress_service().recorder(user.user_id, "wordle"),
    )
    round_ = exercise.start(cards[0].lemma)

    round_key = f"{user.user_id}:wordle"
    _active_rounds[round_key] = (exercise, round_)

    return ExerciseResponse(
        status="ok",
        data={
            "word_length": round_.prompt["word_length"],
            "max_attempts": round_.prompt["max_attempts"],
        },
    )


@router.post("/wordle/guess")
async def wordle_guess(
    body: WordleGuessRequest,
    user: Annotated[SessionData, Depends(get_current_user)],
) -> ExerciseResponse:
    """Submit a wordle guess."""
    round_key = f"{user.user_id}:wordle"
    state = _active_rounds.get(round_key)
    if not state:
        raise HTTPException(status_code=400, detail="No active wordle game.")
    exercise, round_ = state
    result = exercise.submit(round_, body.guess)
    guesses = round_.prompt["guesses"]
    results = round_.prompt["results"]
    max_attempts: int = round_.prompt["max_attempts"]
    finished = result.correct or len(guesses) >= max_attempts
    data: dict[str, Any] = {
        "letters": results[-1] if results else [],
        "finished": finished,
        "correct": result.correct,
        "attempts_left": max_attempts - len(guesses),
        "keyboard_state": round_.prompt["keyboard_state"],
    }
    if finished:
        data["answer"] = round_.expected.target.text
        del _active_rounds[round_key]
    return ExerciseResponse(status="ok", data=data)


@router.post("/diacritic-typing/start")
async def diacritic_start(
    body: DiacriticStartRequest,
    user: Annotated[SessionData, Depends(get_current_user)],
) -> ExerciseResponse:
    """Start a new diacritic typing round on an accented single word."""
    query = CardQuery(
        language=body.language,
        known_languages=get_learner_params().known_languages,
        gloss_language=body.hint_language,
        translation_languages=[body.hint_language],
        accented_only=True,
        single_word=True,
        min_length=_MIN_WORD_LENGTH,
        max_cefr=body.max_cefr,
    )
    cards = _draw(user, query, 1)
    if not cards:
        missing = f"accented lemmas for {body.language}"
        raise NoRoundContentError(missing)
    exercise = DiacriticTypingExercise(
        progress_callback=get_progress_service().recorder(
            user.user_id,
            "diacritic_typing",
        ),
    )
    round_ = exercise.start(
        cards[0],
        hint_level=body.hint_level,
        hint_language=body.hint_language,
    )

    round_key = f"{user.user_id}:diacritic"
    _active_rounds[round_key] = (exercise, round_)

    return ExerciseResponse(
        status="ok",
        data={
            "display": round_.prompt["display"],
            "glosses": round_.prompt["glosses"],
            "word_length": len(round_.prompt["display"]),
            "translation": round_.prompt["translation"],
        },
    )


@router.post("/diacritic-typing/keystroke")
async def diacritic_keystroke(
    body: DiacriticKeystrokeRequest,
    user: Annotated[SessionData, Depends(get_current_user)],
) -> ExerciseResponse:
    """Submit a keystroke for diacritic typing."""
    round_key = f"{user.user_id}:diacritic"
    state = _active_rounds.get(round_key)
    if not state:
        raise HTTPException(
            status_code=400,
            detail="No active diacritic game.",
        )
    exercise, round_ = state
    result = exercise.submit(round_, body.character)
    data: dict[str, Any] = {
        "display": round_.prompt["display"],
        "correct_so_far": result.correct,
        "finished": len(result.lemma_results) > 0,
        "errors": round_.expected.error_count,
    }
    if len(result.lemma_results) > 0:
        del _active_rounds[round_key]
    return ExerciseResponse(status="ok", data=data)


@router.post("/sentence-reconstruction/start")
async def reconstruction_start(
    body: ReconstructionStartRequest,
    user: Annotated[SessionData, Depends(get_current_user)],
) -> ExerciseResponse:
    """Start a sentence reconstruction round from a concept example sentence.

    The corpus has example sentences for en and it, plus a small curated set for
    pt, es, and fr. The prompt names the drilled lemma and its meaning; the
    sentence itself carries no stored translation.
    """
    query = CardQuery(
        language=body.language,
        known_languages=get_learner_params().known_languages,
        gloss_language=body.hint_language,
        translation_languages=[body.hint_language],
        require_example=True,
        # A concept's examples are shared by all of its lemmas: a sentence for
        # "casa" says nothing about "lar".
        example_mentions_lemma=True,
        max_cefr=body.max_cefr,
    )
    picked = _sentence_using_lemma(_draw(user, query, _SENTENCE_CANDIDATES))
    if picked is None:
        missing = f"example sentences for {body.language}"
        raise NoRoundContentError(missing)
    card, sentence = picked
    exercise = SentenceReconstructionExercise(
        progress_callback=get_progress_service().recorder(
            user.user_id,
            "sentence_reconstruction",
        ),
    )
    round_ = exercise.start(
        sentence=sentence,
        translation=_sentence_hint(card, body.hint_language),
        lemma_id=card.lemma.id,
    )

    round_key = f"{user.user_id}:reconstruction"
    _active_rounds[round_key] = (exercise, round_)

    return ExerciseResponse(
        status="ok",
        data={
            "translation": round_.prompt["translation"],
            "portions": round_.prompt["portions"],
        },
    )


@router.post("/sentence-reconstruction/submit")
async def reconstruction_submit(
    body: ReconstructionSubmitRequest,
    user: Annotated[SessionData, Depends(get_current_user)],
) -> ExerciseResponse:
    """Submit a reconstruction attempt."""
    round_key = f"{user.user_id}:reconstruction"
    state = _active_rounds.get(round_key)
    if not state:
        raise HTTPException(
            status_code=400,
            detail="No active reconstruction game.",
        )
    exercise, round_ = state
    result = exercise.submit(round_, body.selected_portions)
    # One attempt per sentence: the page shows the answer on a miss.
    del _active_rounds[round_key]
    return ExerciseResponse(
        status="ok",
        data={
            "correct": result.correct,
            "finished": True,
            "answer": " ".join(round_.expected),
        },
    )


def _sentence_using_lemma(cards: list[LemmaCard]) -> tuple[LemmaCard, str] | None:
    """Return the first card with an example that contains its lemma's text.

    The card query already keeps cards with such an example; this picks the
    sentence itself among the concept's examples. The match is a case-folded
    substring, so an inflected form that starts with the lemma (pt "casas")
    still counts. When no example names its lemma, the first card's first
    example is used.
    """
    for card in cards:
        needle = card.lemma.text.casefold()
        for sentence in card.examples:
            if needle in sentence.casefold():
                return card, sentence
    for card in cards:
        if card.examples:
            return card, card.examples[0]
    return None


def _sentence_hint(card: LemmaCard, hint_language: str) -> str:
    """Return the reconstruction prompt: the drilled lemma and its meaning."""
    meaning = next(iter(card.translations.get(hint_language, [])), None)
    if card.lemma.language == hint_language or meaning is None:
        meaning = card.gloss or ""
    return f"A sentence with “{card.lemma.text}” ({meaning})"


@router.post("/conversational-tutor/message")
async def tutor_message(
    body: TutorMessageRequest,
    user: Annotated[SessionData, Depends(get_current_user)],
) -> ExerciseResponse:
    """Send a message to the conversational tutor."""
    history_key = f"{user.email}:tutor"
    history = _tutor_histories.setdefault(history_key, [])

    history.append(TutorMessage(role="user", content=body.text))
    result = tutor_reply(
        body.text,
        history,
        language=body.language,
        topic=body.topic,
    )

    correction_text = (
        result.correction.content if result.correction.content.strip() else None
    )
    reply = TutorMessage(
        role="tutor",
        content=result.conversation.content,
        translation=result.conversation.translation or None,
        correction=correction_text,
    )
    history.append(reply)

    errors = [
        {"original": e.original, "corrected": e.corrected, "explanation": e.explanation}
        for e in result.correction.errors
    ]

    return ExerciseResponse(
        status="ok",
        data={
            "response": {
                "content": result.conversation.content,
                "translation": result.conversation.translation or None,
                "correction": correction_text,
                "errors": errors,
            },
        },
    )
