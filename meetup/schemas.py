from ninja import Schema
from typing import List, Optional
from datetime import datetime
from pydantic import model_validator


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
    adTitle: str
    adEndedAt: datetime
    isPublic: bool
    category: List[int] | str

    @model_validator(mode="before")
    def split_category(self):
        if isinstance(self.category, str):
            self.category = [int(x.strip()) for x in self.category.split(",")]
        return self


class MeetupResponseSchema(Schema):
    id: int
    isOrganizer: bool
    organizer: OrganizerSchema
    name: str
    description: str
    place: str
    placeDescription: str
    startedAt: datetime
    endedAt: datetime
    adTitle: str
    adEndedAt: datetime
    isPublic: bool
    image: str | None = None
    category: List[int] | str

    @model_validator(mode="before")
    def split_category(self):
        if isinstance(self.category, List):
            self.category = ", ".join(str(id) for id in self.category)
        return self


class MeetupListResponseSchema(Schema):
    id: int
    isOrganizer: bool
    organizer: OrganizerSchema
    startedAt: datetime
    endedAt: datetime
    adEndedAt: datetime
    isPublic: bool
    image: str
