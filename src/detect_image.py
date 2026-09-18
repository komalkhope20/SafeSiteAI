"""
detect_image.py
----------------
Quick way to test your detector on a single photo without needing a
webcam — useful for checking your setup works, and for grabbing a
screenshot for your pitch deck / report.

USAGE
-----
    python detect_image.py --image path/to/photo.jpg
    python detect_image.py --image path/to/photo.jpg --zone "Zone-3-Rooftop"

Saves an annotated copy to outputs/snapshots/ and prints what was detected.
Does NOT open a display window, so it also works on servers / this sandbox
with no monitor attached.
"""

import argparse
import os
import time

import cv2
from ultralytics import YOLO

from config import CUSTOM_MODEL_PATH, GENERIC_MODEL_PATH, CONFIDENCE_THRESHOLD, SNAPSHOTS_DIR, DEFAULT_ZONE
from db import init_db, log_violation
from config import VIOLATION_CLASSES


def load_model():
    if os.path.exists(CUSTOM_MODEL_PATH):
        print(f"[MODEL] Using custom model: {CUSTOM_MODEL_PATH}")
        return YOLO(CUSTOM_MODEL_PATH), True
    print(f"[MODEL] No custom model found — using generic pretrained model: {GENERIC_MODEL_PATH}")
    return YOLO(GENERIC_MODEL_PATH), False


def run(image_path, zone, log_to_db=False):
    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        return

    init_db()
    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)

    model, is_custom_model = load_model()
    results = model(image_path, conf=CONFIDENCE_THRESHOLD, verbose=False)
    annotated = results[0].plot()

    print("\n[DETECTIONS]")
    found_violation = False
    if results[0].boxes is not None:
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]
            confidence = float(box.conf[0])
            print(f"  - {cls_name}: {confidence:.2f}")

            if is_custom_model and cls_name in VIOLATION_CLASSES:
                found_violation = True
                if log_to_db:
                    log_violation(zone, cls_name, confidence, image_path)

    if not results[0].boxes or len(results[0].boxes) == 0:
        print("  (nothing detected — try a clearer photo or lower CONFIDENCE_THRESHOLD in config.py)")

    out_name = f"test_{int(time.time())}.jpg"
    out_path = os.path.join(SNAPSHOTS_DIR, out_name)
    cv2.imwrite(out_path, annotated)
    print(f"\n[SAVED] Annotated image written to: {out_path}")

    if found_violation and log_to_db:
        print("[DB] Violation(s) logged to database.")
    elif not is_custom_model:
        print("[NOTE] Running in demo mode (generic model) — no real PPE violation logic applied.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run SafeSite AI detection on a single image")
    parser.add_argument("--image", required=True, help="Path to the image file")
    parser.add_argument("--zone", default=DEFAULT_ZONE, help="Zone label for this image")
    parser.add_argument("--log", action="store_true", help="Log any detected violations to the database")
    args = parser.parse_args()
    run(args.image, args.zone, args.log)
