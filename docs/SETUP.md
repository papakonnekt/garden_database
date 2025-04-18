# Garden Database Setup Guide

This guide provides detailed instructions for setting up and running the Garden Database on your own server.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: [Install Docker Compose](https://docs.docker.com/compose/install/)
- **Git**: [Install Git](https://git-scm.com/downloads)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/papakonnekt/garden-database.git
cd garden-database
```

### 2. Run the Setup Script

The setup script will guide you through the installation process:

**On Windows:**
```
Right-click on scripts\setup.ps1 and select "Run with PowerShell"
```
Or use the batch file:
```
scripts\run_setup.bat
```

**On Linux/Mac:**
```bash
chmod +x ./scripts/setup.sh  # Make the script executable
./scripts/setup.sh
```

This script will:
- Create a default `.env` file if one doesn't exist
- Apply necessary patches to the Django settings
- Start the Docker containers
- Set up the database
- Apply migrations
- Collect static files

The first run may take several minutes as it builds the images and sets up the database.

### 3. Environment Configuration

The setup script automatically creates a `.env` file with secure default values:

```
# Database Configuration
POSTGRES_DB=garden_db
POSTGRES_USER=garden_db_user
POSTGRES_PASSWORD=garden_db_password

# Django Configuration
DJANGO_SECRET_KEY=<randomly generated secure key>
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# First Run Flag
FIRST_RUN=true
```

**No manual configuration is needed** for local development. The script generates a secure random key and sets up working default values.

For production deployment, you may want to edit these values:
- Change the database password to something more secure
- Set `DJANGO_DEBUG=False`
- Add your domain to `DJANGO_ALLOWED_HOSTS`

### 4. Create an Admin Account

On first run, when you access the application, you'll be automatically redirected to a setup page where you can create an admin account.

After creating your admin account, edit the `.env` file and set `FIRST_RUN=false` to disable the setup page.

### 5. Access the Application

- **Web Interface**: http://localhost:8000
- **Admin Interface**: http://localhost:8000/admin
- **API**: http://localhost:8000/api/v1/
- **GraphQL**: http://localhost:8000/graphql

## Configuration Options

### Changing the Port

If you want to run the application on a different port, edit the `docker-compose.yml` file and change the port mapping:

```yaml
services:
  web:
    ports:
      - "8080:8000"  # Change 8080 to your desired port
```

### Production Deployment

For production deployment, make the following changes:

1. Update the `.env` file:
   ```
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=your-domain.com
   ```

2. Set up HTTPS using a reverse proxy like Nginx with Let's Encrypt.

3. Consider using a managed database service instead of the Docker PostgreSQL container.

## Database Backup and Restore

### Creating a Backup

```bash
docker-compose exec db pg_dump -U garden_db_user garden_db > backup.sql
```

### Restoring from a Backup

```bash
cat backup.sql | docker-compose exec -T db psql -U garden_db_user garden_db
```

## Updating the Application

To update to the latest version:

```bash
git pull
docker-compose down
docker-compose up -d --build
docker-compose exec web python garden_db_project/manage.py migrate
```

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. Check that the PostgreSQL container is running:
   ```bash
   docker-compose ps
   ```

2. Verify the database credentials in the `.env` file match those in `settings.py`.

3. Try restarting the containers:
   ```bash
   docker-compose restart
   ```

### Migration Errors

If you encounter migration errors:

```bash
docker-compose exec web python garden_db_project/manage.py showmigrations
```

To reset migrations (use with caution, will delete all data):

```bash
docker-compose down -v
docker-compose up -d
```

### Container Logs

To view logs for troubleshooting:

```bash
docker-compose logs -f web  # For web container logs
docker-compose logs -f db   # For database container logs
```

## System Requirements

Minimum requirements:
- 1 CPU core
- 2GB RAM
- 10GB disk space

Recommended:
- 2+ CPU cores
- 4GB+ RAM
- 20GB+ disk space

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
