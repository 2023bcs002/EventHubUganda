from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
] 