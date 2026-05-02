"""
Quick Example: Using JARVIS 2.0 Enhanced

This shows how to use each new system.
"""

# Example 1: Wake Word Detection
print("\n=== 1. Wake Word Detection ===")
from jarvis.wake_word import WakeWordListener

def on_wake_word():
    print("🎤 Wake word detected! Ready to listen...")

listener = WakeWordListener(callback=on_wake_word)
listener.start()
print("Listening for 'Hey Jarvis'...")
# listener.stop()  # Stop when done


# Example 2: Screen Awareness
print("\n=== 2. Screen Awareness ===")
from jarvis.vision import ScreenReader, OCRHandler

screen_reader = ScreenReader()
screenshot = screen_reader.capture_screen()
screen_reader.save_screenshot("my_screen.png")

ocr = OCRHandler()
text = ocr.extract_text_from_image(screenshot)
print(f"Extracted {len(text)} characters from screen")


# Example 3: AI Agent with Multi-Step Planning
print("\n=== 3. Multi-Step Task Planning ===")
from jarvis.agent import AIAgent
from jarvis import brain
from jarvis.memory import MemoryStore
from pathlib import Path

memory = MemoryStore(Path("./data/jarvis.db"))

# This would normally use OpenAI/Claude
# agent = AIAgent(brain, memory)
# plan = agent.plan_from_command("Open Chrome and search for Python")
# result = agent.execute_plan(plan)
# print(f"Execution result: {result}")


# Example 4: Learning System
print("\n=== 4. User Learning ===")
from jarvis.learning import LearningEngine

learner = LearningEngine(Path("./data/jarvis.db"))

# Learn from interactions
learner.learn_command("open chrome")
learner.learn_command("open chrome", success=True)
learner.learn_command("open chrome", success=True)
learner.learn_preference("browser", "Chrome")

# Query learned information
print("Favorite commands:", learner.get_favorite_commands(3))
print("Browser preference:", learner.get_preference("browser"))
print("\nProfile Summary:")
print(learner.get_user_profile_summary())


# Example 5: System Control
print("\n=== 5. System Control ===")
from jarvis.system_control import SystemControl

system = SystemControl()

# Open application (Windows example)
# result = system.open_application("notepad")
# print(result)

# Check system info
print("System info:", system.get_system_info())


# Example 6: Logging & Error Handling
print("\n=== 6. Logging & Error Handling ===")
from jarvis.logging_system import create_logger_system, ErrorHandler

logger_system, logger = create_logger_system(Path("./logs"))
logger.info("This is a test log message")

error_handler = ErrorHandler(learner)
try:
    result = 10 / 0
except Exception as e:
    msg = error_handler.handle_error(e, context="division_test", recovery_action="Use non-zero divisor")
    print(msg)


# Example 7: Full Integration (FastAPI Server)
print("\n=== 7. Running Enhanced JARVIS Server ===")
print("""
To start the enhanced JARVIS server:

    python -m uvicorn app.main_enhanced:app --reload

Then visit:
    http://localhost:8000/docs  (API documentation)
    http://localhost:8000/       (UI)

API Endpoints Available:
    POST   /command              - Process user commands
    POST   /screen/analyze       - Check screen with OCR
    POST   /system/open-app      - Launch application
    POST   /system/close-app     - Close application
    GET    /learning/profile     - View learning profile
    GET    /learning/favorites   - Get favorite commands
    GET    /errors/summary       - Debug information
    GET    /status               - System status
    WS     /ws                   - Real-time WebSocket
""")
