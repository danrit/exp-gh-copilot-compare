"""
Iterate over a CSV export and check whether corresponding objects exist in an AWS S3 bucket.

This script builds S3 object keys from the CSV `publicId` field and retrieves
object attributes using S3 HEAD requests (no download).
"""

from __future__ import annotations

import csv
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from tqdm import tqdm

# settings:
CSV_FILE_PATH = "data/export.lite.csv"
TIMESTAMP_FORMAT = "%Y%m%d-%H%M%S"

# SKIPPED_PREFIX path prefix in publicId file (from cloudinary) not in AWS S3.
SKIPPED_PREFIX = "editorial/"

# EXTENSION_JPEG: best guess based on dataset.
IMAGE_EXTENSION = "jpg"

# DOWNLOADED_FILES_PATH: local run folder created by download.py containing files to upload.
DOWNLOADED_FILES_PATH = "data/runs/20260223-054344"

# BACKUP_EXTENSION: all the files are PSD file originally. Prior to
# replacing the original by a real jpg version, we are doing a backup as PSD.
BACKUP_EXTENSION = "psd"

# OBJECT_MODIFIED_DATE_LIMIT: objects modified before this date will be copied.
OBJECT_MODIFIED_DATE_LIMIT = "2026-01-01"
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


def _format_size(num_bytes: int | None) -> str:
    """Format bytes as a human-readable size (B, KB, MB, GB, TB)."""
    if num_bytes is None:
        return "unknown"
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{num_bytes} B"


class _StartEndOnlyFilter(logging.Filter):
    """Allow only START/END messages through (intended for console handler)."""

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return msg.startswith("START ") or msg.startswith("END ")


def _configure_logger(log_file_path: Path) -> logging.Logger:
    """Configure and return a logger that logs details to file and start/end to console."""
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("cgm-5625.upload")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        formatter.converter = time.localtime  # keep log timestamps in local time

        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(_StartEndOnlyFilter())

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


def _parse_object_modified_date_limit(value: str) -> datetime:
    """Parse YYYY-MM-DD into a timezone-aware local datetime (start-of-day)."""
    local_tz = datetime.now().astimezone().tzinfo
    return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=local_tz)


def main() -> int:
    """Run the S3 existence/metadata check."""
    load_dotenv()

    bucket_name = _require_env("AWS_S3_BUCKET_NAME").strip()
    s3 = boto3.client("s3")

    modified_date_limit = _parse_object_modified_date_limit(OBJECT_MODIFIED_DATE_LIMIT)

    timestamp = datetime.now().astimezone().strftime(TIMESTAMP_FORMAT)
    log_file_path = Path("data") / "logs" / timestamp / "upload.log"
    logger = _configure_logger(log_file_path)

    csv_path = Path(CSV_FILE_PATH)
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "publicId" not in reader.fieldnames:
            raise RuntimeError("CSV must contain a 'publicId' column")

        public_ids: list[str] = []
        for row in reader:
            public_id = (row.get("publicId") or "").strip()
            if public_id:
                public_ids.append(public_id)

    total_files = len(public_ids)
    logger.info(f"START upload of {total_files} files...")

    for public_id in tqdm(public_ids, total=total_files, unit="file", desc="Uploading", dynamic_ncols=True):
        object_relative_path = _object_relative_path_from_public_id(public_id)
        object_key = f"{object_relative_path}.{IMAGE_EXTENSION}"
        object_uri = f"s3://{bucket_name}/{object_key}"

        try:
            head = s3.head_object(Bucket=bucket_name, Key=object_key)
        except ClientError as e:
            code = (e.response.get("Error") or {}).get("Code")
            status = (e.response.get("ResponseMetadata") or {}).get("HTTPStatusCode")
            if code in {"404", "NoSuchKey", "NotFound"} or status == 404:
                logger.info(f"Do NOT exist: {object_uri} !")
                continue
            raise

        size_human = _format_size(head.get("ContentLength"))
        last_modified_raw = head.get("LastModified")
        last_modified = last_modified_raw if isinstance(last_modified_raw, datetime) else None
        etag = head.get("ETag")

        logger.info(
            f"Exist: {object_uri} ; size={size_human} ; {_format_last_modified(last_modified_raw)} ; etag={etag}"
        )

        if isinstance(last_modified, datetime) and last_modified < modified_date_limit:
            logger.info(
                f"Object {object_key} was modified before {OBJECT_MODIFIED_DATE_LIMIT}, "
                f"it will be copied to a new object key with the backup extension."
            )

            backup_object_key = f"{object_relative_path}.{BACKUP_EXTENSION}"
            try:
                s3.copy_object(
                    Bucket=bucket_name,
                    Key=backup_object_key,
                    CopySource={"Bucket": bucket_name, "Key": object_key},
                )
            except ClientError as e:
                logger.error(f"Failed to copy object {object_key} to {backup_object_key}: {e}")
            else:
                logger.info(f"Object {object_key} was successfully copied to {backup_object_key}!")

            local_relative_path = _object_relative_path_from_public_id(public_id)
            local_file_path = Path(DOWNLOADED_FILES_PATH) / f"{local_relative_path}.{IMAGE_EXTENSION}"
            if not local_file_path.is_file():
                logger.info(f"Local file {local_file_path} does not exist, cannot upload to {object_key}!")
                continue

            try:
                s3.upload_file(
                    str(local_file_path),
                    bucket_name,
                    object_key,
                    ExtraArgs={"ContentType": "image/jpeg"},
                )
            except ClientError as e:
                logger.error(f"Failed to upload {local_file_path} to {object_key}: {e}")
            except OSError as e:
                logger.error(f"Failed to read local file {local_file_path} for upload to {object_key}: {e}")
            else:
                logger.info(f"Object {object_key} was successfully uploaded from {local_file_path}!")
        else:
            logger.info(
                f"Object {object_key} was modified after {OBJECT_MODIFIED_DATE_LIMIT}, it will NOT be copied."
            )

    logger.info(f"END upload of {total_files} files!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
