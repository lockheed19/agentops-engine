from typing import Annotated, Any, Dict, List, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class IncidentMetrics(TypedDict):
    service_name: str
    error_rate: float
    p99_latency_ms: float
    cpu_utilization: float
    memory_utilization: float

class AgentState(TypedDict):
    # Annotates message list to append new messages instead of overwriting
    messages: Annotated[List[BaseMessage], add_messages]
    
    incident_id: str
    service_name: str
    severity: str
    
    # State flags accumulated during graph execution
    telemetry_data: Optional[IncidentMetrics]
    logs_analyzed: List[str]
    root_cause_hypothesis: Optional[str]
    proposed_remediation: Optional[Dict[str, Any]]
    remediation_approved: Optional[bool]
    remediation_executed: bool