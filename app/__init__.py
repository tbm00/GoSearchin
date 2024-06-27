# app.__init__.py

from flask import Flask

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    from .search import search_bp
    app.register_blueprint(search_bp)

    return app
