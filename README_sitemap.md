# Sitemap Generation and S3 Upload

이 프로젝트는 공개된 모임들을 포함한 sitemap을 자동으로 생성하고 S3에 업로드하는 Django management command를 제공합니다.

## 기능

- 홈페이지 URL (`https://www.place-holder.site/`) 자동 포함
- 공개된 모임들의 상세 페이지 URL (`https://www.place-holder.site/ad/{meetup_id}`) 자동 포함
- XML Sitemap 표준 준수
- S3에 자동 업로드
- Crontab을 통한 자동화 지원

## Command 사용법

### 기본 사용법

```bash
python manage.py generate_sitemap
```

### 옵션

- `--base-url`: 사이트의 기본 URL (기본값: `https://www.place-holder.site`)
- `--bucket-name`: S3 버킷 이름 (설정되지 않은 경우 `AWS_S3_MEDIA_BUCKET_NAME` 사용)
- `--dry-run`: 실제 업로드 없이 sitemap만 생성하여 출력

### 예시

```bash
# Dry run - sitemap만 생성하여 출력
python manage.py generate_sitemap --dry-run

# 커스텀 기본 URL 사용
python manage.py generate_sitemap --base-url https://my-domain.com

# 커스텀 S3 버킷 사용
python manage.py generate_sitemap --bucket-name my-custom-bucket
```

## 자동화 설정 (Crontab)

매일 밤 2시에 sitemap을 업데이트하려면 다음과 같이 crontab을 설정하세요:

```bash
# crontab 편집
crontab -e

# 다음 줄을 추가 (프로젝트 경로를 실제 경로로 변경)
0 2 * * * /path/to/placeholder/scripts/generate_sitemap.sh >> /path/to/placeholder/logs/cron.log 2>&1
```

### Crontab 설정 예시

```bash
# 매일 오전 2시에 실행
0 2 * * * /home/ubuntu/placeholder/scripts/generate_sitemap.sh

# 매 6시간마다 실행
0 */6 * * * /home/ubuntu/placeholder/scripts/generate_sitemap.sh

# 주중 매일 오전 1시에 실행
0 1 * * 1-5 /home/ubuntu/placeholder/scripts/generate_sitemap.sh
```

## 생성되는 Sitemap 구조

```xml
<?xml version="1.0" ?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.place-holder.site</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://www.place-holder.site/ad/123</loc>
    <lastmod>2025-08-09T12:34:56.789+00:00</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <!-- 더 많은 모임 URLs -->
</urlset>
```

## URL 우선순위

- **홈페이지**: `priority="1.0"`, `changefreq="daily"`
- **모임 상세 페이지**: `priority="0.8"`, `changefreq="weekly"`

## 로깅

스크립트 실행 결과는 `logs/sitemap.log` 파일에 기록됩니다:

```
Sat Aug  9 21:29:45 KST 2025: Sitemap generation and upload completed successfully
```

## 에러 처리

- 데이터베이스 연결 실패 시 에러 메시지 출력
- S3 업로드 실패 시 에러 메시지 출력
- 모든 에러는 Django logging 시스템을 통해 기록

## 의존성

- Django
- boto3 (S3 업로드)
- PostgreSQL (데이터베이스)

## 파일 구조

```
placeholder/
├── meetup/
│   └── management/
│       └── commands/
│           └── generate_sitemap.py    # Django management command
├── scripts/
│   └── generate_sitemap.sh           # Crontab 실행 스크립트
├── logs/
│   ├── sitemap.log                   # Sitemap 생성 로그
│   └── cron.log                      # Crontab 실행 로그
└── placeholder/
    └── utils/
        └── s3.py                     # S3Service (업로드 기능 포함)
```

## 주의사항

1. S3 버킷에 쓰기 권한이 있어야 합니다
2. AWS 인증 정보가 올바르게 설정되어야 합니다
3. `is_public=True`인 모임만 sitemap에 포함됩니다
4. 생성된 sitemap은 S3의 루트에 `sitemap.xml`로 저장됩니다
