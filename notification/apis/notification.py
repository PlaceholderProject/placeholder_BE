# -*- coding: utf-8 -*-
from django.db.models import F
from ninja import Router

from notification.models import Notification
from notification.schemas.notification import NotificationListResultSchema
from placeholder.schemas.base import ErrorSchema
from placeholder.utils.auth import JWTAuth
from placeholder.utils.decorators import handle_exceptions

notification_router = Router(tags=["notification"])


@notification_router.get("", response={200: NotificationListResultSchema}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def get_notifications(request):
    user = request.auth
    notifications = Notification.objects.filter(recipient=user)[:10]
    return 200, {"result": notifications}


@notification_router.post(
    "{notification_id}/read", response={204: None, 404: ErrorSchema}, auth=JWTAuth(), by_alias=True
)
@handle_exceptions
def read_notification(request, notification_id):
    user = request.auth
    result = Notification.objects.filter(id=notification_id, recipient=user).update(is_public=~F("is_public"))
    if not result:
        return 404, {"message": "존재하지 않은 알림 입니다."}
    return 204
