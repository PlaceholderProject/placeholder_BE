# -*- coding: utf-8 -*-
from typing import List

from placeholder.schemas.base import BaseSchema


class MemberListSchema(BaseSchema):
    id: int
    meetup_id: int
    user_id: int
    role: str


class MemberListResultSchema(BaseSchema):
    result: List[MemberListSchema]
