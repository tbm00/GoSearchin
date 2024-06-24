from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    with app.app_context():
        # Register Blueprints
        from .routes.search import search_bp
        from .routes.user import user_bp

        app.register_blueprint(search_bp)
        app.register_blueprint(user_bp)

    return app