# Services Documentation

This document provides a detailed overview of the services within the `govt-assist-workforce-backend` application. Each service is responsible for a specific set of functionalities, from handling analytics and user authentication to managing workforce agents and processing messages.

## Table of Contents

1.  [Analytics Service](#analytics-service)
2.  [App Service](#app-service)
3.  [Auth Service](#auth-service)
4.  [Container Service](#container-service)
5.  [Dashboard Service](#dashboard-service)
6.  [Data Source Service](#data-source-service)
7.  [Document Service](#document-service)
8.  [Instruction Service](#instruction-service)
9.  [LLM Guard Service](#llm-guard-service)
10. [Local Docs Service](#local-docs-service)
11. [Message Processor Service](#message-processor-service)
12. [Prompt Integrated Topic Service](#prompt-integrated-topic-service)
13. [Publish App Service](#publish-app-service)
14. [Response Consumer Service](#response-consumer-service)
15. [Service Bus Service](#service-bus-service)
16. [SharePoint Service](#sharepoint-service)
17. [Tool Service](#tool-service)
18. [Topic Service](#topic-service)
19. [Topic Service (Migrated)](#topic-service-migrated)
20. [Trigger Service](#trigger-service)
21. [Workforce Agent Service](#workforce-agent-service)
22. [Workforce Agent Service (Migrated)](#workforce-agent-service-migrated)

---

## Analytics Service

The `AnalyticsService` is responsible for handling all logic related to analytics, including user feedback, agent performance metrics, and generating analytics summaries and trends.

### Functions

#### `verify_user_can_access_agent(agent_id: str, user_email: str, user_role: str = "NORMAL") -> bool`

Verifies if a user has permission to access analytics for a specific agent.

-   **agent_id**: The ID of the agent/app.
-   **user_email**: The email of the user making the request.
-   **user_role**: The role of the user (NORMAL, ADMIN, SUPER_ADMIN).
-   **Returns**: `True` if the user has access, `False` otherwise.

#### `record_feedback(analytics_data: AnalyticsCreateRequest, agent_id: str, user_email: str) -> AnalyticsResponse`

Records user feedback for a chatbot response.

-   **analytics_data**: The analytics data containing feedback information.
-   **agent_id**: The ID of the agent.
-   **user_email**: The email of the user.
-   **Returns**: The created analytics record.
-   **Raises**: `ValueError` if the agent_id is invalid or data validation fails.

#### `get_agent_analytics(agent_id: str, user_email: str, user_role: str = "NORMAL", limit: int = 100, offset: int = 0) -> List[AnalyticsResponse]`

Gets analytics records for a specific agent.

-   **agent_id**: The ID of the chatbot agent.
-   **user_email**: The email of the user making the request.
-   **user_role**: The role of the user.
-   **limit**: Maximum number of records to return.
-   **offset**: Number of records to skip.
-   **Returns**: A list of analytics records, or an empty list if the user has no access.

#### `get_analytics_summary(agent_id: str) -> dict`

Gets summary statistics for an agent's analytics.

-   **agent_id**: The ID of the chatbot agent.
-   **Returns**: A dictionary with summary statistics.

#### `get_feedback_trends(agent_id: str, days: int = 30) -> List[dict]`

Gets feedback trends over time for an agent.

-   **agent_id**: The ID of the chatbot agent.
-   **days**: Number of days to look back.
-   **Returns**: A list of daily feedback trends.

#### `delete_analytics_record(record_id: str) -> bool`

Deletes a specific analytics record.

-   **record_id**: The ID of the analytics record to delete.
-   **Returns**: `True` if deletion was successful.

#### `update_analytics_record(record_id: str, update_data: dict) -> AnalyticsResponse`

Updates an existing analytics record.

-   **record_id**: The ID of the analytics record to update.
-   **update_data**: A dictionary containing fields to update.
-   **Returns**: The updated analytics record.

#### `log_performance_metrics(agent_id: str, query: str, response: str, response_time: float, department: str = None) -> Optional[str]`

Logs agent performance metrics.

-   **agent_id**: The ID of the chatbot agent.
-   **query**: The user query.
-   **response**: The agent response.
-   **response_time**: Response time in seconds.
-   **department**: The department associated with the query (optional).
-   **Returns**: The created record's `query_id` or `None` if it failed.

#### `get_performance_analytics(user_email: str, user_role: str = "NORMAL", agent_id: Optional[str] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, departments: Optional[List[str]] = None) -> dict`

Gets performance analytics with date range and department filters.

-   **user_email**: The email of the user making the request.
-   **user_role**: The role of the user.
-   **agent_id**: The ID of the chatbot agent (optional).
-   **start_date**: Start date for analysis.
-   **end_date**: End date for analysis.
-   **departments**: List of department filters (optional).
-   **Returns**: A dictionary with performance analytics data.

#### `get_daily_query_data(user_email: str, start_date: datetime, end_date: datetime, user_role: str = "NORMAL", agent_id: Optional[str] = None, departments: Optional[List[str]] = None) -> List[Dict]`

Gets daily query counts from the `AgentPerformanceMetrics` table with filters.

-   **user_email**: The email of the user making the request.
-   **start_date**: Start date for analysis.
-   **end_date**: End date for analysis.
-   **user_role**: The role of the user.
-   **agent_id**: The ID of the chatbot agent (optional).
-   **departments**: List of department filters (optional).
-   **Returns**: A list of daily query counts.

#### `get_query_count_for_period(start_date: datetime, end_date: datetime, agent_id: Optional[str] = None) -> int`

Gets the total query count for a specific time period from `AgentPerformanceMetrics`.

-   **start_date**: Start date for analysis.
-   **end_date**: End date for analysis.
-   **agent_id**: The ID of the chatbot agent (optional).
-   **Returns**: The total query count.

#### `get_usage_heatmap_data(user_email: str, start_date: datetime, end_date: datetime, user_role: str = "NORMAL", agent_id: Optional[str] = None, departments: Optional[List[str]] = None) -> Dict`

Generates chatbot usage heatmap data.

-   **user_email**: The email of the user making the request.
-   **start_date**: Start date for analysis.
-   **end_date**: End date for analysis.
-   **user_role**: The role of the user.
-   **agent_id**: Optional agent filter.
-   **departments**: Optional list of department filters.
-   **Returns**: A dictionary with heatmap matrix data and metadata.

#### `update_recommendation_status(rec_id: str, status: str) -> bool`

Updates the status of a recommendation.

-   **rec_id**: The ID of the recommendation.
-   **status**: The new status.
-   **Returns**: `True` if the update was successful.

#### `should_refresh_recommendations(agent_id: str, department: str = None) -> bool`

Checks if recommendations for a specific agent are older than 2 days.

-   **agent_id**: The ID of the agent.
-   **department**: The department (optional).
-   **Returns**: `True` if recommendations should be refreshed.

#### `get_active_recommendations(agent_id: str = None, department: str = None) -> List`

Gets all open recommendations with optional filtering.

-   **agent_id**: The ID of the agent (optional).
-   **department**: The department (optional).
-   **Returns**: A list of active recommendations.

#### `clear_old_recommendations(agent_id: str, department: str = None)`

Removes old recommendations for a specific agent when generating new ones.

-   **agent_id**: The ID of the agent.
-   **department**: The department (optional).

#### `get_recommendations(agent_id: str)`

Gets recommendations for a specific agent, auto-refreshing if needed.

-   **agent_id**: The ID of the agent.
-   **Returns**: A dictionary with recommendations and metadata.

#### `get_recommendations_by_departments(departments: List[str])`

Gets all recommendations for specific departments.

-   **departments**: A list of department names.
-   **Returns**: A dictionary with recommendations and metadata.

#### `get_recommendations_with_filters(agent_id: str = None, departments: Optional[List[str]] = None)`

Gets recommendations with both agent and department filters.

-   **agent_id**: The ID of the agent (optional).
-   **departments**: A list of department names (optional).
-   **Returns**: A dictionary with recommendations and metadata.

---

## App Service

The `AppService` handles the core logic for managing applications (agents), including creation, retrieval, updates, and deletion.

### Functions

#### `check_app_authorization(app_id: str, user_email: str, db)`

Checks if a user has access to the app.

-   **app_id**: The app ID to check access for.
-   **user_email**: The email of the user requesting access.
-   **db**: The database session.
-   **Raises**: `HTTPException` (403) if the user is not authorized, or (404) if the app is not found.

#### `create_app(app_data) -> Dict[str, Any]`

Creates a new app after checking if the name already exists.

-   **app_data**: The app creation data object.
-   **Returns**: A dictionary with the `app_id` and a success message.
-   **Raises**: `HTTPException` (400) if an app with the same name already exists.

#### `get_all_apps(...) -> Dict[str, Any]`

Gets a paginated, filtered list of apps with multi-column sorting.

-   **search**: Search term to filter apps.
-   **ordering**: List of sort criteria.
-   **filter_by**: Field to filter by (legacy).
-   **filter_value**: Value to filter by (legacy).
-   **page**: Page number.
-   **page_size**: Number of items per page.
-   **searchable_fields**: Fields to search in.
-   **email**: Filter by email.
-   **name**: Filter by name.
-   **is_initialised**: Filter by initialization status.
-   **created_at_start**: Filter by creation date (start).
-   **created_at_end**: Filter by creation date (end).
-   **Returns**: A dictionary with apps and pagination metadata.

#### `get_app_by_id(app_id: str) -> Dict[str, Any]`

Gets app details by ID.

-   **app_id**: The app ID.
-   **Returns**: App details.
-   **Raises**: `HTTPException` (404) if the app is not found.

#### `update_app(app_id: str, app_data) -> Dict[str, str]`

Updates an existing app.

-   **app_id**: The app ID to update.
-   **app_data**: The update data.
-   **Returns**: A success message.
-   **Raises**: `HTTPException` (404) if the app is not found.

#### `delete_app(app_id: str) -> Dict[str, str]`

Deletes an app by ID.

-   **app_id**: The app ID to delete.
-   **Returns**: A success message.
-   **Raises**: `HTTPException` (404) if the app is not found, or (500) if deletion fails.

#### `delete_apps_by_email(email: str) -> dict`

Deletes all apps belonging to a specific email.

-   **email**: The user's email.
-   **Returns**: A dictionary with the deletion status.

#### `delete_apps_except_ids(excluded_ids: List[str]) -> dict`

Deletes all apps except for those with the specified IDs.

-   **excluded_ids**: A list of app IDs to preserve.
-   **Returns**: A dictionary with information about the deletion operation.

#### `get_app_initialization_status(app_id: str) -> Dict[str, Any]`

Checks if an app is initialized.

-   **app_id**: The app ID to check.
-   **Returns**: A dictionary with the initialization status.
-   **Raises**: `HTTPException` (404) if the app is not found.

---

## Auth Service

The `AuthService` manages user authentication, including OAuth2 integration, token management, and user role administration.

### Functions

#### `generate_login_url() -> str`

Generates the OAuth login URL.

-   **Returns**: The OAuth login URL.

#### `process_oauth_callback(code: str, state: str, request: Request) -> Dict[str, str]`

Processes the OAuth callback and creates a user session.

-   **code**: The authorization code from the OAuth provider.
-   **state**: The state parameter for CSRF protection.
-   **request**: The FastAPI request object.
-   **Returns**: A dictionary containing the `access_token`, `refresh_token`, and `user_id`.

#### `refresh_token(refresh_token: str) -> Dict[str, str]`

Refreshes an access token using a refresh token.

-   **refresh_token**: The refresh token.
-   **Returns**: A dictionary with the new `access_token` and `refresh_token`.
-   **Raises**: `HTTPException` (401) for an invalid refresh token, or (404) if the user is not found.

#### `logout(request: Request, response: Response) -> Dict[str, Any]`

Logs out a user by clearing the session, cookies, and invalidating the refresh token.

-   **request**: The FastAPI request object.
-   **response**: The FastAPI response object.
-   **Returns**: A dictionary with a success message.

#### `check_auth_status(token: str) -> Dict[str, Any]`

Checks the authentication status using an access token.

-   **token**: The access token.
-   **Returns**: A dictionary with the authentication status and user information.
-   **Raises**: `HTTPException` (401) if the token is invalid or the user is not found.

#### `get_all_users() -> List[Dict[str, Any]]`

Gets all users with filtered fields.

-   **Returns**: A list of all users.

#### `update_user_role(email: str, role: str) -> Dict[str, Any]`

Updates a user's role.

-   **email**: The user's email.
-   **role**: The new role (`SUPER_ADMIN`, `ADMIN`, or `NORMAL`).
-   **Returns**: A dictionary with the updated user information.
-   **Raises**: `HTTPException` (400) for an invalid role, or (404) if the user is not found.

---

## Container Service

The `ContainerService` is responsible for managing containers (folders) associated with an app.

### Functions

#### `get_containers(app_id: str) -> Dict[str, Any]`

Gets all containers for an app.

-   **app_id**: The app ID.
-   **Returns**: A dictionary with the containers and a message.
-   **Raises**: `HTTPException` (404) if the app is not found.

#### `add_containers(app_id: str, folders: List[Dict[str, Any]]) -> Dict[str, str]`

Adds multiple containers to an app.

-   **app_id**: The app ID.
-   **folders**: A list of folder data dictionaries.
-   **Returns**: A success message.
-   **Raises**: `HTTPException` (404) if the app is not found, (409) for duplicate folder paths, or (400) for other errors.

#### `update_containers(app_id: str, folders: List[Dict[str, Any]]) -> Dict[str, str]`

Updates containers by replacing existing ones with new folders.

-   **app_id**: The app ID.
-   **folders**: A list of folder data dictionaries.
-   **Returns**: A success message.
-   **Raises**: `HTTPException` (404) if the app is not found, (409) for duplicate folder paths, or (400) for other errors.

#### `delete_container(app_id: str, folder_id: str) -> Dict[str, str]`

Deletes a specific container.

-   **app_id**: The app ID.
-   **folder_id**: The folder ID to delete.
-   **Returns**: A success message.
-   **Raises**: `HTTPException` (404) if the container or app is not found, or (400) for other errors.

---

## Dashboard Service

The `DashboardService` handles business logic for dashboard endpoints, providing an aggregated view of analytics and agent performance with proper authorization.

### Functions

#### `get_accessible_agents(user_email: str, user_role: str) -> List[str]`

Gets a list of agent IDs that the user has access to.

-   **user_email**: The user's email.
-   **user_role**: The user's role.
-   **Returns**: A list of accessible agent IDs.

#### `get_dashboard_overview(...) -> Dict[str, Any]`

Gets a dashboard overview with key performance indicators (KPIs).

-   **user_email**: The user's email.
-   **user_role**: The user's role.
-   **agent_id**: Optional agent filter.
-   **departments**: Optional list of department filters.
-   **start_date**: Optional start date for the analysis.
-   **end_date**: Optional end date for the analysis.
-   **Returns**: A dictionary with the dashboard overview data.

#### `get_performance_metrics(...) -> PerformanceMetricsResponse`

Gets performance metrics with trends.

-   **user_email**: The user's email.
-   **user_role**: The user's role.
-   **agent_id**: Optional agent filter.
-   **departments**: Optional list of department filters.
-   **start_date**: Optional start date.
-   **end_date**: Optional end date.
-   **time_granularity**: The granularity of the time series data (e.g., "day").
-   **Returns**: A `PerformanceMetricsResponse` object.

#### `get_agents_list(...) -> Dict[str, Any]`

Gets a list of agents with optional metrics.

-   **user_email**: The user's email.
-   **user_role**: The user's role.
-   **departments**: Optional list of department filters.
-   **include_metrics**: Whether to include performance metrics for each agent.
-   **Returns**: A dictionary with the list of agents and metadata.

#### `get_department_analytics(...) -> DepartmentAnalyticsResponse`

Gets an analytics breakdown by department.

-   **user_email**: The user's email.
-   **user_role**: The user's role.
-   **start_date**: Optional start date.
-   **end_date**: Optional end date.
-   **Returns**: A `DepartmentAnalyticsResponse` object.

#### `get_topic_analytics(...) -> Dict[str, Any]`

Gets topic analytics and trends.

-   **user_email**: The user's email.
-   **user_role**: The user's role.
-   **agent_id**: Optional agent filter.
-   **departments**: Optional list of department filters.
-   **limit**: The maximum number of topics to return.
-   **include_trends**: Whether to include trend data.
-   **Returns**: A dictionary with topic analytics.

#### `get_usage_heatmap(...) -> HeatmapResponse`

Gets usage heatmap data.

-   **user_email**: The user's email.
-   **user_role**: The user's role.
-   **agent_id**: Optional agent filter.
-   **departments**: Optional list of department filters.
-   **days**: The number of days to include in the heatmap.
-   **Returns**: A `HeatmapResponse` object.

#### `get_recommendations(...) -> Dict[str, Any]`

Gets AI-generated recommendations.

-   **user_email**: The user's email.
-   **user_role**: The user's role.
-   **agent_id**: Optional agent filter.
-   **departments**: Optional list of department filters.
-   **priority**: Optional priority filter.
-   **status**: The status of recommendations to retrieve (e.g., "Open").
-   **Returns**: A dictionary with recommendations and metadata.

#### `export_data(...) -> Dict[str, Any]`

Exports dashboard data in various formats (JSON, CSV).

-   **user_email**: The user's email.
-   **user_role**: The user's role.
-   **format**: The export format (`json` or `csv`).
-   **data_type**: The type of data to export (`overview`, `performance`, etc.).
-   **agent_id**: Optional agent filter.
-   **departments**: Optional list of department filters.
-   **start_date**: Optional start date.
-   **end_date**: Optional end date.
-   **Returns**: A dictionary with the exported data.

---

## Data Source Service

The `DataSourceService` manages the data sources linked to an app.

### Functions

#### `get_all_sources(app_id: str)`

Fetches all data sources linked to an app.

-   **app_id**: The app ID.
-   **Returns**: A list of all data sources for the app.

#### `get_source_by_type(app_id: str, source_type: str)`

Fetches a specific data source by its type.

-   **app_id**: The app ID.
-   **source_type**: The type of the data source.
-   **Returns**: The data source, or `None` if not found.

#### `add_source(app_id: str, source_data: dict)`

Adds a new data source to the given app.

-   **app_id**: The app ID.
-   **source_data**: A dictionary with the data for the new source.
-   **Returns**: The newly created data source.

#### `add_multiple_sources(app_id: str, sources_data: list[str])`

Adds multiple data sources to the given app.

-   **app_id**: The app ID.
-   **sources_data**: A list of data source types to add.
-   **Returns**: A list of the newly created data sources.

#### `update_all_sources(app_id: str, sources_data: list[str])`

Replaces all data sources for an app.

-   **app_id**: The app ID.
-   **sources_data**: A list of the new data source types.
-   **Returns**: A list of the newly created data sources.

#### `remove_source_by_type(app_id: str, source_type: str)`

Removes a single data source by type for an app.

-   **app_id**: The app ID.
-   **source_type**: The type of the data source to remove.
-   **Returns**: `True` if the source was deleted, `False` otherwise.

#### `remove_all_sources(app_id: str)`

Removes all data sources associated with an app.

-   **app_id**: The app ID.
-   **Returns**: The number of sources deleted.

---

## Document Service

The `DocumentService` is responsible for managing documents associated with an app.

### Functions

#### `get_documents(app_id: str) -> Dict[str, Any]`

Gets all documents for an app.

-   **app_id**: The app ID.
-   **Returns**: A dictionary with the documents and a message.
-   **Raises**: `HTTPException` (404) if the app is not found.

#### `add_documents(app_id: str, files: List[Dict[str, Any]]) -> Dict[str, str]`

Adds multiple documents to an app.

-   **app_id**: The app ID.
-   **files**: A list of file data dictionaries.
-   **Returns**: A success message.
-   **Raises**: `HTTPException` (404) if the app is not found, or (400) for other errors.

#### `update_documents(app_id: str, files: List[Dict[str, Any]]) -> Dict[str, str]`

Updates documents by replacing existing ones with new files.

-   **app_id**: The app ID.
-   **files**: A list of file data dictionaries.
-   **Returns**: A success message.
-   **Raises**: `HTTPException` (404) if the app is not found, or (400) for other errors.

#### `delete_document(app_id: str, file_id: str) -> Dict[str, str]`

Deletes a specific document.

-   **app_id**: The app ID.
-   **file_id**: The file ID to delete.
-   **Returns**: A success message.
-   **Raises**: `HTTPException` (404) if the document or app is not found, or (400) for other errors.

---

## Instruction Service

The `InstructionService` manages the instructional prompts for an app.

### Functions

#### `get_instruction(app_id: str) -> Dict[str, Any]`

Gets the instruction for an app.

-   **app_id**: The app ID.
-   **Returns**: The instruction data.
-   **Raises**: `HTTPException` (404) if the instruction or app is not found.

#### `add_instruction(app_id: str, instruction_data: Dict[str, Any]) -> Dict[str, Any]`

Adds a new instruction to an app.

-   **app_id**: The app ID.
-   **instruction_data**: The instruction data.
-   **Returns**: A success message and the instruction ID.
-   **Raises**: `HTTPException` (404) if the app is not found, (409) if an instruction already exists, or (400) for other errors.

#### `update_instruction(app_id: str, instruction_data: Dict[str, Any]) -> Dict[str, str]`

Updates an instruction or creates it if it doesn't exist.

-   **app_id**: The app ID.
-   **instruction_data**: The instruction data.
-   **Returns**: A success message.
-   **Raises**: `HTTPException` (404) if the app is not found, or (400) for other errors.

#### `delete_instruction(app_id: str) -> Dict[str, str]`

Deletes an instruction.

-   **app_id**: The app ID.
-   **Returns**: A success message.
-   **Raises**: `HTTPException` (404) if the instruction or app is not found, or (400) for other errors.

---

## LLM Guard Service

The `LLMGuardService` provides a low-latency wrapper around LLM-Guard's prompt injection scanner, optimized for production use with caching and performance monitoring.

### Functions

#### `scan_prompt(prompt: str) -> Tuple[bool, float, Optional[str]]`

Scans a prompt for injection attempts.

-   **prompt**: The user prompt to scan.
-   **Returns**: A tuple containing:
    -   `is_safe` (bool): `True` if the prompt is safe.
    -   `risk_score` (float): The risk score from 0.0 to 1.0.
    -   `sanitized_prompt` (str): The sanitized version of the prompt.

#### `scan_prompt_async(prompt: str) -> Tuple[bool, float, Optional[str]]`

Asynchronous version of `scan_prompt`.

-   **prompt**: The user prompt to scan.
-   **Returns**: The same as `scan_prompt`.

#### `get_metrics() -> Dict[str, Any]`

Gets the current performance metrics.

-   **Returns**: A dictionary with performance metrics.

#### `reset_metrics()`

Resets the performance metrics.

#### `clear_cache()`

Clears the cache.

#### `update_threshold(new_threshold: float)`

Updates the risk threshold dynamically.

-   **new_threshold**: The new threshold value (0.0-1.0).

---

## Local Docs Service

The `LocalFileService` manages local files uploaded to an app, including handling uploads to Azure Blob Storage.

### Functions

#### `get_localfiles(app_id: str) -> Dict[str, Any]`

Gets all local files for an app.

-   **app_id**: The app ID.
-   **Returns**: A dictionary with the local files and a message.
-   **Raises**: `HTTPException` (404) if the app is not found.

#### `add_localfiles(app_id: str, files: List[Dict[str, Any]]) -> Dict[str, str]`

Adds multiple local files to an app.

-   **app_id**: The app ID.
-   **files**: A list of file data dictionaries.
-   **Returns**: A success message.
-   **Raises**: `HTTPException` (404) if the app is not found, or (400) for other errors.

#### `update_localfiles(app_id: str, files: List[Dict[str, Any]]) -> Dict[str, str]`

Updates local files by replacing existing ones with new files.

-   **app_id**: The app ID.
-   **files**: A list of file data dictionaries.
-   **Returns**: A success message.
-   **Raises**: `HTTPException` (404) if the app is not found, or (400) for other errors.

#### `delete_localfile(app_id: str, file_id: str) -> Dict[str, str]`

Deletes a specific local file.

-   **app_id**: The app ID.
-   **file_id**: The file ID to delete.
-   **Returns**: A success message.
-   **Raises**: `HTTPException` (404) if the file or app is not found, or (400) for other errors.

#### `upload_local_files_to_container(app_id: str, container_name: str) -> List[Dict]`

Uploads local files to a blob storage container when creating a workforce agent.

-   **app_id**: The app ID.
-   **container_name**: The name of the blob storage container.
-   **Returns**: A list of dictionaries with the upload results.

#### `get_file_content(app_id: str, file_id: str) -> bytes`

Gets the file content by file ID.

-   **app_id**: The app ID.
-   **file_id**: The file ID.
-   **Returns**: The file content as bytes.
-   **Raises**: `HTTPException` (404) if the file is not found, or (500) for other errors.

---

## Message Processor Service

The `MessageProcessorService` handles asynchronous processing of chat messages from an Azure Service Bus queue.

### Functions

#### `start_processing()`

Starts the background message processing loop.

#### `stop_processing()`

Stops the background message processing.

#### `get_processing_stats() -> Dict[str, Any]`

Gets the current processing statistics from lightweight status tracking.

-   **Returns**: A dictionary containing processing statistics.

---

## Prompt Integrated Topic Service

The `PromptIntegratedTopicService` is a refactored version of the topic service that uses a centralized prompt management system.

### Functions

#### `detect_topic_and_department(query: str) -> Optional[Dict[str, str]]`

Detects the topic and department using the prompt manager.

-   **query**: The user query to classify.
-   **Returns**: A dictionary with the topic and department, or `None` if detection fails.

#### `get_prompt_info() -> Dict[str, any]`

Gets information about the prompts used by this service.

-   **Returns**: A dictionary with prompt configuration information.

#### `update_departments(new_departments: List[str])`

Updates the list of available departments.

-   **new_departments**: The new list of department names.

---

## Publish App Service

The `PublishedAppService` manages the publishing and visibility of apps.

### Functions

#### `get_published_app_by_app_id(app_id: str)`

Gets a published app by its app ID.

-   **app_id**: The app ID.
-   **Returns**: The published app, or `None` if not found.

#### `get_all_published_apps()`

Gets all published apps.

-   **Returns**: A list of all published apps.

#### `get_published_apps_for_user(email: str)`

Gets published apps that are visible to a specific user.

-   **email**: The user's email.
-   **Returns**: A list of visible published apps.

#### `publish_app(app_id: str, publish_data: Dict[str, Any])`

Publishes an app.

-   **app_id**: The app ID.
-   **publish_data**: A dictionary with the publishing data (visibility, etc.).
-   **Returns**: The newly published app.
-   **Raises**: `ValueError` for invalid data.

#### `update_published_app(app_id: str, publish_data: Dict[str, Any])`

Updates a published app.

-   **app_id**: The app ID.
-   **publish_data**: A dictionary with the updated publishing data.
-   **Returns**: The updated published app.
-   **Raises**: `ValueError` if the app is not published or for invalid data.

#### `patch_published_app(app_id: str, patch_data: Dict[str, Any])`

Partially updates a published app.

-   **app_id**: The app ID.
-   **patch_data**: A dictionary with the fields to update.
-   **Returns**: The updated published app.
-   **Raises**: `ValueError` if the app is not published or for invalid data.

#### `unpublish_app(app_id: str)`

Unpublishes an app.

-   **app_id**: The app ID.
-   **Returns**: `True` if successful.
-   **Raises**: `ValueError` if the app is not published.

---

## Response Consumer Service

The `ResponseConsumerService` provides methods to consume response messages from the Service Bus response queue.

### Functions

#### `poll_for_response(correlation_id: str, timeout: int = 30) -> Optional[Dict[str, Any]]`

Polls for a specific response message by correlation ID.

-   **correlation_id**: The correlation ID to match.
-   **timeout**: The maximum seconds to wait.
-   **Returns**: The response data if found, `None` if the timeout is reached.

#### `stream_responses(correlation_id: str, timeout: int = 300) -> AsyncIterator[Dict[str, Any]]`

Streams responses for a correlation ID using a Server-Sent Events (SSE) pattern.

-   **correlation_id**: The correlation ID to match.
-   **timeout**: The maximum seconds to stream.
-   **Yields**: Response data chunks as they arrive.

#### `consume_user_responses(user_id: str, max_messages: int = 10) -> List[Dict[str, Any]]`

Consumes all pending responses for a specific user.

-   **user_id**: The user ID to filter responses.
-   **max_messages**: The maximum number of messages to retrieve.
-   **Returns**: A list of response messages for the user.

#### `get_processing_stats() -> Dict[str, Any]`

Gets the current processing statistics for the response consumer.

-   **Returns**: A dictionary containing processing statistics.

#### `health_check() -> Dict[str, Any]`

Performs a health check on the response queue consumer.

-   **Returns**: A health status dictionary.

---

## Service Bus Service

The `ServiceBusService` provides enterprise-grade message queuing capabilities for Azure Service Bus.

### Functions

#### `publish_message(...) -> str`

Publishes a message to the specified Service Bus queue.

-   **queue_name**: The target queue name.
-   **message_data**: The message payload as a dictionary.
-   **correlation_id**: Optional correlation ID for message tracking.
-   **session_id**: Optional session ID for message grouping.
-   **delay_seconds**: Optional delay before the message becomes available.
-   **Returns**: The message ID of the published message.
-   **Raises**: `ServiceBusError` when message publishing fails.

#### `publish_chat_message(chat_data: Dict[str, Any], user_id: str, session_id: Optional[str] = None) -> str`

Publishes a chat message to the chat processing queue.

-   **chat_data**: The chat message data.
-   **user_id**: The user identifier.
-   **session_id**: Optional chat session ID.
-   **Returns**: The message correlation ID for tracking.

#### `publish_response(response_data: Dict[str, Any]) -> str`

Publishes a response message to the response queue.

-   **response_data**: The response message data.
-   **Returns**: The message ID for tracking.

#### `consume_messages(...)`

Consumes messages from the specified queue with proper error handling.

-   **queue_name**: The queue to consume from.
-   **message_handler**: An async function to handle received messages.
-   **max_messages**: The maximum number of messages to receive in one batch.
-   **max_wait_time**: The maximum wait time in seconds.

#### `check_queue_access(queue_name: str) -> bool`

Checks if a specific queue can be accessed.

-   **queue_name**: The queue name to check.
-   **Returns**: `True` if the queue is accessible, `False` otherwise.

#### `health_check() -> Dict[str, Any]`

Performs a health check on the Service Bus connection and queues.

-   **Returns**: A health status dictionary.

#### `close()`

Closes the Service Bus client and cleans up resources.

---

## SharePoint Service

The `SharePointService` handles interactions with SharePoint, including retrieving data and processing queries.

### Functions

#### `get_sharepoint_structure(user_email: str) -> Dict[str, Any]`

Gets the complete SharePoint structure for a user.

-   **user_email**: The user's email address.
-   **Returns**: A dictionary containing the SharePoint structure data.

#### `process_query(user_email: str, query: str) -> Dict[str, Any]`

Processes a natural language query about SharePoint content.

-   **user_email**: The user's email address.
-   **query**: The natural language query.
-   **Returns**: A dictionary containing the query results.

#### `upload_file(user_email: str, site_id: str, folder_path: str, file_name: Optional[str] = None) -> Dict[str, Any]`

Uploads a file to SharePoint.

-   **user_email**: The user's email address.
-   **site_id**: The SharePoint site ID.
-   **folder_path**: The path to upload to.
-   **file_name**: Optional filename override.
-   **Returns**: A dictionary containing the upload result.

---

## Tool Service

The `ToolService` manages the tools associated with an app.

### Functions

#### `get_tools_by_app_id(app_id: str)`

Gets all tools for an app.

-   **app_id**: The app ID.
-   **Returns**: A list of all tools for the app.

#### `get_tool_by_type(app_id: str, tool_type: str)`

Gets a specific tool by its type.

-   **app_id**: The app ID.
-   **tool_type**: The type of the tool.
-   **Returns**: The tool, or `None` if not found.

#### `check_tool_exists(app_id: str, tool_type: str) -> bool`

Checks if a tool exists for an app.

-   **app_id**: The app ID.
-   **tool_type**: The type of the tool.
-   **Returns**: `True` if the tool exists, `False` otherwise.

#### `add_tool(app_id: str, tool_type: str)`

Adds a new tool to an app.

-   **app_id**: The app ID.
-   **tool_type**: The type of the tool to add.
-   **Returns**: The newly created tool.
-   **Raises**: `HTTPException` (409) if the tool already exists.

#### `add_multiple_tools(app_id: str, tool_data: dict)`

Adds multiple tools to an app.

-   **app_id**: The app ID.
-   **tool_data**: A dictionary containing a list of tool types to add.
-   **Returns**: A list of the newly created tools.
-   **Raises**: `HTTPException` (400) for invalid or duplicate tools.

#### `update_tools(app_id: str, tool_data: dict)`

Updates the tools for an app by removing all existing tools and adding new ones.

-   **app_id**: The app ID.
-   **tool_data**: A dictionary containing a list of the new tool types.
-   **Returns**: A list of the newly created tools.
-   **Raises**: `HTTPException` (400) for invalid tools.

#### `delete_tool(app_id: str, tool_type: str)`

Deletes a tool by its type.

-   **app_id**: The app ID.
-   **tool_type**: The type of the tool to delete.
-   **Returns**: `True` if the tool was deleted, `False` otherwise.

#### `delete_all_tools(app_id: str)`

Deletes all tools for an app.

-   **app_id**: The app ID.
-   **Returns**: The number of tools deleted.

---

## Topic Service

The `TopicService` is responsible for detecting topics and departments from user queries and managing a topic registry.

### Functions

#### `detect_topic_and_department_from_query(query: str) -> Tuple[Optional[str], Optional[str]]`

Uses AI to detect both the main topic and department from a user query.

-   **query**: The user query.
-   **Returns**: A tuple containing the detected topic and department.

#### `detect_topic_from_query_fallback(query: str) -> Optional[str]`

A fallback method for topic detection only.

-   **query**: The user query.
-   **Returns**: The detected topic.

#### `detect_topic_from_query(query: str) -> Optional[str]`

A backward-compatibility method that only returns the topic.

-   **query**: The user query.
-   **Returns**: The detected topic.

#### `update_topic_registry(topic_name: str, department: str = None, agent_id: str = None)`

Updates or creates a topic in the registry with department information.

-   **topic_name**: The name of the topic.
-   **department**: The department associated with the topic (optional).
-   **agent_id**: The agent ID associated with the topic (optional).

#### `get_topic_analytics() -> Dict`

Gets analytics about topics.

-   **Returns**: A dictionary with topic analytics.

#### `get_emerging_topics(...) -> List[Dict]`

Gets emerging topics based on recent growth patterns with date range and department filters.

-   **agent_id**: Optional agent filter.
-   **start_date**: Optional start date.
-   **end_date**: Optional end date.
-   **departments**: Optional list of department filters.
-   **limit**: Optional limit on the number of topics to return.
-   **Returns**: A list of emerging topics.

#### `get_topic_evolution_simple(...) -> Dict`

Gets simple topic evolution data for a bubble chart.

-   **start_date**: Optional start date.
-   **end_date**: Optional end date.
-   **min_growth**: The minimum growth count for a topic to be included.
-   **limit**: The maximum number of topics to return.
-   **agent_id**: Optional agent filter.
-   **departments**: Optional list of department filters.
-   **Returns**: A dictionary with topic evolution data.

---

## Topic Service (Migrated)

The `TopicService` (migrated) is a refactored version that uses a centralized prompt management system for detecting topics and departments.

### Functions

#### `detect_topic_and_department(query: str) -> Optional[Dict[str, str]]`

Detects both the topic and department from a user query using AI.

-   **query**: The user query.
-   **Returns**: A dictionary with the 'topic' and 'department', or `None` on failure.

#### `detect_topic_from_query_fallback(query: str) -> Optional[str]`

A fallback method for topic detection only, using managed prompts.

-   **query**: The user query.
-   **Returns**: The detected topic, or "General Query" on failure.

#### `update_departments(new_departments: List[str])`

Updates the list of available departments.

-   **new_departments**: The new list of department names.

#### `save_topic_to_analytics(user_id: int, agent_id: int, topic: str, department: Optional[str] = None) -> bool`

Saves the detected topic to the analytics database.

-   **user_id**: The user's ID.
-   **agent_id**: The agent's ID.
-   **topic**: The detected topic.
-   **department**: The detected department (optional).
-   **Returns**: `True` if successful, `False` otherwise.

---

## Trigger Service

The `TriggerService` manages the triggers associated with an app, which can be conversational or time-based.

### Functions

#### `get_trigger_by_app_id(app_id)`

Gets the trigger for an app.

-   **app_id**: The app ID.
-   **Returns**: The trigger, or `None` if not found.

#### `add_conversational_trigger(app_id, trigger_data: ConversationalTriggerCreate)`

Adds a new conversational trigger to an app.

-   **app_id**: The app ID.
-   **trigger_data**: The data for the conversational trigger.
-   **Returns**: The newly created trigger.

#### `add_time_trigger(app_id, trigger_data: TimeTriggerCreate)`

Adds a new time-based trigger to an app.

-   **app_id**: The app ID.
-   **trigger_data**: The data for the time-based trigger.
-   **Returns**: The newly created trigger.

#### `update_trigger(app_id, trigger_data: TriggerUpdate)`

Updates a trigger or creates it if it doesn't exist.

-   **app_id**: The app ID.
-   **trigger_data**: The data for the trigger.
-   **Returns**: The updated or created trigger.

#### `delete_trigger(app_id)`

Deletes a trigger by app ID.

-   **app_id**: The app ID.
-   **Returns**: `True` if the trigger was deleted, `False` otherwise.

---

## Workforce Agent Service

The `WorkforceAgentService` is responsible for creating, operating, and managing workforce agents.

### Functions

#### `prepare_workforce_parameters(resources: Dict[str, Any], access_token: str) -> Dict[str, Any]`

Prepares the parameters for creating a workforce agent.

-   **resources**: A dictionary of app resources (documents, containers, etc.).
-   **access_token**: The user's access token.
-   **Returns**: A dictionary of parameters for creating the agent.

#### `transform_email_in_query(query: str) -> str`

Transforms email addresses in a query to a specific format.

-   **query**: The user query.
-   **Returns**: The transformed query.

#### `generate_enhanced_response_message(query: str, response: str, language: str = "en") -> str`

Uses AI to generate an enhanced message based on the query and the actual response.

-   **query**: The user query.
-   **response**: The actual response from the agent.
-   **language**: The language of the response.
-   **Returns**: The enhanced response message.

#### `generate_response_message(query: str, response: str, language: str = "en") -> str`

Uses AI to generate a brief message based on the query and response.

-   **query**: The user query.
-   **response**: The actual response from the agent.
-   **language**: The language of the response.
-   **Returns**: The brief response message.

#### `create_agent(app_id: str, access_token: str) -> Dict[str, Any]`

Creates a workforce agent for an app.

-   **app_id**: The app ID.
-   **access_token**: The user's access token.
-   **Returns**: A dictionary with a success message and the agent ID.
-   **Raises**: `Exception` if the agent already exists or creation fails.

#### `operate_agent(app_id: str, query_data: UserQuery, access_token: str) -> WorkforceResponse`

Operates a workforce agent for an app.

-   **app_id**: The app ID.
-   **query_data**: The user query data.
-   **access_token**: The user's access token.
-   **Returns**: A `WorkforceResponse` object.
-   **Raises**: `Exception` if the agent is not found or operation fails.

#### `delete_agent(app_id: str) -> Dict[str, str]`

Deletes a workforce agent.

-   **app_id**: The app ID.
-   **Returns**: A success message.
-   **Raises**: `Exception` if the agent is not found or deletion fails.

#### `operate_agent_public_stream(app_id: str, query_data: UserQuery) -> AsyncGenerator[str, None]`

Operates a workforce agent with a streaming response for public use.

-   **app_id**: The app ID.
-   **query_data**: The user query data.
-   **Yields**: Server-Sent Events (SSE) with response chunks.

#### `operate_agent_non_public_stream(app_id: str, query_data: UserQuery, access_token=None, metrics=None) -> AsyncGenerator[str, None]`

Operates a workforce agent with a streaming response for non-public use.

-   **app_id**: The app ID.
-   **query_data**: The user query data.
-   **access_token**: The user's access token (optional).
-   **metrics**: A dictionary for collecting metrics (optional).
-   **Yields**: Server-Sent Events (SSE) with response chunks.

---

## Workforce Agent Service (Migrated)

The `WorkforceAgentService` (migrated) is a refactored version that uses a centralized prompt management system.

### Functions

#### `create_agent(agent_name: str, user_id: int) -> Agent`

Creates a new agent.

-   **agent_name**: The name of the agent.
-   **user_id**: The ID of the user creating the agent.
-   **Returns**: The newly created `Agent` object.
-   **Raises**: `ValueError` if an agent with the same name already exists for the user.

#### `list_agents(user_id: Optional[int] = None) -> List[Agent]`

Lists all agents, optionally filtered by user.

-   **user_id**: The user ID to filter by (optional).
-   **Returns**: A list of `Agent` objects.

#### `delete_agent(agent_id: int) -> bool`

Deletes an agent.

-   **agent_id**: The ID of the agent to delete.
-   **Returns**: `True` if successful, `False` otherwise.

#### `get_user_assistant(user_id: int) -> Optional[UserAssistants]`

Gets the user's assistant configuration.

-   **user_id**: The user's ID.
-   **Returns**: The `UserAssistants` object, or `None` if not found.

#### `search_and_respond(...) -> Dict[str, Any]`

Searches for information and generates a response.

-   **agent_id**: The agent ID.
-   **query**: The user query.
-   **user_id**: The user ID.
-   **cosmos_container**: The Cosmos DB container.
-   **language**: The language of the response.
-   **public**: Whether the agent is public.
-   **department**: The department associated with the query.
-   **topic**: The topic of the query.
-   **is_voice**: Whether the response should be voice-friendly.
-   **Returns**: A dictionary with the response data.

#### `generate_enhanced_response_message(query: str, response: str, language: str = "en") -> str`

Uses AI to generate an enhanced message, managed by the prompt system.

-   **query**: The user query.
-   **response**: The actual response from the agent.
-   **language**: The language of the response.
-   **Returns**: The enhanced response message.

#### `generate_response_message(query: str, response: str, language: str = "en") -> str`

Uses AI to generate a brief message, managed by the prompt system.

-   **query**: The user query.
-   **response**: The actual response from the agent.
-   **language**: The language of the response.
-   **Returns**: The brief response message.

#### `clean_document_name(doc_name: str) -> str`

Cleans up document names for display.

-   **doc_name**: The document name to clean.
-   **Returns**: The cleaned document name.

#### `build_temporary_vector_index(...) -> Dict[str, Any]`

Builds a temporary vector index for the given files.

-   **agent_id**: The agent ID.
-   **files**: A list of files to index.
-   **folder_path**: The path to the folder containing the files (optional).
-   **index_name**: The name of the index to create (optional).
-   **Returns**: A dictionary with the result of the operation.

#### `search_temporary_index(index_name: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]`

Searches in a temporary vector index.

-   **index_name**: The name of the index to search.
-   **query**: The search query.
-   **top_k**: The number of top results to return.
-   **Returns**: A list of search results.
