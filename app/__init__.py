"""Initialize Flask app."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from ddtrace import patch_all

db = SQLAlchemy()
patch_all()

def create_app():
    """Construct the core application."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@127.0.0.1:8889/videoDevo"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

    db.init_app(app)

    with app.app_context():
        from . import routes  # Import routes

        db.create_all()  # Create database tables for our data models

        return app