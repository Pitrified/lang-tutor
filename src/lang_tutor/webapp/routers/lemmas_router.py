"""Lemma browsing page routes.

Serves pages for browsing and viewing vocabulary lemmas.
"""

from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_tools.schemas.auth import SessionData

from lang_tutor.content import get_content_source
from lang_tutor.webapp.core.auth import get_current_user

router = APIRouter(prefix="/lemmas", tags=["lemmas"])


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def lemma_list(
    request: Request,
    user: Annotated[SessionData, Depends(get_current_user)],
    language: Annotated[str | None, Query()] = None,
    topic: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    """Render lemma browsing page with optional filters."""
    lemmas = get_content_source().get_lemmas_filtered(language=language, topic=topic)
    templates = request.app.state.templates
    return templates.TemplateResponse(
        request,
        "pages/lemmas/index.html",
        {
            "user": user,
            "active_page": "lemmas",
            "language_filter": language,
            "topic_filter": topic,
            "lemmas": lemmas,
        },
    )


@router.get("/partial", response_class=HTMLResponse, include_in_schema=False)
async def lemma_list_partial(
    request: Request,
    user: Annotated[SessionData, Depends(get_current_user)],
    language: Annotated[str | None, Query()] = None,
    topic: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    """Return only the lemma table partial (for HTMX filter updates)."""
    lemmas = get_content_source().get_lemmas_filtered(language=language, topic=topic)
    templates = request.app.state.templates
    return templates.TemplateResponse(
        request,
        "pages/lemmas/_lemma_table.html",
        {"lemmas": lemmas},
    )


@router.get("/{lemma_id}", response_class=HTMLResponse, include_in_schema=False)
async def lemma_detail(
    request: Request,
    lemma_id: str,
    user: Annotated[SessionData, Depends(get_current_user)],
) -> HTMLResponse:
    """Render lemma detail page."""
    lemma = get_content_source().get_lemma_by_id(lemma_id)
    templates = request.app.state.templates
    return templates.TemplateResponse(
        request,
        "pages/lemmas/detail.html",
        {
            "user": user,
            "active_page": "lemmas",
            "lemma_id": lemma_id,
            "lemma": lemma,
        },
    )
