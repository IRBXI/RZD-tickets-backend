from app.models.db_models import Station
from abc import ABC, abstractmethod


class StationRepo(ABC):
    @staticmethod
    @abstractmethod
    async def get_station_by_name(name: str) -> Station:
        pass

    @staticmethod
    @abstractmethod
    async def create_station(name: str, station_code: str) -> Station:
        pass
