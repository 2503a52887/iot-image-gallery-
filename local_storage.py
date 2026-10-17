"""
Local Storage Engine & AWS Simulator for IoT Image Gallery
Allows the application to run completely offline without an active AWS account,
simulating S3 bucket storage, DynamoDB table events, and Pillow-based Lambda thumbnail generation.
"""

import os
import json
import uuid
import io
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
S3_LOCAL_DIR = os.path.join(DATA_DIR, "s3")
ORIGINALS_DIR = os.path.join(S3_LOCAL_DIR, "originals")
THUMBNAILS_DIR = os.path.join(S3_LOCAL_DIR, "thumbnails")
DB_FILE = os.path.join(DATA_DIR, "dynamodb_events.json")
STATE_FILE = os.path.join(DATA_DIR, "device_state.json")

# Ensure required folders exist
os.makedirs(ORIGINALS_DIR, exist_ok=True)
os.makedirs(THUMBNAILS_DIR, exist_ok=True)


def load_device_state():
    """Load ESP32 and LED state from local file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    # Default initial state
    default_state = {
        "device_id": "ESP32-CAM-01",
        "device_status": "Active",  # Active or Inactive
        "led_status": "OFF",         # ON or OFF
        "last_ping": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_device_state(default_state)
    return default_state


def save_device_state(state):
    """Save ESP32 and LED state to local file."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def set_esp32_status(is_active: bool):
    """Update ESP32 device status."""
    state = load_device_state()
    state["device_status"] = "Active" if is_active else "Inactive"
    state["last_ping"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_device_state(state)
    return state


def set_led_status(is_on: bool):
    """Update ESP32 LED status."""
    state = load_device_state()
    state["led_status"] = "ON" if is_on else "OFF"
    save_device_state(state)
    return state


def load_events():
    """Load all image events simulating DynamoDB scan."""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                events = json.load(f)
                # Sort newest first
                return sorted(events, key=lambda x: x.get("timestamp", ""), reverse=True)
        except Exception:
            return []
    return []


def save_events(events):
    """Save events list to local json file simulating DynamoDB put."""
    with open(DB_FILE, "w") as f:
        json.dump(events, f, indent=2)


def generate_thumbnail(image_bytes: bytes, max_size=(300, 300)) -> bytes:
    """
    Generate a thumbnail from image bytes using Pillow, matching AWS Lambda logic.
    Maintains aspect ratio and converts to JPEG.
    """
    with Image.open(io.BytesIO(image_bytes)) as img:
        # Convert RGBA/P to RGB for JPEG compatibility
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        out_io = io.BytesIO()
        img.save(out_io, format="JPEG", quality=85)
        return out_io.getvalue()


def store_image_event(image_bytes: bytes, original_filename: str, event_source: str = "Dashboard Upload"):
    """
    Process image:
    1. Save original to local S3 simulation folder
    2. Generate thumbnail using Pillow and save to local thumbnails folder
    3. Record metadata in DynamoDB simulation file
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event_id = f"evt_{uuid.uuid4().hex[:10]}"
    ext = os.path.splitext(original_filename)[1].lower()
    if not ext:
        ext = ".jpg"

    safe_original_name = f"{event_id}_original{ext}"
    safe_thumb_name = f"{event_id}_thumb.jpg"

    original_path = os.path.join(ORIGINALS_DIR, safe_original_name)
    thumb_path = os.path.join(THUMBNAILS_DIR, safe_thumb_name)

    # Save original image (S3 Originals simulator)
    with open(original_path, "wb") as f:
        f.write(image_bytes)

    # Generate and save thumbnail (AWS Lambda + Pillow simulator)
    thumb_bytes = generate_thumbnail(image_bytes)
    with open(thumb_path, "wb") as f:
        f.write(thumb_bytes)

    # Query current device state
    dev_state = load_device_state()

    # Create DynamoDB event record
    event_record = {
        "event_id": event_id,
        "timestamp": timestamp,
        "filename": original_filename,
        "original_key": safe_original_name,
        "thumbnail_key": safe_thumb_name,
        "original_path": original_path,
        "thumbnail_path": thumb_path,
        "file_size_kb": round(len(image_bytes) / 1024, 2),
        "device_id": dev_state.get("device_id", "ESP32-CAM-01"),
        "device_status": dev_state.get("device_status", "Active"),
        "led_status": dev_state.get("led_status", "OFF"),
        "event_source": event_source,
        "storage": "Local S3 Simulator"
    }

    events = load_events()
    events.insert(0, event_record)
    save_events(events)

    return event_record


def create_synthetic_iot_image(title: str, subtitle: str, color_scheme="cyan") -> bytes:
    """Generate a clean synthetic camera frame image for mock captures."""
    width, height = 800, 600
    img = Image.new("RGB", (width, height), color="#0f172a")
    draw = ImageDraw.Draw(img)

    # Background gradient pattern
    colors = {
        "cyan": ("#082f49", "#0284c7", "#06b6d4"),
        "blue": ("#0c4a6e", "#0369a1", "#38bdf8"),
        "amber": ("#451a03", "#d97706", "#fbbf24")
    }.get(color_scheme, ("#082f49", "#0284c7", "#06b6d4"))

    # Top banner
    draw.rectangle([0, 0, width, 60], fill=colors[0])
    draw.line([0, 60, width, 60], fill=colors[2], width=2)

    # Camera viewfinder crosshairs
    cx, cy = width // 2, height // 2
    draw.line([cx - 40, cy, cx + 40, cy], fill=colors[2], width=2)
    draw.line([cx, cy - 40, cx, cy + 40], fill=colors[2], width=2)
    draw.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], outline=colors[2], width=1)

    # Corner brackets (viewfinder)
    bracket_len = 30
    # Top-left
    draw.line([40, 90, 40 + bracket_len, 90], fill="#38bdf8", width=3)
    draw.line([40, 90, 40, 90 + bracket_len], fill="#38bdf8", width=3)
    # Top-right
    draw.line([width - 40 - bracket_len, 90, width - 40, 90], fill="#38bdf8", width=3)
    draw.line([width - 40, 90, width - 40, 90 + bracket_len], fill="#38bdf8", width=3)
    # Bottom-left
    draw.line([40, height - 50, 40 + bracket_len, height - 50], fill="#38bdf8", width=3)
    draw.line([40, height - 50 - bracket_len, 40, height - 50], fill="#38bdf8", width=3)
    # Bottom-right
    draw.line([width - 40 - bracket_len, height - 50, width - 40, height - 50], fill="#38bdf8", width=3)
    draw.line([width - 40, height - 50 - bracket_len, width - 40, height - 50], fill="#38bdf8", width=3)

    # Info text box
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((30, 20), f"ESP32-CAM FEED // {title.upper()}", fill="#ffffff")
    draw.text((width - 220, 20), f"REC ● {ts}", fill="#ef4444")

    # Center label box
    draw.rectangle([cx - 200, cy + 120, cx + 200, cy + 180], fill="#1e293b", outline=colors[1], width=2)
    draw.text((cx - 180, cy + 130), title, fill="#e0f2fe")
    draw.text((cx - 180, cy + 155), subtitle, fill="#94a3b8")

    out_io = io.BytesIO()
    img.save(out_io, format="JPEG", quality=90)
    return out_io.getvalue()


def seed_sample_data():
    """Seeds 3 realistic initial IoT captures if the gallery is empty."""
    events = load_events()
    if len(events) > 0:
        return

    samples = [
        ("Laboratory Entrance Gate", "Motion Trigger - Authorized Access", "cyan"),
        ("IoT Edge Node Station #4", "Periodic Telemetry Snapshot", "blue"),
        ("Optical Sensor Checkpoint", "Ambient Lux Threshold Triggered", "amber")
    ]

    for title, subtitle, scheme in samples:
        img_bytes = create_synthetic_iot_image(title, subtitle, scheme)
        filename = f"{title.lower().replace(' ', '_')}.jpg"
        store_image_event(img_bytes, filename, event_source="ESP32 Edge Cam Trigger")


def trigger_esp32_capture_simulation():
    """
    Simulates a full ESP32 capture event cycle:
    1. Turn LED status ON
    2. Capture frame from camera
    3. Generate thumbnail with Pillow
    4. Save to S3 & DynamoDB
    5. Turn LED status OFF
    """
    # 1. Turn LED ON
    set_led_status(True)

    # 2. Generate frame
    title = f"ESP32-CAM Capture #{uuid.uuid4().hex[:4].upper()}"
    subtitle = "On-Demand Trigger Event via Dashboard"
    img_bytes = create_synthetic_iot_image(title, subtitle, "cyan")

    # 3. Store event
    filename = f"capture_{uuid.uuid4().hex[:6]}.jpg"
    event_record = store_image_event(img_bytes, filename, event_source="Capture Event Button")

    # 4. Turn LED OFF
    set_led_status(False)

    return event_record
