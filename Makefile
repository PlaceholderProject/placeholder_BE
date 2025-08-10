# Makefile for Django project

# 기본 Python 명령어
PYTHON := python
PIP := pip
PYTEST := pytest

# Django 관리 명령어
MANAGE := $(PYTHON) manage.py

# 테스트 설정
TEST_PATH := tests/
PYTEST_ARGS := -v --tb=short

.PHONY: help install test test-coverage test-unit test-integration lint format check migrate run clean

# 기본 도움말
help:
	@echo "Available commands:"
	@echo "  install          - Install dependencies"
	@echo "  test             - Run all tests"
	@echo "  test-coverage    - Run tests with coverage report"
	@echo "  test-unit        - Run only unit tests"
	@echo "  test-integration - Run only integration tests"
	@echo "  lint             - Run linting (flake8)"
	@echo "  format           - Format code (black + isort)"
	@echo "  check            - Run all checks (lint + test)"
	@echo "  migrate          - Run database migrations"
	@echo "  run              - Start development server"
	@echo "  clean            - Clean up temporary files"

# 의존성 설치
install:
	$(PIP) install -r requirements.txt
	@echo "Dependencies installed successfully!"

# Poetry를 사용하는 경우
install-poetry:
	poetry install
	@echo "Dependencies installed with Poetry!"

# 모든 테스트 실행
test:
	$(PYTEST) $(TEST_PATH) $(PYTEST_ARGS)

# 커버리지 포함 테스트 실행
test-coverage:
	$(PYTEST) $(TEST_PATH) $(PYTEST_ARGS) --cov=. --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/"

# 단위 테스트만 실행
test-unit:
	$(PYTEST) $(TEST_PATH) -k "not test_integration" $(PYTEST_ARGS)

# 통합 테스트만 실행
test-integration:
	$(PYTEST) $(TEST_PATH) -k "test_integration" $(PYTEST_ARGS)

# 특정 테스트 파일 실행
test-user:
	$(PYTEST) tests/user/ $(PYTEST_ARGS)

test-meetup:
	$(PYTEST) tests/meetup/ $(PYTEST_ARGS)

test-models:
	$(PYTEST) tests/*/test_models.py $(PYTEST_ARGS)

test-apis:
	$(PYTEST) tests/*/test_*.py -k "API" $(PYTEST_ARGS)

# 린팅
lint:
	flake8 .
	@echo "Linting completed!"

# 코드 포맷팅
format:
	black .
	isort .
	@echo "Code formatting completed!"

# 모든 체크 실행
check: lint test
	@echo "All checks completed successfully!"

# 데이터베이스 마이그레이션
migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

# 개발 서버 실행
run:
	$(MANAGE) runserver

# 슈퍼유저 생성
createsuperuser:
	$(MANAGE) createsuperuser

# 테스트 데이터베이스 생성 및 마이그레이션
test-setup:
	$(MANAGE) migrate --settings=placeholder.settings.local
	@echo "Test database setup completed!"

# 임시 파일 정리
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	@echo "Cleanup completed!"

# 개발 환경 완전 설정
setup-dev: install migrate createsuperuser
	@echo "Development environment setup completed!"

# CI/CD용 명령어
ci-test: lint test-coverage
	@echo "CI tests completed!"

# 특정 앱의 테스트만 실행
test-app-%:
	$(PYTEST) tests/$*/ $(PYTEST_ARGS)

# 주요 테스트만 실행 (빠른 확인)
test-core:
	$(PYTEST) tests/user/ tests/meetup/test_models.py tests/test_utils.py::TestS3Service tests/test_fixed.py $(PYTEST_ARGS)

# 실패한 테스트만 재실행
test-failed:
	$(PYTEST) --lf $(PYTEST_ARGS)

# 테스트 데이터베이스 리셋
test-db-reset:
	$(MANAGE) flush --noinput --settings=placeholder.settings.local
	$(MANAGE) migrate --settings=placeholder.settings.local
