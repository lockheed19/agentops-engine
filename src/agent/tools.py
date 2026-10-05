from typing import Any, Dict, List
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from src.mock_services.telemetry import MockTelemetryService


# --- Pydantic Argument Schemas ---

class FetchMetricsInput(BaseModel):
    service_name: str = Field(
        description="Name of the microservice to query metrics for (e.g., 'payment-service')."
    )


class FetchLogsInput(BaseModel):
    service_name: str = Field(description="Name of the target service.")
    limit: int = Field(default=5, description="Number of recent log entries to retrieve.")


class InspectDBPoolInput(BaseModel):
    service_name: str = Field(
        description="Service name associated with the database connection pool."
    )


class ExecuteRemediationInput(BaseModel):
    action_type: str = Field(
        description="Type of remediation to execute (e.g., 'kill_blocking_query', 'scale_replica_set')."
    )
    target_service: str = Field(description="Name of the service receiving the action.")


# --- Structured LangChain Tools ---

@tool("get_service_metrics", args_schema=FetchMetricsInput)
async def get_service_metrics(service_name: str) -> Dict[str, Any]:
    """Query real-time infrastructure metrics (error rate, latency, CPU/memory usage) for a microservice."""
    return await MockTelemetryService.fetch_service_metrics(service_name)


@tool("get_service_logs", args_schema=FetchLogsInput)
async def get_service_logs(service_name: str, limit: int = 5) -> List[str]:
    """Fetch recent tail logs and error stack traces for a given service."""
    return await MockTelemetryService.fetch_recent_logs(service_name, limit)


@tool("inspect_db_connection_pool", args_schema=InspectDBPoolInput)
async def inspect_db_connection_pool(service_name: str) -> Dict[str, Any]:
    """Inspect database connection pool metrics, lock wait timeouts, and active blocking queries."""
    return await MockTelemetryService.inspect_db_connection_pool(service_name)


@tool("execute_remediation_action", args_schema=ExecuteRemediationInput)
async def execute_remediation_action(action_type: str, target_service: str) -> Dict[str, Any]:
    """Execute an automated remediation action on infrastructure. High impact: requires authorization."""
    return await MockTelemetryService.execute_remediation_action(action_type, target_service)


# Exported toolset
incident_tools = [
    get_service_metrics,
    get_service_logs,
    inspect_db_connection_pool,
    execute_remediation_action,
]