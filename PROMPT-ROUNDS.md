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

Plan

1. download.py: Add logic to:
    - Load CLOUDINARY_BASE_URL from .env using python-dotenv
    - Read the CSV file and iterate over rows
    - Build download URL from the pattern
    - Create a timestamped subfolder under data/runs/
    - Download each image using requests, preserving the publicId path structure
    - Log progress messages
2. pyproject.toml: Add requests and python-dotenv as dependencies (create if not present).

- `download.py`: Add CSV reading, URL building, timestamped folder creation, and image downloading with console logging.
- `pyproject.toml`: Create (or update) with requests and python-dotenv dependencies.

## Round 2

### Context

- file `.github/copilot-instructions.md`
- file `data/export.lite.csv`
- file `download.py`
- file `pyproject.toml`

### Prompt

Update `download.py` to move logging messages to a logger instead of using print statements. Here are detailed implementation instructions:
- name the log file `download.log` and create a subfolder in `data/logs`, with the same timestamp string as the one used for the downloaded files, to store it.
- import the `logging` module and configure it:
    - set the logging level to `INFO`
    - set the log format to include the timestamp (format '%Y-%m-%d %H:%M:%S'), log level and message
    - set the log file path to the one defined above
- replace the print statements for logging the download progress and success messages with appropriate logging calls (e.g., `logging.info()`)
- add one "start" logging message (`logging.info()`) at the start of the download process to log the total number of files to download, with the following format: `START download of {total_files} files...`
- add one "end" logging message (`logging.info()`) at the end of the download process to log the completion of the download, with the following format: `END download of {total_files} files!`
- Output the "start" and "end" logging messages in the console as well, with the same format as the log file.

### Response

1. Add import logging
2. Add a configure_logging(timestamp) helper that sets up a file handler (data/logs/<timestamp>/download.log) and a console handler, both with the required format
3. Read CSV rows into a list first to get total_files
4. Call configure_logging early in download_images
5. Replace print calls with logging.info()
6. Add START and END log messages

No new dependencies needed — logging is stdlib

- `download.py`: Add logging import, configure_logging() helper, replace print with logging.info(), add START/END messages.

## Round 2.1

### Context

- file `.github/copilot-instructions.md`
- file `data/export.lite.csv`
- file `download.py`
- file `pyproject.toml`

### Prompt

Update `download.py` to have logging messages (`Downloading [...]` and `Downloaded [...]`) output ONLY in the log file, not in the console. Keep the "start" and "end" logging messages output in both (console and log file). That way, the console will show less, while the log file will contain all the detailed messages about each file being downloaded.

### Response

In configure_logging, set the console handler to only show WARNING and above (effectively hiding INFO detail messages), but keep the file handler at INFO. Then, for the START/END messages, use a level that passes through the console filter — the cleanest stdlib approach is to add a custom level (e.g. NOTICE between INFO and WARNING), but the simpler approach is to just use logging.WARNING for START/END on the console while keeping everything at INFO in the file.

Actually, the cleanest approach without a custom level: keep both handlers at INFO, but set the console handler's level to WARNING and log START/END with logging.warning(). However, that semantically misuses WARNING.

Best approach: add a custom NOTICE log level (e.g. 25, between INFO=20 and WARNING=30). Use it for START/END messages — both handlers will show it. Use logging.info() for per-file messages — only the file handler (at INFO=20) will show them, since the console handler is set to NOTICE=25.

- `download.py`: Add a NOTICE custom log level, set console handler level to NOTICE, keep file handler at INFO, use logging.notice() for START/END and logging.info() for per-file messages.

## Round 3

### Context

- file `.github/copilot-instructions.md`
- file `data/export.lite.csv`
- file `download.py`
- file `pyproject.toml`

### Prompt

Edit `download.py` to add a **progress bar** to the download process. Here are detailed implementation instructions:
- consider using an existing Python library for implementation.
- It should show the number of files downloaded and the total number of files to download plus a percentage of completion.
- It should update after each file is downloaded.
- It should be displayed in the console, not in the log file.

### Response

1. pyproject.toml: Add tqdm as a dependency — it's the most popular and well-maintained Python progress bar library.
2. download.py:
    - Import tqdm
    - Wrap the row iteration with a tqdm progress bar showing file count and percentage
    - Ensure tqdm writes to sys.stderr (console only, not captured by the logging file handler)

- `download.py`: Import tqdm and wrap the download loop with a progress bar.
- `pyproject.toml`: Add tqdm to dependencies.

## Round 4

### Context

- file `.github/copilot-instructions.md`
- file `data/export.lite.csv`
- file `pyproject.toml`
- file `upload.py`

### Prompt

This is the first step to implement the upload process: iterate over the CSV file and for each row: build the equivalent S3 object key then get the Object attributes (...). If the object does not exist, log an error message. Here are detailed implementation instructions:

Edit `upload.py` to iterate over the CSV file at `CSV_FILE_PATH` and for each row:

- in the CSV file the column to use for the file relative path and name is `publicId`
- build the S3 object key using the following pattern: `s3://{AWS_S3_BUCKET_NAME}/{OBJECT_RELATIVE_PATH}.{IMAGE_EXTENSION}`
  - `AWS_S3_BUCKET_NAME` is an environment variable defined in `.env`
  - `OBJECT_RELATIVE_PATH` is a variable to define by removing the prefix defined in `SKIPPED_PREFIX` from the `publicId` value
  - `IMAGE_EXTENSION` is defined in `upload.py`
- Retrieve the S3 Object attributes (or metadata) without downloading the file and output the following attributes with the following format: `Exist: {object_key} ; size={size} ; {last modified date} ; etag={etag} ; {content type} ; {checksum}`
- if the object does not exist, log an error message with the following format: `Do NOT exist: {object_key} !`

Use the `boto3` library to interact with AWS S3. Authentication is not part of this project, it is assumed that the credentials are already available in a shared credential file (`~/.aws/credentials`) and that `boto3` can access them without any additional configuration.

Usage of the updated `upload.py` should be as follows: `python upload.py` (+ any required parameters if needed)

### Response

1. upload.py:
    - Add imports: csv, logging, os, boto3, dotenv
    - Load .env and read AWS_S3_BUCKET_NAME
    - Add configure_logging() (reusing same pattern as download.py)
    - Add build_s3_object_key() helper to strip SKIPPED_PREFIX and build the key
    - Add check_objects() function iterating over CSV rows, calling s3.get_object_attributes() to retrieve metadata without downloading, logging existence or error
2. pyproject.toml: Add boto3 dependency.
3. .env: Document the new AWS_S3_BUCKET_NAME variable.

- `pyproject.toml`: Add boto3 dependency.
- `upload.py`: Add imports, env loading, logging setup, S3 key builder, and check_objects() main function.
- `.env`: Add AWS_S3_BUCKET_NAME alongside the existing variable.
