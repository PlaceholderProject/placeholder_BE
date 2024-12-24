from ninja import Schema
from datetime import datetime

from meetup.models import Meetup
from placeholder.schema.base import BaseSchema
from pydantic import field_validator, model_validator, validator, computed_field


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



# class MeetupResponseSchema(BaseModelSchema):
#     organizer = OrganizerSchema
#     class Meta:
#         model = Meetup
#         fields = ["id", "name", "discription", "place", "place_description", "started_at", "ended_at", "ad_title", "ad_title", "ad_ended_at", "is_public", "image", "category"]


    # @computed_field
    # @property
    # def organizer(self):
    #     return OrganizerSchema()
    #


class MeetupListResponseSchema(BaseSchema):
    id: int
    is_organizer: bool | None = False
    organizer: OrganizerSchema
    started_at: datetime | None = None
    ended_at: datetime | None = None
    ad_ended_at: datetime | None = None
    is_public: bool
    image: str | None = ""
