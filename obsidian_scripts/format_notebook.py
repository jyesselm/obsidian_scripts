import pandas as pd
import shutil
import os
import click
import datetime
import glob
from datetime import datetime
from pathlib import Path

from obsidian_scripts.logger import setup_applevel_logger, get_logger
from obsidian_scripts.util import get_plot_count
from obsidian_scripts.markdown import *


def get_notebook_plots(path):
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
        "constructs"     : "[]",
        "experiments"    : "[]",
        "sequencing-runs": "[]",
        "status"         : "",
    }
    return metadata


def write_metadata(metadata, f):
    # write meta data
    keys = "date,year,week,type,project,constructs".split(",")
    keys += "experiments,sequencing-runs".split(",")
    f.write(f"---\n")
    for k in keys:
        f.write(f"{k}: {metadata[k]}\n")
    # get remaining keys I don't know about now
    for k, v in metadata.items():
        if k in keys:
            continue
        f.write(f"{k}: {v}\n")
    f.write(f"---\n\n")


def extract_meta_data_from_notebook_cell(content):
    text = "".join(content)
    sections = text.split("##")
    log = get_logger("MAIN")
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
    for l in lines:
        if not l.startswith('-'):
            continue
        l = l[2:]
        key, value = l.split(":")
        key = key.strip()
        value = value.strip()
        metadata[key] = value
    text = "##".join(sections)
    new_content = [l + "\n" for l in text.split("\n")]
    return metadata, new_content


def get_merged_meta_data(default, cur, notebook):
    metadata = default.copy()
    for k, v in notebook.items():
        metadata[k] = notebook[k]
    for k, v in cur.items():
        metadata[k] = cur[k]
    return metadata


def format_notebook(npath, target):
    # setup
    setup_applevel_logger()
    log = get_logger("MAIN")
    # make sure we are dealing in absolute paths
    npath = os.path.abspath(npath)
    target = os.path.abspath(target)
    name = Path(npath).stem
    os.system(f"jupyter nbconvert --to markdown {npath} > /dev/null")
    plot_path = f"{Path(npath).parent}/{name}_files"
    os.system(f"mogrify -background white -flatten {plot_path}/*.png")
    attach_path = f"{target}/attachments/"
    os.makedirs(attach_path, exist_ok=True)
    cur_metadata = {}
    if os.path.isfile(f"{target}/{name}.md"):
        log.info(
                "MD file already exists! Hopefully we are updating it so reading "
                "metadata")
        cur_metadata = extract_metadata_from_md_file(f"{target}/{name}.md")
        os.remove(f"{target}/{name}.md")
    try:
        shutil.move(f"{Path(npath).parent}/{name}.md", target)
    except:
        pass
    f = open(f"{target}/{name}.md", "r")
    content = f.readlines()
    f.close()
    notebook_metadata, content = extract_meta_data_from_notebook_cell(content)
    default_metadata = generate_default_metadata(npath)
    metadata = get_merged_meta_data(
            default_metadata, cur_metadata, notebook_metadata)
    # update image paths
    plot_pathes = get_notebook_plots(plot_path)
    pc = get_plot_count(attach_path)
    pi = 0
    for i, line in enumerate(content):
        if not content[i].startswith("![png]"):
            continue
        content[i] = f"![png](attachments/{pc}.png)"
        shutil.copy(plot_pathes[pi], f"attachments/{pc}.png")
        pi += 1
        pc += 1
    # remove extra spaces
    new_content = []
    for i in range(0, len(content) - 1):
        if len(content[i]) < 2 and len(content[i + 1]) < 2:
            continue
        new_content.append(content[i])
    new_content.append(content.pop())
    shutil.rmtree(plot_path)
    f = open(f"{target}/{name}.md", "w")
    write_metadata(metadata, f)
    f.writelines(new_content)
    f.write(f"\n#notebook\n")
    f.close()


@click.command()
@click.argument("npath")
@click.option("-t", "--target", default=".")
def main(npath, target):
    format_notebook(npath, target)


if __name__ == "__main__":
    main()
