"""Flask application factory for the Generic vs. Branded Medicine Finder."""
from flask import Flask

from .api import register_routes

def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )
    register_routes(app)
    return app


app = create_app()
