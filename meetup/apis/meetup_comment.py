# -*- coding: utf-8 -*-
from django.db.models import BooleanField, Case, F, When
from ninja import Router

from meetup.apis.meetup import meetup_router
from meetup.models import Meetup, MeetupComment
from meetup.schemas.comment import (
    CommentSchema,
    MeetupCommentCreateSchema,
    MeetupCommentListSchema,
)
from notification.models import Notification
from placeholder.schemas.base import ErrorSchema
from placeholder.utils.auth import JWTAuth
from placeholder.utils.decorators import handle_exceptions

meetup_comment_router = Router(tags=["MeetupComment"])


@meetup_router.post(
    "{meetup_id}/comment",
    response={201: CommentSchema, 401: ErrorSchema, 404: ErrorSchema},
    auth=JWTAuth(),
    by_alias=True,
    tags=["MeetupComment"],
)
@handle_exceptions
def create_meetup_comment(request, meetup_id, payload: MeetupCommentCreateSchema):
    user = request.auth
    meetup = Meetup.objects.filter(id=meetup_id).first()
    if not meetup:
        return 404, {"message": "존재 하지 않은 모임 입니다."}
    comment = MeetupComment.objects.select_related("user").create(
        user=user, meetup_id=meetup_id, meetup=meetup, **payload.dict(by_alias=False)
    )
    if user != meetup.organizer:
        Notification.objects.create(
            type=Notification.NotificationType.MEETUP_COMMENT.value,
            model_id=meetup.id,
            sender=user,
            recipient=meetup.organizer,
            message=f"{meetup.ad_title}에서 {user.nickname}님이 회원님의 모임에 댓글을 달았습니다.",
        )
    return 201, comment


@meetup_router.get(
    "{meetup_id}/comment",
    response={200: MeetupCommentListSchema, 401: ErrorSchema, 404: ErrorSchema},
    by_alias=True,
    tags=["MeetupComment"],
)
@handle_exceptions
def get_comments(request, meetup_id):
    if not Meetup.objects.filter(id=meetup_id).exists():
        return 404, {"message": "존재 하지 않은 모임 입니다."}
    comments = (
        MeetupComment.objects.select_related("user", "meetup")
        .filter(meetup_id=meetup_id, is_delete=False)
        .annotate(
            is_organizer=Case(
                When(meetup__organizer=F("user"), then=True), default=False, output_field=BooleanField()
            ),
        )
        .order_by("root", "-created_at")
    )
    return 200, {"result": comments}


@meetup_comment_router.post(
    "{comment_id}/reply",
    response={201: CommentSchema, 401: ErrorSchema, 404: ErrorSchema},
    auth=JWTAuth(),
    by_alias=True,
)
@handle_exceptions
def create_comment_reply(request, comment_id, payload: MeetupCommentCreateSchema):
    user = request.auth
    comment = MeetupComment.objects.select_related("user", "meetup").filter(id=comment_id, is_delete=False).first()
    if not comment:
        return 404, {"message": "존재 하지 않은 댓글 입니다."}
    meetup = comment.meetup
    root = comment.root or comment_id
    recipient = comment.user.nickname
    reply = MeetupComment.objects.create(
        root=root, recipient=recipient, user=user, meetup=meetup, **payload.dict(by_alias=False)
    )
    if user != meetup.organizer:
        Notification.objects.create(
            type=Notification.NotificationType.MEETUP_COMMENT.value,
            model_id=meetup.id,
            sender=user,
            recipient=meetup.organizer,
            message=f"{meetup.ad_title}에서 {user.nickname}님이 회원님의 댓글에 답글을 달았습니다.",
        )
    return 201, reply


@meetup_comment_router.put(
    "{comment_id}", response={200: CommentSchema, 401: ErrorSchema, 404: ErrorSchema}, auth=JWTAuth(), by_alias=True
)
@handle_exceptions
def update_comment(request, comment_id, payload: MeetupCommentCreateSchema):
    user = request.auth
    comment = MeetupComment.objects.select_related("user").filter(id=comment_id, is_delete=False).first()
    if not comment:
        return 404, {"message": "존재 하지 않은 댓글 입니다."}
    if user != comment.user:
        return 401, {"message": "권한이 없습니다."}
    MeetupComment.objects.filter(id=comment_id).update(**payload.model_dump(by_alias=False))
    comment.refresh_from_db()
    return 200, comment


@meetup_comment_router.delete(
    "{comment_id}", response={204: None, 401: ErrorSchema, 404: ErrorSchema}, auth=JWTAuth(), by_alias=True
)
@handle_exceptions
def delete_comment(request, comment_id):
    user = request.auth
    comment = MeetupComment.objects.select_related("user").filter(id=comment_id, is_delete=False).first()
    if not comment:
        return 404, {"message": "존재 하지 않은 댓글 입니다."}
    if user != comment.user:
        return 401, {"message": "권한이 없습니다."}
    comment.delete()
    return 204, None
