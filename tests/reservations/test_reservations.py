import pytest
from django.urls import reverse
from django.utils.dateparse import parse_date
from rest_framework import status

from reservations.models import Reservation

# Five dates in order, for testing ranges
DATES = [
    '2018-02-01',  # 0
    '2018-02-02',  # 1
    '2018-02-03',  # 2
    '2018-02-04',  # 3
    '2018-02-05',  # 4
]


@pytest.mark.django_db
def test_create_valid_reservation(client, room, customer, superuser):
    client.force_authenticate(user=superuser)

    assert not Reservation.objects.exists()

    # Create a valid reservation
    valid_data = {
        'customer': customer.id,
        'room': room.id,
        'start_date': DATES[1],
        'end_date': DATES[3],
    }
    response = client.post(reverse('reservation-list'), valid_data)

    assert response.status_code == status.HTTP_201_CREATED

    # Verify that a reservation was created with given data
    reservation = Reservation.objects.get()
    assert reservation.customer == customer
    assert reservation.room == room


@pytest.mark.django_db
def test_create_reservation_invalid_dates(client, room, customer, superuser):
    client.force_authenticate(user=superuser)

    assert not Reservation.objects.exists()

    # Try to create a reservation with start date after end date
    invalid_data = {
        'customer': customer.id,
        'room': room.id,
        'start_date': DATES[3],
        'end_date': DATES[1],
    }
    response = client.post(reverse('reservation-list'), invalid_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Verify that no reservation was created
    assert not Reservation.objects.exists()


@pytest.mark.parametrize('start,end', [
    (0, 2), (2, 4),  # Overlapping start or end
    (2, 2), (0, 4),  # Both stand and end are inside or outside range
    (0, 1), (3, 4),  # Start or end dates conflict (exactly equal)
    (1, 1), (3, 3),  # Same as above, but with single start/end date
])
@pytest.mark.django_db
def test_create_reservation_conflict_ranges(
    client, room, other_room, customer, other_customer, superuser, start, end
):
    client.force_authenticate(user=superuser)

    # Initial reservation
    Reservation.objects.create(
        customer=customer,
        room=room,
        start_date=DATES[1],
        end_date=DATES[3]
    )
    assert Reservation.objects.count() == 1

    # Try to create reservation with conflicting dates (should fail)
    data = {
        'customer': other_customer.id,
        'room': room.id,
        'start_date': DATES[start],
        'end_date': DATES[end],
    }
    response = client.post(reverse('reservation-list'), data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Reservation.objects.count() == 1

    # But verify that we can still add for another room
    data['room'] = other_room.id
    response = client.post(reverse('reservation-list'), data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Reservation.objects.count() == 2


@pytest.mark.django_db
def test_update_existing_reservation(client, room, customer, superuser):
    client.force_authenticate(user=superuser)

    # Initial reservation
    reservation = Reservation.objects.create(
        customer=customer,
        room=room,
        start_date=DATES[1],
        end_date=DATES[3]
    )
    assert Reservation.objects.count() == 1

    # Update reservation start date
    data = {
        'start_date': DATES[2],
    }
    response = client.patch(reverse('reservation-detail', args=[reservation.pk]), data)
    assert response.status_code == status.HTTP_200_OK

    # Verify start date was updated
    reservation.refresh_from_db()
    assert reservation.start_date == parse_date(DATES[2])


@pytest.mark.django_db
def test_update_with_conflicting_reservation(client, room, customer, superuser):
    client.force_authenticate(user=superuser)

    # Initial reservation
    Reservation.objects.create(
        customer=customer,
        room=room,
        start_date=DATES[0],
        end_date=DATES[2]
    )
    assert Reservation.objects.count() == 1

    # Second reservation (doesn't conflict yet)
    reservation = Reservation.objects.create(
        customer=customer,
        room=room,
        start_date=DATES[3],
        end_date=DATES[4]
    )
    assert Reservation.objects.count() == 2

    # Attempt to update second reservation with conflicting start date (should fail)
    data = {
        'start_date': DATES[2],
    }
    response = client.patch(reverse('reservation-detail', args=[reservation.pk]), data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Verify start date wasn't update
    reservation.refresh_from_db()
    assert reservation.start_date == parse_date(DATES[3])
