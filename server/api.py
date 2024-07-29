      
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
from apps.weibo_UI import bp as weibo_bp
from apps.RAG_Vector import bp as vector_bp
from apps.RAG_Document import bp as document_bp
#from apps.Inference import bp as inference_bp
#from apps.Content_Creator import bp as content_creator_bp
# TODO: Import new blueprint here


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(demo_bp)
    app.register_blueprint(weibo_bp)
    app.register_blueprint(vector_bp)
    app.register_blueprint(document_bp)
    #app.register_blueprint(inference_bp)
    #app.register_blueprint(content_creator_bp)
    # TODO: Register new blueprint here
    db.init_app(app)

    return app


app = create_app()
with app.app_context():
    db.create_all()

host = '127.0.0.1'
port = 5000

logger.info('Server is up and running.')
logger.info('Please visit http://{}:{}/demo/heartbeat to verify.'.format(host, port))

if __name__ == '__main__':
    app.run(host=host, port=port)

    