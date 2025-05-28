from app.models.db_models import BannedToken, Station, User
from abc import ABC, abstractmethod
from pydantic import EmailStr


class AbstractStationRepo(ABC):
    @staticmethod
    @abstractmethod
    async def get_station_by_name(name: str) -> Station:
        pass

    @staticmethod
    @abstractmethod
    async def create_station(name: str, station_code: str) -> Station:
        pass


class AbstractUserRepo(ABC):
    @staticmethod
    @abstractmethod
    async def get_user_by_email(email: str) -> User | None:
        pass

    @staticmethod
    @abstractmethod
    async def get_user_by_id(id: str) -> User | None:
        pass

    @staticmethod
    @abstractmethod
    async def create_user(
        email: EmailStr, password: str, name: str, active: bool
    ) -> User:
        pass


class AbstractAuthRepo(ABC):
    user_repo: AbstractUserRepo

    @abstractmethod
    async def authorize(self, email: str, password: str) -> User | None:
        pass

    @staticmethod
    @abstractmethod
    async def get_banned_token_by_id(id) -> BannedToken | None:
        pass

    @staticmethod
    @abstractmethod
    async def add_banned_token(id, expired) -> BannedToken:
        pass
