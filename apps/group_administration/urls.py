from django.urls import path
from .views import *


app_name = 'group_administration'

urlpatterns = [
    path('main/<int:room_id>', show_admin_page, name='group_admin_main'),
    path('member_list/<int:room_id>', show_member_list, name='member_list'),
    path('expel_member', expel_member, name='expel_member'),
    path('transfer_master', transfer_master, name='transfer_master'),
    path('activate_room/<int:room_id>', activate_room, name='activate_room'),
    path('close_room', delete_room, name='close_room'),
    path('direct_invitation/<int:room_id>', direct_invitation, name='direct_invitation'),
    path('search/<int:room_id>/', search_users, name='search_users'),
    path('suggest_join/<int:room_id>', suggest_join, name='suggest_join'),
]