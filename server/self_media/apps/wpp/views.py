from loguru import logger
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/wpp"
)


class DraftAddItem(BaseModel):
    title: str
    content: str
    thumb_media_id: str


class Response(BaseModel):
    success: bool
    code: str
    message: str
    data: dict = None


@router.get("/heartbeat")
def heartbeat():
    logger.info('run heartbeat')
    return 'heartbeat'


@router.post("/draft_add")
def draft_add(item: DraftAddItem):
    logger.info('run draft_add')
    logger.info(item)
    data = {}
    return Response(success=True, code='000000', message='success', data=data)
