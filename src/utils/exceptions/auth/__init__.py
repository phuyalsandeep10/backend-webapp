from fastapi import HTTPException, status

class AuthException(HTTPException):
    """Base exception for authentication module"""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=message)

# Profile update specific exceptions
class UserNotFoundException(AuthException):
    """Exception raised when user is not found"""
    def __init__(self, message: str = "User not found"):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND)

class NoDataToUpdateException(AuthException):
    """Exception raised when no data provided for update"""
    def __init__(self, message: str = "No data to update"):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)

class UserUpdateFailedException(AuthException):
    """Exception raised when user update fails"""
    def __init__(self, message: str = "Failed to update user"):
        super().__init__(message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)