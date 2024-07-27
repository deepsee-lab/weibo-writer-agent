# -*- coding: utf-8 -*-
# Standard library imports.
import sqlite3
# Related third party imports.
from flask import Flask
from loguru import logger
# Local application/library specific imports.
from configs import config
from extends import (
    db,
)
from apps.demo.models import DemoModel
from apps.demo import bp as demo_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(demo_bp)

    db.init_app(app)

    return app


app = create_app()

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
