class BizError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


PARAM_ERROR = 40001
JSON_ERROR = 40002
RULE_VALIDATE_ERROR = 40003
NOT_FOUND = 40401
CONFLICT = 40901
UNAUTHORIZED = 40101
FORBIDDEN = 40301
SYSTEM_ERROR = 50001
AI_ERROR = 50002
