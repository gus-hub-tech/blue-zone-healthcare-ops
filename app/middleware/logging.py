"""Logging middleware"""
import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Log request and response details"""
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown"
            }
        )
        
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Request failed: {str(e)}", exc_info=True)
            raise
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time
            }
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
