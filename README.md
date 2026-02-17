# README

A collection of python scripts to achieve a one-off task of downloading and uploading a list of images.

This is one-off experiment comparing multiple GitHub Copilot models. Multiple rounds of prompts and code generation is performed for each reviewed model and then committed successively in a different branch of the repository.

## Models

List of models reviewed:

- **GPT-5 mini** (0x)
- **GPT-5.2** (1x)
- **Gemini 3 Pro** (1x)
- **Claude Sonnet 4.5** (1.0x)
- **Claude Opus 4.5** (3.0x)

Extra:

- **Gemini 3 Flash** (0.33x)
- **Claude Haiku 4.5** (0.33x)

## Context

During the migration from an old image delivery service (Cloudinary) to new one, we realised that a significant number of the images (~1000) were using photoshop format (PSD) under a jpg extension in our catalog: a AWS S3 bucket. The old image delivery service supports this format and deliver the image as a jpeg, but the new one does not. The usage of Photoshop format wasn't desirable in the first place, it was decided to convert all the images at the source (in our catalog) to a proper jpeg format.

This is achieved by leveraging the PSP support in the old image delivery service to convert the images, download them and then replace the original PSP image in the S3 bucket with the new jpeg version.

This what the scripts in this repository are doing.
