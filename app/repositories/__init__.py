from app.repositories.abstract_repos import StationRepo
from app.repositories.tortoise_stations_repo import TortoiseStationRepo


def setup_repos() -> None:
    TortoiseStationRepo()


def get_station_repo() -> StationRepo:
    return TortoiseStationRepo()
