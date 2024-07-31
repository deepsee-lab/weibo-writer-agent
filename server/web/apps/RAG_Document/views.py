# -*- coding: utf-8 -*-
# Standard library imports.
import sqlite3,os
# Related third party imports.
from flask import Flask, Blueprint,render_template,jsonify,request,url_for
from loguru import logger
from werkzeug.utils import secure_filename
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.word_document import UnstructuredWordDocumentLoader
from typing import List
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
# Local application/library specific imports.


bp = Blueprint("RAG_Document", __name__, url_prefix='/RAG_Document')


@bp.route('/heartbeat2')
def heartbeat2():
    logger.info('run heartbeat')
    return 'heartbeat2'

@bp.route('/upload',methods=['GET','POST'])
def upload():
    if request.method == "POST":
        f = request.files['file']
        f.save(os.path.join('/mnt/d/code/python/webo_write/flask/weibo-writer-agent/server/apps/RAG_Document/static/', secure_filename(f.filename)))
        return 'upload success'

@bp.route('/split_document')
def split_document(split_type):
    pdf_file='/mnt/d/code/python/webo_write/flask/weibo-writer-agent/server/apps/RAG_Document/static/123.pdf'
    if 'normal' in split_type:
        documents=url_for('normal_split',document_file=pdf_file)
    return documents

@bp.route('/normal_split')
def normal_split(document_file):
    def get_file_extension(filename: str) -> str:
        return filename.split(".")[-1]
    class FileLoadFactory:
        def get_loader(filename: str):
            ext = get_file_extension(filename)
            if ext == "pdf":
                return PyPDFLoader(filename)
            elif ext == "docx" or ext == "doc":
                return UnstructuredWordDocumentLoader(filename)
            else:
                raise NotImplementedError(f"File extension {ext} not supported.")
    def load_docs(filename: str) -> List[Document]:
        file_loader = FileLoadFactory.get_loader(filename)
        pages = file_loader.load_and_split()
        return pages
    raw_docs = load_docs(document_file)
    if len(raw_docs) == 0:
        return "抱歉，文档内容为空"
    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=200,
                        chunk_overlap=60,
                        length_function=len,
                        add_start_index=True,
                    )
    documents = text_splitter.split_documents(raw_docs)
    if documents is None or len(documents) == 0:
        return "无法读取文档内容"
    return documents