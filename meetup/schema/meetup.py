from ninja import Schema
from datetime import datetime


class OrganizerSchema(Schema):
    name: str
    profile_image: str | None = None


class MeetupCreateSchema(Schema):
    name: str
    description: str
    place: str
    placeDescription: str
    startedAt: datetime | None = None
    endedAt: datetime | None = None
    adTitle: str
    adEndedAt: datetime
    isPublic: bool
    category: str


class MeetupResponseSchema(Schema):
    id: int
    isOrganizer: bool
    organizer: OrganizerSchema
    name: str
    description: str
    place: str
    placeDescription: str
    startedAt: datetime | None = None
    endedAt: datetime | None = None
    adTitle: str
    adEndedAt: datetime
    isPublic: bool
    image: str | None = None
    category: str | None = None


class MeetupListResponseSchema(Schema):
    id: int
    isOrganizer: bool
    organizer: OrganizerSchema
    startedAt: datetime
    endedAt: datetime
    adEndedAt: datetime
    isPublic: bool
    image: str
