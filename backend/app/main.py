"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database.neo4j_client import close_neo4j
from app.api import health, contracts, graph, analyze


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    log = logging.getLogger("lexgraph")
    log.info("Starting LexGraph AI — seeding knowledge graph from %s", settings.data_path)
    try:
        from app.services.seed import run_seed
        await run_seed()
        log.info("Knowledge graph ready")
    except Exception as e:
        log.warning("Seed failed (%s) — API will serve empty graph", e)
    yield
    log.info("Shutting down LexGraph AI")
    await close_neo4j()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="LexGraph AI",
        version="0.1.0",
        description="Legal intelligence: find what is missing from a contract.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(contracts.router)
    app.include_router(graph.router)
    app.include_router(analyze.router)

    @app.get("/")
    async def root():
        return {"service": "lexgraph-ai", "version": "0.1.0"}

    return app


app = create_app()
