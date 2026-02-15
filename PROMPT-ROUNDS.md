# Prompt rounds

## Preparations

- data:
  - create 2 datasets files:
    - the full one `data/export-2026-02-05T01_28_30.025Z.csv`
    - a lite one: `data/export.lite.csv` (for test)
- init `download.py`:
  - a short file description
  - define required parameters
- init `upload.py`:
  - a short file description

## Round 1

### Context

- file `.github/copilot-instructions.md`
- file `data/export.lite.csv`
- file `download.py`
- file `pyproject.toml`

### Prompt

Edit `download.py` to download the images in the CSV file whose name is in
 `CSV_FILE_PATH`. Here are detailed implementation instructions:
- in the CSV file the column to use for the file relative path and name is `publicId`
- to build the download URL, use the following pattern: `{CLOUDINARY_BASE_URL}/{DEFAULT_TRANSFORMATION_PREFIX}/{publicId}.{IMAGE_EXTENSION}`
  - `CLOUDINARY_BASE_URL`, `DEFAULT_TRANSFORMATION_PREFIX` and `IMAGE_EXTENSION` are defined in `download.py`
- create a timestamp string using the format defined in `TIMESTAMP_FORMAT` and create a subfolder in `data/runs` with this timestamp string as name, to store the downloaded files
- save the downloaded file in
- log the download progress in the console with the following format: `Downloading {publicId}...` and log a success message when the download is successful: `Downloaded {publicId} successfully!`

In a secret local file `.env` the following variables are defined:
- `CLOUDINARY_BASE_URL`: contains the base URL of the Cloudinary account where the images are hosted

Usage of the updated `download.py` should be as follows: `python download.py` (+ any required parameters if needed)

### Response

Solution (step-by-step)

1. Load environment variables from the local .env file to read CLOUDINARY_BASE_URL.
2. Create a timestamped run directory under data/runs using TIMESTAMP_FORMAT.
3. Parse the CSV file at CSV_FILE_PATH using csv.DictReader and read the publicId column.
4. For each publicId, build the download URL using the given pattern and stream-download the file.
5. Preserve the publicId path structure under the run directory (create parent dirs as needed), save the file with IMAGE_EXTENSION, and log progress messages.

Changes grouped by file:

- `download.py`: Add CSV parsing, .env loading, run-directory creation and downloading logic. Uses requests and python-dotenv (dependencies added in pyproject.toml).
- `pyproject.toml`: Add required dependencies: requests and python-dotenv.
