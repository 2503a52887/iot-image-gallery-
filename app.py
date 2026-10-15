
import streamlit as st
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from PIL import Image, ImageOps
from pathlib import Path
from datetime import datetime
from io import BytesIO

# Page setup
st.set_page_config(
    page_title="IoT Image Gallery",
    page_icon="📸",
    layout="wide"
)

# Folders
BASE_DIR = Path(__file__).parent
IMAGE_DIR = BASE_DIR / "images"
THUMB_DIR = BASE_DIR / "thumbnails"

IMAGE_DIR.mkdir(exist_ok=True)
THUMB_DIR.mkdir(exist_ok=True)

# AWS settings
BUCKET = "chandhu-iot-gallery-2027"
REGION = "us-east-1"

# Dashboard heading
st.title("📸 IoT Image Gallery")
st.write("ESP32 Event Capture and Image Monitoring Dashboard")

# Create thumbnail
def create_thumbnail(image, path):
    thumb_path = THUMB_DIR / f"{path.stem}_thumb.jpg"
    thumb = ImageOps.contain(image, (400, 300))
    thumb.save(thumb_path, format="JPEG")
    return thumb_path

# Get local images
def get_images():
    return sorted(
        [
            p for p in IMAGE_DIR.iterdir()
            if p.is_file()
            and p.suffix.lower() in [".png", ".jpg", ".jpeg"]
        ],
        key=lambda p: p.name.lower()
    )

# Metrics
images = get_images()
c1, c2, c3 = st.columns(3)
c1.metric("IoT Device", "ESP32")
c2.metric("Gallery Status", "Active")
c3.metric("Total Local Images", len(images))

st.divider()

# Capture event
st.subheader("🔘 Capture Event")

if "event_time" not in st.session_state:
    st.session_state.event_time = None

if st.button("📸 Capture Event"):
    st.session_state.event_time = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )
    st.success("Event captured successfully!")

if st.session_state.event_time:
    st.write("Last Event:", st.session_state.event_time)
    st.success("🟢 LED Status: ON (simulated)")
else:
    st.info("🔴 LED Status: OFF (simulated)")

st.caption(
    "Capture Event and LED are simulated; "
    "this button does not control a physical ESP32."
)

st.divider()

# Upload local image
st.subheader("📤 Upload New Image")

uploaded_file = st.file_uploader(
    "Choose a JPG or PNG image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    try:
        with Image.open(uploaded_file) as original:
            img = ImageOps.exif_transpose(original).convert("RGB")

        filename = Path(uploaded_file.name).name
        save_path = IMAGE_DIR / filename

        if save_path.suffix.lower() == ".png":
            img.save(save_path, format="PNG")
        else:
            img.save(save_path, format="JPEG")

        create_thumbnail(img, save_path)
        st.success(f"{filename} uploaded successfully!")
        st.image(img, caption=filename, width=300)

    except Exception as error:
        st.error(f"Image error: {error}")

st.divider()

# AWS S3 image
st.subheader("☁️ AWS S3 Image Gallery")
st.write(f"Bucket: `{BUCKET}`")
s3_filename = st.text_input(
    "S3 image filename",
    value="bottle.png"
)

if st.button("Load Image from AWS S3"):
    try:
        # Uses credentials configured for this Python process.
        s3 = boto3.client("s3", region_name=REGION)

        response = s3.get_object(
            Bucket=BUCKET,
            Key=s3_filename.strip()
        )

        image_bytes = response["Body"].read()

        with Image.open(BytesIO(image_bytes)) as original:
            s3_image = ImageOps.exif_transpose(original).convert("RGB")

        st.image(
            s3_image,
            caption=f"AWS S3: {s3_filename}",
            width=400
        )
        st.success("Image loaded successfully from S3!")

        # Save a local copy for the gallery
        local_name = Path(s3_filename).name
        local_path = IMAGE_DIR / local_name

        if local_path.suffix.lower() == ".png":
            s3_image.save(local_path, format="PNG")
        else:
            s3_image.save(local_path, format="JPEG")

        create_thumbnail(s3_image, local_path)
        st.info("A local gallery copy and thumbnail were created.")

    except (ClientError, BotoCoreError) as error:
        st.error(
            "S3 image could not be loaded. Check AWS credentials, "
            "bucket, filename, region, and s3:GetObject permission."
        )
        st.code(str(error))

    except Exception as error:
        st.error(f"Could not open image: {error}")

st.divider()

# Local image gallery
st.subheader("🖼️ Image Gallery")
images = get_images()

if not images:
    st.warning(
        "No local images found. Upload a photo above "
        "or load bottle.png from AWS S3."
    )
else:
    for start in range(0, len(images), 3):
        cols = st.columns(3)

        for col, path in zip(cols, images[start:start + 3]):
            with col:
                try:
                    with Image.open(path) as original:
                        img = ImageOps.exif_transpose(
                            original
                        ).convert("RGB")

                    thumb_path = create_thumbnail(img, path)

                    st.image(
                        img,
                        caption=path.name,
                        use_container_width=True
                    )

                    st.caption("✅ Thumbnail created")

                    with Image.open(thumb_path) as thumb:
                        st.image(
                            thumb,
                            caption=f"{path.stem} thumbnail",
                            width=200
                        )

                except Exception as error:
                    st.error(
                        f"Cannot open {path.name}: {error}"
                    )

st.divider()

st.caption(
    "IoT Image Gallery | ESP32 | AWS IoT Core | "
    "S3 | Lambda | API Gateway | DynamoDB"
)
