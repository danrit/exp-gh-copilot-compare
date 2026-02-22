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

## Round 2.2

### Context

- file `.github/copilot-instructions.md`
- file `data/export.lite.csv`
- file `download.py`
- file `pyproject.toml`

### Prompt

There is an issue with the current implementation: it is confusing how the timestamp string used for folders is based on UTC time, while the timestamps in the log messages are based on local time. Update the implementation to use the same timezone for both, ideally local time.

### Response

1. Switch the run folder timestamp generation from UTC to local time by using datetime.now().astimezone() (local tz-aware).
2. Keep the logging timestamp consistent by switching the formatter to use local time explicitly via formatter.converter = time.localtime.
3. Remove the unused timezone import after changing timestamp generation.

- `download.py`: Use local time consistently for both the folder timestamp and log timestamps.

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

1. Add tqdm as a dependency (widely used progress bar library).
2. Import tqdm in download.py.
3. Wrap the download loop with tqdm(...) so it shows downloaded/total and % in the console.
4. Ensure the progress bar is console-only by leaving the logger’s console handler filtered to START/END (the per-file logger.info(...) stays file-only due to the filter).
5. Update the bar after each file completes by iterating through tqdm.

- `download.py`: Show a tqdm progress bar in the console (not the log file) that updates after each downloaded file.
- `pyproject.toml`: Add tqdm dependency for a console progress bar.

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

1. Add required runtime dependencies (boto3) to pyproject.toml.
2. Replace the incomplete upload.py skeleton with a working script that:
    - loads .env and reads AWS_S3_BUCKET_NAME
    - iterates CSV_FILE_PATH, reads publicId
    - removes SKIPPED_PREFIX from publicId to form OBJECT_RELATIVE_PATH
    - builds s3://{bucket}/{OBJECT_RELATIVE_PATH}.{IMAGE_EXTENSION}
    - calls head_object to fetch metadata (no download)
    - logs Exist: ... line with size, last modified date, etag, content type, checksum
    - logs Do NOT exist: ... ! when missing

- `pyproject.toml`: Add boto3 dependency for S3 head_object.
- `upload.py`: Implement the CSV iteration + S3 object key building + head_object metadata output formats from PROMPT.md.

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

1. Update upload.py to match PROMPT.md:
    - Replace print(...) with a logger configured like download.py (file logs + console START/END only).
    - Create data/logs/<timestamp>/upload.log using local-time timestamp.
    - Remove content type and checksum from the “Exist” line.
    - Display ContentLength as human-readable size.
    - Log START/END messages with total file count (collect publicIds first).
2. Keep dependencies as-is (already includes python-dotenv and boto3; no new libraries needed).

- `upload.py`: Implement the logging behavior, human-readable size formatting, and simplified “Exist” output exactly as requested in PROMPT.md.

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

1. Add tqdm to upload.py imports.
2. Wrap the per-object loop with tqdm(...) so the console shows processed/total and a percentage.
3. Keep per-object logging via logger.info(...) (it will continue to go only to the log file because the console handler is filtered to START/END).

- `upload.py`: Add a tqdm progress bar for the upload/check loop; it renders in the console and is not written to the log file.

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

1. Add the missing settings in upload.py: BACKUP_EXTENSION and OBJECT_MODIFIED_DATE_LIMIT = "2026-01-01".
2. Parse OBJECT_MODIFIED_DATE_LIMIT into a timezone-aware local datetime at start-of-day for correct comparison with S3 LastModified.
3. After head_object succeeds, compare LastModified to the limit:
   - If earlier: log the required “will be copied…” message, then copy the object to {OBJECT_RELATIVE_PATH}.{BACKUP_EXTENSION} and log success or a relevant error.
   - Else: log the required “will NOT be copied.” message.
4. Keep existing logger + tqdm behavior unchanged.

- `upload.py`: Add date-limit settings, parse/compare LastModified, and perform conditional copy_object with required log messages.

## Round 7.1

### Context

- file `.github/copilot-instructions.md`
- file `data/export.lite.csv`
- file `download.py`
- file `pyproject.toml`
- file `upload.py`

### Prompt

There is an issue with the current implementation: the `BACKUP_EXTENSION` variable used was incorrectly removed from the file `upload.py` during an earlier change in this prompt session (in an attempt of code cleaning?). During the last prompt, the variable became needed and with no specific instruction given, it was set by the agent to an arbitrary value of `bak`.

Edit `upload.py` to change `BACKUP_EXTENSION` variable to its initial value of `psd`. And restore the comment describing it for code clarity, see below.

```python
# BACKUP_EXTENSION: all the files are PSD file originally. Prior to
# replacing the original by a real jpg version, we are doing a backup as PSD.
```

### Response

1. Open PROMPT.md and identify the required change: BACKUP_EXTENSION must be restored to its original value psd, along with a specific explanatory comment.
2. Update upload.py:
    - Change BACKUP_EXTENSION from "bak" to "psd".
    - Restore the two-line comment exactly as provided in PROMPT.md (keeping it adjacent to the setting for clarity).
3. No dependency changes are needed.

- `upload.py`: Restore BACKUP_EXTENSION to psd and reinstate the original comment explaining why it is used.

## Round 8

### Context

- file `.github/copilot-instructions.md`
- file `data/export.lite.csv`
- file `download.py`
- file `pyproject.toml`
- file `upload.py`

### Prompt

Edit `download.py` to remove one subfolder (`editorial`), part of the `publicID` created for each image downloaded (similarly to what is done in `upload.py`). Here are detailed implementation instructions:

- define a new variable `SKIPPED_PREFIX` with the value `editorial/`
- update `local_path` to remove the `SKIPPED_PREFIX` from the `publicId` value when building the local path to save the downloaded file.

### Response

1. Add SKIPPED_PREFIX = "editorial/" to download.py settings (mirroring upload.py).
2. When building the output_path, remove SKIPPED_PREFIX from the start of public_id (only if present) so the local folder tree doesn’t include editorial/.
3. Keep the download URL unchanged (still uses the original publicId).

- `download.py`: Add SKIPPED_PREFIX and strip it from the local output path computation.

## Round 9

### Context

- file `.github/copilot-instructions.md`
- file `data/export.lite.csv`
- file `download.py`
- file `pyproject.toml`
- file `upload.py`

### Prompt

Finally update `upload.py` to add actual upload of the file (downloaded by `download.py`) to S3 if the last modified date of the existing object is earlier than the `OBJECT_MODIFIED_DATE_LIMIT`. Here are detailed implementation instructions:

- define a new variable `DOWNLOADED_FILES_PATH` in `upload.py` with the value `data/runs/20260223-054344`
- inside the existing logic where the object is copied to a backup key if it is modified before the `OBJECT_MODIFIED_DATE_LIMIT`, add the upload of the file located at `{DOWNLOADED_FILES_PATH}/{publicId}.{IMAGE_EXTENSION}` to the original object key in S3 (the one that was checked for existence and metadata).
- log a message if the local file to upload does not exist with the following format: `Local file {local_file_path} does not exist, cannot upload to {object_key}!`
- log a message when the upload is successful with the following format: `Object {object_key} was successfully uploaded from {local_file_path}!`
- if the upload operation fails, log a relevant error message.

### Response

1. Add DOWNLOADED_FILES_PATH setting to upload.py with the exact value from PROMPT.md.
2. When an object exists and is older than OBJECT_MODIFIED_DATE_LIMIT, keep the existing backup copy logic.
3. In that same branch, locate the local file at {DOWNLOADED_FILES_PATH}/{publicId}.{IMAGE_EXTENSION} (do not strip SKIPPED_PREFIX for this path; it must match the on-disk structure created from publicId).
4. If the local file does not exist, log exactly: Local file {local_file_path} does not exist, cannot upload to {object_key}!
5. If it exists, upload it to the original object_key in S3. Log success exactly: Object {object_key} was successfully uploaded from {local_file_path}!
6. If the upload fails, log a relevant error message (include key, path, and exception).

## Round 9.1

### Context

- file `.github/copilot-instructions.md`
- file `data/export.lite.csv`
- file `download.py`
- file `pyproject.toml`
- file `upload.py`

### Prompt

There is an issue with the current implementation: error message: `Local file {local_file_path} does not exist, cannot upload to {object_key}!` is logged even when the local file actually exists. It seems to be because the `publicId` value used to build the `local_file_path` still contains the `SKIPPED_PREFIX` (`editorial/`) which is not present in the actual filename of the downloaded file (as it was removed in `download.py`). Fix the issue in `upload.py`.

### Response

1. Identify why the local file check is wrong: download.py strips SKIPPED_PREFIX when writing to disk, but upload.py still uses the raw public_id (with editorial/) when building local_file_path.
2. Fix upload.py to build the local file path using the same “relative” path logic as downloads:
    - compute local_relative_path = _object_relative_path_from_public_id(public_id)
    - use that to form {DOWNLOADED_FILES_PATH}/{local_relative_path}.{IMAGE_EXTENSION}
3. Keep the rest of the S3 logic, logging, and tqdm behavior unchanged.

- `upload.py`: Build local_file_path from the publicId with SKIPPED_PREFIX removed (matching download.py output structure), so existing local files are correctly detected.
