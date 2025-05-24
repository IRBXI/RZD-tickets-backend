from fastapi import HTTPException, status
from typing import Any


class ForbiddenException(HTTPException):
    def __init__(self, detail: Any = None) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail if detail else "Forbidden",
        )


class BadRequestException(HTTPException):
    def __init__(self, detail: Any = None) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail if detail else "Bad request"
        )

class NonExistentException(HTTPException):
    def __init__(self, detail: Any = None) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail if detail else "Not found"
        )


class AuthFailedException(HTTPException):
    def __init__(self, detail: Any = None) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail if detail else "Authenticate failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
