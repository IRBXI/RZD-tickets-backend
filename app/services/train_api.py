from app.models import TrainsRequest, SeatsRequest, Train, Car
from abc import ABC, abstractmethod


class TrainAPI(ABC):
    @abstractmethod
    async def get_trains(self, request_data: TrainsRequest) -> list[Train]:
        pass

    @abstractmethod
    async def get_train_seats(self, request_data: SeatsRequest) -> dict[int, Car]:
        pass

    class APIUnavailableException(Exception):
        pass
