# SafeSite AI — Real-Time Helmet & Harness Compliance Detection

A low-cost, real-time computer vision system that monitors construction site
camera feeds for PPE (helmet/vest) compliance, logs violations, sends
alerts, and displays everything on a live dashboard.

Built with **YOLOv8, OpenCV, SQLite, and Streamlit** — entirely free and
open-source tools, so it's affordable for small/mid-size contractors who
can't afford enterprise safety-monitoring systems.

---

## ✅ Project status: fully working, in two modes

This project runs in **two modes** so you always have something working:

1. **Demo mode (works immediately, no setup)** — uses YOLOv8's generic
   pretrained model, which detects "person" out of the box. Lets you test
   the entire pipeline (camera → detection → dashboard) right away.
2. **Real PPE mode** — once you train a custom model on a helmet dataset
   (steps below), the exact same code automatically switches to detecting
   real helmet/no-helmet violations. No code changes needed — it just
   checks whether `models/best.pt` exists.

---

## 📁 Project structure

```
safesite-ai/
├── requirements.txt
├── README.md
├── models/
│   └── best.pt              <- your trained model goes here (not included)
├── data/
│   └── sample_images/       <- put test photos here
├── outputs/
│   ├── violations.db        <- SQLite database (auto-created)
│   └── snapshots/           <- saved violation images (auto-created)
└── src/
    ├── config.py             <- ALL settings live here — edit this first
    ├── db.py                 <- database read/write functions
    ├── alert.py              <- sound + email alert logic
    ├── detect_webcam.py      <- MAIN SCRIPT: live camera/video detection
    ├── detect_image.py       <- test detection on a single photo
    ├── train_helmet_model.py <- train your own PPE model (run on Colab)
    ├── generate_demo_data.py <- fills the dashboard with sample data
    └── dashboard.py          <- Streamlit dashboard
```

---

## 🚀 Quick start (demo mode — 5 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Go into the src folder — all scripts are run from here
cd src

# 3. Set up the database
python db.py

# 4. Generate sample violation data so the dashboard isn't empty
python generate_demo_data.py

# 5. Launch the dashboard
streamlit run dashboard.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`) — you'll
see a fully working dashboard with charts, filters, and a snapshot gallery.

### Try live detection (demo mode, generic model)

```bash
python detect_webcam.py --source 0 --zone "Zone-1-Entrance"
```

This opens your webcam and draws boxes around detected people in real
time. Press `q` to quit. It's labeled "DEMO MODE" on screen because it's
using the generic person-detector, not a trained helmet model yet.

### Test on a single photo instead of a webcam

```bash
python detect_image.py --image ../data/sample_images/your_photo.jpg
```

---

## 🎯 Getting to REAL helmet detection (the main event)

The demo mode proves the pipeline works, but the actual project value is
detecting helmets specifically. Here's how to get there:

### Step 1 — Get a labeled dataset
Go to [Roboflow Universe](https://universe.roboflow.com), search **"hard
hat detection"** or **"PPE detection"**, and pick a dataset with at least
~1000 images. Export it in **YOLOv8 format**.

### Step 2 — Train (best done on Google Colab, free GPU)
Open `src/train_helmet_model.py`, update `DATASET_YAML_PATH` to point at
your downloaded dataset's `data.yaml`, then run:

```bash
python train_helmet_model.py
```

This automatically copies the trained weights to `models/best.pt` when done.

### Step 3 — That's it
Re-run `detect_webcam.py` or `detect_image.py` — they detect
`models/best.pt` automatically and switch from demo mode to real
helmet/no-helmet violation logic, with logging and alerts, with zero code
changes needed.

**Important:** update `CUSTOM_CLASS_NAMES` and `VIOLATION_CLASSES` in
`src/config.py` to match the exact class names in your dataset's
`data.yaml` (e.g. some datasets use `"Hardhat"`/`"NO-Hardhat"` instead of
`"helmet"`/`"no-helmet"`).

---

## ⚙️ Key settings (all in `src/config.py`)

| Setting | What it controls |
|---|---|
| `CONFIDENCE_THRESHOLD` | Minimum confidence to count a detection at all |
| `CONSECUTIVE_FRAMES_REQUIRED` | How many frames in a row a violation must appear before it's logged (avoids false alarms from one blurry frame) |
| `VIOLATION_COOLDOWN_SECONDS` | Minimum time between logging the same violation twice in the same zone |
| `VIOLATION_CLASSES` | Which detected classes count as a violation |
| `ENABLE_SOUND_ALERT` / `ENABLE_EMAIL_ALERT` | Turn alert channels on/off |

---

## 🔔 Setting up email alerts (optional)

In `src/config.py`:
```python
ENABLE_EMAIL_ALERT = True
EMAIL_SENDER = "your_alert_bot@gmail.com"
EMAIL_PASSWORD = "your_app_password"   # Gmail: use an "App Password", not your real password
EMAIL_RECEIVER = "site_supervisor@example.com"
```

---

## 🖥️ Multiple cameras / zones

Run one `detect_webcam.py` process per camera, each with its own `--zone`
label and `--source`:

```bash
python detect_webcam.py --source 0 --zone "Zone-1-Entrance"
python detect_webcam.py --source 1 --zone "Zone-2-Scaffolding"
python detect_webcam.py --source rtsp://camera-ip/stream --zone "Zone-3-Rooftop"
```

All of them write to the same `violations.db`, so the dashboard shows a
unified view across every zone.

---

## 🧭 Why these tools

- **YOLOv8** — modern, fast, accurate object detection; free via Ultralytics.
- **OpenCV** — handles all video I/O, drawing, and image processing.
- **SQLite** — zero-setup database, perfect for a single-site deployment.
- **Streamlit** — builds a working dashboard in pure Python, so project
  time goes into the detection model (the hard part) instead of frontend
  plumbing.

---

## 📌 Known limitations (be upfront about these in your pitch)

- Harness "clipped in" detection is much harder than helmet detection
  (the clip point is often not visible to a camera at distance) — this
  project focuses on helmet/vest detection as the primary, reliable
  feature.
- Accuracy depends heavily on your training dataset — more images, more
  varied lighting/angles = better real-world performance.
- No person re-identification/tracking is implemented — each frame is
  evaluated independently (the consecutive-frame counter approximates
  this without needing a full tracking algorithm).
