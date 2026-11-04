from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, UserResponse

def register_user(data: RegisterRequest, db: Session) -> AuthResponse:
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists"
        )
        
    user = User(
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_access_token(user.id, user.email)
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

def login_user(data: LoginRequest, db: Session) -> AuthResponse:
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    token = create_access_token(user.id, user.email)
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )
