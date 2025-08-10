# -*- coding: utf-8 -*-
from io import BytesIO
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from django.core.management.base import BaseCommand, CommandError

from meetup.models import Meetup
from placeholder.utils.s3 import S3Service


class Command(BaseCommand):
    help = "공개된 모임들의 sitemap을 생성하고 S3에 업로드합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--base-url",
            type=str,
            default="https://www.place-holder.site",
            help="사이트의 기본 URL (기본값: https://www.place-holder.site)",
        )
        parser.add_argument("--bucket-name", type=str, default=None, help="S3 버킷 이름 (설정되지 않은 경우 기본값 사용)")
        parser.add_argument("--dry-run", action="store_true", help="실제 업로드 없이 sitemap만 생성하여 출력")

    def handle(self, *args, **options):
        base_url = options["base_url"].rstrip("/")
        bucket_name = options["bucket_name"]
        dry_run = options["dry_run"]

        try:
            # Sitemap XML 생성
            sitemap_xml = self.generate_sitemap(base_url)

            if dry_run:
                self.stdout.write("Generated sitemap:")
                self.stdout.write(sitemap_xml)
                return

            # S3에 업로드
            self.upload_to_s3(sitemap_xml, bucket_name)

            self.stdout.write(self.style.SUCCESS("Successfully generated and uploaded sitemap to S3"))

        except Exception as e:
            raise CommandError(f"Error generating or uploading sitemap: {str(e)}")

    def generate_sitemap(self, base_url):
        """Sitemap XML을 생성합니다."""
        self.stdout.write("Generating sitemap...")

        # Root element 생성
        urlset = Element("urlset")
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

        # 홈페이지 추가
        self.add_url(urlset, base_url, priority="1.0", changefreq="daily")

        # 공개된 모임들 추가
        public_meetups = Meetup.objects.filter(is_public=True).select_related("organizer")

        self.stdout.write(f"Found {public_meetups.count()} public meetups")

        for meetup in public_meetups:
            meetup_url = f"{base_url}/ad/{meetup.id}"

            # 모임의 마지막 수정 날짜 (updated_at이 있다면)
            lastmod = None
            if hasattr(meetup, "updated_at") and meetup.updated_at:
                lastmod = meetup.updated_at.isoformat()
            elif hasattr(meetup, "created_at") and meetup.created_at:
                lastmod = meetup.created_at.isoformat()

            self.add_url(urlset, meetup_url, lastmod=lastmod, priority="0.8", changefreq="weekly")

        # XML을 예쁘게 포맷팅
        rough_string = tostring(urlset, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")

        # XML 선언부 정리 (minidom이 추가하는 불필요한 빈 줄 제거)
        lines = pretty_xml.split("\n")
        # 첫 번째 빈 줄 제거
        if len(lines) > 1 and lines[1].strip() == "":
            lines.pop(1)

        return "\n".join(lines)

    def add_url(self, urlset, url, lastmod=None, priority=None, changefreq=None):
        """URL element를 sitemap에 추가합니다."""
        url_elem = SubElement(urlset, "url")

        loc = SubElement(url_elem, "loc")
        loc.text = url

        if lastmod:
            lastmod_elem = SubElement(url_elem, "lastmod")
            lastmod_elem.text = lastmod

        if changefreq:
            changefreq_elem = SubElement(url_elem, "changefreq")
            changefreq_elem.text = changefreq

        if priority:
            priority_elem = SubElement(url_elem, "priority")
            priority_elem.text = priority

    def upload_to_s3(self, sitemap_xml, bucket_name=None):
        """생성된 sitemap을 S3에 업로드합니다."""
        self.stdout.write("Uploading sitemap to S3...")

        try:
            s3_service = S3Service(bucket_name=bucket_name)

            # XML 문자열을 bytes로 변환
            sitemap_bytes = sitemap_xml.encode("utf-8")

            # BytesIO 객체 생성
            sitemap_file = BytesIO(sitemap_bytes)

            # S3에 업로드 (sitemap.xml로 저장)
            success = s3_service.upload_file(file=sitemap_file, key="sitemap.xml", content_type="application/xml")

            if not success:
                raise Exception("S3 upload returned False")

            self.stdout.write("Sitemap uploaded successfully to S3")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to upload sitemap to S3: {str(e)}"))
            raise
