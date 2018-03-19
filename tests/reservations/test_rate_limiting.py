import time

import pytest
from django.urls import reverse
from django.utils.dateparse import parse_date
from rest_framework import status

from reservations.models import Reservation


@pytest.fixture
def reservation(customer, room):
    return Reservation.objects.create(
        customer=customer,
        room=room,
        start_date='2018-2-16',
        end_date='2018-2-18',
    )


@pytest.mark.django_db
def test_rate_limit(client, user, reservation):
    '''
    Non-superusers should get throttling if making more than one update on a reservation
    '''
    client.force_authenticate(user=user)

    # Update end date 2-20-2018
    updated_date = '2018-2-20'
    data = {'end_date': updated_date}
    response = client.patch(reverse('reservation-detail', args=[reservation.pk]), data)
    assert response.status_code == status.HTTP_200_OK

    reservation.refresh_from_db()
    assert reservation.end_date == parse_date(updated_date)

    # Try to update again, should fail due to rate limiting
    data = {'end_date': '2018-3-30'}
    response = client.patch(reverse('reservation-detail', args=[reservation.pk]), data)
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    # Date should still be set to first update (2-20-2018)
    reservation.refresh_from_db()
    assert reservation.end_date == parse_date(updated_date)


@pytest.mark.slow
@pytest.mark.django_db
def test_rate_limit_wait(client, user, reservation):
    '''
    Similar test as above, but we're waiting between state change requests
    '''
    client.force_authenticate(user=user)

    # Make first update to 2-20-2018
    first_date = '2018-2-20'
    data = {'end_date': first_date}
    response = client.patch(reverse('reservation-detail', args=[reservation.pk]), data)
    assert response.status_code == status.HTTP_200_OK

    reservation.refresh_from_db()
    assert reservation.end_date == parse_date(first_date)

    # Wait for 80 seconds (throttle is for 1 minute), then make second update request
    time.sleep(80)

    # Make second update to 3-30-2018 (should succeed)
    second_date = '2018-3-30'
    data = {'end_date': second_date}
    response = client.patch(reverse('reservation-detail', args=[reservation.pk]), data)
    assert response.status_code == status.HTTP_200_OK

    # Date should now be updated to second update
    reservation.refresh_from_db()
    assert reservation.end_date == parse_date(second_date)
