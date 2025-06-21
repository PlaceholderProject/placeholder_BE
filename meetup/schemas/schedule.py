# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List

from ninja.orm import create_schema

from meetup.models import Schedule
from placeholder.schemas.base import BaseSchema
from user.schemas.user import UserProfileSchema


class ScheduleSchema(BaseSchema):
    id: int
    meetup_id: int
    participant: List[UserProfileSchema]
    scheduled_at: datetime | None = None
    place: str
    address: str
    latitude: str
    longitude: str
    memo: str
    image: str | None = None
    comment_count: int | None = 0


ScheduleCreateSchema = create_schema(
    Schedule, exclude=["id", "created_at", "updated_at", "meetup", "participant"], base_class=BaseSchema
)
