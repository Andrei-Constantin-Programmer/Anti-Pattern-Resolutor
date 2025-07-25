from enum import Enum
import json
from pathlib import Path
import re
import textwrap

from confluence_extractor import MARKDOWN_DIRECTORY
from conversion_exception import ConversionException
from configuration import Settings

class Severity(Enum):
    MINOR = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

NO_CATEGORY = "Uncategorised"
ANY_LANGUAGE = "Any"
DEFAULT_SEVERITY = Severity.MEDIUM

def _clean_markdown(text: str):
    content = re.sub(r'^\*+\s*', '', text)                      # bullet points
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)          # bold
    content = re.sub(r'\*(.*?)\*', r'\1', content)              # italic *
    content = re.sub(r'_(.*?)_', r'\1', content)                # italic _
    content = re.sub(r'\s+', ' ', content.replace('\n', ' '))   # extra spaces & new lines
    return content


def _extract_section(text: str, section_title: str):
    pattern = rf"##\s+[^\n]*{section_title}[^\n]*\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""


def _extract_title(text: str):
    match = re.search(r"#\s+(.+)", text)
    if not match:
        raise ConversionException(f"Missing title")
    return _clean_markdown(match.group(1))


def _bullets_to_string(text):
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("*"):
            continue

        lines.append(_clean_markdown(line))
    return "\n".join(lines)


def _require_section(markdown: str, section: str) -> str:
    content = _extract_section(markdown, section)
    if not content:
        raise ConversionException(f"Missing required section: '{section}'")
    return content


def _prompt_for_metadata(title: str):
    print(f"\nProcessing: {title}")

    category = input(f"  Category [default: {NO_CATEGORY}]: ").strip() or NO_CATEGORY
    language = input(f"  Language [default: {ANY_LANGUAGE}]: ").strip() or ANY_LANGUAGE

    print(f"  Severity options: {', '.join(s.name for s in Severity)}")
    severity_input = input(f"  Severity [default: {DEFAULT_SEVERITY.name}]: ").strip().upper()

    try:
        severity = Severity[severity_input] if severity_input else DEFAULT_SEVERITY
    except KeyError:
        print(f"  Invalid severity '{severity_input}', using default: {DEFAULT_SEVERITY.name}")
        severity = DEFAULT_SEVERITY

    return category, language, severity


def _to_snake_case(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s\-]+", "_", text)
    return text


def convert_markdown_to_json(markdown: str, category: str = NO_CATEGORY, language: str = ANY_LANGUAGE, severity: Severity = DEFAULT_SEVERITY):
    markdown = textwrap.dedent(markdown)

    json_object = {
        "name": _extract_title(markdown),
        "description": _clean_markdown(_require_section(markdown, "Explanation")),
        "category": category,
        "language": language,
        "severity": severity.name,
        "problem": _bullets_to_string(_extract_section(markdown, "Problems")),
        "remediation": _bullets_to_string(_extract_section(markdown, "Possible fixes")),
        "limitation": _bullets_to_string(_extract_section(markdown, "Limitations")),
    }

    return json_object


def convert_markdown_directory(use_default_metadata: bool = False):
    settings = Settings()
    output_dir = Path(settings.output_dir)
    if not output_dir.exists() or not output_dir.is_dir():
        raise ConversionException(f"Invalid output directory: {output_dir}")

    markdown_files = list(MARKDOWN_DIRECTORY.glob("*.md"))

    if not markdown_files:
        print("No markdown files found.")
        return

    for file in markdown_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                markdown = textwrap.dedent(f.read())
                title = _extract_title(markdown)

                if (use_default_metadata):
                    category, language, severity = NO_CATEGORY, ANY_LANGUAGE, DEFAULT_SEVERITY    
                else:
                    category, language, severity = _prompt_for_metadata(title)

                json_obj = convert_markdown_to_json(markdown, category, language, severity)

                file_name = f"{_to_snake_case(title)}.json"
                output_path = output_dir / file_name

                with open(output_path, "w", encoding="utf-8") as out_file:
                    json.dump([json_obj], out_file, indent=2)
            
            print(f"Saved to: {output_path.name}")

        except ConversionException as e:
            print(f"Skipping {file.name}: {e}")
        except Exception as e:
            print(f"Error processing {file.name}: {e}")