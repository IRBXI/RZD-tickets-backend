from app.db_models import Station
import pandas as pd




async def load_stations():
    # Check that moscow is in the db.
    # If it isn't there all the stations are probably not yet loaded in this db instance
    moskow = await Station.get_or_none(id="2000000")
    if moskow is not None:
        return

    table = pd.read_csv("./static/tutu_routes.csv", sep=";")
    station_by_id = dict()
    for _, row in table.iterrows():
        station_by_id[row["departure_station_id"]] = row["departure_station_name"]
        station_by_id[row["arrival_station_id"]] = row["arrival_station_name"]
    for id, station in station_by_id.items():
        await Station.create(id=id, name=station)
