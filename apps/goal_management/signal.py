from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model


@receiver(post_save, sender=get_user_model())
def update_goals_index(sender, instance, **kwargs):
    from .models import Goal
    from .search_indexes import GoalDocument
    goals = Goal.objects.filter(user=instance)
    
    for goal in goals:
        GoalDocument().update(goal)