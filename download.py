"""
Download images listed in a CSV export from Cloudinary and save them locally.

The CSV row field `publicId` is used both to build the download URL and to
create the relative output path for each downloaded image.
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

from __future__ import annotations

import csv
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv


def _require_env(name: str) -> str:
    """Return an environment variable value or raise a helpful error."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value.rstrip("/")


def _build_download_url(cloudinary_base_url: str, public_id: str) -> str:
    """Build the download URL for a given Cloudinary publicId."""
    return f"{cloudinary_base_url}/{DEFAULT_TRANSFORMATION_PREFIX}/{public_id}.{IMAGE_EXTENSION}"


def _download_to_path(url: str, output_path: Path) -> None:
    """Download a URL to the given path, creating its parent directories."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    req = Request(url, headers={"User-Agent": "cgm-5625-downloader/1.0"})
    with urlopen(req, timeout=60) as resp, output_path.open("wb") as f:
        f.write(resp.read())


def main() -> int:
    """Entry point: read CSV, download each image into a timestamped run folder."""
    load_dotenv()

    cloudinary_base_url = _require_env("CLOUDINARY_BASE_URL")

    timestamp = datetime.now(timezone.utc).strftime(TIMESTAMP_FORMAT)
    run_dir = Path("data") / "runs" / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    csv_path = Path(CSV_FILE_PATH)
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "publicId" not in reader.fieldnames:
            raise RuntimeError("CSV must contain a 'publicId' column")

        for row in reader:
            public_id = (row.get("publicId") or "").strip()
            if not public_id:
                continue

            print(f"Downloading {public_id}...")
            url = _build_download_url(cloudinary_base_url, public_id)

            output_path = run_dir / f"{public_id}.{IMAGE_EXTENSION}"
            try:
                _download_to_path(url, output_path)
            except (HTTPError, URLError, TimeoutError) as e:
                raise RuntimeError(f"Failed to download {public_id} from {url}: {e}") from e

            print(f"Downloaded {public_id} successfully!")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
