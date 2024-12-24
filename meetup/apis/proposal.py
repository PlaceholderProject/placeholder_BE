from ninja import Router

from meetup.models import Meetup, Member
from meetup.models.proposal import Proposal
from placeholder.utils.decorators import handle_exceptions
from meetup.schemas.proposal import ProposalListSchema, ProposalSchema, ProposalCreateSchema
from meetup.apis.meetup import meetup_router
from placeholder.schemas.base import ResultSchema, Error
from placeholder.utils.auth import JWTAuth


proposal_router = Router(tags=["Proposal"])


@meetup_router.get("{meetup_id}/proposal", response={200: ResultSchema, 401: Error}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def get_proposals(request, meetup_id):
    meetup = Meetup.objects.filter(id=meetup_id).first()
    if not meetup:
        return 404, {"message": "존재 하지 않은 모임입니다."}
    if not request.auth == meetup.organizer:
        return 401, {"message": "권한이 없습니다."}
    proposals = Proposal.objects.prefetch_related("user").filter(meetup_id=meetup_id).all()

    return 200, {"result": [ProposalListSchema(id=proposal.id, user=proposal.user, text=proposal.text, status=proposal.status) for proposal in proposals]}


@meetup_router.post("{meetup_id}/proposal", response={201: ProposalSchema, 404: Error}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def post_proposal(request, meetup_id, payload: ProposalCreateSchema):
    meetup = Meetup.objects.filter(id=meetup_id).first()
    if not meetup:
        return 404, {"message": "존재 하지 않은 모임입니다."}
    proposal = Proposal.objects.create(user=request.auth, meetup=meetup, text=payload.text)
    return 201, proposal


@meetup_router.delete("{meetup_id}/proposal/{proposal_id}", response={204: None, 401: Error, 404: Error}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def delete_proposal(request, meetup_id, proposal_id):
    meetup = Meetup.objects.filter(id=meetup_id).first()
    if not meetup:
        return 404, {"message": "존재 하지 않은 모임 입니다."}
    if not request.auth == meetup.organizer:
        return 401, {"message": "권한이 없습니다."}

    proposal = Proposal.objects.filter(id=proposal_id).first()
    if not proposal:
        return 404, {"message": "존재 하지 않은 신청 입니다."}
    proposal.delete()
    return 204, None


@proposal_router.post("{proposal_id}/acceptance", response={200: ProposalSchema, 401: Error, 404: Error}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def accept_proposal(request, proposal_id):
    proposal = Proposal.objects.prefetch_related("meetup").filter(id=proposal_id).first()
    if not proposal:
        return 404, {"message": "존재 하지 않은 신청 입니다."}
    if not request.auth == proposal.meetup.organizer:
        return 401, {"message": "권한이 없습니다."}
    proposal.status = Proposal.ProposalStatus.ACCEPTANCE.value
    proposal.save()
    if not Member.objects.filter(user=request.auth, meetup_id=proposal.meetup_id).exists():
        Member.objects.create(user=request.auth, meetup_id=proposal.meetup_id)

    return proposal


@proposal_router.post("{proposal_id}/refuse", response={200: ProposalSchema, 401: Error, 404: Error}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def refuse_proposal(request, proposal_id):
    proposal = Proposal.objects.filter(id=proposal_id).first()
    if not proposal:
        return 404, {"message": "존재 하지 않은 신청 입니다."}
    if not request.auth == proposal.meetup.organizer:
        return 401, {"message": "권한이 없습니다."}
    proposal.status = Proposal.ProposalStatus.REFUSE.value
    proposal.save()
    return proposal


@proposal_router.post("{proposal_id}/ignore", response={200: ProposalSchema, 401: Error, 404: Error}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def ignore_proposal(request, proposal_id):
    proposal = Proposal.objects.filter(id=proposal_id).first()
    if not proposal:
        return 404, {"message": "존재 하지 않은 신청 입니다."}
    if not request.auth == proposal.meetup.organizer:
        return 401, {"message": "권한이 없습니다."}
    proposal.status = Proposal.ProposalStatus.IGNORE.value
    proposal.save()
    return proposal
