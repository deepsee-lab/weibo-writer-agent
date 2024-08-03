from typing import List
from loguru import logger
from fastapi import APIRouter
from pydantic import BaseModel, Field
from apps.vector.vector_store.milvus_class import MilvusClass, client
from apps.vector.api import get_embeddings

router = APIRouter(
    prefix="/vector"
)


class SearchItem(BaseModel):
    kb_id: str = Field(description='32-bit UUID without -', default='uuid' + '0' * 28)
    query: str
    top_k: int = Field(default=5)
    output_fields: List[str] = Field(default=["text"])


class Response(BaseModel):
    success: bool
    code: str
    message: str
    data: dict


@router.post("/search")
def search(item: SearchItem):
    logger.info('run search')
    logger.info(item)
    kb_id = item.kb_id
    query = item.query
    top_k = item.top_k
    output_fields = item.output_fields
    query_vectors = get_embeddings([query])
    results = client.search(
        collection_name=kb_id,
        data=query_vectors,
        limit=top_k,
        output_fields=output_fields,
    )
    data = {
        'results': results
    }
    return Response(success=True, code='000000', message='success', data=data)


@router.get("/heartbeat")
def heartbeat():
    logger.info('run heartbeat')
    return 'heartbeat'
