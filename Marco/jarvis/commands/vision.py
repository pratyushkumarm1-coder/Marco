import cv2
import numpy as np
from datetime import datetime
from ultralytics import YOLO
from ..config import OPENAI_API_KEY
from ..memory import log_command
from openai import OpenAI


model = YOLO("yolov8n.pt")
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def capture_frame(camera_index: int = 0) -> np.ndarray | None:
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("[WARN] Could not open webcam")
        return None
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("[WARN] Could not capture frame")
        return None
    return frame


def detect_objects(frame: np.ndarray, confidence: float = 0.4) -> list[dict]:
    results = model(frame, verbose=False)
    detections = []
    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            if conf >= confidence:
                label = model.names[cls_id]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({
                    "label": label,
                    "confidence": round(conf, 2),
                    "bbox": [x1, y1, x2, y2],
                })
    return detections


def describe_scene(detections: list[dict]) -> str:
    if not detections:
        return "I can see the surroundings but nothing distinct was detected."

    labels = [d["label"] for d in detections]
    unique_labels = list(dict.fromkeys(labels))
    count_map = {l: labels.count(l) for l in unique_labels}

    object_summary = ", ".join(
        f"{count} {label}{'s' if count > 1 else ''}" if count > 1 else label
        for label, count in count_map.items()
    )

    prompt = (
        f"I used object detection and found: {object_summary}. "
        "Describe this scene in 1-2 natural sentences as if you are seeing it yourself. "
        "Be concise and conversational. No markdown, no bullet points."
    )

    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are Marco describing what you see through a camera. Be brief and natural."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=150,
    )

    return response.choices[0].message.content.strip()


def save_snapshot(frame: np.ndarray, detections: list[dict], description: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"snapshots/snap_{timestamp}.jpg"
    cv2.imwrite(filename, frame)
    log_command(
        command="vision_scan",
        parameters={"detections": detections, "filename": filename},
        status="success",
        response=description,
    )
    return filename


def full_scan(camera_index: int = 0) -> tuple[str, list[dict]]:
    frame = capture_frame(camera_index)
    if frame is None:
        return "I am unable to access the camera at the moment, sir.", []

    detections = detect_objects(frame)
    description = describe_scene(detections)

    try:
        save_snapshot(frame, detections, description)
    except Exception:
        pass

    return description, detections
