from ninja import Router, Schema, File, UploadedFile
from typing import List
from django.shortcuts import get_object_or_404
from meetup.models import Meetup, Category
from meetup.schemas import (
    MeetupCreateSchema,
    MeetupResponseSchema,
    MeetupListResponseSchema
)
from placeholder.utils.decorators import handle_exceptions
from placeholder.utils.exceptions import UnauthorizedAccessException
from placeholder.utils.auth import JWTAuth

meetup_router = Router()


@meetup_router.post("", response={201: MeetupResponseSchema}, auth=JWTAuth())
@handle_exceptions
def create_meetup(request, payload: MeetupCreateSchema, image: UploadedFile = File(None)):
    user = request.auth
    meetup = Meetup.objects.create(
        organizer=user,
        name=payload.name,
        description=payload.description,
        place=payload.place,
        place_description=payload.placeDescription,
        started_at=payload.startedAt,
        ended_at=payload.endedAt,
        ad_title=payload.ad_title,
        ad_ended_at=payload.adEndedAt,
        is_public=payload.isPublic,
        image=image,
    )
    categories = Category.objects.filter(id__in=payload.category)
    meetup.category.set(categories)
    meetup.save()

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
        ad_title=meetup.ad_title,
        adEndedAt=meetup.ad_ended_at,
        isPublic=meetup.is_public,
        image=meetup.image,
        category=[cat.name for cat in meetup.category.all()],
    )


@meetup_router.get("", response={200: MeetupListResponseSchema}, auth=JWTAuth())
@handle_exceptions
def get_meetups(request):
    meetups = Meetup.objects.select_related('organizer').prefetch_related('category').all()
    response = []
    for meetup in meetups:
        is_organizer = meetup.organizer == request.auth
        response.append(MeetupListResponseSchema(
            id=meetup.id,
            isOrganizer=is_organizer,
            organizer={
                "name": meetup.organizer.nickname,
                "profile_image": meetup.organizer.image.url if meetup.organizer.image else None
            },
            startedAt=meetup.started_at,
            endedAt=meetup.ended_at,
            adEndedAt=meetup.ad_ended_at,
            isPublic=meetup.is_public,
            image=meetup.image,
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
        ad_title=meetup.ad_title,
        adEndedAt=meetup.ad_ended_at,
        isPublic=meetup.is_public,
        image=meetup.image,
        category=[cat.id for cat in meetup.category.all()],
    )


@meetup_router.put("/{meetup_id}", response={200: MeetupResponseSchema}, auth=JWTAuth())
@handle_exceptions
def update_meetup(request, meetup_id: int, payload: MeetupCreateSchema):
    meetup = get_object_or_404(Meetup, id=meetup_id)
    if meetup.organizer != request.auth:
        raise UnauthorizedAccessException()

    for field, value in payload.dict().items():
        if field != 'category':
            setattr(meetup, field.lower(), value)
    meetup.save()

    if 'category' in payload.dict():
        categories = Category.objects.filter(id__in=payload.category)
        meetup.category.set(categories)

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
        ad_title=meetup.ad_title,
        adEndedAt=meetup.ad_ended_at,
        isPublic=meetup.is_public,
        image=meetup.image,
        category=[cat.name for cat in meetup.category.all()],
    )


@meetup_router.delete("/{meetup_id}", auth=JWTAuth())
@handle_exceptions
def delete_meetup(request, meetup_id: int):
    meetup = get_object_or_404(Meetup, id=meetup_id)
    if meetup.organizer != request.auth:
        raise UnauthorizedAccessException()
    meetup.delete()
    return 204
