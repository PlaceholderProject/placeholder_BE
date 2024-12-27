# -*- coding: utf-8 -*-
from datetime import datetime
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
    started_at: datetime | None = None
    ended_at: datetime | None = None
    ad_title: str
    ad_ended_at: datetime
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
    started_at: datetime | None = None
    ended_at: datetime | None = None
    ad_title: str
    ad_ended_at: datetime
    is_public: bool
    image: str | None = None
    category: str | None = None
    like_count: int


class MeetupListSchema(BaseSchema):
    id: int
    is_organizer: bool | None = False
    organizer: OrganizerSchema
    started_at: datetime | None = None
    ended_at: datetime | None = None
    ad_ended_at: datetime | None = None
    is_public: bool
    image: str | None = ""
    like_count: int


class MeetupListResultSchema(BaseSchema):
    result: List[MeetupListSchema]
