# Garden Database & Horticulture Management

A Django-based web application designed for managing comprehensive horticultural data. It allows users to store, retrieve, and manage information about plants, seeds, companion planting interactions, pests, diseases, fertilizers, soil profiles, and growing regions. The application features a web interface, REST/GraphQL APIs, and integrates with AI tools via prompts for efficient data generation. The goal is to provide a robust tool for gardeners, researchers, and enthusiasts.

## Technology Stack

*   Python
*   Django (including Django REST Framework, Graphene-Django)
*   PostgreSQL
*   Docker / Docker Compose
*   Bootstrap

## Setup and Installation

### Prerequisites

*   Docker and Docker Compose
*   Git

### Using Docker (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/papakonnekt/garden-database.git
    cd garden-database
    ```
2.  **Configure Environment:**
    *   Run `setup.bat` (Windows) or `setup.sh` (Linux/Mac). These scripts help create the necessary `.env` file.
    *   Alternatively, create the `.env` file manually. Refer to `docs/SETUP.md` for detailed instructions on required environment variables.
3.  **Start the application:**
    ```bash
    docker-compose up -d
    ```
4.  **Access the application:**
    *   Open your web browser to `http://localhost:8000`.
    *   On the first run, you might be prompted to create an administrator account.

### Setup Scripts

The `setup.bat` (for Windows) and `setup.sh` (for Linux/Mac) scripts are provided to help automate the initial environment configuration, primarily focusing on creating the `.env` file with necessary settings like database credentials and Django secret key.

## Folder Overview

*   [**`/app`**](./app/README.md): Contains the core Django application code.
*   [**`/docs`**](./docs/README.md): Project documentation.
*   [**`/prompts`**](./prompts/README.md): AI prompts for research/generation.
*   [**`/scripts`**](./scripts/README.md): Utility scripts for the project.

## Known Issues

*   **Seeds Tab:** The 'Seeds' tab functionality is currently under development and may not work as expected.

## Author

Created by papakonnekt

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
