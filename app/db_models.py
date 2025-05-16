from tortoise.models import Model
from tortoise import fields
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def hash_password(password: str):
    return pwd_context.hash(password)


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
    password = fields.CharField(max_length=255)

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


class Station(Model):
    # Stations use 7 character long ids
    id = fields.CharField(primary_key=True, max_length=7)
    # TODO: Maybe research all the posible station names we are going to store to cut down on the max_length
    name = fields.CharField(max_length=100)
