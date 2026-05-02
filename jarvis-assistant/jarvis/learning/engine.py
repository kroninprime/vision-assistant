"""Learning system - JARVIS learns user preferences over time."""
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger("jarvis.learning")


class LearningEngine:
    """
    Learns user patterns and preferences.
    
    Tracks:
    - Frequently used commands
    - User preferences
    - Time-based patterns
    - Error recovery
    """

    def __init__(self, memory_db_path: Path):
        self.db_path = memory_db_path
        self.user_profile: Dict[str, Any] = {
            "favorite_commands": {},
            "preferences": {},
            "time_patterns": {},
            "error_recovery": {},
            "learned_at": datetime.now().isoformat(),
        }
        self._load_profile()

    def _load_profile(self):
        """Load existing user profile from disk."""
        profile_file = self.db_path.parent / "user_profile.json"
        if profile_file.exists():
            try:
                with open(profile_file) as f:
                    self.user_profile = json.load(f)
                logger.info("User profile loaded")
            except Exception as e:
                logger.warning(f"Failed to load profile: {e}")

    def _save_profile(self):
        """Save user profile to disk."""
        profile_file = self.db_path.parent / "user_profile.json"
        try:
            with open(profile_file, "w") as f:
                json.dump(self.user_profile, f, indent=2)
            logger.debug("User profile saved")
        except Exception as e:
            logger.error(f"Failed to save profile: {e}")

    def learn_command(self, command: str, success: bool = True):
        """Record command for learning patterns."""
        if command not in self.user_profile["favorite_commands"]:
            self.user_profile["favorite_commands"][command] = {
                "count": 0,
                "success_count": 0,
                "last_used": None,
            }

        entry = self.user_profile["favorite_commands"][command]
        entry["count"] += 1
        if success:
            entry["success_count"] += 1
        entry["last_used"] = datetime.now().isoformat()

        logger.debug(f"Learned command: {command} (count: {entry['count']})")
        self._save_profile()

    def learn_preference(self, key: str, value: Any):
        """Store user preference."""
        self.user_profile["preferences"][key] = {
            "value": value,
            "learned_at": datetime.now().isoformat(),
        }
        logger.info(f"Learned preference: {key} = {value}")
        self._save_profile()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Retrieve learned preference."""
        if key in self.user_profile["preferences"]:
            return self.user_profile["preferences"][key]["value"]
        return default

    def get_favorite_commands(self, limit: int = 5) -> List[tuple]:
        """Get most frequently used commands."""
        commands = self.user_profile["favorite_commands"]
        sorted_commands = sorted(
            commands.items(),
            key=lambda x: x[1]["count"],
            reverse=True,
        )
        return sorted_commands[:limit]

    def record_error_recovery(self, error_type: str, recovery_action: str):
        """Learn from errors and recovery actions."""
        if error_type not in self.user_profile["error_recovery"]:
            self.user_profile["error_recovery"][error_type] = []

        self.user_profile["error_recovery"][error_type].append({
            "recovery": recovery_action,
            "timestamp": datetime.now().isoformat(),
        })
        logger.info(f"Recorded error recovery: {error_type} -> {recovery_action}")
        self._save_profile()

    def suggest_recovery(self, error_type: str) -> Optional[str]:
        """Suggest recovery action based on past learning."""
        if error_type in self.user_profile["error_recovery"]:
            recoveries = self.user_profile["error_recovery"][error_type]
            if recoveries:
                return recoveries[-1]["recovery"]  # Most recent
        return None

    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze learned patterns."""
        commands = self.user_profile["favorite_commands"]
        total_commands = sum(c["count"] for c in commands.values())
        success_rate = (
            sum(c["success_count"] for c in commands.values()) / total_commands
            if total_commands > 0
            else 0
        )

        return {
            "total_commands_learned": total_commands,
            "success_rate": success_rate,
            "favorite_commands": self.get_favorite_commands(3),
            "error_recovery_strategies": len(self.user_profile["error_recovery"]),
            "preferences_learned": len(self.user_profile["preferences"]),
        }

    def get_user_profile_summary(self) -> str:
        """Get human-readable user profile summary."""
        patterns = self.analyze_patterns()
        fav_commands = patterns["favorite_commands"]

        summary = f"""
JARVIS User Profile
====================
Commands learned: {patterns['total_commands_learned']}
Success rate: {patterns['success_rate']:.1%}

Favorite commands:
"""
        for cmd, data in fav_commands:
            summary += f"  • {cmd} (used {data['count']} times)\n"

        summary += f"\nUser preferences: {patterns['preferences_learned']}\n"
        summary += f"Error recovery strategies: {patterns['error_recovery_strategies']}\n"

        return summary
