from __future__ import annotations


class HUD:
    def set_state(self, state: str) -> None:
        print(f"[HUD] {state}")


class SoundFX:
    def play(self, cue: str) -> None:
        print(f"[SFX] {cue}")

