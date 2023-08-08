import glob
import os
from datetime import datetime
from pathlib import Path

from obsidian_scripts.logger import get_logger

log = get_logger("NOTEBOOK")


def get_notebook_plots(path):
    """
    get all the plots generated as seperate pngs
    :param path:
    :return:
    """
    plot_files = glob.glob(path + "/*.png")
    paired = []
    for pf in plot_files:
        name = Path(pf).stem
        spl = name.split("_")
        paired.append([pf, int(spl[-2])])
    paired.sort(key=lambda x: x[1])
    return [x[0] for x in paired]


def generate_default_metadata(npath):
    c_time = os.stat(npath).st_birthtime
    dt_c = datetime.fromtimestamp(c_time)
    date = dt_c.strftime("%Y-%m-%d")
    metadata = {
        "date"           : date,
        "year"           : dt_c.year,
        "week"           : dt_c.strftime('%Y-%U'),
        "type"           : "notebook",
        "notebook-path"  : npath,
        "project"        : "",
        "constructs"     : [],
        "experiments"    : [],
        "sequencing-runs": [],
        "status"         : "",
    }
    return metadata


def extract_meta_data_from_notebook_cell(content):
    text = "".join(content)
    sections = text.split("##")
    metadata_section = ""
    for s in sections:
        if s.startswith(" metadata\n"):
            metadata_section = s
            sections.remove(s)
            log.info("found METADATA section")
            break
    if len(metadata_section) == 0:
        log.info("no METADATA section found")
    lines = metadata_section.split("\n")
    metadata = {}
    for line in lines:
        if not line.startswith('-'):
            continue
        line = line[2:]
        key, value = line.split(":")
        key = key.strip()
        value = value.strip()
        metadata[key] = value
    text = "##".join(sections)
    new_content = [line + "\n" for line in text.split("\n")]
    return metadata, new_content


class NotebookDeposit:
    def __init__(self):
        pass

    def run(self, nb_path, target_path):
        pass
