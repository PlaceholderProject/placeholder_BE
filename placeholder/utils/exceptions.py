# -*- coding: utf-8 -*-
from ninja.errors import HttpError

from placeholder.utils.enums import APIStatus


class CustomException(HttpError):
    def __init__(self, status: APIStatus):
        super().__init__(status.code, status.message)


class EmailAlreadyExistsException(CustomException):
    def __init__(self):
        super().__init__(APIStatus.EMAIL_ALREADY_EXISTS)


class NicknameAlreadyExistsException(CustomException):
    def __init__(self):
        super().__init__(APIStatus.NICKNAME_ALREADY_EXISTS)


class InvalidCredentialsException(CustomException):
    def __init__(self):
        super().__init__(APIStatus.INVALID_CREDENTIALS)


class InvalidTokenException(CustomException):
    def __init__(self):
        super().__init__(APIStatus.INVALID_TOKEN)


class UnauthorizedAccessException(CustomException):
    def __init__(self):
        super().__init__(APIStatus.UNAUTHORIZED)


class ForbiddenException(CustomException):
    def __init__(self):
        super().__init__(APIStatus.FORBIDDEN)


class NotFoundException(CustomException):
    def __init__(self, message=None):
        # APIStatus.NOT_FOUND를 사용하되 메시지만 오버라이드
        status = APIStatus.NOT_FOUND
        if message:
            # 메시지만 교체
            self.status_code = status.code
            self.message = message
            super(HttpError, self).__init__(status.code, message)
        else:
            super().__init__(status)
