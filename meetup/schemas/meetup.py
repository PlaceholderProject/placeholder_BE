# -*- coding: utf-8 -*-
from datetime import date
from typing import List

from placeholder.schemas.base import BaseSchema


class OrganizerSchema(BaseSchema):
    nickname: str
    profile_image: str | None = None


class MeetupCreateSchema(BaseSchema):
    name: str
    description: str
    place: str
    place_description: str
    started_at: date | None = None
    ended_at: date | None = None
    ad_title: str
    ad_ended_at: date
    is_public: bool
    category: str | None = None


class MeetupSchema(BaseSchema):
    id: int
    is_organizer: bool | None = True
    organizer: OrganizerSchema
    name: str
    description: str
    place: str
    place_description: str
    started_at: date | None = None
    ended_at: date | None = None
    ad_title: str
    ad_ended_at: date
    is_public: bool
    image: str | None = None
    category: str | None = None
    like_count: int | None = 0
    is_like: bool | None = False
    comment_count: int | None = 0


class MeetupListSchema(BaseSchema):
    id: int
    is_organizer: bool | None = False
    organizer: OrganizerSchema
    started_at: date | None = None
    ended_at: date | None = None
    ad_ended_at: date | None = None
    ad_title: str
    place: str
    is_public: bool
    image: str | None = ""
    like_count: int
    is_like: bool
    comment_count: int


class MeetupListResultSchema(BaseSchema):
    result: List[MeetupListSchema]
