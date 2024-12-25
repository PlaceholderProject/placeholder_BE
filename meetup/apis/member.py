from meetup.models import Meetup
from placeholder.utils.decorators import handle_exceptions
from meetup.schemas.member import MemberListSchema
from meetup.apis.meetup import meetup_router
from meetup.models.member import Member
from placeholder.schemas.base import ResultSchema, ErrorSchema
from placeholder.utils.auth import JWTAuth


@meetup_router.get("{meetup_id}/member", response={200: ResultSchema}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def get_members(request, meetup_id):
    members = Member.objects.filter(meetup_id=meetup_id).all()
    return 200, {"result": [MemberListSchema(id=member.id, meetup_id=member.meetup_id, user_id=member.user_id, role=member.role) for member in members]}


@meetup_router.delete("{meetup_id}/member/{member_id}", response={204: None, 401: ErrorSchema, 404: ErrorSchema}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def delete_member(request, meetup_id, member_id):
    meetup = Meetup.objects.filter(id=meetup_id).first()
    if not meetup:
        return 404, {"message": "존재 하지 않는 모임 입니다."}
    if not request.auth == meetup.organizer:
        return 401, {"message": "권한이 없습니다."}

    member = Member.objects.filter(id=member_id).first()
    if not member:
        return 404, {"message": "존재 하지 않은 모임원 입니다."}
    member.delete()
    return 204, None
