from tortoise.models import Model
from tortoise import fields


class Station(Model):
    # Stations use 7 character long ids
    id = fields.CharField(primary_key=True, max_length=7)
    # TODO: Maybe research all the posible station names we are going to store to cut down on the max_length
    name = fields.CharField(max_length=100)
