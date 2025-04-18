#!/bin/bash

# Simple setup script for the Garden Database project (macOS/Linux)

echo "--- Garden Database Setup ---"

# 1. Check for Docker
echo "[1/3] Checking for Docker..."
if ! command -v docker &> /dev/null
then
    echo "Error: Docker command could not be found."
    echo "Please install Docker Desktop (macOS/Windows) or Docker Engine (Linux)."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker daemon is running (basic check)
if ! docker info &> /dev/null; then
    echo "Error: Docker daemon is not running."
    echo "Please start Docker Desktop or the Docker service."
    exit 1
fi
echo "Docker found and seems to be running."

# 2. Build and start containers
echo "[2/3] Building and starting Docker containers..."
docker-compose up -d --build
if [ $? -ne 0 ]; then
    echo "Error: docker-compose command failed."
    exit 1
fi
echo "Containers started in the background."

# Give services a moment to initialize (optional)
echo "Waiting a few seconds for services to initialize..."
sleep 5

# 3. Open application in browser
echo "[3/3] Opening application in your default browser..."
URL="http://localhost:8000"
# Use 'open' on macOS, 'xdg-open' on Linux
if command -v open &> /dev/null; then
  open "$URL"
elif command -v xdg-open &> /dev/null; then
  xdg-open "$URL"
else
  echo "Could not automatically open browser. Please navigate to $URL"
fi

echo "--- Setup Complete ---"
echo "If the application doesn't load immediately, please wait a bit longer for it to fully start."

exit 0