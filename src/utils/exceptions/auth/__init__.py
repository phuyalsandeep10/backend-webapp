from fastapi import HTTPException, status


# Profile update specific exceptions
class UserNotFoundException(HTTPException):
    """Exception raised when user is not found"""

    def __init__(self, message: str = "User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class NoDataToUpdateException(HTTPException):
    """Exception raised when no data provided for update"""

    def __init__(self, message: str = "No data to update"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class UserUpdateFailedException(HTTPException):
    """Exception raised when user update fails"""

    def __init__(self, message: str = "Failed to update user"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        )
