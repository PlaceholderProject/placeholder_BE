# -*- coding: utf-8 -*-
from ninja import Router

from meetup.apis.schedule import schedule_router
from meetup.models import Member, Schedule, ScheduleComment
from meetup.schemas.comment import (
    CommentListResultSchema,
    CommentSchema,
    ScheduleCommentCreateSchema,
)
from notification.models import Notification
from placeholder.utils.auth import JWTAuth
from placeholder.utils.decorators import handle_exceptions
from placeholder.utils.exceptions import ForbiddenException, NotFoundException

schedule_comment_router = Router(tags=["ScheduleComment"])


@schedule_router.post(
    "{schedule_id}/comment",
    response=CommentSchema,
    auth=JWTAuth(),
    by_alias=True,
    tags=["ScheduleComment"],
)
@handle_exceptions
def create_schedule_comment(request, schedule_id, payload: ScheduleCommentCreateSchema):
    user = request.auth
    schedule = Schedule.objects.prefetch_related("participant").filter(id=schedule_id).first()
    if not schedule:
        raise NotFoundException("존재 하지 않은 스케줄 입니다.")
    if not Member.objects.filter(meetup__schedule__id=schedule_id, user=user).exists():
        raise ForbiddenException()
    comment = ScheduleComment.objects.select_related("user").create(
        user=user, schedule_id=schedule_id, **payload.dict(by_alias=False)
    )
    notifications = [
        Notification(
            type=Notification.NotificationType.SCHEDULE_COMMENT.value,
            model_id=schedule.id,
            sender=user,
            recipient=member.organizer,
            message=f"{schedule.memo}에서 {user.nickname}님이 댓글을 달았습니다.",
        )
        for member in schedule.participant.all()
        if not member == user
    ]
    if notifications:
        Notification.objects.bulk_create(notifications)

    return comment


@schedule_router.get(
    "{schedule_id}/comment",
    response=CommentListResultSchema,
    auth=JWTAuth(),
    by_alias=True,
    tags=["ScheduleComment"],
)
@handle_exceptions
def get_schedules(request, schedule_id):
    user = request.auth
    schedule = Schedule.objects.filter(id=schedule_id).first()
    if not schedule:
        raise NotFoundException("존재 하지 않은 스케줄 입니다.")
    if not Member.objects.filter(meetup__schedule__id=schedule_id, user=user).exists():
        raise ForbiddenException()
    comments = ScheduleComment.objects.select_related("user").order_by("root", "-created_at")
    return {"result": comments}


@schedule_comment_router.post(
    "{comment_id}/reply",
    response=CommentSchema,
    auth=JWTAuth(),
    by_alias=True,
)
@handle_exceptions
def create_schedule_reply(request, comment_id, payload: ScheduleCommentCreateSchema):
    user = request.auth
    comment = ScheduleComment.objects.select_related("user", "schedule").filter(id=comment_id, is_delete=False).first()
    if not comment:
        raise NotFoundException("존재하지 않은 댓글 입니다")
    schedule = comment.schedule
    root = comment.root or comment_id
    recipient = comment.user.nickname
    reply = ScheduleComment.objects.create(
        root=root, recipient=recipient, user=user, schedule=schedule, **payload.dict(by_alias=False)
    )

    if user != comment.user:
        Notification.objects.create(
            type=Notification.NotificationType.SCHEDULE_COMMENT.value,
            model_id=schedule.id,
            sender=user,
            recipient=comment.user,
            message=f"{user.nickname}님이 회원님의 댓글에 댓글을 달았습니다.",
        )

    return reply


@schedule_comment_router.put("{comment_id}", response=CommentSchema, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def update_schedule(request, comment_id, payload: ScheduleCommentCreateSchema):
    user = request.auth
    comment = ScheduleComment.objects.select_related("user").filter(id=comment_id).first()
    if not comment:
        raise NotFoundException("존재 하지 않은 댓글 입니다.")
    if user != comment.user:
        raise ForbiddenException()
    for attr, value in payload.model_dump(by_alias=False).items():
        setattr(comment, attr, value)
    comment.save()
    return comment


@schedule_comment_router.delete("{comment_id}", response=None, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def delete_schedule(request, comment_id):
    user = request.auth
    comment = ScheduleComment.objects.select_related("user").filter(id=comment_id).first()
    if not comment:
        raise NotFoundException("존재 하지 않은 댓글 입니다.")
    if user != comment.user:
        raise ForbiddenException()
    comment.delete()
    return None
