from loguru import logger
from fastapi import APIRouter

router = APIRouter(
    prefix="/document"
)
from apps.document.algorithm import docx_parsing


@router.get("/heartbeat")
def heartbeat():
    logger.info('run heartbeat')
    return 'heartbeat'


@router.post("/docx_to_json")
def docx_to_json():
    doc_path = ''
    result = docx_parsing.docx_to_json(doc_path)
    return result


@router.post("/docx_to_text")
def docx_to_text():
    doc_path = ''
    result = docx_parsing.docx_to_text(doc_path)
    return result
