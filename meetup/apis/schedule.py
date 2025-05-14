# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models import Count, Q
from ninja import File, Router, UploadedFile

from meetup.apis.meetup import meetup_router
from meetup.models import Meetup, Member, Schedule
from meetup.schemas.schedule import ScheduleCreateSchema, ScheduleSchema
from placeholder.schemas.base import ErrorSchema, ResultSchema
from placeholder.utils.auth import JWTAuth
from placeholder.utils.decorators import handle_exceptions

schedule_router = Router(tags=["Schedule"])


@meetup_router.get(
    "{meetup_id}/schedule",
    response={200: ResultSchema, 401: ErrorSchema},
    auth=JWTAuth(),
    by_alias=True,
    tags=["Schedule"],
)
@handle_exceptions
def get_schedules(request, meetup_id):
    meetup = Meetup.objects.filter(id=meetup_id).first()
    if not meetup:
        return 404, {"message": "존재 하지 않은 모임입니다."}
    if not Member.objects.filter(meetup_id=meetup_id, user=request.auth).exists():
        return 401, {"message": "권한이 없습니다."}
    schedules = (
        Schedule.objects.prefetch_related("participant")
        .filter(meetup_id=meetup_id)
        .annotate(
            comment_count=Count(
                "schedulecomment",
                filter=Q(schedulecomment__is_delete=False),
            ),
        )
        .order_by("scheduled_at")
        .all()
    )
    result = [
        ScheduleSchema(
            id=schedule.id,
            meetup_id=schedule.meetup_id,
            participant=schedule.participant,
            scheduled_at=schedule.scheduled_at,
            place=schedule.place,
            address=schedule.address,
            latitude=schedule.latitude,
            longitude=schedule.longitude,
            memo=schedule.memo,
            image=schedule.image,
            comment_count=schedule.comment_count,
        )
        for schedule in schedules
    ]
    return 200, {"result": result}


@meetup_router.post(
    "{meetup_id}/schedule",
    response={201: ScheduleSchema, 401: ErrorSchema},
    auth=JWTAuth(),
    by_alias=True,
    tags=["Schedule"],
)
@handle_exceptions
def create_schedule(request, meetup_id, payload: ScheduleCreateSchema, image: UploadedFile = File(None)):
    meetup = Meetup.objects.filter(id=meetup_id).first()
    if not meetup:
        return 404, {"message": "존재 하지 않은 모임입니다."}
    if not Member.objects.filter(meetup_id=meetup_id, user=request.auth).exists():
        return 401, {"message": "권한이 없습니다."}
    with transaction.atomic():
        schedule = Schedule.objects.create(**payload.dict(by_alias=False), meetup_id=meetup_id, image=image)
        schedule.participant.set([request.auth])
        schedule.save()
    return 201, schedule


@schedule_router.get(
    "{schedule_id}", response={200: ScheduleSchema, 401: ErrorSchema, 404: ErrorSchema}, auth=JWTAuth(), by_alias=True
)
@handle_exceptions
def get_schedule(request, schedule_id):
    if not Member.objects.filter(meetup__schedule__id=schedule_id, user=request.auth).exists():
        return 401, {"message": "권한이 없습니다."}
    schedule = (
        Schedule.objects.filter(id=schedule_id)
        .order_by("-scheduled_at")
        .annotate(
            comment_count=Count(
                "schedulecomment",
                filter=Q(schedulecomment__is_delete=False),
            ),
        )
        .first()
    )
    if not schedule:
        return 404, {"message": "존재 하지 않은 스케쥴 입니다."}
    return 200, schedule


@schedule_router.put(
    "{schedule_id}", response={200: ScheduleSchema, 401: ErrorSchema, 404: ErrorSchema}, auth=JWTAuth(), by_alias=True
)
@handle_exceptions
def update_schedule(request, schedule_id, payload: ScheduleCreateSchema):
    if not Member.objects.filter(meetup__schedule__id=schedule_id, user=request.auth).exists():
        return 401, {"message": "권한이 없습니다."}
    schedule = (
        Schedule.objects.filter(id=schedule_id)
        .annotate(
            comment_count=Count(
                "schedulecomment",
                filter=Q(schedulecomment__is_delete=False),
            ),
        )
        .first()
    )
    if not schedule:
        return 404, {"message": "존재 하지 않은 스케쥴 입니다."}
    for attr, value in payload.model_dump(by_alias=False).items():
        setattr(schedule, attr, value)
    schedule.save()
    return 200, schedule


@schedule_router.delete(
    "{schedule_id}", response={204: None, 401: ErrorSchema, 404: ErrorSchema}, auth=JWTAuth(), by_alias=True
)
@handle_exceptions
def delete_schedule(request, schedule_id):
    if not Member.objects.filter(meetup__schedule__id=schedule_id, user=request.auth).exists():
        return 401, {"message": "권한이 없습니다."}
    schedule = Schedule.objects.filter(id=schedule_id).order_by("-scheduled_at").first()
    if not schedule:
        return 404, {"message": "존재 하지 않은 스케쥴 입니다."}
    schedule.delete()
    return 204, None
