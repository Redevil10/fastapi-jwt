from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool | None = True
    is_superuser: bool = False


class UserCreate(UserBase):
    username: str
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    password: str | None = None


class UserDelete(UserBase):
    status: str


class UserInDBBase(UserBase):
    id: int

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(User):
    hashed_password: str
