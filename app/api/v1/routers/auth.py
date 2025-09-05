from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.models.owner import Owner
from app.schemas.user import UserCreate, UserLogin, UserOut, Token

router = APIRouter()


@router.post("/test")
def test_endpoint():
    """テスト用エンドポイント - データベースを使用しない"""
    return {"message": "Test endpoint working"}


@router.post("/test-login")
def test_login_endpoint(user_login: UserLogin):
    """テスト用ログインエンドポイント - データベースを使用しない"""
    return {
        "message": "Login endpoint working", 
        "email": user_login.email,
        "password_received": bool(user_login.password)
    }


@router.post("/register", response_model=UserOut)
def register_user(user_create: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        name=user_create.name,
        email=user_create.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create associated owner
    db_owner = Owner(
        name=user_create.name,
        email=user_create.email,
        user_id=db_user.id
    )
    db.add(db_owner)
    db.commit()
    
    return db_user


@router.post("/login", response_model=Token)
def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_login.email).first()
    
    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if hashed_password exists and is not empty
    if not user.hashed_password or not user.hashed_password.strip():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account configuration error. Please contact administrator."
        )
    
    # Verify password
    if not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user