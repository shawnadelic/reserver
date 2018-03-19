from rest_framework.throttling import SimpleRateThrottle


class PerReservationRateThrottle(SimpleRateThrottle):
    scope = 'per_reservation'

    def get_cache_key(self, request, view):
        '''
        Create cache key in format of throttle_per_reservation_<id> each
        time a reservation object is throttled.
        '''
        obj = view.get_object()
        return 'throttle_per_reservation_{}'.format(obj.id)
