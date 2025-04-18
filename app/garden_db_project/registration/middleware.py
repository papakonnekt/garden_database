# app/garden_db_project/registration/middleware.py
from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch
from django.contrib.auth import get_user_model
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class FirstAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.
        self.register_admin_url = None
        try:
            # Cache the URL reverse lookup
            self.register_admin_url = reverse('register_admin')
        except NoReverseMatch:
            logger.warning("URL 'register_admin' not found during middleware initialization. "
                           "Ensure it's defined in your URLconf.")


    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        # Check if any superuser exists
        has_superuser = User.objects.filter(is_superuser=True).exists()

        if not has_superuser and self.register_admin_url:
            # Define paths that should always be accessible, even without a superuser
            # Check if the current path is the registration page itself or static files
            is_allowed_path = (
                request.path == self.register_admin_url or
                (settings.STATIC_URL and request.path.startswith(settings.STATIC_URL)) or
                (settings.MEDIA_URL and request.path.startswith(settings.MEDIA_URL))
            )

            if not is_allowed_path:
                 logger.info(f"No superuser found. Redirecting request for '{request.path}' to admin registration.")
                 return redirect(self.register_admin_url)
        elif not has_superuser and not self.register_admin_url:
             # Log a warning if the URL couldn't be resolved earlier
             logger.error("FirstAdminMiddleware cannot redirect because 'register_admin' URL is not configured.")


        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
