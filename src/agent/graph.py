from typing import Literal
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from src.agent.nodes import (
    root_cause_synthesizer_node,
    tool_execution_node,
    triage_investigator_node,
    human_approval_gate_node
)
from src.core.state import AgentState

def should_continue(state: AgentState) -> Literal["execute_tools", "human_approval", "synthesize", "end"]:
    """Conditional router that intercepts high-impact remediation tools for human authorization."""
    messages = state["messages"]
    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        # Detect if any tool call is high-risk remediation
        has_remediation_call = any(
            tc["name"] == "execute_remediation_action" for tc in last_message.tool_calls
        )
        if has_remediation_call:
            # Route to human gate if not previously approved
            if not state.get("remediation_approved"):
                return "human_approval"
            return "execute_tools"

        return "execute_tools"

    # Route to root cause synthesis when diagnostic investigation completes
    if len(messages) > 1:
        return "synthesize"

    return "end"

def build_incident_graph():
    """Constructs the stateful LangGraph DAG with HITL pause checkpoints."""
    workflow = StateGraph(AgentState)

    # 1. Add Nodes
    workflow.add_node("investigate", triage_investigator_node)
    workflow.add_node("human_approval", human_approval_gate_node)
    workflow.add_node("execute_tools", tool_execution_node)
    workflow.add_node("synthesize", root_cause_synthesizer_node)

    # 2. Add Edges & Conditional Routing
    workflow.add_edge(START, "investigate")

    workflow.add_conditional_edges(
        "investigate",
        should_continue,
        {
            "execute_tools": "execute_tools",
            "human_approval": "human_approval",
            "synthesize": "synthesize",
            "end": END,
        },
    )

    # # After running tools, loop back to the investigator to evaluate new evidence
    # workflow.add_edge("execute_tools", "investigate")
    # workflow.add_edge("synthesize", END)
    workflow.add_edge("human_approval", "execute_tools")
    workflow.add_edge("execute_tools", "investigate")
    workflow.add_edge("synthesize", END)

    # In-memory checkpointer for thread-safe state persistence
    checkpointer = MemorySaver()

    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_approval"]
    )

incident_agent_app = build_incident_graph()