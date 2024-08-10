# -*- coding: utf-8 -*-
# Standard library imports.
import sqlite3,os,json,re,requests
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
        choose_dict={}
        choose_dict['result']=1
        return jsonify(choose_dict)
        
@bp.route('/model_run',methods=["POST"])
def model_run():
    if request.method == "POST":
        
        data = request.get_json()
        type_name=data['type_name']
        model_select=data['model_name']
        KB_id=data['KB_id']
        top_selector=data['top_selector']
        top_K=int(top_selector)
        query=data['query']
        logger.info(query)
        url = 'http://127.0.0.1:6020/vector/search'
        json_data = {
            "kb_id": KB_id,
            "query": query,
            "top_k": top_K,
            "output_fields": [
              "text"
            ]
        }
        # 发送请求并存储响应
        response_p = requests.post(url, json=json_data)
        logger.info(response_p.json())
        # 检查响应状态代码
        res_p=''
        instruction_temp=''
        answer_p=response_p.json()
        if answer_p['message'] == 'success':
            # 打印响应文本
            res_p=answer_p['data']['results']
            instruction_temp=res_p[0][0]['entity']['text']
        instruction='你的任务是根据已知内容回答问题，已知：'+instruction_temp
        prompt = f"""
        # 目标
        {instruction}

        # 用户输入
        {query}
        """
        url = 'http://127.0.0.1:4010/private/inference'
        json_data = {
            "messages": [
                {
                  "role": "user",
                  "content": prompt
                }
            ],
            "inference_service": "ollama",
            "model": "qwen2:1.5b-instruct-fp16",
            "max_tokens": 4096,
            "stream": False,
            "temperature": 0.8,
            "timeout": 60
        }
        # 发送请求并存储响应
        response = requests.post(url, json=json_data)
        print(response.json())
        # 检查响应状态代码
        res=''
        answer=response.json()
        if answer['message'] == 'success':
            # 打印响应文本
            res=answer['data']['result']
        choose_dict={}
        choose_dict['result']=1
        choose_dict['content']=res
        #choose_dict['content']=response
        return jsonify(choose_dict)
    
@bp.route('/upload',methods=['GET','POST'])
def upload():
    username='lnform'
    if request.method == "POST":
        f = request.files['file']
        _filename_ascii_add_strip_re = re.compile(r'[^A-Za-z0-9_\u4E00-\u9FBF\u3040-\u30FF\u31F0-\u31FF.-]')
        filename = str(_filename_ascii_add_strip_re.sub('', '_'.join( # 新的正则
                f.filename.split()))).strip('._')
        filename=secure_filename(filename)
        save_path=os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            os.mkdir(current_app.config['UPLOAD_FOLDER'])
        f.save(save_path)
        return 'upload success'
    return render_template('upload_Document.html',username=username)

@bp.route('/Pic_upload',methods=['POST'])
def Pic_upload():
    if request.method == "POST":
        f = request.files['file']
        _filename_ascii_add_strip_re = re.compile(r'[^A-Za-z0-9_\u4E00-\u9FBF\u3040-\u30FF\u31F0-\u31FF.-]')
        filename = str(_filename_ascii_add_strip_re.sub('', '_'.join( # 新的正则
                f.filename.split()))).strip('._')
        filename=secure_filename(filename)
        save_path=os.path.join(current_app.config['UPLOAD_FOLDER_PIC'], filename)
        if not os.path.exists(current_app.config['UPLOAD_FOLDER_PIC']):
            os.mkdir(current_app.config['UPLOAD_FOLDER_PIC'])
        f.save(save_path)
        return 'upload success'

@bp.route('/self_media',methods=["POST","GET"])
def self_media():
    if request.method == "POST":
        data = request.get_json()
        if 'send_draft' in data['Type']:
            type_name=data['type_name']
            model_select=data['model_name']
            #split_document=data['split_document']
            vector_select=data['vector_select']
            title=data['title']
            thumb_media_id=data['thumb_media_id']
            query='以'+str(title)+'为题，写一篇文章'
            url = 'http://127.0.0.1:4010/private/inference'
            json_data = {
                "messages": [
                    {
                    "role": "user",
                    "content": query
                    }
                ],
                "inference_service": "ollama",
                "model": "qwen2:1.5b-instruct-fp16",
                "max_tokens": 4096,
                "stream": False,
                "temperature": 0.8,
                "timeout": 60
            }
            # 发送请求并存储响应
            response = requests.post(url, json=json_data)
            print(response.json())
            # 检查响应状态代码
            res=''
            answer=response.json()
            choose_dict={}
            choose_dict['result']=0
            if answer['message'] == 'success':
                # 打印响应文本
                res=answer['data']['result']
                url_self_media= 'http://127.0.0.1:6050/wpp/draft_add'
                json_data_self_media = {
                    "title": title,
                    "content": res,
                    "thumb_media_id": thumb_media_id
                }
                # 发送请求并存储响应
                response_self_media = requests.post(url_self_media, json=json_data_self_media)
                self_media_res=response_self_media.json()
                if self_media_res['success']:
                    choose_dict['result']=1
            choose_dict['content']=res
            #choose_dict['content']=response
            return jsonify(choose_dict)
        elif 'selec_picture' in data['Type']:
            filepath=current_app.config['UPLOAD_FOLDER_PIC']
            files=os.listdir(filepath)
            file_dict={}
            file_dict['list']=files
            return jsonify(file_dict)
    username="lnform"
    return render_template('self_media.html',username=username)
  
@bp.route('/submit_kb',methods=["POST","GET"])
def submit_kb():
    if request.method == "POST":
        data = request.get_json()
        #({'Dim':Dim,'Kb_id':Kb_id,'Kb_name':Kb_name,'desc':desc,'vector_store_name':vector_store_name,'embedding_model_name':embedding_model_name}),
        Dim=data['Dim']
        Dim=int(Dim)
        Kb_id=data['Kb_id']
        Kb_name=data['Kb_name']
        desc=data['desc']
        vector_store_name=data['vector_store_name']
        embedding_model_name=data['embedding_model_name']
        url = 'http://127.0.0.1:6020/vector/kb_add_one'
        json_data = {
          "kb_id": Kb_id,
          "kb_name": Kb_name,
          "kb_desc": desc,
          "vector_store_name": vector_store_name,
          "embedding_model_name": embedding_model_name,
          "dim": Dim
        }
        # 发送请求并存储响应
        response = requests.post(url, json=json_data)
        #print(response.json())
        # 检查响应状态代码
        res=''
        answer=response.json()
        choose_dict={}
        choose_dict['result']=0
        if answer['success']:
            choose_dict['result']=1
        #choose_dict['content']=res
        #choose_dict['content']=response
        return jsonify(choose_dict)
    username="lnform"
    return render_template('upload_Document.html',username=username)

@bp.route('/submit_doc',methods=["POST","GET"])
def submit_doc():
    if request.method == "POST":
        data = request.get_json()
        if 'selec_file' in data['Type']:
            filepath=current_app.config['UPLOAD_FOLDER']
            files=os.listdir(filepath)
            file_dict={}
            file_dict['list']=files
            return jsonify(file_dict)
        elif 'add_doc' in data['Type']:
            Kb_id_doc=data['Kb_id_doc']
            Doc_id=data['Doc_id']
            Doc_name=data['Doc_name']
            doc_file=data['doc_file']
            filepath=os.path.join(current_app.config['UPLOAD_FOLDER'], doc_file)
            doc_content_base64=data['doc_content_base64']
            url = 'http://127.0.0.1:6020/vector/doc_add_one'
            json_data = {
                "kb_id": Kb_id_doc,
                "doc_id": Doc_id,
                "doc_name": Doc_name,
                "doc_path": filepath,
                "doc_content_base64": doc_content_base64
            }
            # 发送请求并存储响应
            response = requests.post(url, json=json_data)
            #print(response.json())
            # 检查响应状态代码
            res=''
            answer=response.json()
            choose_dict={}
            choose_dict['result']=0
            if answer['success']:
                choose_dict['result']=1
            return jsonify(choose_dict)
    username="lnform"
    return render_template('upload_Document.html',username=username)

@bp.route('/submit_file_parsing',methods=["POST","GET"])
def submit_file_parsing():
    if request.method == "POST":
        data = request.get_json()
        if 'selec_file' in data['Type']:
            filepath=current_app.config['UPLOAD_FOLDER']
            files=os.listdir(filepath)
            file_dict={}
            file_dict['list']=files
            return jsonify(file_dict)
        elif 'add_file_parsing' in data['Type']:
            #'doc_id_parsing':doc_id_parsing,'doc_name_parsing':doc_name_parsing,'doc_file_parsing':doc_file_parsing,'doc_file_parsing_way':doc_file_parsing_way}
            doc_id_parsing=data['doc_id_parsing']
            doc_name_parsing=data['doc_name_parsing']
            doc_file_parsing=data['doc_file_parsing']
            doc_file_parsing_way=data['doc_file_parsing_way']
            filepath=os.path.join(current_app.config['UPLOAD_FOLDER'], doc_file_parsing)
            if 'doc_to_json' in doc_file_parsing_way:
                url = 'http://127.0.0.1:7030/document/docx_to_json'
            elif 'doc_to_text' in doc_file_parsing_way:
                url = 'http://127.0.0.1:6020/vector/doc_add_one'
            json_data = {
                    "doc_id": doc_id_parsing,
                    "doc_name": doc_name_parsing,
                    "doc_path": filepath
            }
            # 发送请求并存储响应
            response = requests.post(url, json=json_data)
            #print(response.json())
            # 检查响应状态代码
            res=''
            answer=response.json()
            choose_dict={}
            choose_dict['result']=0
            if answer['success']:
                choose_dict['result']=1
            return jsonify(choose_dict)
    username="lnform"
    return render_template('upload_Document.html',username=username)