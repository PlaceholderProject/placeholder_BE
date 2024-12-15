from enum import Enum
from abc import ABC


class StrEnum(Enum):
    @classmethod
    def get_values(cls):
        return [member.value for member in cls]


class APIStatus(StrEnum):
    SUCCESS = (200, "성공적으로 처리되었습니다.")
    BAD_REQUEST = (400, "잘못된 요청입니다.")
    EMAIL_ALREADY_EXISTS = (400, "이미 사용 중인 이메일입니다.")
    NICKNAME_ALREADY_EXISTS = (400, "이미 사용 중인 닉네임입니다.")
    UNAUTHORIZED = (401, "인증되지 않았습니다.")
    INVALID_CREDENTIALS = (401, "유효하지 않은 자격 증명입니다.")
    INVALID_TOKEN = (401, "유효하지 않은 토큰입니다.")
    FORBIDDEN = (403, "권한이 없습니다.")
    NOT_FOUND = (404, "리소스를 찾을 수 없습니다.")
    UNPROCESSABLE = (422, "유효하지 않은 요청입니다.")
    INTERNAL_SERVER_ERROR = (500, "서버 내부 오류가 발생했습니다.")

    def __init__(self, code, message):
        self.code = code
        self.message = message
        