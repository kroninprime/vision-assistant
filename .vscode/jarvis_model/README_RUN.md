# Run Your JARVIS MVP (Windows)

## 1) Open terminal in this folder

`c:\Users\PERI\Desktop\python workspace\.vscode\jarvis_model`

## 2) Create virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

## 3) Install dependencies

```powershell
pip install -r requirements.txt
```

## 3.1) Enable real AI chat brain

Create `.env` from `.env.example` and set:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Without this key, Jarvis falls back to non-LLM responses.

## 3.2) Free mode (no API key)

Use local Ollama model (fully free on your PC):

```powershell
ollama pull llama3.1:8b
ollama serve
```

Then in `.env` keep:

```env
OPENAI_API_KEY=
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.1:8b
```

Now Jarvis chat uses local model automatically.

## 4) Optional OCR setup

Install Tesseract OCR:

- Download: https://github.com/UB-Mannheim/tesseract/wiki
- If needed, set `TESSERACT_CMD` in `.env` (copy from `.env.example`)

## 5) Start server

```powershell
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

## 5.1) Global wake mode (Cursor not required)

If you want Jarvis to wake from anywhere on your PC:

```powershell
powershell -ExecutionPolicy Bypass -File .\RUN_JARVIS_DAEMON.ps1
```

Then:

- Keep that terminal running in background
- Double-tap `Ctrl` anywhere on Windows
- Jarvis UI opens and says it is online

## 6) Test from browser

- Open visual UI: `http://127.0.0.1:8000/`
- API docs: `http://127.0.0.1:8000/docs`
- Use `POST /command`

Example body:

```json
{
  "text": "open notepad",
  "include_screen_context": false
}
```

Try these commands:

- `open chrome`
- `close chrome`
- `volume 35`
- `open notepad`
- `run whoami`
- `what is on my screen` (set `include_screen_context: true`)
- `open chrome and search black holes`
- `search machine learning roadmap`
- `website github.com`
- `open youtube`
- `open spotify`
- `open resume.pdf`
- `organize downloads`
- `create portfolio about data science`
- `create project on expense tracker`
- `create website about fitness coaching`
- `build game on space adventure`
- `explain what is docker`
- `search and tell latest ai news`
- `remember favorite_music = interstellar`
- `my preferences`

## 7) Enable wake word mode (optional)

1. Install microphone dependencies (PyAudio can be tricky on Windows)
2. Create `.env` from `.env.example`
3. Set:

```env
JARVIS_ENABLE_WAKE_WORD=true
JARVIS_WAKE_WORD=hey jarvis
```

Then restart server and say:

- "Hey Jarvis"
- followed by command (example: "open calculator")

---

## Important Reality Check

This is a real working local JARVIS MVP, but movie-level JARVIS requires:

- stronger planning model (GPT/Claude tool-calling)
- robust safety and permission checks
- native OS APIs for deep control
- advanced visual grounding

Use this project as the executable base and keep iterating.
