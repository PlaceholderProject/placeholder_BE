# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List

from ninja.orm import create_schema

from meetup.models.comment import MeetupComment, ScheduleComment
from placeholder.schemas.base import BaseSchema
from user.schemas.user import UserProfileSchema

MeetupCommentCreateSchema = create_schema(MeetupComment, fields=["text"], base_class=BaseSchema)


ScheduleCommentCreateSchema = create_schema(ScheduleComment, fields=["text"], base_class=BaseSchema)


class CommentSchema(BaseSchema):
    id: int
    root: int | None = None
    recipient: str | None = None
    user: UserProfileSchema
    text: str
    created_at: datetime


class CommentListResultSchema(BaseSchema):
    result: List[CommentSchema]
