from django.contrib import admin
from user.models.user import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass