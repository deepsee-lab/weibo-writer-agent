# server

## 服务框架说明

Flask: flask_sample, web, self_media

FastAPI: fastapi_sample, agent, embedding, extraction, memory, retrieve

## 服务调度说明

web: agent(llm、rag等问答模式切换), memory(知识库管理), self_media(创作平台使用)

agent: retrieve(知识检索)

memory: extraction(文档解析、切片), embedding(文本向量化)

retrieve: embedding

## 各服务端口

flask_sample: 2000

fastapi_sample: 2001

self_media: 4000

embedding: 5001

extraction: 5002

memory: 5003

retrieve: 5004

agent: 5005

web: 6000起
