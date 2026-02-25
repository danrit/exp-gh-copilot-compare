"""
Download the list of jpeg transformed images from cloudinary and save them locally.

Reads image public IDs from a CSV file, builds download URLs using the Cloudinary
base URL and transformation prefix, and saves the images into a timestamped subfolder
under data/runs/.
"""

import csv
import logging
import os
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

# Settings
DEFAULT_TRANSFORMATION_PREFIX = 'image/upload/t_hires2/v1'
IMAGE_EXTENSION = 'jpg'
# CSV_FILE_PATH = 'data/export-2026-02-05T01_28_30.025Z.csv'
CSV_FILE_PATH = 'data/export.lite.csv'
TIMESTAMP_FORMAT = '%Y%m%d-%H%M%S'
LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

CLOUDINARY_BASE_URL = os.environ['CLOUDINARY_BASE_URL']


def configure_logging(timestamp: str) -> None:
    """Configure logging to write to both a timestamped log file and the console."""
    log_dir = Path('data/logs') / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    file_handler = logging.FileHandler(log_dir / 'download.log', encoding='utf-8')
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])


def build_download_url(public_id: str) -> str:
    """Build the Cloudinary download URL for a given publicId."""
    return f"{CLOUDINARY_BASE_URL}/{DEFAULT_TRANSFORMATION_PREFIX}/{public_id}.{IMAGE_EXTENSION}"


def download_images(csv_file_path: str) -> None:
    """
    Read image public IDs from the CSV file and download each image into a
    timestamped subfolder under data/runs/.
    """
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    configure_logging(timestamp)

    run_dir = Path('data/runs') / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        rows = list(csv.DictReader(csvfile))

    total_files = len(rows)
    logging.info(f"START download of {total_files} files...")

    for row in rows:
        public_id = row['publicId']
        url = build_download_url(public_id)
        dest_path = run_dir / f"{public_id}.{IMAGE_EXTENSION}"

        logging.info(f"Downloading {public_id}...")

        # Preserve subdirectory structure from the publicId path
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        dest_path.write_bytes(response.content)
        logging.info(f"Downloaded {public_id} successfully!")

    logging.info(f"END download of {total_files} files!")


if __name__ == '__main__':
    download_images(CSV_FILE_PATH)
