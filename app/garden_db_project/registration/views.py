# app/garden_db_project/registration/views.py
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy, NoReverseMatch
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.views import View
from .forms import FirstAdminRegistrationForm
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

# Define the login URL name - adjust if your login URL has a different name
# Common defaults include 'login', 'account_login' (django-allauth), etc.
LOGIN_URL_NAME = 'login'

class FirstAdminRegisterView(View):
    template_name = 'registration/first_admin_register.html'
    form_class = FirstAdminRegistrationForm
    success_url = None # Will be set dynamically

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            # Use reverse_lazy for class attributes or resolve dynamically
            self.success_url = reverse_lazy(LOGIN_URL_NAME)
        except NoReverseMatch:
            logger.error(f"Could not reverse the login URL named '{LOGIN_URL_NAME}'. "
                         f"Ensure it's defined in your URLconf. Falling back to '/'.")
            self.success_url = reverse_lazy('/') # Fallback URL

    def dispatch(self, request, *args, **kwargs):
        # Check if a superuser already exists before processing the view
        if User.objects.filter(is_superuser=True).exists():
            messages.warning(request, "An admin account already exists. Please log in.")
            # Redirect to login or dashboard if admin exists
            try:
                # Resolve the URL here for immediate redirection
                login_url = reverse(LOGIN_URL_NAME)
                return redirect(login_url)
            except NoReverseMatch:
                 logger.error(f"Could not reverse login URL ('{LOGIN_URL_NAME}') during dispatch. Redirecting to root.")
                 # Fallback redirect to home page or admin index
                 return redirect('/')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                logger.info(f"First admin user '{user.username}' created successfully.")
                messages.success(request, f"Admin account '{user.username}' created successfully. Please log in.")
                # Resolve the success_url before redirecting
                redirect_url = self.success_url.format() # Resolve the lazy object
                return redirect(redirect_url)
            except Exception as e:
                 # Catch potential errors during user creation/saving
                 logger.error(f"Error creating first admin user: {e}", exc_info=True)
                 messages.error(request, "An unexpected error occurred while creating the admin account. Please check the logs and try again.")
                 # Re-render the form, keeping entered data but showing an error
                 return render(request, self.template_name, {'form': form})
        else:
            # Form is invalid, re-render with errors
            logger.warning("First admin registration form validation failed.")
            messages.warning(request, "Please correct the errors below.") # Use warning for validation errors
            return render(request, self.template_name, {'form': form})
