"""
generate_demo_data.py
----------------------
Populates the database with realistic-looking sample violations so you can
show off the dashboard immediately — without needing a trained model,
webcam, or real footage yet. Great for a first look, screenshots for your
report, or as a fallback if live detection isn't working during a demo.

USAGE
-----
    python generate_demo_data.py

This does NOT touch your real detection pipeline — it just writes rows to
violations.db and generates simple placeholder snapshot images.

Run `python db.py` once first if you haven't already (this script also
calls init_db() itself, so that's not strictly required).
"""

import os
import random
from datetime import datetime, timedelta

import cv2
import numpy as np

from config import SNAPSHOTS_DIR
from db import init_db, log_violation, clear_all_violations

ZONES = ["Zone-1-Entrance", "Zone-2-Scaffolding", "Zone-3-Rooftop", "Zone-4-Storage"]
VIOLATION_TYPES = ["no-helmet", "no-vest"]


def make_placeholder_snapshot(zone, violation_type, index):
    """Creates a simple synthetic image standing in for a real camera
    snapshot, so the dashboard's image gallery has something to display."""
    img = np.full((300, 400, 3), (40, 40, 40), dtype=np.uint8)

    # A crude "person" silhouette so it doesn't look like a blank card.
    cv2.circle(img, (200, 90), 30, (200, 200, 200), -1)          # head
    cv2.rectangle(img, (160, 120), (240, 240), (200, 200, 200), -1)  # body

    box_color = (0, 0, 255)  # red box = violation
    cv2.rectangle(img, (140, 60), (260, 250), box_color, 3)
    cv2.putText(img, violation_type.upper(), (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    cv2.putText(img, zone, (20, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
    path = os.path.join(SNAPSHOTS_DIR, f"demo_{zone}_{violation_type}_{index}.jpg".replace(" ", "_"))
    cv2.imwrite(path, img)
    return path


def main():
    init_db()
    clear_all_violations()

    print("[DEMO] Generating sample violations...")
    now = datetime.now()

    count = 0
    for day_offset in range(2):  # today and yesterday
        for _ in range(15):
            zone = random.choice(ZONES)
            violation_type = random.choice(VIOLATION_TYPES)
            confidence = round(random.uniform(0.55, 0.95), 2)
            timestamp = now - timedelta(
                days=day_offset,
                hours=random.randint(0, 12),
                minutes=random.randint(0, 59),
            )

            snapshot_path = make_placeholder_snapshot(zone, violation_type, count)

            # log_violation always stamps "now" internally, so we insert
            # directly via a small workaround to backdate demo timestamps.
            import sqlite3
            from config import DB_PATH

            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                """
                INSERT INTO violations (timestamp, zone, violation_type, confidence, image_path)
                VALUES (?, ?, ?, ?, ?)
                """,
                (timestamp.isoformat(timespec="seconds"), zone, violation_type, confidence, snapshot_path),
            )
            conn.commit()
            conn.close()
            count += 1

    print(f"[DEMO] Inserted {count} sample violations across {len(ZONES)} zones.")
    print("[DEMO] Run `streamlit run dashboard.py` to view them.")


if __name__ == "__main__":
    main()
