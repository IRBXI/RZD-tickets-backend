from abc import ABC, abstractmethod
from typing import Any
from app.repositories.abstract_repos import (
    AbstractStationRepo,
    AbstractAuthRepo,
    AbstractUserRepo,
)
from app.models import TrainsRequest, SeatsRequest, Train, Car, User, TokenPair
from app.models.db_models import Station
from pydantic import EmailStr


class AbstractTrainService(ABC):
    @abstractmethod
    async def get_trains(self, request_data: TrainsRequest) -> list[Train]:
        pass

    @abstractmethod
    async def get_train_seats(self, request_data: SeatsRequest) -> dict[int, Car]:
        pass


class AbstractStationService(ABC):
    station_repo: AbstractStationRepo

    @abstractmethod
    async def get_station_code(self, name: str) -> str:
        pass

    @abstractmethod
    async def get_station_by_name(self, name: str) -> Station:
        pass

    @abstractmethod
    async def create_station(self, name: str, station_code: str) -> Station:
        pass


class AbstractUserService(ABC):
    user_repo: AbstractUserRepo

    @abstractmethod
    async def get_user_by_email(self, email: EmailStr) -> User | None:
        pass

    @abstractmethod
    async def get_user_by_id(self, id: str) -> User | None:
        pass

    @abstractmethod
    async def create_user(
        self, email: EmailStr, password: str, name: str, active: bool
    ) -> User:
        pass


class AbstractAuthService(ABC):
    auth_repo: AbstractAuthRepo
    user_repo: AbstractUserRepo

    @abstractmethod
    async def authorize(self, email: str, password: str) -> User | None:
        pass

    @staticmethod
    @abstractmethod
    def create_token(user: User) -> TokenPair:
        pass

    @staticmethod
    @abstractmethod
    def get_expire_time() -> int:
        pass

    @abstractmethod
    async def decode_access_token(self, token: str) -> dict[str, Any]:
        pass

    @abstractmethod
    async def add_banned_token(self, id, expired):
        pass

    @staticmethod
    @abstractmethod
    def refresh_token_state(token: str) -> dict[str, Any]:
        pass

    @abstractmethod
    async def get_current_active_user(self, token: str) -> User:
        pass
