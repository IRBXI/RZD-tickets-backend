from fastapi import APIRouter, HTTPException
from app.models.db_models import Station
from app.services.abstract_APIs import StationAPI, APIUnavailableException
from app.services.rzd_APIs import RZD_StationAPI
from app.repositories.abstract_repos import StationsRepo
from app.repositories.tortoise_stations_repo import TortoiseStationsRepo

from app.models import StationCode
from http import HTTPStatus

router = APIRouter(tags=["stations"])

station_api: StationAPI = RZD_StationAPI()
station_repo: StationsRepo = TortoiseStationsRepo()


@router.get("/stations", response_model=StationCode)
async def get_station_code(name: str):
    try:
        station = await station_repo.get_station_by_name(name)
    except StationsRepo.NoStationException:
        pass
    else:
        return station.id  # type: ignore

    try:
        station_code = await station_api.get_station_code(name)
    except APIUnavailableException as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e))

    if len(station_code) == 0:  # type: ignore
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="There is no station with this name",
        )

    # caching the retrieved station code
    await station_repo.create_station(name, station_code)  # type: ignore

    return station_code
