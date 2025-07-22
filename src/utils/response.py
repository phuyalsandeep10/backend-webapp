from typing import Any, Generic, List, Optional, TypeVar, Union

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic.generics import GenericModel

T = TypeVar("T")


class CustomResponseSchema(GenericModel, Generic[T]):
    success: str
    data: Optional[Union[T, List[T]]]
    message: str


class CustomResponse:

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Successful",
        status_code: int = status.HTTP_200_OK,
    ):
        content = {"success": True, "message": message, "data": data}
        return JSONResponse(status_code=status_code, content=content)

    @staticmethod
    def error(
        data: Optional[Any] = None,
        message: Optional[str] = "Unsuccessful",
        status_code: Optional[int] = status.HTTP_400_BAD_REQUEST,
    ):
        content = {"success": False, "message": message, "data": data}
        return JSONResponse(status_code=status_code, content=content)
