from flask import Flask
from routes.search import search_bp
from routes.user import user_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(search_bp)
app.register_blueprint(user_bp)

if __name__ == '__main__':
    app.run(debug=True)
