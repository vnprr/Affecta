from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from clinical_rag_agent.api import health_routes, ingest_routes, metrics_routes, openai_routes, session_routes
from clinical_rag_agent.config import get_settings
from clinical_rag_agent.services.container import create_container


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.state.container = create_container(settings)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_routes.router)
    app.include_router(metrics_routes.router)
    app.include_router(openai_routes.router)
    app.include_router(ingest_routes.router)
    app.include_router(session_routes.router)
    return app


app = create_app()

