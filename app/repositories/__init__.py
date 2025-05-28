from app.repositories.abstract_repos import (
    AbstractStationRepo,
    AbstractUserRepo,
    AbstractAuthRepo,
)
from app.repositories.tortoise_repos import (
    TortoiseStationRepo,
    TortoiseUserRepo,
    TortoiseAuthRepo,
)


def setup_repos() -> None:
    TortoiseStationRepo()
    TortoiseUserRepo()
    TortoiseAuthRepo()


def get_station_repo() -> AbstractStationRepo:
    return TortoiseStationRepo()


def get_user_repo() -> AbstractUserRepo:
    return TortoiseUserRepo()


def get_auth_repo() -> AbstractAuthRepo:
    return TortoiseAuthRepo()
