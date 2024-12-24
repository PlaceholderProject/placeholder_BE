from placeholder.models.base import BaseModel
from user.models.user import User
from meetup.models.meetup import Meetup
from django.db import models
from placeholder.utils.enums import StrEnum


class Member(BaseModel):
    class MemberRole(StrEnum):
        ORGANIZER = "ORGANIZER", "모임장"
        MEMBER = "MEMBER", "모임원"
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="회원")
    meetup = models.ForeignKey(Meetup, on_delete=models.CASCADE, verbose_name="모임")
    role = models.CharField(verbose_name="역할", choices=MemberRole.get_values())
