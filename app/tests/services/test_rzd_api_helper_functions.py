from app.models import Stop, SeatsRequest, PathSegment, Car
from app.services.rzd_APIs import RZD_TrainAPI


class TestStopsToSeatsRequests:
    def test_empty_stops_returns_empty_list(self):
        assert RZD_TrainAPI._stops_to_seats_requests("123", []) == []

    def test_two_stops(self):
        stops = [
            Stop(
                station_name="Station A",
                station_code="2000000",
                date="01.01.2025",
                arrival_time=None,
                departure_time="10:00",
            ),
            Stop(
                station_name="Station B",
                station_code="2004000",
                date="01.01.2025",
                arrival_time="11:00",
                departure_time="11:05",
            ),
        ]
        requests: list[SeatsRequest] = RZD_TrainAPI._stops_to_seats_requests(
            "123", stops
        )

        assert len(requests) == 1
        request = requests[0]
        assert request.train_number == "123"
        assert request.train_request.from_code == "2000000"
        assert request.train_request.to_code == "2004000"
        assert request.train_request.date == "01.01.2025"
        assert request.departure_time == "10:00"
        assert request.arrival_time == "11:00"

    def test_three_stops(self):
        stops = [
            Stop(
                station_name="A",
                station_code="2000000",
                date="01.01.2025",
                arrival_time=None,
                departure_time="10:00",
            ),
            Stop(
                station_name="B",
                station_code="2004000",
                date="01.01.2025",
                arrival_time="11:00",
                departure_time="11:05",
            ),
            Stop(
                station_name="C",
                station_code="2006000",
                date="01.01.2025",
                arrival_time="12:00",
                departure_time=None,
            ),
        ]
        requests = RZD_TrainAPI._stops_to_seats_requests("456", stops)

        assert len(requests) == 2
        # First request (A -> B)
        assert requests[0].train_number == "456"
        assert requests[0].train_request.from_code == "2000000"
        assert requests[0].train_request.to_code == "2004000"
        assert requests[0].departure_time == "10:00"
        assert requests[0].arrival_time == "11:00"
        # Second request (B -> C)
        assert requests[1].train_number == "456"
        assert requests[1].train_request.from_code == "2004000"
        assert requests[1].train_request.to_code == "2006000"
        assert requests[1].departure_time == "11:05"
        assert requests[1].arrival_time == "12:00"

    def test_single_stop_returns_empty_list(self):
        stops = [
            Stop(
                station_name="A",
                station_code="2000000",
                date="01.01.2025",
                arrival_time=None,
                departure_time="10:00",
            ),
        ]
        assert RZD_TrainAPI._stops_to_seats_requests("123", stops) == []

    def test_uses_previous_stops_date(self):
        stops = [
            Stop(
                station_name="A",
                station_code="2000000",
                date="01.01.2025",
                arrival_time=None,
                departure_time="23:00",
            ),
            Stop(
                station_name="B",
                station_code="2004000",
                date="02.01.2025",
                arrival_time="01:00",
                departure_time="01:30",
            ),
            Stop(
                station_name="C",
                station_code="2006000",
                date="02.01.2025",
                arrival_time="02:00",
                departure_time=None,
            ),
        ]
        requests = RZD_TrainAPI._stops_to_seats_requests("123", stops)

        assert requests[0].train_request.date == "01.01.2025"  # Uses first stop's date
        assert requests[1].train_request.date == "02.01.2025"  # Uses second stop's date


class TestCombineCarsSeatsInfo:
    def test_empty_input(self):
        cars_for_segment = []
        result = RZD_TrainAPI._combine_cars_seats_info(cars_for_segment)
        assert result == {}

    def test_single_car_single_seat(self):
        seg1 = PathSegment(
            start_station_name="A",
            end_station_name="B",
            start_time="01:00",
            end_time="02:00",
        )
        car = Car(car_number=1, car_type="TypeA", free_seats={"001": [seg1]})
        cars_for_segment = [{1: car}]
        result = RZD_TrainAPI._combine_cars_seats_info(cars_for_segment)
        assert result == {1: car}

    def test_multiple_segments_for_one_seat(self):
        seg1 = PathSegment(
            start_station_name="A",
            end_station_name="B",
            start_time="01:00",
            end_time="02:00",
        )
        seg2 = PathSegment(
            start_station_name="B",
            end_station_name="C",
            start_time="02:05",
            end_time="03:00",
        )
        car1 = Car(car_number=1, car_type="TypeA", free_seats={"001": [seg1]})
        car2 = Car(car_number=1, car_type="TypeA", free_seats={"001": [seg2]})
        cars_for_segment = [{1: car1}, {1: car2}]
        result = RZD_TrainAPI._combine_cars_seats_info(cars_for_segment)
        assert result == {
            1: Car(car_number=1, car_type="TypeA", free_seats={"001": [seg1, seg2]})
        }

    def test_multiple_seats(self):
        seg1 = PathSegment(
            start_station_name="A",
            end_station_name="B",
            start_time="01:00",
            end_time="02:00",
        )
        seg2 = PathSegment(
            start_station_name="B",
            end_station_name="C",
            start_time="02:05",
            end_time="03:00",
        )
        car1 = Car(car_number=1, car_type="TypeA", free_seats={"001": [seg1]})
        car2 = Car(car_number=1, car_type="TypeA", free_seats={"002": [seg2]})
        cars_for_segment = [{1: car1}, {1: car2}]
        result = RZD_TrainAPI._combine_cars_seats_info(cars_for_segment)
        expected_car = Car(
            car_number=1, car_type="TypeA", free_seats={"001": [seg1], "002": [seg2]}
        )
        assert result == {1: expected_car}
