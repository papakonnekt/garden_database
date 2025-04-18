# Garden Database Django Application

This directory contains the core Django application for the Garden Database project.

## Overview

The application is built using Django 4.2 and leverages several key libraries:

*   **Django REST Framework (DRF):** For building RESTful APIs.
*   **Graphene-Django:** For providing a GraphQL API endpoint.
*   **Celery & Redis:** For handling asynchronous tasks, specifically bulk data imports.
*   **Psycopg2:** For connecting to a PostgreSQL database.
*   **Whitenoise:** For serving static files efficiently.
*   **Gunicorn:** As the WSGI HTTP server for deployment.

## Key Components

*   **`garden_db_project/`:** The main Django project directory.
    *   **`horticulture/`:** The primary application containing the core logic and data models for managing horticultural information (Plants, Pests, Diseases, Regions, Soil Profiles, Fertilizers, Seeds, Companionship data, etc.). It includes:
        *   Models (`models.py`) defining the database schema.
        *   Serializers (`serializers.py`) for the REST API.
        *   GraphQL schema (`schema.py`) for the GraphQL API.
        *   API Views (`views.py`) using DRF ViewSets.
        *   Web Views (`web_views.py`) for user-facing HTML pages.
        *   Bulk import functionality (`bulk_import_handler.py`, `tasks.py`, `new_bulk_import_view.py`) allowing data import via JSON, processed asynchronously using Celery.
        *   Admin interface configuration (`admin.py`).
        *   Tests (`tests.py`, `test_*.py`) for various components.
        *   A weather API client (`weather_api.py`).
    *   **`registration/`:** A small application responsible for handling the initial setup and registration of the first administrator user. It uses middleware (`middleware.py`) to intercept requests and redirect to a registration form (`forms.py`, `views.py`) if no admin user exists.
    *   `settings.py`: Standard Django settings (patched by `settings_patch.py` during setup).
    *   `urls.py`: Root URL configuration.
    *   `manage.py`: Django's command-line utility.
*   **`Dockerfile`:** Defines the container image for deploying the application, based on Python 3.10.
*   **`requirements.txt`:** Lists all Python dependencies.
*   **`settings_patch.py`:** A utility script run during setup to integrate the `registration` app into the main project settings and URL configuration.

## Functionality

The application provides a comprehensive system for storing, managing, and accessing garden-related data through both REST and GraphQL APIs, as well as a basic web interface. It supports bulk data imports and includes a mechanism for initial administrator setup.