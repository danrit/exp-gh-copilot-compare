"""
Upload the list of files to the AWS S3 bucket.

Reads image public IDs from a CSV file, maps them to S3 object keys, and checks
whether each object already exists in the bucket by retrieving its attributes.
"""

import csv
import logging
import os
from datetime import date, datetime
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

# Settings
CSV_FILE_PATH = 'data/export.lite.csv'
TIMESTAMP_FORMAT = '%Y%m%d-%H%M%S'
LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# SKIPPED_PREFIX: path prefix in publicId (from Cloudinary) not present in AWS S3 key.
SKIPPED_PREFIX = 'editorial/'
# IMAGE_EXTENSION: assumed jpg as Cloudinary replaces the original extension with
# the actual image format (psd), but the original upload was likely jpg.
IMAGE_EXTENSION = 'jpg'
# BACKUP_EXTENSION: all files are PSD originally; backup is kept as PSD before
# replacing with the real jpg version.
BACKUP_EXTENSION = 'psd'

AWS_S3_BUCKET_NAME = os.environ['AWS_S3_BUCKET_NAME']

# DOWNLOADED_FILES_PATH: path to the local directory containing the downloaded files.
DOWNLOADED_FILES_PATH = Path('data/runs/20260302-060031')

# OBJECT_MODIFIED_DATE_LIMIT: objects with LastModified earlier than this date will be
# copied to a backup key before being replaced with the jpg version.
OBJECT_MODIFIED_DATE_LIMIT = date.fromisoformat('2026-01-01')

# Custom log level between INFO (20) and WARNING (30) for high-level progress messages.
NOTICE_LEVEL = 25
logging.addLevelName(NOTICE_LEVEL, 'NOTICE')


def notice(message: str, *args, **kwargs) -> None:
    """Log a message at the custom NOTICE level."""
    logging.log(NOTICE_LEVEL, message, *args, **kwargs)


def configure_logging(timestamp: str) -> None:
    """Configure logging to write to both a timestamped log file and the console.

    The file handler captures all messages (INFO and above).
    The console handler only shows NOTICE and above, hiding per-row detail messages.
    """
    log_dir = Path('data/logs') / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    file_handler = logging.FileHandler(log_dir / 'upload.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(NOTICE_LEVEL)
    console_handler.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])


def build_s3_object_key(public_id: str) -> str:
    """Build the S3 object key from a Cloudinary publicId.

    Strips the SKIPPED_PREFIX from the publicId and appends the IMAGE_EXTENSION.
    """
    relative_path = public_id.removeprefix(SKIPPED_PREFIX)
    return f"{relative_path}.{IMAGE_EXTENSION}"


def build_s3_backup_key(public_id: str) -> str:
    """Build the S3 backup object key from a Cloudinary publicId.

    Strips the SKIPPED_PREFIX from the publicId and appends the BACKUP_EXTENSION.
    """
    relative_path = public_id.removeprefix(SKIPPED_PREFIX)
    return f"{relative_path}.{BACKUP_EXTENSION}"


def format_size(size_bytes: int) -> str:
    """Format a byte count into a human-readable string (e.g. KB, MB, GB)."""
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def check_objects(csv_file_path: str) -> None:
    """Iterate over the CSV file and check whether each image exists in S3.

    For each row, builds the S3 object key, retrieves the object attributes
    without downloading the file, and logs the result.
    """
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    configure_logging(timestamp)

    s3 = boto3.client('s3')

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        rows = list(csv.DictReader(csvfile))

    total_files = len(rows)
    notice(f"START checking {total_files} objects in S3 bucket '{AWS_S3_BUCKET_NAME}'...")

    # tqdm writes to stderr by default, keeping the progress bar out of the log file
    with tqdm(total=total_files, unit='file', desc='Checking') as progress_bar:
        for row in rows:
            public_id = row['publicId']
            object_key = build_s3_object_key(public_id)
            s3_uri = f"s3://{AWS_S3_BUCKET_NAME}/{object_key}"

            try:
                response = s3.get_object_attributes(
                    Bucket=AWS_S3_BUCKET_NAME,
                    Key=object_key,
                    ObjectAttributes=['ETag', 'ObjectSize'],
                )

                size = format_size(response.get('ObjectSize', 0))
                last_modified = response.get('LastModified', 'N/A')
                etag = response.get('ETag', 'N/A')

                logging.info(f"Exist: {s3_uri} ; size={size} ; {last_modified} ; etag={etag}")

                if last_modified != 'N/A' and last_modified.date() < OBJECT_MODIFIED_DATE_LIMIT:
                    logging.info(
                        f"Object {object_key} was modified before {OBJECT_MODIFIED_DATE_LIMIT}, "
                        f"it will be copied to a new object key with the backup extension."
                    )
                    backup_key = build_s3_backup_key(public_id)
                    backup_s3_uri = f"s3://{AWS_S3_BUCKET_NAME}/{backup_key}"
                    try:
                        s3.copy_object(
                            Bucket=AWS_S3_BUCKET_NAME,
                            CopySource={'Bucket': AWS_S3_BUCKET_NAME, 'Key': object_key},
                            Key=backup_key,
                        )
                        logging.info(f"Object {object_key} was successfully copied to {backup_s3_uri}!")
                    except ClientError as copy_error:
                        logging.error(f"Failed to copy {s3_uri} to {backup_s3_uri}: {copy_error}")

                    local_path = public_id.removeprefix(SKIPPED_PREFIX)
                    local_file_path = DOWNLOADED_FILES_PATH / f"{local_path}.{IMAGE_EXTENSION}"

                    if not local_file_path.exists():
                        logging.error(f"Local file {local_file_path} does not exist, cannot upload to {object_key}!")
                    else:
                        try:
                            s3.upload_file(
                                Filename=str(local_file_path),
                                Bucket=AWS_S3_BUCKET_NAME,
                                Key=object_key,
                            )
                            logging.info(f"Object {object_key} was successfully uploaded from {local_file_path}!")
                        except ClientError as upload_error:
                            logging.error(f"Failed to upload {local_file_path} to {s3_uri}: {upload_error}")

                else:
                    logging.info(
                        f"Object {object_key} was modified after {OBJECT_MODIFIED_DATE_LIMIT}, "
                        f"it will NOT be copied."
                    )

            except ClientError as e:
                if e.response['Error']['Code'] in ('NoSuchKey', '404'):
                    logging.error(f"Do NOT exist: {s3_uri} !")
                else:
                    raise
            finally:
                progress_bar.update(1)

    notice(f"END checking {total_files} objects in S3 bucket '{AWS_S3_BUCKET_NAME}'!")


if __name__ == '__main__':
    check_objects(CSV_FILE_PATH)
