# -*- coding: utf-8 -*-
from typing import List

from placeholder.schemas.base import BaseSchema
from user.schemas.user import UserProfileSchema


class MemberListSchema(BaseSchema):
    id: int
    meetup_id: int
    user: UserProfileSchema
    role: str


class MemberListResultSchema(BaseSchema):
    result: List[MemberListSchema]
