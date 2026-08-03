from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, get_current_user
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    generate_telegram_link_code
)
from app.models.user import User
from app.models.settings import UserSettings
from app.models.category import Category
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, TelegramLinkRequest

router = APIRouter()

# Default System Categories to seed for every new user
DEFAULT_CATEGORIES = [
    {"name": "Food", "icon": "utensils", "color": "#ef4444"},
    {"name": "Transport", "icon": "car", "color": "#f59e0b"},
    {"name": "Shopping", "icon": "shopping-bag", "color": "#10b981"},
    {"name": "Subscriptions", "icon": "tv", "color": "#6366f1"},
    {"name": "Entertainment", "icon": "film", "color": "#8b5cf6"},
    {"name": "Bills", "icon": "file-text", "color": "#ec4899"},
    {"name": "Utilities", "icon": "wrench", "color": "#06b6d4"},
    {"name": "Healthcare", "icon": "activity", "color": "#14b8a6"},
    {"name": "Education", "icon": "book", "color": "#3b82f6"},
    {"name": "Rent", "icon": "home", "color": "#a855f7"},
    {"name": "Travel", "icon": "plane", "color": "#f97316"},
    {"name": "Investment", "icon": "trending-up", "color": "#22c55e"},
    {"name": "Salary", "icon": "dollar-sign", "color": "#84cc16"},
    {"name": "Miscellaneous", "icon": "tag", "color": "#64748b"}
]

@router.post("/register", response_model=Token, status_code=status.HTTP_211_CREATED if hasattr(status, "HTTP_211_CREATED") else 201)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists in the system."
        )

    # Create new user
    user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        currency=user_in.currency,
        timezone=user_in.timezone
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create default user settings
    user_settings = UserSettings(user_id=user.id, preferred_currency=user.currency)
    db.add(user_settings)

    # Create default categories for user
    for cat in DEFAULT_CATEGORIES:
        c = Category(
            user_id=user.id,
            name=cat["name"],
            icon=cat["icon"],
            color=cat["color"],
            is_system=True
        )
        db.add(c)

    db.commit()

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login", response_model=Token)
def login(login_in: UserLogin, db: Session = Depends(get_db)) -> Any:
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> Any:
    return current_user

@router.post("/generate-telegram-code")
def generate_telegram_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    code = generate_telegram_link_code()
    current_user.telegram_link_code = code
    current_user.telegram_link_code_expires = datetime.utcnow() + timedelta(minutes=15)
    db.commit()
    return {"link_code": code, "expires_in_minutes": 15}
