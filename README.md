# README

This is an experiment comparing several GitHub Copilot models. Multiple rounds of prompts and code generation is performed for each reviewed model and then committed successively in a different branch of the repository. No manual change is made to the generated code.

Once can then observe two things:

- Gage the overall implementation of the different models by comparing the branches. See if the advanced models are actually generating better code than simple models.
- follow the prompt instructions and code change in each commit for a model: checking how well a model can follow instructions. This "iterative Spec-driven-Development (SDD)" approach is a sort of experiment inside an experiment.

Practically this repo is a collection of two python scripts to achieve a one-off task of downloading and uploading a list of images.

## Models

List of models reviewed:

- **GPT-5 mini** (0x)
- **GPT-5.2** (1x)
- **Claude Sonnet 4.6** (1.0x)
- **Claude Opus 4.6** (3.0x)

Extra:

- **Gemini 3 Flash** (0.33x)
- **Claude Haiku 4.5** (0.33x)
- **Gemini 3 Pro** (1x)

## Experiment process

- Using edit mode in copilot chat.
- I have split the works into multiple steps, that I have progressively defined, and prompted the model for each one.
- Accepting all the edit suggestions (no manual changes), and create a git commit for each round.
- a round is defined as a prompt, code generation, commit.
- validate by testing and prompt again, ie do another round, if needed until the correct result is achieved for that step.
- Consequently, a step can be made of multiple rounds.
- When the models suggest edit to the dependencies (in `pyproject.toml`), I have accepted them and run `pip install -e .` manually.

Using one "chat session" per model. the model is actually fed the whole history of the prompts and responses at every new round of prompt. The committed file [`PROMPT-ROUNDS.md`](./PROMPT-ROUNDS.md) is here for the us to review the rounds of change later. It was not passed-on as a context to the model because that is the purpose of GitHub Copilot chat session history!

Practically, because I couldn't copy-paste markdown into the Copilot IDE plugin prompt text area, I have entered it into a local, non-committed file, `PROMPT.md`, and then entered into the prompt (same text at every round): 

> Follow the instructions given in `PROMPT.md` file

## Context

During the migration from an old image delivery service (Cloudinary) to new one, we realised that a significant number of the images (~1000) were using photoshop format (PSD) under a jpg extension in our catalog: an AWS S3 bucket. The old image delivery service supports this format and deliver the image as a jpeg, but the new one does not. The usage of Photoshop format wasn't desirable in the first place, it was decided to convert all the images at the source (in our catalog) to a proper jpeg format.

This is achieved by leveraging the PSP support in the old image delivery service to convert the images, download them and then replace the original PSP image in the S3 bucket with the new jpeg version.

This what the scripts in this repository are doing.
