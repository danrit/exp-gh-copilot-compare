"""
Iterate over a CSV export and check whether corresponding objects exist in an AWS S3 bucket.

This script builds S3 object keys from the CSV `publicId` field and retrieves
object attributes using S3 HEAD requests (no download).
"""

from __future__ import annotations

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# settings:
CSV_FILE_PATH = "data/export.lite.csv"
TIMESTAMP_FORMAT = "%Y%m%d-%H%M%S"

# SKIPPED_PREFIX path prefix in publicId file (from cloudinary) not in AWS S3.
SKIPPED_PREFIX = "editorial/"

# EXTENSION_JPEG: best guess based on dataset.
IMAGE_EXTENSION = "jpg"

# BACKUP_EXTENSION: currently unused by PROMPT.md step; kept for later steps.
BACKUP_EXTENSION = "psd"
# end settings


def _require_env(name: str) -> str:
    """Return an environment variable value or raise a helpful error."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _object_relative_path_from_public_id(public_id: str) -> str:
    """Derive OBJECT_RELATIVE_PATH by removing SKIPPED_PREFIX from the publicId (if present)."""
    public_id = public_id.strip()
    if SKIPPED_PREFIX and public_id.startswith(SKIPPED_PREFIX):
        return public_id[len(SKIPPED_PREFIX) :]
    return public_id


def _format_last_modified(value: Any) -> str:
    """Format S3 LastModified value (datetime) to an ISO string."""
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.isoformat()
        return value.astimezone().isoformat()
    return str(value)


def _get_checksum(head: dict[str, Any]) -> str:
    """Extract a checksum from S3 head response, if present."""
    return (
        head.get("ChecksumSHA256")
        or head.get("ChecksumSHA1")
        or head.get("ChecksumCRC32C")
        or head.get("ChecksumCRC32")
        or ""
    )


def main() -> int:
    """Run the S3 existence/metadata check."""
    load_dotenv()

    bucket_name = _require_env("AWS_S3_BUCKET_NAME").strip()
    s3 = boto3.client("s3")

    csv_path = Path(CSV_FILE_PATH)
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "publicId" not in reader.fieldnames:
            raise RuntimeError("CSV must contain a 'publicId' column")

        for row in reader:
            public_id = (row.get("publicId") or "").strip()
            if not public_id:
                continue

            object_relative_path = _object_relative_path_from_public_id(public_id)
            object_key = f"{object_relative_path}.{IMAGE_EXTENSION}"
            object_uri = f"s3://{bucket_name}/{object_key}"

            try:
                head = s3.head_object(Bucket=bucket_name, Key=object_key)
            except ClientError as e:
                code = (e.response.get("Error") or {}).get("Code")
                status = (e.response.get("ResponseMetadata") or {}).get("HTTPStatusCode")
                if code in {"404", "NoSuchKey", "NotFound"} or status == 404:
                    print(f"Do NOT exist: {object_uri} !")
                    continue
                raise

            size = head.get("ContentLength")
            last_modified = _format_last_modified(head.get("LastModified"))
            etag = head.get("ETag")
            content_type = head.get("ContentType")
            checksum = _get_checksum(head)

            print(
                f"Exist: {object_uri} ; size={size} ; {last_modified} ; etag={etag} ; {content_type} ; {checksum}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
