# -*- coding: utf-8 -*-
from ninja import Router

from notification.models import Notification
from notification.schemas.notification import NotificationListResultSchema
from placeholder.utils.auth import JWTAuth
from placeholder.utils.decorators import handle_exceptions

notification_router = Router(tags=["notification"])


@notification_router.get("", response={200: NotificationListResultSchema}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def get_notifications(request):
    user = request.auth
    notifications = Notification.objects.filter(recipient=user)[:10]
    return 200, {"result": notifications}
