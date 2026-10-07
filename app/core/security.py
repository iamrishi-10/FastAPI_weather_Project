import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from pwdlib import PasswordHash



ph = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return ph.verify(password, hashed_password)



def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expires_in = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expires_in})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


if __name__ == '__main__':
    password = "mypassword123"
    hashed = hash_password(password)
    print("Hashed password:", hashed)
    print("Verify correct password:", verify_password(password, hashed))
    print("Verify wrong password:", verify_password("wrongpassword", hashed))

    token = create_access_token({"sub": "42"})
    print("Access token:", token)

    payload = verify_access_token(token)
    print("Decoded payload:", payload)

    tampered_payload = verify_access_token(token + "tampered")
    print("Tampered token payload:", tampered_payload)

