# web/__init__.py
from flask import Flask
from web.routes import register_routes
from web.webhook import register_webhook

def create_flask_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Register routes
    register_routes(app)
    register_webhook(app)
    
    return app