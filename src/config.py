"""
config.py
---------
Central place for all project settings. Change values here instead of
hunting through every file — zone names, thresholds, file paths, etc.
"""

import os

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
SNAPSHOTS_DIR = os.path.join(OUTPUTS_DIR, "snapshots")
DB_PATH = os.path.join(OUTPUTS_DIR, "violations.db")

# Pretrained general-purpose model (detects "person" — always works out of
# the box, used as a fallback / for testing the pipeline before you have a
# custom helmet-trained model).
GENERIC_MODEL_PATH = "yolov8n.pt"

# Path to YOUR custom-trained helmet/PPE model once you train one (see
# src/train_helmet_model.py). Until that file exists, the app automatically
# falls back to the generic person-detector so you can still demo the full
# pipeline (video -> detection -> logging -> alert -> dashboard).
CUSTOM_MODEL_PATH = os.path.join(MODELS_DIR, "best.pt")

# ---------------------------------------------------------------------------
# DETECTION SETTINGS
# ---------------------------------------------------------------------------

# Minimum confidence for a detection to count at all.
CONFIDENCE_THRESHOLD = 0.15

# How many consecutive violating frames are needed before we log a violation.
# This avoids logging a violation because of one blurry / occluded frame.
CONSECUTIVE_FRAMES_REQUIRED = 2

# Minimum seconds between two logged violations for the SAME zone, so a
# person standing without a helmet for 30 seconds doesn't create 200 rows.
VIOLATION_COOLDOWN_SECONDS = 1

# Class names your CUSTOM model should be trained on. Update this list to
# match the classes in your Roboflow dataset's data.yaml.
CUSTOM_CLASS_NAMES = [
    'Boots',
    'Hardhat',
    'Machinary',
    'No-Hardhat',
    'No-mask',
    'No-safetyvest',
    'Person',
    'Safetyvest'
]
# Classes (from the custom model) that count as a *violation* when detected.
VIOLATION_CLASSES = ['No-Hardhat', 'No-safetyvest', 'No-mask']
# ---------------------------------------------------------------------------
# ZONES
# ---------------------------------------------------------------------------
# A "zone" is just a label for whichever camera / area a frame comes from.
# In a real deployment each camera feed would be tagged with a fixed zone
# name. For a single-webcam demo, everything is tagged "Zone-1".
DEFAULT_ZONE = "Zone-1"

# ---------------------------------------------------------------------------
# ALERTING
# ---------------------------------------------------------------------------
ENABLE_SOUND_ALERT = True
ENABLE_EMAIL_ALERT = False  # flip to True and fill in EMAIL_* below to use

EMAIL_SENDER = "your_alert_bot@gmail.com"
EMAIL_PASSWORD = "your_app_password"          # use an app password, not your real password
EMAIL_RECEIVER = "site_supervisor@example.com"
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587
