from __future__ import annotations

from datetime import datetime

from .actions import ComputerControl, InternetAutomation, LifeManager
from .activation import ClapDetector, PresenceGate, TriggerFusion, WakeWordDetector
from .autonomy import AutonomousTaskEngine, MultiAgentCoordinator
from .background import JobQueue
from .brain import DialogueManager, NLU, PlannerAgent, Predictor
from .file_data import FileDataManager
from .integrations import PhoneBridge, PluginLoader, SmartHomeBridge
from .memory import LongTermMemory, MemoryPolicies, ShortTermMemory, VectorStore
from .perception import CameraAwareness, ScreenAwareness
from .security import AuditLog, Permissions
from .ui import HUD, SoundFX
from .voice import ASRStream, BargeIn, ProsodyController, TTSEngine, VAD, VoiceConfig


class JarvisCore:
    def __init__(self) -> None:
        self.fusion = TriggerFusion()
        self.clap = ClapDetector()
        self.wake = WakeWordDetector()
        self.presence = PresenceGate()
        self.voice_config = VoiceConfig(enable_tts=False, microphone_enabled=True, keyboard_fallback=False)
        self.asr = ASRStream(self.voice_config)
        self.vad = VAD()
        self.barge = BargeIn()
        self.tts = TTSEngine(self.voice_config)
        self.prosody = ProsodyController()
        self.nlu = NLU()
        self.planner = PlannerAgent()
        self.autonomy = AutonomousTaskEngine()
        self.agents = MultiAgentCoordinator()
        self.dialog = DialogueManager()
        self.predictor = Predictor()
        self.control = ComputerControl()
        self.internet = InternetAutomation()
        self.life = LifeManager()
        self.files = FileDataManager()
        self.screen = ScreenAwareness()
        self.camera = CameraAwareness()
        self.short_mem = ShortTermMemory()
        self.long_mem = LongTermMemory()
        self.vector_store = VectorStore()
        self.memory_policy = MemoryPolicies()
        self.permissions = Permissions()
        self.audit = AuditLog()
        self.hud = HUD()
        self.sfx = SoundFX()
        self.jobs = JobQueue()
        self.phone = PhoneBridge()
        self.home = SmartHomeBridge()
        self.plugins = PluginLoader()
        self._awake = False
        self.continuous_listening = False
        self._register_default_plugins()

    def _register_default_plugins(self) -> None:
        self.plugins.register("screen_awareness", "Screen OCR and UI interpretation adapter point")
        self.plugins.register("face_auth", "Face recognition adapter point")
        self.plugins.register("automation_agent", "Human-like UI automation adapter point")
        self.plugins.register("mail_digest", "Email digest adapter point")

    def _greeting(self) -> str:
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        return (
            f"{greeting}, sci bro. All systems are online. "
            f"{self.control.system_status()} {self.life.summary()} {self.predictor.suggest()}"
        )

    def speak(self, text: str, mood: str = "calm") -> None:
        self.tts.speak(self.prosody.style(text, mood))

    def _execute(self, action: str, payload: dict[str, str]) -> str:
        if action == "safety_check":
            intent_name = payload.get("intent", "")
            if not self.permissions.allowed(intent_name):
                return "Action blocked by safety policy."
            return "Safety check passed."
        if action == "open_app":
            return self.control.open_app(payload.get("raw", ""))
        if action == "web_search":
            return self.internet.web_search(payload.get("query", ""))
        if action == "youtube_search":
            return self.internet.youtube_search(payload.get("query", ""))
        if action == "news_search":
            return self.internet.latest_news()
        if action == "create_reminder":
            return self.life.create_reminder(payload.get("raw", ""))
        if action == "status_report":
            return f"{self.control.system_status()} {self.life.summary()}"
        if action == "time_now":
            return f"Current time is {datetime.now().strftime('%I:%M %p')}."
        if action == "screen_read":
            return self.screen.read_screen()
        if action == "screen_error_check":
            return self.screen.detect_errors()
        if action == "face_recognition":
            return self.camera.face_recognition()
        if action == "object_detection":
            return self.camera.object_detection()
        if action == "calendar_summary":
            return self.life.calendar_summary()
        if action == "email_summary":
            return self.life.email_summary()
        if action == "list_plugins":
            plugins = self.plugins.list_plugins()
            return "Plugins: " + ("; ".join(plugins) if plugins else "none")
        if action == "phone_status":
            return self.phone.status()
        if action == "smart_home_status":
            return self.home.status()
        if action == "file_search":
            return self.files.search_files(".", payload.get("query", ""))
        if action == "ui_automation":
            return self.control.ui_action(payload.get("raw", ""))
        if action == "sleep_mode":
            self._awake = False
            return "Entering sleep mode. Say wake up Jarvis when needed."
        if action == "chat":
            return self.dialog.respond_chat(payload.get("message", ""))
        return f"Unknown action: {action}"

    def _process_utterance(self, text: str) -> str:
        if not self.vad.is_speech(text):
            return ""
        if self.barge.interrupted(text):
            self.hud.set_state("idle")
            msg = "Understood. Stopping current flow."
            self.speak(msg)
            return msg

        intent = self.nlu.parse(text)
        plan = self.planner.make_plan(text, intent)
        self.autonomy.run_plan(plan)
        self.agents.assign(text)
        self.audit.record(f"intent={intent.name} request={text}")
        self.long_mem.track_habit(intent.name)
        if self.memory_policy.retain(text):
            self.short_mem.add(text)
            self.vector_store.add(text)

        self.hud.set_state("acting")
        responses = [self._execute(step.action, step.payload) for step in plan.steps]
        final_text = " ".join(r for r in responses if r).strip()
        if not final_text:
            final_text = self.dialog.respond_chat(text)
        self.speak(final_text)
        self.hud.set_state("listening" if self._awake else "idle")
        return final_text

    def handle_text(self, heard: str) -> str:
        heard = heard.strip()
        if not heard:
            return ""
        if heard.lower() == "exit":
            return "Shutting down."

        clap_score = self.clap.detect_from_text(heard)
        if clap_score > 0:
            self.fusion.arm_from_clap(clap_score)
            if not self._awake:
                return "Clap detected. Awaiting wake phrase."
            return "Clap detected."

        wake_score = self.wake.score(heard)
        if not self._awake and wake_score > 0:
            event = self.fusion.activate_from_wake_phrase(wake_score)
            if event and self.presence.is_present():
                self._awake = True
                self.hud.set_state("listening")
                self.sfx.play("wake")
                greeting = self._greeting()
                self.speak(greeting, mood="formal")
                return greeting

        if not self._awake:
            return "Jarvis is sleeping. Say wake up Jarvis."

        result = self._process_utterance(heard)
        print(self.jobs.run_next())
        return result

    def trigger_wake(self, source: str) -> str:
        src = source.lower().strip()
        if src == "clap":
            self.fusion.arm_from_clap(0.95)
            return "Clap trigger armed. Say wake up Jarvis."
        if src in {"voice", "wake", "wake_phrase"}:
            event = self.fusion.activate_from_wake_phrase(0.95)
            if event and self.presence.is_present():
                self._awake = True
                self.hud.set_state("listening")
                self.sfx.play("wake")
                greeting = self._greeting()
                self.speak(greeting, mood="formal")
                return greeting
            return "Wake phrase detected but presence check failed."
        if src == "face":
            self._awake = True
            return "Face presence trigger accepted. Jarvis is awake."
        if src == "hotkey":
            self._awake = True
            return "Manual hotkey trigger accepted. Jarvis is awake."
        return "Unknown trigger source."

    def toggle_continuous_listen(self, enabled: bool) -> str:
        self.continuous_listening = enabled
        return f"Continuous listening {'enabled' if enabled else 'disabled'}."

    def feature_matrix(self) -> dict[str, dict[str, str]]:
        return {
            "activation_system": {
                "clap_detection": "integrated via clap trigger + fusion",
                "voice_wake": "integrated via wake phrase scoring",
                "face_auto_wake": "available as trigger endpoint",
                "manual_hotkey": "available as trigger endpoint",
            },
            "core_ai_brain": {"status": "integrated: nlu + planner + dialogue + predictor"},
            "voice_system": {
                "wake_word": "enabled",
                "continuous_listening": "enabled" if self.continuous_listening else "disabled",
                "interruptible": "enabled (stop/cancel)",
                "tts": "enabled in runtime output",
            },
            "computer_control": {"status": "open apps, status, web, ui automation"},
            "automation": {"status": "mouse/keyboard actions available"},
            "awareness": {"screen": "read + error check", "camera": "face + object adapters"},
            "autonomy": {"status": "plan + execute + retry-ready scaffold"},
            "multi_agent": {"status": "planner/coding/research/executor assignment active"},
            "internet": {"status": "web search + youtube + news + browsing"},
            "file_data": {"status": "file search + folder ops"},
            "life": {"status": "calendar + reminders + email summary"},
            "memory": {"status": "short-term + long-term + habits + semantic store"},
            "self_improve": {"status": "audit hooks + extension points integrated"},
            "predictive_intelligence": {"status": self.predictor.suggest()},
            "personality": {"status": "calm/intelligent/formal response style"},
            "voice_experience": {"status": "startup/wake cues + spoken responses"},
            "visual_ui_hud": {"status": "idle/listening/acting states"},
            "background_tasks": {"status": "job queue integrated"},
            "security": {"status": "permissions + voice/face auth adapters + audit"},
            "multi_device": {"status": "phone + smart-home bridges"},
            "modular_architecture": {"status": "plugin registry active"},
            "runtime": {"awake": str(self._awake), "mic": self.asr.microphone_status()},
        }

    def capture_from_system_mic(self) -> str:
        if not self.asr.microphone_ready():
            return ""
        return self.asr.listen_once().strip()

    def run(self) -> None:
        self.hud.set_state("idle")
        self.sfx.play("startup")
        self.speak("Jarvis runtime initialized. Listening for wake phrase.")
        print(f"[MIC] {self.asr.microphone_status()}")
        while True:
            heard = self.asr.listen_once()
            if heard.lower().strip() == "exit":
                self.speak("Shutting down.")
                break
            self.handle_text(heard)

