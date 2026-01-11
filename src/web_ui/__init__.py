"""React web interface for tenant management.

Provides FastAPI backend endpoints for the React frontend.
"""

from src.web_ui.backend import create_web_app
from src.web_ui.routes import router

__all__ = ["create_web_app", "router"]
