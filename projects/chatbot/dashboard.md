# Dashboard Documentation

## 1. Overview

The `DashboardAPIClient` is a high-level asynchronous client designed to facilitate communication with the backend services for the Government Assistance Workforce dashboard. It is built to be used within an environment where a user is already authenticated, leveraging the user's existing access and refresh tokens for seamless and secure API interactions.

The client handles complexities such as token management, automatic token refreshing, and request retries, allowing developers to focus on implementing dashboard features rather than low-level request logic.

## 2. Core Features

- **Asynchronous by Design**: Built on `httpx`, the client is fully asynchronous (`async/await`), making it suitable for modern, high-performance web applications.
- **Seamless Authentication**: Utilizes the logged-in user's JWT access token for all API requests.
- **Automatic Token Refresh**: Intelligently refreshes the access token in the background before it expires, preventing interruptions and `401 Unauthorized` errors.
- **Resilient API Requests**: Implements automatic retry logic for requests that fail due to transient network issues or temporary `401` errors (post-token refresh).
- **Context Management**: Can be used as an async context manager (`async with`) for clean setup and teardown of resources, including the background token refresh task.
- **Structured Endpoint Methods**: Provides dedicated, easy-to-use methods for all dashboard-specific API endpoints.

## 3. Getting Started

### Installation

The client requires the `httpx` library. Ensure it is installed in your environment:

```bash
pip install httpx
```

### Initialization and Usage

To use the client, you need the user's `access_token` and `refresh_token`. In a typical web application, the access token is obtained from the `Authorization` header, and the refresh token is retrieved from a secure cookie.

Here is a basic example of how to initialize and use the client:

```python
import asyncio

from dashboard.api_client import DashboardAPIClient

async def main():
    # In a real application, these tokens would be retrieved from the
    # user's session, headers, or secure storage.
    api_url = "https://api.example.com"
    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    refresh_token = "def50200f0..." # From a secure cookie

    # Initialize the client
    api_client = DashboardAPIClient(
        api_url=api_url,
        access_token=access_token,
        refresh_token=refresh_token
    )

    # Use the client as an async context manager
    async with api_client:
        try:
            # Fetch dashboard overview data
            overview_data = await api_client.get_dashboard_overview(
                departments=["claims-processing", "customer-support"]
            )
            print("Dashboard Overview:", overview_data)

            # Fetch performance data for a specific time range
            performance_data = await api_client.get_dashboard_performance(
                start_date="2025-07-01",
                end_date="2025-07-31",
                time_granularity="week"
            )
            print("Performance Data:", performance_data)

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 4. Class: `DashboardAPIClient`

### `__init__(self, api_url, access_token, refresh_token)`

Initializes the API client.

- **`api_url` (str)**: The base URL for the backend API (e.g., `https://api.example.com`).
- **`access_token` (str)**: The user's JWT access token.
- **`refresh_token` (Optional[str])**: The user's refresh token, used for automatic token renewal. If not provided, the client cannot refresh the session.

---

## 5. API Endpoint Methods

This section details the methods available for interacting with specific dashboard API endpoints. All methods are `async` and return a dictionary parsed from the JSON response. They will raise an `httpx.HTTPStatusError` for non-2xx responses.

### 5.1. Dashboard Data

#### `get_dashboard_overview(...)`
Retrieves a high-level overview of Key Performance Indicators (KPIs).

- **Endpoint**: `GET /api/v1/dashboard/overview`
- **Parameters**:
    - `agent_id` (Optional[str]): Filter KPIs for a specific agent.
    - `departments` (Optional[list]): Filter by a list of department names.
    - `start_date` (Optional[str]): Start date for the data range (`YYYY-MM-DD`).
    - `end_date` (Optional[str]): End date for the data range (`YYYY-MM-DD`).
- **Returns**: `Dict[str, Any]` containing overview data and KPIs.

#### `get_dashboard_performance(...)`
Fetches performance metrics and trend data over a specified period.

- **Endpoint**: `GET /api/v1/dashboard/performance`
- **Parameters**:
    - `agent_id` (Optional[str]): Filter for a specific agent.
    - `departments` (Optional[list]): Filter by a list of department names.
    - `start_date` (Optional[str]): Start date (`YYYY-MM-DD`).
    - `end_date` (Optional[str]): End date (`YYYY-MM-DD`).
    - `time_granularity` (str): The granularity for trend data. Can be `hour`, `day`, `week`, or `month`. Defaults to `day`.
- **Returns**: `Dict[str, Any]` containing performance metrics and trends.

#### `get_dashboard_agents(...)`
Gets a list of all agents accessible to the current user.

- **Endpoint**: `GET /api/v1/dashboard/agents`
- **Parameters**:
    - `departments` (Optional[list]): Filter agents by department.
    - `include_metrics` (bool): Whether to include basic performance metrics for each agent. Defaults to `True`.
- **Returns**: `Dict[str, Any]` containing a list of agents.

#### `get_dashboard_departments(...)`
Retrieves analytics and performance data aggregated by department.

- **Endpoint**: `GET /api/v1/dashboard/departments`
- **Parameters**:
    - `start_date` (Optional[str]): Start date (`YYYY-MM-DD`).
    - `end_date` (Optional[str]): End date (`YYYY-MM-DD`).
- **Returns**: `Dict[str, Any]` containing department-level analytics.

#### `get_dashboard_topics(...)`
Fetches trending topics from user interactions and their evolution over time.

- **Endpoint**: `GET /api/v1/dashboard/topics`
- **Parameters**:
    - `agent_id` (Optional[str]): Filter topics for a specific agent.
    - `departments` (Optional[list]): Filter by department.
    - `limit` (int): The maximum number of topics to return. Defaults to `20`.
    - `include_trends` (bool): Whether to include trend data for each topic. Defaults to `True`.
- **Returns**: `Dict[str, Any]` containing topic analytics.

#### `get_dashboard_heatmap(...)`
Gets data for generating a usage heatmap (e.g., activity by day/hour).

- **Endpoint**: `GET /api/v1/dashboard/usage-heatmap`
- **Parameters**:
    - `agent_id` (Optional[str]): Filter for a specific agent.
    - `departments` (Optional[list]): Filter by department.
    - `days` (int): The number of past days to include in the heatmap data. Defaults to `7`.
- **Returns**: `Dict[str, Any]` containing data points for the heatmap.

#### `get_dashboard_recommendations(...)`
Fetches AI-generated recommendations for operational improvements.

- **Endpoint**: `GET /api/v1/dashboard/recommendations`
- **Parameters**:
    - `agent_id` (Optional[str]): Filter recommendations for a specific agent.
    - `departments` (Optional[list]): Filter by department.
    - `priority` (Optional[str]): Filter by priority level (`Urgent`, `High`, `Medium`, `Low`).
    - `status` (str): Filter by status (`Open`, `Resolved`). Defaults to `Open`.
- **Returns**: `Dict[str, Any]` containing a list of recommendations.

### 5.2. Data Export

#### `export_dashboard_data(...)`
Exports a specified type of dashboard data in a chosen format.

- **Endpoint**: `GET /api/v1/dashboard/export`
- **Parameters**:
    - `data_type` (str): The type of data to export (`overview`, `performance`, `agents`, `departments`, `topics`).
    - `format` (str): The desired export format (`json`, `csv`, `excel`). Defaults to `json`.
    - `agent_id`, `departments`, `start_date`, `end_date`: Optional filters corresponding to the selected `data_type`.
- **Returns**: `Dict[str, Any]` containing the exported data, often with a link or payload.

---

## 6. Core Client Methods

These methods form the foundation of the client's functionality.

#### `request(method, endpoint, ...)`
The core method for making any authenticated API request. The higher-level methods (e.g., `get_dashboard_overview`) use this internally. It handles adding the auth header, making the request, and initiating a token refresh/retry cycle on `401` errors.

#### `refresh_auth()`
Manually triggers the token refresh process. This is typically handled automatically by the background task but can be called directly if needed.

#### `update_tokens(access_token, refresh_token)`
Allows for external updates of the tokens stored in the client instance. This is useful if the authentication flow in the parent application provides new tokens that the client should use.

#### `close()`
Gracefully closes the client's session and cancels any background tasks. It's important to call this to ensure clean resource cleanup if not using the `async with` block.

---

## 7. Legacy Methods

These methods are maintained for backward compatibility. It is recommended to use the new `get_dashboard_*` methods where possible.

#### `get_analytics_performance(...)`
**Legacy**: Use `get_dashboard_performance` instead. This method now redirects its call to `get_dashboard_performance`.

#### `get_agent_analytics(agent_id, ...)`
**Legacy**: Fetches raw analytics records for a specific agent.

- **Endpoint**: `GET /api/v1/analytics/agent/{agent_id}`
- **Returns**: `list` of analytics records.

---

## 8. Helper Functions

### `create_client_from_browser_tokens(...)`
A utility function to simplify client instantiation from common browser-based token sources.

- **Parameters**:
    - `api_url` (str): The API base URL.
    - `auth_header` (str): The full value of the `Authorization` header (e.g., `"Bearer eyJ..."`).
    - `refresh_token` (Optional[str]): The refresh token.
- **Returns**: A new `DashboardAPIClient` instance.

## 9. Error Handling

The client is designed to be robust.
- **Successful Requests**: Methods for specific endpoints return a dictionary parsed from the API's JSON response.
- **HTTP Errors**: If the API returns an error status code (e.g., 4xx or 5xx) that is not a `401` (which triggers a retry), the method will raise an `httpx.HTTPStatusError`. It is the responsibility of the caller to catch and handle these exceptions.
- **Token Refresh Failure**: If the token refresh mechanism fails, an error is logged, and the background refresh loop will stop. Subsequent API calls will likely fail with a `401` error until the client is re-initialized with valid tokens.
