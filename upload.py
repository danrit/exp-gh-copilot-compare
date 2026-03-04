"""
Upload the list of files to the AWS S3 bucket.
"""

import csv
import logging
import os
from datetime import datetime
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
            content_type = response.get('ContentType', '')
            checksum = response.get('ChecksumSHA256', response.get('ChecksumSHA1', ''))

            logging.info(
                "Exist: s3://%s/%s ; size=%s ; %s ; etag=%s ; %s ; %s",
                bucket_name, object_key, size, last_modified, etag, content_type, checksum,
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
