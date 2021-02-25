import os

from peewee import Model, CharField, FloatField, ForeignKeyField
from playhouse.db_url import connect

db = connect(os.environ.get('DATABASE_URL', 'sqlite:///my_database.db'))

class BaseModel(Model):
    class Meta:
        database = db

class Donor(BaseModel):
    name = CharField(max_length=255, unique=True)

class Donation(BaseModel):
    value = FloatField()
    donor = ForeignKeyField(Donor, field='name', backref='donations')

class User(BaseModel):
    username = CharField(max_length=255, unique=True)
    password = CharField(max_length=255)
