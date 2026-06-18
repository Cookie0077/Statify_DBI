from datetime import timedelta, datetime

import jwt
from fastapi import Security, HTTPException, Depends
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sqlalchemy.orm import Session

import models
from helper import verify_password

api_key_header = APIKeyHeader(name='A-API-Key', auto_error=False)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "7d842b41094112c03c492b17f915ee87cf851cab5c7174db255ca87a0dfe2f68"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != "STATIKEY":
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key


def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.DBUser).filter(models.DBUser.Name == username).first()
    if not user:
        return False
    if not verify_password(password, user.Password):
        return False
    return user


def get_User_id(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    userID: str = payload.get("sub")
    if userID is None:
        raise HTTPException(status_code=401, detail="Not authorized")

    return userID
