from django.contrib import admin
from .models import *

class TagAdmin(admin.ModelAdmin):
    list_display = ['tag_name']

admin.site.register(Tag, TagAdmin)
admin.site.register(Goal)
admin.site.register(ActivityTag)
admin.site.register(AchievementReport)