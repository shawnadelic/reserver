from django.conf.urls import include, url
from rest_framework import routers

from reservations.views import (
    CustomerViewSet, DestinationViewSet, ReservationViewSet, RoomViewSet
)

router = routers.DefaultRouter()
router.register('customers', CustomerViewSet)
router.register('destinations', DestinationViewSet)
router.register('reservations', ReservationViewSet)
router.register('rooms', RoomViewSet)

urlpatterns = [
    url(r'^', include(router.urls))
]
