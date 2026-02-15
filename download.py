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

    # Create timestamped run directory under data/runs
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    run_dir = Path('data') / 'runs' / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    # Open CSV and iterate rows
    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            public_id = (row.get('publicId') or '').strip()
            if not public_id:
                # skip rows without publicId
                continue

            # Build download URL
            download_url = f"{cloudinary_base}/{DEFAULT_TRANSFORMATION_PREFIX}/{public_id}.{IMAGE_EXTENSION}"

            print(f"Downloading {public_id}...")

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
                print(f"Downloaded {public_id} successfully!")
            except Exception as exc:
                # Brief error reporting, continue with next file
                print(f"Failed to download {public_id}: {exc}")

if __name__ == '__main__':
    download_images()
