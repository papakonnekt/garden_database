@echo off
REM Simple setup script for the Garden Database project (Windows)

echo --- Garden Database Setup ---

REM 1. Check for Docker
echo [1/3] Checking for Docker...
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Docker command could not be found.
    echo Please install Docker Desktop for Windows.
    echo Visit: https://docs.docker.com/get-docker/
    goto :eof
)

REM Check if Docker daemon is running (basic check)
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Docker daemon is not running.
    echo Please start Docker Desktop.
    goto :eof
)
echo Docker found and seems to be running.

REM 2. Build and start containers
echo [2/3] Building and starting Docker containers...
docker-compose up -d --build
if %errorlevel% neq 0 (
    echo Error: docker-compose command failed.
    goto :eof
)
echo Containers started in the background.

REM Give services a moment to initialize (optional)
echo Waiting a few seconds for services to initialize...
timeout /t 5 /nobreak > nul

REM 3. Open application in browser
echo [3/3] Opening application in your default browser...
set URL="http://localhost:8000"
start "" %URL%

echo --- Setup Complete ---
echo If the application doesn't load immediately, please wait a bit longer for it to fully start.

:eof