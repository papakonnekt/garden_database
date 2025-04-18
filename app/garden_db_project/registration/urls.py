# app/garden_db_project/registration/urls.py
from django.urls import path
from .views import FirstAdminRegisterView

# Define an app name for namespacing if desired, though not strictly necessary here
# app_name = 'registration'

urlpatterns = [
    # URL for the first admin registration page
    path('register-admin/', FirstAdminRegisterView.as_view(), name='register_admin'),

    # It's common to include standard auth URLs here as well if this app handles all auth
    # from django.contrib.auth import views as auth_views
    # path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # ... other auth views like password reset ...
]
