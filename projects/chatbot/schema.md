# Documentation for Schema Definitions

This document provides a comprehensive overview of the Pydantic schemas used in this project. These schemas define the data structures for API requests and responses, service bus messages, and other components, ensuring data consistency and validation across the application.

## Table of Contents

- [Enterprise-Grade Documentation for Schema Definitions](#enterprise-grade-documentation-for-schema-definitions)
  - [Table of Contents](#table-of-contents)
  - [1. `analytics_schemas.py`](#1-analytics_schemaspy)
    - [1.1. `TrendPoint`](#11-trendpoint)
    - [1.2. `PerformanceMetricsResponse`](#12-performancemetricsresponse)
    - [1.3. `AgentAnalyticsResponse`](#13-agentanalyticsresponse)
    - [1.4. `HeatmapResponse`](#14-heatmapresponse)
    - [1.5. `DepartmentAnalyticsResponse`](#15-departmentanalyticsresponse)
    - [1.6. `TopicAnalyticsResponse`](#16-topicanalyticsresponse)
    - [1.7. `RecommendationResponse`](#17-recommendationresponse)
  - [2. `common/base_schema.py`](#2-commonbase_schemapy)
    - [2.1. `ModelBaseInfo`](#21-modelbaseinfo)
    - [2.2. `FindBase`](#22-findbase)
    - [2.3. `SearchOptions`](#23-searchoptions)
    - [2.4. `FindResult`](#24-findresult)
    - [2.5. `FindDateRange`](#25-finddaterange)
    - [2.6. `DateRangeFilter`](#26-daterangefilter)
    - [2.7. `Blank`](#27-blank)
    - [2.8. `FindUniqueValues`](#28-finduniquevalues)
    - [2.9. `UniqueValuesResult`](#29-uniquevaluesresult)
  - [3. `dashboard.py`](#3-dashboardpy)
    - [3.1. `AnalyticsCreateRequest`](#31-analyticscreaterequest)
    - [3.2. `AnalyticsResponse`](#32-analyticsresponse)
  - [4. `errors.py`](#4-errorspy)
    - [4.1. `ErrorDetail`](#41-errordetail)
    - [4.2. `ErrorResponse`](#42-errorresponse)
    - [4.3. `ValidationErrorResponse`](#43-validationerrorresponse)
    - [4.4. `ConflictErrorResponse`](#44-conflicterrorresponse)
    - [4.5. `ServiceErrorResponse`](#45-serviceerrorresponse)
    - [4.6. `AuthErrorResponse`](#46-autherrorresponse)
    - [4.7. `ErrorCodes`](#47-errorcodes)
  - [5. `service_bus_schemas.py`](#5-service_bus_schemaspy)
    - [5.1. Enums](#51-enums)
    - [5.2. `BaseServiceBusMessage`](#52-baseservicebusmessage)
    - [5.3. `ChatMessageContent`](#53-chatmessagecontent)
    - [5.4. `ChatMessage`](#54-chatmessage)
    - [5.5. `ChatResponseContent`](#55-chatresponsecontent)
    - [5.6. `ChatResponse`](#56-chatresponse)
    - [5.7. `SystemNotification`](#57-systemnotification)
    - [5.8. `StatusUpdate`](#58-statusupdate)
    - [5.9. `ErrorNotification`](#59-errornotification)
    - [5.10. `MessageEnvelope`](#510-messageenvelope)
    - [5.11. `QueueHealthStatus`](#511-queuehealthstatus)
    - [5.12. `ServiceBusHealthCheck`](#512-servicebushealthcheck)
    - [5.13. `deserialize_message` function](#513-deserialize_message-function)
  - [6. `workflow_builder_schema.py`](#6-workflow_builder_schemapy)
    - [6.1. `AgentInfo`](#61-agentinfo)
    - [6.2. `UserQuery`](#62-userquery)
    - [6.3. `WorkforceResponse`](#63-workforceresponse)
  - [7. `workforce_builder_stepper_schema.py`](#7-workforce_builder_stepper_schemapy)
    - [7.1. `InstructionBase`](#71-instructionbase)
    - [7.2. `InstructionCreate`](#72-instructioncreate)
    - [7.3. `InstructionUpdate`](#73-instructionupdate)
    - [7.4. `AppCreate`](#74-appcreate)
    - [7.5. `AppUpdate`](#75-appupdate)
    - [7.6. `FileResource`](#76-fileresource)
    - [7.7. `FolderResource`](#77-folderresource)
    - [7.8. `ResourceResponse`](#78-resourceresponse)
    - [7.9. `TriggerUpdate`](#79-triggerupdate)
    - [7.10. `ConversationalTriggerCreate`](#710-conversationaltriggercreate)
    - [7.11. `TimeTriggerCreate`](#711-timetriggercreate)
    - [7.12. `TriggerResponse`](#712-triggerresponse)
    - [7.13. `ToolCreate`](#713-toolcreate)
    - [7.14. `PublishAppRequest`](#714-publishapprequest)
    - [7.15. `PublishedAppResponse`](#715-publishedappresponse)
    - [7.16. `PublishAppPatchRequest`](#716-publishapppatchrequest)
    - [7.17. `DataSourcePayload`](#717-datasourcepayload)
    - [7.18. `ToolUpdate`](#718-toolupdate)
    - [7.19. `ToolPayload`](#719-toolpayload)
    - [7.20. `BaseAgents`](#720-baseagents)
    - [7.21. `FindAgents`](#721-findagents)

---

## 1. `analytics_schemas.py`

This file defines the Pydantic models for analytics-related API responses, primarily for dashboard endpoints.

### 1.1. `TrendPoint`

A single data point in a time series trend.

| Field | Type | Description |
|---|---|---|
| `timestamp` | `datetime` | The timestamp of the data point. |
| `value` | `float` | The value of the data point. |
| `label` | `Optional[str]` | An optional label for the data point. |

### 1.2. `PerformanceMetricsResponse`

The response schema for performance metrics.

| Field | Type | Description |
|---|---|---|
| `avg_response_time` | `float` | Average response time in seconds. |
| `total_queries` | `int` | Total number of queries. |
| `satisfaction_rate` | `float` | Satisfaction rate percentage (0-100). |
| `query_volume_trend` | `List[TrendPoint]` | A list of `TrendPoint` objects representing query volume over time. |
| `response_time_trend` | `List[TrendPoint]` | A list of `TrendPoint` objects representing response time over time. |
| `satisfaction_trend` | `List[TrendPoint]` | A list of `TrendPoint` objects representing satisfaction rate over time. |
| `summary` | `Dict[str, Any]` | A dictionary containing summary statistics. |

### 1.3. `AgentAnalyticsResponse`

The response schema for agent-specific analytics.

| Field | Type | Description |
|---|---|---|
| `agent_id` | `str` | The ID of the agent. |
| `total_queries` | `int` | The total number of queries handled by the agent. |
| `avg_response_time` | `float` | The average response time of the agent. |
| `satisfaction_rate` | `float` | The satisfaction rate for the agent. |
| `top_queries` | `List[Dict[str, Any]]` | A list of the top queries handled by the agent. |
| `department_breakdown` | `Dict[str, int]` | A breakdown of queries by department. |

### 1.4. `HeatmapResponse`

The response schema for usage heatmap data.

| Field | Type | Description |
|---|---|---|
| `heatmap_data` | `Dict[str, Dict[str, int]]` | A nested dictionary with a date -> hour -> count structure. |

### 1.5. `DepartmentAnalyticsResponse`

The response schema for department analytics.

| Field | Type | Description |
|---|---|---|
| `department_counts` | `Dict[str, int]` | Query counts by department. |
| `total_queries` | `int` | Total queries across all departments. |
| `summary` | `Dict[str, Any]` | Summary statistics. |

### 1.6. `TopicAnalyticsResponse`

The response schema for topic analytics.

| Field | Type | Description |
|---|---|---|
| `emerging_topics` | `List[Dict[str, Any]]` | A list of emerging topics. |
| `topic_evolution` | `List[Dict[str, Any]]` | Data on the evolution of topics over time. |
| `topic_distribution` | `Dict[str, int]` | The distribution of queries across different topics. |

### 1.7. `RecommendationResponse`

The response schema for AI recommendations.

| Field | Type | Description |
|---|---|---|
| `id` | `str` | The ID of the recommendation. |
| `agent_id` | `str` | The ID of the agent for whom the recommendation is made. |
| `department` | `Optional[str]` | The department associated with the recommendation. |
| `title` | `str` | The title of the recommendation. |
| `description` | `str` | A description of the recommendation. |
| `type` | `str` | The type of recommendation. |
| `priority` | `str` | The priority of the recommendation. |
| `status` | `str` | The status of the recommendation. |
| `created_at` | `datetime` | The timestamp when the recommendation was created. |

---

## 2. `common/base_schema.py`

This file contains common base schemas used throughout the application for things like database models and query parameters.

### 2.1. `ModelBaseInfo`

A base schema for database models, including common fields.

| Field | Type | Description |
|---|---|---|
| `id` | `int` | The primary key of the model. |
| `uuid` | `UUID` | The UUID of the model. |
| `created_at` | `datetime` | The timestamp when the model was created. |
| `updated_at` | `datetime` | The timestamp when the model was last updated. |

### 2.2. `FindBase`

A base schema for search query parameters.

| Field | Type | Description |
|---|---|---|
| `ordering` | `Optional[str]` | The field to order the results by. |
| `page` | `Optional[int]` | The page number for pagination. |
| `page_size` | `Optional[int]` | The number of results per page. |
| `search` | `Optional[str]` | A search term. |

### 2.3. `SearchOptions`

Extends `FindBase` to include the total count of search results.

| Field | Type | Description |
|---|---|---|
| `total_count` | `Optional[int]` | The total number of results found. |

### 2.4. `FindResult`

The response schema for a search query.

| Field | Type | Description |
|---|---|---|
| `founds` | `Optional[List]` | A list of the search results. |
| `search_options` | `Optional[SearchOptions]` | The search options used for the query. |

### 2.5. `FindDateRange`

A schema for filtering by a date range.

| Field | Type | Description |
|---|---|---|
| `created_at__lt` | `str` | Less than the specified date. |
| `created_at__lte` | `str` | Less than or equal to the specified date. |
| `created_at__gt` | `str` | Greater than the specified date. |
| `created_at__gte` | `str` | Greater than or equal to the specified date. |

### 2.6. `DateRangeFilter`

A more structured schema for filtering by a date range.

| Field | Type | Description |
|---|---|---|
| `date_range_field` | `str` | The name of the datetime field to filter by. |
| `start_date` | `Optional[datetime]` | The start of the date range (inclusive). |
| `end_date` | `Optional[datetime]` | The end of the date range (inclusive). |

### 2.7. `Blank`

An empty schema that can be used as a placeholder.

### 2.8. `FindUniqueValues`

A schema for finding unique values for a specific field.

| Field | Type | Description |
|---|---|---|
| `field_name` | `str` | The name of the field to find unique values for. |

### 2.9. `UniqueValuesResult`

The response schema for a unique values query.

| Field | Type | Description |
|---|---|---|
| `founds` | `List[Any]` | A list of the unique values found. |
| `search_options` | `Optional[SearchOptions]` | The search options used for the query. |

---

## 3. `dashboard.py`

This file defines schemas related to the dashboard functionality.

### 3.1. `AnalyticsCreateRequest`

The request schema for creating a new analytics entry.

| Field | Type | Description |
|---|---|---|
| `query` | `str` | The query that was made. |
| `response` | `str` | The response that was given. |
| `is_liked` | `bool` | Whether the response was liked by the user. |

### 3.2. `AnalyticsResponse`

The response schema for an analytics entry.

| Field | Type | Description |
|---|---|---|
| `id` | `str` | The ID of the analytics entry. |
| `agent_id` | `str` | The ID of the agent that handled the query. |
| `query` | `str` | The query that was made. |
| `response` | `str` | The response that was given. |
| `is_liked` | `bool` | Whether the response was liked by the user. |
| `user_email` | `str` | The email of the user who made the query. |
| `created_at` | `datetime` | The timestamp when the entry was created. |
| `updated_at` | `datetime` | The timestamp when the entry was last updated. |

---

## 4. `errors.py`

This file defines structured error response models for consistent error handling across the API.

### 4.1. `ErrorDetail`

A schema for providing detailed information about an error.

| Field | Type | Description |
|---|---|---|
| `field` | `Optional[str]` | The field that caused the error. |
| `code` | `Optional[str]` | An error code for the specific error. |
| `message` | `str` | A human-readable error message. |
| `context` | `Optional[Dict[str, Any]]` | Additional context about the error. |

### 4.2. `ErrorResponse`

The standard error response format.

| Field | Type | Description |
|---|---|---|
| `error_code` | `str` | A machine-readable error code. |
| `message` | `str` | A human-readable error message. |
| `correlation_id` | `str` | A unique identifier for error tracking. |
| `timestamp` | `datetime` | The timestamp of the error. |
| `details` | `Optional[List[ErrorDetail]]` | A list of `ErrorDetail` objects with more information. |

### 4.3. `ValidationErrorResponse`

An error response for validation errors.

| Field | Type | Description |
|---|---|---|
| `error_code` | `str` | The error code, defaults to "VALIDATION_ERROR". |

### 4.4. `ConflictErrorResponse`

An error response for resource conflicts (e.g., duplicate items).

| Field | Type | Description |
|---|---|---|
| `error_code` | `str` | The error code, defaults to "RESOURCE_CONFLICT". |
| `conflicting_field` | `Optional[str]` | The field that caused the conflict. |
| `conflicting_value` | `Optional[str]` | The value that caused the conflict. |

### 4.5. `ServiceErrorResponse`

An error response for errors related to external services.

| Field | Type | Description |
|---|---|---|
| `error_code` | `str` | The error code, defaults to "SERVICE_ERROR". |
| `service_name` | `Optional[str]` | The name of the failing service. |
| `retry_after` | `Optional[int]` | The number of seconds to wait before retrying. |

### 4.6. `AuthErrorResponse`

An error response for authentication or authorization errors.

| Field | Type | Description |
|---|---|---|
| `error_code` | `str` | The error code, defaults to "AUTH_ERROR". |
| `auth_type` | `Optional[str]` | The type of authentication that failed. |

### 4.7. `ErrorCodes`

A class containing constants for standard error codes used in the application.

---

## 5. `service_bus_schemas.py`

This file defines Pydantic models for messages sent through Azure Service Bus, ensuring data integrity and type safety.

### 5.1. Enums

-   **`MessageType`**: An enum for the supported message types (`CHAT_MESSAGE`, `CHAT_RESPONSE`, etc.).
-   **`MessagePriority`**: An enum for message priority levels (`LOW`, `NORMAL`, `HIGH`, `URGENT`).
-   **`ProcessingStatus`**: An enum for the status of message processing (`PENDING`, `IN_PROGRESS`, etc.).

### 5.2. `BaseServiceBusMessage`

A base schema for all Service Bus messages.

| Field | Type | Description |
|---|---|---|
| `message_id` | `str` | A unique identifier for the message. |
| `correlation_id` | `str` | An ID for tracking related messages. |
| `message_type` | `MessageType` | The type of the message. |
| `timestamp` | `datetime` | The creation timestamp of the message. |
| `source` | `str` | The source system identifier. |
| `priority` | `MessagePriority` | The priority of the message. |
| `retry_count` | `int` | The number of retry attempts. |
| `session_id` | `Optional[str]` | A session identifier for message grouping. |
| `user_id` | `Optional[str]` | The identifier of the user. |

### 5.3. `ChatMessageContent`

The schema for the content of a chat message.

| Field | Type | Description |
|---|---|---|
| `message` | `str` | The text of the chat message. |
| `conversation_id` | `str` | The ID of the conversation. |
| `parent_message_id` | `Optional[str]` | The ID of the parent message for threading. |
| `attachments` | `List[Dict[str, Any]]` | A list of message attachments. |
| `metadata` | `Dict[str, Any]` | Additional message metadata. |

### 5.4. `ChatMessage`

The schema for a chat message sent to the processing queue.

| Field | Type | Description |
|---|---|---|
| `message_type` | `Literal[MessageType.CHAT_MESSAGE]` | The message type, fixed to `CHAT_MESSAGE`. |
| `content` | `ChatMessageContent` | The content of the chat message. |
| `processing_options` | `Dict[str, Any]` | Options for message processing (e.g., model, temperature). |
| `expected_response_time` | `Optional[int]` | The expected response time in seconds. |

### 5.5. `ChatResponseContent`

The schema for the content of a chat response.

| Field | Type | Description |
|---|---|---|
| `response` | `str` | The generated response text. |
| `response_id` | `str` | A unique identifier for the response. |
| `conversation_id` | `str` | The ID of the conversation. |
| `original_message_id` | `str` | The ID of the original message. |
| `model_used` | `str` | The AI model used for generation. |
| `processing_time` | `float` | The processing time in seconds. |
| `token_usage` | `Dict[str, int]` | Statistics on token usage. |
| `confidence_score` | `Optional[float]` | The confidence score of the response. |

### 5.6. `ChatResponse`

The schema for a chat response from processing.

| Field | Type | Description |
|---|---|---|
| `message_type` | `Literal[MessageType.CHAT_RESPONSE]` | The message type, fixed to `CHAT_RESPONSE`. |
| `content` | `ChatResponseContent` | The content of the chat response. |
| `status` | `ProcessingStatus` | The processing status. |
| `error_details` | `Optional[Dict[str, Any]]` | Details of any errors that occurred during processing. |

### 5.7. `SystemNotification`

The schema for system notifications.

| Field | Type | Description |
|---|---|---|
| `message_type` | `Literal[MessageType.SYSTEM_NOTIFICATION]` | The message type, fixed to `SYSTEM_NOTIFICATION`. |
| `notification_type` | `str` | The type of system notification. |
| `title` | `str` | The title of the notification. |
| `message` | `str` | The message of the notification. |
| `action_required` | `bool` | Whether action is required. |
| `action_url` | `Optional[str]` | The URL for the required action. |
| `expires_at` | `Optional[datetime]` | The expiration time of the notification. |

### 5.8. `StatusUpdate`

The schema for status update messages.

| Field | Type | Description |
|---|---|---|
| `message_type` | `Literal[MessageType.STATUS_UPDATE]` | The message type, fixed to `STATUS_UPDATE`. |
| `entity_type` | `str` | The type of the entity being updated. |
| `entity_id` | `str` | The ID of the entity. |
| `status` | `ProcessingStatus` | The current status. |
| `progress_percentage` | `Optional[int]` | The progress percentage (0-100). |
| `status_message` | `Optional[str]` | A detailed status message. |
| `estimated_completion` | `Optional[datetime]` | The estimated completion time. |

### 5.9. `ErrorNotification`

The schema for error notifications.

| Field | Type | Description |
|---|---|---|
| `message_type` | `Literal[MessageType.ERROR_NOTIFICATION]` | The message type, fixed to `ERROR_NOTIFICATION`. |
| `error_code` | `str` | An identifier for the error code. |
| `error_message` | `str` | A human-readable error message. |
| `error_details` | `Dict[str, Any]` | Detailed information about the error. |
| `stack_trace` | `Optional[str]` | The stack trace of the error. |
| `affected_entity_type` | `Optional[str]` | The type of the affected entity. |
| `affected_entity_id` | `Optional[str]` | The ID of the affected entity. |
| `resolution_steps` | `Optional[List[str]]` | Suggested steps for resolution. |
| `requires_manual_intervention` | `bool` | Whether manual intervention is required. |

### 5.10. `MessageEnvelope`

An envelope for Service Bus messages, including routing and delivery information.

| Field | Type | Description |
|---|---|---|
| `routing_key` | `str` | The routing key for the message. |
| `delivery_count` | `int` | The number of delivery attempts. |
| `enqueued_time` | `datetime` | The time the message was enqueued. |
| `scheduled_enqueue_time` | `Optional[datetime]` | The scheduled delivery time. |
| `time_to_live` | `Optional[int]` | The message TTL in seconds. |
| `message` | `Union[...]` | The actual message payload. |

### 5.11. `QueueHealthStatus`

The schema for the health status of a queue.

| Field | Type | Description |
|---|---|---|
| `queue_name` | `str` | The name of the queue. |
| `status` | `str` | The health status (e.g., "healthy", "unhealthy"). |
| `active_message_count` | `int` | The number of active messages. |
| `dead_letter_message_count` | `int` | The number of dead-letter messages. |
| `scheduled_message_count` | `int` | The number of scheduled messages. |
| `size_in_bytes` | `int` | The size of the queue in bytes. |
| `last_updated` | `datetime` | The timestamp of the last update. |
| `error_details` | `Optional[str]` | Details of any errors if the queue is unhealthy. |

### 5.12. `ServiceBusHealthCheck`

The schema for the overall Service Bus health check response.

| Field | Type | Description |
|---|---|---|
| `overall_status` | `str` | The overall health status. |
| `service_bus_connection` | `bool` | The status of the Service Bus connection. |
| `queues` | `List[QueueHealthStatus]` | A list of health statuses for individual queues. |
| `total_messages_processing` | `int` | The total number of messages being processed. |
| `last_health_check` | `datetime` | The timestamp of the last health check. |
| `alerts` | `List[str]` | A list of active health alerts. |

### 5.13. `deserialize_message` function

A function to deserialize a message dictionary to the appropriate Pydantic model.

-   **Parameters**: `message_data` (a dictionary containing the raw message data).
-   **Returns**: A deserialized message object.
-   **Raises**: `ValueError` if the message type is unknown or the data is invalid.

---

## 6. `workflow_builder_schema.py`

This file defines schemas related to the workflow builder.

### 6.1. `AgentInfo`

A schema for agent information.

| Field | Type | Description |
|---|---|---|
| `agent_type` | `str` | The type of the agent. |
| `container_client` | `Any` | The container client. |
| `conversation_history` | `List[Dict[str, str]]` | The history of the conversation. |
| `document_cont_id` | `str` | The ID of the document container. |
| `custom_prompt` | `str` | A custom prompt for the agent. |
| `trigger_documents` | `str` | The documents that trigger the agent. |

### 6.2. `UserQuery`

A schema for a user query.

| Field | Type | Description |
|---|---|---|
| `query` | `str` | The user's query. |
| `language` | `Optional[str]` | The detected or specified language. |
| `confidence` | `Optional[float]` | The confidence of the language detection. |
| `audio_quality` | `Optional[float]` | The quality score of the audio. |

### 6.3. `WorkforceResponse`

A schema for the response from the workforce agent.

| Field | Type | Description |
|---|---|---|
| `message` | `str` | A message from the agent. |
| `agent_type` | `str` | The type of the agent. |
| `response` | `str` | The response to the user's query. |
| `language` | `Optional[str]` | The language of the response. |
| `conversation_id` | `Optional[str]` | The ID of the conversation. |
| `metadata` | `Optional[Dict[str, Any]]` | Additional metadata. |

---

## 7. `workforce_builder_stepper_schema.py`

This file defines schemas for the multi-step workforce builder process.

### 7.1. `InstructionBase`

A base schema for an instruction.

| Field | Type | Description |
|---|---|---|
| `instruction` | `str` | The instruction text. |

### 7.2. `InstructionCreate`

A schema for creating a new instruction. Inherits from `InstructionBase`.

### 7.3. `InstructionUpdate`

A schema for updating an existing instruction. Inherits from `InstructionBase`.

### 7.4. `AppCreate`

A schema for creating a new application.

| Field | Type | Description |
|---|---|---|
| `email` | `EmailStr` | The user's email for the app. |
| `app_name` | `str` | The name of the application. |
| `description` | `Optional[str]` | A description of the application. |
| `logo` | `Optional[str]` | A URL to the application's logo. |

### 7.5. `AppUpdate`

A schema for updating an existing application.

| Field | Type | Description |
|---|---|---|
| `app_name` | `Optional[str]` | The name of the application. |
| `description` | `Optional[str]` | A description of the application. |
| `logo` | `Optional[str]` | A URL to the application's logo. |

### 7.6. `FileResource`

A schema for a file resource.

| Field | Type | Description |
|---|---|---|
| `file_name` | `str` | The name of the file. |
| `file_path` | `str` | The path to the file. |
| `file_id` | `str` | The ID of the file. |
| `drive_id` | `str` | The ID of the drive where the file is stored. |

### 7.7. `FolderResource`

A schema for a folder resource.

| Field | Type | Description |
|---|---|---|
| `folder_name` | `str` | The name of the folder. |
| `folder_path` | `str` | The path to the folder. |
| `folder_id` | `str` | The ID of the folder. |
| `drive_id` | `str` | The ID of the drive where the folder is stored. |

### 7.8. `ResourceResponse`

A schema for the response of a resource query.

| Field | Type | Description |
|---|---|---|
| `documents` | `List[dict]` | A list of documents. |
| `containers` | `List[dict]` | A list of containers. |
| `data_sources` | `List[dict]` | A list of data sources. |

### 7.9. `TriggerUpdate`

A schema for updating a trigger.

| Field | Type | Description |
|---|---|---|
| `trigger_type` | `str` | The type of the trigger. |
| `prompt` | `str` | The prompt for the trigger. |

### 7.10. `ConversationalTriggerCreate`

A schema for creating a conversational trigger.

| Field | Type | Description |
|---|---|---|
| `trigger_type` | `str` | The type of the trigger. |
| `prompt` | `str` | The prompt for the trigger. |

### 7.11. `TimeTriggerCreate`

A schema for creating a time-based trigger.

| Field | Type | Description |
|---|---|---|
| `trigger_type` | `str` | The type of the trigger. |
| `schedule` | `Dict[str, Any]` | The schedule for the trigger. |

### 7.12. `TriggerResponse`

A schema for the response of a trigger query.

| Field | Type | Description |
|---|---|---|
| `id` | `str` | The ID of the trigger. |
| `trigger_type` | `str` | The type of the trigger. |
| `prompt` | `Optional[str]` | The prompt for the trigger. |

### 7.13. `ToolCreate`

A schema for creating a tool.

| Field | Type | Description |
|---|---|---|
| `tool_type` | `str` | The type of the tool. |

### 7.14. `PublishAppRequest`

A schema for a request to publish an application.

| Field | Type | Description |
|---|---|---|
| `visibility` | `str` | The visibility of the application (e.g., "private", "public"). |
| `allowed_teammates` | `Optional[List[str]]` | A list of teammates who are allowed to access the app. |
| `iframe_params` | `Optional[Dict[str, Any]]` | Iframe parameters for public visibility. |

### 7.15. `PublishedAppResponse`

A schema for the response of a publish application request.

| Field | Type | Description |
|---|---|---|
| `id` | `str` | The ID of the published app. |
| `app_id` | `str` | The ID of the application. |
| `visibility` | `str` | The visibility of the application. |
| `published_at` | `datetime` | The timestamp when the app was published. |
| `published_by` | `str` | The user who published the app. |
| `allowed_teammates` | `Optional[List[str]]` | A list of teammates who are allowed to access the app. |
| `iframe_params` | `Optional[Dict[str, Any]]` | Iframe parameters for public visibility. |

### 7.16. `PublishAppPatchRequest`

A schema for a request to patch a published application.

| Field | Type | Description |
|---|---|---|
| `visibility` | `Optional[str]` | The visibility of the application. |
| `allowed_teammates` | `Optional[List[str]]` | A list of teammates who are allowed to access the app. |
| `iframe_params` | `Optional[Dict[str, Any]]` | Iframe parameters for public visibility. |

### 7.17. `DataSourcePayload`

A schema for a data source payload.

| Field | Type | Description |
|---|---|---|
| `sources` | `List[str]` | A list of data sources. |

### 7.18. `ToolUpdate`

A schema for updating tools.

| Field | Type | Description |
|---|---|---|
| `tools` | `List[str]` | A list of tool types as strings. |

### 7.19. `ToolPayload`

A schema for a tool payload.

| Field | Type | Description |
|---|---|---|
| `tools` | `List[str]` | A list of tools. |

### 7.20. `BaseAgents`

A base schema for agents.

| Field | Type | Description |
|---|---|---|
| `name` | `str` | The name of the agent. |
| `is_initialised` | `Optional[bool]` | Whether the agent has been initialized. |

### 7.21. `FindAgents`

A schema for finding agents.

| Field | Type | Description |
|---|---|---|
| `created_at_start` | `Optional[date]` | The start date for filtering by creation date. |
| `created_at_end` | `Optional[date]` | The end date for filtering by creation date. |
