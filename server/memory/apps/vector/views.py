from loguru import logger
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/vector"
)


class KbBaseItem(BaseModel):
    kb_id: str


class KbAddItem(KbBaseItem):
    kb_name: str


class KbDropItem(KbBaseItem):
    pass


class Response(BaseModel):
    success: bool
    code: str
    message: str
    data: dict = None


@router.post("/kb_add")
def kb_add(item: KbAddItem):
    logger.info('run kb_add')
    logger.info(item)
    return Response(success=True, code='000000', message='success', data={})


@router.post("/kb_drop")
def kb_drop(item: KbDropItem):
    logger.info('run kb_drop')
    logger.info(item)
    return Response(success=True, code='000000', message='success', data={})


@router.get("/heartbeat")
def heartbeat():
    logger.info('run heartbeat')
    return 'heartbeat'
