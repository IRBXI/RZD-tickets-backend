from app.services.abstract_services import TrainService, StationService
from app.services.rzd_services import RzdTrainService, RzdStationService


async def setup_services() -> None:
    await RzdTrainService.create()
    await RzdStationService.create()


def get_train_service() -> TrainService:
    return RzdTrainService()


def get_station_service() -> StationService:
    return RzdStationService()
