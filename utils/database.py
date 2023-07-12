import databases
from sqlalchemy import create_engine, MetaData

from config import settings

# default to use sqlite
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
)

# to use postgres db
# engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True)

database = databases.Database(settings.SQLALCHEMY_DATABASE_URI)

metadata = MetaData()


# Dependency
def get_db():
    yield database
