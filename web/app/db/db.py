import databases
import ormar
import sqlalchemy
import datetime

from .config import settings

database = databases.Database(settings.db_url)
metadata = sqlalchemy.MetaData()


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class User(ormar.Model):
    class Meta(BaseMeta):
        tablename = "users"

    id: int = ormar.Integer(primary_key=True)
    email: str = ormar.String(max_length=128, unique=True, nullable=False)
    full_name: str = ormar.String(max_length=128, nullable=False)
    password: str = ormar.String(max_length=128, nullable=False)
    created_date: datetime.datetime = ormar.DateTime(default=datetime.datetime.now())
    active: bool = ormar.Boolean(default=True, nullable=False)


class Gardens(ormar.Model):
    class Meta(BaseMeta):
        tablename = "gardens"

    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=128, unique=True, nullable=False)
    created_date: datetime.datetime = ormar.DateTime(default=datetime.datetime.now())
    active: bool = ormar.Boolean(default=True, nullable=False)


class GardensLogs(ormar.Model):
    class Meta(BaseMeta):
        tablename = "gardens_logs"

    id: int = ormar.Integer(primary_key=True)
    garden_id: int = ormar.Integer(nullable=False)
    data: str = ormar.JSON(nullable=False)
    date: datetime.datetime = ormar.DateTime(default=datetime.datetime.now())


engine = sqlalchemy.create_engine(settings.db_url)
metadata.create_all(engine)
