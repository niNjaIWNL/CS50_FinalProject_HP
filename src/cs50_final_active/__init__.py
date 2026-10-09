from flask import Flask

from .pages import bp as pages_bp


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY="dev")
    app.register_blueprint(pages_bp)
    return app