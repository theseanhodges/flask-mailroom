import os
import random

from passlib.hash import pbkdf2_sha256

from model import db, Donor, Donation, User

db.connect(os.environ.get('DATABASE_URL', 'sqlite:///my_database.db'))

# This line will allow you "upgrade" an existing database by
# dropping all existing tables from it.
db.drop_tables([Donor, Donation, User])

db.create_tables([Donor, Donation, User])

if os.environ.get('IN_HEROKU') != "true":
    # Don't create test data in Heroku

    User(username="Test", password=pbkdf2_sha256.hash('test')).save()

    alice = Donor(name="Alice")
    alice.save()

    bob = Donor(name="Bob")
    bob.save()

    charlie = Donor(name="Charlie")
    charlie.save()

    donors = [alice, bob, charlie]

    for x in range(30):
        Donation(donor=random.choice(donors), value=random.randint(100, 10000)).save()
