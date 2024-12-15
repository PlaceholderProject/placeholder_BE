from django.db import models
from placeholder.models.base import BaseModel
from user.models.user import User
from meetup.models.category import Category


class Meetup(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    place = models.CharField(max_length=255)
    place_description = models.TextField()
    image = models.ImageField(verbose_name="이미지", upload_to="meetup_images", null=True, blank=True, default=None)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    ad_title = models.CharField(max_length=255)
    ad_ended_at = models.DateTimeField()
    is_public = models.BooleanField(default=True)
    category = models.ManyToManyField(Category, related_name='meetups')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_meetups')

    def __str__(self):
        return self.name
