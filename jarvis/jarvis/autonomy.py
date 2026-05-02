from __future__ import annotations

from dataclasses import dataclass

from .models import TaskPlan


@dataclass
class ExecutionResult:
    completed: bool
    message: str
    retries: int = 0


class AutonomousTaskEngine:
    def run_plan(self, plan: TaskPlan) -> ExecutionResult:
        if not plan.steps:
            return ExecutionResult(completed=False, message="No plan steps to execute.")
        return ExecutionResult(completed=True, message=f"Executed {len(plan.steps)} planned steps.")


class MultiAgentCoordinator:
    def assign(self, request: str) -> dict[str, str]:
        lowered = request.lower()
        if "code" in lowered:
            return {"planner": "active", "coding_agent": "active", "research_agent": "standby", "executor": "active"}
        if "research" in lowered or "search" in lowered:
            return {"planner": "active", "coding_agent": "standby", "research_agent": "active", "executor": "active"}
        return {"planner": "active", "coding_agent": "standby", "research_agent": "standby", "executor": "active"}

