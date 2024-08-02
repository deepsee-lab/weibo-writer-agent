# -*- coding: utf-8 -*-
# Standard library imports.
from typing import List
# Related third party imports.
from loguru import logger
from pydantic import BaseModel
from fastapi import APIRouter

# Local application/library specific imports.

router = APIRouter(
    prefix="/llm"
)


class InfOneItem(BaseModel):
    messages: List[str]
    model_type: str
    model: str
    max_tokens: int
    stream: bool
    temperature: float
    top_p: float
    timeout: int


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
