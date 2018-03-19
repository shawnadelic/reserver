from django.db import models


class Reservation(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return str(self.customer)


class Room(models.Model):
    number = models.IntegerField()
    destination = models.ForeignKey('Destination', on_delete=models.CASCADE, related_name='rooms')

    class Meta:
        unique_together = ('number', 'destination')

    def __str__(self):
        return 'Room {} ({})'.format(self.number, self.destination)


class Destination(models.Model):
    name = models.CharField(max_length=120)
    address_1 = models.CharField(max_length=120)
    address_2 = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Customer(models.Model):
    first_name = models.CharField(max_length=120)
    middle_name = models.CharField(max_length=120, blank=True)
    last_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=120)
    email = models.EmailField()

    def __str__(self):
        return '{}, {}'.format(self.last_name, self.first_name)
