from fastapi import Request, status
from fastapi.exceptions import RequestValidationError

from .response import CustomResponse as cr


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return cr.error(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        data=exc.errors(),
        message="Validation error",
    )
