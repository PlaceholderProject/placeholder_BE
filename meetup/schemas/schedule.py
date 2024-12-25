from meetup.models import Schedule
from placeholder.schemas.base import BaseSchema
from ninja.orm import create_schema
from typing import List
from user.schemas.user import UserProfileSchema
from datetime import datetime


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


ScheduleCreateSchema = create_schema(
    Schedule,
    exclude=["id", "created_at", "updated_at", "image", "meetup", "participant"],
    base_class=BaseSchema
)
