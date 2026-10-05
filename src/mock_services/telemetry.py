import asyncio
from typing import Any, Dict, List

class MockTelemetryService:
    """Simulates async infrastructure telemetry (Prometheus, Datadog, Postgres logs)."""

    @staticmethod
    async def fetch_service_metrics(service_name: str) -> Dict[str, Any]:
        await asyncio.sleep(0.2)  # Simulate I/O latency
        
        if service_name.lower() == "payment-service":
            return {
                "service_name": service_name,
                "error_rate": 0.18,  # 18% error rate (threshold is > 5%)
                "p99_latency_ms": 3400.0,
                "cpu_utilization": 0.88,
                "memory_utilization": 0.65,
                "status": "DEGRADED",
            }
        
        return {
            "service_name": service_name,
            "error_rate": 0.001,
            "p99_latency_ms": 45.0,
            "cpu_utilization": 0.25,
            "memory_utilization": 0.40,
            "status": "HEALTHY",
        }

    @staticmethod
    async def fetch_recent_logs(service_name: str, limit: int = 5) -> List[str]:
        await asyncio.sleep(0.2)
        if service_name.lower() == "payment-service":
            return [
                "2026-10-05T11:30:01Z [ERROR] DBConnectionTimeout: Pool exhausted (max=50 connections)",
                "2026-10-05T11:30:02Z [WARN] Retrying query 'SELECT * FROM transactions WHERE user_id = $1' (attempt 3/3)",
                "2026-10-05T11:30:03Z [ERROR] Query Execution Failed: Lock Wait Timeout Exceeded on table 'orders'",
                "2026-10-05T11:30:05Z [FATAL] HTTP 504 Gateway Timeout propagated to upstream client",
                "2026-10-05T11:30:06Z [INFO] Health check failing on pod payment-service-7f8d9b-x2k9l",
            ][:limit]
        return ["2026-10-05T11:30:00Z [INFO] Heartbeat OK"]

    @staticmethod
    async def inspect_db_connection_pool(service_name: str) -> Dict[str, Any]:
        await asyncio.sleep(0.15)
        return {
            "service": service_name,
            "active_connections": 50,
            "max_connections": 50,
            "idle_connections": 0,
            "blocking_queries": [
                {
                    "pid": 84920,
                    "query": "UPDATE orders SET status = 'PROCESSING' WHERE status = 'PENDING';",
                    "duration_seconds": 142.5,
                    "lock_type": "ExclusiveLock",
                }
            ],
        }

    @staticmethod
    async def execute_remediation_action(action_type: str, target_service: str) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        if action_type == "kill_blocking_query":
            return {
                "success": True,
                "action": action_type,
                "target": target_service,
                "details": "Terminated PID 84920. Connection pool active connections dropped to 12/50. Latency normalized.",
            }
        elif action_type == "scale_replica_set":
            return {
                "success": True,
                "action": action_type,
                "target": target_service,
                "details": "Scaled pod replicas from 3 to 6.",
            }
        return {"success": False, "error": f"Unknown remediation action: {action_type}"}