from typing import Annotated
from app.models.models import (
    Train,
    TrainsRequest,
    SeatsRequest,
    Car,
)
from app.services.abstract_services import TrainService
from app.core.exceptions import APIUnavailableException
from app.services import get_train_service
from fastapi import APIRouter, HTTPException, Depends
from http import HTTPStatus

router = APIRouter(tags=["train"])


@router.post("/trains/get_trains", response_model=list[Train])
async def get_train(
    train_service: Annotated[TrainService, Depends(get_train_service)],
    request_data: TrainsRequest,
):
    try:
        trains = await train_service.get_trains(request_data)
    except APIUnavailableException as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e))

    return trains


@router.post("/trains/get_seats", response_model=dict[int, Car])
async def get_seats(
    train_service: Annotated[TrainService, Depends(get_train_service)],
    request_data: SeatsRequest,
):
    try:
        seats_info = await train_service.get_train_seats(request_data)
    except APIUnavailableException as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e))

    return seats_info
