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

Step-by-step solution

1. Edit upload.py to:
    - Load .env using python-dotenv to get AWS_S3_BUCKET_NAME.
    - Read the CSV file and iterate over rows.
    - For each row, strip SKIPPED_PREFIX from publicId to get the object relative path.
    - Build the S3 object key as {relative_path}.{IMAGE_EXTENSION}.
    - Use boto3 S3 client's head_object to retrieve metadata without downloading.
    - Log the attributes if the object exists, or log an error if it doesn't (404 / NoSuchKey).
    - Set up logging (to file + console via tqdm) and use tqdm for progress.
2. Update pyproject.toml to add boto3 as a dependency.

- `upload.py`: Implement CSV iteration, S3 object key construction, and metadata retrieval using boto3.
- `pyproject.toml`: Add boto3 as a dependency.

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

### Response

Step-by-step solution
1. Add a helper function format_size to convert bytes into a human-readable string (KB, MB, GB).
2. Remove content_type and checksum from the logging output.
3. Replace the raw size in the log line with the formatted human-readable size.

- `upload.py`: Remove content_type/checksum, add format_size helper, use it in the log line.

## Round 6

### Context

- file `.github/copilot-instructions.md`
- file `data/export.lite.csv`
- file `download.py`
- file `pyproject.toml`
- file `upload.py`

### Prompt

Edit `upload.py` to add a **progress bar** to the upload process, similar to the one implemented in `download.py`. Here are detailed implementation instructions:

- It should show the number of files uploaded and the total number of files to upload plus a percentage of completion.
- It should update after each file is uploaded.
- It should be displayed in the console, not in the log file.

### Response

The upload.py file already imports tqdm and wraps the loop with it. The progress bar is already in place showing count, total, and percentage. No changes are needed — the implementation already matches what PROMPT.md requests.

However, looking more closely, the current tqdm usage is correct but let me confirm it fully satisfies the prompt: ✅ shows number of files and total, ✅ percentage, ✅ updates after each iteration, ✅ displayed in console not log file.

The file already has the progress bar implemented correctly. No changes are required to any file.

## Round 7

### Context

- file `.github/copilot-instructions.md`
- file `data/export.lite.csv`
- file `download.py`
- file `pyproject.toml`
- file `upload.py`

### Prompt

Now that `upload.py` can iterate over the CSV file and run successfully this simple object check using `boto3` library to interact with AWS S3, the next step is to create a copy of the existing object to a new object key with a different extension. Here are detailed implementation instructions:

- define a new variable `OBJECT_MODIFIED_DATE_LIMIT` in `upload.py` with a date value '2026-01-01'
- For each row in the CSV file, after successfully checking the existence of the object and retrieving its attributes and IF the `LastModified` attribute is earlier than the `OBJECT_MODIFIED_DATE_LIMIT`:
  - log a message with the following format: `Object {object_key} was modified before {OBJECT_MODIFIED_DATE_LIMIT}, it will be copied to a new object key with the backup extension.`
  - create a copy of the object to a new S3 object with the key defined using the following pattern: `s3://{AWS_S3_BUCKET_NAME}/{OBJECT_RELATIVE_PATH}.{BACKUP_EXTENSION}`
    - `AWS_S3_BUCKET_NAME` is an environment variable defined in `.env`
    - `OBJECT_RELATIVE_PATH` is a variable to define by removing the prefix defined in `SKIPPED_PREFIX` from the `publicId` value
    - `BACKUP_EXTENSION` is defined in `upload.py`
  - log a message when the copy is successful with the following format: `Object {object_key} was successfully copied to {backup_object_key}!`
  - if the copy operation fails, log a relevant error message.
- If the `LastModified` attribute is later than or equal to the `OBJECT_MODIFIED_DATE_LIMIT`, log a message with the following format: `Object {object_key} was modified after {OBJECT_MODIFIED_DATE_LIMIT}, it will NOT be copied.`

### Response

Step-by-step solution

 1. Add OBJECT_MODIFIED_DATE_LIMIT as a date string '2026-01-01', then parse it into a timezone-aware datetime for comparison with LastModified (which is timezone-aware from boto3).
2. After the successful head_object call, compare last_modified against the date limit.
3. If before the limit: log the intent, perform copy_object to {object_relative_path}.{BACKUP_EXTENSION}, log success or error.
4. If on or after the limit: log that it will NOT be copied.

- `upload.py`: Add OBJECT_MODIFIED_DATE_LIMIT, parse it as a timezone-aware datetime, and add the copy logic after the existence check.
