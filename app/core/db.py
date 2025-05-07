from app.db_models import Station
import pandas as pd


async def load_stations():
    # Check that moscow is in the db.
    # If it isn't there all the stations are probably not yet loaded in this db instance
    moskow = await Station.get_or_none(id="2000000")
    if moskow is not None:
        return
    # TODO: Load {id, station} pairs to the Stations table
    table = pd.read_csv("./static/tutu_routes.csv")
