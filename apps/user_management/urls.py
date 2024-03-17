from django.urls import path
from . import views

app_name = 'user_management'

urlpatterns = [
    path("", views.start, name="start"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("signup/", views.user_signup, name="signup"),
    path("signup/email/", views.user_signup_email, name="signup_email"),
    path("update/", views.user_update, name="update"),
    path("update/start/", views.user_update_start, name="update_start"),
    path("main/", views.main, name="main"), 
    path('detail/<int:pk>/', views.detail, name='detail'),
    path('update/<int:pk>/', views.update, name='update'),
]