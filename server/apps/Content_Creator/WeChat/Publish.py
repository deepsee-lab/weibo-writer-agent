import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = 'https://sh.api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={}'.format(os.getenv('access_token'))
# 参数说明
# 参数	是否必须	说明
# access_token	是	调用接口凭证
# media_id	是	要发布的草稿的media_id
MEDIA_ID = 'XXXX'
json_data = {
    "media_id": MEDIA_ID,
}
resp = requests.post(url, json=json_data)
print(resp.json())
# 返回参数说明
# 参数	说明
# errcode	错误码
# errmsg	错误信息
# publish_id	发布任务的id
# msg_data_id	消息的数据ID
