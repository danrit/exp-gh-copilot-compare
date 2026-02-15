# Copilot Instructions

## Overview

This project contains several python scripts to achieve a one-off task: downloading locally from an image delivery service (Cloudinary) a set of images specified in a CSV file and uploading them in a AWS S3 bucket.

Images on the delivery service are publicly accessible.

The AWS s3 bucket is private and authentication is not part of that project: an external process, using library from AWS `boto3` is responsible for providing the credentials and make available in a shared credential file (`~/.aws/credentials`). This project will use `boto3` to access the credentials and perform AWS requests.

## Comments

Use docstrings to describe the purpose of each package, module, class or function.

Use Block and Inline Comments only for non-obvious logic.

## Usage of dependencies

When requested in the prompt to achieve a requirement, use popular and well-maintained libraries when appropriate.

Prefer using the python standard library first and external libraries second if it is the general best practice to achieve the requirement.

Use libraries to keep the code in this project simple and reduce the amount of code to maintain.

The management of dependencies is done with the standard configuration file `pyproject.toml`. When using an adding, updating or removing library during a code change, include the change in that file.