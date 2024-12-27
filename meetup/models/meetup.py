# -*- coding: utf-8 -*-
from django.db import models

from placeholder.models.base import BaseModel
from user.models.user import User


class Meetup(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    place = models.CharField(max_length=255)
    place_description = models.TextField()
    image = models.ImageField(verbose_name="이미지", upload_to="meetup_images", null=True, blank=True, default=None)
    started_at = models.DateTimeField(null=True, default=None)
    ended_at = models.DateTimeField(null=True, default=None)
    ad_title = models.CharField(max_length=255)
    ad_ended_at = models.DateTimeField()
    is_public = models.BooleanField(default=True)
    category = models.CharField(max_length=255, null=True, blank=True, default=None)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_meetups")
    like_count = models.PositiveIntegerField(blank=True, default=0)

    def __str__(self):
        return self.name


class MeetupLike(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meetup = models.ForeignKey(Meetup, on_delete=models.CASCADE)
