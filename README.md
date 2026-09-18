# 🦺 SafeSite AI — Real-Time PPE Compliance Detection

**SafeSite AI** is a low-cost computer vision system for monitoring construction-site camera feeds and identifying PPE compliance issues.

It uses **YOLOv8, OpenCV, SQLite, and Streamlit** to detect PPE-related violations, record them, capture violation snapshots, generate alerts, and display safety analytics through a dashboard.

> **Current focus:** Helmet and safety-vest compliance. Harness clip-in detection is not currently implemented reliably.

---

## 🎯 Problem

Construction sites require continuous safety monitoring, but manually observing multiple camera feeds can be difficult and time-consuming.

SafeSite AI aims to assist safety supervisors by automatically analyzing camera feeds and highlighting potential PPE violations.

### The system can:

* 🎥 Process live webcam/video feeds
* 🪖 Detect helmet compliance using a custom-trained model
* 🦺 Detect safety-vest compliance
* ⚠️ Identify configured PPE violations
* 📸 Save violation snapshots
* 🗄️ Log violations in SQLite
* 🔔 Generate sound/email alerts
* 📊 Display violation analytics in a Streamlit dashboard
* 🏗️ Organize detections by construction-site zones

---

# 🧠 How It Works

```text
Camera / Video
      ↓
   OpenCV
      ↓
    YOLOv8
      ↓
 PPE Detection
      ↓
Violation Check
      ↓
 ┌────┴─────────────┐
 ↓                  ↓
Compliant        Violation
                    ↓
          ┌─────────┴─────────┐
          ↓                   ↓
      Snapshot             Alert
          ↓
     SQLite Database
          ↓
  Streamlit Dashboard
```

---

# 🚀 Project Modes

SafeSite AI supports two modes.

## 1. Demo Mode

Demo mode uses the standard YOLOv8 pretrained model.

It can detect objects such as **people**, allowing the complete application pipeline to be tested without training a custom PPE model.

This mode is useful for demonstrating:

```text
Camera → Detection → Database → Dashboard
```

---

## 2. Real PPE Detection

Real PPE detection uses a custom-trained YOLOv8 model.

After training, place the trained model at:

```text
models/best.pt
```

The application can then use the custom model for PPE detection.

The exact classes depend on the dataset used for training.

Example:

```text
helmet
no-helmet
vest
no-vest
```

Some datasets may use different names, such as:

```text
Hardhat
NO-Hardhat
Safety Vest
NO-Safety Vest
```

Therefore, the class names configured in the application must match the trained model.

---

# 📁 Project Structure

```text
safesite-ai/
│
├── requirements.txt
├── README.md
│
├── models/
│   └── best.pt
│
├── data/
│   └── sample_images/
│
├── outputs/
│   ├── violations.db
│   └── snapshots/
│
└── src/
    ├── config.py
    ├── db.py
    ├── alert.py
    ├── detect_webcam.py
    ├── detect_image.py
    ├── train_helmet_model.py
    ├── generate_demo_data.py
    └── dashboard.py
```

### Important Files

| File                    | Purpose                          |
| ----------------------- | -------------------------------- |
| `config.py`             | Project configuration            |
| `db.py`                 | SQLite database operations       |
| `alert.py`              | Sound and email alerts           |
| `detect_webcam.py`      | Real-time camera/video detection |
| `detect_image.py`       | Detection on individual images   |
| `train_helmet_model.py` | Custom YOLOv8 model training     |
| `generate_demo_data.py` | Generates sample dashboard data  |
| `dashboard.py`          | Streamlit dashboard              |

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/safesite-ai.git
cd safesite-ai
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Quick Start — Demo Mode

Go to the `src` directory:

```bash
cd src
```

Initialize the database:

```bash
python db.py
```

Generate sample violation data:

```bash
python generate_demo_data.py
```

Start the dashboard:

```bash
streamlit run dashboard.py
```

Open the Streamlit URL shown in the terminal, usually:

```text
http://localhost:8501
```

---

# 🎥 Run Live Detection

To use the default webcam:

```bash
python detect_webcam.py --source 0 --zone "Zone-1-Entrance"
```

Example zones:

```text
Zone-1-Entrance
Zone-2-Scaffolding
Zone-3-Rooftop
```

Press `q` to stop the detection window.

---

# 🖼️ Test an Image

Place an image inside:

```text
data/sample_images/
```

Then run:

```bash
python detect_image.py --image ../data/sample_images/your_photo.jpg
```

---

# 🎯 Train a Custom PPE Model

For real helmet/vest detection, a custom labeled dataset is required.

A suitable dataset can be obtained from sources such as:

[Roboflow Universe](https://universe.roboflow.com/?utm_source=chatgpt.com)

Search for:

```text
hard hat detection
PPE detection
helmet detection
construction safety
```

Choose a dataset with appropriate PPE classes and export it in a YOLO-compatible format.

---

## Training

Open:

```text
src/train_helmet_model.py
```

Configure the dataset YAML path:

```text
DATASET_YAML_PATH
```

Then run:

```bash
python train_helmet_model.py
```

After successful training, place the trained model at:

```text
models/best.pt
```

The detection scripts can then use the custom model.

---

# ⚙️ Configuration

Most settings are available in:

```text
src/config.py
```

| Setting                       | Purpose                                                          |
| ----------------------------- | ---------------------------------------------------------------- |
| `CONFIDENCE_THRESHOLD`        | Minimum confidence required for a detection                      |
| `CONSECUTIVE_FRAMES_REQUIRED` | Number of consecutive frames required before logging a violation |
| `VIOLATION_COOLDOWN_SECONDS`  | Prevents repeated logging of the same violation too frequently   |
| `VIOLATION_CLASSES`           | Classes treated as PPE violations                                |
| `ENABLE_SOUND_ALERT`          | Enables/disables sound alerts                                    |
| `ENABLE_EMAIL_ALERT`          | Enables/disables email alerts                                    |

### Why consecutive frames?

Object detection can occasionally produce incorrect results because of:

* Motion
* Blur
* Occlusion
* Poor lighting

Requiring a violation to appear across multiple consecutive frames can help reduce false alerts.

---

# 🔔 Email Alerts

Email alerts are optional.

Configure the required settings in:

```text
src/config.py
```

Example:

```python
ENABLE_EMAIL_ALERT = True

EMAIL_SENDER = "your_alert_bot@gmail.com"
EMAIL_PASSWORD = "your_app_password"
EMAIL_RECEIVER = "site_supervisor@example.com"
```

> **Security:** Never commit real passwords, API keys, or other credentials to GitHub.

---

# 📹 Multiple Cameras / Zones

Multiple detection processes can be run for different cameras or zones.

Example:

```bash
python detect_webcam.py --source 0 --zone "Zone-1-Entrance"
```

```bash
python detect_webcam.py --source 1 --zone "Zone-2-Scaffolding"
```

For an RTSP camera:

```bash
python detect_webcam.py --source "rtsp://camera-ip/stream" --zone "Zone-3-Rooftop"
```

The detections can be stored in the same SQLite database:

```text
outputs/violations.db
```

This allows the dashboard to provide a unified view across different zones.

---

# 📊 Dashboard

The Streamlit dashboard provides a centralized view of recorded safety events.

It can display:

* Total violations
* Violation types
* Zone-wise statistics
* Violation trends
* Recent events
* Saved violation snapshots

---

# 🛠️ Technology Stack

| Technology               | Purpose                       |
| ------------------------ | ----------------------------- |
| **Python**               | Application development       |
| **YOLOv8 / Ultralytics** | Object detection              |
| **OpenCV**               | Video and image processing    |
| **SQLite**               | Violation storage             |
| **Streamlit**            | Monitoring dashboard          |
| **Pandas**               | Data processing and analytics |

---

# ⚠️ Limitations

### 1. Harness Clip Detection

Reliable detection of whether a safety harness is actually clipped in is significantly more difficult than detecting a helmet or vest.

The clip point may not be visible from a distant camera.

Therefore, the current implementation focuses primarily on **helmet and vest compliance**.

### 2. Model Accuracy

Detection performance depends heavily on the training dataset.

Factors such as:

* Lighting
* Camera angle
* Occlusion
* Worker distance
* Crowd density
* PPE appearance

can affect accuracy.

### 3. No Full Person Tracking

The current system does not implement dedicated person tracking or re-identification.

The consecutive-frame mechanism helps reduce isolated false detections but should not be considered a full tracking solution.

### 4. Prototype

This project is a prototype intended for educational, research, and demonstration purposes.

A production deployment would require additional validation, security, privacy controls, reliable hardware, and operational monitoring.

---

# 🔮 Future Improvements

Possible improvements include:
- Person tracking and re-identification
- Improved PPE detection accuracy
- Reliable harness detection
- Mobile notifications
- Cloud-based monitoring

---

# 📌 Project Objective

SafeSite AI is designed as a **safety-monitoring assistant**, not a replacement for human safety officers.

The objective is to help supervisors identify potential PPE violations faster by continuously analyzing camera feeds.

```text
Human Safety Officer
        +
   SafeSite AI
        ↓
Automated Monitoring
        ↓
Faster Identification of
Potential PPE Violations
```

---

## 👩‍💻 Project

**SafeSite AI — Real-Time PPE Compliance Detection**

Built with:

**YOLOv8 · OpenCV · SQLite · Streamlit · Python**
