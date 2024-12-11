from ninja import Schema
from typing import List, Optional
from datetime import datetime


class OrganizerSchema(Schema):
    name: str
    profile_image: Optional[str]


class MeetupCreateSchema(Schema):
    name: str
    description: str
    place: str
    placeDescription: str
    startedAt: datetime
    endedAt: datetime
    ad_title: str
    adEndedAt: datetime
    isPublic: bool
    category: List[int]


class MeetupResponseSchema(Schema):
    id: int
    isOrganizer: bool
    organizer: OrganizerSchema
    name: str
    description: str
    place: str
    placeDescription: str
    latitude: float
    longitude: float
    startedAt: datetime
    endedAt: datetime
    ad_title: str
    adEndedAt: datetime
    isPublic: bool
    image: str | None = None
    category: List[str]


class MeetupListResponseSchema(Schema):
    id: int
    isOrganizer: bool
    organizer: OrganizerSchema
    startedAt: datetime
    endedAt: datetime
    adEndedAt: datetime
    isPublic: bool
    image: str
