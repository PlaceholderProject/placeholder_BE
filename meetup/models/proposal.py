# -*- coding: utf-8 -*-
from django.db import models

from meetup.models import Meetup
from placeholder.models.base import BaseModel
from placeholder.utils.enums import StrEnum
from user.models.user import User


class Proposal(BaseModel):
    class ProposalStatus(StrEnum):
        PENDING = "pending", "대기"
        ACCEPTANCE = "acceptance", "수락"
        REFUSE = "refuse", "거절"
        IGNORE = "ignore", "무시"

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="회원")
    meetup = models.ForeignKey(Meetup, on_delete=models.CASCADE, verbose_name="모임")
    text = models.CharField(verbose_name="내용", blank=True, default="")
    status = models.CharField(
        verbose_name="상태", choices=ProposalStatus.choices(), blank=True, default=ProposalStatus.PENDING.value
    )
    is_hide_to_proposer = models.BooleanField(verbose_name="신청자 숨김 여부", default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_proposal_user_meetup",
                fields=["user", "meetup"],
            ),
        ]
