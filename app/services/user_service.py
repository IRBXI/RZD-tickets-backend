from app.services import AbstractUserService
from app.repositories import get_user_repo
from app.models import User
from pydantic import EmailStr
from app.util.hashing import hash_str


class UserService(AbstractUserService):
    # Singleton
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(UserService, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.user_repo = get_user_repo()

    async def get_user_by_email(self, email: EmailStr) -> User | None:
        user = await self.user_repo.get_user_by_email(email)
        if user is None:
            return None

        return User.model_validate(user, from_attributes=True)

    async def get_user_by_id(self, id: str) -> User | None:
        user = await self.user_repo.get_user_by_id(id)
        if user is None:
            return None

        return User.model_validate(user, from_attributes=True)

    async def create_user(
        self, email: EmailStr, password: str, name: str, active: bool
    ) -> User:
        user = await self.user_repo.create_user(email, hash_str(password), name, active)
        return User.model_validate(user, from_attributes=True)
