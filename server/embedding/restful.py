from fastapi import Response, status
from .models import BaseResponse, User


def make_response(data=None, message="success", code=status.HTTP_200_OK):
    return Response(
        status_code=code,
        media_type="application/json",
        content=BaseResponse(code=code, message=message, data=data).json()
    )
