"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.user_management.urls")),
    path('goal/', include('apps.goal_management.urls')),
    path('group/', include('apps.group_management.urls')),
    path("alarm/", include("apps.alarm.urls")),
    path("accounts/", include("allauth.urls")),
    path('accounts/', include('allauth.socialaccount.urls')),
    path('board/', include('apps.free_board.urls')),
    path('group_activity/', include("apps.group_activity.urls")),
    path('group_admin/', include("apps.group_administration.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# 개발 중에만 사용 (production에서는 웹 서버에서 처리하도록 하자)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)