from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from ...database import get_db
from ...crud import user as crud_user
from ...schemas.user import UserCreate, User
from ...schemas.token import Token
from ...core.security import create_access_token, create_refresh_token

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    # Check if user exists
    user = await crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    user = await crud_user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )
    
    # Create new user
    user = await crud_user.create(db, obj_in=user_in)
    return user


@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Login and get access token"""
    user = await crud_user.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not crud_user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
