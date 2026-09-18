"""
dashboard.py
------------
The supervisor-facing dashboard. Reads straight from the SQLite database
that detect_webcam.py / detect_image.py write to.

USAGE
-----
    streamlit run dashboard.py

Then open the URL it prints (usually http://localhost:8501).
"""

import os
import sys

import pandas as pd
import streamlit as st

# Allow running `streamlit run dashboard.py` directly from the src/ folder.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DEFAULT_ZONE
from db import init_db, get_all_violations, clear_all_violations

st.set_page_config(page_title="SafeSite AI Dashboard", layout="wide")

init_db()

st.title("🦺 SafeSite AI — Safety Compliance Dashboard")
st.caption("Real-time helmet & harness compliance monitoring")

violations = get_all_violations()
df = pd.DataFrame(violations)

# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------
if df.empty:
    st.info(
        "No violations logged yet. Run `python detect_webcam.py` or "
        "`python detect_image.py --image your_photo.jpg --log` to generate data, "
        "then refresh this page."
    )
    st.stop()

df["timestamp"] = pd.to_datetime(df["timestamp"])

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

zones = ["All"] + sorted(df["zone"].unique().tolist())
selected_zone = st.sidebar.selectbox("Zone", zones)

violation_types = ["All"] + sorted(df["violation_type"].unique().tolist())
selected_type = st.sidebar.selectbox("Violation type", violation_types)

filtered_df = df.copy()
if selected_zone != "All":
    filtered_df = filtered_df[filtered_df["zone"] == selected_zone]
if selected_type != "All":
    filtered_df = filtered_df[filtered_df["violation_type"] == selected_type]

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Clear all data (demo reset)"):
    clear_all_violations()
    st.sidebar.success("Cleared. Refresh the page.")

# ---------------------------------------------------------------------------
# Headline metrics
# ---------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)

today = pd.Timestamp.now().normalize()
violations_today = df[df["timestamp"] >= today]

col1.metric("Total violations logged", len(df))
col2.metric("Violations today", len(violations_today))
col3.metric("Zones monitored", df["zone"].nunique())

st.markdown("---")

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
# chart_col1, chart_col2 = st.columns(2)

# with chart_col1:
#     st.subheader("Violations by zone")
#     st.bar_chart(df["zone"].value_counts())

# with chart_col2:
#     st.subheader("Violations by type")
#     st.bar_chart(df["violation_type"].value_counts())

# st.subheader("Violations over time")
# time_series = df.set_index("timestamp").resample("h").size()
# st.line_chart(time_series)

# st.markdown("---")

# ---------------------------------------------------------------------------
# Recent violations table + snapshot gallery
# ---------------------------------------------------------------------------
st.subheader("Recent violations")
st.dataframe(
    filtered_df[["timestamp", "zone", "violation_type", "confidence"]],
    use_container_width=True,
)

st.subheader("Snapshot gallery (most recent 8)")
gallery_rows = filtered_df.head(8)
gallery_cols = st.columns(4)

for idx, (_, row) in enumerate(gallery_rows.iterrows()):
    col = gallery_cols[idx % 4]
    img_path = row.get("image_path")
    with col:
        if img_path and os.path.exists(img_path):
            st.image(img_path, caption=f"{row['violation_type']} — {row['zone']}", use_container_width=True)
        else:
            st.write(f"{row['violation_type']} — {row['zone']} (image not found)")

st.markdown("---")
st.caption("SafeSite AI — built with YOLOv8, OpenCV, SQLite, and Streamlit.")