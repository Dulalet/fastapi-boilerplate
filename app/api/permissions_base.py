import functools
from abc import ABC, abstractmethod

from fastapi import HTTPException
from starlette import status


class BasePermission(ABC):
    """
    Abstract permission that all other Permissions must be inherited from.

    Defines basic error message, status & error codes.

    Upon initialization, calls abstract method  `has_required_permissions`
    which will be specific to concrete implementation of Permission class.
    """

    error_msg = "Forbidden"
    status_code = status.HTTP_403_FORBIDDEN

    @abstractmethod
    def has_required_permissions(self, *args, **kwargs) -> bool:
        ...

    def __init__(self, *args, **kwargs):
        if not self.has_required_permissions(*args, **kwargs):
            raise HTTPException(status_code=self.status_code, detail=self.error_msg)


def check_permissions(permissions: list):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for permission in permissions:
                permission(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator
