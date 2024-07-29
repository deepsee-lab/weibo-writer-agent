# -*- coding: utf-8 -*-
# Standard library imports.
import sqlite3
# Related third party imports.
from flask import Flask, Blueprint,render_template,request
from loguru import logger
from langchain_community.vectorstores import Chroma
from langchain_community import embeddings
# Local application/library specific imports.


bp = Blueprint("RAG_Vector", __name__, url_prefix='/RAG_Vector')

@bp.route('/heartbeat1')
def heartbeat1():
    logger.info('run heartbeat')
    return 'heartbeat1'

@bp.route('/vector')
def vector(documents,vector_type):
    if 'chroma' in vector_type:
        db = Chroma.from_documents(documents, embeddings.OllamaEmbeddings(model='nomic-embed-text'),persist_directory='data')
        db.persist()
        return db