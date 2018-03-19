from django.contrib.auth import get_user_model

from reservations.models import Room


def populate_rooms(destination, floors, rooms_per_floor):
    '''
    Factory function to initialize room objects for a single destination

    Room numbers are assigned based on number of floors and number of
    rooms per floor.

    We are assuming a simple floor model where each floor has the same
    number of rooms
    '''
    for floor in range(1, floors + 1):
        for num in range(rooms_per_floor):
            room_num = floor * 100 + num
            Room.objects.create(
                number=room_num,
                destination=destination
            )


def create_user(username, email, **kwargs):
    User = get_user_model()
    user = User.objects.create(
        username=username,
        email=email,
        **kwargs
    )
    user.set_password('redcabbage')
    user.save()
    return user
