from datetime import datetime

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


class MeetupResponseSchema(BaseSchema):
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


class MeetupListResponseSchema(BaseSchema):
    id: int
    is_organizer: bool | None = False
    organizer: OrganizerSchema
    started_at: datetime | None = None
    ended_at: datetime | None = None
    ad_ended_at: datetime | None = None
    is_public: bool
    image: str | None = ""
