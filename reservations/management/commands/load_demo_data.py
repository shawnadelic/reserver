# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from reservations.models import Customer, Destination
from tests.helpers import create_user, populate_rooms

fake = Faker()


def random_phone_number():
    '''
    Random phone number with a simple format
    '''
    return '{:03}-{:03}-{:04}'.format(
        random.randint(0, 999),
        random.randint(0, 999),
        random.randint(0, 9999)
    )


def populate_fake_customers(num):
    for _ in range(num):
        Customer.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone=random_phone_number(),
            email=fake.email()
        )


def populate_fake_destinations(num):
    destination_type = ('Hotel', 'Motel', 'Inn')

    for _ in range(num):
        destination = Destination.objects.create(
            name='{} {}'.format(fake.company(), random.choice(destination_type)),
            address_1=fake.street_address(),
            city=fake.city(),
            state=fake.state_abbr(),
            zip=fake.zipcode_plus4()
        )

        # Generate a random range of floors and rooms per floor
        # and populate a room for each destination
        floors = random.randint(2, 3)
        rooms_per_floor = random.randint(20, 30)
        populate_rooms(destination, floors, rooms_per_floor)


def create_test_user():
    User = get_user_model()
    username = 'testuser'
    if not User.objects.filter(username=username).exists():
        create_user(
            username='testuser',
            email='testuser@example.com'
        )
        print('Added test user (username: testuser, password: redcabbage)!')


class Command(BaseCommand):
    help = 'Populate with demo data'

    def handle(self, *args, **options):
        with transaction.atomic():
            num_destinations = 2
            num_customers = 4
            populate_fake_destinations(num_destinations)
            populate_fake_customers(num_customers)
            create_test_user()

            print('Added demo data for {} destinations and {} customers!'.format(num_destinations, num_customers))
