from placeholder.schemas.base import BaseSchema


class MemberListSchema(BaseSchema):
    id: int
    meetup_id: int
    user_id: int
    role: str
