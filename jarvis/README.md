# JARVIS (Voice-First Master Scaffold)

This repository contains an integrated, voice-first JARVIS foundation with all major feature domains wired together:

- Activation (clap + wake phrase fusion adapter)
- Voice pipeline (ASR/VAD/barge-in/TTS)
- AI brain (NLU + planner + dialogue + predictive suggestion)
- Action layer (computer control + internet automation + life reminders)
- Memory (short-term + long-term + semantic store)
- Security (permissions + auth adapters + audit log)
- UI/HUD states and sound cues
- Background jobs
- Integrations (phone, smart home, plugins)

## Run

1. Create environment and install dependencies:

```powershell
pip install -r requirements.txt
```

2. Download Vosk English model (no PyAudio needed):

- Download: [https://alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)
- Recommended model: `vosk-model-small-en-us-0.15`
- Extract it to: `models/vosk-model-small-en-us-0.15`

Or auto-install with:

```powershell
powershell -ExecutionPolicy Bypass -File .\install_vosk_model.ps1
```

3. Start Jarvis:

```powershell
python -m jarvis.main
```

You can also start it without Cursor by double-clicking:

- `start_jarvis.bat`

4. Wake and interact (voice-first):

- Say/type: `wake up jarvis`
- Then commands like:
  - `open notepad`
  - `search black holes`
  - `remind me to revise physics`
  - `status report`
  - `read screen`
  - `detect errors on screen`
  - `face recognition`
  - `object detection`
  - `calendar summary`
  - `email summary`
  - `phone status`
  - `smart home status`
  - `list plugins`
  - `find file notes`
  - `move mouse` / `click` / `type hello`
  - `sleep mode`
- Exit with: `exit`

## Run Without Cursor (Auto-Start on Windows)

Install startup task (run once in PowerShell as your user):

```powershell
powershell -ExecutionPolicy Bypass -File .\install_startup_task.ps1
```

This makes JARVIS start automatically whenever you log into Windows, even if Cursor is not open.

If Task Scheduler needs admin rights on your machine, use the no-admin startup-folder method:

```powershell
powershell -ExecutionPolicy Bypass -File .\install_startup_folder.ps1
```

To remove auto-start later:

```powershell
powershell -ExecutionPolicy Bypass -File .\uninstall_startup_task.ps1
```

Or for startup-folder method:

```powershell
powershell -ExecutionPolicy Bypass -File .\uninstall_startup_folder.ps1
```

Manual control:

- Start now: `start_jarvis.bat`
- Stop now: `stop_jarvis.bat`

## Notes

- The project is fully integrated as a single pipeline.
- Some modules are adapter-ready for advanced provider integrations (high-accuracy clap DSP, production face/object vision, and deep browser autonomy).
- This is intentional so you can incrementally plug in stronger providers without changing architecture.

