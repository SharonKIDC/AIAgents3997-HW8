"""FastAPI backend application for web UI.

Creates and configures the FastAPI application for serving
the React frontend.
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Convert Pydantic validation errors to user-friendly format."""
        validation_errors = {}
        for error in exc.errors():
            # Get field name from location (e.g., ["body", "building_number"])
            loc = error.get("loc", [])
            field = loc[-1] if loc else "unknown"
            msg = error.get("msg", "Invalid value")

            # Create user-friendly error messages
            if "int_parsing" in error.get("type", ""):
                msg = f"{field.replace('_', ' ').title()} must be a valid number"
            elif "missing" in error.get("type", ""):
                msg = f"{field.replace('_', ' ').title()} is required"

            if field not in validation_errors:
                validation_errors[field] = []
            validation_errors[field].append(msg)

        return JSONResponse(
            status_code=200,  # Return 200 so frontend handles it consistently
            content={
                "success": False,
                "validation_errors": validation_errors,
                "message": "Please fix the validation errors",
            },
        )

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "web-ui"}

    static_path = Path(__file__).parent / "static"
    if static_path.exists():
        app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")

    return app


web_app = create_web_app()
