---
name: learning-business-skill
description: "Transform unstructured Markdown source files (meeting transcripts, technical documentation) into a structured Learning Path and a synthetic technical summary tailored to the user's professional profile. Use when: learning path, instructional design, summarize transcript, training curriculum, generate summary, expertise assessment, tailored curriculum, technical onboarding, meeting transcript analysis."
---

# Learning Path Generator

## When to Use

As an expert Instructional Designer and Technical Analyst, use this skill when the user wants to:
- Generate a learning path or training curriculum from workshop source files
- Summarize workshop transcriptions and notes into a structured technical overview
- Assess expertise and tailor instructional content to a professional profile
- Produce a structured `SUMMARY.md` from a set of Transcription and Notes files

## Input File Types

Two file types are required per workshop session. Both carry timecodes for cross-referencing.

| Type | Naming pattern | Contains images |
|------|---------------|----------------|
| Transcription | `{nn}_{workshop-name}_transcription.md` | No |
| Notes | `{nn}_{workshop-name}_notes.md` | Possibly (Base64) |

`{nn}` is a zero-padded session number (`01`, `02`, …). The workshop name slug must match between paired files. At least one file of each type must be provided — see Step 1 for validation.

## Prerequisites

- **Python ≥ 3.11** — required by the preprocessing script
- **uv** (recommended) — simplifies script execution. Install if not present:
  ```bash
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # or: pip install uv
  ```
  If uv is unavailable, run the script directly with Python — no external dependencies are needed:
  ```bash
  python <SKILL_DIR>/scripts/clean_base64_images.py [args]
  ```

## Workflow

Execute this workflow through five distinct steps. Do not skip steps or combine them unless explicitly authorized by the user.

---

### Step 1: Project Initialization

**Goal:** Collect and validate the source files.

**Actions:**

1. Present the following prompt to the user:
   ```
   Project Initialization: Please provide your workshop files. I expect two types:
   - Transcription files: {nn}_{workshop-name}_transcription.md
   - Notes files:         {nn}_{workshop-name}_notes.md

   Provide at least one of each. Multiple session pairs are supported.
   ```

2. Once files are provided, classify each file by its suffix:
   - Ends with `_transcription.md` → **Transcription**
   - Ends with `_notes.md` → **Notes**
   - Otherwise → warn the user that the file does not match the expected naming convention and ask them to confirm whether to include it.

3. Verify the minimum requirement: at least one Transcription file **and** at least one Notes file must be present. If either type is missing, tell the user which type is absent and wait for them to supply it before continuing.

4. Group paired files by their `{nn}_{workshop-name}` prefix and report the detected sessions to the user. Example:
   ```
   Detected sessions:
   - 01_kickoff   → 01_kickoff_transcription.md + 01_kickoff_notes.md
   - 02_deep-dive → 02_deep-dive_transcription.md (no notes file found)
   ```
   If a session is missing its pair, ask the user whether to proceed without it or supply the missing file.

**⚠️ MANDATORY STOPPING POINT**: Do NOT proceed to Step 2 until validation passes (at least one Transcription and one Notes file confirmed).

---

### Step 2: Preprocessing — Base64 Image Cleaning

**Goal:** Remove Base64-encoded images from Notes files to reduce token usage and keep analysis focused on textual content.

**Actions:**

1. Run `clean_base64_images.py` against **Notes files only** (files classified as `_notes.md` in Step 1) in a single invocation:
   ```bash
   uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/clean_base64_images.py <notes1.md> <notes2.md> ...
   ```
   Replace `<SKILL_DIR>` with the absolute path to this skill's directory. Each file produces a `<stem>_cleaned.md` sibling in the same directory.

   If uv is unavailable, run directly:
   ```bash
   python <SKILL_DIR>/scripts/clean_base64_images.py <notes1.md> <notes2.md> ...
   ```

   Do **not** pass Transcription files to this script — they contain no images.

2. Report to the user how many images were replaced per Notes file (the script prints this automatically).

3. For all subsequent steps, use:
   - The **cleaned Notes files** (`<stem>_cleaned.md`) as the Notes source
   - The **original Transcription files** unchanged

4. If no Base64 images are found in any Notes file, notify the user and treat the original Notes files as the cleaned source for all subsequent steps.

---

### Step 3: Synthetic Summary and File Generation

**Goal:** Create a high-level technical overview by cross-referencing Transcription and Notes files, then save it to the project.

**Actions:**

1. Analyze the source material using both file types together:
   - Use **Notes files** as the primary source of structured content (concepts, architecture, vocabulary, diagrams)
   - Use **Transcription files** to enrich context: where timecodes align between a Transcription and its paired Notes file, use the spoken dialogue to clarify or expand on the notes
   - Cross-reference by matching timecodes across paired files (same `{nn}_{workshop-name}` prefix)

2. Synthesize content across three dimensions:
   - **Conceptual** (Business Logic)
   - **Technical** (Systems/Architecture)
   - **Vocabulary** (Glossary of Terms)

3. Ask the user to confirm the target directory for the output file. Default to the current working directory if the user does not specify otherwise.

4. Generate a file named `SUMMARY.md` in the confirmed directory. This file must contain:
   - **Executive Overview**: A high-level summary of the workshop content.
   - **Conceptual Points**: Key business rules and functional logic.
   - **Technical Points**: Data flows, software architecture details, and system constraints.
   - **Glossary**: Definitions of industry-specific or project-specific terminology.

5. Notify the user that `SUMMARY.md` has been created.

**⚠️ OPTIONAL STOPPING POINT**: Invite the user to review `SUMMARY.md` before continuing:
```
SUMMARY.md has been written to <target_dir>. Review it if you'd like, then
let me know when to proceed to the expertise assessment (or just say "continue").
```

---

### Step 4: Expertise Assessment

**Goal:** Calibrate the learning depth based on the user's current knowledge.

**Actions:**

1. Ask the user 2-3 questions specific to the workshop subject matter. Derive the questions from the content of the source files — do not use generic or pre-written examples. The questions should probe:
   - Familiarity with the core domain concepts covered in the workshop
   - Prior exposure to the tools, systems, or processes discussed
   - Current role and how it relates to the workshop content

**⚠️ MANDATORY STOPPING POINT**: Do NOT proceed to Step 5 until the user has responded to the expertise questions.

---

### Step 5: Tailored Learning Path Generation

**Goal:** Output the final instructional curriculum.

**Actions:**

1. Synthesize the cleaned source material and the user's expertise level to create a Learning Path with the following structure:
   - **Introduction**: Alignment of the path with the user's role (e.g., Data Engineer).
   - **Curriculum Table**: Columns for Module Number, Title, Objectives, and Estimated Duration.
   - **Detailed Module Breakdown**: For each module, provide key takeaways and Role-Specific Insights (e.g., how the functional logic affects data pipeline design).
   - **Validation**: Three deep-dive questions to test comprehension.

2. Present the completed Learning Path to the user and confirm the workflow is complete:
   ```
   Your tailored Learning Path is ready. Let me know if you'd like to adjust
   the depth, scope, or focus of any module.
   ```

---

## Tools

### Script: clean_base64_images.py

**Description**: Scans Markdown files for inline Base64-encoded images and replaces each one with a human-readable descriptive tag (`[Image description: ...]`) inferred from the image's alt text, the nearest preceding section heading, and the surrounding paragraph. Uses Python stdlib only — no external dependencies.

**Usage** (replace `<SKILL_DIR>` with the absolute path to this skill's directory):
```bash
# Single Notes file, write cleaned output alongside source
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/clean_base64_images.py file_notes.md

# Single Notes file, specify output path
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/clean_base64_images.py file_notes.md --output cleaned.md

# Overwrite Notes source in place
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/clean_base64_images.py file_notes.md --inplace

# Multiple Notes files (each gets a _cleaned.md sibling)
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/clean_base64_images.py a_notes.md b_notes.md c_notes.md
```

**Arguments:**
- `files` (positional, required): One or more Markdown file paths to process
- `--output PATH`: Write cleaned output to a specific path (single input file only)
- `--inplace`: Overwrite each input file in place

**Output**: Cleaned Markdown file(s) with Base64 images replaced by `[Image description: ...]` tags. Prints a summary of replacements to stdout.

**When to use:** Always run in Step 2 on Notes files only, before any analysis or file generation.
**When NOT to use:** Do not run on Transcription files, already-cleaned files, or non-Markdown files.

---

## Constraints

- **File types**: Only files matching `*_transcription.md` or `*_notes.md` are valid inputs. Warn the user if other files are provided.
- **Minimum input**: Do not begin analysis without at least one Transcription file and one Notes file.
- **Script scope**: Run `clean_base64_images.py` on Notes files only. Never pass Transcription files to the script.
- **Timecode cross-referencing**: When enriching Notes content with Transcription dialogue, match on timecodes within the same session pair (`{nn}_{workshop-name}`). Do not cross sessions.
- **File creation**: Use the available environment tools to write `SUMMARY.md` to the confirmed target directory.
- **No emojis**: Use standard Markdown headers and bullet points. Do not use any icons or emojis in responses or generated files.
- **Noise filtering**: When processing transcripts, ignore filler words and administrative digressions to focus strictly on functional and technical value.
- **Use cleaned content**: All analysis (SUMMARY.md, Learning Path) must be based on the cleaned Notes files (or original Notes files if no images were found) and the original Transcription files.

## Stopping Points

- ✋ Step 1: Wait for valid source files (at least one Transcription + one Notes) before any analysis
- ✋ Step 3: Optional — invite user to review `SUMMARY.md` before proceeding
- ✋ Step 4: Wait for user expertise responses before generating the learning path

## Output

- `SUMMARY.md`: Synthetic technical summary written to the user's project directory
- Learning Path document: Tailored curriculum with modules, objectives, durations, and validation questions
