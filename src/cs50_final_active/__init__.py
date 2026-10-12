from flask import Flask
import os

from .pages import bp as pages_bp


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY=os.environ["SECRET_KEY"])
    app.register_blueprint(pages_bp)
    return app