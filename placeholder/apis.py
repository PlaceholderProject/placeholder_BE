from ninja import NinjaAPI
from user.apis.auth import auth_router
from user.apis.user import user_router
from meetup.apis import meetup_router
from ninja.errors import HttpError, ValidationError
from django.http import JsonResponse
import logging
from placeholder.utils.enums import APIStatus

logger = logging.getLogger(__name__)

api = NinjaAPI()

api.add_router("/auth", auth_router)
api.add_router("/user", user_router)
api.add_router("/meetup", meetup_router)


def global_exception_handler(request, exc):
    if isinstance(exc, HttpError):
        return JsonResponse({"detail": exc.message}, status=exc.status_code)
    elif isinstance(exc, ValidationError):
        return JsonResponse({"detail": APIStatus.BAD_REQUEST.message}, status=APIStatus.BAD_REQUEST.code)

    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JsonResponse({"detail": APIStatus.INTERNAL_SERVER_ERROR.message}, status=APIStatus.INTERNAL_SERVER_ERROR.code)


api.add_exception_handler(Exception, global_exception_handler)
