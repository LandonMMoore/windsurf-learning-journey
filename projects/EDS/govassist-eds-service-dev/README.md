# EDS - Electronic Database System


## 📋 Table of Contents

- [Features](#-features)
- [Getting Started](#-getting-started)
- [Folder Structure](#-folder-structure)
- [API Documentation](#-Interactive-documentation)
- [Database Management](#-database-management)
- [Deployment](#-deployment)
- [Contributing](#-contributing)


## ✨ Features

### Core Functionality
- **PAR Management**: Comprehensive PAR (Project Application Repository) management system
- **Budget Analysis**: Advanced budget tracking and analysis with multiple fund types
- **Dashboard System**: Customizable dashboards with widgets and favorites
- **AI Assistant**: Intelligent query processing with chat history using LangChain
- **Report Generation**: Automated report creation and management

### AI & Analytics
- **Natural Language Queries**: Process complex queries using AI models
- **Chat History**: Persistent conversation management
- **OpenAI & Anthropic Integration**: Multi-model AI support
- **RAG (Retrieval-Augmented Generation)**: Enhanced query processing

## 🚀 Getting Started

### Prerequisites

- Python 3.9+ (Preferred: 3.13.2)
- Poetry (for dependency management)
- Git (for version control)
- SQL Server or PostgreSQL database
- Docker and Docker Compose

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd govassist-eds-service
   ```
2. **Activate the virtual environment**
   ```bash
   poetry shell
   ```
3. **Install dependencies**
   ```bash
   poetry install
   ```


4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start development services**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start the application**
   ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
    or
    ```bash
    fastapi dev main.py
   ```
   

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.




## 📁 Folder Structure

```
govassist-eds-service/
├── src/                          # Main application source
│   ├── api/                      # API layer
│   │   ├── endpoints/            # API route handlers
│   │   └── routes.py             # Route registration
│   ├── core/                     # Core application logic
│   │   ├── config.py             # Configuration management
│   │   ├── container.py          # Dependency injection
│   │   ├── exceptions.py         # Custom exceptions
│   │   └── middleware.py         # Custom middleware
│   ├── model/                    # Database models
│   │   ├── base_model.py         # Base model class
│   │   ├── par_model.py          # PAR entity model
│   │   └── ...                   # Other entity models
│   ├── schema/                   # Pydantic schemas
│   │   ├── base_schema.py        # Base schema class
│   │   ├── par_schema.py         # PAR schemas
│   │   ├── dashboard_schema.py   # Dashboard schemas
│   │   └── ...                   # Other schemas
│   ├── services/                 # Business logic services
│   │   ├── base_service.py       # Base service class
│   │   ├── par_service.py        # PAR business logic
│   │   ├── dashboard_service.py  # Dashboard business logic
│   │   └── ...                   # Other services
│   ├── repository/               # Data access layer
│   │   ├── base_repository.py    # Base repository class
│   │   ├── par_repository.py     # PAR data access
│   │   ├── dashboard_repository.py # Dashboard data access
│   │   └── ...                   # Other repositories
│   ├── elasticsearch/            # Elasticsearch integration
│   │   ├── service.py            # ES service
│   │   ├── client.py             # ES client
│   │   ├── models.py             # ES models
│   │   ├── constants.py          # ES constants
│   │   ├── aggregation_utils.py  # Aggregation utilities
│   │   ├── filter_utils.py       # Filter utilities
│   │   ├── group_by.py           # Group by utilities
│   │   └── mappings/             # ES index mappings
│   ├── mongodb/                  # MongoDB integration
│   │   ├── client.py             # MongoDB client
│   │   ├── collections.py        # Collection definitions
│   │   ├── chat_services.py      # Chat history services
│   │   └── report_services.py    # Report services
│   ├── agents/                   # AI agents and RAG
│   │   ├── clarify_agent.py      # Query clarification agent
│   │   ├── analyzer_agent.py     # Data analysis agent
│   │   ├── report_generation_manager_agent.py # Report generation
│   │   ├── prompts/              # AI prompt templates
│   │   ├── rag_query/            # RAG query processing
│   │   ├── tools/                # AI agent tools
│   │   └── report_generator/     # Report generation tools
│   ├── util/                     # Utility functions
│   │   ├── es_agent.py           # Elasticsearch agent utilities
│   │   ├── elasticsearch.py      # ES utilities
│   │   ├── chart_helpers.py      # Chart generation helpers
│   │   ├── send_email.py         # Email utilities
│   │   ├── validators.py         # Validation utilities
│   │   └── ...                   # Other utilities
│   ├── main.py                   # Application entry point
│   ├── __init__.py               # Package initialization
│   └── Sample_Budget.xlsx        # Sample data file
├── migrations/                   # Database migrations
├── tests/                        # Test suite
├── docker-compose.dev.yml        # Development services
├── Dockerfile                    # Production container
├── pyproject.toml               # Project configuration
├── alembic.ini                  # Migration configuration
└── README.md                    # This file
```


### Interactive Documentation

Once the application is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🗄 Database Management

### Running Migrations

To understand and manage database migrations, please refer to the documentation provided in:
migrations/README.md

### Database Connections

The application supports multiple database engines:

- **SQL Server** (default): Uses ODBC Driver 18
- **PostgreSQL**: Native psycopg2 support


Database connection is configured via environment variables and automatically mapped based on the `ENV` setting.


## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature/fix branch**
   ```bash
   git checkout -b feat/your-feature-name
   ```
   or
      ```bash
   git checkout -b fix/your-fix-name
   ```
3. **Make your changes**
4. **Run tests and linting**
   ```bash
    ruff check --fix . && isort . && black .
   ```
5. **Commit your changes**
   ```bash
   git commit -m "feat: add your feature description"
   ```
   or
    ```bash
   git commit -m "fix: add your feature description"
   ```
6. **Push to your branch**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write comprehensive docstrings
- Add unit tests for new functionality
- Update documentation as needed

### Code Quality

The project uses several tools to maintain code quality:

```bash
# Format code
poetry run black src/

# Sort imports
poetry run isort src/

# Lint code
poetry run ruff check src/

# Fix linting issues
poetry run ruff check --fix src/
```


