import os
import pickle
from math import sqrt
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import requests
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from geopy.geocoders import Nominatim

ULTRALYTICS_DIR = os.path.join(os.path.dirname(__file__), ".ultralytics")
os.makedirs(ULTRALYTICS_DIR, exist_ok=True)
os.environ["YOLO_CONFIG_DIR"] = ULTRALYTICS_DIR

from ultralytics import YOLO


app = FastAPI(title="Vision Assistant API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "yolov8n.pt"
DB_PATH = "known_faces.pkl"
FACE_SIZE = (120, 120)
FACE_MATCH_THRESHOLD = 0.70
MAX_TEMPLATES_PER_NAME = 5
ANIMAL_LABELS = {"dog", "cat", "cow", "horse", "sheep", "bird"}
MIN_CONFIDENCE_BY_LABEL = {
    "person": 0.4,
    "dog": 0.72,
    "cat": 0.72,
    "horse": 0.72,
    "cow": 0.72,
    "sheep": 0.72,
    "bird": 0.72,
}
KNOWN_WIDTHS_M = {
    "person": 0.45,
    "car": 1.8,
    "bus": 2.5,
    "truck": 2.5,
    "bicycle": 0.6,
    "motorcycle": 0.8,
    "dog": 0.35,
    "cat": 0.25,
    "cow": 0.9,
    "horse": 0.8,
    "chair": 0.5,
    "bottle": 0.08,
    "cup": 0.09,
    "cell phone": 0.07,
}
DEFAULT_WIDTH_M = 0.5
FOCAL_LENGTH_PX = 700.0

model = YOLO(MODEL_PATH)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def normalize_face(gray_frame: np.ndarray, face_box: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
    x, y, w, h = face_box
    if w <= 0 or h <= 0:
        return None
    face_region = gray_frame[y : y + h, x : x + w]
    if face_region.size == 0:
        return None
    resized = cv2.resize(face_region, FACE_SIZE)
    equalized = cv2.equalizeHist(resized)
    return equalized.astype(np.float32) / 255.0


def load_known_faces() -> tuple[list, list]:
    if not os.path.exists(DB_PATH):
        return [], []

    with open(DB_PATH, "rb") as db_file:
        encodings, names = pickle.load(db_file)

    cleaned_faces = []
    cleaned_names = []
    for encoding, name in zip(encodings, names):
        if isinstance(encoding, np.ndarray) and encoding.shape == FACE_SIZE:
            cleaned_faces.append(encoding.astype(np.float32))
            cleaned_names.append(name)
    return cleaned_faces, cleaned_names


known_encs, known_names = load_known_faces()


class LocationPayload(BaseModel):
    latitude: float
    longitude: float
    accuracy_m: Optional[float] = None
    label: Optional[str] = None


class ChatPayload(BaseModel):
    message: str


def save_known_faces() -> None:
    with open(DB_PATH, "wb") as db_file:
        pickle.dump((known_encs, known_names), db_file)


def estimate_distance_m(label: str, box_width_px: float) -> Optional[float]:
    if box_width_px <= 0:
        return None
    real_width = KNOWN_WIDTHS_M.get(label, DEFAULT_WIDTH_M)
    return round((real_width * FOCAL_LENGTH_PX) / box_width_px, 2)


def should_keep_detection(label: str, confidence: float) -> bool:
    threshold = MIN_CONFIDENCE_BY_LABEL.get(label, 0.48)
    return confidence >= threshold


def calculate_iou(box_a: List[int], box_b: List[int]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_width = max(0, inter_x2 - inter_x1)
    inter_height = max(0, inter_y2 - inter_y1)
    inter_area = inter_width * inter_height
    if inter_area == 0:
        return 0.0

    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)
    union_area = area_a + area_b - inter_area
    if union_area <= 0:
        return 0.0
    return inter_area / union_area


def describe_horizontal_position(center_x: float, frame_width: int) -> str:
    ratio = center_x / max(frame_width, 1)
    if ratio < 0.33:
        return "left"
    if ratio > 0.66:
        return "right"
    return "center"


def describe_vertical_position(center_y: float, frame_height: int) -> str:
    ratio = center_y / max(frame_height, 1)
    if ratio < 0.33:
        return "top"
    if ratio > 0.66:
        return "bottom"
    return "middle"


def build_detection_summary(detections: List[Dict]) -> str:
    if not detections:
        return "No objects detected."

    priority_detection = next(
        (
            d
            for d in detections
            if d["label"] in {"recognized face", "unknown face", "person"}
        ),
        None,
    )
    if priority_detection:
        target_name = priority_detection["label"]
        return (
            f"{len(detections)} objects detected. "
            f"Primary subject is {target_name} at about {priority_detection['distance_m']} meters "
            f"on the {priority_detection['position']['horizontal']}."
        )

    nearest = min(
        [d for d in detections if d.get("distance_m") is not None],
        key=lambda d: d["distance_m"],
        default=None,
    )
    if not nearest:
        return f"{len(detections)} objects detected."

    return (
        f"{len(detections)} objects detected. "
        f"Nearest is {nearest['label']} at about {nearest['distance_m']} meters "
        f"on the {nearest['position']['horizontal']}."
    )


def detect_face_locations(gray_frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
    faces = face_cascade.detectMultiScale(
        gray_frame,
        scaleFactor=1.05,
        minNeighbors=4,
        minSize=(40, 40),
    )
    return [tuple(map(int, face)) for face in faces]


def match_face_name(gray_frame: np.ndarray, face_box: Tuple[int, int, int, int]) -> Optional[str]:
    if not known_encs:
        return None

    candidate = normalize_face(gray_frame, face_box)
    if candidate is None:
        return None

    best_name = None
    best_score = -1.0
    for saved_face, saved_name in zip(known_encs, known_names):
        result = cv2.matchTemplate(candidate, saved_face, cv2.TM_CCOEFF_NORMED)
        score = float(result[0][0])
        if score > best_score:
            best_score = score
            best_name = saved_name

    if best_score >= FACE_MATCH_THRESHOLD:
        return best_name
    return None


@app.get("/health")
def health() -> Dict:
    return {
        "ok": True,
        "known_faces": len(known_names),
        "model": MODEL_PATH,
        "face_recognition_available": True,
        "face_engine": "opencv",
    }


@app.get("/faces")
def list_faces() -> Dict:
    unique = list(dict.fromkeys(known_names))
    return {"count": len(unique), "names": unique}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)) -> Dict:
    content = await file.read()
    nparr = np.frombuffer(content, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image payload.")

    frame_height, frame_width = frame.shape[:2]
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    results = model.predict(frame, verbose=False, imgsz=640)
    detections: List[Dict] = []
    recognized_name = None
    face_seen = False
    person_detected = False

    for box in results[0].boxes:
        conf = float(box.conf[0])
        label = model.names[int(box.cls[0])]
        if not should_keep_detection(label, conf):
            continue

        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int).tolist()
        width_px = max(float(x2 - x1), 1.0)
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        distance_m = estimate_distance_m(label, width_px)

        detections.append(
            {
                "label": label,
                "conf": round(conf, 3),
                "box": [x1, y1, x2, y2],
                "distance_m": distance_m,
                "position": {
                    "horizontal": describe_horizontal_position(center_x, frame_width),
                    "vertical": describe_vertical_position(center_y, frame_height),
                },
                "center": {"x": round(center_x, 1), "y": round(center_y, 1)},
            }
        )

        if label == "person":
            face_seen = True
            person_detected = True

    face_locations = detect_face_locations(gray_frame)
    if face_locations:
        face_seen = True
        first_face = face_locations[0]
        recognized_name = match_face_name(gray_frame, first_face)
        face_boxes = []
        for x, y, w, h in face_locations:
            face_boxes.append([x, y, x + w, y + h])

        detections = [
            detection
            for detection in detections
            if detection["label"] not in ANIMAL_LABELS
            or all(calculate_iou(detection["box"], face_box) < 0.22 for face_box in face_boxes)
        ]

        x, y, w, h = first_face
        center_x = x + (w / 2)
        center_y = y + (h / 2)
        detections.append(
            {
                "label": recognized_name if recognized_name else "unknown face",
                "conf": 0.99,
                "box": [x, y, x + w, y + h],
                "distance_m": estimate_distance_m("person", float(w)),
                "position": {
                    "horizontal": describe_horizontal_position(center_x, frame_width),
                    "vertical": describe_vertical_position(center_y, frame_height),
                },
                "center": {"x": round(center_x, 1), "y": round(center_y, 1)},
            }
        )

    detections.sort(
        key=lambda item: item["distance_m"] if item["distance_m"] is not None else 9999
    )

    object_pairs = []
    for i in range(len(detections)):
        for j in range(i + 1, len(detections)):
            first = detections[i]
            second = detections[j]
            pixel_distance = sqrt(
                (first["center"]["x"] - second["center"]["x"]) ** 2
                + (first["center"]["y"] - second["center"]["y"]) ** 2
            )
            object_pairs.append(
                {
                    "between": [first["label"], second["label"]],
                    "pixel_distance": round(pixel_distance, 1),
                }
            )

    voice_parts = [build_detection_summary(detections)]
    if recognized_name:
        voice_parts.insert(0, f"Welcome back, {recognized_name}.")
    elif face_seen and known_names:
        voice_parts.insert(0, "Face detected but not recognized.")
    elif face_seen:
        voice_parts.insert(0, "Face detected. You can say your name to save it.")

    return {
        "detections": detections,
        "recognized_name": recognized_name,
        "face_seen": face_seen,
        "object_distances": object_pairs[:10],
        "voice": " ".join(voice_parts),
    }


@app.post("/save_face")
async def save_face(
    file: UploadFile = File(...),
    name: str = Query(..., min_length=1, max_length=60),
) -> Dict:
    content = await file.read()
    nparr = np.frombuffer(content, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image payload.")

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_locations = detect_face_locations(gray_image)
    # Fallback: if no face is found, use the full frame as a face region to allow saving
    if not face_locations:
        h, w = gray_image.shape[:2]
        face_locations = [(0, 0, w, h)]

    normalized_name = name.strip()
    if not normalized_name:
        raise HTTPException(status_code=400, detail="Name cannot be blank.")

    face_template = normalize_face(gray_image, face_locations[0])
    if face_template is None:
        raise HTTPException(status_code=400, detail="Unable to process face image.")

    matched_name = match_face_name(gray_image, face_locations[0])

    if matched_name and matched_name == normalized_name:
        known_encs.append(face_template)
        known_names.append(normalized_name)
    else:
        known_encs.append(face_template)
        known_names.append(normalized_name)

    # Trim to last N templates per name to keep DB small
    combined = list(zip(known_names, known_encs))
    pruned = []
    for n in set(known_names):
        samples = [c for c in combined if c[0] == n][-MAX_TEMPLATES_PER_NAME :]
        pruned.extend(samples)
    known_names[:] = [c[0] for c in pruned]
    known_encs[:] = [c[1] for c in pruned]

    save_known_faces()
    return {
        "status": "saved",
        "name": normalized_name,
        "message": f"Face saved for {normalized_name}.",
    }


@app.post("/location_voice")
def location_voice(payload: LocationPayload) -> Dict:
    lat_dir = "north" if payload.latitude >= 0 else "south"
    lon_dir = "east" if payload.longitude >= 0 else "west"
    lat_deg = abs(payload.latitude)
    lon_deg = abs(payload.longitude)
    label_text = f" near {payload.label}" if payload.label else ""
    accuracy_text = (
        f" with about {round(payload.accuracy_m, 1)} meters accuracy"
        if payload.accuracy_m is not None
        else ""
    )
    address = None
    try:
        geolocator = Nominatim(user_agent="vision-assistant")
        loc = geolocator.reverse((payload.latitude, payload.longitude), language="en", timeout=5)
        if loc and loc.address:
            address = loc.address
    except Exception:
        address = None

    if address:
        voice = f"You are near {address}{accuracy_text}."
    else:
        voice = (
            f"You are roughly {lat_deg:.2f} degrees {lat_dir} and {lon_deg:.2f} degrees {lon_dir}{label_text}{accuracy_text}."
        )
    return {"voice": voice, "address": address}


@app.post("/chat")
def chat(payload: ChatPayload) -> Dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY not set on server.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a concise assistant for the vision app. Keep replies short."},
            {"role": "user", "content": payload.message},
        ],
        "max_tokens": 120,
        "temperature": 0.6,
    }
    try:
        resp = requests.post("https://api.openai.com/v1/chat/completions", json=body, headers=headers, timeout=10)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return {"reply": content}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI request failed: {exc}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
