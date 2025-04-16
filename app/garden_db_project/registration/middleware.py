from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.models import User
import os

class FirstRunMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if it's the first run and there are no users
        first_run = os.environ.get('FIRST_RUN', 'false').lower() == 'true'
        
        # Skip redirect for the setup page itself and static files
        if (first_run and not User.objects.exists() and 
            not request.path.startswith('/static/') and 
            not request.path.startswith('/media/') and
            request.path != reverse('first_time_setup')):
            return redirect('first_time_setup')
        
        response = self.get_response(request)
        return response
