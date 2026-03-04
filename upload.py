"""
Upload the list of files to the AWS S3 bucket.
"""

import csv
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from tqdm import tqdm

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

OBJECT_MODIFIED_DATE_LIMIT = '2026-01-01'

DOWNLOADED_FILES_PATH = 'data/runs/20260305-061749'


def format_size(size_bytes):
    """Format a byte count into a human-readable string (e.g., KB, MB, GB)."""
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if abs(size_bytes) < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def main():
    """Iterate over the CSV, build S3 keys, and check if each object exists."""
    load_dotenv()
    bucket_name = os.environ['AWS_S3_BUCKET_NAME']

    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    log_dir = Path('data/logs') / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'upload.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=str(log_file),
    )

    s3_client = boto3.client('s3')

    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        rows = list(csv.DictReader(csvfile))

    total_files = len(rows)
    logging.info("START upload check of %d files...", total_files)

    for row in tqdm(rows, desc="Checking S3 objects", unit="file"):
        public_id = row['publicId']

        # Remove the cloudinary-specific prefix to get the S3 relative path
        if public_id.startswith(SKIPPED_PREFIX):
            object_relative_path = public_id[len(SKIPPED_PREFIX):]
        else:
            object_relative_path = public_id

        object_key = f"{object_relative_path}.{IMAGE_EXTENSION}"

        try:
            response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
            size = response['ContentLength']
            last_modified = response['LastModified']
            etag = response['ETag']

            logging.info(
                "Exist: s3://%s/%s ; size=%s ; %s ; etag=%s",
                bucket_name, object_key, format_size(size), last_modified, etag,
            )

            date_limit = datetime.strptime(OBJECT_MODIFIED_DATE_LIMIT, '%Y-%m-%d').replace(tzinfo=timezone.utc)

            if last_modified < date_limit:
                logging.info(
                    "Object %s was modified before %s, it will be copied to a new object key with the backup extension.",
                    object_key, OBJECT_MODIFIED_DATE_LIMIT,
                )

                backup_object_key = f"{object_relative_path}.{BACKUP_EXTENSION}"
                try:
                    s3_client.copy_object(
                        Bucket=bucket_name,
                        CopySource={'Bucket': bucket_name, 'Key': object_key},
                        Key=backup_object_key,
                    )
                    logging.info(
                        "Object %s was successfully copied to %s!",
                        object_key, backup_object_key,
                    )
                except ClientError as copy_error:
                    logging.error(
                        "Failed to copy %s to %s: %s",
                        object_key, backup_object_key, copy_error,
                    )

                # Upload the downloaded file to replace the original object
                local_file_path = Path(DOWNLOADED_FILES_PATH) / f"{object_relative_path}.{IMAGE_EXTENSION}"
                if not local_file_path.exists():
                    logging.error(
                        "Local file %s does not exist, cannot upload to %s!",
                        local_file_path, object_key,
                    )
                else:
                    try:
                        s3_client.upload_file(
                            str(local_file_path),
                            bucket_name,
                            object_key,
                            ExtraArgs={'ContentType': 'image/jpeg'},
                        )
                        logging.info(
                            "Object %s was successfully uploaded from %s!",
                            object_key, local_file_path,
                        )
                    except ClientError as upload_error:
                        logging.error(
                            "Failed to upload %s to %s: %s",
                            local_file_path, object_key, upload_error,
                        )

            else:
                logging.info(
                    "Object %s was modified after %s, it will NOT be copied.",
                    object_key, OBJECT_MODIFIED_DATE_LIMIT,
                )

        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                logging.error(
                    "Do NOT exist: s3://%s/%s !",
                    bucket_name, object_key,
                )
            else:
                logging.error(
                    "Error checking s3://%s/%s: %s",
                    bucket_name, object_key, e,
                )

    logging.info("END upload check of %d files!", total_files)


if __name__ == '__main__':
    main()
