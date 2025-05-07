import datetime
from pydantic import BaseModel

# !!! Probably not the last version of these models (will be edited) !!!


class Compartment(BaseModel):
    number: int
    free_places: list[str]


class Car(BaseModel):
    compartments: list[Compartment]


class CarGroup(BaseModel):
    car_type: str
    place_quantity: int
    cars: list[Car] = []

    def add_car(self, car: Car) -> None:
        self.cars.append(car)


class Train(BaseModel):
    train_number: str
    train_name: str
    origin_station_name: str
    origin_station_code: str
    destination_station_name: str
    destination_station_code: str
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
