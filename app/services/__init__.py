from app.services.abstract_services import (
    AbstractTrainService,
    AbstractStationService,
    AbstractUserService,
    AbstractAuthService,
)
from app.services.rzd_services import RzdTrainService, RzdStationService
from app.services.user_service import UserService
from app.services.auth_service import AuthService


async def setup_services() -> None:
    await RzdTrainService.create()
    await RzdStationService.create()
    UserService()
    AuthService()


def get_train_service() -> AbstractTrainService:
    return RzdTrainService()


def get_station_service() -> AbstractStationService:
    return RzdStationService()


def get_user_service() -> AbstractUserService:
    return UserService()


def get_auth_service() -> AbstractAuthService:
    return AuthService()
