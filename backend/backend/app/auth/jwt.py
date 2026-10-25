from datetime import datetime, timedelta

SECRET_KEY = 'change-me'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(email: str) -> str:
    expiry = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return f'{email}:{int(expiry.timestamp())}'
