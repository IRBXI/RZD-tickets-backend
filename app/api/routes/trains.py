from typing import Annotated
from app.models.models import (
    Train,
    TrainsRequest,
    SeatsRequest,
    Car,
)
from app.core.exceptions import APIUnavailableException
from app.services import AbstractTrainService, get_train_service
from fastapi import APIRouter, HTTPException, Depends
from http import HTTPStatus

router = APIRouter(tags=["train"])


@router.post("/trains/get_trains", response_model=list[Train])
async def get_train(
    request_data: TrainsRequest,
    train_service: Annotated[AbstractTrainService, Depends(get_train_service)],
):
    try:
        trains = await train_service.get_trains(request_data)
    except APIUnavailableException as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e))

    return trains


@router.post("/trains/get_seats", response_model=dict[int, Car])
async def get_seats(
    request_data: SeatsRequest,
    train_service: Annotated[AbstractTrainService, Depends(get_train_service)],
):
    try:
        seats_info = await train_service.get_train_seats(request_data)
    except APIUnavailableException as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e))

    return seats_info
