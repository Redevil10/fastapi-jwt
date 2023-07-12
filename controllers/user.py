from datetime import timedelta
from typing import List, Optional

from databases import Database
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import EmailStr

from config import settings
from controllers.token import (create_access_token, get_password_hash,
                               oauth2_scheme, verify_password)
from models.user import UserTable
from schemas.token import Token, TokenData
from schemas.user import User, UserCreate, UserDelete, UserInDB, UserUpdate
from utils.database import get_db


async def get_user(
    db: Database, user_id: int | None, username: str | None, email: EmailStr | None
) -> User:
    if user_id is not None:
        db_user = await get_db_user_by_id(db, user_id)
    elif username is not None:
        db_user = await get_db_user_by_username(db, username)
    elif email is not None:
        db_user = await get_db_user_by_email(db, email)
    else:
        raise HTTPException(
            status_code=404,
            detail="Invalid query. Should pass in user_id or username or email",
        )

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user = convert_user_for_api(db_user)
    return user


async def get_db_user_by_id(db: Database, user_id: int) -> UserInDB:
    query = UserTable.select().where(UserTable.c.id == user_id)
    return await db.fetch_one(query=query)


async def get_db_user_by_email(db: Database, user_email: EmailStr) -> UserInDB:
    query = UserTable.select().where(UserTable.c.email == user_email)
    return await db.fetch_one(query=query)


async def get_db_user_by_username(db: Database, username: str) -> UserInDB:
    query = UserTable.select().where(UserTable.c.username == username)
    return await db.fetch_one(query=query)


def convert_user_for_api(db_user: UserInDB) -> User:
    user = User(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        is_active=db_user.is_active,
        is_superuser=db_user.is_superuser,
    )
    return user


async def get_all_users(db: Database) -> List[User]:
    db_users = await get_db_users_all(db)
    if db_users is None:
        raise HTTPException(status_code=404, detail="User not found")
    user = convert_users_for_api(db_users)
    return user


async def get_db_users_all(db: Database) -> List[UserInDB]:
    query = UserTable.select()
    return await db.fetch_all(query=query)


def convert_users_for_api(db_users: List[UserInDB]) -> List[User]:
    users = []
    for db_user in db_users:
        user = convert_user_for_api(db_user)
        users.append(user)
    return users


async def create_user(db: Database, user: UserCreate) -> User:
    # check if user already exists
    conflict_user = await get_db_user_by_email(db, user_email=user.email)
    if conflict_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    conflict_user = await get_db_user_by_username(db, username=user.username)
    if conflict_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    query = UserTable.insert()
    values = {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "hashed_password": get_password_hash(user.password),
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
    }
    await db.execute(query=query, values=values)
    db_user = await get_db_user_by_username(db, username=user.username)
    user = convert_user_for_api(db_user)
    return user


async def create_default_superuser(db: Database) -> User:
    default_admin_user = UserCreate(
        username=settings.DEFAULT_SUPERUSER_USERNAME,
        email=settings.DEFAULT_SUPERUSER_EMAIL,
        full_name=settings.DEFAULT_SUPERUSER_FULL_NAME,
        password=settings.DEFAULT_SUPERUSER_PASSWORD,
        is_active=True,
        is_superuser=True,
    )
    return await create_user(db, default_admin_user)


async def update_user(db: Database, user_id: int, user: UserUpdate) -> User:
    db_user = await get_db_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    query = UserTable.update().where(UserTable.c.id == user_id)

    values = {}
    # if allow to update username
    if user.username is not None and user.username != db_user.username:
        conflict_user = await get_db_user_by_username(db, user.username)
        if conflict_user is not None:
            raise HTTPException(
                status_code=404, detail="User with same username already exists"
            )
        values["username"] = user.username

    # if allow to update email
    if user.email is not None and user.email != db_user.email:
        conflict_user = await get_db_user_by_email(db, user.email)
        if conflict_user is not None:
            raise HTTPException(
                status_code=404, detail="User with same email already exists"
            )
        values["email"] = user.email

    if user.full_name is not None and user.full_name != db_user.full_name:
        values["full_name"] = user.full_name
    if user.password is not None:
        values["hashed_password"] = get_password_hash(user.password)
    if user.is_active is not None and user.is_active != db_user.is_active:
        values["is_active"] = user.is_active
    if user.is_superuser is not None and user.is_superuser != db_user.is_superuser:
        values["is_superuser"] = user.is_superuser
    await db.execute(query, values)
    db_user = await get_db_user_by_id(db, user_id)
    updated_user = convert_user_for_api(db_user)
    return updated_user


async def delete_user(db: Database, user_id: int) -> UserDelete:
    db_user = await get_db_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    query = UserTable.delete().where(UserTable.c.id == user_id)
    await db.execute(query)
    deleted_user = UserDelete(
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        is_active=db_user.is_active,
        is_superuser=db_user.is_superuser,
        status="deleted",
    )
    return deleted_user


# authentications


async def authenticate_user(
    db: Database, username: str, password: str
) -> Optional[User]:
    db_user = await get_db_user_by_username(db, username)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


async def get_current_user(
    db: Database = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    db_user = await get_db_user_by_username(db, username=token_data.username)
    if db_user is None:
        raise credentials_exception
    user = convert_user_for_api(db_user)
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


async def create_token(db: Database, form_data: OAuth2PasswordRequestForm) -> Token:
    db_user = await authenticate_user(db, form_data.username, form_data.password)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    token = Token(access_token=access_token, token_type="bearer")
    return token
