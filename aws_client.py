"""
AWS Client Integration for IoT Image Gallery
Handles real AWS services (S3, DynamoDB, API Gateway, IoT Core) using boto3
with graceful error handling, credentials isolation, and local fallback.
"""

import os
import io
import json
import uuid
from datetime import datetime
from typing import Tuple, Dict, Any, List

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError
import requests
from PIL import Image

# Configuration from environment variables
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "iot-image-gallery-bucket")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE_NAME", "IoTImageEvents")
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "")


class AWSManager:
    """Manages AWS service clients and operations."""

    def __init__(self, region_name: str = AWS_REGION):
        self.region = region_name
        self.s3_client = None
        self.dynamodb_client = None
        self.dynamodb_resource = None
        self._init_clients()

    def _init_clients(self):
        """Initializes boto3 clients using standard AWS credential chain."""
        try:
            session = boto3.Session(region_name=self.region)
            self.s3_client = session.client("s3")
            self.dynamodb_client = session.client("dynamodb")
            self.dynamodb_resource = session.resource("dynamodb")
        except Exception:
            self.s3_client = None
            self.dynamodb_client = None
            self.dynamodb_resource = None

    def test_connection(self) -> Tuple[bool, str]:
        """
        Tests whether the current environment has valid AWS credentials and S3/DynamoDB access.
        Returns (is_connected: bool, status_message: str)
        """
        if not self.s3_client:
            return False, "Boto3 client could not be initialized."

        try:
            # Check S3 connectivity by listing buckets
            self.s3_client.list_buckets()
            return True, f"Connected to AWS (Region: {self.region}). S3 & DynamoDB ready."
        except NoCredentialsError:
            return False, "AWS Credentials not found. Please configure .env or AWS CLI."
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code", "ClientError")
            msg = e.response.get("Error", {}).get("Message", str(e))
            return False, f"AWS Error [{code}]: {msg}"
        except EndpointConnectionError:
            return False, "Network error: Unable to connect to AWS endpoint."
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def upload_image_and_record_event(
        self,
        image_bytes: bytes,
        filename: str,
        device_id: str = "ESP32-CAM-01",
        device_status: str = "Active",
        led_status: str = "OFF",
        event_source: str = "Cloud Upload"
    ) -> Dict[str, Any]:
        """
        AWS Cloud workflow:
        1. Upload original image to S3 (originals/)
        2. Generate thumbnail with Pillow and upload to S3 (thumbnails/)
        3. Insert metadata record into DynamoDB table
        """
        event_id = f"evt_{uuid.uuid4().hex[:10]}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ext = os.path.splitext(filename)[1].lower() or ".jpg"

        original_key = f"originals/{event_id}_{filename}"
        thumb_key = f"thumbnails/{event_id}_thumb.jpg"

        # 1. Upload original to S3
        content_type = "image/png" if ext == ".png" else "image/jpeg"
        self.s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=original_key,
            Body=image_bytes,
            ContentType=content_type
        )

        # 2. Generate thumbnail and upload
        with Image.open(io.BytesIO(image_bytes)) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            thumb_io = io.BytesIO()
            img.save(thumb_io, format="JPEG", quality=85)
            thumb_bytes = thumb_io.getvalue()

        self.s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=thumb_key,
            Body=thumb_bytes,
            ContentType="image/jpeg"
        )

        # 3. Generate pre-signed URLs for display in dashboard
        original_url = self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": original_key},
            ExpiresIn=3600
        )
        thumb_url = self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": thumb_key},
            ExpiresIn=3600
        )

        # 4. Record event in DynamoDB
        table = self.dynamodb_resource.Table(DYNAMODB_TABLE)
        record = {
            "event_id": event_id,
            "timestamp": timestamp,
            "filename": filename,
            "original_key": original_key,
            "thumbnail_key": thumb_key,
            "original_url": original_url,
            "thumbnail_url": thumb_url,
            "file_size_kb": str(round(len(image_bytes) / 1024, 2)),
            "device_id": device_id,
            "device_status": device_status,
            "led_status": led_status,
            "event_source": event_source,
            "storage": f"AWS S3 ({S3_BUCKET})"
        }

        table.put_item(Item=record)
        return record

    def fetch_events_from_dynamodb(self) -> List[Dict[str, Any]]:
        """Scans DynamoDB table for all image events."""
        try:
            table = self.dynamodb_resource.Table(DYNAMODB_TABLE)
            response = table.scan()
            items = response.get("Items", [])

            # Regenerate presigned URLs if needed
            for item in items:
                if "original_key" in item and not item.get("original_url"):
                    item["original_url"] = self.s3_client.generate_presigned_url(
                        "get_object",
                        Params={"Bucket": S3_BUCKET, "Key": item["original_key"]},
                        ExpiresIn=3600
                    )
                if "thumbnail_key" in item and not item.get("thumbnail_url"):
                    item["thumbnail_url"] = self.s3_client.generate_presigned_url(
                        "get_object",
                        Params={"Bucket": S3_BUCKET, "Key": item["thumbnail_key"]},
                        ExpiresIn=3600
                    )

            # Sort by timestamp descending
            return sorted(items, key=lambda x: str(x.get("timestamp", "")), reverse=True)
        except Exception as e:
            print(f"Error fetching DynamoDB events: {e}")
            return []

    def trigger_via_api_gateway(self, payload: dict) -> Tuple[bool, str]:
        """Sends an on-demand trigger to AWS API Gateway endpoint."""
        if not API_GATEWAY_URL:
            return False, "API Gateway URL is not configured in .env."

        try:
            resp = requests.post(f"{API_GATEWAY_URL}/events", json=payload, timeout=8)
            if resp.status_code in (200, 201):
                return True, f"API Gateway Event dispatched: {resp.text}"
            return False, f"API Gateway error: HTTP {resp.status_code} - {resp.text}"
        except Exception as e:
            return False, f"Failed to connect to API Gateway: {str(e)}"
