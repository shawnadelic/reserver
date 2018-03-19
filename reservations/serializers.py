from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import qs_exists

from reservations.models import Customer, Destination, Reservation, Room


class OrderedDateValidator(object):
    '''
    Make sure start date doesn't come after end date
    '''
    def __call__(self, value):
        end_date = None
        start_date = None

        # Default to current values, if instance exists
        if self.instance is not None:
            end_date = self.instance.end_date
            start_date = self.instance.start_date

        end_date = value.get('end_date', end_date)
        start_date = value.get('start_date', start_date)

        if end_date < start_date:
            raise serializers.ValidationError('Invalid dates. Start date must come before end date.')

    def set_context(self, serializer):
        self.instance = getattr(serializer, 'instance', None)


class UniqueForDateRangeValidator(object):
    '''
    Make sure that no conflicting reservations exist for room and date range
    '''
    def __call__(self, value):
        room = None
        start = None
        end = None

        # Default to current values, if instance exists
        if self.instance is not None:
            room = self.instance.room
            start = self.instance.start_date
            end = self.instance.end_date

        room = value.get('room', room)
        start = value.get('start_date', start)
        end = value.get('end_date', end)

        overlap_q = (
            Q(start_date__lte=start, end_date__gte=start) |
            Q(start_date__lte=end, end_date__gte=end) |
            Q(start_date__lte=start, end_date__gte=end) |
            Q(start_date__gte=start, end_date__lte=end)
        )
        queryset = Reservation.objects.filter(overlap_q, room=room)

        # Exclude current instance if updating an existing range
        if self.instance is not None:
            queryset = queryset.exclude(id=self.instance.id)

        if qs_exists(queryset):
            raise serializers.ValidationError('Conflicting reservation exists for this room and date range.')

    def set_context(self, serializer):
        self.instance = getattr(serializer, 'instance', None)


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = (
            'id', 'first_name', 'middle_name', 'last_name', 'phone', 'email'
        )


class ReservationSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        '''
        Check-in status for each reservation.

        Returns a `status` for each reservation (pending, in_house, or checked_out),
        depending on whether today's date falls in range of reservation.
        '''
        today = timezone.now().date()
        if today < obj.start_date:
            return 'pending'
        elif obj.start_date <= today <= obj.end_date:
            return 'in_house'
        else:
            return 'checked_out'

    class Meta:
        model = Reservation
        fields = ('id', 'customer', 'room', 'start_date', 'end_date', 'status',)
        validators = [
            OrderedDateValidator(),
            UniqueForDateRangeValidator()
        ]


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('id', 'number', 'destination')


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = (
            'id', 'name', 'address_1', 'address_2', 'city', 'state', 'zip'
        )
