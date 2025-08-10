# -*- coding: utf-8 -*-
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from meetup.models import Meetup
from placeholder.utils.s3 import S3Service


@pytest.mark.django_db
class TestGenerateSitemapCommand:
    """Sitemap 생성 command 테스트"""

    def test_dry_run_generates_sitemap(self, create_organizer):
        """Dry run 모드에서 sitemap이 올바르게 생성되는지 테스트"""
        # 공개 모임 생성
        meetup = Meetup.objects.create(
            name="테스트 모임",
            description="테스트 모임입니다",
            place="서울",
            place_description="강남",
            ad_title="테스트 광고",
            ad_ended_at="2025-12-31",
            is_public=True,
            organizer=create_organizer,
        )

        out = StringIO()
        call_command("generate_sitemap", "--dry-run", stdout=out)

        output = out.getvalue()

        # 출력에 필요한 내용들이 포함되어 있는지 확인
        assert "Generating sitemap..." in output
        assert "Generated sitemap:" in output
        assert "https://www.place-holder.site" in output
        assert f"https://www.place-holder.site/ad/{meetup.id}" in output
        assert '<?xml version="1.0" ?>' in output
        assert 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"' in output

    def test_custom_base_url(self, create_organizer):
        """커스텀 base URL이 올바르게 적용되는지 테스트"""
        custom_url = "https://custom-domain.com"

        # 공개 모임 생성
        meetup = Meetup.objects.create(
            name="테스트 모임",
            description="테스트 모임입니다",
            place="서울",
            place_description="강남",
            ad_title="테스트 광고",
            ad_ended_at="2025-12-31",
            is_public=True,
            organizer=create_organizer,
        )

        out = StringIO()
        call_command("generate_sitemap", "--dry-run", f"--base-url={custom_url}", stdout=out)

        output = out.getvalue()

        # 커스텀 URL이 사용되는지 확인
        assert custom_url in output
        assert f"{custom_url}/ad/{meetup.id}" in output

    def test_only_public_meetups_included(self, create_organizer):
        """공개 모임만 sitemap에 포함되는지 테스트"""
        # 공개 모임
        public_meetup = Meetup.objects.create(
            name="공개 모임",
            description="공개 모임입니다",
            place="서울",
            place_description="강남",
            ad_title="공개 광고",
            ad_ended_at="2025-12-31",
            is_public=True,
            organizer=create_organizer,
        )

        # 비공개 모임
        private_meetup = Meetup.objects.create(
            name="비공개 모임",
            description="비공개 모임입니다",
            place="서울",
            place_description="강남",
            ad_title="비공개 광고",
            ad_ended_at="2025-12-31",
            is_public=False,
            organizer=create_organizer,
        )

        out = StringIO()
        call_command("generate_sitemap", "--dry-run", stdout=out)

        output = out.getvalue()

        # 공개 모임만 포함되는지 확인
        assert f"https://www.place-holder.site/ad/{public_meetup.id}" in output
        assert f"https://www.place-holder.site/ad/{private_meetup.id}" not in output

    @patch.object(S3Service, "upload_file")
    def test_s3_upload_success(self, mock_upload, create_organizer):
        """S3 업로드가 성공적으로 호출되는지 테스트"""
        mock_upload.return_value = True

        # 공개 모임 생성
        Meetup.objects.create(
            name="테스트 모임",
            description="테스트 모임입니다",
            place="서울",
            place_description="강남",
            ad_title="테스트 광고",
            ad_ended_at="2025-12-31",
            is_public=True,
            organizer=create_organizer,
        )

        out = StringIO()
        call_command("generate_sitemap", stdout=out)

        output = out.getvalue()

        # S3 업로드 관련 메시지 확인
        assert "Uploading sitemap to S3..." in output
        assert "Successfully generated and uploaded sitemap to S3" in output

        # upload_file이 올바른 파라미터로 호출되었는지 확인
        mock_upload.assert_called_once()
        call_args = mock_upload.call_args
        assert call_args[1]["key"] == "sitemap.xml"
        assert call_args[1]["content_type"] == "application/xml"

    @patch.object(S3Service, "upload_file")
    def test_s3_upload_failure(self, mock_upload, create_organizer):
        """S3 업로드 실패 시 에러 처리 테스트"""
        mock_upload.return_value = False

        # 공개 모임 생성
        Meetup.objects.create(
            name="테스트 모임",
            description="테스트 모임입니다",
            place="서울",
            place_description="강남",
            ad_title="테스트 광고",
            ad_ended_at="2025-12-31",
            is_public=True,
            organizer=create_organizer,
        )

        out = StringIO()
        err = StringIO()

        with pytest.raises(CommandError):
            call_command("generate_sitemap", stdout=out, stderr=err)

    def test_no_meetups(self):
        """모임이 없을 때도 정상 작동하는지 테스트"""
        out = StringIO()
        call_command("generate_sitemap", "--dry-run", stdout=out)

        output = out.getvalue()

        # 홈페이지 URL은 항상 포함되어야 함
        assert "https://www.place-holder.site" in output
        assert "Found 0 public meetups" in output

    def test_sitemap_xml_structure(self, create_organizer):
        """생성된 XML이 sitemap 표준에 맞는지 테스트"""
        # 공개 모임 생성
        meetup = Meetup.objects.create(
            name="XML 테스트 모임",
            description="XML 구조 테스트",
            place="서울",
            place_description="강남",
            ad_title="XML 테스트",
            ad_ended_at="2025-12-31",
            is_public=True,
            organizer=create_organizer,
        )

        out = StringIO()
        call_command("generate_sitemap", "--dry-run", stdout=out)

        output = out.getvalue()

        # XML 구조 확인
        assert '<?xml version="1.0" ?>' in output
        assert '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' in output
        assert "<url>" in output
        assert "<loc>" in output
        assert "<priority>" in output
        assert "<changefreq>" in output
        assert "</urlset>" in output

        # 홈페이지 우선순위 확인
        homepage_section = output[output.find("<loc>https://www.place-holder.site</loc>") :]
        next_url = homepage_section.find("<url>")
        homepage_priority = homepage_section[: next_url if next_url > 0 else len(homepage_section)]
        assert "<priority>1.0</priority>" in homepage_priority
        assert "<changefreq>daily</changefreq>" in homepage_priority
