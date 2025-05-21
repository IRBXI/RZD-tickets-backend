from datetime import datetime
from app.models import Train, CarGroup, Stop, PathSegment, Car
import json as js


class RzdJsonConverter:
    @staticmethod
    def get_trains_from_json(json: dict) -> list[Train]:
        trains = json["tp"][0]["list"]
        return [
            Train(
                number=train["number"],
                name=train["brand"],
                origin_station_name=train["station0"],
                destination_station_name=train["station1"],
                departure_time=datetime.strptime(
                    f'{train["date0"]} {train["time0"]}', "%d.%m.%Y %H:%M"
                ),
                arrival_time=datetime.strptime(
                    f'{train["date1"]} {train["time1"]}', "%d.%m.%Y %H:%M"
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

    @staticmethod
    def get_stops_from_json(json: dict) -> list[Stop]:
        stops = json["data"]["routes"][0]["stops"]
        return [
            Stop(
                station_name=stop["station"]["name"],
                station_code=str(stop["station"]["code"]),
                date=(
                    stop["depTimeMSK"].split()[0].replace("-", ".")
                    if stop["depTimeMSK"] is not None
                    else None
                ),
                departure_time=(
                    stop["depTimeMSK"].split()[1]
                    if stop["depTimeMSK"] is not None
                    else None
                ),
                arrival_time=(
                    stop["arvTimeMSK"].split()[1]
                    if stop["arvTimeMSK"] is not None
                    else None
                ),
            )
            for stop in stops
        ]

    @staticmethod
    def get_seats_from_str(seats_str: str) -> list[str]:
        seats = seats_str.split(",")
        res = []
        for s in seats:
            s = "".join(c for c in s if c.isdigit() or c == "-")
            # TODO: take into account seats with 'M' or 'Ж' in seat number
            if "-" in s:
                first, last = map(int, s.split("-"))
                for i in range(first, last + 1):
                    res.append("{:03d}".format(i))
                continue
            res.append("{:03d}".format(int(s)))

        return res

    @staticmethod
    def get_cars_from_json(json: dict) -> dict[int, Car]:
        print(js.dumps(json, indent=4, ensure_ascii=False))

        json = json["lst"][0]

        if "result" in json and json["result"] == "FAIL":
            return {}

        path_segment = PathSegment(
            start_station_name=json["station0"],
            end_station_name=json["station1"],
            start_time=json["time0"],
            end_time=json["time1"],
        )

        res: dict[int, Car] = {}
        cars = json["cars"]
        for car in cars:
            new_car = Car(
                car_number=car["cnumber"],
                car_type=car["catLabelLoc"],
                free_seats={},
            )
            for seat in RzdJsonConverter.get_seats_from_str(car["places"]):
                new_car.free_seats[seat] = [path_segment]
            res[new_car.car_number] = new_car

        return res
