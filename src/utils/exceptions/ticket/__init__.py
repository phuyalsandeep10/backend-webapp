from fastapi.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND


class TicketNotFound(HTTPException):
    """
    Custom Ticket Exception for ticket not found
    """

    def __init__(self, detail="Ticket not found"):
        super().__init__(status_code=HTTP_404_NOT_FOUND, detail=detail)


class TicketStatusNotFound(HTTPException):
    """
    Custom Ticket Status Exception for ticket not found
    """

    def __init__(self, detail="Ticket status not found"):
        super().__init__(status_code=HTTP_404_NOT_FOUND, detail=detail)


class TicketSLANotFound(HTTPException):
    """
    Custom Ticket SLA Exception for ticket not found
    """

    def __init__(self, detail="Ticket SLA not found"):
        super().__init__(status_code=HTTP_404_NOT_FOUND, detail=detail)
