# -*- coding: utf-8 -*-
# Standard library imports.
import json
from typing import List
# Related third party imports.
import uvicorn
from loguru import logger
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# Local application/library specific imports.
from configs import config
from api import get_retrieve_inference, get_llm_inference

app = FastAPI(
    title="RAG",
    description="RAG",
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
)
# 允许所有来源
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许访问的源列表
    allow_credentials=True,  # 支持 cookies 跨域
    allow_methods=["*"],  # 允许的请求方法
    allow_headers=["*"],  # 允许的请求头
)


class MessageItem(BaseModel):
    role: str = Field(description="Choose from system, user, assistant...", default="user")
    content: str = Field(default="prompt")


class InfItem(BaseModel):
    # llm
    messages: List[MessageItem] = Field(description="Please refer to openai to write")
    inference_service: str = Field(description="Choose from ollama, xinference, api...", default="ollama")
    model: str = Field(default="qwen2:1.5b-instruct-fp16")
    max_tokens: int = Field(default=4096)
    stream: bool = Field(default=False)
    temperature: float = Field(default=0.8)
    timeout: int = Field(default=60)
    # rag
    rag: bool = Field(default=False)
    kb_id: str = Field(default="uuid" + "0" * 28)
    history_count: int = Field(default=10)
    top_k: int = Field(default=10)
    threshold_value: float = Field(default=0.0)
    retrieve_only: bool = Field(default=False)


class Response(BaseModel):
    success: bool
    code: str
    message: str
    data: dict


@app.get("/")
def index():
    logger.info('index')
    return "index"


@app.get('/heartbeat')
def heartbeat():
    logger.info('run heartbeat')
    return 'heartbeat'


@app.post('/inference')
def inference(item: InfItem):
    logger.info('run inference')
    logger.info('item: {}'.format(item))

    kb_id = item.kb_id
    messages = item.messages
    messages = [{'role': message.role, 'content': message.content} for message in messages]
    query = messages[-1]['content']
    # query = '你好'
    top_k = item.top_k
    output_fields = ["text"]
    retrieve_result = get_retrieve_inference(kb_id, query, top_k, output_fields)

    logger.info('retrieve_result: {}'.format(retrieve_result))

    inference_service = item.inference_service
    model = item.model
    max_tokens = item.max_tokens
    stream = item.stream
    temperature = item.temperature
    timeout = item.timeout

    llm_result = get_llm_inference(inference_service, messages, model, max_tokens, stream, temperature, timeout)
    data = {
        'retrieve_result': retrieve_result,
        'llm_result': llm_result,
    }

    return Response(success=True, code='000000', message='success', data=data)


host = '0.0.0.0'
port = 7020
reload = True

logger.info('Server is up and running.')
logger.info('Browse http://127.0.0.1:{}/heartbeat to verify.'.format(port))
logger.info('Browse http://127.0.0.1:{}/docs to test.'.format(port))

if __name__ == '__main__':
    uvicorn.run(app="main:app", reload=reload, host=host, port=port)
