""""dependencies" module"""

import os
from datetime import timedelta, datetime
from typing import Union
from fastapi import HTTPException, status
from jose import JWTError, ExpiredSignatureError, jwt


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """Create JWT token when a user login or register.
    """

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=10)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode,
                             os.getenv("JWT_SECRET_KEY"),
                             algorithm=os.getenv("JWT_ALGORITHM"))
    return encoded_jwt


async def validate_token(token: str):
    """Validate JWT token and refresh expired time.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token,
                             os.getenv("JWT_SECRET_KEY"),
                             algorithms=os.getenv("JWT_ALGORITHM"))
        uid: str = payload.get("uid")
        if uid is None:
            raise credentials_exception
    except ExpiredSignatureError as exc:
        raise HTTPException(status_code=403, detail="Token has been expired.") from exc
    except JWTError as exc:
        raise credentials_exception from exc
    return uid
