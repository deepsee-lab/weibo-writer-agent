# -*- coding: utf-8 -*-
# Standard library imports.
import os
import sqlite3
# Related third party imports.
from flask import Flask
from loguru import logger
# Local application/library specific imports.
from configs import config
from extends import (
    db,
)
from apps.wpp import bp as wpp_bp
# TODO: Import new blueprint here


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(wpp_bp)
    # TODO: Register new blueprint here
    db.init_app(app)

    return app


app = create_app()

with app.app_context():
    db.create_all()

host = '127.0.0.1'
port = 4000
debug = True

logger.info('Server is up and running.')
logger.info('Please visit http://{}:{}/wpp/heartbeat to verify.'.format(host, port))

if __name__ == '__main__':
    app.run(debug=debug, host=host, port=port)
