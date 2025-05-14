from tortoise.models import Model
from tortoise import fields

class BaseModel(Model):
    id = fields.IntField(primary_key=True)

    class Meta:
        abstract = True

    @classmethod
    async def get_by_id(cls, record_id: int):
        return await cls.get_or_none(id=record_id)


class User(BaseModel):
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True)

    class Meta:
        table = "users"

    @classmethod
    async def find_by_email(cls, email: str):
        return await cls.get_or_none(email=email)


class Station(Model):
    # Stations use 7 character long ids
    id = fields.CharField(primary_key=True, max_length=7)
    # TODO: Maybe research all the posible station names we are going to store to cut down on the max_length
    name = fields.CharField(max_length=100)
