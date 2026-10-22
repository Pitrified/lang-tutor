"""Lemma browsing page routes.

Serves pages for browsing and viewing vocabulary lemmas. The list is a paged,
prefix-searchable view over the `lang-tools` corpus (324k lemmas, so never the
whole pool); the detail page shows every meaning of a lemma as one drill card
per sense.
"""

from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_tools.schemas.auth import SessionData

from lang_tutor.content import get_content_source
from lang_tutor.webapp.core.auth import get_current_user

router = APIRouter(prefix="/lemmas", tags=["lemmas"])

#: Lemmas per page of the browser.
PAGE_SIZE = 50

#: The corpus languages, in the order the language filter lists them.
LANGUAGES: tuple[tuple[str, str], ...] = (
    ("pt", "Portuguese"),
    ("es", "Spanish"),
    ("fr", "French"),
    ("it", "Italian"),
    ("en", "English"),
)


def _list_context(
    language: str | None,
    topic: str | None,
    q: str | None,
    offset: int,
) -> dict[str, object]:
    """Return the template context shared by the full page and the partial."""
    language, topic, q = (value or None for value in (language, topic, q))
    page = get_content_source().get_lemma_page(
        language=language,
        topic=topic,
        query=q,
        limit=PAGE_SIZE,
        offset=offset,
    )
    filters = {"language": language, "topic": topic, "q": q}
    return {
        "lemmas": page.lemmas,
        "total": page.total,
        "offset": offset,
        "page_size": PAGE_SIZE,
        "page_query": urlencode({k: v for k, v in filters.items() if v}),
        "language_filter": language,
        "topic_filter": topic,
        "query": q,
        "languages": LANGUAGES,
    }


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def lemma_list(
    request: Request,
    user: Annotated[SessionData, Depends(get_current_user)],
    language: Annotated[str | None, Query()] = None,
    topic: Annotated[str | None, Query()] = None,
    q: Annotated[str | None, Query()] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> HTMLResponse:
    """Render the lemma browser with optional filters."""
    templates = request.app.state.templates
    return templates.TemplateResponse(
        request,
        "pages/lemmas/index.html",
        {
            "user": user,
            "active_page": "lemmas",
            **_list_context(language, topic, q, offset),
        },
    )


@router.get("/partial", response_class=HTMLResponse, include_in_schema=False)
async def lemma_list_partial(
    request: Request,
    user: Annotated[SessionData, Depends(get_current_user)],
    language: Annotated[str | None, Query()] = None,
    topic: Annotated[str | None, Query()] = None,
    q: Annotated[str | None, Query()] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> HTMLResponse:
    """Return only the lemma table partial (for HTMX filter and page updates)."""
    templates = request.app.state.templates
    return templates.TemplateResponse(
        request,
        "pages/lemmas/_lemma_table.html",
        _list_context(language, topic, q, offset),
    )


@router.get("/{lemma_id}", response_class=HTMLResponse, include_in_schema=False)
async def lemma_detail(
    request: Request,
    lemma_id: str,
    user: Annotated[SessionData, Depends(get_current_user)],
) -> HTMLResponse:
    """Render a lemma with every meaning (one card per sense, best first)."""
    source = get_content_source()
    lemma = source.get_lemma_by_id(lemma_id)
    senses = (
        source.get_sense_cards(
            lemma_id,
            translation_languages=[code for code, _ in LANGUAGES],
        )
        if lemma is not None
        else []
    )
    templates = request.app.state.templates
    return templates.TemplateResponse(
        request,
        "pages/lemmas/detail.html",
        {
            "user": user,
            "active_page": "lemmas",
            "lemma_id": lemma_id,
            "lemma": lemma,
            "senses": senses,
        },
    )
