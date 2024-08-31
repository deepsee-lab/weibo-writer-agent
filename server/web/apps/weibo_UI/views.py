# -*- coding: utf-8 -*-
# Standard library imports.
import sqlite3,os,json,re,requests,uuid
# Related third party imports.
from flask import Flask, Blueprint,render_template,request,jsonify,url_for,current_app,session,redirect,g
from functools import wraps
from loguru import logger
from werkzeug.utils import secure_filename
from extends import (
    db,
)
# Local application/library specific imports.
from apps.weibo_UI.rag_run import *
from apps.weibo_UI.models import weibo_UI_Model

bp = Blueprint("weibo_UI", __name__, url_prefix='/weibo_UI',static_folder='static',template_folder='templates')


##############################################################################################
#  网页功能部分
##############################################################################################

@bp.before_request
def before_request():
    if session.get('name'):
        result = weibo_UI_Model.query.filter_by(name=session.get('name')).first()
        if result:
            g.user = session.get('name')
        else:
            g.user = None
    else:
        g.user = None

def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if g.user:
            result = weibo_UI_Model.query.filter_by(name=g.user).first()
            if result:
                return func(*args, **kwargs)
            else:
                return redirect('/weibo_UI/login')
        else:
            return redirect('/weibo_UI/login')
    return inner


@bp.route('/index' )
@login_required
def show():
    username=session.get("name")
    print('qwe',username)
    return render_template('index.html',username=username)

@bp.route('/login',methods=['GET','POST'] )
def login():
    if request.method == 'GET':
        return render_template('pages_login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        users = weibo_UI_Model.query.all()
        gate_key=0
        for user in users:
            if user.name==username and user.text==password:
                gate_key=1
                session["name"] = username
                session["pwd"] = password
                return render_template('index.html',username=username)

@bp.route('/logout',methods=['GET','POST'] )
@login_required
def logout():
    session.clear()
    return render_template('pages_login.html')

@bp.route('/add_user',methods=['GET','POST'] )
def add_user():
    if request.method == "POST":
        data = request.get_json()
        UserName=data['UserName']
        Pwd=data['Pwd']
        new_user = weibo_UI_Model()
        new_user.name = UserName
        new_user.text = Pwd
        db.session.add(new_user)
        db.session.commit()
        choose_dict={}
        choose_dict['result']=1
        return jsonify(choose_dict)
    return render_template('add_user.html')


@bp.route('/get_by_id',methods=['GET','POST'] )
@login_required  
def get_by_id():
    get_user = weibo_UI_Model.query.get(1)  # User.query.filter_by(id=get_id).first()
    return "编号：{0}，用戶名：{1}，邮箱：{2}".format(get_user.id, get_user.name, get_user.text)

##########################################################################################################


@bp.route('/submit_file_parsing',methods=["POST","GET"])
@login_required  
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
    username=session.get("name")
    return render_template('upload_Document.html',username=username,status='')

######################################################################################
#self_media
######################################################################################


@bp.route('/upload_img',methods=["POST","GET"])
@login_required  
def upload_img():
    username=session.get("name")
    if request.method == "POST":
        f = request.files['file']
        filename=secure_filename(filename)
        save_path=os.path.join(current_app.config['UPLOAD_FOLDER_PIC'], filename)
        if not os.path.exists(current_app.config['UPLOAD_FOLDER_PIC']):
            os.mkdir(current_app.config['UPLOAD_FOLDER_PIC'])
        f.save(save_path)
        status="upload ok"
        return render_template('upload_img.html',username=username,status=status)
    return render_template('upload_img.html',username=username,status=status)


@bp.route('/material_video_add',methods=["POST","GET"])
@login_required  
def material_video_add():
    username=session.get("name")
    status=""
    if request.method == "POST":
        access_token='abc'
        if not os.path.exists(current_app.config['UPLOAD_FOLDER_VIDEO']):
            os.mkdir(current_app.config['UPLOAD_FOLDER_VIDEO'])
        files=os.listdir(current_app.config['UPLOAD_FOLDER_VIDEO'])
        choose_dict={}
        choose_dict['success_result']=0
        choose_dict['fail_result']=0
        choose_dict['result']=0
        data = request.get_json()
        Introduction=data['Introduction']
        Title=data['Title']
        for file in files:
            pic_path=os.path.join(current_app.config['UPLOAD_FOLDER_VIDEO'],file)
            ####  post  ####
            url_self_media= 'http://127.0.0.1:6050/wpp/material_video_add'
            json_data_self_media = {
                "access_token": access_token,
                "file_path": pic_path,
                "title": Title,
                "introduction": Introduction
            }
            # 发送请求并存储响应
            response_self_media = requests.post(url_self_media, json=json_data_self_media)
            self_media_res=response_self_media.json()
            if self_media_res['success']:
                choose_dict['success_result']+=1
                choose_dict['result']=1
            else:
                choose_dict['fail_result']+=1
        choose_dict['content']='成功了'+str(choose_dict['success_result'])+'个, '+'失败了'+str(choose_dict['fail_result'])+'个'
        return jsonify(choose_dict)
    return render_template('upload_video.html',username=username,status=status)

@bp.route('/upload_video',methods=["POST","GET"])
@login_required  
def upload_video():
    username=session.get("name")
    status=""
    if request.method == "POST":
        f = request.files['file']
        filename=secure_filename(filename)
        save_path=os.path.join(current_app.config['UPLOAD_FOLDER_VIDEO'], filename)
        if not os.path.exists(current_app.config['UPLOAD_FOLDER_VIDEO']):
            os.mkdir(current_app.config['UPLOAD_FOLDER_VIDEO'])
        f.save(save_path)
        status="upload ok"
        return render_template('upload_video.html',username=username,status=status)
    return render_template('upload_video.html',username=username,status=status)

@bp.route('/publish_free',methods=["POST","GET"])
@login_required  
def publish_free():
    username=session.get("name")
    if request.method == "POST":
        access_token='abc'
        choose_dict={}
        choose_dict['result']=0
        data = request.get_json()
        Media_id=data['Media_id']
        ####  post  ####
        url_self_media= 'http://127.0.0.1:6050/wpp/publish_free'
        json_data_self_media = {
            "access_token": access_token,
            "MEDIA_ID": Media_id
        }
        # 发送请求并存储响应
        response_self_media = requests.post(url_self_media, json=json_data_self_media)
        self_media_res=response_self_media.json()
        if self_media_res['success']:
            choose_dict['result']=1
        return jsonify(choose_dict)
    return render_template('publish_free.html',username=username)
######################################################################################
# 知识库
######################################################################################
@bp.route('/choose_model')
@login_required  
def choose_model():
    username=session.get("name")
    return render_template('choose_model.html',username=username)
#################################################################
############     1、 知识库问答
#################################################################
@bp.route('/choose_model_post',methods=["POST"])
@login_required  
def choose_model_post():
    if request.method == "POST":
        data = request.get_json()
        type_name=data['type_name']
        model_type=['-- pls choose --']
        kb_list_content=[]
        if "choose_type" in type_name:
            try:
                res=os.popen("ps -ef | grep ollama").read()
                if 'ollama serve' in res:
                    model_type.append("ollama")
            except:
                logger.info('no ollama')
            try:
                res=os.popen("ps -ef | grep xinference").read()
                if 'xinference' in res:
                    model_type.append("xinference")
            except:
                logger.info('no xinference')
            choose_dict={}
            choose_dict['result']=1
            choose_dict['content']=model_type
            return jsonify(choose_dict)
        elif "choose_model" in type_name:
            type_select=data['type_select']
            model_list=[]
            if "ollama" in type_select:
                try:
                    res=os.popen("ollama list").read()
                    models=res.split('\n')
                    for index_i, item_i in enumerate(models):
                        if index_i == 0:
                            continue
                        model_list.append(item_i.split()[0])
                        print(item_i.split()[0])
                except:
                    logger.info('no ollama')
            choose_dict={}
            choose_dict['result']=1
            choose_dict['content']=model_list
            return jsonify(choose_dict)
        elif "choose_KB" in type_name:
            try:
                res=kb_list()
                kb_list_content=res['data']['kb_list']
                logger.info('kb_list')
                
            except:
                logger.info('no get kb list')
            choose_dict={}
            choose_dict['result']=1
            choose_dict['content']=kb_list_content
            logger.info(kb_list_content)
            return jsonify(choose_dict)

@bp.route('/model_run',methods=["POST"])
@login_required  
def model_run():
    if request.method == "POST":
        data = request.get_json()
        type_name=data['type_name']
        model_select=data['model_name']
        KB_id=data['KB_id']
        top_selector=data['top_selector']
        top_K=int(top_selector)
        query=data['query']
        logger.info(KB_id)
        logger.info(query)
        if KB_id=='0':
            url = 'http://127.0.0.1:4010/private/inference'
            # 检查响应状态代码
            rag_result=''
            retrieve_result=''
            answer=no_vector_model_rag(url,query,type_name,model_select)
            if answer['message'] == 'success':
                # 打印响应文本
                rag_result=answer['data']['result']
                retrieve_result='(no select vector)'
        else:
            url = 'http://127.0.0.1:7020/inference'
            # 检查响应状态代码
            rag_result=''
            retrieve_result=''
            logger.info('rag_before:',KB_id)
            logger.info(KB_id)
            answer=vector_model_rag(url,KB_id,top_K,query,type_name,model_select)
            if answer['message'] == 'success':
                # 打印响应文本
                rag_result=answer['data']['rag_result']
                retrieve_result=answer['data']['retrieve_result'][0][0]['entity']['text']
        choose_dict={}
        choose_dict['result']=1
        choose_dict['rag_result']=rag_result
        choose_dict['retrieve_result']=retrieve_result
        #choose_dict['content']=response
        return jsonify(choose_dict)
#################################################################
############     2、 新建知识库
#################################################################
@bp.route('/upload',methods=['GET','POST'])
@login_required  
def upload():
    username=session.get("name")
    status=''
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
        status="upload ok"
    return render_template('upload_Document.html',username=username,status=status)

@bp.route('/submit_kb',methods=["POST","GET"])
@login_required  
def submit_kb():
    if request.method == "POST":
        unique_id=str(uuid.uuid4()).replace('-','')
        #print('lll',unique_id)
        # 02d2f68d6de441c38968c6b58b31dcfd
        data = request.get_json()
        Dim=1024
        Kb_id=unique_id
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
    username=session.get("name")
    return render_template('upload_Document.html',username=username,status='')

@bp.route('/submit_doc',methods=["POST","GET"])
@login_required  
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
            print('222',Kb_id_doc)
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
    username=session.get("name")
    return render_template('upload_Document.html',username=username,status='')

######################################################################################
# 微信公众号
######################################################################################

#################################################################
############     1、 上传素材
#################################################################
@bp.route('/text_to_picture_video',methods=["POST","GET"])
@login_required  
def text_to_picture_video():
    username=session.get("name")
    pic_status=''
    video_status=''
    upload_status=''
    if request.method == "POST":
        data = request.get_json()
        type_name=data['type']
        text=data['text']
        if 'picture' in type_name:
            ####  post  ####
            print('123')
            url_self_media= 'https://83440n0z70.vicp.fun/image/FLUX_1_dev/generate'
            json_data_picture = {
                "prompt": text,
                "filename": "demo",
                "upload_to_cdn": True,
                "bucket_name": "wwa-test",
                "expire_time": 3600
            }
            # 发送请求并存储响应
            response_self_media = requests.post(url_self_media, json=json_data_picture)
            print('444',str(response_self_media))
            self_media_res=response_self_media.json()
            try:
                url_link=self_media_res['data']['url']
            except:
                url_link='no find'
            pic_status='generate ok, check link:'+str(url_link)
        elif 'video' in type_name:
            ####  post  ####
            url_self_media= 'https://83440n0z70.vicp.fun/video/CogVideoX_2b/generate'
            json_data_picture = {
                "prompt": text,
                "filename": "demo",
                "upload_to_cdn": True,
                "bucket_name": "wwa-test",
                "expire_time": 3600
            }
            # 发送请求并存储响应
            response_self_media = requests.post(url_self_media, json=json_data_picture)
            self_media_res=response_self_media.json()
            try:
                url_link=self_media_res['data']['url']
            except:
                url_link='no find'
            video_status='generate ok, check link:'+str(url_link)
    return render_template('text_to_picture_video.html',username=username,pic_status=pic_status,video_status=video_status,upload_status=upload_status)

@bp.route('/submit_pic',methods=["POST","GET"])
@login_required  
def submit_pic():
    if request.method == "POST":
        data = request.get_json()
        if 'selec_pic' in data['Type']:
            filepath=current_app.config['UPLOAD_FOLDER_PIC']
            files=os.listdir(filepath)
            file_dict={}
            file_dict['list']=files
            return jsonify(file_dict)
        elif 'add_pic' in data['Type']:#qpic
            access_token=os.getenv('access_token')
            filename=data['pic_file']
            pic_path=os.path.join(current_app.config['UPLOAD_FOLDER_PIC'], filename)
            logger.info(pic_path)
            ####  post  ####
            url_self_media= 'http://127.0.0.1:6050/wpp/upload_img'
            json_data_self_media = {
                "access_token": access_token,
                "file_path": pic_path
            }
            # 发送请求并存储响应
            response_self_media = requests.post(url_self_media, json=json_data_self_media)
            self_media_res=response_self_media.json()
            upload_status='upload qpic fail'
            choose_dict={}
            choose_dict['result']=0
            choose_dict['content']=upload_status
            if self_media_res['success']:
                choose_dict['content']=self_media_res['data']['url']
                choose_dict['result']=1
            return jsonify(choose_dict)
        elif 'submit_pic' in data['Type']:#wpp
            access_token=os.getenv('access_token')
            filename=data['pic_file']
            pic_path=os.path.join(current_app.config['UPLOAD_FOLDER_PIC'], filename)
            logger.info(pic_path)
            logger.info(access_token)
            ####  post  ####
            url_self_media= 'http://127.0.0.1:6050/wpp/material_img_add'
            json_data_self_media = {
                "access_token": access_token,
                "file_path": pic_path
            }
            # 发送请求并存储响应
            response_self_media = requests.post(url_self_media, json=json_data_self_media)
            self_media_res=response_self_media.json()
            upload_status='wpp fail'
            choose_dict={}
            choose_dict['result']=0
            choose_dict['content']=upload_status
            if self_media_res['success']:
                choose_dict['content']='okk'
                choose_dict['result']=1
            return jsonify(choose_dict)
            
@bp.route('/submit_video',methods=["POST","GET"])
@login_required  
def submit_video():
    if request.method == "POST":
        data = request.get_json()
        if 'selec_vedio' in data['Type']:
            filepath=current_app.config['UPLOAD_FOLDER_VIDEO']
            files=os.listdir(filepath)
            file_dict={}
            file_dict['list']=files
            return jsonify(file_dict)
        elif 'submit_vedio' in data['Type']:
            access_token=os.getenv('access_token')
            filename=data['pic_file']
            pic_path=os.path.join(current_app.config['UPLOAD_FOLDER_VIDEO'], filename)
            print(pic_path)
            ####  post  ####
            url_self_media= 'http://127.0.0.1:6050/wpp/material_video_add'
            json_data_self_media = {
                "access_token": access_token,
                "file_path": pic_path,
                "title": Title,
                "introduction": Introduction
            }
            # 发送请求并存储响应
            response_self_media = requests.post(url_self_media, json=json_data_self_media)
            self_media_res=response_self_media.json()
            upload_status='upload qpic fail'
            choose_dict={}
            choose_dict['result']=0
            choose_dict['content']=upload_status
            if self_media_res['success']:
                choose_dict['content']=self_media_res['data']['url']
                choose_dict['result']=1
            return jsonify(choose_dict)
        elif 'submit_pic' in data['Type']:
            access_token=os.getenv('access_token')
            filename=data['pic_file']
            pic_path=os.path.join(current_app.config['UPLOAD_FOLDER_PIC'], filename)
            print(pic_path)
            ####  post  ####
            url_self_media= 'http://127.0.0.1:6050/wpp/material_img_add'
            json_data_self_media = {
                "access_token": access_token,
                "file_path": pic_path
            }
            # 发送请求并存储响应
            response_self_media = requests.post(url_self_media, json=json_data_self_media)
            self_media_res=response_self_media.json()
            upload_status='upload qpic fail'
            choose_dict={}
            choose_dict['result']=0
            choose_dict['content']=upload_status
            if self_media_res['success']:
                choose_dict['content']='okk'
                choose_dict['result']=1
            return jsonify(choose_dict)           

@bp.route('/get_token',methods=["POST","GET"])
@login_required  
def get_token():
    if request.method == "POST":
        data = request.get_json()
        if 'get_token' in data['Type']:
            appid=os.getenv('appid')
            secret=os.getenv('secret')
            ####  post  ####
            url_self_media= 'http://127.0.0.1:6050/wpp/stable_access_token_get'
            json_data_self_media = {
                "appid": appid,
                "secret": secret
            }
            # 发送请求并存储响应
            response_self_media = requests.post(url_self_media, json=json_data_self_media)
            self_media_res=response_self_media.json()
            token_status='get token fail'
            choose_dict={}
            choose_dict['result']=0
            choose_dict['content']=token_status
            if self_media_res['success']:
                choose_dict['content']=self_media_res['data']['stable_access_token']['access_token']
                choose_dict['result']=1
            return jsonify(choose_dict)
        elif 'update_token' in  data['Type']:
            appid=os.getenv('appid')
            secret=os.getenv('secret')
            ####  post  ####
            url_self_media= 'http://127.0.0.1:6050/wpp/stable_access_token_get'
            json_data_self_media = {
                "appid": appid,
                "secret": secret
            }
            # 发送请求并存储响应
            response_self_media = requests.post(url_self_media, json=json_data_self_media)
            self_media_res=response_self_media.json()
            token_status='get token fail'
            choose_dict={}
            choose_dict['result']=0
            choose_dict['content']=token_status
            if self_media_res['success']:
                choose_dict['content']=self_media_res['data']['stable_access_token']['access_token']
                file_path =current_app.config['VAR_FILE_PATH']
                new_line=[]
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    for item in lines:
                        if 'access_token=' in item:
                            str_line='access_token='+choose_dict['content']
                            new_line.append(str_line)
                        else:
                            new_line.append(item)
                # 将修改后的内容写回文件
                with open(file_path, 'w') as file:
                    file.writelines(new_line)
                choose_dict['result']=1
            return jsonify(choose_dict)        
          

#################################################################
############     2、 新建草稿
#################################################################
@bp.route('/draft_add',methods=["POST","GET"])
@login_required  
def draft_add():
    username=session.get("name")
    if request.method == "POST":
        choose_dict={}
        choose_dict['result']=0
        data = request.get_json()
        thumb_media_id=data['thumb_media_id']
        Title=data['Title']
        content=data['content']
        ####  post  ####
        url_self_media= 'http://127.0.0.1:6050/wpp/draft_add'
        json_data_self_media = {
            "title": Title,
            "content": content,
            "thumb_media_id": thumb_media_id
        }
        # 发送请求并存储响应
        response_self_media = requests.post(url_self_media, json=json_data_self_media)
        self_media_res=response_self_media.json()
        if self_media_res['success']:
            choose_dict['result']=1
        return jsonify(choose_dict)
    return render_template('draft_add.html',username=username)

#################################################################
############     3、 发布文章
#################################################################
@bp.route('/self_media',methods=["POST","GET"])
@login_required
def self_media():
    if request.method == "POST":
        data = request.get_json()
        if 'publish' in data['Type']:
            MEDIA_ID=data['MEDIA_ID']
            access_token=os.getenv('access_token')
            # 检查响应状态代码
            ####  post  ####
            url_self_media= 'http://127.0.0.1:6050/wpp/publish_free'
            json_data_self_media = {
                "access_token": access_token,
                "MEDIA_ID": MEDIA_ID
            }
        # 发送请求并存储响应
        response_self_media = requests.post(url_self_media, json=json_data_self_media)
        self_media_res=response_self_media.json()
        choose_dict={}
        choose_dict['result']=0
        if self_media_res['success']:
            choose_dict['result']=1
            #choose_dict['content']=response
            return jsonify(choose_dict)
    username=session.get("name")
    return render_template('self_media.html',username=username)
######################################################################################
# 智能微博
######################################################################################

#################################################################
############     1、 微博草稿
#################################################################
@bp.route('/weibo_choose_model',methods=["POST","GET"])
@login_required  
def weibo_choose_model():
    if request.method == "POST":
        data = request.get_json()
        type_name=data['type_name']
        model_type=['-- pls choose --']
        kb_list_content=[]
        if "choose_type" in type_name:
            try:
                res=os.popen("ps -ef | grep ollama").read()
                if 'ollama serve' in res:
                    model_type.append("ollama")
            except:
                logger.info('no ollama')
            try:
                res=os.popen("ps -ef | grep xinference").read()
                if 'xinference' in res:
                    model_type.append("xinference")
            except:
                logger.info('no xinference')
            choose_dict={}
            choose_dict['result']=1
            choose_dict['content']=model_type
            return jsonify(choose_dict)
        elif "choose_model" in type_name:
            type_select=data['type_select']
            model_list=[]
            if "ollama" in type_select:
                try:
                    res=os.popen("ollama list").read()
                    models=res.split('\n')
                    for index_i, item_i in enumerate(models):
                        if index_i == 0:
                            continue
                        model_list.append(item_i.split()[0])
                        print(item_i.split()[0])
                except:
                    logger.info('no ollama')
            choose_dict={}
            choose_dict['result']=1
            choose_dict['content']=model_list
            return jsonify(choose_dict)
        elif "choose_KB" in type_name:
            print('246')
            try:
                res=kb_list()
                kb_list_content=res['data']['kb_list']
            except:
                logger.info('no get kb list')
            choose_dict={}
            choose_dict['result']=1
            choose_dict['content']=kb_list_content
            return jsonify(choose_dict)
    else:
        username=session.get("name")
        return render_template('weibo_daily.html',username=username)

@bp.route('/weibo_model_run',methods=["POST"])
@login_required  
def weibo_model_run():
    if request.method == "POST":
        data = request.get_json()
        type_name=data['type_name']
        model_select=data['model_name']
        KB_id=data['KB_id']
        top_selector=data['top_selector']
        top_K=int(top_selector)
        query=data['query']
        logger.info(query)
        if KB_id=='0':
            url = 'http://127.0.0.1:4010/private/inference'
            # 检查响应状态代码
            rag_result=''
            retrieve_result=''
            answer=no_vector_model_rag(url,query,type_name,model_select)
            if answer['message'] == 'success':
                # 打印响应文本
                rag_result=answer['data']['result']
                retrieve_result='(no select vector)'
        else:
            url = 'http://127.0.0.1:7020/inference'
            # 检查响应状态代码
            rag_result=''
            retrieve_result=''
            answer=vector_model_rag(url,KB_id,top_K,query,type_name,model_select)
            if answer['message'] == 'success':
                # 打印响应文本
                rag_result=answer['data']['rag_result']
                retrieve_result=answer['data']['retrieve_result'][0][0]['entity']['text']
        choose_dict={}
        choose_dict['result']=1
        choose_dict['rag_result']=rag_result
        choose_dict['retrieve_result']=retrieve_result
        #choose_dict['content']=response
        return jsonify(choose_dict)
#################################################################
############     2、 新浪微博
#################################################################