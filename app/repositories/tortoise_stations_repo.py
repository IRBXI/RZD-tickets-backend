from typing import Awaitable
from app.models.db_models import Station
from .abstract_repos import StationsRepo


class TortoiseStationsRepo(StationsRepo):
    # Singleton
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(TortoiseStationsRepo, cls).__new__(cls)
        return cls.instance

    @staticmethod
    async def get_station_by_name(name: str) -> Awaitable[Station]:
        name = name.upper()
        station = await Station.get_or_none(name=name)

        if station is None:
            raise StationsRepo.NoStationException(
                "There is no station in db with this name"
            )

        return station

    @staticmethod
    async def create_station(name: str, station_code: str) -> Awaitable[Station]:
        name = name.upper()
        station = await Station.create(id=station_code, name=name)
        return station
