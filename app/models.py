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
    free_seats: int
    min_price: int


class Train(BaseModel):
    number: str
    name: str
    origin_station_name: str
    destination_station_name: str
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    car_groups: list[CarGroup]
