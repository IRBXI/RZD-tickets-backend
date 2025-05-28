from abc import ABC, abstractmethod
from app.repositories.abstract_repos import StationRepo
from app.models import TrainsRequest, SeatsRequest, Train, Car
from app.models.db_models import Station


class TrainService(ABC):
    @abstractmethod
    async def get_trains(self, request_data: TrainsRequest) -> list[Train]:
        pass

    @abstractmethod
    async def get_train_seats(self, request_data: SeatsRequest) -> dict[int, Car]:
        pass


class StationService(ABC):
    station_repo: StationRepo

    @abstractmethod
    async def get_station_code(self, name: str) -> str:
        pass

    @abstractmethod
    async def get_station_by_name(self, name: str) -> Station:
        pass

    @abstractmethod
    async def create_station(self, name: str, station_code: str) -> Station:
        pass
