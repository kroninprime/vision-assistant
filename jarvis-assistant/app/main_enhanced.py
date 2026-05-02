"""
Enhanced JARVIS Main Application

Integrates:
✓ Wake word detection
✓ Screen awareness + OCR
✓ AI agent orchestrator
✓ Learning system
✓ Comprehensive logging
✓ Error handling
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any

from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from jarvis.config import load_settings, Settings
from jarvis import brain
from jarvis.memory import MemoryStore
from jarvis.wake_word import WakeWordListener
from jarvis.vision import ScreenReader, OCRHandler
from jarvis.agent import AIAgent
from jarvis.learning import LearningEngine
from jarvis.logging_system import create_logger_system, ErrorHandler
from jarvis.system_control import SystemControl

# Initialize logging
logger_system, logger = create_logger_system(Path("./logs"))

# Load settings
settings: Settings = load_settings()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR.parent / "app" / "static"

# Initialize core systems
memory = MemoryStore(settings.data_dir / "jarvis.db")
learning_engine = LearningEngine(settings.data_dir)
error_handler = ErrorHandler(learning_engine)
system_control = SystemControl()

# Initialize vision/screen awareness
screen_reader = ScreenReader()
ocr_handler = OCRHandler()

# Initialize AI Agent
ai_agent = AIAgent(brain, memory, settings)

# Initialize wake word listener
wake_word_listener = WakeWordListener(
    wake_words=["hey jarvis", "jarvis"],
    callback=lambda: logger.info("🎤 Wake word detected - ready for input"),
)

logger.info("🚀 JARVIS Enhanced System Initialized")
logger.info(f"Wake word listener ready: {wake_word_listener.is_listening()}")


class Command(BaseModel):
    text: str
    history: List[Dict[str, str]] | None = None


class ScreenAnalysisRequest(BaseModel):
    extract_text: bool = True


# FastAPI App
app = FastAPI(
    title="JARVIS Enhanced Assistant",
    version="2.0.0",
    description="Advanced AI agent with vision, learning, and automation"
)

# Serve static UI
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ============= API Routes =============

@app.get("/")
async def root() -> FileResponse:
    """Serve UI."""
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return FileResponse(BASE_DIR / "fallback.html")


@app.get("/status")
async def status() -> Dict[str, Any]:
    """System status."""
    return {
        "status": "ok",
        "version": "2.0.0",
        "wake_word_active": wake_word_listener.is_listening(),
        "learning_enabled": True,
        "screen_awareness": True,
        "ai_agent_ready": ai_agent is not None,
        "plan_running": ai_agent.is_executing(),
    }


@app.post("/command")
async def handle_command(command: Command) -> Dict[str, str]:
    """
    Process user command.
    
    Flow:
    1. Parse command
    2. Generate execution plan
    3. Execute multi-step tasks
    4. Learn from interaction
    5. Return result
    """
    try:
        logger.info(f"📝 Command received: {command.text}")
        
        learning_engine.learn_command(command.text)
        memory.add_history("user", command.text)

        response = brain.chat(settings, command.history or [], command.text)
        
        if any(keyword in command.text.lower() for keyword in 
               ["open", "close", "click", "type", "screenshot", "search", "launch", "browser", "screen"]):
            plan = ai_agent.plan_from_command(command.text, command.history)
            automation_result = ai_agent.execute_plan(plan)
            if automation_result:
                response += f"\n[Action result: {automation_result}]"
            learning_engine.learn_command(command.text, success=True)

        memory.add_history("assistant", response)
        logger.info(f"✓ Response: {response[:100]}...")
        return {"reply": response, "status": "success"}

    except Exception as e:
        error_msg = error_handler.handle_error(e, context="command_processing")
        logger.error(f"✗ Error processing command: {e}")
        memory.add_history("assistant", error_msg)
        return {"reply": error_msg, "status": "error"}


@app.post("/screen/analyze")
async def analyze_screen(request: ScreenAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze current screen.
    
    Captures screenshot and optionally extracts text via OCR.
    """
    try:
        logger.info("📸 Analyzing screen...")
        
        # Capture screen
        screenshot = screen_reader.capture_screen()
        screenshot_bytes = screen_reader.screenshot_to_bytes()
        
        result = {
            "screenshot_captured": True,
            "dimensions": screen_reader.get_screen_dimensions(),
            "description": screen_reader.get_screen_description(),
        }
        
        # Extract text if requested
        if request.extract_text:
            ocr_result = ocr_handler.extract_text_with_confidence(screenshot)
            result["extracted_text"] = ocr_result["text"][:500]  # First 500 chars
            result["text_confidence"] = ocr_result["confidence"]
            logger.info(f"OCR extracted text (confidence: {ocr_result['confidence']:.1%})")
        
        return result

    except Exception as e:
        error_msg = error_handler.handle_error(e, context="screen_analysis")
        return {"status": "error", "error": error_msg}


@app.post("/system/open-app")
async def open_app(app_name: str) -> Dict[str, str]:
    """Open application."""
    try:
        result = system_control.open_application(app_name)
        learning_engine.learn_command(f"open {app_name}")
        return {"status": "success", "message": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/system/close-app")
async def close_app(app_name: str) -> Dict[str, str]:
    """Close application."""
    try:
        result = system_control.close_application(app_name)
        return {"status": "success", "message": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/system/set-volume")
async def set_volume(level: int) -> Dict[str, str]:
    """Adjust system volume."""
    try:
        result = system_control.set_volume(level)
        return {"status": "success", "message": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/system/set-brightness")
async def set_brightness(level: int) -> Dict[str, str]:
    """Adjust screen brightness."""
    try:
        result = system_control.set_brightness(level)
        return {"status": "success", "message": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/system/execute")
async def execute_command(cmd: str) -> Dict[str, str]:
    """Execute a system command."""
    try:
        result = system_control.execute_command(cmd)
        return {"status": "success", "message": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/system/info")
async def system_info() -> Dict[str, Any]:
    """Get system information."""
    return {
        "info": system_control.get_system_info(),
        "running_processes": system_control.list_running_processes(),
    }


@app.get("/learning/profile")
async def get_learning_profile() -> Dict[str, Any]:
    """Get user learning profile."""
    try:
        return {
            "profile": learning_engine.analyze_patterns(),
            "summary": learning_engine.get_user_profile_summary(),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/learning/favorites")
async def get_favorite_commands() -> Dict[str, Any]:
    """Get favorite/frequently used commands."""
    try:
        favorites = learning_engine.get_favorite_commands(10)
        return {
            "favorite_commands": [
                {"command": cmd, "count": data["count"], "success_rate": 
                 (data["success_count"] / data["count"] if data["count"] > 0 else 0)}
                for cmd, data in favorites
            ]
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/errors/summary")
async def get_error_summary() -> Dict[str, str]:
    """Get error summary for debugging."""
    return {"summary": error_handler.get_error_summary()}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket for real-time interaction.
    
    Message format:
    {
        "type": "command" | "screenshot" | "status",
        "data": {...}
    }
    """
    await websocket.accept()
    logger.info("📡 WebSocket client connected")

    try:
        while True:
            message = await websocket.receive_json()
            msg_type = message.get("type", "command")
            msg_data = message.get("data", {})

            if msg_type == "command":
                # Process command
                cmd = Command(**msg_data)
                result = await handle_command(cmd)
                await websocket.send_json({"type": "response", "data": result})

            elif msg_type == "screenshot":
                # Analyze screen
                req = ScreenAnalysisRequest(**msg_data)
                result = await analyze_screen(req)
                await websocket.send_json({"type": "screenshot", "data": result})

            elif msg_type == "status":
                # Get status
                result = await status()
                await websocket.send_json({"type": "status", "data": result})

    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        logger.info("📡 WebSocket client disconnected")


@app.on_event("startup")
async def startup_event():
    """Run on app startup."""
    logger.info("🔧 JARVIS startup sequence...")
    
    # Start wake word listener
    wake_word_listener.start()
    logger.info("✓ Wake word listener activated")
    
    # Log learning profile
    logger.info(learning_engine.get_user_profile_summary())


@app.on_event("shutdown")
async def shutdown_event():
    """Run on app shutdown."""
    logger.info("🛑 JARVIS shutting down...")
    
    # Stop wake word listener
    wake_word_listener.stop()
    logger.info("✓ Wake word listener stopped")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting JARVIS Enhanced Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
