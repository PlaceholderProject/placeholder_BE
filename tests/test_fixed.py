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
class TestBasicAPI(APITestCase):
    """기본적인 API 동작 테스트"""

    def setup_method(self):
        self.client = Client()

    def test_meetup_list_structure(self, create_meetup):
        """모임 목록 응답 구조 확인"""
        response = self.client.get("/api/v1/meetup")

        assert response.status_code == 200
        response_data = response.json()

        # 실제 응답 구조 확인
        print("Meetup List Response:", response_data.keys())

        # 페이지네이션 구조가 다를 수 있음
        if "result" in response_data:
            assert len(response_data["result"]) >= 1
        elif "items" in response_data:
            assert len(response_data["items"]) >= 1
        else:
            # 직접 리스트일 경우
            assert isinstance(response_data, list)
            assert len(response_data) >= 1

    def test_meetup_creation_basic(self, create_user):
        """기본 모임 생성 테스트"""
        headers = self.get_auth_headers(create_user)

        data = {
            "name": "기본 테스트 모임",
            "description": "테스트 설명",
            "place": "서울",
            "placeDescription": "강남",
            "adTitle": "광고 제목",
            "adEndedAt": (date.today() + timedelta(days=3)).isoformat(),
            "startedAt": (date.today() + timedelta(days=7)).isoformat(),
            "endedAt": (date.today() + timedelta(days=14)).isoformat(),
            "isPublic": True,
        }

        response = self.client.post(
            "/api/v1/meetup", data=json.dumps(data), content_type="application/json", **headers
        )

        # 생성 성공하면 201, 실제 API 동작에 따라 다를 수 있음
        print(f"Meetup Creation Status: {response.status_code}")
        if response.status_code not in [200, 201]:
            print(f"Error Response: {response.content}")

        assert response.status_code in [200, 201]

    def test_auth_endpoints_exist(self):
        """인증 엔드포인트 존재 확인"""
        # 로그인 엔드포인트 확인 (GET 요청으로 method not allowed 확인)
        response = self.client.get("/api/v1/auth/login")
        # 405 (Method Not Allowed)가 나오면 엔드포인트가 존재하는 것
        assert response.status_code == 405

        # 이메일 확인 엔드포인트
        response = self.client.get("/api/v1/auth/email")
        assert response.status_code == 405

    def test_s3_mock_response(self):
        """S3 서비스 Mock 응답 테스트"""
        from unittest.mock import MagicMock, patch

        from placeholder.utils.s3 import S3Service

        with patch.object(S3Service, "_get_s3_client") as mock_get_client:
            mock_s3_client = MagicMock()
            mock_get_client.return_value = mock_s3_client

            # Mock successful response
            mock_response = {
                "url": "https://test-bucket.s3.amazonaws.com/",
                "fields": {"key": "test-file.jpg", "Content-Type": "image/jpeg"},
            }
            mock_s3_client.generate_presigned_post.return_value = mock_response

            s3_service = S3Service()
            result = s3_service.create_presigned_url("test-file.jpg", "image/jpeg")

            assert result == mock_response
            assert "url" in result
            assert "fields" in result


@pytest.mark.django_db
class TestSimplifiedIntegration(APITestCase):
    """단순화된 통합 테스트"""

    def setup_method(self):
        self.client = Client()

    def test_user_registration_and_login(self):
        """사용자 등록 및 로그인 플로우"""
        # 1. 사용자 등록
        register_data = {"email": "integration@test.com", "password": "Test123!", "nickname": "통합테스터", "bio": "통합 테스트"}

        response = self.client.post("/api/v1/user", data=json.dumps(register_data), content_type="application/json")

        assert response.status_code == 201

        # 2. 로그인
        login_data = {"email": "integration@test.com", "password": "Test123!"}

        response = self.client.post("/api/v1/auth/login", data=json.dumps(login_data), content_type="application/json")

        assert response.status_code == 200
        tokens = response.json()
        assert "access" in tokens
        assert "refresh" in tokens

    def test_error_handling_basic(self):
        """기본 에러 핸들링 테스트"""
        # 잘못된 엔드포인트
        response = self.client.get("/api/v1/nonexistent")
        assert response.status_code == 404

        # 인증 없이 보호된 리소스 접근
        response = self.client.post("/api/v1/meetup")
        assert response.status_code == 401
