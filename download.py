"""
Download the list of jpeg transformed images from Cloudinary and save them locally.
"""

import csv
import logging
import os
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from tqdm import tqdm

# settings:
DEFAULT_TRANSFORMATION_PREFIX = 'image/upload/t_hires2/v1'
# EXTENSION_JPEG: this one is a best guess, as cloudinary seems to have remove
# the actual 'fake' extension the image was uploaded with and replaced it with
# the actual format of the image: psd. We will assume the original extension
# was jpg, because it seems to be the most common one in the dataset.
IMAGE_EXTENSION = 'jpg' #
# CSV_FILE_PATH = 'data/export-2026-02-05T01_28_30.025Z.csv'
CSV_FILE_PATH = 'data/export.lite.csv'

TIMESTAMP_FORMAT = '%Y%m%d-%H%M%S'


def main():
    """Read the CSV file, download each image from Cloudinary, and save it locally."""
    load_dotenv()
    cloudinary_base_url = os.environ['CLOUDINARY_BASE_URL']

    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    output_dir = Path('data/runs') / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    log_dir = Path('data/logs') / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'download.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=str(log_file),
    )

    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        rows = list(csv.DictReader(csvfile))

    total_files = len(rows)
    logging.info("START download of %d files...", total_files)

    for row in tqdm(rows, desc="Downloading", unit="file"):
        public_id = row['publicId']
        url = f"{cloudinary_base_url}/{DEFAULT_TRANSFORMATION_PREFIX}/{public_id}.{IMAGE_EXTENSION}"
        dest_path = output_dir / f"{public_id}.{IMAGE_EXTENSION}"

        logging.info("Downloading %s...", public_id)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(url, timeout=60)
        response.raise_for_status()

        dest_path.write_bytes(response.content)
        logging.info("Downloaded %s successfully!", public_id)

    logging.info("END download of %d files!", total_files)


if __name__ == '__main__':
    main()
