from django.contrib import admin
from meetup.models.category import Category
from meetup.models.meetup import Meetup


@admin.register(Meetup)
class MeetupAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class MeetupAdmin(admin.ModelAdmin):
    pass
