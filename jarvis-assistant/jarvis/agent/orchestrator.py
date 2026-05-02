"""Main AI Agent orchestrator - plans and executes multi-step tasks."""
import logging
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from jarvis.system_control import SystemControl

logger = logging.getLogger("jarvis.agent")


class TaskState(Enum):
    """Task execution states."""
    PLANNED = "planned"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class Task:
    """Single task unit."""
    id: str
    name: str
    action: str
    params: Dict[str, Any]
    state: TaskState = TaskState.PLANNED
    result: Optional[str] = None
    error: Optional[str] = None


@dataclass
class Plan:
    """Multi-step execution plan."""
    goal: str
    tasks: List[Task]
    created_at: str
    completed_at: Optional[str] = None


class AIAgent:
    """Orchestrates multi-step task execution."""

    def __init__(self, brain, memory_store, settings=None):
        self.brain = brain
        self.memory = memory_store
        self.settings = settings
        self.system_control = SystemControl()
        self.current_plan: Optional[Plan] = None
        self.task_handlers: Dict[str, callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        from jarvis.automation import files, web

        self.task_handlers = {
            "open_app": self._handle_open_app,
            "close_app": self._handle_close_app,
            "type_text": self._handle_type_text,
            "click": self._handle_click,
            "screenshot": self._handle_screenshot,
            "analyze_screen": self._handle_analyze_screen,
            "read_file": files.handle_files,
            "execute_command": self._handle_execute_command,
            "search_web": web.handle_web,
        }

    def plan_from_command(self, command: str, history: List[Dict] = None) -> Plan:
        history = history or []
        prompt = f"""You are an AI assistant planning multi-step tasks.

User command: "{command}"

Generate a structured plan with numbered steps. Each step must use one of the available actions exactly.

Available actions:
- open_app
- close_app
- type_text
- click
- screenshot
- analyze_screen
- search_web
- execute_command

Format each step like this:
STEP 1: open_app - chrome
STEP 2: search_web - black holes
STEP 3: type_text - find the nearest NASA website

If no automation is needed, return a single execute_command step with the original command.
"""

        plan_text = self.brain.chat(self.settings, history, prompt)
        logger.info(f"Generated plan for '{command}':\n{plan_text}")

        tasks = self._parse_plan_text(plan_text, command)
        plan = Plan(goal=command, tasks=tasks, created_at=datetime.now().isoformat())
        self.current_plan = plan
        return plan

    def _parse_plan_text(self, plan_text: str, original_command: str) -> List[Task]:
        tasks: List[Task] = []
        lines = [line.strip() for line in plan_text.splitlines() if line.strip()]

        for index, line in enumerate(lines):
            step_content = line
            match = re.match(r"^step\s*\d+\s*[:.-]?\s*(.*)$", line, re.I)
            if match:
                step_content = match.group(1).strip()

            action, param_text = self._split_action(step_content)
            params = self._build_params(action, param_text, original_command)
            task_id = f"task_{index}"
            tasks.append(Task(id=task_id, name=step_content, action=action, params=params))

        if not tasks:
            tasks = [Task(
                id="task_0",
                name="Execute command",
                action="execute_command",
                params={"command": original_command},
            )]

        return tasks

    def _split_action(self, text: str) -> tuple[str, str]:
        if "-" in text:
            action, params = text.split("-", 1)
        elif ":" in text:
            action, params = text.split(":", 1)
        else:
            action, params = text, ""
        return action.strip().lower().replace(" ", "_"), params.strip()

    def _build_params(self, action: str, text: str, original_command: str) -> Dict[str, Any]:
        if action in {"open_app", "open"}:
            return {"app_name": text or self._extract_app_name(original_command)}
        if action in {"close_app", "close"}:
            return {"app_name": text or self._extract_app_name(original_command)}
        if action in {"type_text", "type"}:
            return {"text": text or original_command}
        if action == "click":
            coords = re.findall(r"(-?\d+)", text)
            params = {"description": text}
            if len(coords) >= 2:
                params["x"] = int(coords[0])
                params["y"] = int(coords[1])
            return params
        if action in {"search_web", "search", "google_search"}:
            return {"query": text or original_command}
        if action in {"execute_command", "execute", "run_command"}:
            return {"command": text or original_command}
        if action in {"screenshot", "analyze_screen"}:
            return {}

        return {"command": text or original_command}

    def _extract_app_name(self, command: str) -> str:
        words = command.lower().split()
        for candidate in ["chrome", "edge", "firefox", "notepad", "calculator", "explorer", "powershell"]:
            if candidate in words:
                return candidate
        return command

    def execute_plan(self, plan: Optional[Plan] = None) -> str:
        plan = plan or self.current_plan
        if not plan:
            return "No plan to execute"

        logger.info(f"Executing plan: {plan.goal}")
        results: List[str] = []

        for task in plan.tasks:
            try:
                task.state = TaskState.EXECUTING
                logger.info(f"Executing task: {task.name}")
                handler = self.task_handlers.get(task.action)
                if not handler:
                    handler = self._handle_execute_command
                    task.action = "execute_command"

                result = handler(**task.params)
                task.result = str(result)
                task.state = TaskState.COMPLETED
                results.append(str(result))
                logger.info(f"✓ Task complete: {task.name}")
            except Exception as exc:
                task.error = str(exc)
                task.state = TaskState.FAILED
                results.append(f"Task failed: {task.name} -> {exc}")
                logger.error(f"✗ Task failed: {task.name} - {exc}", exc_info=True)

        self.memory.store_action(
            action="plan_executed",
            input=plan.goal,
            output="\n".join(results),
        )
        plan.completed_at = datetime.now().isoformat()
        return "\n".join(results)

    async def execute_plan_async(self, plan: Optional[Plan] = None) -> str:
        return self.execute_plan(plan)

    def _handle_open_app(self, app_name: str, **kwargs) -> str:
        return self.system_control.open_application(app_name)

    def _handle_close_app(self, app_name: str, **kwargs) -> str:
        return self.system_control.close_application(app_name)

    def _handle_type_text(self, text: str, **kwargs) -> str:
        import pyautogui
        import time
        try:
            time.sleep(0.5)
            pyautogui.typewrite(text)
            return f"Typed: {text}"
        except Exception as exc:
            return f"Failed to type text: {exc}"

    def _handle_click(self, x: int = None, y: int = None, description: str = "", **kwargs) -> str:
        import pyautogui
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y)
                return f"Clicked at ({x}, {y})"
            pyautogui.click()
            return f"Clicked: {description or 'default position'}"
        except Exception as exc:
            return f"Failed to click: {exc}"

    def _handle_screenshot(self, **kwargs) -> str:
        from jarvis.vision import ScreenReader
        try:
            sr = ScreenReader()
            sr.capture_screen()
            path = sr.save_screenshot()
            return f"Screenshot saved: {path}"
        except Exception as exc:
            return f"Failed to take screenshot: {exc}"

    def _handle_analyze_screen(self, **kwargs) -> str:
        from jarvis.vision import ScreenReader, OCRHandler
        try:
            sr = ScreenReader()
            image = sr.capture_screen()
            ocr = OCRHandler()
            text = ocr.extract_text_from_image(image)
            return f"Screen text: {text[:500]}"
        except Exception as exc:
            return f"Failed to analyze screen: {exc}"

    def _handle_execute_command(self, command: str, check: bool = False, **kwargs) -> str:
        return self.system_control.execute_command(command, check=check)

    def is_executing(self) -> bool:
        return bool(self.current_plan and any(t.state == TaskState.EXECUTING for t in self.current_plan.tasks))
