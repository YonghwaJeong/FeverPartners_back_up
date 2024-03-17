from django.urls import path
from . import views

app_name = 'free_board'

urlpatterns = [
  path('<int:study_room_id>/', views.index, name='list'),  #메인 페이지
  path('<int:study_room_id>/<int:post_id>/', views.post_detail, name='detail'),
  path('<int:study_room_id>/comments/create/<int:post_id>/', views.create_comment, name='create_comment'),
  path('<int:study_room_id>/posts/create/', views.create_post, name='create_post'),
  path('<int:study_room_id>/posts/modify/<int:post_id>/', views.modify_post, name='modify_post'),
  path('<int:study_room_id>/posts/delete/<int:post_id>/', views.post_delete, name='post_delete'),
  path('<int:study_room_id>/comments/modify/<int:comment_id>/', views.modify_comment, name='modify_comment'),
  path('<int:study_room_id>/comments/delete/<int:comment_id>/', views.comment_delete, name='comment_delete'),
  path('<int:study_room_id>/vote/post/<int:post_id>/', views.vote_post, name='vote_post'),
]
