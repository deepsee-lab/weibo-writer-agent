from loguru import logger
from fastapi import APIRouter
from pydantic import BaseModel, Field
from apps.wpp.scripts.add_draft import add_draft

router = APIRouter(
    prefix="/wpp"
)


class DraftAddItem(BaseModel):
    title: str = Field(default="title")
    content: str = Field(default="content")
    thumb_media_id: str = Field(default="xxxxxx_xxx-xxxx")


class Response(BaseModel):
    success: bool
    code: str
    message: str
    data: dict


@router.get("/heartbeat")
def heartbeat():
    logger.info('run heartbeat')
    return 'heartbeat'


@router.post("/draft_add")
def draft_add(item: DraftAddItem):
    logger.info('run draft_add')
    logger.info(item)
    title, content, thumb_media_id = item.title, item.content, item.thumb_media_id
    res = add_draft(title, content, thumb_media_id)
    logger.info(res)
    if 'errcode' in res:
        return Response(success=False, code=str(res['errcode']), message=res['errmsg'], data={})
    else:
        return Response(success=True, code='000000', message='success', data={})
