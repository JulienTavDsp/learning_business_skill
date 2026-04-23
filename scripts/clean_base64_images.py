#!/usr/bin/env python3
"""
clean_base64_images.py - Replace Base64-encoded images in Markdown files with descriptive tags.

For each inline Base64 image found (e.g. ![alt](data:image/png;base64,...)), the script
infers a human-readable description from the alt text, the nearest preceding heading, and
the surrounding paragraph, then replaces the image with:

    [Image description: <inferred description>]

Usage:
    # Default: writes <stem>_cleaned.md alongside the source file
    uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/clean_base64_images.py file.md

    # Write to a specific output file (single input only)
    uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/clean_base64_images.py file.md --output cleaned.md

    # Overwrite the source file in place
    uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/clean_base64_images.py file.md --inplace

    # Process multiple files (each gets a _cleaned.md sibling)
    uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/clean_base64_images.py a.md b.md c.md
"""

import argparse
import re
import sys
from pathlib import Path

# Matches: ![alt text](data:image/TYPE;base64,BASE64DATA)
# Handles multi-line base64 blobs with re.DOTALL.
_BASE64_IMG_RE = re.compile(
    r'!\[([^\]]*)\]\(data:image/[^;]+;base64,[A-Za-z0-9+/=\s]+\)',
    re.DOTALL,
)

# Matches ATX headings: ## Heading Text
_HEADING_RE = re.compile(r'^#{1,6}\s+(.+)$', re.MULTILINE)


def _nearest_heading(text_before: str) -> str | None:
    """Return the text of the last heading that appears before the image."""
    matches = _HEADING_RE.findall(text_before)
    return matches[-1].strip() if matches else None


def _preceding_snippet(text_before: str, max_chars: int = 150) -> str | None:
    """Return the last non-empty line before the image (trimmed to max_chars)."""
    lines = [ln.strip() for ln in text_before[-max_chars * 2:].splitlines() if ln.strip()]
    if not lines:
        return None
    snippet = lines[-1][:max_chars]
    # Skip lines that are just heading markers or horizontal rules
    if re.fullmatch(r'#{1,6}.*|[-*_]{3,}', snippet):
        return lines[-2][:max_chars] if len(lines) >= 2 else None
    return snippet


def _build_description(alt: str, heading: str | None, snippet: str | None) -> str:
    """Compose the descriptive tag from available context parts."""
    parts: list[str] = []
    if alt and alt.strip():
        parts.append(alt.strip())
    if heading:
        parts.append(f"in section '{heading}'")
    if snippet and snippet != alt.strip():
        parts.append(f"related to: {snippet}")
    body = ', '.join(parts) if parts else 'image content not available'
    return f'[Image description: {body}]'


def clean_content(content: str) -> tuple[str, list[dict]]:
    """
    Replace all Base64 images in *content* with descriptive tags.

    Returns:
        cleaned   - the modified string
        log       - list of dicts with keys: position, alt, description
    """
    log: list[dict] = []

    def _replacer(m: re.Match) -> str:
        alt = m.group(1)
        before = content[: m.start()]
        heading = _nearest_heading(before)
        snippet = _preceding_snippet(before)
        description = _build_description(alt, heading, snippet)
        log.append({'position': m.start(), 'alt': alt, 'description': description})
        return description

    cleaned = _BASE64_IMG_RE.sub(_replacer, content)
    return cleaned, log


def _resolve_output(source: Path, output_arg: str | None, inplace: bool) -> Path:
    if output_arg:
        return Path(output_arg)
    if inplace:
        return source
    return source.with_name(source.stem + '_cleaned' + source.suffix)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Replace Base64-encoded images in Markdown files with descriptive tags.'
    )
    parser.add_argument('files', nargs='+', help='Markdown file(s) to process')
    parser.add_argument(
        '--output',
        metavar='PATH',
        help='Output file path (only valid when processing a single input file)',
    )
    parser.add_argument(
        '--inplace',
        action='store_true',
        help='Overwrite each input file in place',
    )
    args = parser.parse_args()

    if args.output and len(args.files) > 1:
        print('ERROR: --output can only be used with a single input file.', file=sys.stderr)
        sys.exit(1)

    any_error = False
    for file_str in args.files:
        source = Path(file_str)
        if not source.exists():
            print(f'ERROR: File not found: {source}', file=sys.stderr)
            any_error = True
            continue

        content = source.read_text(encoding='utf-8')
        cleaned, log = clean_content(content)

        if not log:
            print(f'{source}: No Base64 images found. No output written.')
            continue

        out_path = _resolve_output(source, args.output, args.inplace)
        out_path.write_text(cleaned, encoding='utf-8')

        print(f'{source}: Replaced {len(log)} Base64 image(s) -> {out_path}')
        for entry in log:
            print(f'  {entry["description"]}')

    if any_error:
        sys.exit(1)


if __name__ == '__main__':
    main()
