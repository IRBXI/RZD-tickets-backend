from abc import ABC, abstractmethod
from typing import Awaitable
from app.models import TrainsRequest, SeatsRequest, Train, Car
from app.models import StationCode


class APIUnavailableException(Exception):
    pass


class TrainAPI(ABC):
    @abstractmethod
    async def get_trains(self, request_data: TrainsRequest) -> Awaitable[list[Train]]:
        pass

    @abstractmethod
    async def get_train_seats(
        self, request_data: SeatsRequest
    ) -> Awaitable[dict[int, Car]]:
        pass


class StationAPI(ABC):
    @abstractmethod
    async def get_station_code(self, name: str) -> Awaitable[str]:
        pass
