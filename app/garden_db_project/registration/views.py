from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.conf import settings
from django.contrib import messages
import os
from .forms import FirstTimeSetupForm

def first_time_setup(request):
    # Check if we should show the first-time setup page
    first_run = os.environ.get('FIRST_RUN', 'false').lower() == 'true'
    
    # If it's not the first run or there are already users, redirect to home
    if not first_run or User.objects.exists():
        return redirect('home')
    
    if request.method == 'POST':
        form = FirstTimeSetupForm(request.POST)
        if form.is_valid():
            # Create the superuser
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            user.is_staff = True
            user.is_superuser = True
            user.save()
            
            # Log the user in
            login(request, user)
            
            # Show a success message
            messages.success(request, 'Your admin account has been created successfully! You are now logged in.')
            
            # Redirect to the home page
            return redirect('home')
    else:
        form = FirstTimeSetupForm()
    
    return render(request, 'registration/first_time_setup.html', {'form': form})
