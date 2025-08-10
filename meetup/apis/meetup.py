# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List, Optional
from urllib.parse import unquote

from django.db import transaction
from django.db.models import (
    BooleanField,
    Case,
    Count,
    Exists,
    F,
    OuterRef,
    Q,
    Value,
    When,
)
from ninja import Query, Router
from ninja.pagination import paginate

from meetup.models import Meetup, MeetupLike, Member
from meetup.schemas.meetup import (
    MeetupCreateSchema,
    MeetupLikeSchema,
    MeetupListSchema,
    MeetupSchema,
)
from placeholder.pagination import CustomPagination
from placeholder.schemas.base import PresignedUrlSchema
from placeholder.utils.auth import JWTAuth, anonymous_user
from placeholder.utils.decorators import handle_exceptions
from placeholder.utils.enums import MeetupSort
from placeholder.utils.exceptions import NotFoundException, UnauthorizedAccessException
from placeholder.utils.s3 import S3Service

meetup_router = Router(tags=["Meetup"])


@meetup_router.post("", response={201: MeetupSchema}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def create_meetup(request, payload: MeetupCreateSchema):
    user = request.auth

    with transaction.atomic():
        meetup = Meetup.objects.create(**payload.dict(by_alias=False), organizer=user)
        Member.objects.create(user=request.auth, meetup=meetup, role=Member.MemberRole.ORGANIZER.value)
    return meetup


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
        is_organizer = Case(
            When(organizer_id=user.id, then=Value(True)), default=Value(False), output_field=BooleanField()
        )
    else:
        is_like_annotation = Value(False, output_field=BooleanField())
        is_organizer = Value(False, output_field=BooleanField())

    now = datetime.now()
    filters = {"ad_ended_at__gte": now}
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
            is_organizer=is_organizer,
        )
        .filter(**filters)
        .all()
    )
    if sort and sort in ["like", "latest", "deadline"]:
        if sort == "like":
            meetups = meetups.order_by("-like_count")
        elif sort == "latest":
            meetups = meetups.order_by("-created_at")
        elif sort == "deadline":
            meetups = meetups.order_by("-ad_ended_at")

    return meetups


@meetup_router.get("presigned-url", response=PresignedUrlSchema, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def get_presigned_url(request, filetype):
    s3_service = S3Service()
    filetype_list = filetype.split(",")
    result = s3_service.create_multi_presigned_url("meetup", filetype_list)
    return result


@meetup_router.get("{meetup_id}", response=MeetupSchema, auth=[JWTAuth(), anonymous_user], by_alias=True)
@handle_exceptions
def get_meetup(request, meetup_id: int):
    user = request.auth

    if user.is_authenticated:
        is_like_annotation = Exists(MeetupLike.objects.filter(meetup_id=OuterRef("id"), user=user))
        is_organizer = Case(
            When(organizer_id=user.id, then=Value(True)), default=Value(False), output_field=BooleanField()
        )
    else:
        is_like_annotation = Value(False, output_field=BooleanField())
        is_organizer = Value(False, output_field=BooleanField())

    meetup = (
        Meetup.objects.select_related("organizer")
        .annotate(
            is_like=is_like_annotation,
            comment_count=Count("meetupcomment", filter=Q(meetupcomment__is_delete=False)),
            is_organizer=is_organizer,
        )
        .filter(id=meetup_id)
        .first()
    )
    if not meetup:
        raise NotFoundException("존재 하지 않은 모임 입니다.")

    return meetup


@meetup_router.put("{meetup_id}", response=MeetupSchema, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def update_meetup(request, meetup_id: int, payload: MeetupCreateSchema):
    user = request.auth
    meetup = (
        Meetup.objects.select_related("organizer")
        .annotate(is_like=Exists(MeetupLike.objects.filter(meetup_id=OuterRef("id"), user=user)))
        .filter(id=meetup_id)
        .first()
    )
    if not meetup:
        raise NotFoundException("존재 하지 않은 모임 입니다.")
    if meetup.organizer != user:
        raise UnauthorizedAccessException()
    for attr, value in payload.model_dump(by_alias=False).items():
        setattr(meetup, attr, value)

    meetup.save()
    return meetup


@meetup_router.delete("{meetup_id}", response={204: None}, auth=JWTAuth())
@handle_exceptions
def delete_meetup(request, meetup_id: int):
    meetup = Meetup.objects.filter(id=meetup_id).first()
    if not meetup:
        raise NotFoundException("존재 하지 않은 모임 입니다.")
    if meetup.organizer != request.auth:
        raise UnauthorizedAccessException()
    meetup.delete()
    return None


@meetup_router.post("{meetup_id}/like", response=None, auth=JWTAuth())
@handle_exceptions
def like_meetup(request, meetup_id: int):
    user = request.auth
    like, is_create = MeetupLike.objects.get_or_create(user=user, meetup_id=meetup_id)
    if is_create:
        Meetup.objects.filter(id=meetup_id).update(like_count=F("like_count") + 1)
        return None
    like.delete()
    Meetup.objects.filter(id=meetup_id).update(like_count=F("like_count") - 1)
    return None


@meetup_router.get("{meetup_id}/like", response=MeetupLikeSchema, auth=[JWTAuth(), anonymous_user], by_alias=True)
@handle_exceptions
def get_meetup_like(request, meetup_id: int):
    user = request.auth

    if user.is_authenticated:
        is_like_annotation = Exists(MeetupLike.objects.filter(meetup_id=OuterRef("id"), user=user))
    else:
        is_like_annotation = Value(False, output_field=BooleanField())

    meetup = Meetup.objects.filter(id=meetup_id).annotate(is_like=is_like_annotation).first()

    return meetup
