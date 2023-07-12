import databases
from config import settings
from sqlalchemy import MetaData, create_engine

# default to use sqlite
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# to use postgres db
# engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, echo=True)

database = databases.Database(settings.SQLALCHEMY_DATABASE_URL)

metadata = MetaData()


# Dependency
def get_db():
    yield database
