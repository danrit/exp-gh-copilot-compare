"""
Upload the list of files to the AWS S3 bucket.

Reads image public IDs from a CSV file, maps them to S3 object keys, and checks
whether each object already exists in the bucket by retrieving its attributes.
"""

import csv
import logging
import os
from datetime import datetime
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

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

    for row in rows:
        public_id = row['publicId']
        object_key = build_s3_object_key(public_id)
        s3_uri = f"s3://{AWS_S3_BUCKET_NAME}/{object_key}"

        try:
            response = s3.get_object_attributes(
                Bucket=AWS_S3_BUCKET_NAME,
                Key=object_key,
                ObjectAttributes=['ETag', 'Checksum', 'ObjectSize'],
            )
            # Retrieve head separately for ContentType and LastModified
            head = s3.head_object(Bucket=AWS_S3_BUCKET_NAME, Key=object_key)

            size = response.get('ObjectSize', 'N/A')
            last_modified = response.get('LastModified', head.get('LastModified', 'N/A'))
            etag = response.get('ETag', 'N/A')
            content_type = head.get('ContentType', 'N/A')
            checksum = response.get('Checksum', 'N/A')

            logging.info(
                f"Exist: {s3_uri} ; size={size} ; {last_modified} ; "
                f"etag={etag} ; {content_type} ; {checksum}"
            )
        except ClientError as e:
            if e.response['Error']['Code'] in ('NoSuchKey', '404'):
                logging.error(f"Do NOT exist: {s3_uri} !")
            else:
                raise

    notice(f"END checking {total_files} objects in S3 bucket '{AWS_S3_BUCKET_NAME}'!")


if __name__ == '__main__':
    check_objects(CSV_FILE_PATH)
