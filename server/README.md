# server

## 服务框架

Flask: flask_sample, web

FastAPI: fastapi_sample, others

## 服务调度

web(实时): agent(智能体使用), rag(知识库对话), memory(知识库管理), self_media(创作平台使用)...

agent(实时): llm(大模型推理生成) + toolkit(工具调用)

rag(实时): retrieve(知识检索) + llm(大模型推理生成)

memory(非实时): document_parser(文档解析) + text_chunking(文本分块) + embedding(文本向量化)...

retrieve(实时): embedding(文本向量化), web_parser(网页解析) + text_chunking(文本分块), memory(知识库管理)...

toolkit(实时/非实时): all

## 服务端口

###### model

llm(原子服务. 多蓝图: private，saas): 4010

embedding(原子服务. 单蓝图: private，saas): 4020

reranker(原子服务. 单蓝图): 待定

###### framework

flask_sample: 5010

fastapi_sample: 5020

###### toolkit

toolkit(原子服务. 多蓝图: 各个toolkit): 6010

memory(复合服务. 多蓝图: db, vector...): 6020

web_parser(原子服务. 多蓝图: search_engine_api, page_parser...): 待定

text_chunking(原子服务. 单蓝图): 6040

self_media(原子服务. 多蓝图: wb, wpp...): 6050

creation(原子服务. 多蓝图: image, audio, video): 待定

###### algorithm

agent(复合服务. 单蓝图): 7010

rag(复合服务. 单蓝图): 7020

document_parser(原子服务. 多蓝图: Word, PDF, Table, Image...): 7030

retrieve(复合服务. 多蓝图: vector search, keywords search, web browser...): 7040

###### workflow

workflow: 待定

###### web

web(复合服务. 多蓝图): 9000起
