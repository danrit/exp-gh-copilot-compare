"""
Download the list of jpeg transformed images from cloudinary and save them locally
"""

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

# Added imports and implementation
import os
import csv
from pathlib import Path
from datetime import datetime
import logging

# External libs
import requests
from dotenv import load_dotenv

def download_images():
    """Read CSV file, build Cloudinary URLs from publicId and download images into a timestamped run folder."""
    # Load environment variables from local .env (if present)
    load_dotenv()

    cloudinary_base = os.getenv('CLOUDINARY_BASE_URL')
    if not cloudinary_base:
        raise RuntimeError("CLOUDINARY_BASE_URL not set in environment (.env)")

    # Create timestamped run directory under data/runs and data/logs
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    run_dir = Path('data') / 'runs' / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    log_dir = Path('data') / 'logs' / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / 'download.log'

    # Configure logging:
    # - file_handler: logs all INFO+ messages to the file (detailed download messages go here)
    # - stream_handler: only allows START/END messages to be printed to console via a filter
    logger = logging.getLogger('cgm.download')
    logger.setLevel(logging.INFO)
    logger.propagate = False
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # remove any existing handlers on this logger to avoid duplicates
    for h in list(logger.handlers):
        logger.removeHandler(h)

    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

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

    # Read CSV into memory to compute total files
    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = list(csv.DictReader(csvfile))
    total_files = sum(1 for row in reader if (row.get('publicId') or '').strip())

    logger.info(f"START download of {total_files} files...")

    # Iterate and download
    for row in reader:
        public_id = (row.get('publicId') or '').strip()
        if not public_id:
            # skip rows without publicId
            continue

        # Build download URL
        download_url = f"{cloudinary_base}/{DEFAULT_TRANSFORMATION_PREFIX}/{public_id}.{IMAGE_EXTENSION}"

        logger.info(f"Downloading {public_id}...")

        # Build local file path preserving publicId directory structure
        local_path = run_dir / f"{public_id}.{IMAGE_EXTENSION}"
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with requests.get(download_url, stream=True, timeout=30) as resp:
                resp.raise_for_status()
                # Write content in chunks
                with open(local_path, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            logger.info(f"Downloaded {public_id} successfully!")
        except Exception as exc:
            # Brief error reporting, continue with next file
            logger.error(f"Failed to download {public_id}: {exc}")

    logger.info(f"END download of {total_files} files!")

if __name__ == '__main__':
    download_images()
