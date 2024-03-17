from django.db import models
from django.contrib.auth import get_user_model

class Tag(models.Model):
    tag_name = models.CharField(max_length=10)
    parent_tag = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.tag_name

class ActivityTag(models.Model):
    tag_name = models.CharField(max_length=10)

    def __str__(self):
        return self.tag_name

class Goal(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='goal')
    tags = models.ManyToManyField(Tag, default=None)
    activityTags = models.ManyToManyField(ActivityTag, default=None)
    title = models.CharField(max_length=50)
    content = models.TextField()
    favor_offline = models.BooleanField(default=False)
    is_in_group = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    belonging_group_id = models.IntegerField(null=True)

class AchievementReport(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='achievement_reports/', blank=True, null=True)
    reacted_love = models.ManyToManyField(get_user_model(), default=None, related_name='loved_reports')
    reacted_respectful = models.ManyToManyField(get_user_model(), default=None, related_name='respected_reports')
    reacted_dislike = models.ManyToManyField(get_user_model(), default=None, related_name='disliked_reports')

# 아래는 혹시 몰라서 미리 정의해놓은 모델들 

class UserReport(models.Model):
    reporter = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='report')
    report_target = models.ForeignKey(AchievementReport, on_delete=models.CASCADE, related_name='report')