# Documentation for the `repository` Module

This document provides a comprehensive overview of the `repository` module, which is responsible for all database interactions in the application. Each file within this module corresponds to a specific data model and contains a repository class with methods for creating, reading, updating, and deleting records.

## Core Concepts

The repository pattern is used to separate the application's business logic from the data access logic. This has several advantages:

*   **Decoupling:** The business logic is not tied to a specific database implementation.
*   **Testability:** The business logic can be tested independently of the database.
*   **Maintainability:** The data access logic is centralized and easier to maintain.

Each repository class is initialized with a `session_factory`, which is used to create new database sessions. This ensures that each database operation is performed in a separate session, which is important for preventing race conditions and other concurrency issues.

## File-by-File Breakdown

This section provides a detailed description of each file in the `repository` module.

### `__init__.py`
This file is empty and serves to mark the `repository` directory as a Python package.

### `analytics_repository.py`
This file contains the `AnalyticsRepository` class, which is responsible for all database operations related to analytics.

**`AnalyticsRepository` Class**

| Method | Description | Parameters | Returns |
| --- | --- | --- | --- |
| `create` | Create a new analytics record. | `analytics_data: AnalyticsCreateRequest`, `agent_id`, `user_email` | `ChatbotAnalytics` |
| `get_by_id` | Get an analytics record by ID. | `record_id: str` | `Optional[ChatbotAnalytics]` |
| `get_by_agent_id` | Get analytics records for a specific agent. | `agent_id: str`, `limit: int = 100`, `offset: int = 0` | `List[ChatbotAnalytics]` |
| `get_by_user_id` | Get analytics records for a specific user. | `user_id: str`, `limit: int = 100`, `offset: int = 0` | `List[ChatbotAnalytics]` |
| `get_by_session_id` | Get analytics records for a specific session. | `session_id: str` | `List[ChatbotAnalytics]` |
| `get_analytics_summary` | Get summary statistics for an agent's analytics. | `agent_id: str` | `Dict[str, Any]` |
| `get_feedback_trends` | Get feedback trends over time for an agent. | `agent_id: str`, `days: int = 30` | `List[Dict[str, Any]]` |
| `update` | Update an analytics record. | `record_id: str`, `update_data: Dict[str, Any]` | `Optional[ChatbotAnalytics]` |
| `delete` | Delete an analytics record. | `record_id: str` | `bool` |
| `get_recent_feedback` | Get recent feedback for an agent within specified hours. | `agent_id: str`, `hours: int = 24` | `List[ChatbotAnalytics]` |
| `get_feedback_by_query_pattern` | Get feedback records that match a query pattern. | `agent_id: str`, `query_pattern: str` | `List[ChatbotAnalytics]` |
| `count_total_feedback` | Get total feedback count for an agent. | `agent_id: str` | `int` |
| `create_performance_metrics` | Create a new performance metrics record. | `agent_id: str`, `query: str`, `response: str`, `response_time: float`, `department: str = None` | `str` |
| `get_performance_analytics` | Get performance analytics with date range and department filters. | `agent_id: Optional[str] = None`, `start_date: Optional[datetime] = None`, `end_date: Optional[datetime] = None`, `departments: Optional[List[str]] = None` | `Dict[str, Any]` |
| `get_daily_query_data` | Get daily query counts from AgentPerformanceMetrics table with date range and filters. | `start_date: datetime`, `end_date: datetime`, `agent_id: Optional[str] = None`, `departments: Optional[List[str]] = None` | `List[Dict]` |
| `get_query_count_for_period` | Get total query count for a specific time period from AgentPerformanceMetrics. | `start_date: datetime`, `end_date: datetime`, `agent_id: Optional[str] = None` | `int` |
| `get_daily_query_trends` | Get daily query trends from AgentPerformanceMetrics. | `agent_id: Optional[str] = None`, `days: int = 30` | `List[Dict[str, Any]]` |
| `get_query_volume_summary` | Get summary statistics for query volume from AgentPerformanceMetrics. | `agent_id: Optional[str] = None` | `Dict[str, Any]` |
| `get_heatmap_interaction_data` | Get raw interaction data for heatmap generation. | `start_date: datetime`, `end_date: datetime`, `agent_id: Optional[str] = None`, `departments: Optional[List[str]] = None` | `List[Dict]` |
| `create_recommendation` | Create a recommendation for specific agent. | `agent_id: str`, `title: str`, `description: str`, `type: str`, `priority: str`, `department: str = None` | `str` |
| `update_recommendation_status` | Update recommendation status. | `rec_id: str`, `status: str` | `bool` |
| `get_simple_analytics_summary` | Get analytics summary for specific agent - auto-detects department from database. | `agent_id: str` | `Dict` |
| `get_recommendations_for_agent` | Get all recommendations for a specific agent (Python filtering only) - ULTRA SAFE. | `agent_id: str` | `List` |
| `check_need_refresh_for_agent` | Check if agent needs new recommendations (Python filtering only) - ULTRA SAFE. | `agent_id: str` | `bool` |
| `clear_agent_recommendations` | Clear all recommendations for specific agent (Python filtering) - ULTRA SAFE. | `agent_id: str` | `None` |
| `should_refresh_recommendations` | DEPRECATED - Use check_need_refresh_for_agent instead. | `agent_id: str`, `department: str = None` | `bool` |
| `get_active_recommendations` | ULTRA SAFE - Get recommendations with Python-only filtering. | `agent_id: str = None`, `departments: Optional[List[str]] = None` | `List` |
| `get_recommendations_by_departments` | ULTRA SAFE - Get recommendations by departments with Python filtering. | `departments: List[str]` | `List` |
| `get_recommendations_by_department` | ULTRA SAFE - Get recommendations by single department (backward compatibility). | `department: str` | `List` |
| `clear_old_recommendations` | DEPRECATED - Use clear_agent_recommendations instead. | `agent_id: str`, `department: str = None` | `None` |

### `app_repository.py`
This file contains the `AppRepository` class, which is responsible for all database operations related to apps.

**`AppRepository` Class**

| Method | Description | Parameters | Returns |
| --- | --- | --- | --- |
| `get_app_by_id` | Get an app by ID. | `app_id` | `Apps` |
| `get_app_by_name` | Get an app by name. | `app_name` | `Apps` |
| `get_app_by_name_and_email` | Get an app by name and email. | `app_name: str`, `email: str` | `Apps` |
| `create_app` | Create a new app. | `app_data` | `Apps` |
| `update_app` | Update an existing app. | `app_id`, `app_data` | `Apps` |
| `delete_app` | Delete an app by ID. | `app_id` | `bool` |
| `get_all_apps` | Get all apps with pagination and multi-column sorting. | `search=None`, `ordering=None`, `filter_by=None`, `filter_value=None`, `page=1`, `page_size=100`, `searchable_fields=None`, `email=None`, `name=None`, `is_initialised=None`, `created_at_start=None`, `created_at_end=None` | `dict` |
| `get_apps_by_email` | Get all apps for a specific email. | `email: str` | `List[Apps]` |
| `delete_apps_except_ids` | Delete all apps except those with the specified IDs. | `excluded_ids` | `dict` |
| `check_app_initialization` | Check if an app is initialized (has an entry in AgentState). | `app_id` | `dict` |

### `auth_repository.py`
This file contains the `AuthRepository` class, which is responsible for all database operations related to authentication.

**`AuthRepository` Class**

| Method | Description | Parameters | Returns |
| --- | --- | --- | --- |
| `get_user_by_email` | Get a user by email. | `email: str` | `Optional[User]` |
| `get_user_by_id` | Get a user by ID. | `user_id: str` | `Optional[User]` |
| `get_all_users` | Get all users. | | `List[User]` |
| `create_user` | Create a new user. | `user_data: Dict[str, Any]` | `User` |
| `update_user_last_login` | Update user's last login time. | `user: User` | `User` |
| `update_user_role` | Update user's role. | `email: str`, `role: str` | `Optional[User]` |
| `store_token_data` | Store token data in the database. | `access_token: str`, `refresh_token: str`, `token_type: str`, `expire_time: float`, `user_id: str` | `None` |

### `container_repository.py`
This file contains the `ContainerRepository` class, which is responsible for all database operations related to app containers.

**`ContainerRepository` Class**

| Method | Description | Parameters | Returns |
| --- | --- | --- | --- |
| `get_containers_by_app_id` | Get all containers for an app. | `app_id` | `List[AppContainers]` |
| `get_container_by_folder_id` | Get a specific container by folder ID. | `app_id`, `folder_id` | `AppContainers` |
| `add_container` | Add a new container to an app. | `app_id`, `folder_data` | `AppContainers` |
| `add_multiple_containers` | Add multiple containers to an app. | `app_id`, `folders_data` | `List[AppContainers]` |
| `delete_container` | Delete a container by folder ID. | `app_id`, `folder_id` | `bool` |
| `delete_all_containers` | Delete all containers for an app. | `app_id` | `int` |

### `datasource_repository.py`
This file contains the `DataSourceRepository` class, which is responsible for all database operations related to app data sources.

**`DataSourceRepository` Class**

| Method | Description | Parameters | Returns |
| --- | --- | --- | --- |
| `get_sources_by_app_id` | Get all data sources for an app. | `app_id` | `List[AppDataSources]` |
| `get_source_by_type` | Get a specific data source by type. | `app_id`, `source_type` | `AppDataSources` |
| `add_data_source` | Add a new data source to an app. | `app_id`, `source_data` | `AppDataSources` |
| `add_multiple_data_sources` | Add multiple data sources to an app. | `app_id`, `sources_data`, `email` | `List[AppDataSources]` |
| `update_all_data_sources` | Replace all existing data sources for an app with new ones. | `app_id`, `sources_data`, `email` | `List[AppDataSources]` |
| `delete_data_source` | Delete a data source by type. | `app_id`, `source_type` | `bool` |
| `delete_all_data_sources` | Delete all data sources for an app. | `app_id` | `int` |

### `document_repository.py`
This file contains the `DocumentRepository` class, which is responsible for all database operations related to app documents.

**`DocumentRepository` Class**

| Method | Description | Parameters | Returns |
| --- | --- | --- | --- |
| `get_documents_by_app_id` | Get all documents for an app. | `app_id` | `List[AppDocuments]` |
| `get_document_by_file_id` | Get a specific document by file ID. | `app_id`, `file_id` | `AppDocuments` |
| `add_document` | Add a new document to an app. | `app_id`, `file_data` | `AppDocuments` |
| `add_multiple_documents` | Add multiple documents to an app. | `app_id`, `files_data` | `List[AppDocuments]` |
| `delete_document` | Delete a document by file ID. | `app_id`, `file_id` | `bool` |
| `delete_all_documents` | Delete all documents for an app. | `app_id` | `int` |

### `instruction_repository.py`
This file contains the `InstructionRepository` class, which is responsible for all database operations related to app instructions.

**`InstructionRepository` Class**

| Method | Description | Parameters | Returns |
| --- | --- | --- | --- |
| `get_instruction_by_app_id` | Get the instruction for an app. | `app_id` | `AppInstructions` |
| `add_instruction` | Add a new instruction to an app. | `app_id`, `instruction_text` | `AppInstructions` |
| `update_instruction` | Update an instruction or create if it doesn't exist. | `app_id`, `instruction_text` | `AppInstructions` |
| `delete_instruction` | Delete an instruction by app ID. | `app_id` | `bool` |

### `localdocs_repository.py`
This file contains the `LocalFileRepository` class, which is responsible for all database operations related to local files.

**`LocalFileRepository` Class**

| Method | Description | Parameters | Returns |
| --- | --- | --- | --- |
| `get_localfiles_by_app_id` | Get all active local files for an app. | `app_id` | `List[AppLocalFiles]` |
| `get_localfile_by_file_id` | Get a specific local file by file ID. | `app_id`, `file_id` | `AppLocalFiles` |
| `get_localfile_with_content` | Get a specific local file with content by file ID. | `app_id`, `file_id` | `AppLocalFiles` |
| `add_localfile` | Add a new local file to an app. | `app_id`, `file_data` | `AppLocalFiles` |
| `add_multiple_localfiles` | Add multiple local files to an app. | `app_id`, `files_data` | `List[AppLocalFiles]` |
| `update_localfile` | Update a local file. | `app_id`, `file_id`, `update_data` | `AppLocalFiles` |
| `soft_delete_localfile` | Soft delete a local file by file ID. | `app_id`, `file_id` | `bool` |
| `soft_delete_all_localfiles` | Soft delete all local files for an app. | `app_id` | `int` |
| `delete_localfile` | Hard delete a local file by file ID (legacy method - kept for compatibility). | `app_id`, `file_id` | `bool` |
| `delete_all_localfiles` | Hard delete all local files for an app (legacy method - kept for compatibility). | `app_id` | `int` |
| `get_file_by_hash` | Get a file by its hash (for deduplication). | `app_id`, `file_hash` | `AppLocalFiles` |
| `get_files_by_extension` | Get all files by extension. | `app_id`, `file_extension` | `List[AppLocalFiles]` |
| `get_app_storage_stats` | Get storage statistics for an app. | `app_id` | `dict` |
| `search_files` | Search files by name. | `app_id`, `search_term` | `List[AppLocalFiles]` |
| `restore_file` | Restore a soft-deleted file. | `app_id`, `file_id` | `bool` |

### `publish_app_repository.py`
This file contains the `PublishedAppRepository` class, which is responsible for all database operations related to published apps.

**`PublishedAppRepository` Class**

| Method | Description | Parameters | Returns |
| --- | --- | --- | --- |
| `get_published_app_by_app_id` | Get a published app by app ID. | `app_id` | `PublishedApps` |
| `get_all_published_apps` | Get all published apps. | | `List[PublishedApps]` |
| `get_published_apps_for_user` | Get published apps visible to a specific user. | `email` | `List[PublishedApps]` |
| `publish_app` | Publish an app. | `app_id`, `publish_data` | `PublishedApps` |
| `update_published_app` | Update a published app. | `app_id`, `publish_data` | `PublishedApps` |
| `patch_published_app` | Partially update a published app. | `app_id`, `patch_data` | `PublishedApps` |
| `unpublish_app` | Unpublish an app. | `app_id` | `bool` |

### `sharepoint_repository.py`
This file contains the `SharePointRepository` class, which is responsible for all database operations related to SharePoint.

**`SharePointRepository` Class**

| Method | Description | Parameters | Returns |
| --- | --- | --- | --- |
| `get_user_by_email` | Get user by email using the session. | `email: str` | `User` |
| `get_user_token` | Get OAuth token from database using existing utility function. | `user_id: str`, `token_type: str = "sharepoint"` | `Dict[str, Any]` |

### `tool_repository.py`
This file contains the `ToolRepository` class, which is responsible for all database operations related to app tools.

**`ToolRepository` Class**

| Method | Description | Parameters | Returns |
| --- | --- | --- | --- |
| `get_tools_by_app_id` | Get all tools for an app. | `app_id` | `List[AppTools]` |
| `get_tool_by_type` | Get a specific tool by type. | `app_id`, `tool_type` | `AppTools` |
| `add_tool` | Add a new tool to an app. | `app_id`, `tool_type` | `AppTools` |
| `add_multiple_tools` | Add multiple tools to an app. | `app_id`, `tool_types` | `List[AppTools]` |
| `delete_tool` | Delete a tool by type. | `app_id`, `tool_type` | `bool` |
| `delete_all_tools` | Delete all tools for an app. | `app_id` | `int` |

### `topic_repository.py`
This file contains the `TopicRepository` class, which is responsible for all database operations related to topics.

**`TopicRepository` Class**

| Method | Description | Parameters | Returns |
| --- | --- | --- | --- |
| `get_topic_by_name` | Get a topic by its name. | `topic_name: str` | `Optional[TopicRegistry]` |
| `get_growth_status` | Determine status based on growth count. | `growth_count: int` | `str` |
| `update_topic_status_based_on_growth` | Update topic status based on its current growth count. | `topic_id: str` | `bool` |
| `update_topic_activity` | Update topic activity (increment count and update last_seen) with optional department update. | `topic_id: str`, `department: str = None` | `bool` |
| `update_topic_by_name` | Update topic activity by name with optional department update. | `topic_name: str`, `department: str = None`, `agent_id: str = None` | `bool` |
| `create_topic` | Create a new topic with department information. | `topic_name: str`, `department: str = None`, `agent_id: str = None` | `Optional[TopicRegistry]` |
| `get_all_topics` | Get all topics, optionally filtered by status and department. | `status: Optional[str] = None`, `department: Optional[str] = None` | `List[TopicRegistry]` |
| `get_popular_topics` | Get most popular topics with optional department filter. | `limit: int = 10`, `status: str = "Active"`, `department: Optional[str] = None` | `List[TopicRegistry]` |
| `get_recent_topics` | Get recently created topics with optional department filter. | `days: int = 30`, `limit: int = 10`, `department: Optional[str] = None` | `List[TopicRegistry]` |
| `get_trending_topics` | Get trending topics with departments filter. | `agent_id: Optional[str] = None`, `start_date: Optional[datetime] = None`, `end_date: Optional[datetime] = None`, `departments: Optional[List[str]] = None`, `limit: int = 20` | `List[TopicRegistry]` |
| `get_topic_analytics` | Get comprehensive topic analytics with growth-based status information. | | `Dict` |
| `deactivate_stale_topics` | Deactivate topics that haven't been seen for specified days. | `days_threshold: int = 90` | `int` |
| `search_topics` | Search topics by name with optional department filter. | `search_term: str`, `limit: int = 20`, `department: Optional[str] = None` | `List[TopicRegistry]` |
| `delete_topic` | Delete a topic by ID. | `topic_id: str` | `bool` |
| `update_topic_status` | Update topic status. | `topic_id: str`, `status: str` | `bool` |
| `get_topics_for_evolution` | Get topics for evolution analysis within specified date range with departments filter. | `start_date: Optional[datetime] = None`, `end_date: Optional[datetime] = None`, `min_growth: int = 1`, `limit: int = 50`, `agent_id: Optional[str] = None`, `departments: Optional[List[str]] = None` | `List[TopicRegistry]` |
| `migrate_topics_to_growth_status` | One-time migration to update all existing topics to use growth-based status. | | `Dict` |

### `trigger_repository.py`
This file contains the `TriggerRepository` class, which is responsible for all database operations related to app triggers.

**`TriggerRepository` Class**

| Method | Description | Parameters | Returns |
| --- | --- | --- | --- |
| `get_trigger_by_app_id` | Get the trigger for an app. | `app_id` | `AppTriggers` |
| `add_trigger` | Add a new trigger to an app. | `app_id`, `trigger_data` | `AppTriggers` |
| `update_trigger` | Update a trigger or create if it doesn't exist. | `app_id`, `trigger_data` | `AppTriggers` |
| `delete_trigger` | Delete a trigger by app ID. | `app_id` | `bool` |

### `workforce_agents_repository.py`
This file contains the `WorkforceAgentRepository` class, which is responsible for all database operations related to workforce agents.

**`WorkforceAgentRepository` Class**

| Method | Description | Parameters | Returns |
| --- | --- | --- | --- |
| `get_agent_by_app_id` | Get agent state by app ID. | `app_id: str` | `Optional[AgentState]` |
| `get_all_app_resources` | Fetches all resources associated with an app from the database, including local files. | `app_id: str` | `Dict[str, Any]` |
| `create_agent_state` | Create a new agent state in the database. | `agent_data: Dict[str, Any]` | `AgentState` |
| `update_agent_conversation` | Update agent conversation history. | `app_id: str`, `conversation_history: List[Dict[str, str]]` | `bool` |
| `delete_agent` | Delete an agent by app ID. | `app_id: str` | `bool` |
| `get_container_client` | Get a container client for the agent. | `cosmo_endpoint: str`, `cosmo_key: str`, `agent_state: AgentState` | `ContainerClient` |
| `update_agent_conversation_efficiently` | Update agent conversation with user query and assistant response in a single transaction. | `app_id: str`, `user_query: str`, `assistant_response: str` | `bool` |
