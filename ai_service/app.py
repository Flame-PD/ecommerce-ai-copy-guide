"""FastAPI application entrypoint for the AI Intelligent Service Layer.

Starts a Uvicorn server exposing the AI gateway.

Usage::

    python -m ai_service.app
    # or
    uvicorn ai_service.app:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai_service.config.settings import get_settings
from ai_service.gateway.router import router
from ai_service.utils.logger import logger


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown logic.

    On startup:
        - Ensure the FAISS data directory exists.
        - Attempt to load an existing FAISS index from disk.
        - Log configuration summary.

    On shutdown:
        - (Reserved for graceful resource cleanup.)
    """
    settings = get_settings()

    # -- ensure data directory exists ----------------------------------------
    data_dir = Path(settings.FAISS_INDEX_PATH).parent
    data_dir.mkdir(parents=True, exist_ok=True)

    # -- attempt to restore a previously saved index -------------------------
    _try_load_existing_index()

    logger.info(
        "=" * 60 + "\n"
        "  AI Service Layer starting …\n"
        "  Model  : {} @ {}\n"
        "  Embed  : {}\n"
        "  Top-K  : {}\n"
        "  Server : {}:{}\n"
        "=".format(
            settings.MODEL_NAME,
            settings.BASE_URL,
            settings.EMBEDDING_MODEL,
            settings.TOP_K,
            settings.HOST,
            settings.PORT,
        ),
    )

    yield  # --- application runs here ---

    logger.info("AI Service Layer shutting down")


def _try_load_existing_index() -> None:
    """Try to restore a previously persisted FAISS index at startup.

    If the index files exist, they are loaded into the global retriever
    singleton so the knowledge base survives restarts.  Failures are
    logged but do not prevent startup — the user can always call
    ``POST /api/v1/ingest`` to rebuild.
    """
    from pathlib import Path as _Path

    from ai_service.gateway.router import _get_retriever
    from ai_service.rag.vector_store import VectorStore

    settings = get_settings()
    index_dir = _Path(settings.FAISS_INDEX_PATH)

    if not (index_dir / "index.faiss").is_file():
        logger.info("No existing FAISS index found — starting with empty knowledge base")
        return

    try:
        store = VectorStore.load(str(index_dir))
        retriever = _get_retriever()
        retriever._store = store  # inject the loaded store
        logger.success("Restored FAISS index from {} | {} docs", index_dir, store.count)
    except Exception:
        logger.warning("Failed to load existing FAISS index — starting with empty knowledge base")
        logger.exception("Load error details")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

settings = get_settings()

app = FastAPI(
    title="E-Commerce AI Copy Guide — AI Service Layer",
    description="Intelligent e-commerce assistant: title & description generation, "
    "RAG-powered Q&A, review sentiment analysis, product recommendations, "
    "and livestream script generation.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

app.include_router(router)


# ---------------------------------------------------------------------------
# Health-check at root
# ---------------------------------------------------------------------------

@app.get("/", tags=["Root"])
async def root():
    """Redirect to the API docs."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "ai_service.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
