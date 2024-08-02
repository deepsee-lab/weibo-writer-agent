# -*- coding: utf-8 -*-
# Standard library imports.
from typing import List
# Related third party imports.
from loguru import logger
from pydantic import BaseModel, Field
from fastapi import APIRouter

# Local application/library specific imports.

router = APIRouter(
    prefix="/llm"
)


class InfItem(BaseModel):
    # llm
    messages: List[str] = Field(description="Please refer to openai to write")
    inference_service: str = Field(description="Choose from ollama, xinference, api...", default="ollama")
    model: str = Field(default="qwen2:1.5b-instruct-fp16")
    max_tokens: int = Field(default=4096)
    stream: bool = Field(default=False)
    temperature: float = Field(default=0.8)
    timeout: int = Field(default=60)
    # rag
    rag: bool = Field(default=False)
    kb_id: str = Field(default="0" * 32)
    history_count: int = Field(default=10)
    top_k: int = Field(default=10)
    threshold_value: float = Field(default=0.0)
    retrieve_only: bool = Field(default=False)


class Response(BaseModel):
    success: bool
    code: str
    message: str
    data: dict


@router.post('/inference')
def inference(item: InfItem):
    logger.info('run inference')
    logger.info('item: {}'.format(item))

    result = 'llm result'
    data = {
        'result': result,
    }

    return Response(success=True, code='000000', message='success', data=data)


@router.get("/heartbeat")
def heartbeat():
    logger.info('run heartbeat')
    return 'heartbeat'
