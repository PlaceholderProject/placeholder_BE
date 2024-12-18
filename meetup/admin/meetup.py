from django.contrib import admin
from meetup.models.meetup import Meetup


@admin.register(Meetup)
class MeetupAdmin(admin.ModelAdmin):
    pass

