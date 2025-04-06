# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional

from django.db.models import BooleanField, Case, F, When
from ninja import File, Form, Query, Router
from ninja.files import UploadedFile

from meetup.models import Meetup, Proposal
from placeholder.utils.auth import JWTAuth
from placeholder.utils.decorators import handle_exceptions
from placeholder.utils.enums import MeetupStatus
from user.models.user import User
from user.schemas.user import (
    MyAdListSchema,
    MyMeetupListSchema,
    MyProposalListSchema,
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


@user_router.get("/me/meetup", response={200: MyMeetupListSchema}, auth=JWTAuth())
@handle_exceptions
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
    return 200, {"result": meetups}


@user_router.get("/me/ad", response={200: MyAdListSchema}, auth=JWTAuth())
@handle_exceptions
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
    return 200, {"result": ads}


@user_router.get("/me/proposal", response={200: MyProposalListSchema}, auth=JWTAuth())
@handle_exceptions
def get_my_proposals(request):
    user = request.auth

    proposals = (
        Proposal.objects.select_related("meetup").filter(user=user).annotate(meetup_name=F("meetup__name")).all()
    )

    return 200, {"result": proposals}
