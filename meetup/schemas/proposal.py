# -*- coding: utf-8 -*-
from typing import List

from ninja.orm import create_schema
from pydantic import Field

from meetup.models.proposal import Proposal
from placeholder.schemas.base import BaseSchema
from user.schemas.user import UserProfileSchema


class ProposalListSchema(BaseSchema):
    id: int
    user: UserProfileSchema
    text: str
    status: str


class ProposalCreateSchema(BaseSchema):
    text: str = Field(min_length=0, max_length=40)


ProposalSchema = create_schema(Proposal, fields=["id", "user", "meetup", "text", "status"])


class ProposalListResultSchema(BaseSchema):
    result: List[ProposalListSchema]
