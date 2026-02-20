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

1. Load environment variables from .env (if present) and read CLOUDINARY_BASE_URL.
2. Create a run output folder under data/runs/<timestamp> using TIMESTAMP_FORMAT.
3. Parse CSV_FILE_PATH, reading the publicId column for each row.
4. For each publicId, build the download URL: {CLOUDINARY_BASE_URL}/{DEFAULT_TRANSFORMATION_PREFIX}/{publicId}.{IMAGE_EXTENSION}.
5. Download the file and save it under the run folder, preserving the publicId relative path (create parent dirs as needed).
6. Print progress logs exactly as requested.

- `download.py`: Implement CSV-driven downloads, .env loading, timestamped run folder creation, URL building, and console progress logging.
- `pyproject.toml`: Add python-dotenv to load .env so CLOUDINARY_BASE_URL is available at runtime.

## Round 1.1

### Context

- file `.github/copilot-instructions.md`
- file `data/export.lite.csv`
- file `download.py`
- file `pyproject.toml`

### Prompt

There is an issue with the current implementation: running `python download.py` output the error message: 
```
  File "/Users/gabriel.damour/PycharmProjects/cgm-5625/download.py", line 20
    from __future__ import annotations
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
SyntaxError: from __future__ imports must occur at the beginning of the file
```
Fix the issue.

### Response

1. Open download.py and move from __future__ import annotations to the very top (it must come right after the module docstring, before any other code).
2. Keep settings/constants after the imports to avoid reintroducing the same SyntaxError.

- `download.py`: Fix the SyntaxError by placing the __future__ import at the beginning of the file (after the docstring) and keeping constants below imports.

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

1. Compute the run timestamp once (already done) and reuse it for both downloads and logs folders.
2. Create data/logs/<timestamp>/download.log.
3. Configure a dedicated logger with:
    - level INFO
    - formatter including timestamp '%Y-%m-%d %H:%M:%S', level, and message
    - a FileHandler writing to download.log
    - a StreamHandler writing to console (so START/END also appear in console)
4. Read all CSV rows first to collect publicIds and compute total_files.
5. Log START download of {total_files} files..., then iterate downloads logging progress/success via logger.info(...), and finally log END download of {total_files} files!.

- `download.py`: Replace print() calls with structured logging, add timestamped log folder+file, and log START/END messages to both file and console.

## Round 2.1

### Context

- file `.github/copilot-instructions.md`
- file `data/export.lite.csv`
- file `download.py`
- file `pyproject.toml`

### Prompt

Update `download.py` to have logging messages (`Downloading [...]` and `Downloaded [...]`) output ONLY in the log file, not in the console. Keep the "start" and "end" logging messages output in both (console and log file). That way, the console will show less, while the log file will contain all the detailed messages about each file being downloaded.

### Response

1. Update the logger configuration to use two handlers with different levels:
    - File handler: logs everything (INFO) so it contains detailed per-file messages.
    - Console handler: logs only high-level messages by filtering to START... and END....
2. Keep using logger.info(...) in the download loop; the filtering will ensure those messages go only to the file.

- `download.py`: Add a console filter so only START/END messages appear on stdout, while all INFO messages (including per-file) go to download.log.
