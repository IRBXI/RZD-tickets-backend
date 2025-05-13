from datetime import datetime
from app.models import Train, CarGroup, Station


# Coverts a json from the rzd api to a list[Train]
def get_train_list(json: dict) -> list[Train]:
    trains = json["tp"][0]["list"]
    return [
        Train(
            number=train["number"],
            name=train["brand"],
            origin_station_name=train["station0"],
            destination_station_name=train["station1"],
            departure_time=datetime.strptime(
                f"{train["date0"]} {train["time0"]}", "%d.%m.%Y %H:%M"
            ),
            arrival_time=datetime.strptime(
                f"{train["date1"]} {train["time1"]}", "%d.%m.%Y %H:%M"
            ),
            car_groups=[
                CarGroup(
                    car_type=car_group["typeLoc"],
                    free_seats=car_group["freeSeats"],
                    min_price=car_group["tariff"],
                )
                for car_group in train["cars"]
            ],
        )
        for train in trains
    ]


def get_stations(json: dict) -> list[Station]:
    stations = [stop["station"] for stop in json["data"]["routes"][0]["stops"]]
    return [
        Station(
            name=station["name"],
            code=station["code"],
        )
        for station in stations
    ]
