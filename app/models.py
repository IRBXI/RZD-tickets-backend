import datetime
from typing import Annotated
from pydantic import BaseModel, AfterValidator, EmailStr, validator
from app.util.validators import validate_traincode, validate_date, validate_time

# !!! Probably not the last version of these models (will be edited) !!!

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserRegister(UserBase):
    password: str
    password_again: str

    @validator("confirm_correct")
    def verify_passwords(cls, v, values, **kwargs):
        password = values.get("password");

        if v != password:
            raise ValueError("Passwords do not math");

        return v

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    email: EmailStr
    password: str

class JwtTokenSchema(BaseModel):
    token: str
    payload: dict
    expire: datetime


class TokenPair(BaseModel):
    access: JwtTokenSchema
    refresh: JwtTokenSchema


class RefreshToken(BaseModel):
    refresh: str

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


class Station(BaseModel):
    name: str
    code: str


class TrainsRequest(BaseModel):
    from_code: Annotated[str, AfterValidator(validate_traincode)] = "2000000"
    to_code: Annotated[str, AfterValidator(validate_traincode)] = "2000000"
    date: Annotated[str, AfterValidator(validate_date)] = "%d.%m.%Y"


class SeatsRequest(BaseModel):
    train_request: TrainsRequest
    train_number: str = "000A"
    departure_time: Annotated[str, AfterValidator(validate_time)]
    arrival_time: Annotated[str, AfterValidator(validate_time)]
