from typing import List

from controllers import user as user_ctrl
from databases import Database
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from schemas.token import Token
from schemas.user import User, UserCreate, UserDelete, UserUpdate
from utils.database import get_db

router = APIRouter()


@router.post("/init", response_model=User)
async def create_default_superuser(db: Database = Depends(get_db)) -> User:
    """
    Create the default superuser. Run this once when deploy a new app.
    """
    return await user_ctrl.create_default_superuser(db)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Database = Depends(get_db)
) -> Token:
    """
    OAuth2 login, return access token.
    """
    return await user_ctrl.create_token(db, form_data)


@router.get("/me", response_model=User)
async def get_users_me(
    current_user: User = Depends(user_ctrl.get_current_active_user),
) -> User:
    """
    Get current user details.
    """
    return current_user


@router.get("/", response_model=User)
async def get_user(
    user_id: int | None = None,
    username: str | None = None,
    email: EmailStr | None = None,
    db: Database = Depends(get_db),
    current_user: User = Depends(user_ctrl.get_current_active_superuser),
) -> User:
    """
    Get user details by email.
    Require superuser privilege
    """
    return await user_ctrl.get_user(db, user_id, username, email)


@router.get("/all", response_model=List[User])
async def get_all_users(
    db: Database = Depends(get_db),
    current_user: User = Depends(user_ctrl.get_current_active_superuser),
) -> List[User]:
    """
    Get all users details.
    Require superuser privilege
    """
    return await user_ctrl.get_all_users(db)


@router.post("/", response_model=User)
async def create_user(
    user: UserCreate,
    db: Database = Depends(get_db),
    current_user: User = Depends(user_ctrl.get_current_active_superuser),
) -> User:
    """
    Create new user.
    Require superuser privilege
    """
    return await user_ctrl.create_user(db, user)


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Database = Depends(get_db),
    current_user: User = Depends(user_ctrl.get_current_active_superuser),
) -> User:
    """
    Update user details (full_name, password, is_active, is_superuser) by email.
    Require superuser privilege
    """
    return await user_ctrl.update_user(db, user_id, user_update)


@router.delete("/{user_id}", response_model=UserDelete)
async def delete_user(
    user_id: int,
    db: Database = Depends(get_db),
    current_user: User = Depends(user_ctrl.get_current_active_superuser),
) -> UserDelete:
    """
    Delete user by email.
    Require superuser privilege
    """
    return await user_ctrl.delete_user(db, user_id)
