from ai_chat import chat_reply
from memory import MemoryStore
from plugins import PluginManager
from project_builder import create_game_hq, create_portfolio, create_python_project, create_website_hq
from qa_assistant import answer_doubt
from task_engine import TaskEngine

plugin_manager = PluginManager()
task_engine = TaskEngine(plugin_manager)

def plan_and_execute(text: str, screen_context: str = "", memory: MemoryStore | None = None) -> str:
    low = text.lower().strip()

    steps = task_engine.build_steps(text)
    if steps:
        logs, status = task_engine.execute_steps(steps)
        headline = "Task completed." if status == "completed" else "Task partially failed."
        return headline + "\n" + "\n".join(logs[:6])

    if low.startswith("open "):
        app = text[5:].strip()
        return plugin_manager.execute("system.open", app)

    if low.startswith("website "):
        url = text[8:].strip()
        return plugin_manager.execute("web.open", url)

    if low.startswith("search "):
        query = text[7:].strip()
        return plugin_manager.execute("web.search", query)

    if low.startswith("search and tell ") or low.startswith("search and summarize "):
        query = text.split(" ", 3)[3].strip()
        return plugin_manager.execute("web.search_summary", query)

    if low.startswith("close "):
        app = text[6:].strip()
        return plugin_manager.execute("system.close", app)

    if low.startswith("run "):
        cmd = text[4:].strip()
        return plugin_manager.execute("system.command", cmd)

    if low.startswith("volume "):
        value = text[7:].strip()
        return plugin_manager.execute("system.volume", value)

    if "what is on my screen" in low or "error on my screen" in low:
        if not screen_context:
            return "I could not read screen text. Try again with OCR enabled."
        preview = screen_context[:600]
        return f"I detected this on your screen:\n{preview}"

    if low.startswith("create portfolio on ") or low.startswith("create portfolio about "):
        topic = text.split(" on ", 1)[1].strip() if " on " in low else text.split(" about ", 1)[1].strip()
        folder = create_portfolio(topic)
        return f"Portfolio created for '{topic}'. Path: {folder}"

    if low.startswith("create project on ") or low.startswith("create project about "):
        topic = text.split(" on ", 1)[1].strip() if " on " in low else text.split(" about ", 1)[1].strip()
        folder = create_python_project(topic)
        return f"Project scaffold created for '{topic}'. Path: {folder}"

    if low.startswith("create website on ") or low.startswith("create website about ") or low.startswith("build website on ") or low.startswith("build website about "):
        topic = text.split(" on ", 1)[1].strip() if " on " in low else text.split(" about ", 1)[1].strip()
        folder = create_website_hq(topic)
        return f"High-quality website created for '{topic}'. Path: {folder}"

    if low.startswith("create game on ") or low.startswith("create game about ") or low.startswith("build game on ") or low.startswith("build game about "):
        topic = text.split(" on ", 1)[1].strip() if " on " in low else text.split(" about ", 1)[1].strip()
        folder = create_game_hq(topic)
        return f"Playable game created for '{topic}'. Path: {folder}"

    if low.startswith("doubt ") or low.startswith("explain "):
        question = text.split(" ", 1)[1].strip()
        ai_answer = chat_reply(question, recent_context=memory.recent_context(8) if memory else "", screen_context=screen_context)
        if ai_answer.startswith("AI chat request failed:") or "not configured yet" in ai_answer:
            return answer_doubt(question)
        return ai_answer

    if "remember " in low and memory:
        pref = text.split("remember ", 1)[1].strip()
        if "=" in pref:
            key, value = pref.split("=", 1)
            memory.set_preference(key.strip(), value.strip())
            return f"Saved preference: {key.strip()}."
        return "Use format: remember key = value"

    if "my preferences" in low and memory:
        prefs = memory.list_preferences()
        if not prefs:
            return "I do not have preferences stored yet."
        lines = [f"{k}: {v}" for k, v in prefs.items()]
        return "Known preferences:\n" + "\n".join(lines[:10])

    recent = memory.recent_context(10) if memory else ""
    ai_answer = chat_reply(text, recent_context=recent, screen_context=screen_context)
    if ai_answer.startswith("AI chat request failed:") or "not configured yet" in ai_answer:
        if recent:
            return (
                f"I heard: '{text}'. Recent context loaded. "
                "Try: search quantum computing, website github.com, create portfolio about AI, create project on finance app, explain black holes."
            )
        return (
            f"I heard: '{text}'. "
            "Try: search your topic, website example.com, create portfolio about your topic, create project on your topic, explain your doubt."
        )
    return ai_answer
