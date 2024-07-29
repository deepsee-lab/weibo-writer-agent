# -*- coding: utf-8 -*-
# Standard library imports.
import sqlite3
# Related third party imports.
from flask import Flask, Blueprint,render_template,request,jsonify,url_for
from loguru import logger
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOllama
# Local application/library specific imports.


bp = Blueprint("weibo_UI", __name__, url_prefix='/weibo_UI',static_folder='static',template_folder='templates')

@bp.route('/index' )
def show():
    username="lnform"
    return render_template('index.html',username=username)

@bp.route('/choose_model')
def choose_model():
    username="lnform"
    return render_template('choose_model.html',username=username)
        
@bp.route('/choose_model_post',methods=["POST"])
def choose_model_post():
    if request.method == "POST":
        type_name=request.form.get('type_name')
        print('+++',type_name)
        choose_dict={}
        choose_dict['result']=1
        return jsonify(choose_dict)
        
@bp.route('/model_run',methods=["POST"])
def model_run():
    if request.method == "POST":
        type_name=request.form.get('type_name')
        model_select=request.form.get('model_select')
        split_document=request.form.get('split_document')
        vector_select=request.form.get('vector_select')
        query=request.form.get('query')
        #split
        documents=url_for('split_document',split_document)
        db=url_for('vector',documents,vector_select)
        qa_chain = RetrievalQA.from_chain_type(
            llm = ChatOllama(model=model_select),  # 语言模型
            chain_type="stuff",  # prompt的组织方式，后面细讲
            retriever=db.as_retriever()  # 检索器
        )
        response = qa_chain.run(query)
        choose_dict={}
        choose_dict['result']=1
        choose_dict['content']=response
        return jsonify(choose_dict)