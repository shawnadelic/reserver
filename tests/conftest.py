import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIClient, APIRequestFactory

from reservations.models import Customer, Destination
from tests.helpers import create_user, populate_rooms


def pytest_addoption(parser):
    parser.addoption(
        '--slow',
        action='store_true',
        default=False,
        help='run slow tests'
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption('--slow'):
        return

    skip_slow = pytest.mark.skip(reason='need --slow option to run')
    for item in items:
        if 'slow' in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture
def client():
    """Replacement for default client fixture"""
    return APIClient()


@pytest.fixture
def rf():
    """Replacement for default request factory fixture"""
    return APIRequestFactory()


@pytest.fixture
def superuser():
    return create_user(
        username='superuser',
        email='superuser@example.com',
        is_superuser=True,
        is_staff=True,
    )


@pytest.fixture
def user():
    return create_user(
        username='user',
        email='user@example.com',
    )


@pytest.fixture
def anonymous_user():
    return AnonymousUser()


@pytest.fixture
def destination():
    destination = Destination.objects.create(
        name='Test Hotel',
        address_1='123 Fake St',
        city='Los Angeles',
        state='CA',
        zip='90210'
    )

    populate_rooms(destination, floors=4, rooms_per_floor=60)

    return destination


@pytest.fixture
def customer():
    return Customer.objects.create(
        first_name='Julie',
        last_name='Mitchell',
        phone='555-555-1234',
        email='juliemitchell@example.com'
    )


@pytest.fixture
def other_customer():
    return Customer.objects.create(
        first_name='Donald',
        last_name='Chapman',
        phone='555-555-5678',
        email='donaldchapman@example.com'
    )


@pytest.fixture
def room(destination):
    return destination.rooms.first()


@pytest.fixture
def other_room(destination, room):
    return destination.rooms.exclude(id=room.id).first()
