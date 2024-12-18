from ninja import Router, File, UploadedFile
from django.shortcuts import get_object_or_404
from meetup.models import Meetup
from meetup.schema.meetup import (
    MeetupCreateSchema,
    MeetupResponseSchema,
    MeetupListResponseSchema, OrganizerSchema
)
from placeholder.utils.decorators import handle_exceptions
from placeholder.utils.exceptions import UnauthorizedAccessException
from placeholder.utils.auth import JWTAuth
from django.db import transaction

meetup_router = Router()


@meetup_router.post("", response={201: MeetupResponseSchema}, auth=JWTAuth())
@handle_exceptions
def create_meetup(request, payload: MeetupCreateSchema, image: UploadedFile = File(None)):
    user = request.auth

    with transaction.atomic():
        meetup = Meetup.objects.create(
            organizer=user,
            name=payload.name,
            description=payload.description,
            place=payload.place,
            place_description=payload.placeDescription,
            started_at=payload.startedAt,
            ended_at=payload.endedAt,
            ad_title=payload.adTitle,
            ad_ended_at=payload.adEndedAt,
            is_public=payload.isPublic,
            image=image,
        )

    return 201, MeetupResponseSchema(
        id=meetup.id,
        isOrganizer=True,
        organizer={
            "name": user.nickname,
            "profile_image": user.image.url if user.image else None
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


@meetup_router.get("", response={200: list[MeetupListResponseSchema]}, auth=JWTAuth())
@handle_exceptions
def get_meetups(request):
    meetups = Meetup.objects.select_related('organizer').prefetch_related('category').all()
    response = []
    for meetup in meetups:
        is_organizer = meetup.organizer == request.auth
        response.append(MeetupListResponseSchema(
            id=meetup.id,
            isOrganizer=is_organizer,
            organizer=OrganizerSchema(
                name=meetup.organizer.nickname,
                profile_image=meetup.organizer.image.url if meetup.organizer.image else None
            ),
            startedAt=meetup.started_at,
            endedAt=meetup.ended_at,
            adEndedAt=meetup.ad_ended_at,
            isPublic=meetup.is_public,
            image=meetup.image.url if meetup.image else None,
        ))
    return response


@meetup_router.get("/{meetup_id}", response={200: MeetupResponseSchema}, auth=JWTAuth())
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


@meetup_router.put("/{meetup_id}", response={200: MeetupResponseSchema}, auth=JWTAuth())
@handle_exceptions
def update_meetup(request, meetup_id: int, payload: MeetupCreateSchema):
    meetup = get_object_or_404(Meetup, id=meetup_id)
    if meetup.organizer != request.auth:
        raise UnauthorizedAccessException()

    meetup.save(payload.dict())

    return MeetupResponseSchema(
        id=meetup.id,
        isOrganizer=True,
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


@meetup_router.delete("/{meetup_id}", auth=JWTAuth())
@handle_exceptions
def delete_meetup(request, meetup_id: int):
    meetup = get_object_or_404(Meetup, id=meetup_id)
    if meetup.organizer != request.auth:
        raise UnauthorizedAccessException()
    meetup.delete()
    return 204
