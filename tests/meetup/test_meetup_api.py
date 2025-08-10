# -*- coding: utf-8 -*-
import json
from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from meetup.models import Meetup, MeetupLike
from meetup.models.member import Member
from tests.conftest import APITestCase

User = get_user_model()


@pytest.mark.django_db
class TestMeetupAPI(APITestCase):
    """Meetup API 테스트"""

    def setup_method(self):
        """테스트 메서드 실행 전 초기화"""
        self.client = Client()
        self.meetup_url = "/api/v1/meetup"

    def test_create_meetup_success(self, create_user, meetup_data):
        """모임 생성 성공 테스트"""
        headers = self.get_auth_headers(create_user)

        response = self.client.post(
            self.meetup_url, data=json.dumps(meetup_data), content_type="application/json", **headers
        )

        assert response.status_code == 201
        response_data = response.json()
        assert response_data["name"] == meetup_data["name"]

        # 데이터베이스 확인
        meetup = Meetup.objects.get(id=response_data["id"])
        assert meetup.organizer == create_user

        # 주최자가 멤버로 자동 추가되었는지 확인
        member = Member.objects.get(user=create_user, meetup=meetup)
        assert member.role == Member.MemberRole.ORGANIZER.value

    def test_get_meetups_list(self, create_meetup_with_member):
        """모임 목록 조회 테스트"""
        response = self.client.get(self.meetup_url)

        assert response.status_code == 200
        response_data = response.json()

        # 실제 페이지네이션 구조에 맞춤
        assert "result" in response_data
        assert "total" in response_data
        assert len(response_data["result"]) >= 1

        # 모임 데이터 확인
        meetup_item = response_data["result"][0]
        assert "id" in meetup_item
        assert "meetup" in meetup_item  # 실제 필드명

    def test_get_meetup_detail(self, create_meetup):
        """모임 상세 조회 테스트"""
        detail_url = f"{self.meetup_url}/{create_meetup.id}"
        response = self.client.get(detail_url)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == create_meetup.id
        assert response_data["name"] == create_meetup.name


@pytest.mark.django_db
class TestMeetupLikeAPI(APITestCase):
    """모임 좋아요 API 테스트"""

    def setup_method(self):
        self.client = Client()

    def test_like_meetup_success(self, create_meetup, create_user):
        """모임 좋아요 성공 테스트"""
        headers = self.get_auth_headers(create_user)
        like_url = f"/api/v1/meetup/{create_meetup.id}/like"

        response = self.client.post(like_url, **headers)

        assert response.status_code == 200

        # 좋아요가 생성되었는지 확인
        assert MeetupLike.objects.filter(user=create_user, meetup=create_meetup).exists()

    def test_like_meetup_unauthorized(self, create_meetup):
        """인증 없이 좋아요 시도 실패 테스트"""
        like_url = f"/api/v1/meetup/{create_meetup.id}/like"

        response = self.client.post(like_url)

        assert response.status_code == 401
