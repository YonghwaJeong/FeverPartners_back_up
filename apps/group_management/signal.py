from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model


@receiver(post_save, sender=get_user_model())
def update_goals_index(sender, instance, **kwargs):
    from .models import Room
    from .search_indexes import RoomDocument
    rooms = Room.objects.filter(master=instance)
    
    for room in rooms:
        RoomDocument().update(room)