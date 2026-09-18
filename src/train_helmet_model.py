"""
train_helmet_model.py
----------------------
Run this to train your OWN helmet/PPE detection model on a labeled dataset.

This is best run on Google Colab (free GPU) rather than your laptop CPU —
training on CPU can take hours even for a small dataset.

STEPS TO USE THIS FILE
-----------------------
1. Go to https://universe.roboflow.com and search "hard hat detection" or
   "PPE detection". Pick a dataset with at least ~1000 images.
2. Export it in "YOLOv8" format. Roboflow gives you either:
     a) a direct download ZIP, or
     b) a code snippet using the `roboflow` pip package.
3. Unzip/download it so you end up with a folder containing:
       data.yaml
       train/images  train/labels
       valid/images  valid/labels
       test/images   test/labels
4. Update DATASET_YAML_PATH below to point at that data.yaml file.
5. Update config.py's CUSTOM_CLASS_NAMES to match the classes listed
   inside that data.yaml (order matters).
6. Run this script:  python train_helmet_model.py
7. When training finishes, copy the resulting weights file into the
   models/ folder as best.pt:
       runs/detect/train/weights/best.pt  -->  models/best.pt
   (This script does that copy for you automatically at the end.)
8. Re-run detect_webcam.py or detect_image.py — they will now
   automatically use your trained model instead of the generic one.

NOTES ON epochs / imgsz
------------------------
- epochs=50 is a reasonable starting point for a small dataset (1-3k images).
- imgsz=640 is the YOLOv8 default and works well for most cases.
- If training is slow, use the "yolov8n" (nano) base model — smaller and
  faster than yolov8s/m/l/x, and plenty accurate for a class project.
"""

import os
import shutil

from ultralytics import YOLO

# ---------------------------------------------------------------------------
# 1. EDIT THIS PATH to point at your downloaded Roboflow dataset's data.yaml
# ---------------------------------------------------------------------------
DATASET_YAML_PATH = r"C:\Users\sunil\Downloads\Construction Site Safety.v2i.yolov8\data.yaml"

# Base pretrained model to fine-tune from. "yolov8n.pt" = nano (fastest).
BASE_MODEL = "yolov8n.pt"

EPOCHS = 50
IMAGE_SIZE = 640

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")


def main():
    if not os.path.exists(DATASET_YAML_PATH):
        print(f"[ERROR] Dataset not found at: {DATASET_YAML_PATH}")
        print("Edit DATASET_YAML_PATH at the top of this file to point at your")
        print("downloaded Roboflow dataset's data.yaml before running training.")
        return

    print(f"[TRAIN] Loading base model: {BASE_MODEL}")
    model = YOLO(BASE_MODEL)

    print(f"[TRAIN] Starting training for {EPOCHS} epochs on {DATASET_YAML_PATH}")
    model.train(data=DATASET_YAML_PATH, epochs=EPOCHS, imgsz=IMAGE_SIZE)

    # Ultralytics saves the best weights here by default:
    best_weights = os.path.join("runs", "detect", "train", "weights", "best.pt")

    if os.path.exists(best_weights):
        os.makedirs(MODELS_DIR, exist_ok=True)
        dest = os.path.join(MODELS_DIR, "best.pt")
        shutil.copy(best_weights, dest)
        print(f"[TRAIN] Done. Best model copied to: {dest}")
        print("[TRAIN] detect_webcam.py and detect_image.py will now use this model automatically.")
    else:
        print(f"[WARNING] Training finished but couldn't find weights at {best_weights}.")
        print("Check the runs/detect/train*/weights/ folder manually and copy best.pt into models/.")


if __name__ == "__main__":
    main()
