from django.urls import path
from .views import *


app_name = 'group_management'

urlpatterns = [
    path('create_group/', start_creation, name='start_creation'),
    path('create_group/on_submit/', create_room, name='create_room'),
    path('member_recommendation/<int:room_id>', recommend_member, name='recommendation_page'),
    path('suggest_join/<int:room_id>', suggest_join, name='suggest_join'),
    path('member_recommendation/', show_user_list, name='recommendation_page'),
    path('group_list/', show_group_list, name='group_list'),
    path('check_goals', check_user_goal),
    path('check_status/<int:room_id>', check_room_status),
]