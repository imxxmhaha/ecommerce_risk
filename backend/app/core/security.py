import base64
import binascii
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone

from app.core.config import get_settings
from app.core.errors import BizError, UNAUTHORIZED


def verify_password(plain_password: str, password_hash: str) -> bool:
    parts = password_hash.split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        return False
    _, iterations, salt, expected_hex = parts
    try:
        digest = hashlib.pbkdf2_hmac("sha256", plain_password.encode(), salt.encode(), int(iterations))
        return hmac.compare_digest(binascii.hexlify(digest).decode(), expected_hex)
    except ValueError:
        return False


def hash_password(plain_password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(12)
    iterations = 100000
    digest = hashlib.pbkdf2_hmac("sha256", plain_password.encode(), salt.encode(), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${binascii.hexlify(digest).decode()}"


def _encode_json(data: dict) -> str:
    raw = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _decode_json(data: str) -> dict:
    padding = "=" * (-len(data) % 4)
    return json.loads(base64.urlsafe_b64decode((data + padding).encode()).decode())


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"uid": user_id, "exp": int(expire_at.timestamp()), "nonce": secrets.token_hex(8)}
    body = _encode_json(payload)
    signature = hmac.new(settings.auth_secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{signature}"


def verify_access_token(token: str) -> int:
    settings = get_settings()
    try:
        body, signature = token.split(".", 1)
        expected = hmac.new(settings.auth_secret.encode(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise BizError(UNAUTHORIZED, "invalid token")
        payload = _decode_json(body)
        if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
            raise BizError(UNAUTHORIZED, "token expired")
        return int(payload["uid"])
    except BizError:
        raise
    except Exception as exc:
        raise BizError(UNAUTHORIZED, "invalid token") from exc
