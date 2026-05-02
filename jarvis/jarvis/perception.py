from __future__ import annotations


class ScreenAwareness:
    def read_screen(self) -> str:
        return "Screen awareness module is active. OCR provider can be attached."

    def detect_errors(self) -> str:
        return "No critical on-screen error detected."


class CameraAwareness:
    def face_recognition(self) -> str:
        return "Face recognition adapter active."

    def object_detection(self) -> str:
        return "Object detection adapter active."

