from pathlib import Path
from obsidian_scripts.logger import get_logger
import re

log = get_logger("MARKDOWN")


def extract_metadata(path):
    """
    collects metadata from markdown file.
    :param path:
    :return: dictionary of metadata tags
    """
    if not Path(path).exists():
        raise ValueError(f"{path} is not a valid path")
    with open(path, "r", encoding="utf8") as f:
        lines = f.readlines()
    text = "".join(lines)
    sections = text.split("---")
    # no meta data found
    if len(sections) < 2:
        return {}
    lines = sections[1].split("\n")
    metadata = {}
    for line in lines:
        spl = line.split(":")
        if len(spl) == 1 and len(spl[0]) == 0:
            continue
        key, value = spl
        key = key.strip()
        value = value.strip()
        if value.find("[") == -1:
            metadata[key] = value
        else:
            value = value[1:-1]
            metadata[key] = value.split()
    return metadata


def merge_metadatas(org_metadata, new_metadata):
    merged = org_metadata.copy()
    for k, v in new_metadata.items():
        if k in merged:
            continue
        merged[k] = v
    return merged


def parse_markdown_file(path):
    """
    parses a markdown file and returns the content
    :param path:
    :return:
    """


def add_dates_to_metadata(metadata, date):
    metadata["date"] = date.strftime("%Y-%m-%d")
    metadata["year"] = date.strftime("%Y")
    metadata["week"] = metadata["year"] + "-" + str(int(date.strftime("%U")) + 1)
    return metadata


def get_metadata_str(metadata):
    """
    generates the metadata string for a markdown file
    :param metadata: dictionary of metadata
    :return: string of metadata
    """
    txt = ""
    txt += f"---\n"
    txt += f"date: {metadata['date']}\n"
    txt += f"year: {metadata['year']}\n"
    txt += f"week: {metadata['week']}\n"
    if "type" in metadata:
        txt += f"type: {metadata['type']}\n"
    seen_keys = ["date", "year", "week", "type"]
    for key, value in metadata.items():
        if key in seen_keys:
            continue
        if isinstance(value, list):
            value = "[" + " ".join(value) + "]"
        txt += f"{key}: {value}\n"
    txt += f"---\n"
    return txt


def split_markdown_by_headings(markdown_text):
    # Split the markdown text by headings using a regular expression
    sections = re.split(r"(#+\s+.+\n)", markdown_text)
    start_pos = 0
    while start_pos < len(sections):
        if sections[start_pos].count("#") > 0:
            break
        start_pos += 1

    # Combine the headings with their corresponding content
    combined_sections = []
    i = start_pos
    while i < len(sections) - 1:
        heading = sections[i]
        level = heading.count("#") if heading else None
        if sections[i + 1].count("#") == 0:
            combined_sections.append((level, heading + sections[i + 1]))
            i += 2
        else:
            combined_sections.append((level, heading))
            i += 1

    return combined_sections


def extract_markdown_section(path, section_name):
    """
    gets a section from a markdown file
    :param path:
    :param section_name:
    :return:
    """
    if not Path(path).exists():
        raise ValueError(f"{path} is not a valid path")
    with open(path, "r", encoding="utf8") as f:
        lines = f.readlines()
    text = "".join(lines)
    sections = split_markdown_by_headings(text)
    keep = []
    keep_level = 0
    found = False
    for level, section in sections:
        lines = section.split("\n")
        heading_line = lines[0].strip()
        if heading_line == section_name:
            found = True
            keep_level = level
            keep.append(section)
            continue
        if found and level > keep_level:
            keep.append(section)
        elif found and level <= keep_level:
            break
    return "".join(keep)
