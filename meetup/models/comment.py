# -*- coding: utf-8 -*-
from django.db import models

from meetup.models.meetup import Meetup
from meetup.models.schedule import Schedule
from placeholder.models.base import BaseModel
from user.models.user import User


class CommentManager(models.Manager):
    def get_queryset(self):
        return Comment.objects.filter(is_delete=True).all()


class Comment(BaseModel):
    root = models.BigIntegerField(null=True, blank=True, default=None)
    recipient = models.CharField(max_length=16, null=True, blank=True, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="작성자")
    text = models.TextField()
    is_delete = models.BooleanField(default=False)

    object = CommentManager

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        return self.save()


class MeetupComment(Comment):
    meetup = models.ForeignKey(Meetup, on_delete=models.CASCADE, verbose_name="모임")


class ScheduleComment(Comment):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, verbose_name="스케줄")
