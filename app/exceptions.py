"""Custom exception classes"""

class ValidationError(Exception):
    """Validation error exception"""
    pass

class AuthenticationError(Exception):
    """Authentication error exception"""
    pass

class AuthorizationError(Exception):
    """Authorization error exception"""
    pass

class NotFoundError(Exception):
    """Resource not found exception"""
    pass

class ConflictError(Exception):
    """Conflict error exception"""
    pass

class DatabaseError(Exception):
    """Database error exception"""
    pass
