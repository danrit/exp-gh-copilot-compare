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

Step-by-step solution

1. Read the CSV file using the csv standard library module, extracting the publicId column.
2. Load CLOUDINARY_BASE_URL from a .env file using the python-dotenv library (popular, well-maintained, and the standard way to load .env files).
3. Build download URLs using the pattern {CLOUDINARY_BASE_URL}/{DEFAULT_TRANSFORMATION_PREFIX}/{publicId}.{IMAGE_EXTENSION}.
4. Create a timestamped output directory under data/runs/ using TIMESTAMP_FORMAT.
5. Download each image using requests (popular, well-maintained HTTP library), creating subdirectories as needed (since publicId can contain /).
6. Log progress to the console.
7. Update pyproject.toml to include the new dependencies (python-dotenv, requests).

- `download.py`: Rewrite the script to read the CSV, build URLs, download images into a timestamped folder, and log progress.
- `pyproject.toml`: Add requests and python-dotenv as dependencies.

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

Step-by-step solution

1. Import logging from the standard library.
2. Count total rows in the CSV upfront so we can log the total before starting downloads.
3. Create a data/logs/{timestamp}/ directory and configure logging.basicConfig to write to download.log inside it, with the specified format and INFO level.
4. Replace print() calls with logging.info().
5. Add START/END messages that go to both the log file and the console. To achieve "console as well" for only those two messages, add a temporary StreamHandler or simply also print() them alongside the logging call. The cleanest approach: use print() for just those two plus logging.info().

No new dependencies are needed — logging is part of the standard library, so pyproject.toml stays unchanged

- `download.py`: Replace print with logging, add log file configuration, add START/END messages printed to both console and log file.

## Round 2.1

### Context

- file `.github/copilot-instructions.md`
- file `data/export.lite.csv`
- file `download.py`
- file `pyproject.toml`

### Prompt

There is an issue with the current implementation: it is confusing how the timestamp string used for folders is based on UTC time, while the timestamps in the log messages are based on local time. Update the implementation to use the same timezone for both, ideally local time.

### Response

Step-by-step solution

1. Change the timestamp for folder names from datetime.now(timezone.utc) to datetime.now() (local time).
2. Add datefmt and a logging.Formatter with converter set to time.localtime — but actually, logging already uses local time by default, so the log timestamps are already local. The only mismatch is the folder timestamp using UTC. Simply switching the folder timestamp to local time fixes the inconsistency.

The fix is a one-line change: replace datetime.now(timezone.utc) with datetime.now()

- `download.py`: Change the timestamp from UTC to local time so it matches the log message timestamps.

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

Step-by-step solution

1. Add tqdm — the most popular and well-maintained Python library for progress bars. It shows count, total, and percentage out of the box.
2. Wrap the download loop with tqdm, setting the total and a description.
3. Remove the print() calls for START/END since tqdm will handle console progress display (keep the logging.info calls for the log file).
4. Add tqdm to pyproject.toml dependencies.

- `download.py`: Wrap the download loop with tqdm for a console progress bar; keep log-only messages for START/END.
- `pyproject.toml`: Add tqdm as a dependency.
