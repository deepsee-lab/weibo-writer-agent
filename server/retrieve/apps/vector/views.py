from loguru import logger
from fastapi import APIRouter

router = APIRouter(
    prefix="/vector"
)


@router.get("/search")
def search():
    logger.info('run search')
    return 'search'


@router.get("/heartbeat")
def heartbeat():
    logger.info('run heartbeat')
    return 'heartbeat'
