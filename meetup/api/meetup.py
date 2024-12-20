from ninja import Router, File, UploadedFile
from django.shortcuts import get_object_or_404
from meetup.models import Meetup
from meetup.schema.meetup import (
    MeetupCreateSchema,
    MeetupResponseSchema,
    MeetupListResponseSchema,
    OrganizerSchema,
)
from placeholder.utils.decorators import handle_exceptions
from placeholder.utils.exceptions import UnauthorizedAccessException
from placeholder.utils.auth import JWTAuth
from django.db import transaction
from typing import List


meetup_router = Router(tags=["Meetup"])


@meetup_router.post("", response={201: MeetupResponseSchema}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def create_meetup(request, payload: MeetupCreateSchema, image: UploadedFile = File(None)):
    user = request.auth

    with transaction.atomic():
        meetup = Meetup.objects.create(**payload.dict(by_alias=False), organizer=user, image=image)
    return 201, meetup


@meetup_router.get("", response={200: List[MeetupListResponseSchema]}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def get_meetups(request):
    meetups = Meetup.objects.select_related('organizer').all()
    response = []
    for meetup in meetups:
        is_organizer = meetup.organizer == request.auth
        response.append(MeetupListResponseSchema(
            id=meetup.id,
            isOrganizer=is_organizer,
            organizer=OrganizerSchema(
                nickname=meetup.organizer.nickname,
                profile_image=meetup.organizer.image.url if meetup.organizer.image else None
            ),
            startedAt=meetup.started_at,
            endedAt=meetup.ended_at,
            adEndedAt=meetup.ad_ended_at,
            isPublic=meetup.is_public,
            image=meetup.image.url if meetup.image else "",
        ))
    return 200, response


@meetup_router.get("/{meetup_id}", response={200: MeetupResponseSchema}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def get_meetup(request, meetup_id: int):
    meetup = get_object_or_404(Meetup, id=meetup_id)
    is_organizer = meetup.organizer == request.auth
    return MeetupResponseSchema(
        id=meetup.id,
        isOrganizer=is_organizer,
        organizer={
            "name": meetup.organizer.nickname,
            "profile_image": meetup.organizer.image.url if meetup.organizer.image else None
        },
        name=meetup.name,
        description=meetup.description,
        place=meetup.place,
        placeDescription=meetup.place_description,
        startedAt=meetup.started_at,
        endedAt=meetup.ended_at,
        adTitle=meetup.ad_title,
        adEndedAt=meetup.ad_ended_at,
        isPublic=meetup.is_public,
        image=meetup.image,
        category=meetup.category,
    )


@meetup_router.put("/{meetup_id}", response={200: MeetupResponseSchema}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def update_meetup(request, meetup_id: int, payload: MeetupCreateSchema):
    meetup = get_object_or_404(Meetup, id=meetup_id)
    if meetup.organizer != request.auth:
        raise UnauthorizedAccessException()

    return meetup.update(**payload.dict())


@meetup_router.delete("/{meetup_id}", response={204: None}, auth=JWTAuth())
@handle_exceptions
def delete_meetup(request, meetup_id: int):
    meetup = get_object_or_404(Meetup, id=meetup_id)
    if meetup.organizer != request.auth:
        raise UnauthorizedAccessException()
    meetup.delete()
    return 204, None
