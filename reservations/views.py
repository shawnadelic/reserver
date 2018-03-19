from rest_framework import viewsets

from reservations.models import Customer, Destination, Reservation, Room
from reservations.serializers import (
    CustomerSerializer, DestinationSerializer, ReservationSerializer,
    RoomSerializer
)
from reservations.throttling import PerReservationRateThrottle


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_throttles(self):
        throttles = super(ReservationViewSet, self).get_throttles()

        # Add per-object rate limiting throttle if action updates objects
        # (Bypass for superusers)
        if not self.request.user.is_superuser and self.request.method in ('PUT', 'PATCH'):
            throttles.append(PerReservationRateThrottle())

        return throttles


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
