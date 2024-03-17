from django.urls import path
from . import views

app_name = 'alarm'

urlpatterns = [
    path('show_alarms', views.show_alarms, name='show_alarms'),
    path('alarm_detail_as_user/<int:pk>/', views.alarm_detail_as_user, name='alarm_detail_as_user'),
    path('alarm_detail_as_master/<int:pk>', views.alarm_detail_as_master, name='alarm_detail_as_master'),
    path('alarm_detail_direct/<int:pk>', views.alarm_detail_direct, name='alarm_detail_direct'),
    path('accept_request/<int:alarm_id>/', views.accept_request, name='accept_request'),
    path('accept_direct_request/<int:alarm_id>/', views.accept_direct_request, name='accept_direct_request'),
    path('reject_request/<int:alarm_id>/', views.reject_request, name='reject_request'),
]