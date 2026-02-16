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

Solution (step-by-step)
1. Load environment variables (from .env) and read AWS_S3_BUCKET_NAME.
2. Open the CSV and iterate rows, reading publicId.
3. For each publicId build OBJECT_RELATIVE_PATH by stripping SKIPPED_PREFIX when present and append IMAGE_EXTENSION to form the S3 key.
4. Use boto3.client('s3').head_object(Bucket=bucket, Key=key) to fetch metadata without downloading.
5. On success print the required "Exist: ..." line with size, last modified, etag, content type and a checksum fallback.
6. If head_object reports the object does not exist, print "Do NOT exist: {object_key} !".
7. Continue processing remaining rows.

Changes grouped by file:

- `upload.py`: Implement CSV iteration, environment loading and S3 head_object checks. Uses boto3 and python-dotenv.
- `pyproject.toml`: Add boto3 to project dependencies.

## Round 5

### Context

- file `.github/copilot-instructions.md`
- file `data/export.lite.csv`
- file `download.py`
- file `pyproject.toml`
- file `upload.py`

### Prompt

Edit `upload.py` to improve the output:

- Remove `content type` and `checksum` from the output line, as they are actually not useful in the current context.
- Format the size in a human-readable format (e.g., KB, MB, GB)
- move logging messages to a logger instead of using print statements. Here are detailed implementation instructions:
  - name the log file `upload.log` and create a subfolder in `data/logs`, with the same timestamp string as the one used for the downloaded files, to store it.
  - configure the logger:
      - set the logging level to `INFO`
      - set the log format to include the timestamp (format '%Y-%m-%d %H:%M:%S'), log level and message
      - set the log file path to the one defined above
  - replace the print statements with appropriate logging calls (e.g., `logging.info()`)
  - add one "start" logging message (`logging.info()`) at the start of the upload process to log the total number of files to download, with the following format: `START upload of {total_files} files...`
  - add one "end" logging message (`logging.info()`) at the end of the upload process to log the completion of the download, with the following format: `END upload of {total_files} files!`
- Output the "start" and "end" logging messages in the console as well, with the same format as the log file, just like in `download.py`. The other logging messages (existence and metadata of each file) should be output only in the log file, not in the console.

### Response

Solution (step-by-step)
1. Determine a timestamp string to use for the upload log folder. Reuse the latest run folder name under data/runs if present (so upload logs share the same timestamp as a previous download run); otherwise fall back to now().
2. Create data/logs/<timestamp> and set upload.log path.</timestamp>
3. Configure a dedicated module logger (INFO level, timestamped formatter). Attach a FileHandler that logs all INFO+ messages, and a StreamHandler filtered to only allow START/END messages to the console.
4. Read the CSV into memory to compute total_files, log START upload..., then iterate rows, call head_object for each key and log existence/metadata lines to the file-only logger.
5. Format ContentLength into a human-readable size string and remove content-type and checksum from the output line.
6. Log END upload... at the end.

Changes grouped by file:

- `upload.py`: Create a timestamped log folder (reusing latest data/runs timestamp if available), configure logger with a console filter for START/END messages, use logger for all messages, and output Exist lines without content-type/checksum and with human-readable size.

## Round 5.1

### Context

- file `.github/copilot-instructions.md`
- file `data/export.lite.csv`
- file `download.py`
- file `pyproject.toml`
- file `upload.py`

### Prompt

Edit `upload.py` to change the location of the log file: Here are detailed implementation instructions:

- create a timestamp string using the format defined in `TIMESTAMP_FORMAT` and create a subfolder in `data/logs` with this timestamp string as name, to save the log file.
- Keep the filename as `upload.log`
- remove the logic to reuse the latest run folder name under `data/runs` as it should not be needed anymore.

### Response

Solution (step-by-step)
1. Replace the existing _choose_timestamp implementation (which searched data/runs) with a simpler function that returns the current timestamp using TIMESTAMP_FORMAT.
2. Keep main() unchanged (it already calls _choose_timestamp); the log folder will now always use the current timestamp under data/logs.
3. This meets the PROMPT.md requirements: create a timestamp string from TIMESTAMP_FORMAT, create data/logs/<timestamp>/upload.log, and remove reuse of latest run folder logic.</timestamp>

- `upload.py`: Change _choose_timestamp to always use now() instead of inspecting data/runs.
