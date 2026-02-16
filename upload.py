"""
Upload the list of files to the AWS S3 bucket.

This module checks for the existence and attributes of S3 objects corresponding
to rows in the CSV file. It does not perform uploads; it only queries object
metadata (head_object).
"""

# settings:
CSV_FILE_PATH = 'data/export.lite.csv'

TIMESTAMP_FORMAT = '%Y%m%d-%H%M%S'

# SKIPPED_PREFIX path prefix in publicId file (from cloudinary) not in AWS S3.
SKIPPED_PREFIX = 'editorial/'
# EXTENSION_JPEG: this one is a best guess, as cloudinary seems to have remove
# the actual 'fake' extension the image was uploaded with and replaced it with
# the actual format of the image: psd. We will assume the original extension
# was jpg, because it seems to be the most common one in the dataset.
IMAGE_EXTENSION = 'jpg' #
# BACKUP_EXTENSION: all the files are PSD file originally. Prior to
# replacing the original by a real jpg version, we are doing a backup as PSD.
BACKUP_EXTENSION = 'psd'

# Added imports and implementation
import os
import csv
from pathlib import Path
from typing import Optional
from datetime import datetime

import logging
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import sys
from tqdm import tqdm


def _build_s3_key(public_id: str) -> str:
    """Return the S3 object key (relative path) for a given publicId."""
    if public_id.startswith(SKIPPED_PREFIX):
        rel = public_id[len(SKIPPED_PREFIX):]
    else:
        rel = public_id
    # ensure no leading slash
    rel = rel.lstrip('/')
    return f"{rel}.{IMAGE_EXTENSION}"


def _head_s3_object(s3_client, bucket: str, key: str) -> Optional[dict]:
    """Return head_object response dict or None if object does not exist."""
    try:
        return s3_client.head_object(Bucket=bucket, Key=key)
    except ClientError as exc:
        err_code = exc.response.get('Error', {}).get('Code', '')
        # Common "not found" codes: '404', 'NoSuchKey', 'NotFound'
        if err_code in ('404', 'NoSuchKey', 'NotFound', 'NoSuchBucket'):
            return None
        # Re-raise unexpected errors
        raise


def _human_readable_size(num: Optional[int]) -> str:
    """Format bytes as human readable string (e.g. 1.2 MB)."""
    if num is None or num == '-' or not isinstance(num, (int, float)):
        return str(num)
    num = float(num)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0 or unit == 'TB':
            if unit == 'B':
                return f"{int(num)} {unit}"
            return f"{num:.2f} {unit}"
        num /= 1024.0
    return f"{num:.2f} PB"


def _choose_timestamp() -> str:
    """
    Return the current timestamp string using TIMESTAMP_FORMAT.

    The upload log will always be placed under data/logs/<timestamp>/upload.log.
    """
    return datetime.now().strftime(TIMESTAMP_FORMAT)


def main():
    """Iterate CSV rows, build S3 keys and log object attributes or not-found message."""
    load_dotenv()

    bucket = os.getenv('AWS_S3_BUCKET_NAME')
    if not bucket:
        raise RuntimeError("AWS_S3_BUCKET_NAME not set in environment (.env)")

    # Determine timestamp for logs and create log folder
    timestamp = _choose_timestamp()
    log_dir = Path('data') / 'logs' / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / 'upload.log'

    # Configure logger: file handler gets all messages, console only shows START/END
    logger = logging.getLogger('cgm.upload')
    logger.setLevel(logging.INFO)
    logger.propagate = False

    fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # clear existing handlers
    for h in list(logger.handlers):
        logger.removeHandler(h)

    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)

    class _StartEndFilter(logging.Filter):
        """Allow only START/END messages to go to the console."""
        def filter(self, record):
            try:
                msg = record.getMessage()
            except Exception:
                msg = str(record.msg)
            return msg.startswith('START') or msg.startswith('END')

    stream_handler.addFilter(_StartEndFilter())
    logger.addHandler(stream_handler)

    s3 = boto3.client('s3')

    # Read CSV into memory to compute total files
    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = list(csv.DictReader(csvfile))
    total_files = sum(1 for row in reader if (row.get('publicId') or '').strip())

    logger.info(f"START upload of {total_files} files...")

    # Iterate CSV rows and log results (detailed messages go to file only).
    # Show a console progress bar (stdout) that counts processed files vs total_files.
    with tqdm(total=total_files, unit='file', desc='Uploaded', file=sys.stdout) as progress:
        for row in reader:
            public_id = (row.get('publicId') or '').strip()
            if not public_id:
                continue

            key = _build_s3_key(public_id)
            s3_uri = f"s3://{bucket}/{key}"

            try:
                meta = _head_s3_object(s3, bucket, key)
            except Exception as exc:
                logger.error(f"Error querying {s3_uri} : {exc}")
                progress.update(1)
                continue

            if meta is None:
                logger.info(f"Do NOT exist: {s3_uri} !")
                progress.update(1)
                continue

            # Extract attributes with sensible fallbacks
            size = meta.get('ContentLength', '-')
            size_str = _human_readable_size(size)
            last_modified = meta.get('LastModified')
            last_modified_str = last_modified.isoformat() if hasattr(last_modified, 'isoformat') else str(last_modified)
            etag = meta.get('ETag', '-')

            # Print in the requested format (without content type and checksum):
            # Exist: {object_key} ; size={size} ; {last modified date} ; etag={etag}
            logger.info(f"Exist: {s3_uri} ; size={size_str} ; {last_modified_str} ; etag={etag}")
            progress.update(1)

    logger.info(f"END upload of {total_files} files!")


if __name__ == '__main__':
    main()
