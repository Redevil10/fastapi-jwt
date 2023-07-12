from sqlalchemy import Boolean, Column, Integer, String, Table
from utils.database import metadata

UserTable = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True, autoincrement=True),
    Column("username", String(length=50), unique=True, index=True),
    Column("email", String(length=50), unique=True, index=True),
    Column("full_name", String(length=50)),
    Column("hashed_password", String),
    Column("is_active", Boolean, default=True),
    Column("is_superuser", Boolean, default=False),
)
