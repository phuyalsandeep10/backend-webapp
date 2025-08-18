from fastapi.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT


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


class TicketPriorityNotFound(HTTPException):
    """
    Custom Ticket Priority Exception for ticket not found
    """

    def __init__(self, detail="Ticket Priority not found"):
        super().__init__(status_code=HTTP_404_NOT_FOUND, detail=detail)


class TicketPriorityExists(HTTPException):
    """
    Custom Ticket Priority Exists Exception
    """

    def __init__(self, detail="Ticket Priority already exists"):
        super().__init__(status_code=HTTP_409_CONFLICT, detail=detail)


class TicketAlreadyConfirmed(HTTPException):
    """
    Custom Ticket Already Confirmed Exception
    """

    def __init__(self, detail="This ticket has been already confirmed"):
        super().__init__(status_code=HTTP_409_CONFLICT, detail=detail)
