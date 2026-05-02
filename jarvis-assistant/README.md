# Jarvis Assistant (starter)

Minimal scaffolding for a locally running, always-on assistant you can extend with new skills.

## What you get
- FastAPI service with `/command` endpoint.
- Skill registry pattern in `app/main.py`.
- Example skill in `skills/example_skill.py`.
- Background task hook (`background_tick`) where proactive jobs can run (poll sensors, schedule tasks, etc.).
- Brain wrapper (`app/brain.py`) calls OpenAI if `OPENAI_API_KEY` is set.
- Web console UI with mic button at `http://127.0.0.1:8000/`.

## Run it
```powershell
cd jarvis-assistant
python -m venv .venv
.\\.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
copy .env.example to .env and set `OPENAI_API_KEY` if you want smarter answers
```

Test a command:
```powershell
curl -X POST http://127.0.0.1:8000/command -H "Content-Type: application/json" -d "{\"text\": \"what's the weather\"}"
```

## Adding skills
1. Create a new file under `skills/`, define a function `(prompt: str) -> str`.
2. Register it with `assistant.register("keyword", handler)`.
3. Restart the server.

## Voice wake (clap) loop
Keep the API running, then in another terminal:
```powershell
cd jarvis-assistant
.\.venv\Scripts\activate
python voice_loop.py
```
- Clap once: it says "Yes?" and listens.
- Say your command; it speaks the reply.
- Say "shut down" to stop the loop.

## Making it feel like Jarvis
- Proactive tasks: implement real work in `background_tick` (calendar alerts, file watchers with `watchdog`, system checks).
- System control: add skills that call PowerShell scripts (launch apps, adjust volume, move files) **carefully and with explicit allow-lists**.
- Secure secrets: load API keys via `.env` and `python-dotenv`.

## Autostart on Windows
- Create a scheduled task that runs `.venv\\Scripts\\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000` at logon.
- Or drop a shortcut into `shell:startup` that runs `powershell -NoExit -Command \"cd <path>; .\\.venv\\Scripts\\activate; uvicorn app.main:app\"`.

## Next ideas
- Route by intent (use OpenAI or a local model to pick skills).
- Add persistence (SQLite) for notes and reminders.
- Expose a small React/Next dashboard to monitor status and trigger commands.
