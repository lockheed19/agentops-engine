import asyncio
from langchain_core.messages import HumanMessage
from src.agent.graph import incident_agent_app


async def main():
    thread_config = {"configurable": {"thread_id": "INC-89214"}}

    initial_state = {
        "messages": [
            HumanMessage(
                content="Alert fired: P99 latency on payment-service is 3400ms and error rate spiked to 18%. Investigate and resolve."
            )
        ],
        "incident_id": "INC-89214",
        "service_name": "payment-service",
        "severity": "SEV-1",
        "logs_analyzed": [],
        "remediation_executed": False,
    }

    print("=== STARTING AGENT TRIAGE INVOCATION ===")
    
    # Run agent until it hits the interrupt checkpoint
    async for event in incident_agent_app.astream(initial_state, config=thread_config):
        for node_name, state_update in event.items():
            print(f"\n--- [NODE COMPLETED]: {node_name} ---")
            if "messages" in state_update and state_update["messages"]:
                last_msg = state_update["messages"][-1]
                print(f"Message Output: {last_msg.content}")
                if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                    print(f"Tool Calls Initiated: {last_msg.tool_calls}")

    # Inspect graph state at pause boundary
    current_state = await incident_agent_app.aget_state(thread_config)
    print("\n=== AGENT PAUSED FOR HUMAN AUTHORIZATION ===")
    print(f"Next Node to Execute: {current_state.next}")

    # Simulate human operator authorizing the remediation
    print("\n=== OPERATOR GRANTS REMEDIATION APPROVAL ===")
    await incident_agent_app.aupdate_state(
        thread_config,
        {"remediation_approved": True},
        as_node="human_approval",
    )

    # Resume graph execution from checkpoint
    print("\n=== RESUMING AGENT GRAPH EXECUTION ===")
    async for event in incident_agent_app.astream(None, config=thread_config):
        for node_name, state_update in event.items():
            print(f"\n--- [NODE COMPLETED]: {node_name} ---")
            if "messages" in state_update and state_update["messages"]:
                last_msg = state_update["messages"][-1]
                print(f"Output: {last_msg.content}")


if __name__ == "__main__":
    asyncio.run(main())