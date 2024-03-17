from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Authentication)
admin.site.register(MemberAuthentication)
admin.site.register(UserActivityInfo)