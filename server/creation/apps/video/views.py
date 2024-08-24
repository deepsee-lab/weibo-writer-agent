# -*- coding: utf-8 -*-
# Standard library imports.
# Related third party imports.
from loguru import logger
from fastapi import APIRouter
from pydantic import BaseModel, Field
# Local application/library specific imports.
from apps.video.algorithm.CogVideoX.CogVideoX_2b import inf
from apis.cdn.upload import upload

router = APIRouter(
    prefix="/video"
)


class GenerateItem(BaseModel):
    prompt: str = Field(
        default="A detailed wooden toy ship with intricately carved masts and sails is seen gliding smoothly over a plush, blue carpet that mimics the waves of the sea. The ship's hull is painted a rich brown, with tiny windows. The carpet, soft and textured, provides a perfect backdrop, resembling an oceanic expanse. Surrounding the ship are various other toys and children's items, hinting at a playful environment. The scene captures the innocence and imagination of childhood, with the toy ship's journey symbolizing endless adventures in a whimsical, indoor setting."
    )
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


@router.post("/CogVideoX_2b/generate")
def generate(item: GenerateItem):
    logger.info('run generate')
    logger.info('item: {}'.format(item))
    output_file = inf(item.prompt, item.filename)
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
