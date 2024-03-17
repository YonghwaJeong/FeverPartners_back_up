from django.urls import path
from .views import *

app_name = 'group_activity'

urlpatterns = [
    path('main/<int:room_id>', show_activity_main, name="main_page"),
    path('activate/<int:room_id>/', activate, name='activate'),
    path('authentication/<int:room_id>/<int:auth_id>', create_authentication, name='create_authentication'),
    path('auth/<int:room_id>', create_auth, name='create_auth'),
    path('verify/<int:room_id>/', verify, name='verify'),
    path('accept_auth_log/<int:member_auth_id>', accept_auth_log, name='accept_auth_log'),
    path('refuse_auth_log/<int:member_auth_id>', refuse_auth_log, name='refuse_auth_log'),
    path('show_log/<int:room_id>', show_log, name='show_log'),
    path('member_list/<int:room_id>', show_member_list, name="member_list"),
    path('permission_check', permission_check, name='permission_check'),
    path('withdraw_from_room', withdraw_from_room, name='withdraw_from_room'),
    path('close_auth/<int:room_id>/<int:auth_id>', close_authentication, name='close_auth'),
    path('auth_detail/<int:auth_id>', load_auth_detail)
]