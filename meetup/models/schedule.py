# -*- coding: utf-8 -*-
from django.db import models

from meetup.models.meetup import Meetup
from placeholder.models.base import BaseModel
from user.models.user import User


class Schedule(BaseModel):
    meetup = models.ForeignKey(Meetup, on_delete=models.CASCADE, verbose_name="모임")
    participant = models.ManyToManyField(User, verbose_name="참여자")
    scheduled_at = models.DateTimeField(verbose_name="예정일")
    place = models.CharField(max_length=50, verbose_name="장소")
    address = models.CharField(max_length=50, verbose_name="주소")
    latitude = models.CharField(max_length=50, verbose_name="위도")
    longitude = models.CharField(max_length=50, verbose_name="경도")
    memo = models.CharField(max_length=50, verbose_name="메모")
    image = models.CharField(verbose_name="이미지", null=True, blank=True, default="")
