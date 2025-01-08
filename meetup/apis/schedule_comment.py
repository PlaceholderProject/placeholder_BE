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
from placeholder.schemas.base import ErrorSchema
from placeholder.utils.auth import JWTAuth
from placeholder.utils.decorators import handle_exceptions

schedule_comment_router = Router(tags=["ScheduleComment"])


@schedule_router.post(
    "{schedule_id}/comment",
    response={201: CommentSchema, 401: ErrorSchema, 404: ErrorSchema},
    auth=JWTAuth(),
    by_alias=True,
    tags=["ScheduleComment"],
)
@handle_exceptions
def create_schedule_comment(request, schedule_id, payload: ScheduleCommentCreateSchema):
    user = request.auth
    schedule = Schedule.objects.prefetch_related("participant").filter(id=schedule_id).first()
    if not schedule:
        return 404, {"message": "존재 하지 않은 스케줄 입니다."}
    if not Member.objects.filter(meetup__schedule__id=schedule_id, user=user).exists():
        return 401, {"message": "권한이 없습니다."}
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
        for member in schedule.participant
        if not member == user
    ]
    Notification.objects.bulk_create(notifications)

    return 201, comment


@schedule_router.get(
    "{schedule_id}/comment",
    response={200: CommentListResultSchema, 401: ErrorSchema, 404: ErrorSchema},
    auth=JWTAuth(),
    by_alias=True,
    tags=["ScheduleComment"],
)
@handle_exceptions
def get_schedules(request, schedule_id):
    user = request.auth
    schedule = Schedule.objects.filter(id=schedule_id).first()
    if not schedule:
        return 404, {"message": "존재 하지 않은 스케줄 입니다."}
    if not Member.objects.filter(meetup__schedule__id=schedule_id, user=user).exists():
        return 401, {"message": "권한이 없습니다."}
    comments = ScheduleComment.objects.select_related("user").order_by("root", "-created_at")
    return 200, {"result": comments}


@schedule_comment_router.post(
    "{comment_id}/reply",
    response={201: CommentSchema, 401: ErrorSchema, 404: ErrorSchema},
    auth=JWTAuth(),
    by_alias=True,
)
@handle_exceptions
def create_schedule_reply(request, comment_id, payload: ScheduleCommentCreateSchema):
    user = request.auth
    comment = ScheduleComment.objects.select_related("user", "schedule").filter(id=comment_id, is_delete=False).first()
    if not comment:
        return 404, {"message": "존재하지 않은 댓글 입니다"}
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

    return 201, reply


@schedule_comment_router.put(
    "{comment_id}", response={200: CommentSchema, 401: ErrorSchema, 404: ErrorSchema}, auth=JWTAuth(), by_alias=True
)
@handle_exceptions
def update_schedule(request, comment_id, payload: ScheduleCommentCreateSchema):
    user = request.auth
    comment = ScheduleComment.objects.select_related("user").filter(id=comment_id).first()
    if not comment:
        return 404, {"message": "존재 하지 않은 댓글 입니다."}
    if user != comment.user:
        return 401, {"message": "권한이 없습니다."}
    for attr, value in payload.dict().items():
        setattr(comment, attr, value)
    comment.save()
    return 200, comment


@schedule_comment_router.delete(
    "{comment_id}", response={204: None, 401: ErrorSchema, 404: ErrorSchema}, auth=JWTAuth(), by_alias=True
)
@handle_exceptions
def delete_schedule(request, comment_id):
    user = request.auth
    comment = ScheduleComment.objects.select_related("user").filter(id=comment_id).first()
    if not comment:
        return 404, {"message": "존재 하지 않은 댓글 입니다."}
    if user != comment.user:
        return 401, {"message": "권한이 없습니다."}
    comment.delete()
    return 204, None
