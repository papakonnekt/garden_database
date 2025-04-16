# Garden Database

A comprehensive database system for gardeners and plant enthusiasts. This application provides a structured way to store, manage, and retrieve information about plants, companion planting relationships, pests, diseases, fertilizers, and more.

## Features

### Data Management
- **Comprehensive Plant Data**: Store detailed information about plants including growth requirements, lifecycle, physical characteristics, and more
- **Companion Planting**: Track which plants grow well together and which should be kept apart
- **Pest & Disease Information**: Document common garden pests and diseases, their symptoms, and control methods
- **Fertilizer Database**: Store information about different fertilizers, their composition, and application methods
- **Seed Catalog**: Track seed varieties, germination rates, and planting instructions

### User Interface
- **Web-based Interface**: Browse and search the database through a user-friendly web UI
- **Responsive Design**: Works on desktop and mobile devices
- **Detailed Views**: Comprehensive information pages for each entity type
- **Search Functionality**: Find plants, seeds, pests, and more with powerful search capabilities
- **Filtering Options**: Filter lists by various criteria (plant type, lifecycle, etc.)

### API Access
- **REST API**: Programmatic access to all database entities
- **GraphQL Endpoint**: Flexible querying capabilities
- **Authentication**: Secure token-based authentication for API access

### Import/Export
- **Bulk Import**: Upload JSON files to add multiple records at once
- **AI-Ready Prompts**: Use provided prompts with AI tools to generate properly formatted data
- **Automatic Relationship Handling**: When importing data about one plant, related entities (companions, pests) are automatically created or updated

## Architecture

The Garden Database is built using:
- **Django**: Web framework for the backend
- **PostgreSQL**: Relational database for data storage
- **Django REST Framework**: For the REST API
- **Graphene-Django**: For the GraphQL API
- **Bootstrap**: For the responsive frontend
- **Docker**: For containerization and easy deployment

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/papakonnekt/garden-database.git
   cd garden-database
   ```

2. Run the setup script:
   ```bash
   ./scripts/setup.sh
   ```

3. Access the application:
   - Web UI: http://localhost:8000
   - On first run, you'll be prompted to create an admin account
   - After setup, you can access the API at http://localhost:8000/api/v1/
   - GraphQL is available at http://localhost:8000/graphql

For detailed setup instructions, see [SETUP.md](docs/SETUP.md).

## Using the Database

### Web Interface

The web interface provides access to all database features:

1. **Browse Plants**: View detailed information about plants, their growing requirements, and relationships
2. **Search**: Use the search bar to find specific plants, seeds, pests, or diseases
3. **Companion Planting**: Explore which plants grow well together and which should be kept apart
4. **Bulk Import**: Upload JSON files to add multiple records at once

### Generating Data with AI

The `prompts` directory contains templates for generating properly formatted data using AI tools:

1. **Plant Research**: Use `plant_research_prompt.txt` to generate comprehensive data about a plant, its companions, and pests
2. **Fertilizer Research**: Use `fertilizer_research_prompt.txt` to generate data about fertilizers

To use these prompts:
1. Copy the content of the prompt file
2. Replace the placeholder (e.g., `[[PLANT_NAME]]`) with the specific item you want to research
3. Submit to an AI tool (like ChatGPT or Claude)
4. Take the JSON output and upload it using the Bulk Import feature

### API Access

The database provides both REST and GraphQL APIs for programmatic access:

- **REST API**: Access endpoints at `/api/v1/`
- **GraphQL**: Access the GraphQL interface at `/graphql`

For detailed API documentation, see the API Docs page in the web interface.

## Data Model

The database includes the following main entities:

- **Plant**: Detailed information about plants
- **Seed**: Information about specific seed varieties
- **Pest**: Garden pests and their control methods
- **Disease**: Plant diseases and their management
- **Fertilizer**: Fertilizer types, composition, and application
- **Region**: Growing regions and zones
- **SoilProfile**: Soil types and characteristics
- **Companionship**: Relationships between plants

For a complete data model, see [DATA_MODEL.md](docs/DATA_MODEL.md).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who have helped build this database
- Special thanks to the open-source community for the tools that made this possible
