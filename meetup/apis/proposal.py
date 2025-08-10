# -*- coding: utf-8 -*-
from typing import List

from ninja import Router
from ninja.pagination import paginate

from meetup.apis.meetup import meetup_router
from meetup.models import Meetup, Member
from meetup.models.proposal import Proposal
from meetup.schemas.proposal import (
    ProposalCreateSchema,
    ProposalListSchema,
    ProposalSchema,
)
from notification.models import Notification
from placeholder.pagination import CustomPagination
from placeholder.utils.auth import JWTAuth
from placeholder.utils.decorators import handle_exceptions
from placeholder.utils.exceptions import ForbiddenException, NotFoundException

proposal_router = Router(tags=["Proposal"])


@meetup_router.get(
    "{meetup_id}/proposal",
    response=List[ProposalListSchema],
    auth=JWTAuth(),
    by_alias=True,
    tags=["Proposal"],
)
@handle_exceptions
@paginate(CustomPagination)
def get_proposals(request, meetup_id):
    meetup = Meetup.objects.filter(id=meetup_id).first()
    if not meetup:
        raise NotFoundException("존재 하지 않은 모임입니다.")
    if not request.auth == meetup.organizer:
        raise ForbiddenException()
    proposals = Proposal.objects.prefetch_related("user").filter(meetup_id=meetup_id).all()

    return proposals


@meetup_router.get(
    "{meetup_id}/proposal/status",
    response=ProposalListSchema,
    auth=JWTAuth(),
)
@handle_exceptions
def get_proposal_status(request, meetup_id):
    user = request.auth
    proposal = Proposal.objects.filter(meetup_id=meetup_id, user=user).first()
    if proposal:
        return proposal
    return None


@meetup_router.post(
    "{meetup_id}/proposal",
    response={201: ProposalSchema},
    auth=JWTAuth(),
    by_alias=True,
    tags=["Proposal"],
)
@handle_exceptions
def post_proposal(request, meetup_id, payload: ProposalCreateSchema):
    user = request.auth
    meetup = Meetup.objects.select_related("organizer").filter(id=meetup_id).first()
    if not meetup:
        raise NotFoundException("존재 하지 않은 모임입니다.")
    if Proposal.objects.filter(user=user, meetup=meetup).exists():
        raise NotFoundException("이미 신청한 모임입니다.")
    proposal = Proposal.objects.create(user=user, meetup=meetup, text=payload.text)

    Notification.objects.create(
        type=Notification.NotificationType.RECEIVED_PROPOSAL.value,
        model_id=proposal.id,
        sender=user,
        recipient=meetup.organizer,
        message=f"{user.nickname}님이 {meetup.ad_title}에 신청서를 보냈습니다.",
    )

    return proposal


@proposal_router.delete("{proposal_id}", response={204: None}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def delete_proposal(request, proposal_id):
    user = request.auth
    proposal = Proposal.objects.select_related("meetup").filter(id=proposal_id).first()
    if not proposal:
        raise NotFoundException("존재 하지 않은 신청 입니다.")
    if user == proposal.meetup.organizer or user == proposal.user:
        proposal.delete()
        return None
    raise ForbiddenException()


@proposal_router.post(
    "{proposal_id}/acceptance",
    response=ProposalSchema,
    auth=JWTAuth(),
    by_alias=True,
)
@handle_exceptions
def accept_proposal(request, proposal_id):
    user = request.auth
    proposal = Proposal.objects.select_related("meetup").filter(id=proposal_id).first()
    if not proposal:
        raise NotFoundException("존재 하지 않은 신청 입니다.")
    meetup = proposal.meetup
    if not request.auth == meetup.organizer:
        raise ForbiddenException()
    proposal.status = Proposal.ProposalStatus.ACCEPTANCE.value
    proposal.save()
    if not Member.objects.filter(user_id=proposal.user_id, meetup_id=meetup.id).exists():
        Member.objects.create(user_id=proposal.user_id, meetup_id=meetup.id)

    Notification.objects.create(
        type=Notification.NotificationType.SENT_PROPOSAL.value,
        model_id=proposal.id,
        sender=user,
        recipient=proposal.user,
        message=f"{meetup.ad_title}에서 회원님의 신청서를 수락했습니다.",
    )
    return proposal


@proposal_router.post(
    "{proposal_id}/refuse",
    response=ProposalSchema,
    auth=JWTAuth(),
    by_alias=True,
)
@handle_exceptions
def refuse_proposal(request, proposal_id):
    user = request.auth
    proposal = Proposal.objects.select_related("meetup").filter(id=proposal_id).first()
    if not proposal:
        raise NotFoundException("존재 하지 않은 신청 입니다.")
    meetup = proposal.meetup
    if not user == meetup.organizer:
        raise ForbiddenException()
    proposal.status = Proposal.ProposalStatus.REFUSE.value
    proposal.save()

    Notification.objects.create(
        type=Notification.NotificationType.SENT_PROPOSAL.value,
        model_id=proposal.id,
        sender=user,
        recipient=proposal.user,
        message=f"{meetup.ad_title}에서 회원님의 신청서를 거절했습니다.",
    )
    return proposal


@proposal_router.post(
    "{proposal_id}/ignore",
    response=ProposalSchema,
    auth=JWTAuth(),
    by_alias=True,
)
@handle_exceptions
def ignore_proposal(request, proposal_id):
    user = request.auth
    proposal = Proposal.objects.select_related("meetup").filter(id=proposal_id).first()
    if not proposal:
        raise NotFoundException("존재 하지 않은 신청 입니다.")
    if not user == proposal.meetup.organizer:
        raise ForbiddenException()
    proposal.status = Proposal.ProposalStatus.IGNORE.value
    proposal.save()
    return proposal


@proposal_router.post(
    "{proposal_id}/hide",
    response=None,
    auth=JWTAuth(),
    by_alias=True,
)
@handle_exceptions
def hide_proposal(request, proposal_id):
    user = request.auth
    proposal = Proposal.objects.select_related("meetup").filter(id=proposal_id, user=user).first()
    if not proposal:
        raise NotFoundException("존재 하지 않은 신청 입니다.")
    proposal.is_hide_to_proposer = True
    proposal.save()
    return None
