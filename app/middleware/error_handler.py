"""Error handling middleware and exception handlers"""
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger(__name__)

class AppException(Exception):
    """Base application exception"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationException(AppException):
    """Validation error exception"""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)

class AuthenticationException(AppException):
    """Authentication error exception"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)

class AuthorizationException(AppException):
    """Authorization error exception"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)

class NotFoundException(AppException):
    """Resource not found exception"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)

class ConflictException(AppException):
    """Conflict error exception"""
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status.HTTP_409_CONFLICT)

def register_exception_handlers(app: FastAPI):
    """Register exception handlers with FastAPI app"""
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.error(f"Application error: {exc.message}", exc_info=True)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )
