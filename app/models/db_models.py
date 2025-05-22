from tortoise.models import Model
from tortoise import fields
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def hash_password(password: str):
    return pwd_context.hash(password)

class Station(Model):
    # All stations use 7 character long ids
    id = fields.CharField(primary_key=True, max_length=7)
    # TODO: Maybe research all the posible station names to cut down on the max_length

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
    created_at = fields.DatetimeField
    updated_at = fields.DatetimeField
    active = fields.BooleanField

    class Meta:
        table = "users"

    @classmethod
    async def find_by_email(cls, email: str):
        return await cls.get_or_none(email=email)

    @classmethod
    async def authorize(cls, email: str, password: str):
        user = await cls.find_by_email(email)
        if not user or not verify_password(password, user.password):
            return False
        return user


class BannedToken(ModelBase):
    expired: fields.DatetimeField
    created_at: fields.DatetimeField

    class Meta:
        table = "bannedtokens"
