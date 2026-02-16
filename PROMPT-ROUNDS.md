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

Solution (step-by-step)
1. Create a timestamp string early and make both run and log subfolders under data/runs/<timestamp> and data/logs/<timestamp>.</timestamp></timestamp>
2. Configure the root logger with level INFO and a formatter that includes timestamp (format '%Y-%m-%d %H:%M:%S'), log level and message. Attach both a FileHandler (download.log in the run-specific logs folder) and a StreamHandler so START/END appear on console.
3. Read the CSV into memory to count how many rows have a non-empty publicId and log the START message.
4. Iterate rows, replacing print() calls with logging.info()/logging.error(), save files in the run folder preserving publicId path structure.
5. Log the END message when finished.

- `download.py`: Replace prints with logging and add log file configuration and START/END messages.

## Round 2.1

### Context

- file `.github/copilot-instructions.md`
- file `data/export.lite.csv`
- file `download.py`
- file `pyproject.toml`

### Prompt

Update `download.py` to have logging messages (`Downloading [...]` and `Downloaded [...]`) output ONLY in the log file, not in the console. Keep the "start" and "end" logging messages output in both (console and log file). That way, the console will show less, while the log file will contain all the detailed messages about each file being downloaded.

## Response

Solution (step-by-step)

1. Create a dedicated logger for this module so we don't affect the root logger.
2. Add a FileHandler that logs all INFO+ messages to the run-specific log file.
3. Add a StreamHandler for console output but attach a filter that only allows START/END messages through.
4. Replace calls to the module-level logging.* functions with the module logger (logger.info / logger.error) so handlers and the filter behave as intended.

- `download.py`: Adjust logging setup to send detailed per-file messages only to the file handler and allow START/END messages to appear on both console and file.

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

## Response

Solution (step-by-step)
1. Add the well-maintained tqdm library to project dependencies.
2. Import tqdm and sys in download.py.
3. Create a console progress bar (writing to stdout) with total = number of files to download.
4. After each successful download, increment the progress bar. Leave START/END log messages unchanged so they still print to console.

Changes grouped by file:

- `download.py`: Add tqdm import and a console progress bar that updates after each successful file download.
- `pyproject.toml`: Add tqdm dependency.
