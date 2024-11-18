from functools import wraps
from ninja.responses import JsonResponse
from ninja.errors import HttpError
import logging

from placeholder.utils.enums import APIStatus


logger = logging.getLogger(__name__)


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpError as he:
            raise he
        except Exception as e:
            logger.error(f"Unhandled exception in {func.__name__}: {e}", exc_info=True)
            return JsonResponse({"detail": APIStatus.INTERNAL_SERVER_ERROR.message}, status=APIStatus.INTERNAL_SERVER_ERROR.code)
    return wrapper
