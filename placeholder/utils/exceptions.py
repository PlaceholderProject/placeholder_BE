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
