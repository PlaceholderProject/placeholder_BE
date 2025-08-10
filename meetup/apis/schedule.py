# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models import Count, Q
from ninja import Router

from meetup.apis.meetup import meetup_router
from meetup.models import Meetup, Member, Schedule
from meetup.schemas.schedule import ScheduleCreateSchema, ScheduleSchema
from placeholder.schemas.base import PresignedUrlSchema, ResultSchema
from placeholder.utils.auth import JWTAuth
from placeholder.utils.decorators import handle_exceptions
from placeholder.utils.exceptions import ForbiddenException, NotFoundException
from placeholder.utils.s3 import S3Service

schedule_router = Router(tags=["Schedule"])


@meetup_router.get(
    "{meetup_id}/schedule",
    response=ResultSchema,
    auth=JWTAuth(),
    by_alias=True,
    tags=["Schedule"],
)
@handle_exceptions
def get_schedules(request, meetup_id):
    meetup = Meetup.objects.filter(id=meetup_id).first()
    if not meetup:
        raise NotFoundException("존재 하지 않은 모임입니다.")
    if not Member.objects.filter(meetup_id=meetup_id, user=request.auth).exists():
        raise ForbiddenException()
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
    return {"result": schedules}


@meetup_router.post(
    "{meetup_id}/schedule",
    response=ScheduleSchema,
    auth=JWTAuth(),
    by_alias=True,
    tags=["Schedule"],
)
@handle_exceptions
def create_schedule(request, meetup_id, payload: ScheduleCreateSchema):
    meetup = Meetup.objects.filter(id=meetup_id).first()
    if not meetup:
        raise NotFoundException("존재 하지 않은 모임입니다.")
    if not Member.objects.filter(meetup_id=meetup_id, user=request.auth).exists():
        raise ForbiddenException()
    with transaction.atomic():
        schedule = Schedule.objects.create(**payload.dict(by_alias=False), meetup_id=meetup_id)
        schedule.participant.set([request.auth])
        schedule.save()
    return schedule


@schedule_router.get("presigned-url", response=PresignedUrlSchema, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def get_presigned_url(request, filetype):
    s3_service = S3Service()
    filetype_list = filetype.split(",")
    result = s3_service.create_multi_presigned_url("schedule", filetype_list)
    return result


@schedule_router.get("{schedule_id}", response=ScheduleSchema, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def get_schedule(request, schedule_id):
    if not Member.objects.filter(meetup__schedule__id=schedule_id, user=request.auth).exists():
        raise ForbiddenException()
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
        raise NotFoundException("존재 하지 않은 스케쥴 입니다.")
    return schedule


@schedule_router.put("{schedule_id}", response=ScheduleSchema, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def update_schedule(request, schedule_id, payload: ScheduleCreateSchema):
    if not Member.objects.filter(meetup__schedule__id=schedule_id, user=request.auth).exists():
        raise ForbiddenException()
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
        raise NotFoundException("존재 하지 않은 스케쥴 입니다.")
    for attr, value in payload.model_dump(by_alias=False).items():
        setattr(schedule, attr, value)
    schedule.save()
    return schedule


@schedule_router.delete("{schedule_id}", response=None, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def delete_schedule(request, schedule_id):
    if not Member.objects.filter(meetup__schedule__id=schedule_id, user=request.auth).exists():
        raise ForbiddenException()
    schedule = Schedule.objects.filter(id=schedule_id).order_by("-scheduled_at").first()
    if not schedule:
        raise NotFoundException("존재 하지 않은 스케쥴 입니다.")
    schedule.delete()
    return None
