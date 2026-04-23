---
name: learning-business-skill
description: "Transform unstructured Markdown source files (meeting transcripts, technical documentation) into a structured Learning Path and a synthetic technical summary tailored to the user's professional profile. Use when: learning path, instructional design, summarize transcript, training curriculum, generate summary, expertise assessment, tailored curriculum, technical onboarding, meeting transcript analysis."
---

# Learning Path Generator

## When to Use

As an expert Instructional Designer and Technical Analyst, use this skill when the user wants to:
- Generate a learning path or training curriculum from source documents
- Summarize meeting transcripts or technical documentation
- Assess expertise and tailor instructional content to a professional profile
- Produce a structured `SUMMARY.md` from unstructured Markdown files

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

**Goal:** Identify and retrieve the source material.

**Actions:**

1. Present the following prompt to the user:
   ```
   Project Initialization: Please provide the Markdown file(s) or specify the
   directory containing the source material (e.g., meeting transcripts). I will
   begin by generating a technical summary before tailoring your learning path.
   ```

2. Wait for the user to provide the Markdown files or point to their location in the workspace.

**⚠️ MANDATORY STOPPING POINT**: Do NOT proceed to Step 2 until the user has provided the source files or their location.

---

### Step 2: Preprocessing — Base64 Image Cleaning

**Goal:** Remove Base64-encoded images from source files to reduce token usage and keep analysis focused on textual content.

**Actions:**

1. Run `clean_base64_images.py` against all source Markdown files in a single invocation:
   ```bash
   uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/clean_base64_images.py <file1.md> <file2.md> ...
   ```
   Replace `<SKILL_DIR>` with the absolute path to this skill's directory. Each file produces a `<stem>_cleaned.md` sibling in the same directory.

   If uv is unavailable, run directly:
   ```bash
   python <SKILL_DIR>/scripts/clean_base64_images.py <file1.md> <file2.md> ...
   ```

2. Report to the user how many images were replaced per file (the script prints this automatically).

3. Use the cleaned output files as the source material for all subsequent steps. Do NOT use the original files.

4. If no Base64 images are found in any file, notify the user and proceed with the original files unchanged.

---

### Step 3: Synthetic Summary and File Generation

**Goal:** Create a high-level technical overview and save it to the project.

**Actions:**

1. Analyze the cleaned source content across three dimensions:
   - **Conceptual** (Business Logic)
   - **Technical** (Systems/Architecture)
   - **Vocabulary** (Glossary of Terms)

2. Ask the user to confirm the target directory for the output file. Default to the current working directory if the user does not specify otherwise.

3. Generate a file named `SUMMARY.md` in the confirmed directory. This file must contain:
   - **Executive Overview**: A high-level summary of the source content.
   - **Conceptual Points**: Key business rules and functional logic.
   - **Technical Points**: Data flows, software architecture details, and system constraints.
   - **Glossary**: Definitions of industry-specific or project-specific terminology.

4. Notify the user that `SUMMARY.md` has been created.

**⚠️ OPTIONAL STOPPING POINT**: Invite the user to review `SUMMARY.md` before continuing:
```
SUMMARY.md has been written to <target_dir>. Review it if you'd like, then
let me know when to proceed to the expertise assessment (or just say "continue").
```

---

### Step 4: Expertise Assessment

**Goal:** Calibrate the learning depth based on the user's current knowledge.

**Actions:**

1. Ask the user 2-3 specific questions regarding their experience with the subject matter. Examples:
   - "What is your current understanding of data aggregation in trading?"
   - "Are you familiar with the specific software architecture mentioned in the documents?"

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

---

## Tools

### Script: clean_base64_images.py

**Description**: Scans Markdown files for inline Base64-encoded images and replaces each one with a human-readable descriptive tag (`[Image description: ...]`) inferred from the image's alt text, the nearest preceding section heading, and the surrounding paragraph. Uses Python stdlib only — no external dependencies.

**Usage:**
```bash
# Single file, write cleaned output alongside source
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/clean_base64_images.py file.md

# Single file, specify output path
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/clean_base64_images.py file.md --output cleaned.md

# Overwrite source in place
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/clean_base64_images.py file.md --inplace

# Multiple files (each gets a _cleaned.md sibling)
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/clean_base64_images.py a.md b.md c.md
```

**Arguments:**
- `files` (positional, required): One or more Markdown file paths to process
- `--output PATH`: Write cleaned output to a specific path (single input file only)
- `--inplace`: Overwrite each input file in place

**Output**: Cleaned Markdown file(s) with Base64 images replaced by `[Image description: ...]` tags. Prints a summary of replacements to stdout.

**When to use:** Always run in Step 2, before any analysis or file generation.
**When NOT to use:** Do not run on already-cleaned files or on non-Markdown files.

---

## Constraints

- **File creation**: Use the available environment tools to write `SUMMARY.md` to the confirmed target directory.
- **No emojis**: Use standard Markdown headers and bullet points. Do not use any icons or emojis in responses or generated files.
- **Noise filtering**: When processing transcripts, ignore filler words and administrative digressions to focus strictly on functional and technical value.
- **Use cleaned content**: All analysis (SUMMARY.md, Learning Path) must be based on the preprocessed files produced in Step 2, not the originals.

## Stopping Points

- ✋ Step 1: Wait for user to provide source files before any analysis
- ✋ Step 3: Optional — invite user to review `SUMMARY.md` before proceeding
- ✋ Step 4: Wait for user expertise responses before generating the learning path

## Output

- `SUMMARY.md`: Synthetic technical summary written to the user's project directory
- Learning Path document: Tailored curriculum with modules, objectives, durations, and validation questions
