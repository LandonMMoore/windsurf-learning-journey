# Documentation: `src/core` Module

## **1. Introduction**

This document provides a comprehensive, enterprise-grade analysis of the `src/core` module for the **WorkForce Agent** backend application. The `core` module represents the architectural backbone of the application, providing critical infrastructure for configuration, database connectivity, dependency injection, authentication, authorization, and robust error handling.

The design philosophy of the `core` module emphasizes security, scalability, and maintainability through the adoption of industry-best practices and design patterns. This documentation serves as a technical reference for developers and architects working with the system.

## **2. Architectural Pillars**

The `src/core` module is engineered around several key architectural concepts:

*   **Layered Architecture:** A strict separation of concerns is maintained between the API, service, and repository layers. The `core` module provides the foundational components upon which these layers are built.
*   **Dependency Injection (DI):** The `dependency-injector` library is leveraged to manage object lifecycles and dependencies. This decouples components, making the system more modular, testable, and maintainable. The central DI container is defined in this module.
*   **Centralized Configuration:** A secure and flexible configuration management system is implemented using `pydantic-settings` and Azure Key Vault. This allows for environment-specific settings and a single source of truth for configuration.
*   **Repository Pattern:** Data access is abstracted through the repository pattern, isolating the business logic from the data persistence technology (SQLAlchemy).
*   **Robust Exception Handling:** A custom, hierarchical exception framework is established to ensure that errors are handled gracefully and consistently. Specialized handlers map low-level library exceptions to meaningful, application-specific errors.
*   **JWT-based Authentication:** Secure, stateless authentication is provided using JSON Web Tokens (JWT), with a clear separation between access and refresh tokens.

## **3. Module Deep Dive**

This section provides a detailed file-by-file breakdown of the `src/core` module.

### `config.py`

*   **Purpose:** Centralizes all application configuration, from database connection strings to external API keys.
*   **Key Features:**
    *   **Azure Key Vault Integration:** Securely loads secrets at runtime from Azure Key Vault using `DefaultAzureCredential`. This avoids storing sensitive information in code or environment files in production.
    *   **Environment-Specific Configurations:** Defines distinct classes (`DevelopmentConfigs`, `TestConfigs`, `ProductionConfigs`) that inherit from a base `Configs` class, allowing for tailored settings for each environment.
    *   **Type-Safe Settings:** Uses `pydantic-settings` to define a typed configuration schema, ensuring that all required settings are present and of the correct type at application startup.
    *   **Dynamic Configuration:** Constructs database connection strings and other values dynamically from the loaded secrets.
    *   **Cached Access:** The `get_configs()` function is decorated with `@lru_cache`, ensuring that the configuration is loaded only once and accessed efficiently throughout the application.

### `database.py`

*   **Purpose:** Manages the application's database connection, engine, and session lifecycle.
*   **Key Components:**
    *   **`BaseModel`:** A declarative base class for all SQLAlchemy models. It includes a `declared_attr` to automatically generate table names based on the class name, promoting consistency.
    *   **`Database` Class:**
        *   Initializes the SQLAlchemy `create_engine` with a connection pool (`QueuePool`) optimized for a production environment. Settings include `pool_pre_ping` to prevent stale connections, `pool_recycle` to manage connection lifespan, and increased pool sizes.
        *   Configures a `scoped_session` factory to ensure that each thread or request gets its own unique `Session` object.
        *   Provides a `session()` context manager (`@contextmanager`) that encapsulates the session lifecycle: it yields a new session, commits on success, rolls back on exception, and ensures the session is closed, preventing resource leaks.

### `container.py`

*   **Purpose:** Implements the Dependency Injection (DI) container for the entire application. This is the heart of the application's loose-coupling strategy.
*   **Key Features:**
    *   **Centralized Dependency Management:** Defines how all major components (repositories, services) are instantiated and wired together.
    *   **Providers:** Uses different `dependency-injector` providers:
        *   `providers.Singleton`: For the `Database` class, ensuring only one instance exists per application process.
        *   `providers.Factory`: For repositories and services, creating a new instance every time one is requested. This is suitable for stateless components.
        *   `providers.Callable`: To provide the database session factory method to repositories.
    *   **Wiring:** The `wiring_config` specifies which modules (primarily API endpoints) will have their dependencies automatically injected by the container. This allows endpoint functions to receive service instances via `Depends()`.

### `auth_functions.py`

*   **Purpose:** Contains standalone, reusable functions for core authorization and user retrieval logic.
*   **Key Functions:**
    *   `update_user_refresh_token(user_id, refresh_token, db)`: Asynchronously updates the `refresh_token` for a given user in the database.
    *   `get_user_by_id(user_id, db)`: Retrieves a user by their primary key.
    *   `get_user_by_email(email, db)`: Retrieves a user by their email address.
    *   `get_user_from_auth(email, db)`: Retrieves a user by joining the `User` and `IntegrationAuth` tables.
    *   `get_all_users(db)`: Retrieves all users.
    *   `verify_user_can_access_app(app_id, user_email, db)`: A critical authorization function. It checks if a user can access a given app by verifying ownership or checking against the app's publishing rules (e.g., public, all teammates, specific teammates).
    *   `is_admin_user(role)`: A simple utility to check if a user's role grants administrative privileges.

### `jwt_auth.py`

*   **Purpose:** Manages the creation, validation, and lifecycle of JSON Web Tokens (JWTs) for user authentication.
*   **Key Features:**
    *   **Token Creation:**
        *   `create_jwt_token(data, expires_delta, token_use)`: A generic, secure token factory. It adds standard claims like `exp` (expiration), `iat` (issued at), and `jti` (JWT ID for uniqueness/revocation). It also adds a custom `token_use` claim to distinguish between token types.
        *   `create_access_token(data)`: Creates a short-lived access token.
        *   `create_refresh_token(user_id, db)`: Creates a long-lived refresh token and persists it to the user's record in the database.
    *   **Token Validation:**
        *   `get_data(token, expected_token_use)`: A FastAPI dependency that decodes and rigorously validates a JWT. It checks the signature, expiration, `token_use` claim, and `iat` timestamp to prevent misuse.
    *   **Token Management:**
        *   `invalidate_refresh_token(user_id, db)`: Invalidates a refresh token by removing it from the database.
        *   `check_refresh_token(user_id, refresh_token, db)`: Securely compares a provided refresh token against the one stored in the database.
    *   **Security:** Uses `hmac.compare_digest` for comparing tokens to mitigate timing attacks.

### `token_security.py`

*   **Purpose:** Provides a security layer for storing and managing sensitive OAuth tokens from third-party integrations (e.g., Azure, SharePoint).
*   **Key Features:**
    *   **Symmetric Encryption:** Uses the `cryptography` library's Fernet implementation to encrypt and decrypt OAuth access and refresh tokens before they are stored in the `IntegrationAuth` table. The encryption key is securely loaded from configuration.
    *   **Token Persistence:** `encrypt_token_data(...)` handles the logic of encrypting and saving tokens for a user and provider.
    *   **Automatic Token Refresh:**
        *   `update_access_token(...)`: Contains the logic to use a stored (and decrypted) refresh token to request a new access token from the OAuth provider's token endpoint.
        *   `get_token_info(db, user_id, provider)`: This is the primary function used by services. It retrieves a user's token, checks if it's expired, and if so, automatically triggers the refresh flow before returning a valid access token.

### `dependencies/auth.py`

*   **Purpose:** Defines a set of reusable FastAPI dependencies to protect API endpoints and provide them with the current user's context.
*   **Key Dependencies:**
    *   `get_current_user(token)`: The core authentication dependency. It extracts the bearer token, uses `jwt_auth.get_data` to validate it, and retrieves the corresponding `User` object from the database.
    *   `get_current_active_user(current_user)`: A dependency that chains off `get_current_user` and adds a check to ensure the user's account is active.
    *   `require_admin_user(current_user)`: Restricts endpoint access to users with `ADMIN` or `SUPER_ADMIN` roles.
    *   `get_optional_current_user(authorization)`: For endpoints that have optional authentication. It attempts to get the user but returns `None` instead of raising an error if authentication fails.
    *   `check_agent_access(user, agent_id)`: A placeholder function to check if a user has access to a specific agent.

### `exceptions.py`

*   **Purpose:** Defines a comprehensive, hierarchical set of custom exception classes for the application. This promotes consistent error handling.
*   **Key Hierarchy:**
    *   **`BaseApplicationError`**: The root of all custom exceptions. It includes a standard structure with a message, error code, context, correlation ID, and timestamp.
    *   **Category-Based Errors:**
        *   `BusinessLogicError`: For errors related to business rule violations.
        *   `ExternalServiceError`: Base for errors from third-party services (`AzureServiceError`, `CosmosDBError`, `LLMServiceError`).
        *   `DataAccessError`: Base for persistence layer errors (`DatabaseError`, `FileSystemError`).
    *   **HTTP-Mapped Exceptions:** Provides simple wrappers around `fastapi.HTTPException` for common HTTP statuses like `NotFoundError`, `AuthError`, `ValidationError`, etc., to be used directly in the service or API layer.

### `exception_handlers.py`

*   **Purpose:** Implements global exception handlers for the FastAPI application, ensuring all uncaught exceptions are translated into a standardized JSON error response.
*   **Key Handlers:**
    *   `create_error_response(...)`: A utility function to build the consistent JSON error structure.
    *   `request_validation_exception_handler`: Catches `RequestValidationError` from Pydantic and formats the response to clearly indicate which fields failed validation.
    *   `sqlalchemy_exception_handler`: Catches generic `SQLAlchemyError`s.
    *   **Custom Exception Handlers:** Provides specific handlers for the custom exceptions defined in `exceptions.py` (e.g., `duplicated_error_handler`, `not_found_error_handler`), mapping them to the appropriate HTTP status codes (400, 404, etc.).
    *   `global_exception_handler`: A catch-all handler for any unexpected `Exception`, preventing stack traces from leaking to the client and returning a generic 500 error.

### `azure_exceptions.py` & `database_exceptions.py` & `llm_exceptions.py`

*   **Purpose:** These modules provide specialized, decorator-based exception handling for interactions with external systems (Azure, Database, LLMs).
*   **Key Features:**
    *   **Exception Mapping:** Each module contains a `map_*_exception` function that takes a low-level exception from an external library (e.g., `azure.core.exceptions.ResourceNotFoundError`, `sqlalchemy.exc.IntegrityError`) and translates it into a corresponding high-level application exception from `exceptions.py`.
    *   **Decorator-Based Handling:** They expose decorators (`@handle_azure_errors`, `@handle_database_errors`, `@handle_llm_errors`) that can be applied to repository or service methods. These decorators wrap the function call in a `try...except` block, automatically catch the low-level exceptions, map them, and re-raise the application-level exception. This keeps the business logic clean of boilerplate error-handling code.
    *   **Context Extraction:** The handlers attempt to extract useful context from the original exception (e.g., the name of a database constraint that was violated, the name of an Azure resource that was not found) and attach it to the new application exception.

### `llm_guard_config.py` & `prompt_config.py`

*   **Purpose:** These modules manage the configuration and schemas related to Large Language Models (LLMs).
*   **`llm_guard_config.py`:**
    *   **Purpose:** Configures `LLM-Guard`, a security tool for detecting prompt injection and other malicious inputs.
    *   **Features:** Defines different `SecurityMode`s (Development, Staging, Production) with varying strictness thresholds. Allows for configuration via environment variables and provides logic to bypass checks for trusted users (e.g., admins).
*   **`prompt_config.py`:**
    *   **Purpose:** Defines a structured, Pydantic-based schema for managing prompt templates.
    *   **Features:**
        *   `PromptConfig`: The main model defining a prompt's name, version, template content, and a list of `PromptVariable`s.
        *   `PromptVariable`: Defines the expected variables in a template, including their type, whether they are required, and default values.
        *   This structured approach enables validation, versioning, and easier management of the prompts used across the application.

### `token_testing.py`

*   **Purpose:** Provides a utility function for validating a SharePoint access token. This appears to be a debugging or testing endpoint.
*   **Key Function:**
    *   `validate_sharepoint_token(token)`: An async function that simulates a complete authentication and validation flow. It gets the current user, retrieves their stored SharePoint OAuth token (using `get_token_info`), and then makes a test call to the Microsoft Graph API (`/v1.0/me`) to verify that the token is active and valid.
