"""Application factory and entry point.

Run with::

    uvicorn app.main:app --reload
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import config
from .controller import extraction_controller, gmail_controller
from .model.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("email_extraction")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(title="Email Business Info Extractor", version="1.0.0")

    init_db()

    if not config.ADMIN_AUTH_ENABLED:
        logger.warning(
            "Admin panel and Gmail routes are UNPROTECTED. Set ADMIN_USERNAME "
            "and ADMIN_PASSWORD to require authentication."
        )
    if not config.GROQ_API_KEY:
        logger.warning(
            "GROQ_API_KEY is not set; extraction requests will fail until it "
            "is configured."
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    config.STATIC_DIR.mkdir(parents=True, exist_ok=True)
    app.mount(
        "/static",
        StaticFiles(directory=str(config.STATIC_DIR)),
        name="static",
    )

    app.include_router(extraction_controller.router)
    app.include_router(gmail_controller.router)
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
