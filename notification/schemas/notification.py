# -*- coding: utf-8 -*-
from typing import List

from ninja.orm import create_schema

from notification.models.notification import Notification
from placeholder.schemas.base import BaseSchema

NotificationSchema = create_schema(Notification, fields=["message", "url", "is_read"])


class NotificationListResultSchema(BaseSchema):
    result: List[NotificationSchema]
