# -*- coding: utf-8 -*-
import logging

from django.http import JsonResponse
from ninja import NinjaAPI, Swagger
from ninja.errors import HttpError, ValidationError

from meetup.apis.meetup import meetup_router
from meetup.apis.meetup_comment import meetup_comment_router
from meetup.apis.member import member_router
from meetup.apis.proposal import proposal_router
from meetup.apis.schedule import schedule_router
from meetup.apis.schedule_comment import schedule_comment_router
from placeholder.utils.enums import APIStatus
from user.apis.auth import auth_router
from user.apis.user import user_router

logger = logging.getLogger(__name__)

api = NinjaAPI(docs=Swagger(settings={"by_alias": True}))

api.add_router("/auth", auth_router)
api.add_router("/user", user_router)
api.add_router("/meetup", meetup_router)
api.add_router("/member", member_router)
api.add_router("/proposal", proposal_router)
api.add_router("/schedule", schedule_router)
api.add_router("/meetup-comment", meetup_comment_router)
api.add_router("/schedule-comment", schedule_comment_router)


def global_exception_handler(request, exc):
    if isinstance(exc, HttpError):
        return JsonResponse({"detail": exc.message}, status=exc.status_code)
    elif isinstance(exc, ValidationError):
        return JsonResponse({"detail": APIStatus.BAD_REQUEST.message}, status=APIStatus.BAD_REQUEST.code)

    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JsonResponse(
        {"detail": APIStatus.INTERNAL_SERVER_ERROR.message}, status=APIStatus.INTERNAL_SERVER_ERROR.code
    )


api.add_exception_handler(Exception, global_exception_handler)
