"""
Download images listed in a CSV export from Cloudinary and save them locally.

The CSV row field `publicId` is used both to build the download URL and to
create the relative output path for each downloaded image.
"""

from __future__ import annotations

# settings:
DEFAULT_TRANSFORMATION_PREFIX = "image/upload/t_hires2/v1"
# EXTENSION_JPEG: this one is a best guess, as cloudinary seems to have remove
# the actual 'fake' extension the image was uploaded with and replaced it with
# the actual format of the image: psd. We will assume the original extension
# was jpg, because it seems to be the most common one in the dataset.
IMAGE_EXTENSION = "jpg"
# CSV_FILE_PATH = 'data/export-2026-02-05T01_28_30.025Z.csv'
CSV_FILE_PATH = "data/export.lite.csv"
TIMESTAMP_FORMAT = "%Y%m%d-%H%M%S"

# SKIPPED_PREFIX path prefix in publicId file (from cloudinary) not needed locally.
SKIPPED_PREFIX = "editorial/"

import csv
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from tqdm import tqdm


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


class _StartEndOnlyFilter(logging.Filter):
    """Allow only START/END messages through (intended for console handler)."""

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return msg.startswith("START ") or msg.startswith("END ")


def _configure_logger(log_file_path: Path) -> logging.Logger:
    """Configure and return a logger that logs details to file and start/end to console."""
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("cgm-5625.download")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        formatter.converter = time.localtime  # keep log timestamps in local time

        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(_StartEndOnlyFilter())

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


def main() -> int:
    """Entry point: read CSV, download each image into a timestamped run folder."""
    load_dotenv()

    cloudinary_base_url = _require_env("CLOUDINARY_BASE_URL")

    timestamp = datetime.now().astimezone().strftime(TIMESTAMP_FORMAT)  # local time

    run_dir = Path("data") / "runs" / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    log_file_path = Path("data") / "logs" / timestamp / "download.log"
    logger = _configure_logger(log_file_path)

    csv_path = Path(CSV_FILE_PATH)
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "publicId" not in reader.fieldnames:
            raise RuntimeError("CSV must contain a 'publicId' column")

        public_ids: list[str] = []
        for row in reader:
            public_id = (row.get("publicId") or "").strip()
            if public_id:
                public_ids.append(public_id)

    total_files = len(public_ids)
    logger.info(f"START download of {total_files} files...")

    for public_id in tqdm(public_ids, total=total_files, unit="file", desc="Downloading", dynamic_ncols=True):
        logger.info(f"Downloading {public_id}...")
        url = _build_download_url(cloudinary_base_url, public_id)

        relative_public_id = public_id
        if SKIPPED_PREFIX and relative_public_id.startswith(SKIPPED_PREFIX):
            relative_public_id = relative_public_id[len(SKIPPED_PREFIX) :]

        output_path = run_dir / f"{relative_public_id}.{IMAGE_EXTENSION}"
        try:
            _download_to_path(url, output_path)
        except (HTTPError, URLError, TimeoutError) as e:
            raise RuntimeError(f"Failed to download {public_id} from {url}: {e}") from e

        logger.info(f"Downloaded {public_id} successfully!")

    logger.info(f"END download of {total_files} files!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
