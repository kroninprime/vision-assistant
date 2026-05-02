# JARVIS Desktop AI Agent - Master Blueprint (2026)

## Vision

Transform the current voice assistant into a full desktop AI agent that can:

- Listen continuously with wake word activation
- Understand user intent with context (voice + screen + memory)
- Plan and execute multi-step tasks autonomously
- Control desktop apps and UI safely
- Respond with real-time visual and spoken feedback

This blueprint preserves the existing architecture:

- `FastAPI` backend
- `WebSocket` real-time communication
- Orb-style frontend UI (TypeScript + Three.js)
- SQLite memory

---

## Target Capabilities

### 1) Wake Word and Speech Loop

- Continuous microphone listening
- Wake phrase: `"hey jarvis"`
- Upon wake: capture user command -> transcribe -> route to planner
- Push UI state transitions over WebSocket:
  - `listening`
  - `thinking`
  - `acting`
  - `speaking`
  - `idle`

### 2) System Control

- Open/close desktop applications
- Execute safe OS commands
- Adjust system settings where supported:
  - Volume
  - Brightness

### 3) Automation Engine

- Parse intent into structured steps
- Execute steps sequentially with status tracking
- Example workflow:
  - Download file
  - Rename file
  - Move file to destination folder

### 4) Screen Awareness

- Capture screenshot on demand or when needed
- OCR text extraction with `pytesseract`
- Send extracted screen context into AI reasoning

### 5) User Interaction Automation

- Mouse movement and clicking (`pyautogui`)
- Keyboard typing and shortcuts
- Element targeting by coordinates or OCR anchors

### 6) Persistent Memory Intelligence

- Store preferences and routines in SQLite
- Track usage patterns over time
- Retrieve relevant memory snippets during planning

### 7) Plugin-Based Modules

Each domain is isolated and independently testable:

- Calendar
- Email
- Browser
- System
- Notes

### 8) Reliability

- Structured logging
- Error categories and fallback responses
- Recovery hooks for failed steps

---

## Suggested Project Structure

```text
jarvis/
  backend/
    app/
      main.py
      config.py
      websocket/
        manager.py
        events.py
      api/
        routes_voice.py
        routes_tasks.py
        routes_system.py
      core/
        state_machine.py
        logger.py
        errors.py
      ai/
        orchestrator.py
        planner.py
        responder.py
      speech/
        wake_word.py
        stt.py
        tts.py
      automation/
        engine.py
        actions.py
        safety.py
      vision/
        screen_capture.py
        ocr.py
      memory/
        models.py
        store.py
        retrieval.py
      plugins/
        base.py
        manager.py
        calendar_plugin.py
        email_plugin.py
        browser_plugin.py
        system_plugin.py
        notes_plugin.py
    requirements.txt
  frontend/
    src/
      ws/client.ts
      ui/orb.ts
      ui/state-panel.ts
      app.ts
  docs/
    architecture.md
    safety_policy.md
    plugin_guide.md
```

---

## Execution Pipeline

1. Wake word listener detects `"hey jarvis"`
2. STT transcribes user command
3. `orchestrator` builds context:
   - user text
   - recent memory
   - optional OCR screen text
4. `planner` generates actionable steps
5. `automation engine` executes steps
6. `responder` builds spoken + UI feedback
7. Results stored in memory and logs

---

## Safety and Permission Model

Critical for desktop control:

- Allowlist system commands
- Block dangerous shell operations by default
- Require confirmation for destructive actions (delete, kill process, file overwrite)
- Timeouts and retries for every automation step
- Emergency stop phrase: `"jarvis stop"`

---

## Recommended Python Dependencies

- `fastapi`
- `uvicorn`
- `websockets`
- `pydantic`
- `sqlalchemy`
- `pyautogui`
- `pytesseract`
- `Pillow`
- `SpeechRecognition`
- `pyaudio` (or platform-specific alternative)
- `python-dotenv`

Optional:

- `psutil` for process/system introspection
- `opencv-python` for advanced vision workflows

---

## Build Phases

### Phase 1 - Core Runtime

- FastAPI app + WebSocket events
- State machine
- Basic STT -> AI -> TTS loop

### Phase 2 - Desktop Control

- Safe command runner
- App launcher
- Basic automation actions (click/type/hotkey)

### Phase 3 - Planning Engine

- Task decomposition
- Sequential executor with progress events
- Retry/fallback behavior

### Phase 4 - Screen Intelligence

- Screenshot capture
- OCR extraction
- Context-enhanced prompt routing

### Phase 5 - Memory Intelligence

- Preference schema
- Pattern learning jobs
- Context retrieval ranking

### Phase 6 - Plugin Expansion

- Calendar/email/browser/notes modules
- Plugin registration + capability metadata

---

## Codex Build Prompt (Ready to Use)

```text
Upgrade this JARVIS voice assistant into a full desktop AI agent with these capabilities:
1) Wake word ("Hey Jarvis") with continuous listening
2) Full desktop/system control (open/close apps, settings, OS commands)
3) Automation engine for multi-step task execution
4) Screen awareness via screenshot + OCR
5) User interaction automation (mouse/keyboard/clicking)
6) Persistent memory intelligence (SQLite preferences + behavior patterns)
7) Plugin-based architecture (calendar, email, browser, system, notes)
8) Real-time UI feedback states (listening/thinking/acting/speaking)
9) Error handling + logging

Tech additions:
pyautogui, pytesseract, SpeechRecognition, subprocess/os

Preserve:
FastAPI + WebSocket backend and Three.js orb frontend.
Generate a clean folder structure and production-ready starter code.
```

---

## Practical Next Step

If you want implementation now, the fastest sequence is:

1. Scaffold backend modules and interfaces
2. Implement WebSocket state events
3. Add wake word + STT service loop
4. Add automation engine with safe action primitives
5. Plug in OCR and memory retrieval

Then iterate plugin-by-plugin.
