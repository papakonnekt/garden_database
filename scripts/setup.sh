#!/bin/bash

# Exit on error
set -e

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit the .env file with your own values before continuing."
    exit 1
fi

# Apply patches to settings and urls
echo "Applying patches to Django settings..."
cd app
python garden_db_project/settings_patch.py
cd ..

# Start the containers
echo "Starting Docker containers..."
docker-compose up -d

# Wait for the database to be ready
echo "Waiting for database to be ready..."
sleep 10

# Run migrations
echo "Running database migrations..."
docker-compose exec web python garden_db_project/manage.py migrate

# Collect static files
echo "Collecting static files..."
docker-compose exec web python garden_db_project/manage.py collectstatic --noinput

echo "Setup complete! You can now access the application at http://localhost:8000"
echo "On first run, you will be prompted to create an admin account."
echo "After setting up your admin account, edit the .env file and set FIRST_RUN=false"
