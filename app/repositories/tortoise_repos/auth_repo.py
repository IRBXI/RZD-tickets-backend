from app.repositories.abstract_repos import AbstractAuthRepo
from app.repositories.tortoise_repos.user_repo import TortoiseUserRepo
from app.models.db_models import User, BannedToken
from app.util.hashing import verify_str


class TortoiseAuthRepo(AbstractAuthRepo):
    # Singleton
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(TortoiseAuthRepo, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.user_repo = TortoiseUserRepo()

    async def authorize(self, email: str, password: str) -> User | None:
        user = await self.user_repo.get_user_by_email(email)
        if user is None or not verify_str(password, user.password):
            return None
        return user

    @staticmethod
    async def get_banned_token_by_id(id) -> BannedToken | None:
        return await BannedToken.get_or_none(id=id)

    @staticmethod
    async def add_banned_token(id, expired) -> BannedToken:
        return await BannedToken.create(id=id, expired=expired)
