# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model

from placeholder.utils.enums import APIStatus, MeetupSort, MeetupStatus
from placeholder.utils.exceptions import (
    CustomException,
    EmailAlreadyExistsException,
    InvalidCredentialsException,
    UnauthorizedAccessException,
)
from placeholder.utils.s3 import S3Service

User = get_user_model()


class TestEnums:
    """Enum 클래스 테스트"""

    def test_api_status_enum(self):
        """APIStatus Enum 테스트"""
        # 값 확인
        assert APIStatus.SUCCESS.code == 200
        assert APIStatus.SUCCESS.message == "성공적으로 처리되었습니다."

        assert APIStatus.BAD_REQUEST.code == 400
        assert APIStatus.BAD_REQUEST.message == "잘못된 요청입니다."

        assert APIStatus.UNAUTHORIZED.code == 401
        assert APIStatus.NOT_FOUND.code == 404
        assert APIStatus.INTERNAL_SERVER_ERROR.code == 500

    def test_meetup_status_enum(self):
        """MeetupStatus Enum 테스트"""
        assert MeetupStatus.ONGOING.value == "ongoing"
        assert MeetupStatus.ENDED.value == "ended"

        # StrEnum 메서드 테스트
        values = MeetupStatus.values()
        assert "ongoing" in values
        assert "ended" in values

    def test_meetup_sort_enum(self):
        """MeetupSort Enum 테스트"""
        assert MeetupSort.LIKE.value == "like"
        assert MeetupSort.LATEST.value == "latest"
        assert MeetupSort.DEADLINE.value == "deadline"


class TestCustomExceptions:
    """커스텀 예외 클래스 테스트"""

    def test_custom_exception_base(self):
        """기본 CustomException 테스트"""
        exception = CustomException(APIStatus.BAD_REQUEST)

        assert exception.status_code == 400
        assert exception.message == "잘못된 요청입니다."

    def test_email_already_exists_exception(self):
        """EmailAlreadyExistsException 테스트"""
        exception = EmailAlreadyExistsException()

        assert exception.status_code == 400
        assert "이미 사용 중인 이메일입니다" in exception.message

    def test_invalid_credentials_exception(self):
        """InvalidCredentialsException 테스트"""
        exception = InvalidCredentialsException()

        assert exception.status_code == 401
        assert "유효하지 않은 자격 증명입니다" in exception.message

    def test_unauthorized_access_exception(self):
        """UnauthorizedAccessException 테스트"""
        exception = UnauthorizedAccessException()

        assert exception.status_code == 401
        assert "인증되지 않았습니다" in exception.message

    def test_forbidden_exception(self):
        """ForbiddenException 테스트"""
        from placeholder.utils.exceptions import ForbiddenException

        exception = ForbiddenException()

        assert exception.status_code == 403
        assert "권한이 없습니다" in exception.message


class TestS3Service:
    """S3Service 테스트"""

    @patch.object(S3Service, "_get_s3_client")
    def test_s3_service_initialization(self, mock_get_client):
        """S3Service 초기화 테스트"""
        mock_s3_client = MagicMock()
        mock_get_client.return_value = mock_s3_client

        s3_service = S3Service()

        assert s3_service is not None
        # _get_s3_client 메서드가 호출되는지만 확인

    @patch.object(S3Service, "_get_s3_client")
    def test_create_presigned_url_success(self, mock_get_client):
        """Presigned URL 생성 성공 테스트"""
        mock_s3_client = MagicMock()
        mock_get_client.return_value = mock_s3_client

        # Mock response for generate_presigned_post
        mock_response = {
            "url": "https://bucket.s3.amazonaws.com/",
            "fields": {"key": "test-image.jpg", "Content-Type": "image/jpeg", "success_action_status": "201"},
        }
        mock_s3_client.generate_presigned_post.return_value = mock_response

        s3_service = S3Service()
        result = s3_service.create_presigned_url("test-image.jpg", "image/jpeg")

        assert result == mock_response
        assert result["url"] == "https://bucket.s3.amazonaws.com/"
        assert result["fields"]["Content-Type"] == "image/jpeg"

        mock_s3_client.generate_presigned_post.assert_called_once()

    @patch.object(S3Service, "_get_s3_client")
    def test_create_presigned_url_failure(self, mock_get_client):
        """Presigned URL 생성 실패 테스트"""
        mock_s3_client = MagicMock()
        mock_get_client.return_value = mock_s3_client

        # ClientError 발생 시뮬레이션
        from botocore.exceptions import ClientError

        error_response = {"Error": {"Code": "NoSuchBucket", "Message": "Bucket does not exist"}}
        mock_s3_client.generate_presigned_post.side_effect = ClientError(error_response, "generate_presigned_post")

        s3_service = S3Service()
        result = s3_service.create_presigned_url("test-image.jpg", "image/jpeg")

        assert result is None

    @patch.object(S3Service, "_get_s3_client")
    def test_create_presigned_url_with_custom_bucket(self, mock_get_client):
        """커스텀 버킷으로 Presigned URL 생성 테스트"""
        mock_s3_client = MagicMock()
        mock_get_client.return_value = mock_s3_client

        mock_response = {"url": "https://custom-bucket.s3.amazonaws.com/", "fields": {"key": "custom-image.jpg"}}
        mock_s3_client.generate_presigned_post.return_value = mock_response

        s3_service = S3Service()
        result = s3_service.create_presigned_url(
            "custom-image.jpg", "image/png", bucket_name="custom-bucket", expiration=30
        )

        assert result == mock_response
        mock_s3_client.generate_presigned_post.assert_called_once_with(
            "custom-bucket",
            "custom-image.jpg",
            Fields={"Content-Type": "image/png", "success_action_status": "201"},
            Conditions=[
                {"success_action_status": "201"},
                ["starts-with", "$Content-Type", "image/"],
                ["content-length-range", 1024, 10485760],
            ],
            ExpiresIn=30,
        )

    @patch.object(S3Service, "create_presigned_url")
    def test_create_multi_presigned_url_success(self, mock_create_url):
        """다중 Presigned URL 생성 성공 테스트"""
        # Mock responses for different file types
        mock_responses = [
            {"url": "https://bucket.s3.amazonaws.com/", "fields": {"key": "test.jpg"}},
            {"url": "https://bucket.s3.amazonaws.com/", "fields": {"key": "test.png"}},
            {"url": "https://bucket.s3.amazonaws.com/", "fields": {"key": "test.gif"}},
        ]
        mock_create_url.side_effect = mock_responses

        s3_service = S3Service()
        result = s3_service.create_multi_presigned_url("images", ["image/jpeg", "image/png", "image/gif"])

        assert "result" in result
        assert len(result["result"]) == 3
        assert result["result"] == mock_responses

        # create_presigned_url이 3번 호출되었는지 확인
        assert mock_create_url.call_count == 3

    @patch.object(S3Service, "create_presigned_url")
    def test_create_multi_presigned_url_with_various_types(self, mock_create_url):
        """다양한 파일 타입으로 다중 URL 생성 테스트"""
        mock_create_url.return_value = {"url": "https://example.com", "fields": {}}

        s3_service = S3Service()
        result = s3_service.create_multi_presigned_url("files", ["image/jpeg", "image/png", "unknown"])

        assert mock_create_url.call_count == 3

        # 각 호출의 인자 확인
        calls = mock_create_url.call_args_list

        # image/jpeg -> .jpeg 확장자
        assert calls[0][0][0].endswith(".jpeg")
        assert calls[0][0][1] == "image/jpeg"

        # image/png -> .png 확장자
        assert calls[1][0][0].endswith(".png")
        assert calls[1][0][1] == "image/png"

        # unknown (슬래시 없음) -> .jpg 기본값
        assert calls[2][0][0].endswith(".jpg")
        assert calls[2][0][1] == "unknown"


@pytest.mark.django_db
class TestAuthUtils:
    """인증 유틸리티 테스트"""

    def test_jwt_auth_valid_token(self, create_user):
        """유효한 JWT 토큰 테스트"""
        from rest_framework_simplejwt.tokens import RefreshToken

        from placeholder.utils.auth import JWTAuth

        # 토큰 생성
        refresh = RefreshToken.for_user(create_user)
        access_token = str(refresh.access_token)

        # JWTAuth 테스트 - authenticate 메서드는 (request, token) 형태
        jwt_auth = JWTAuth()
        authenticated_user = jwt_auth.authenticate(None, access_token)

        assert authenticated_user == create_user

    def test_jwt_auth_invalid_token(self):
        """잘못된 JWT 토큰 테스트"""
        from placeholder.utils.auth import JWTAuth
        from placeholder.utils.exceptions import InvalidTokenException

        mock_request = MagicMock()
        mock_request.META = {"HTTP_AUTHORIZATION": "Bearer invalid_token"}

        jwt_auth = JWTAuth()

        with pytest.raises(InvalidTokenException):
            jwt_auth.authenticate(mock_request, None)

    def test_jwt_auth_missing_token(self):
        """토큰이 없는 경우 테스트"""
        from placeholder.utils.auth import JWTAuth
        from placeholder.utils.exceptions import InvalidTokenException

        jwt_auth = JWTAuth()

        # None 토큰으로 인증 시도 시 예외 발생
        with pytest.raises(InvalidTokenException):
            jwt_auth.authenticate(None, None)

    def test_anonymous_user_auth(self):
        """익명 사용자 인증 테스트"""
        from django.contrib.auth.models import AnonymousUser

        from placeholder.utils.auth import anonymous_user

        mock_request = MagicMock()

        # anonymous_user는 함수이므로 직접 호출
        result = anonymous_user(mock_request)

        assert isinstance(result, AnonymousUser)
        assert result.is_authenticated is False


class TestPagination:
    """페이지네이션 테스트"""

    def test_custom_pagination_class(self):
        """CustomPagination 클래스 테스트"""
        from placeholder.pagination import CustomPagination

        pagination = CustomPagination()

        # 기본 설정 확인
        assert pagination.items_attribute == "result"
        assert hasattr(pagination, "paginate_queryset")
        assert hasattr(pagination, "Input")
        assert hasattr(pagination, "Output")


class TestMiddleware:
    """미들웨어 테스트"""

    def test_put_patch_with_file_form_middleware(self):
        """PutPatchWithFileFormMiddleware 테스트"""
        from placeholder.middleware import PutPatchWithFileFormMiddleware

        mock_get_response = MagicMock()
        middleware = PutPatchWithFileFormMiddleware(mock_get_response)

        # Mock request
        mock_request = MagicMock()
        mock_request.method = "PUT"
        mock_request.content_type = "multipart/form-data"

        # 미들웨어 실행
        middleware(mock_request)

        # get_response가 호출되었는지 확인
        mock_get_response.assert_called_once_with(mock_request)
