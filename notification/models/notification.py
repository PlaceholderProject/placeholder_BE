# -*- coding: utf-8 -*-
from django.db import models

from placeholder.models.base import BaseModel
from placeholder.utils.enums import StrEnum
from user.models.user import User


class Notification(BaseModel):
    class NotificationType(StrEnum):
        MEETUP_COMMENT = "meetup_comment", "모임 댓글"
        SCHEDULE_COMMENT = "schedule_comment", "스캐줄 댓글"
        RECEIVED_PROPOSAL = "received_proposal", "받은 신청"
        SENT_PROPOSAL = "sent_proposal", "보낸 신청"

    type = models.CharField(max_length=32, choices=NotificationType.choices())
    model_id = models.PositiveBigIntegerField()
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_notifications")
    message = models.CharField(max_length=50, blank=True, default="")
    url = models.CharField(blank=True, default="")
    is_read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.url:
            self.url = self._generate_url()
        super().save(*args, **kwargs)

    def _generate_url(self):
        if self.type == "meetup_comment":
            return f"/ad/{self.model_id}/"
        elif self.type == "schedule_comment":
            return f"/schedule/{self.model_id}/"
        elif self.type == "sent_proposal":
            return "/my-space/sent-proposal"
        elif self.type == "received_proposal":
            return "/my-space/received-proposal"
