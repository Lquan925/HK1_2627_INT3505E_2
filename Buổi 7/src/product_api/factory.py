import os

import click
from flask import Flask

from .config import Config
from .extensions import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, instance_path=Config.INSTANCE_PATH)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    from .api.products import products_bp
    from .api.errors import register_error_handlers

    from .api.orders import orders_bp
    from .api.health import health_bp

    app.register_blueprint(orders_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(products_bp)
    register_error_handlers(app)

    @app.cli.command("init-db")
    def init_db():
        """Create database tables without deleting existing data."""
        db.create_all()
        click.echo("Database initialized.")

    return app
