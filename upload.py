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

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv


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


def main():
    """Iterate CSV rows, build S3 keys and print object attributes or not-found message."""
    load_dotenv()

    bucket = os.getenv('AWS_S3_BUCKET_NAME')
    if not bucket:
        raise RuntimeError("AWS_S3_BUCKET_NAME not set in environment (.env)")

    s3 = boto3.client('s3')

    # Read CSV and iterate
    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            public_id = (row.get('publicId') or '').strip()
            if not public_id:
                continue

            key = _build_s3_key(public_id)
            s3_uri = f"s3://{bucket}/{key}"

            try:
                meta = _head_s3_object(s3, bucket, key)
            except Exception as exc:
                # Unexpected AWS error: print and continue
                print(f"Error querying {s3_uri} : {exc}")
                continue

            if meta is None:
                # object does not exist
                print(f"Do NOT exist: {s3_uri} !")
                continue

            # Extract attributes with sensible fallbacks
            size = meta.get('ContentLength', '-')
            last_modified = meta.get('LastModified')
            last_modified_str = last_modified.isoformat() if hasattr(last_modified, 'isoformat') else str(last_modified)
            etag = meta.get('ETag', '-')
            content_type = meta.get('ContentType', '-')
            # try common checksum fields, fall back to ETag
            checksum = meta.get('ChecksumCRC32') or meta.get('ChecksumSHA256') or meta.get('ChecksumSHA1') or etag or '-'

            # Print in the requested format:
            # Exist: {object_key} ; size={size} ; {last modified date} ; etag={etag} ; {content type} ; {checksum}
            print(f"Exist: {s3_uri} ; size={size} ; {last_modified_str} ; etag={etag} ; {content_type} ; {checksum}")


if __name__ == '__main__':
    main()
