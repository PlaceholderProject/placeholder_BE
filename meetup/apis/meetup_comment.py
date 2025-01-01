# -*- coding: utf-8 -*-
from ninja import Router

from meetup.apis.meetup import meetup_router
from meetup.models import Meetup, MeetupComment, Member
from meetup.schemas.comment import (
    CommentListResultSchema,
    CommentSchema,
    MeetupCommentCreateSchema,
)
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
    if not Meetup.objects.filter(id=meetup_id).exists():
        return 404, {"message": "존재 하지 않은 모임 입니다."}
    if not Member.objects.filter(user=user, meetup_id=meetup_id).exists():
        return 401, {"message": "권한이 없습니다."}
    comment = MeetupComment.objects.select_related("user").create(
        user=user, meetup_id=meetup_id, **payload.dict(by_alias=False)
    )
    return 201, comment


@meetup_router.get(
    "{meetup_id}/comment",
    response={200: CommentListResultSchema, 401: ErrorSchema, 404: ErrorSchema},
    auth=JWTAuth(),
    by_alias=True,
    tags=["MeetupComment"],
)
@handle_exceptions
def get_comments(request, meetup_id):
    user = request.auth
    if not Meetup.objects.filter(id=meetup_id).exists():
        return 404, {"message": "존재 하지 않은 모임 입니다."}
    if not Member.objects.filter(user=user, meetup_id=meetup_id).exists():
        return 401, {"message": "권한이 없습니다."}
    comments = MeetupComment.objects.select_related("user").filter(is_delete=False).order_by("root", "-created_at")
    return 200, {"result": comments}


@meetup_comment_router.post(
    "{comment_id}/reply",
    response={200: CommentSchema, 401: ErrorSchema, 404: ErrorSchema},
    auth=JWTAuth(),
    by_alias=True,
)
@handle_exceptions
def create_comment_reply(request, comment_id, payload: MeetupCommentCreateSchema):
    user = request.auth
    comment = MeetupComment.objects.select_related("user").filter(id=comment_id, is_delete=False).first()
    if not comment:
        return 404, {"message": "존재 하지 않은 댓글 입니다."}
    root = comment.root or comment_id
    recipient = comment.user.nickname
    reply = MeetupComment.objects.create(root=root, recipient=recipient, user=user, **payload.dict(by_alias=False))
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
    for attr, value in payload.dict().items():
        setattr(comment, attr, value)
    comment.save()
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
