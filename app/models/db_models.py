from tortoise.models import Model
from tortoise import fields


class Station(Model):
    # All stations use 7 character long ids
    id = fields.CharField(primary_key=True, max_length=7)
    # TODO: Maybe research all the posible station names to cut down on the max_length
    name = fields.CharField(max_length=100)


class ModelBase(Model):
    id = fields.UUIDField(primary_key=True)

    class Meta:
        abstract = True

    @classmethod
    async def get_by_id(cls, record_id: int):
        return await cls.get_or_none(id=record_id)


class User(ModelBase):
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    active = fields.BooleanField()

    class Meta:
        table = "users"


class BannedToken(ModelBase):
    expired: fields.DatetimeField
    created_at: fields.DatetimeField

    class Meta:
        table = "bannedtokens"
