"""
detect_webcam.py
-----------------
The core of the project: reads a live camera, runs YOLO, tracks safety violations,
logs to the SQLite database, and plays an alert tone.
"""

import argparse
import os
import threading
import time
from collections import defaultdict

import cv2
from ultralytics import YOLO

from config import (
    CUSTOM_MODEL_PATH,
    GENERIC_MODEL_PATH,
    CONFIDENCE_THRESHOLD,
    CONSECUTIVE_FRAMES_REQUIRED,
    VIOLATION_COOLDOWN_SECONDS,
    VIOLATION_CLASSES,
    DEFAULT_ZONE,
    SNAPSHOTS_DIR,
)
from db import init_db, log_violation, get_last_violation_time
from alert import trigger_alert


def load_model():
    if os.path.exists(CUSTOM_MODEL_PATH):
        print(f"[MODEL] Loading custom-trained model: {CUSTOM_MODEL_PATH}")
        return YOLO(CUSTOM_MODEL_PATH), True
    print(f"[MODEL] Falling back to generic pretrained model: {GENERIC_MODEL_PATH}")
    return YOLO(GENERIC_MODEL_PATH), False


def play_alert_async(zone, v_class):
    """Run alert in a background thread so the video feed doesn't freeze."""
    thread = threading.Thread(target=trigger_alert, args=(zone, v_class), daemon=True)
    thread.start()


def run(source, zone):
    init_db()
    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)

    model, is_custom_model = load_model()

    try:
        source = int(source)
    except (TypeError, ValueError):
        pass

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"[ERROR] Could not open video source: {source}")
        return

    consecutive_counts = defaultdict(int)

    print("[RUN] Starting detection. Press 'q' in the video window to quit.")
    print(f"[CONFIG] Target Violation Classes: {VIOLATION_CLASSES}")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[INFO] End of stream / camera disconnected.")
            break

        results = model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
        annotated_frame = results[0].plot()

        detected_classes_this_frame = set()
        if results[0].boxes is not None:
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                cls_name = model.names[cls_id]
                confidence = float(box.conf[0])
                detected_classes_this_frame.add((cls_name, confidence))

        if is_custom_model:
            # Case-insensitive matching to protect against subtle YAML discrepancies
            normalized_violation_classes = {v.strip().lower(): v for v in VIOLATION_CLASSES}
            
            violations_seen = set()
            for c_name, c_conf in detected_classes_this_frame:
                if c_name.strip().lower() in normalized_violation_classes:
                    matched_class = normalized_violation_classes[c_name.strip().lower()]
                    violations_seen.add(matched_class)

            # Debug output if any violation class is spotted on screen
            if violations_seen:
                print(f"[TRACKING] Violations in frame: {violations_seen}")

            for v_class in violations_seen:
                consecutive_counts[v_class] += 1

            # Decrement instead of hard-resetting to 0 for smoother detection
            for tracked_class in list(consecutive_counts.keys()):
                if tracked_class not in violations_seen:
                    consecutive_counts[tracked_class] = max(0, consecutive_counts[tracked_class] - 1)

            for v_class, count in consecutive_counts.items():
                if count >= CONSECUTIVE_FRAMES_REQUIRED:
                    last_time = get_last_violation_time(zone, v_class)
                    cooldown_ok = (
                        last_time is None
                        or (time.time() - last_time.timestamp()) > VIOLATION_COOLDOWN_SECONDS
                    )
                    if cooldown_ok:
                        confidence = next(
                            (conf for c, conf in detected_classes_this_frame if c.strip().lower() == v_class.strip().lower()),
                            0.0,
                        )
                        snapshot_name = f"{zone}_{v_class}_{int(time.time())}.jpg".replace(" ", "_")
                        snapshot_path = os.path.join(SNAPSHOTS_DIR, snapshot_name)
                        cv2.imwrite(snapshot_path, annotated_frame)

                        log_violation(zone, v_class, confidence, snapshot_path)
                        play_alert_async(zone, v_class)
                        print(f"\n🚨 [VIOLATION SAVED & BEEPED] {v_class} in {zone} (conf: {confidence:.2f})\n")
                        consecutive_counts[v_class] = 0
        else:
            cv2.putText(
                annotated_frame,
                "DEMO MODE: generic model",
                (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2,
            )

        cv2.putText(
            annotated_frame,
            f"Zone: {zone}",
            (10, annotated_frame.shape[0] - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        cv2.imshow("SafeSite AI - Live Monitor", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("[RUN] Quit key pressed. Shutting down.")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SafeSite AI real-time PPE monitor")
    parser.add_argument(
        "--source",
        default="0",
        help="Webcam index (e.g. 0) or path/URL to a video file. Default: 0",
    )
    parser.add_argument(
        "--zone",
        default=DEFAULT_ZONE,
        help="Label for this camera's zone, used in logs and the dashboard.",
    )
    args = parser.parse_args()
    run(args.source, args.zone)