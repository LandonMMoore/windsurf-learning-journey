# API Documentation - Government Assistance Workforce Backend

## 1. Introduction

This document provides a comprehensive overview of the API for the Government Assistance Workforce Backend. This enterprise-grade system is designed for creating, managing, and operating sophisticated AI-powered workforce agents.

The API is structured around several core concepts:

*   **Apps**: The central entity representing a configurable workforce agent.
*   **Workforce Builder Components**: Resources that define an app's capabilities, including documents, data sources, tools, and triggers.
*   **Workforce Agent**: The operational instance of an app that processes user queries.
*   **Analytics & Dashboard**: A suite of endpoints for monitoring performance, gathering insights, and generating reports.
*   **Authentication**: A secure OAuth2-based system for managing user access.
*   **Asynchronous Processing**: A robust, scalable architecture using Azure Service Bus for handling long-running tasks.

### 1.1. Authentication

Most endpoints are protected and require a valid JWT `Bearer` token in the `Authorization` header. The authentication flow is based on OAuth2, with endpoints provided to initiate login, handle callbacks, and refresh tokens.

---

## 2. Authentication Endpoints (`/auth`, `/auth-debug`)

These endpoints manage user authentication, authorization, and session management.

### `GET /auth/login`

Initiates the OAuth2 login flow by redirecting the user to the provider's authorization URL.

*   **Authentication**: None
*   **Response**: `302 Found` redirect to the OAuth provider.

### `GET /auth/callback`

Handles the callback from the OAuth provider after user authorization. It processes the authorization code, exchanges it for tokens, and redirects the user to the frontend application with the tokens.

*   **Authentication**: None
*   **Query Parameters**: `code`, `state`
*   **Response**: `302 Found` redirect to the frontend URL with tokens in the query string.

### `GET /auth/refresh`

Refreshes an expired access token using a valid refresh token.

*   **Authentication**: None
*   **Query Parameters**: `exist_refresh_token` (string, required)
*   **Success Response (`200 OK`)**:
    ```json
    {
      "access_token": "new.jwt.access.token",
      "refresh_token": "new.jwt.refresh.token"
    }
    ```
*   **Error Response (`401 Unauthorized`)**: If the refresh token is invalid or not found.

### `GET /auth/logout`

Logs out the user by clearing session information.

*   **Authentication**: None
*   **Success Response (`200 OK`)**:
    ```json
    {
      "message": "Logout successful"
    }
    ```

### `GET /auth/status`

Checks the validity of the current user's authentication token.

*   **Authentication**: Bearer Token
*   **Success Response (`200 OK`)**:
    ```json
    {
      "authenticated": true,
      "user": {
        "email": "user@example.com",
        "role": "ADMIN"
      }
    }
    ```
*   **Error Response (`401 Unauthorized`)**: If the token is invalid.

### `GET /users`

Retrieves a list of all users in the system.

*   **Authentication**: Bearer Token
*   **Success Response (`200 OK`)**:
    ```json
    {
      "users": [
        {
          "id": "user_id_1",
          "email": "user1@example.com",
          "role": "NORMAL"
        },
        {
          "id": "user_id_2",
          "email": "admin@example.com",
          "role": "ADMIN"
        }
      ]
    }
    ```

### `PUT /users/{email}/role`

Updates the role of a specific user.

*   **Authentication**: Bearer Token
*   **Path Parameters**: `email` (string, required)
*   **Request Body**:
    ```json
    {
      "role": "ADMIN"
    }
    ```
*   **Success Response (`200 OK`)**:
    ```json
    {
      "message": "User role updated successfully"
    }
    ```

### `GET /auth-debug/check-token`

A diagnostic endpoint to validate a token and retrieve its decoded payload and associated user information from the database.

*   **Authentication**: Bearer Token
*   **Success Response (`200 OK`)**:
    ```json
    {
      "authenticated": true,
      "token_valid": true,
      "payload": {
        "email": "user@example.com",
        "role": "ADMIN",
        "exp": 1678886400
      },
      "user_info": {
        "exists": true,
        "email": "user@example.com",
        "role_in_db": "ADMIN",
        "is_admin": true
      }
    }
    ```

---

## 3. App Management Endpoints (`/apps`)

Endpoints for managing the core "App" entities.

### `POST /apps`

Creates a new app.

*   **Authentication**: Bearer Token
*   **Request Body**: `AppCreate` schema
    ```json
    {
      "app_name": "My New Assistant",
      "description": "An assistant for public works.",
      "logo": "base64-encoded-image-string"
    }
    ```
*   **Success Response (`200 OK`)**:
    ```json
    {
      "app_id": "new-app-uuid",
      "message": "App created successfully"
    }
    ```

### `GET /apps`

Retrieves a paginated and filterable list of apps accessible to the user.

*   **Authentication**: Bearer Token
*   **Query Parameters**:
    *   `page`: integer, optional
    *   `page_size`: integer, optional
    *   `search`: string, optional
    *   `ordering`: string, optional (e.g., `name,-created_at`)
    *   `name`: string, optional
    *   `is_initialised`: boolean, optional
    *   `created_at_start`: date-time, optional
    *   `created_at_end`: date-time, optional
*   **Success Response (`200 OK`)**: A paginated list of app objects.

### `GET /apps/{app_id}`

Retrieves the complete, aggregated details for a specific app, including its resources, tools, triggers, and instructions.

*   **Authentication**: Bearer Token
*   **Path Parameters**: `app_id` (string, required)
*   **Success Response (`200 OK`)**: A comprehensive JSON object containing all app details.

### `PUT /apps/{app_id}`

Updates the basic information of an existing app.

*   **Authentication**: Bearer Token
*   **Path Parameters**: `app_id` (string, required)
*   **Request Body**: `AppUpdate` schema
    ```json
    {
      "app_name": "Updated Assistant Name",
      "description": "Updated description."
    }
    ```
*   **Success Response (`200 OK`)**:
    ```json
    {
      "app_id": "app-uuid",
      "message": "App updated successfully"
    }
    ```

### `DELETE /apps/{app_id}`

Deletes a specific app and all its associated resources.

*   **Authentication**: Bearer Token
*   **Path Parameters**: `app_id` (string, required)
*   **Success Response (`200 OK`)**:
    ```json
    {
      "message": "App deleted successfully"
    }
    ```

### `GET /apps/{app_id}/public`

Retrieves only the public-facing information about an app, suitable for display without authentication.

*   **Authentication**: None
*   **Path Parameters**: `app_id` (string, required)
*   **Success Response (`200 OK`)**: A subset of the app's data.

### `GET /apps/{app_id}/initialization-status`

Checks if the corresponding workforce agent for the app has been initialized.

*   **Authentication**: Bearer Token
*   **Path Parameters**: `app_id` (string, required)
*   **Success Response (`200 OK`)**:
    ```json
    {
      "app_id": "app-uuid",
      "is_initialized": true
    }
    ```

---

## 4. Workforce Builder Component Endpoints

These endpoints manage the various resources that constitute an app's functionality.

### 4.1. Documents (`/apps-documents`)

*   `POST /{app_id}`: Adds one or more file resources (metadata) to an app.
*   `GET /{app_id}`: Retrieves all document resources for an app.
*   `PUT /{app_id}`: Replaces all existing document resources with a new set.
*   `DELETE /{app_id}/{file_id}`: Deletes a specific document resource.

### 4.2. Local Files (`/apps-localdocs`)

*   `POST /{app_id}`: Uploads one or more physical files, saves their content, and creates metadata records.
*   `GET /{app_id}`: Retrieves metadata for all local files associated with an app.
*   `DELETE /{app_id}/{file_id}`: Deletes a specific local file record.
*   `DELETE /{app_id}`: Deletes all local file records for an app.

### 4.3. Containers (`/apps-containers`)

*   `POST /{app_id}`: Adds one or more folder resources (containers) to an app.
*   `GET /{app_id}`: Retrieves all container resources for an app.
*   `PUT /{app_id}`: Replaces all existing container resources with a new set.
*   `DELETE /{app_id}/{folder_id}`: Deletes a specific container resource.

### 4.4. Data Sources (`/apps-sources`)

*   `POST /{app_id}`: Adds multiple data sources (e.g., SharePoint sites) to an app.
*   `GET /{app_id}`: Retrieves all data sources for an app.
*   `PUT /{app_id}`: Replaces all existing data sources with a new set.
*   `DELETE /{app_id}/{source_type}`: Deletes a data source of a specific type.

### 4.5. Tools (`/apps-tools`)

*   `POST /{app_id}`: Adds multiple tools (e.g., `calculator`, `web_search`) to an app.
*   `GET /{app_id}`: Retrieves all tools enabled for an app.
*   `PUT /{app_id}`: Replaces all existing tools with a new set.
*   `DELETE /{app_id}/{tool_type}`: Deletes a specific tool.

### 4.6. Triggers (`/apps-trigger`)

*   `POST /{app_id}`: Creates or updates the conversational trigger (e.g., welcome prompt) for an app.
*   `GET /{app_id}`: Retrieves the trigger for an app.
*   `PUT /{app_id}`: Updates the trigger for an app.
*   `DELETE /{app_id}`: Deletes the trigger for an app.

### 4.7. Instructions (`/apps-instruction`)

*   `POST /{app_id}`: Adds a system-level instruction or persona for the app's agent.
*   `GET /{app_id}`: Retrieves the instruction for an app.
*   `PUT /{app_id}`: Updates the instruction for an app.
*   `DELETE /{app_id}`: Deletes the instruction for an app.

### 4.8. Publishing (`/apps-publish`)

*   `POST /{app_id}`: Publishes an app with specific visibility settings (e.g., `public`, `private`, `team`).
*   `GET /`: Retrieves a list of published apps visible to the requesting user.
*   `GET /{app_id}`: Retrieves the publishing status and settings for a specific app.
*   `PUT /{app_id}`: Updates the publishing settings for an app.
*   `PATCH /{app_id}`: Partially updates the publishing settings.
*   `DELETE /{app_id}`: Unpublishes an app, making it private.

---

## 5. SharePoint Integration Endpoints (`/service/sharepoint`)

### `GET /service/sharepoint/structure`

Retrieves the folder and file structure of the authenticated user's SharePoint environment. This is used to allow users to select SharePoint resources as data sources for their apps.

*   **Authentication**: Bearer Token
*   **Success Response (`200 OK`)**: A hierarchical JSON object representing the SharePoint structure.

---

## 6. Workforce Agent Operation Endpoints (`/workforce`)

These endpoints are for interacting with the live, operational workforce agents.

### 6.1. V1: Synchronous / Streaming Endpoints

#### `POST /initialise-workforce-agent/{app_id}`

Initializes the backend components for a workforce agent, making it ready to process queries.

*   **Authentication**: Bearer Token
*   **Path Parameters**: `app_id` (string, required)
*   **Success Response (`200 OK`)**:
    ```json
    {
      "message": "Agent for app_id initialized successfully"
    }
    ```

#### `POST /operate-workforce-agent/{app_id}`

Sends a query to a workforce agent and receives a streaming response. This is the primary endpoint for authenticated, real-time interaction.

*   **Authentication**: Bearer Token
*   **Path Parameters**: `app_id` (string, required)
*   **Request Body**: `UserQuery` schema
    ```json
    {
      "query": "What are the requirements for a building permit?"
    }
    ```
*   **Response**: A `text/event-stream` response with JSON chunks.
    ```
    data: {"chunk": "To apply for a building permit"}
    data: {"chunk": ", you will need..."}
    ```

#### `POST /operate-workforce-agent-public/{app_id}`

Operates a public-facing workforce agent. Similar to the authenticated endpoint but does not require a token.

*   **Authentication**: None
*   **Response**: A `text/event-stream` response.

#### `DELETE /cleanup-agent/{app_id}`

Deletes the backend components of a workforce agent.

*   **Authentication**: Bearer Token
*   **Path Parameters**: `app_id` (string, required)
*   **Success Response (`200 OK`)**:
    ```json
    {
      "message": "Agent cleaned up successfully"
    }
    ```

### 6.2. V2: Asynchronous Endpoints (Azure Service Bus)

This set of endpoints provides a more robust and scalable way to interact with agents for tasks that can be processed asynchronously.

#### `POST /v2/operate-workforce-agent-async/{app_id}`

Submits a query to an agent for asynchronous processing. The request is queued in Azure Service Bus, and the API returns immediately with a tracking ID.

*   **Authentication**: Bearer Token
*   **Path Parameters**: `app_id` (string, required)
*   **Request Body**: `UserQuery` schema
*   **Success Response (`200 OK`)**:
    ```json
    {
      "message_id": "message-uuid",
      "correlation_id": "correlation-uuid",
      "status": "queued",
      "estimated_processing_time": 30,
      "tracking_url": "/workforce/v2/status/correlation-uuid"
    }
    ```

#### `GET /v2/status/{correlation_id}`

Checks the status of an asynchronously processed message. Supports long-polling.

*   **Authentication**: Bearer Token
*   **Path Parameters**: `correlation_id` (string, required)
*   **Query Parameters**:
    *   `wait`: boolean, optional (If true, holds the connection until the job is complete or timeout is reached).
    *   `timeout`: integer, optional (Max seconds to wait, up to 30).
*   **Success Response (`200 OK`)**:
    ```json
    {
      "message_id": "message-uuid",
      "correlation_id": "correlation-uuid",
      "status": "completed",
      "progress_percentage": 100,
      "processing_time_ms": 15234,
      "response_content": {
        "response": "Here is the final answer...",
        "completed_at": "2025-08-11T10:30:00Z"
      },
      "error_message": null,
      "created_at": "2025-08-11T10:29:45Z",
      "updated_at": "2025-08-11T10:30:00Z"
    }
    ```

#### `POST /v2/status/batch`

Retrieves the status for a batch of up to 20 correlation IDs in a single request.

*   **Authentication**: Bearer Token
*   **Request Body**:
    ```json
    [
      "correlation-uuid-1",
      "correlation-uuid-2"
    ]
    ```
*   **Success Response (`200 OK`)**: A list of status objects, one for each requested ID.

#### `GET /v2/health/service-bus`

Provides health status and queue statistics for the underlying Azure Service Bus.

*   **Authentication**: Bearer Token
*   **Success Response (`200 OK`)**:
    ```json
    {
      "status": "healthy",
      "queue_name": "chat-messages",
      "active_message_count": 5,
      "dead_letter_message_count": 0
    }
    ```

---

## 7. Analytics & Dashboard Endpoints (`/analytics`, `/dashboard`)

A comprehensive suite of endpoints for data analysis and visualization.

### 7.1. Analytics Endpoints (`/analytics`)

*   `POST /feedback`: Records user feedback (like/dislike) for a specific agent response.
*   `GET /agent/{agent_id}`: Retrieves raw analytics records for a specific agent.
*   `GET /performance`: Gets aggregated performance analytics (e.g., response times, query counts) with powerful date and department filters.
*   `GET /apps/emerging-topic`: Identifies topics with recent growth in query volume.
*   `GET /apps/query-forecasting`: Provides actual vs. AI-predicted query volumes.
*   `GET /apps/topic-evolution`: Returns data formatted for a topic evolution bubble chart.
*   `GET /department-counts`: Shows query counts broken down by department.
*   `GET /heatmap`: Provides data for a heatmap visualizing usage patterns by day and time.
*   `GET /recommendations`: Returns a static list of AI-generated recommendations for improving agent performance or knowledge base content.
*   `GET /diagnostics/performance-metrics-count`: An admin-only endpoint to get raw counts from the performance metrics table.

### 7.2. Dashboard Endpoints (`/dashboard`)

These endpoints provide pre-aggregated data tailored for a frontend dashboard. They often wrap the more granular `/analytics` endpoints.

*   `GET /overview`: Retrieves key performance indicators (KPIs) for a high-level dashboard view.
*   `GET /performance`: Gets performance metrics formatted for time-series charts.
*   `GET /agents`: Retrieves a list of agents accessible to the user, with optional summary metrics.
*   `GET /departments`: Gets an analytics breakdown by department.
*   `GET /topics`: Retrieves trending topics and evolution data.
*   `GET /usage-heatmap`: Gets data formatted for a usage heatmap component.
*   `GET /recommendations`: Retrieves AI-generated recommendations.
*   `GET /export`: Allows exporting of various dashboard data types (`overview`, `performance`, etc.) to formats like JSON, CSV, or Excel.
*   `GET /health`: A simple health check for the dashboard API service.

---

## 8. LLM Guard Security Endpoints (`/llm-guard`)

Endpoints for monitoring the prompt injection security layer.

### `GET /metrics`

Retrieves performance and telemetry metrics for the LLM-Guard service, including total scans, cache hits, and average scan time.

*   **Authentication**: Bearer Token
*   **Success Response (`200 OK`)**: A JSON object with detailed metrics and configuration settings.

### `POST /metrics/reset`

Resets the LLM-Guard metrics counters.

*   **Authentication**: Bearer Token
*   **Success Response (`200 OK`)**:
    ```json
    {
      "message": "Metrics reset successfully"
    }
    ```

### `POST /cache/clear`

Clears the LLM-Guard's cache of previously scanned prompts.

*   **Authentication**: Bearer Token
*   **Success Response (`200 OK`)**:
    ```json
    {
      "message": "Cache cleared successfully"
    }
    ```

### `GET /health`

A public-facing health check for the LLM-Guard service.

*   **Authentication**: None
*   **Success Response (`200 OK`)**:
    ```json
    {
      "status": "healthy",
      "service": "llm-guard",
      "total_scans": 1052,
      "average_scan_time_ms": 15.3
    }
    ```
