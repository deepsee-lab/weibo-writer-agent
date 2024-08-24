# -*- coding: utf-8 -*-
# Standard library imports.
# Related third party imports.
from loguru import logger
from fastapi import APIRouter
from pydantic import BaseModel, Field
# Local application/library specific imports.
from apps.image.algorithm.FLUX_1.FLUX_1_dev import inf as flux_1_dev_inf
from apps.image.algorithm.FLUX_1.FLUX_1_schnell import inf as flux_1_schnell_inf
from apis.cdn.upload import upload

router = APIRouter(
    prefix="/image"
)


class GenerateItem(BaseModel):
    prompt: str = Field(default='A cat holding a sign that says hello world')
    filename: str = Field(default='demo')
    # cdn
    upload_to_cdn: bool = Field(default=True)
    bucket_name: str = Field(default='wwa-test')
    expire_time: int = Field(default=3600)


class Response(BaseModel):
    success: bool
    code: str
    message: str
    data: dict


@router.get("/heartbeat")
def heartbeat():
    logger.info('run heartbeat')
    return 'heartbeat'


@router.post("/FLUX_1_dev/generate")
def flux_1_dev_generate(item: GenerateItem):
    logger.info('run generate')
    logger.info('item: {}'.format(item))
    output_file = flux_1_dev_inf(item.prompt, item.filename)
    if item.upload_to_cdn:
        url = upload(item.bucket_name, output_file, item.expire_time)
        data = {
            'url': url
        }
    else:
        data = {
            'output_file': output_file
        }
    logger.info('data: {}'.format(data))
    return Response(success=True, code='000000', message='success', data=data)


@router.post("/FLUX_1_schnell/generate")
def flux_1_schnell_generate(item: GenerateItem):
    logger.info('run generate')
    logger.info('item: {}'.format(item))
    output_file = flux_1_schnell_inf(item.prompt, item.filename)
    if item.upload_to_cdn:
        url = upload(item.bucket_name, output_file, item.expire_time)
        data = {
            'url': url
        }
    else:
        data = {
            'output_file': output_file
        }
    logger.info('data: {}'.format(data))
    return Response(success=True, code='000000', message='success', data=data)
