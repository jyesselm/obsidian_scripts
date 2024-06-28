import click
import os
import glob
import datetime
import json
from pathlib import Path
import pandas as pd
from tabulate import tabulate
import pyperclip

from obsidian_scripts.logger import get_logger, setup_applevel_logger
from obsidian_scripts.markdown import (
    get_metadata_str,
    extract_metadata,
    add_dates_to_metadata,
)
from obsidian_scripts.construct_note import ConstructNote
from obsidian_scripts.dir_note import DirectoryNote
from obsidian_scripts.sequencing_run_note import SequencingRunNote
from obsidian_scripts.parameters import get_parameters
from obsidian_scripts.paths import LIB_DIR
from obsidian_scripts.markdown import extract_markdown_section

from gsheets.sheet import get_sequence_sheet, get_primer_assembly_sheet

log = get_logger("CLI")


def generate_daily_note(dir_path, date):
    txt = ""
    metadata = {
        "type": "daily",
        "tags": "#daily",
    }
    add_dates_to_metadata(metadata, date)
    txt += get_metadata_str(metadata) + "\n"
    yesterday = (date - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow = (date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    txt += f"<< [[{yesterday}]] | [[{tomorrow}]] >>\n\n"
    txt += f"# {date.strftime('%Y-%m-%d')}\n\n"
    txt += f"## reminders\n\n\n"
    txt += f"## things on my mind\n\n"
    f = open(dir_path + date.strftime("%Y-%m-%d") + ".md", "w")
    f.write(txt)
    f.close()


# multi commmand format
@click.group()
def cli():
    pass


@cli.command()
def add_missing_daily():
    setup_applevel_logger()
    # Define your end date as the current date
    end_date = datetime.date.today()
    # Define your start date as one year before the current date
    start_date = datetime.date(end_date.year, 1, 1)
    # Define your directory path
    cur_year = datetime.date.today().year
    dir_path = f"/Users/jyesselman2/Dropbox/notes/daily/{cur_year}/daily/"
    # Iterate from start_date to end_date
    delta = datetime.timedelta(days=1)
    while start_date < end_date:
        start_date += delta
        date_str = start_date.strftime("%Y-%m-%d")
        file_path = dir_path + date_str + ".md"
        if os.path.exists(file_path):
            continue
        print(f"Adding {date_str}")
        generate_daily_note(dir_path, start_date)
        # Move to next day


@cli.command()
def deposit_notebook():
    pass


@cli.command()
@click.argument("path")
def deposit_dir(path):
    dn = DirectoryNote(path)
    dn.write_note()


@cli.command()
def rebuild_dirs():
    pass


@cli.command()
def generate_dir_json():
    setup_applevel_logger()
    params = get_parameters()
    dirs_path = params["paths"]["dirs"]
    construct_design_dirs = glob.glob(dirs_path + "/construct-design/*.md")
    dirs = {}
    for f in construct_design_dirs:
        dir_name = os.path.basename(f).replace(".md", "")
        metadata = extract_metadata(f)
        dirs[dir_name] = metadata
    with open(LIB_DIR + "/resources/construct-design-dirs.json", "w") as f:
        json.dump(dirs, f, indent=2)


# have this update everything?
@cli.command()
def update():
    pass


@cli.command()
def update_construct_notes():
    setup_applevel_logger()
    params = get_parameters()
    dir_path = params["paths"]["constructs"]
    df_seq = get_sequence_sheet()
    df_pa = get_primer_assembly_sheet()
    for i, row in df_seq.iterrows():
        cn = ConstructNote(dir_path, row, df_pa)
        cn.write_note()


@cli.command()
def update_dir_notes():
    pass


@cli.command()
def update_sequence_run_notes():
    setup_applevel_logger()
    params = get_parameters()
    data_path = params["paths"]["sequencing-run-data"]
    data_dirs = glob.glob(f"{data_path}/*")
    data_dirs.sort()
    skip = [
        "2020_10_06_sequencing_minittr_org_no_mg",
        "2020_07_15_sequencing_pepper_rna_org_minittr",
        "2020_10_19_mttr6_buf_and_dms_titrations",
        "2020_11_01_rre_locks_hairpin_tests",
        "2020_11_02_RRE_locks_rerun",
        "2020_11_07_ires_minittrs",
        "2020_11_22_ires_minittrs_3_org_minittr",
        "2021_04_13_mttr-6-alt-h1_sequencing",
        "2021_04_16_org_minittr_fixed_sequencing",
        "2021_11_18_C001I_seq",
    ]
    for dd in data_dirs:
        if os.path.basename(dd) in skip:
            continue
        print(os.path.basename(dd))
        srn = SequencingRunNote(dd)
        srn.write_note()


@cli.command()
@click.argument("days")
def collect_tasks(days):
    setup_applevel_logger()
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=int(days))
    params = get_parameters()
    cur_year = datetime.date.today().year
    dir_path = f"/Users/jyesselman2/Dropbox/notes/daily/"
    all_daily_files = glob.glob(f"{dir_path}/*/daily/*.md")
    # create dictionary with the data to file path
    daily_files = {}
    for f in all_daily_files:
        date_str = os.path.basename(f).replace(".md", "")
        daily_files[date_str] = f
    final_path = f"/Users/jyesselman2/Dropbox/notes/todo/summary.md"
    f = open(final_path, "w")
    f.write(
        f"# Tasks from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n\n"
    )
    for i in range(int(days)):
        date = start_date + datetime.timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        fpath = daily_files[date_str]
        txt = extract_markdown_section(fpath, "## reminders")
        lines = txt.split("\n")
        task_lines = []
        new_lines = []
        in_reminders_section = False
        for line in lines:
            if line.startswith("## reminders"):
                in_reminders_section = True
                new_lines.append(line)
                continue
            if in_reminders_section and line.startswith("##"):
                in_reminders_section = False
            if in_reminders_section and line.startswith("- [ ]"):
                task_lines.append(line)
            elif not in_reminders_section or not line.startswith("- [ ]"):
                new_lines.append(line)
        if len(task_lines) == 0:
            continue
        f.write(f"## {date_str}\n\n")
        for line in task_lines:
            f.write(line + "\n")
        # Write the updated content back to the file
        with open(fpath, "w") as daily_file:
            daily_file.write("\n".join(new_lines))


@cli.command()
@click.argument("title")
@click.option("-t", "--tags", help="The tags for the snippet", default="")
@click.option("-l", "--language", help="The language of the code", default="python")
@click.option("--file", help="The file to read the code from", default=None)
@click.option("-k", "--keywords", help="The keywords for the snippet", default="")
def snippet(title, tags, language, file, keywords):
    setup_applevel_logger()
    if file is None:
        log.info("Reading from clipboard")
        text = pyperclip.paste()
    else:
        with open(file, "r") as f:
            text = f.read()
    metadata = {
        "type": "snippet",
        "tags": ["snippet"],
        "language": language,
        "keywords": [],
    }
    if len(tags) > 0:
        tags = tags.split(",")
        tags = [f"#{t}" for t in tags]
        metadata["tags"].append(tags)
    if len(keywords) > 0:
        keywords = keywords.split(",")
        metadata["keywords"] = keywords
    metadata = add_dates_to_metadata(metadata, datetime.datetime.now())
    metadata_txt = get_metadata_str(metadata)
    path = f"/Users/jyesselman2/Dropbox/notes/capture/snippets/{language}/{title}.md"
    txt = metadata_txt + "\n" + "# " + title + f"\n\n```{language}\n" + text + "\n```"
    with open(path, "w") as f:
        f.write(txt)
    log.info(f"Snippet saved to {path}")
    log.info(f"Metadata: {metadata}")
    log.info(f"Text: {text}")


if __name__ == "__main__":
    cli()
