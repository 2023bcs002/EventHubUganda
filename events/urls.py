from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('event/new/', views.event_create, name='event_create'),
    path('event/<slug:slug>/', views.event_detail, name='event_detail'),
    path('category/<slug:slug>/', views.category_events, name='category_events'),
    path('event/<slug:slug>/edit/', views.event_edit, name='event_edit'),
    path('event/<slug:slug>/delete/', views.event_delete, name='event_delete'),
    path('event/<slug:slug>/register/', views.event_register, name='event_register'),
    path('registrations/', views.registration_list, name='registration_list'),
] 