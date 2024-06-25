from flask import Flask

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
