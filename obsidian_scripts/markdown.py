from pathlib import Path
from obsidian_scripts.logger import get_logger

log = get_logger("MARKDOWN")


def extract_meta_data(path):
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


def parse_markdown_file(path):
    """
    parses a markdown file and returns the content
    :param path:
    :return:
    """


def get_metadata_str(metadata):
    """
    generates the metadata string for a markdown file
    :param metadata: dictionary of metadata
    :return: string of metadata
    """
    txt = ""
    date = metadata["date"].strftime("%Y-%m-%d")
    year = metadata["date"].strftime("%Y")
    week = str(int(metadata["date"].strftime("%U")) + 1)
    txt += f"---\n"
    txt += f"date: {date}\n"
    txt += f"year: {year}\n"
    txt += f"week: {year}-{week}\n"
    if "type" in metadata:
        txt += f"type: {metadata['type']}\n"
    del metadata["date"]
    del metadata["type"]
    for key, value in metadata.items():
        if isinstance(value, list):
            value = "[" + " ".join(value) + "]"
        txt += f"{key}: {value}\n"
    txt += f"---\n"
    return txt
