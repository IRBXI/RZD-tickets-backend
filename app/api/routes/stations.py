from fastapi import APIRouter, HTTPException
from app.services.abstract_APIs import StationAPI, APIUnavailableException
from app.services.rzd_APIs import RZD_StationAPI
from app.models import StationCode
from http import HTTPStatus

router = APIRouter(tags=["stations"])

station_api: StationAPI = RZD_StationAPI()


@router.get("/stations", response_model=StationCode)
async def get_station_code(name: str):
    # TODO:!!! check db for station_code first
    try:
        station_code = await station_api.get_station_code(name)
    except APIUnavailableException as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e))

    if len(station_code) == 0:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="There is no station with this name",
        )

    return station_code
