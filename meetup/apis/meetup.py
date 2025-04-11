# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models import Count, Exists, F, OuterRef, Q
from ninja import File, Router, UploadedFile

from meetup.models import Meetup, MeetupLike, Member
from meetup.schemas.meetup import (
    MeetupCreateSchema,
    MeetupLikeSchema,
    MeetupListResultSchema,
    MeetupSchema,
)
from placeholder.schemas.base import ErrorSchema
from placeholder.utils.auth import JWTAuth
from placeholder.utils.decorators import handle_exceptions
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


@meetup_router.get("", response={200: MeetupListResultSchema}, by_alias=True)
@handle_exceptions
def get_meetups(request):
    user = request.auth if hasattr(request, "auth") else None
    meetups = (
        Meetup.objects.select_related("organizer")
        .annotate(
            is_like=Exists(MeetupLike.objects.filter(meetup_id=OuterRef("id"), user=user)),
            comment_count=Count("meetupcomment", filter=Q(meetupcomment__meetup_id=F("id"))),
        )
        .all()
    )
    return 200, {"result": meetups}


@meetup_router.get("{meetup_id}", response={200: MeetupSchema, 404: ErrorSchema}, by_alias=True)
@handle_exceptions
def get_meetup(request, meetup_id: int):
    user = request.auth if hasattr(request, "auth") else None
    meetup = (
        Meetup.objects.select_related("organizer")
        .annotate(
            is_like=Exists(MeetupLike.objects.filter(meetup_id=OuterRef("id"), user=user)),
            comment_count=Count("meetupcomment", filter=Q(meetupcomment__meetup_id=F("id"))),
        )
        .filter(id=meetup_id)
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


@meetup_router.get("{meetup_id}/like", response={200: MeetupLikeSchema}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def get_meetup_like(request, meetup_id: int):
    user = request.auth

    meetup = (
        Meetup.objects.filter(id=meetup_id)
        .annotate(is_like=Exists(MeetupLike.objects.filter(user=user, meetup_id=meetup_id)))
        .first()
    )
    print(meetup.like_count)

    return 200, meetup
