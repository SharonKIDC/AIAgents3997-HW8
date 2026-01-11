"""FastAPI backend application for web UI.

Creates and configures the FastAPI application for serving
the React frontend.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.config import get_config
from src.web_ui.routes import router


def create_web_app() -> FastAPI:
    """Create and configure the web UI FastAPI application."""
    config = get_config()
    app = FastAPI(
        title="Tenant Management Web UI",
        description="Web interface for residential complex tenant management",
        version="1.0.0",
    )
    if config.get("web_ui.enable_cors", True):
        origins = config.get("web_ui.allowed_origins", ["http://localhost:3000"])
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    app.include_router(router)

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "web-ui"}

    static_path = Path(__file__).parent / "static"
    if static_path.exists():
        app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")

    return app


web_app = create_web_app()
