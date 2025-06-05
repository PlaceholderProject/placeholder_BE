# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List, Optional
from urllib.parse import unquote

from django.db import transaction
from django.db.models import BooleanField, Count, Exists, F, OuterRef, Q, Value
from ninja import File, Query, Router, UploadedFile
from ninja.pagination import paginate

from meetup.models import Meetup, MeetupLike, Member
from meetup.schemas.meetup import (
    MeetupCreateSchema,
    MeetupLikeSchema,
    MeetupListSchema,
    MeetupSchema,
)
from placeholder.pagination import CustomPagination
from placeholder.schemas.base import ErrorSchema
from placeholder.utils.auth import JWTAuth, anonymous_user
from placeholder.utils.decorators import handle_exceptions
from placeholder.utils.enums import MeetupSort
from placeholder.utils.exceptions import UnauthorizedAccessException

meetup_router = Router(tags=["Meetup"])


@meetup_router.post("", response={201: MeetupSchema}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def create_meetup(request, payload: MeetupCreateSchema, image: UploadedFile = File(None)):
    user = request.auth

    with transaction.atomic():
        meetup = Meetup.objects.create(**payload.dict(by_alias=False), organizer=user, image=image)
        Member.objects.create(user=request.auth, meetup=meetup, role=Member.MemberRole.ORGANIZER.value)
    return 201, meetup


@meetup_router.get("", response=List[MeetupListSchema], auth=[JWTAuth(), anonymous_user], by_alias=True)
@handle_exceptions
@paginate(CustomPagination)
def get_meetups(
    request,
    category: Optional[str] = Query(None, description="카테고리"),
    place: Optional[str] = Query(None, description="지역"),
    organizer: Optional[str] = Query(None, description="작성자"),
    ad_title: Optional[str] = Query(None, description="광고 타이틀"),
    description: Optional[str] = Query(None, description="내용"),
    sort: Optional[MeetupSort] = Query(None, description="정렬"),
):
    user = request.auth

    if user.is_authenticated:
        is_like_annotation = Exists(MeetupLike.objects.filter(meetup_id=OuterRef("id"), user=user))
    else:
        is_like_annotation = Value(False, output_field=BooleanField())

    filters = {}
    if category:
        filters["category"] = category
    if place:
        filters["place"] = place
    if organizer:
        filters["organizer__nickname__icontains"] = unquote(organizer)
    if ad_title:
        filters["ad_title__icontains"] = unquote(ad_title)
    if description:
        filters["description__icontains"] = unquote(description)

    meetups = (
        Meetup.objects.select_related("organizer")
        .annotate(
            is_like=is_like_annotation,
            comment_count=Count(
                "meetupcomment",
                filter=Q(meetupcomment__is_delete=False),
            ),
        )
        .filter(**filters)
        .all()
    )
    if sort and sort in ["like", "latest", "deadline"]:
        now = datetime.now()
        if sort == "like":
            meetups = meetups.filter(ad_ended_at__lte=now).order_by("-like_count")
        elif sort == "latest":
            meetups = meetups.filter(ad_ended_at__lte=now).order_by("-created_at")
        elif sort == "deadline":
            meetups = meetups.filter(ad_ended_at__lte=now).order_by("-ad_ended_at")

    return meetups


@meetup_router.get(
    "{meetup_id}", response={200: MeetupSchema, 404: ErrorSchema}, auth=[JWTAuth(), anonymous_user], by_alias=True
)
@handle_exceptions
def get_meetup(request, meetup_id: int):
    user = request.auth

    if user.is_authenticated:
        is_like_annotation = Exists(MeetupLike.objects.filter(meetup_id=OuterRef("id"), user=user))
    else:
        is_like_annotation = Value(False, output_field=BooleanField())

    now = datetime.now()
    meetup = (
        Meetup.objects.select_related("organizer")
        .annotate(
            is_like=is_like_annotation,
            comment_count=Count("meetupcomment", filter=Q(meetupcomment__is_delete=False)),
        )
        .filter(id=meetup_id, ad_ended_at__gte=now)
        .first()
    )
    if not meetup:
        return 404, {"message": "존재 하지 않은 모임 입니다."}

    return 200, meetup


@meetup_router.put("{meetup_id}", response={200: MeetupSchema, 404: ErrorSchema}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def update_meetup(request, meetup_id: int, payload: MeetupCreateSchema, image: UploadedFile = File(None)):
    user = request.auth
    meetup = (
        Meetup.objects.select_related("organizer")
        .annotate(is_like=Exists(MeetupLike.objects.filter(meetup_id=OuterRef("id"), user=user)))
        .filter(id=meetup_id)
        .first()
    )
    if not meetup:
        return 404, {"message": "존재 하지 않은 모임 입니다."}
    if meetup.organizer != user:
        raise UnauthorizedAccessException()
    for attr, value in payload.model_dump(by_alias=False).items():
        setattr(meetup, attr, value)

    if image:
        meetup.image = image

    meetup.save()
    return meetup


@meetup_router.delete("{meetup_id}", response={204: None, 404: ErrorSchema}, auth=JWTAuth())
@handle_exceptions
def delete_meetup(request, meetup_id: int):
    meetup = Meetup.objects.filter(id=meetup_id).first()
    if not meetup:
        return 404, {"message": "존재 하지 않은 모임 입니다."}
    if meetup.organizer != request.auth:
        raise UnauthorizedAccessException()
    meetup.delete()
    return 204, None


@meetup_router.post("{meetup_id}/like", response={200: None, 204: None}, auth=JWTAuth())
@handle_exceptions
def like_meetup(request, meetup_id: int):
    user = request.auth
    like, is_create = MeetupLike.objects.get_or_create(user=user, meetup_id=meetup_id)
    if is_create:
        Meetup.objects.filter(id=meetup_id).update(like_count=F("like_count") + 1)
        return 200, None
    like.delete()
    Meetup.objects.filter(id=meetup_id).update(like_count=F("like_count") - 1)
    return 204, None


@meetup_router.get(
    "{meetup_id}/like", response={200: MeetupLikeSchema}, auth=[JWTAuth(), anonymous_user], by_alias=True
)
@handle_exceptions
def get_meetup_like(request, meetup_id: int):
    user = request.auth

    if user.is_authenticated:
        is_like_annotation = Exists(MeetupLike.objects.filter(meetup_id=OuterRef("id"), user=user))
    else:
        is_like_annotation = Value(False, output_field=BooleanField())

    meetup = Meetup.objects.filter(id=meetup_id).annotate(is_like=is_like_annotation).first()

    return 200, meetup
