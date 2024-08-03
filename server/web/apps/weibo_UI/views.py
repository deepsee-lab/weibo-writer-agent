# -*- coding: utf-8 -*-
# Standard library imports.
import sqlite3,os,json,re
# Related third party imports.
from flask import Flask, Blueprint,render_template,request,jsonify,url_for,current_app
from loguru import logger
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOllama
from werkzeug.utils import secure_filename
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
        url = "http://127.0.0.1:5020"
        headers = {"Content-Type": "application/json"}
        data = {
          "model": "qwen2:7b",
          "prompt": query
        }
        # 发送请求并存储响应
        response = request.post(url, headers=headers, data=json.dumps(data))
        # 检查响应状态代码
        if response.status_code == 200:
            # 打印响应文本
            answer=''
            for item in response.text.split():
              try:
                qqq=json.loads(item)
                answer+=qqq["response"]
                #print(qqq["response"])
              except:
                print(item)
        response = answer
        choose_dict={}
        choose_dict['result']=1
        choose_dict['content']="这里是要插入的文字"
        #choose_dict['content']=response
        return jsonify(choose_dict)
    
@bp.route('/upload',methods=['GET','POST'])
def upload():
    if request.method == "POST":
        f = request.files['file']
        _filename_ascii_add_strip_re = re.compile(r'[^A-Za-z0-9_\u4E00-\u9FBF\u3040-\u30FF\u31F0-\u31FF.-]')
        filename = str(_filename_ascii_add_strip_re.sub('', '_'.join( # 新的正则
                f.filename.split()))).strip('._')
        filename=secure_filename(filename)
        save_path=os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        print(save_path)
        content="1234"
        with open(save_path,"w") as fp:
	        fp.write(content)
        #f.save(save_path)
        return 'upload success'