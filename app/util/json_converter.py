from datetime import datetime
from app.models import Train, CarGroup


# Coverts a json from the rzd api to a list[Train]
def get_train_list(json: dict) -> list[Train]:
    print(json)
    train_list = json["tp"][0]["list"]
    res: list[Train] = []
    # TODO: Maybe rewrite it in a more functional way to remove the cycles
    for train in train_list:
        car_groups: list[CarGroup] = []
        for car_group in train["cars"]:
            car_groups.append(
                CarGroup(
                    car_type=car_group["typeLoc"],
                    free_seats=car_group["freeSeats"],
                    min_price=car_group["tariff"],
                )
            )
        res.append(
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
                car_groups=car_groups,
            )
        )
    return res
