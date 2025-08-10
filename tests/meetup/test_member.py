# -*- coding: utf-8 -*-
import json

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from meetup.models import Meetup
from meetup.models.member import Member
from tests.conftest import APITestCase

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestMemberAPI(APITestCase):
    """Member API 테스트 (Proposal 기반)"""

    def setup_method(self):
        """테스트 메서드 실행 전 초기화"""
        self.client = Client()

    def test_join_meetup_via_proposal(self, create_meetup, create_user):
        """제안을 통한 모임 참가 테스트"""
        headers = self.get_auth_headers(create_user)

        # 1. 제안서 제출
        proposal_data = {"text": "참가하고 싶습니다!"}
        proposal_url = f"/api/v1/meetup/{create_meetup.id}/proposal"

        response = self.client.post(
            proposal_url, data=json.dumps(proposal_data), content_type="application/json", **headers
        )

        assert response.status_code == 201
        proposal_data = response.json()
        proposal_id = proposal_data["id"]

        # 2. 주최자가 제안을 수락
        organizer_headers = self.get_auth_headers(create_meetup.organizer)
        accept_url = f"/api/v1/proposal/{proposal_id}/acceptance"

        response = self.client.post(accept_url, **organizer_headers)
        assert response.status_code == 200

        # 3. 멤버가 생성되었는지 확인
        member = Member.objects.filter(user=create_user, meetup=create_meetup).first()
        assert member is not None
        assert member.role == Member.MemberRole.MEMBER.value

    def test_proposal_already_submitted(self, create_meetup, create_user):
        """이미 제안서를 제출한 모임에 재제출 시도 테스트"""
        headers = self.get_auth_headers(create_user)
        proposal_url = f"/api/v1/meetup/{create_meetup.id}/proposal"

        # 첫 번째 제안서 제출
        proposal_data = {"text": "첫 번째 제안입니다"}
        response = self.client.post(
            proposal_url, data=json.dumps(proposal_data), content_type="application/json", **headers
        )
        assert response.status_code == 201

        # 두 번째 제안서 제출 시도
        proposal_data = {"text": "두 번째 제안입니다"}
        response = self.client.post(
            proposal_url, data=json.dumps(proposal_data), content_type="application/json", **headers
        )

        assert response.status_code == 404  # 실제 API 응답
        assert "이미 신청한 모임입니다" in response.json()["detail"]

    def test_proposal_nonexistent_meetup(self, create_user):
        """존재하지 않는 모임에 제안서 제출 시도 테스트"""
        headers = self.get_auth_headers(create_user)
        proposal_url = "/api/v1/meetup/99999/proposal"

        proposal_data = {"text": "존재하지 않는 모임에 제안합니다"}

        response = self.client.post(
            proposal_url, data=json.dumps(proposal_data), content_type="application/json", **headers
        )

        assert response.status_code == 404
        assert "존재 하지 않은 모임입니다" in response.json()["detail"]

    def test_proposal_unauthorized(self, create_meetup):
        """인증 없이 제안서 제출 시도 테스트"""
        proposal_url = f"/api/v1/meetup/{create_meetup.id}/proposal"
        proposal_data = {"text": "인증 없이 제안합니다"}

        response = self.client.post(proposal_url, data=json.dumps(proposal_data), content_type="application/json")

        assert response.status_code == 401

    def test_leave_meetup_success(self, create_meetup_with_member, create_member_user):
        """모임 탈퇴 성공 테스트"""
        headers = self.get_auth_headers(create_member_user)

        # 멤버 ID 확인
        member = Member.objects.get(user=create_member_user, meetup=create_meetup_with_member)

        delete_url = f"/api/v1/member/{member.id}"  # 실제 Member API 경로

        response = self.client.delete(delete_url, **headers)

        assert response.status_code == 204

        # 멤버가 삭제되었는지 확인
        assert not Member.objects.filter(user=create_member_user, meetup=create_meetup_with_member).exists()

    def test_get_meetup_members(self, create_meetup_with_member):
        """모임 멤버 목록 조회 테스트"""
        meetup_id = create_meetup_with_member.id
        members_url = f"/api/v1/meetup/{meetup_id}/member"  # 실제 API 경로

        # 인증이 필요하므로 주최자 권한으로 조회
        headers = self.get_auth_headers(create_meetup_with_member.organizer)

        response = self.client.get(members_url, **headers)

        assert response.status_code == 200
        response_data = response.json()

        # 실제 응답 구조에 맞춤
        assert "result" in response_data
        assert len(response_data["result"]) == 2  # 주최자 + 일반 멤버


@pytest.mark.django_db(transaction=True)
class TestMemberStats:
    """멤버 통계 테스트"""

    def test_meetup_member_count(self, create_meetup_with_member):
        """모임 멤버 수 확인 테스트"""
        member_count = Member.objects.filter(meetup=create_meetup_with_member).count()

        # 주최자 + 일반 멤버 = 2명
        assert member_count == 2

    def test_user_joined_meetups_count(self, create_member_user, create_organizer):
        """사용자가 참가한 모임 수 확인 테스트"""
        # 기존 참가 모임 수 확인 (create_member_user는 create_meetup_with_member에서 자동 생성)
        initial_count = Member.objects.filter(user=create_member_user).count()

        # 추가 모임 생성하여 참가
        from datetime import date, timedelta

        meetup2 = Meetup.objects.create(
            name="두 번째 모임",
            description="두 번째 모임",
            place="부산",
            place_description="해운대",
            ad_title="두 번째 광고",
            ad_ended_at=date.today() + timedelta(days=5),
            organizer=create_organizer,
        )

        Member.objects.create(user=create_member_user, meetup=meetup2, role=Member.MemberRole.MEMBER.value)

        joined_meetups_count = Member.objects.filter(user=create_member_user).count()

        # 기존 참가 수 + 새로 추가한 모임 = initial_count + 1
        assert joined_meetups_count == initial_count + 1
