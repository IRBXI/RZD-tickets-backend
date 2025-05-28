from app.repositories.abstract_repos import AbstractUserRepo
from app.models.db_models import User
from pydantic import EmailStr


class TortoiseUserRepo(AbstractUserRepo):
    # Singleton
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(TortoiseUserRepo, cls).__new__(cls)
        return cls.instance

    @staticmethod
    async def get_user_by_email(email: str) -> User | None:
        return await User.get_or_none(email=email)

    @staticmethod
    async def get_user_by_id(id: str) -> User | None:
        return await User.get_or_none(id=id)

    @staticmethod
    async def create_user(
        email: EmailStr, password: str, name: str, active: bool
    ) -> User:
        return await User.create(
            email=email, password=password, name=name, active=active
        )
