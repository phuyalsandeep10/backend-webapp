from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.status import (
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from .response import CustomResponse as cr


async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        detail = exc.detail
    elif isinstance(exc, RequestValidationError):
        status_code = HTTP_422_UNPROCESSABLE_ENTITY
        detail = exc.errors()
    else:
        status_code = HTTP_500_INTERNAL_SERVER_ERROR
        detail = str(exc)
    return cr.error(
        status_code=status_code,
        data=detail,
        message="Error",
    )


def add_exceptions_handler(app: FastAPI):
    app.add_exception_handler(RequestValidationError, global_exception_handler)
    app.add_exception_handler(HTTPException, global_exception_handler)
