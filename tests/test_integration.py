# -*- coding: utf-8 -*-
import json
from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from meetup.models import Meetup, MeetupLike
from meetup.models.member import Member
from notification.models.notification import Notification
from tests.conftest import APITestCase

User = get_user_model()


@pytest.mark.django_db
class TestUserJourney(APITestCase):
    """사용자 여정 통합 테스트"""

    def setup_method(self):
        self.client = Client()

    def test_complete_user_journey(self):
        """회원가입부터 모임 참가까지 전체 사용자 여정 테스트"""

        # 1. 회원가입
        register_data = {
            "email": "journey@example.com",
            "password": "Journey123!",
            "nickname": "여정테스터",
            "bio": "테스트 사용자",
        }

        response = self.client.post("/api/v1/user", data=json.dumps(register_data), content_type="application/json")
        assert response.status_code == 201

        # 2. 로그인
        login_data = {"email": "journey@example.com", "password": "Journey123!"}

        response = self.client.post("/api/v1/auth/login", data=json.dumps(login_data), content_type="application/json")
        assert response.status_code == 200
        tokens = response.json()
        access_token = tokens["access"]

        headers = {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}

        # 3. 모임 생성
        meetup_data = {
            "name": "통합테스트 모임",
            "description": "통합테스트용 모임입니다",
            "place": "서울",
            "placeDescription": "강남역",
            "startedAt": (date.today() + timedelta(days=7)).isoformat(),
            "endedAt": (date.today() + timedelta(days=14)).isoformat(),
            "adTitle": "통합테스트 광고",
            "adEndedAt": (date.today() + timedelta(days=3)).isoformat(),
            "isPublic": True,
            "category": "스터디",
        }

        response = self.client.post(
            "/api/v1/meetup", data=json.dumps(meetup_data), content_type="application/json", **headers
        )
        assert response.status_code == 201
        meetup_id = response.json()["id"]

        # 4. 모임 목록에서 내 모임 확인
        response = self.client.get("/api/v1/meetup", **headers)
        assert response.status_code == 200
        meetup_items = response.json()["result"]
        my_meetup = next((item for item in meetup_items if item["id"] == meetup_id), None)
        assert my_meetup is not None
        assert my_meetup["isOrganizer"] is True

        # 5. 다른 사용자 생성 및 모임 참가
        other_user_data = {"email": "other@example.com", "password": "Other123!", "nickname": "다른사용자", "bio": ""}

        response = self.client.post("/api/v1/user", data=json.dumps(other_user_data), content_type="application/json")
        assert response.status_code == 201

        # 다른 사용자 로그인
        other_login_data = {"email": "other@example.com", "password": "Other123!"}

        response = self.client.post(
            "/api/v1/auth/login", data=json.dumps(other_login_data), content_type="application/json"
        )
        other_token = response.json()["access"]
        other_headers = {"HTTP_AUTHORIZATION": f"Bearer {other_token}"}

        # 6. 다른 사용자가 모임에 참가
        join_data = {"text": "some text"}
        response = self.client.post(
            f"/api/v1/meetup/{meetup_id}/proposal",
            data=json.dumps(join_data),
            content_type="application/json",
            **other_headers,
        )
        assert response.status_code == 201

        proposal_id = response.json()["id"]

        response = self.client.post(f"/api/v1/proposal/{proposal_id}/acceptance", **headers)
        assert response.status_code == 200

        # 7. 모임 멤버 수 확인
        member_count = Member.objects.filter(meetup_id=meetup_id).count()
        assert member_count == 2  # 주최자 + 참가자

        # 8. 다른 사용자가 모임에 좋아요
        response = self.client.post(f"/api/v1/meetup/{meetup_id}/like", **other_headers)
        assert response.status_code == 200

        # 9. 좋아요 수 확인
        meetup = Meetup.objects.get(id=meetup_id)
        # 실제 구현에서는 좋아요 수가 자동으로 업데이트되어야 함
        likes_count = MeetupLike.objects.filter(meetup_id=meetup_id).count()
        assert likes_count == 1

    def test_meetup_lifecycle(self, create_user):
        """모임 라이프사이클 테스트"""
        headers = self.get_auth_headers(create_user)

        # 1. 모임 생성
        meetup_data = {
            "name": "라이프사이클 테스트 모임",
            "description": "라이프사이클 테스트",
            "place": "서울",
            "placeDescription": "테스트 장소",
            "startedAt": (date.today() + timedelta(days=7)).isoformat(),
            "endedAt": (date.today() + timedelta(days=14)).isoformat(),
            "adTitle": "라이프사이클 광고",
            "adEndedAt": (date.today() + timedelta(days=3)).isoformat(),
            "isPublic": True,
            "category": "테스트",
        }

        response = self.client.post(
            "/api/v1/meetup", data=json.dumps(meetup_data), content_type="application/json", **headers
        )
        assert response.status_code == 201
        meetup_id = response.json()["id"]

        # 2. 모임 정보 수정
        update_data = {**meetup_data, "name": "수정된 모임 이름", "description": "수정된 설명"}

        response = self.client.put(
            f"/api/v1/meetup/{meetup_id}", data=json.dumps(update_data), content_type="application/json", **headers
        )
        assert response.status_code == 200

        # 3. 모임 상세 조회로 수정 확인
        response = self.client.get(f"/api/v1/meetup/{meetup_id}")
        assert response.status_code == 200
        meetup_detail = response.json()
        assert meetup_detail["name"] == update_data["name"]
        assert meetup_detail["description"] == update_data["description"]

        # 4. 모임 삭제
        response = self.client.delete(f"/api/v1/meetup/{meetup_id}", **headers)
        assert response.status_code == 204

        # 5. 삭제된 모임 조회 시 404 확인
        response = self.client.get(f"/api/v1/meetup/{meetup_id}")
        assert response.status_code == 404


@pytest.mark.django_db
class TestAPIErrorHandling(APITestCase):
    """API 에러 핸들링 통합 테스트"""

    def setup_method(self):
        self.client = Client()

    def test_authentication_errors(self):
        """인증 관련 에러 테스트"""

        # 1. 토큰 없이 인증 필요한 API 호출
        response = self.client.post(
            "/api/v1/meetup", data=json.dumps({"name": "테스트"}), content_type="application/json"
        )
        assert response.status_code == 401

        # 2. 잘못된 토큰으로 API 호출
        headers = {"HTTP_AUTHORIZATION": "Bearer invalid_token"}
        response = self.client.post(
            "/api/v1/meetup", data=json.dumps({"name": "테스트"}), content_type="application/json", **headers
        )
        assert response.status_code == 401

    def test_validation_errors(self, create_user):
        """데이터 검증 에러 테스트"""
        headers = self.get_auth_headers(create_user)

        # 1. 필수 필드 누락
        incomplete_data = {
            "name": "테스트 모임"
            # 필수 필드들 누락
        }

        response = self.client.post(
            "/api/v1/meetup", data=json.dumps(incomplete_data), content_type="application/json", **headers
        )
        assert response.status_code in [400, 422]

        # 2. 잘못된 데이터 형식
        invalid_data = {"name": "테스트 모임", "startedAt": "invalid_date_format"}

        response = self.client.post(
            "/api/v1/meetup", data=json.dumps(invalid_data), content_type="application/json", **headers
        )
        assert response.status_code in [400, 422]

    def test_permission_errors(self, create_meetup, create_user, meetup_data):
        """권한 관련 에러 테스트"""
        headers = self.get_auth_headers(create_user)  # 주최자가 아닌 사용자
        update_data = {**meetup_data, "name": "수정 시도"}
        # 1. 권한 없는 사용자가 모임 수정 시도
        response = self.client.put(
            f"/api/v1/meetup/{create_meetup.id}",
            data=json.dumps(update_data),
            content_type="application/json",
            **headers,
        )
        assert response.status_code == 401

        # 2. 권한 없는 사용자가 모임 삭제 시도
        response = self.client.delete(f"/api/v1/meetup/{create_meetup.id}", **headers)
        assert response.status_code == 401

    def test_not_found_errors(self, create_user, meetup_data):
        """리소스 찾을 수 없음 에러 테스트"""
        headers = self.get_auth_headers(create_user)

        # 1. 존재하지 않는 모임 조회
        response = self.client.get("/api/v1/meetup/99999")
        assert response.status_code == 404

        # 2. 존재하지 않는 모임 수정 시도
        response = self.client.put(
            "/api/v1/meetup/99999", data=json.dumps(meetup_data), content_type="application/json", **headers
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestAPIPerformance(APITestCase):
    """API 성능 테스트"""

    def setup_method(self):
        self.client = Client()

    def test_meetup_list_with_many_records(self, create_organizer):
        """많은 레코드가 있을 때 모임 목록 조회 성능 테스트"""

        # 50개의 모임 생성
        meetups = []
        for i in range(50):
            meetup = Meetup.objects.create(
                name=f"테스트 모임 {i}",
                description=f"테스트 설명 {i}",
                place="서울",
                place_description="테스트 장소",
                ad_title=f"광고 제목 {i}",
                ad_ended_at=date.today() + timedelta(days=5),
                organizer=create_organizer,
                category="테스트",
            )
            meetups.append(meetup)

        # API 호출 시간 측정 (실제 성능 테스트에서는 더 정교한 측정 필요)
        import time

        start_time = time.time()

        response = self.client.get("/api/v1/meetup")

        end_time = time.time()
        response_time = end_time - start_time

        assert response.status_code == 200
        # 1초 이내 응답 (임의 기준)
        assert response_time < 1.0

        # 페이지네이션 확인
        response_data = response.json()
        assert "result" in response_data
        assert "total" in response_data
        assert response_data["total"] == 50
