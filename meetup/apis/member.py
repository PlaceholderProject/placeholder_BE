# -*- coding: utf-8 -*-
from ninja import Router

from meetup.apis.meetup import meetup_router
from meetup.models.member import Member
from meetup.schemas.member import MemberListResultSchema
from placeholder.schemas.base import ErrorSchema
from placeholder.utils.auth import JWTAuth
from placeholder.utils.decorators import handle_exceptions

member_router = Router(tags=["Member"])


@meetup_router.get(
    "{meetup_id}/member", response={200: MemberListResultSchema}, auth=JWTAuth(), by_alias=True, tags=["Member"]
)
@handle_exceptions
def get_members(request, meetup_id):
    members = Member.objects.filter(meetup_id=meetup_id).all()
    return 200, {"result": members}


@member_router.delete(
    "{member_id}", response={204: None, 401: ErrorSchema, 404: ErrorSchema}, auth=JWTAuth(), by_alias=True
)
@handle_exceptions
def delete_member(request, member_id):
    member = Member.objects.select_related("meetup").filter(id=member_id).first()
    if not member:
        return 404, {"message": "존재 하지 않은 모임원 입니다."}

    if request.auth not in [member.user, member.meetup.organizer]:
        return 401, {"message": "권한이 없습니다."}
    member.delete()
    return 204, None
