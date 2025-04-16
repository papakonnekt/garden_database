# Garden Database Quick Start Guide

This guide will help you get up and running with the Garden Database quickly.

## Prerequisites

- Docker and Docker Compose installed on your system
- Git installed on your system

## Quick Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/papakonnekt/garden-database.git
   cd garden-database
   ```

2. **Run the setup script**

   ```bash
   ./scripts/setup.sh
   ```

   This will set up everything you need to get started.

3. **Access the application**

   - Web Interface: http://localhost:8000
   - On first run, you'll be redirected to a setup page to create an admin account
   - After setup, you can access the admin interface at http://localhost:8000/admin
   - API: http://localhost:8000/api/v1/
   - GraphQL: http://localhost:8000/graphql

4. **After creating your admin account**

   Edit the `.env` file and set `FIRST_RUN=false` to disable the setup page on future runs.

## Using the Bulk Import Feature

1. Navigate to http://localhost:8000/bulk-import/
2. Select "Comprehensive" as the entity type
3. Upload a JSON file in the correct format (see sample files in the `sample_data` directory)
4. Click "Import"

## Generating Data with AI

1. Open one of the prompt files in the `prompts` directory
2. Replace the placeholder (e.g., `[[PLANT_NAME]]`) with the specific item you want to research
3. Submit the prompt to an AI tool (like ChatGPT or Claude)
4. Take the JSON output and upload it using the Bulk Import feature

## Stopping the Application

```bash
docker-compose down
```

To remove all data (including the database):

```bash
docker-compose down -v
```

## Next Steps

- Explore the web interface to see the available features
- Check out the API documentation at http://localhost:8000/api/docs/
- Read the full documentation in the `docs` directory
