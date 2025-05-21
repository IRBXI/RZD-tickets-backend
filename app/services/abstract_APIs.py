from app.models import TrainsRequest, SeatsRequest, Train, Car
from app.models import StationCode
from abc import ABC, abstractmethod


class APIUnavailableException(Exception):
    pass


class TrainAPI(ABC):
    @abstractmethod
    async def get_trains(self, request_data: TrainsRequest) -> list[Train]:
        pass

    @abstractmethod
    async def get_train_seats(self, request_data: SeatsRequest) -> dict[int, Car]:
        pass


class StationAPI(ABC):
    @abstractmethod
    async def get_station_code(self, name: str) -> StationCode:
        pass
