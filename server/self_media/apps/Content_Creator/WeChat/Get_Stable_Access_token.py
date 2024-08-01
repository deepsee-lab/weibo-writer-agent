import os
import requests
from dotenv import load_dotenv

load_dotenv()

# 添加访问 ip 到白名单
url = 'https://sh.api.weixin.qq.com/cgi-bin/stable_token'
json_data = {
    "grant_type": "client_credential",
    "appid": os.getenv('appid'),
    "secret": os.getenv('secret')
}
resp = requests.post(url, json=json_data)
print(resp.json())
