from django.contrib import admin

from reservations.models import Customer, Destination, Reservation, Room

admin.site.register(Customer)
admin.site.register(Destination)
admin.site.register(Reservation)
admin.site.register(Room)
