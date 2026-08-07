from __future__ import annotations
import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta
from typing import Any

SECRET_KEY = os.getenv('SECRET_KEY', 'replace-this-secret')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def _urlsafe_b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def _urlsafe_b64decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)

def _sign(message: bytes) -> str:
    signature = hmac.new(SECRET_KEY.encode('utf-8'), message, hashlib.sha256).digest()
    return _urlsafe_b64encode(signature)

def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expires_delta = expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {'sub': subject, 'exp': int((datetime.utcnow() + expires_delta).timestamp())}
    header = {'alg': ALGORITHM, 'typ': 'JWT'}
    encoded_header = _urlsafe_b64encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    encoded_payload = _urlsafe_b64encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
    signature = _sign(f'{encoded_header}.{encoded_payload}'.encode('utf-8'))
    return f'{encoded_header}.{encoded_payload}.{signature}'

def verify_access_token(token: str) -> dict[str, Any]:
    try:
        encoded_header, encoded_payload, signature = token.split('.')
        expected = _sign(f'{encoded_header}.{encoded_payload}'.encode('utf-8'))
        if not hmac.compare_digest(expected, signature):
            raise ValueError('Invalid token signature')
        payload = json.loads(_urlsafe_b64decode(encoded_payload).decode('utf-8'))
        if int(payload.get('exp', 0)) < int(datetime.utcnow().timestamp()):
            raise ValueError('Token has expired')
        return payload
    except (ValueError, json.JSONDecodeError):
        raise ValueError('Invalid token')

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f'{_urlsafe_b64encode(salt)}${_urlsafe_b64encode(hashed)}'

def verify_password(password: str, hashed_password: str) -> bool:
    try:
        salt, expected = hashed_password.split('$', 1)
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), _urlsafe_b64decode(salt), 100000)
        return hmac.compare_digest(_urlsafe_b64encode(hashed), expected)
    except ValueError:
        return False
