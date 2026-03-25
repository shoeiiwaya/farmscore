"""
Auth API — ユーザー登録・ログイン・APIキー管理
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import (
    hash_password, verify_password, create_access_token,
    generate_api_key, get_current_user,
)
from app.db.database import get_db
from app.db.models import User, ApiKey
from app.schemas.auth import UserCreate, UserResponse, TokenResponse, LoginRequest, ApiKeyResponse

router = APIRouter()


@router.post("/signup", response_model=TokenResponse, tags=["auth"])
def signup(req: UserCreate, db: Session = Depends(get_db)):
    """新規ユーザー登録"""
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="このメールアドレスは既に登録されています")

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        name=req.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse, tags=["auth"])
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """ログイン"""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="メールアドレスまたはパスワードが間違っています")

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse, tags=["auth"])
def get_me(user: User = Depends(get_current_user)):
    """現在のユーザー情報"""
    return user


@router.post("/api-keys", response_model=ApiKeyResponse, tags=["auth"])
def create_api_key(
    name: str = "default",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """APIキーを発行"""
    full_key, prefix, key_hash = generate_api_key()

    api_key = ApiKey(
        key_hash=key_hash,
        prefix=prefix,
        user_id=user.id,
        name=name,
    )
    db.add(api_key)
    db.commit()

    return ApiKeyResponse(key=full_key, prefix=prefix, name=name)
