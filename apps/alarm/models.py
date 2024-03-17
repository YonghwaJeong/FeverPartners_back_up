from django.db import models
from apps.group_management.models import Room
from apps.user_management.models import User
from apps.goal_management.models import Goal

class Alarm(models.Model):
    alarm_from = models.ForeignKey(User, related_name='sent_alarms', on_delete=models.CASCADE)
    alarm_to = models.ForeignKey(User, related_name='received_alarms', on_delete=models.CASCADE)
    #alarm 보낼때 room 정보 필요
    room = models.ForeignKey(Room, related_name='alarms', on_delete=models.CASCADE, null=True, blank=True)
    goal = models.ForeignKey(Goal, related_name='goals', on_delete=models.CASCADE, null=True, blank=True)