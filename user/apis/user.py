# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List, Optional

from django.db.models import BooleanField, Case, F, When
from ninja import File, Form, Query, Router
from ninja.files import UploadedFile
from ninja.pagination import paginate

from meetup.models import Meetup, Proposal
from meetup.schemas.proposal import ProposalListSchema
from placeholder.pagination import CustomPagination
from placeholder.utils.auth import JWTAuth
from placeholder.utils.decorators import handle_exceptions
from placeholder.utils.enums import MeetupStatus
from user.models.user import User
from user.schemas.user import (
    MyAdSchema,
    MyMeetupSchema,
    MyProposalSchema,
    UserCreateSchema,
    UserSchema,
    UserUpdateSchema,
)

user_router = Router(tags=["User"])


@user_router.post("", response={201: None})
@handle_exceptions
def create_user(request, payload: UserCreateSchema):
    User.objects.create_user(**payload.dict())
    return 201, None


@user_router.get("/me", response={200: UserSchema}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def get_user(request):
    user = request.auth
    return 200, user


@user_router.put("/me", response={200: UserSchema}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def update_user(request, item: Form[UserUpdateSchema], image: UploadedFile = File(None)):
    user = request.auth

    for attr, value in item.model_dump(by_alias=False).items():
        setattr(user, attr, value)

    if image:
        user.image = image
    user.save()

    return 200, user


@user_router.delete("/me", response={204: None}, auth=JWTAuth())
@handle_exceptions
def delete_user(request):
    user = request.auth

    user.delete()
    return 204, None


@user_router.get("/me/meetup", response=List[MyMeetupSchema], auth=JWTAuth())
@handle_exceptions
@paginate(CustomPagination)
def get_my_meetups(
    request,
    status: Optional[MeetupStatus] = Query(None, description="모임 상태 (ongoing 또는 ended)"),
    organizer: Optional[bool] = Query(None, description="모임장 여부"),
):
    user = request.auth
    now = datetime.now()

    filters = {}
    if status == "ongoing":
        filters["ended_at__gt"] = now
    elif status == "ended":
        filters["ended_at__lt"] = now
    if organizer is not None and organizer:
        filters["organizer"] = user

    meetups = (
        Meetup.objects.prefetch_related("member_set")
        .filter(member__user=user, **filters)
        .annotate(
            is_organizer=Case(When(organizer=user, then=True), default=False, output_field=BooleanField()),
            is_current=Case(
                When(ended_at__gt=now, then=True),
                default=False,
                output_field=BooleanField(),
            ),
        )
        .order_by("ended_at")
        .all()
    )

    if organizer is not None and not organizer:
        meetups = meetups.exclude(organizer=user)
    return meetups


@user_router.get("/me/ad", response=List[MyAdSchema], auth=JWTAuth())
@handle_exceptions
@paginate(CustomPagination)
def get_my_ads(request, status: Optional[str] = Query(None, description="광고 상태 (ongoing 또는 ended)")):
    user = request.auth
    now = datetime.now()

    if status == "ongoing":
        filters = {"ad_ended_at__gt": now}
    elif status == "ended":
        filters = {"ad_ended_at__lt": now}
    else:
        filters = {}

    ads = (
        Meetup.objects.filter(organizer=user, **filters)
        .annotate(
            is_current=Case(
                When(ad_ended_at__gt=now, then=True),
                default=False,
                output_field=BooleanField(),
            )
        )
        .order_by("ad_ended_at")
        .all()
    )
    return ads


@user_router.get("/me/proposal", response=List[MyProposalSchema], auth=JWTAuth())
@handle_exceptions
@paginate(CustomPagination)
def get_my_proposals(request):
    user = request.auth

    proposals = (
        Proposal.objects.select_related("meetup")
        .filter(user=user, is_hide_to_proposer=False)
        .annotate(meetup_name=F("meetup__name"), meetup_ad_title=F("meetup__ad_title"))
        .all()
    )

    return proposals


@user_router.get(
    "me/proposal/received",
    response=List[ProposalListSchema],
    auth=JWTAuth(),
    by_alias=True,
)
@handle_exceptions
@paginate(CustomPagination)
def get_received_proposals(request):
    user = request.auth
    meetups = Meetup.objects.filter(organizer=user).all()
    if not meetups:
        return 404, {"message": "존재 하지 않은 모임입니다."}

    proposals = Proposal.objects.prefetch_related("user").filter(meetup_id__in=meetups).exclude(user=user).all()

    return proposals
