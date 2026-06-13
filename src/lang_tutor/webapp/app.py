"""Application instance for uvicorn.

Entry point: uvicorn lang_tutor.webapp.app:app
"""

from lang_tutor.webapp.main import build_app

# Create application instance
app = build_app()

if __name__ == "__main__":
    import uvicorn

    from lang_tutor.params.lang_tutor_params import get_webapp_params

    params = get_webapp_params()
    uvicorn.run(
        "lang_tutor.webapp.app:app",
        host=params.host,
        port=params.port,
        reload=params.debug,
    )
