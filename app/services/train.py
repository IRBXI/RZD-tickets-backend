from app.models import Stop, SeatsRequest, StationCode, TrainsRequest, Car


def stops_to_seats_requests(
    train_number: StationCode, stops: list[Stop]
) -> list[SeatsRequest]:
    return [
        SeatsRequest(
            train_number=train_number,
            train_request=TrainsRequest(
                from_code=stops[i - 1].station_code,
                to_code=stops[i].station_code,
                date=stops[i - 1].date,  # type: ignore
            ),
            departure_time=stops[i - 1].departure_time,  # type: ignore
            arrival_time=stops[i].arrival_time,  # type: ignore
        )
        for i in range(1, len(stops))
    ]


def combine_cars_seats_info(
    cars_for_segment: list[dict[int, Car]],
) -> dict[int, Car]:
    res: dict[int, Car] = {}
    for cars in cars_for_segment:
        for car_number, car in cars.items():
            for seat, path_segments in car.free_seats.items():
                if car_number not in res:
                    res[car_number] = car
                    break
                res[car_number].free_seats.get(seat, []).append(path_segments[0])
    return res
