# learning-business-skill

A [Cortex Code](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code) skill that transforms unstructured workshop Markdown files into a structured Learning Path and a synthetic technical summary tailored to the user's professional profile.

## What it does

Given a set of workshop transcription and notes files, this skill:

1. Validates and pairs source files by session
2. Cleans Base64-encoded images from Notes files to reduce token usage
3. Generates a `SUMMARY.md` with an executive overview, conceptual and technical points, and a business glossary
4. Assesses the user's expertise through domain-specific questions
5. Produces a tailored Learning Path with a curriculum table, module breakdowns, and validation questions

## Triggers

Load this skill when the user asks about:

- Learning paths or training curricula
- Summarizing workshop transcripts or notes
- Instructional design or technical onboarding
- Expertise assessment and tailored curriculum generation

## Input file format

Two files are required per workshop session, both using timecodes for cross-referencing:

| Type | Naming pattern | Contains images |
|------|---------------|----------------|
| Transcription | `{nn}_{workshop-name}_transcription.md` | No |
| Notes | `{nn}_{workshop-name}_notes.md` | Possibly (Base64) |

`{nn}` is a zero-padded session number (`01`, `02`, ...). At least one file of each type must be provided.

## Output

| File | Description |
|------|-------------|
| `SUMMARY.md` | Synthetic technical summary: executive overview, conceptual points, technical points, glossary |
| Learning Path | Tailored curriculum with module table, detailed breakdowns, and validation questions |

## Prerequisites

- Python >= 3.11
- [uv](https://github.com/astral-sh/uv) (recommended, no external pip dependencies required)

Install uv if not present:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# or
pip install uv
```

If uv is unavailable, the preprocessing script can be run directly with Python — it uses only the standard library.

## Scripts

### `scripts/clean_base64_images.py`

Replaces inline Base64-encoded images in Markdown files with human-readable descriptive tags (`[Image description: ...]`). Run on Notes files only before analysis.

```bash
# Single file — writes <stem>_cleaned.md alongside the source
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/clean_base64_images.py file_notes.md

# Specify output path
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/clean_base64_images.py file_notes.md --output cleaned.md

# Overwrite in place
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/clean_base64_images.py file_notes.md --inplace

# Multiple files
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/clean_base64_images.py a_notes.md b_notes.md c_notes.md
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `files` (positional) | One or more Markdown files to process |
| `--output PATH` | Output path (single input file only) |
| `--inplace` | Overwrite each input file in place |

## Directory structure

```
learning_business_skill/
├── SKILL.md                        # Skill definition and workflow
├── pyproject.toml                  # Python project metadata
├── scripts/
│   └── clean_base64_images.py      # Base64 image cleaner
└── README.md
```

## Installation

Copy this directory to your Cortex Code skills folder:

```bash
# macOS / Linux
~/.snowflake/cortex/skills/learning_business_skill/

# Windows
%USERPROFILE%\.snowflake\cortex\skills\learning_business_skill\
```

Cortex Code will automatically discover and load the skill.
