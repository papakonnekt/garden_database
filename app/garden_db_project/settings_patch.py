"""
This script patches the settings.py and urls.py files to add the registration app
and middleware for the first-time setup.

Run this script after copying the Django project files to the app directory.
"""

import os
import re

def patch_settings():
    settings_path = 'garden_db_project/garden_db_project/settings.py'
    
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # Add registration to INSTALLED_APPS
    if 'registration' not in content:
        pattern = r'(INSTALLED_APPS\s*=\s*\[\s*[^\]]*)\]'
        replacement = r'\1    "registration",\n]'
        content = re.sub(pattern, replacement, content)
    
    # Add FirstRunMiddleware to MIDDLEWARE
    if 'FirstRunMiddleware' not in content:
        pattern = r'(MIDDLEWARE\s*=\s*\[\s*[^\]]*)\]'
        replacement = r'\1    "registration.middleware.FirstRunMiddleware",\n]'
        content = re.sub(pattern, replacement, content)
    
    # Write the modified content back to the file
    with open(settings_path, 'w') as f:
        f.write(content)
    
    print(f"Successfully patched {settings_path}")

def patch_urls():
    urls_path = 'garden_db_project/garden_db_project/urls.py'
    
    with open(urls_path, 'r') as f:
        content = f.read()
    
    # Add import for include if not already present
    if 'from django.urls import path, include' not in content:
        content = content.replace('from django.urls import path', 'from django.urls import path, include')
    
    # Add registration URLs
    if 'path("setup/"' not in content and 'registration.urls' not in content:
        pattern = r'(urlpatterns\s*=\s*\[\s*[^\]]*)\]'
        replacement = r'\1    path("", include("registration.urls")),\n]'
        content = re.sub(pattern, replacement, content)
    
    # Write the modified content back to the file
    with open(urls_path, 'w') as f:
        f.write(content)
    
    print(f"Successfully patched {urls_path}")

if __name__ == "__main__":
    patch_settings()
    patch_urls()
    print("Patching complete!")
