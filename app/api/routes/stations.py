from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from app.core.exceptions import APIUnavailableException, NoStationException
from app.services import StationService, get_station_service

from app.models import StationCode
from http import HTTPStatus

router = APIRouter(tags=["stations"])


@router.get("/stations", response_model=StationCode)
async def get_station_code(
    station_service: Annotated[StationService, Depends(get_station_service)],
    name: str,
):
    try:
        station = await station_service.get_station_by_name(name)
        return station.id
    except APIUnavailableException as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e))
    except NoStationException:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="There is no station with this name",
        )
