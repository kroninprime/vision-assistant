from __future__ import annotations

from datetime import datetime

from .models import Intent, PlanStep, TaskPlan


class NLU:
    def parse(self, text: str) -> Intent:
        lowered = text.lower()
        if "time now" in lowered or lowered.strip() == "time" or "what time" in lowered:
            return Intent(name="time_now", confidence=0.9)
        if "youtube" in lowered and ("search" in lowered or "play" in lowered):
            query = (
                text.lower()
                .replace("search youtube", "")
                .replace("play on youtube", "")
                .replace("youtube", "")
                .strip()
            )
            return Intent(name="youtube_search", entities={"query": query}, confidence=0.85)
        if "latest news" in lowered or "news update" in lowered:
            return Intent(name="news_search", confidence=0.85)
        web_prefixes = (
            "what is",
            "who is",
            "tell me about",
            "explain",
            "search",
            "google",
            "look up",
            "find on web",
        )
        if lowered.startswith(web_prefixes):
            query = text
            for prefix in web_prefixes:
                if lowered.startswith(prefix):
                    query = text[len(prefix) :].strip() or text
                    break
            return Intent(name="web_search", entities={"query": query}, confidence=0.85)
        if "screen" in lowered and "read" in lowered:
            return Intent(name="screen_read", confidence=0.8)
        if "detect error" in lowered or "errors on screen" in lowered:
            return Intent(name="screen_error_check", confidence=0.8)
        if "face" in lowered and "recognition" in lowered:
            return Intent(name="face_recognition", confidence=0.8)
        if "object detection" in lowered:
            return Intent(name="object_detection", confidence=0.8)
        if "calendar" in lowered:
            return Intent(name="calendar_summary", confidence=0.75)
        if "email" in lowered and "summary" in lowered:
            return Intent(name="email_summary", confidence=0.75)
        if "plugins" in lowered:
            return Intent(name="list_plugins", confidence=0.85)
        if "phone status" in lowered:
            return Intent(name="phone_status", confidence=0.8)
        if "smart home status" in lowered:
            return Intent(name="smart_home_status", confidence=0.8)
        if "find file" in lowered or "search file" in lowered:
            return Intent(name="file_search", entities={"query": text}, confidence=0.75)
        if "move mouse" in lowered or "click" in lowered or lowered.startswith("type "):
            return Intent(name="ui_automation", entities={"raw": text}, confidence=0.75)
        if "open" in lowered:
            return Intent(name="open_app", entities={"raw": text}, confidence=0.8)
        if "remind" in lowered:
            return Intent(name="create_reminder", entities={"raw": text}, confidence=0.75)
        if "search" in lowered:
            return Intent(name="web_search", entities={"query": text.replace("search", "").strip()}, confidence=0.8)
        if "status" in lowered:
            return Intent(name="status_report", confidence=0.9)
        if "sleep" in lowered:
            return Intent(name="sleep_mode", confidence=0.9)
        return Intent(name="chat", entities={"message": text}, confidence=0.6)


class PlannerAgent:
    def make_plan(self, text: str, intent: Intent) -> TaskPlan:
        steps = [PlanStep(action="safety_check", payload={"intent": intent.name})]
        if intent.name == "open_app":
            steps.append(PlanStep(action="open_app", payload=intent.entities))
        elif intent.name == "create_reminder":
            steps.append(PlanStep(action="create_reminder", payload=intent.entities))
        elif intent.name == "web_search":
            steps.append(PlanStep(action="web_search", payload=intent.entities))
        elif intent.name == "status_report":
            steps.append(PlanStep(action="status_report"))
        elif intent.name == "time_now":
            steps.append(PlanStep(action="time_now"))
        elif intent.name == "youtube_search":
            steps.append(PlanStep(action="youtube_search", payload=intent.entities))
        elif intent.name == "news_search":
            steps.append(PlanStep(action="news_search"))
        elif intent.name == "sleep_mode":
            steps.append(PlanStep(action="sleep_mode"))
        elif intent.name == "screen_read":
            steps.append(PlanStep(action="screen_read"))
        elif intent.name == "screen_error_check":
            steps.append(PlanStep(action="screen_error_check"))
        elif intent.name == "face_recognition":
            steps.append(PlanStep(action="face_recognition"))
        elif intent.name == "object_detection":
            steps.append(PlanStep(action="object_detection"))
        elif intent.name == "calendar_summary":
            steps.append(PlanStep(action="calendar_summary"))
        elif intent.name == "email_summary":
            steps.append(PlanStep(action="email_summary"))
        elif intent.name == "list_plugins":
            steps.append(PlanStep(action="list_plugins"))
        elif intent.name == "phone_status":
            steps.append(PlanStep(action="phone_status"))
        elif intent.name == "smart_home_status":
            steps.append(PlanStep(action="smart_home_status"))
        elif intent.name == "file_search":
            steps.append(PlanStep(action="file_search", payload=intent.entities))
        elif intent.name == "ui_automation":
            steps.append(PlanStep(action="ui_automation", payload=intent.entities))
        else:
            steps.append(PlanStep(action="chat", payload=intent.entities))
        return TaskPlan(original_request=text, steps=steps)


class Predictor:
    def suggest(self) -> str:
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return "You usually plan your day now. Want me to read your top tasks?"
        if 12 <= hour < 18:
            return "Would you like me to summarize pending work and emails?"
        return "Shall I prepare tomorrow's reminders before you wrap up?"


class DialogueManager:
    def respond_chat(self, text: str) -> str:
        return f"I understood: '{text}'. I can execute actions, check status, or manage tasks."

