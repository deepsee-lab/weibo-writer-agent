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


class InfOneItem(BaseModel):
    messages: List[str] = Field(description="Please refer to openai to write")
    model_type: str = Field(description="Choose from ollama, xinference, api...", default="ollama")
    model: str = Field(default="qwen2:1.5b-instruct-fp16")
    max_tokens: int = Field(default=4096)
    stream: bool = Field(default=False)
    temperature: float = Field(default=0.8)
    # top_p: float
    timeout: int = Field(default=60)


class Response(BaseModel):
    success: bool
    code: str
    message: str
    data: dict = None


@router.post('/inference_one')
def inference_one(item: InfOneItem):
    logger.info('run inference_mul')
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
