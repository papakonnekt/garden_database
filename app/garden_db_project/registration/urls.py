from django.urls import path
from . import views

urlpatterns = [
    path('setup/', views.first_time_setup, name='first_time_setup'),
]
