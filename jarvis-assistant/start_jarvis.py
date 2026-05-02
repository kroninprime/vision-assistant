#!/usr/bin/env python3
"""
🚀 JARVIS 2.0 ENHANCED - QUICK START GUIDE

This script sets up and runs your upgraded JARVIS system.
"""

import os
import sys
import subprocess
from pathlib import Path

print("""
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║                   🤖 JARVIS 2.0 ENHANCED - QUICK START                ║
║                                                                        ║
║              Transform Your Voice Assistant Into An AI Agent           ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝

What's New in JARVIS 2.0:
═════════════════════════════════════════════════════════════════════════

✅ WAKE WORD DETECTION
   - Listen for "Hey Jarvis" 24/7
   - Automatic activation
   - Background thread (no blocking)

✅ SCREEN AWARENESS + OCR
   - Real-time screen capture
   - Extract text from screen
   - Analyze what's currently displayed

✅ MULTI-STEP AUTOMATION
   - Plan complex tasks automatically
   - Execute steps sequentially
   - Track progress in real-time

✅ SYSTEM CONTROL
   - Open/close applications
   - Control volume & brightness
   - Execute system commands

✅ USER LEARNING ENGINE
   - Learns your preferences over time
   - Tracks favorite commands
   - Suggests error recovery

✅ COMPREHENSIVE LOGGING
   - Rotating file logs
   - Error tracking
   - Real-time monitoring

✅ WEBSOCKET API
   - Real-time bidirectional communication
   - Live status updates
   - Instant responses

═════════════════════════════════════════════════════════════════════════
""")

def check_python_version():
    """Verify Python 3.10+"""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required")
        print(f"   Current: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")

def check_dependencies():
    """Check if all required packages are installed."""
    print("\n🔍 Checking dependencies...")
    required = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "speech_recognition",
        "openai",
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    return True

def start_server():
    """Start the JARVIS enhanced FastAPI server."""
    print("\n" + "="*70)
    print("🚀 Starting JARVIS 2.0 Enhanced Server...")
    print("="*70)
    
    try:
        # Start uvicorn server
        subprocess.run([
            sys.executable,
            "-m",
            "uvicorn",
            "app.main_enhanced:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000",
        ])
    except KeyboardInterrupt:
        print("\n\n🛑 JARVIS shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

def show_usage():
    """Display usage instructions."""
    print("""

═════════════════════════════════════════════════════════════════════════
🔗 ACCESS YOUR JARVIS
═════════════════════════════════════════════════════════════════════════

Web Interface:
   http://localhost:8000

API Documentation (Swagger):
   http://localhost:8000/docs

Alternative API Docs (ReDoc):
   http://localhost:8000/redoc

═════════════════════════════════════════════════════════════════════════
📋 EXAMPLE COMMANDS
═════════════════════════════════════════════════════════════════════════

Verbal Commands:
   "Open Chrome"
   "Take a screenshot"
   "What's on my screen?"
   "What's the weather?"
   "Set volume to 50%"

API Commands (curl):
   curl -X POST http://localhost:8000/command \\
     -H "Content-Type: application/json" \\
     -d '{"text":"open notepad","history":[]}'

WebSocket (JavaScript):
   const ws = new WebSocket("ws://localhost:8000/ws");
   ws.send(JSON.stringify({
     type: "command",
     data: { text: "Take a screenshot", history: [] }
   }));

═════════════════════════════════════════════════════════════════════════
📚 DOCUMENTATION FILES
═════════════════════════════════════════════════════════════════════════

📖 UPGRADE_DOCUMENTATION.md
   - Complete guide to new features
   - API endpoints reference
   - Configuration options

📖 ARCHITECTURE.md
   - System architecture diagram
   - Module interaction map
   - Data flow examples

📖 examples_enhanced.py
   - Code examples for each module
   - Usage patterns
   - Integration samples

═════════════════════════════════════════════════════════════════════════
🔧 NEXT STEPS
═════════════════════════════════════════════════════════════════════════

1. ✅ Start the server (this script)

2. 📖 Open UPGRADE_DOCUMENTATION.md for:
   - Full feature list
   - API endpoint details
   - Configuration guide

3. 🧪 Test the API:
   - Visit http://localhost:8000/docs
   - Try /command endpoint
   - Try /screen/analyze

4. 🎤 Enable wake word:
   - Server starts with wake word listener active
   - Say "Hey Jarvis" to activate
   - Check logs for confirmation

5. 📊 Monitor learning:
   - Visit GET /learning/profile
   - See favorite commands
   - View user preferences

6. 🐛 Debug if needed:
   - Check logs/ directory
   - Visit GET /errors/summary
   - Review ARCHITECTURE.md for troubleshooting

═════════════════════════════════════════════════════════════════════════
💡 TIPS
═════════════════════════════════════════════════════════════════════════

• System learns your preferences over time
• All interactions logged for debugging
• Graceful error handling with suggestions
• WebSocket for real-time communication
• Rotating logs prevent disk overflow
• Voice + text input both supported

═════════════════════════════════════════════════════════════════════════
🔐 SECURITY NOTE
═════════════════════════════════════════════════════════════════════════

Make sure to:
✓ Set OPENAI_API_KEY in .env file
✓ Keep your API keys secret
✓ Don't expose the server to untrusted networks
✓ Review executed commands in logs

═════════════════════════════════════════════════════════════════════════
""")

def main():
    """Main startup function."""
    check_python_version()
    
    if not check_dependencies():
        print("\n💾 Install dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    show_usage()
    
    print("\n🚀 Ready to start JARVIS? Press ENTER or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
    
    start_server()

if __name__ == "__main__":
    main()
