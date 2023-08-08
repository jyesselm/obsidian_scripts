import click
import os
import glob
import datetime
import json
from pathlib import Path
import pandas as pd
from tabulate import tabulate

from obsidian_scripts.logger import get_logger
from obsidian_scripts.markdown import get_metadata_str
from obsidian_scripts.construct_note import ConstructNote

from gsheets.sheet import get_sequence_sheet, get_primer_assembly_sheet

log = get_logger("CLI")

NOTES_PATH = "/Users/jyesselman2/Dropbox/notes/"


def generate_daily_note(dir_path, date):
    txt = ""
    metadata = {
        "date": date,
        "type": "daily",
    }
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


def get_protocol_run_files():
    path = "/Users/jyesselman2/gdrive/protocol_runs"
    protcol_run_files = glob.glob(f"{path}/*/*.gsheet")
    return protcol_run_files


# multi commmand format
@click.group()
def cli():
    pass


@cli.command()
def add_missing_daily():
    # Define your end date as the current date
    end_date = datetime.date.today()
    # Define your start date as one year before the current date
    start_date = datetime.date(end_date.year, 1, 1)
    # Define your directory path
    dir_path = "/Users/jyesselman2/Dropbox/notes/daily/2023/daily/"
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
def update_construct_notes():
    dir_path = "/Users/jyesselman2/Dropbox/notes/capture/construct/"
    df_seq = get_sequence_sheet()
    df_pa = get_primer_assembly_sheet()
    for i, row in df_seq.iterrows():
        cn = ConstructNote(dir_path, row, df_pa)
        txt = cn.generate_text()

        break


@cli.command()
def deposit_notebook():
    pass


@cli.command()
@click.argument("path")
def deposit_dir(path):
    path = os.path.abspath(path)
    save_path = path.replace("/Users/jyesselman2/Dropbox", "$DROPBOX")
    dir_name = os.path.basename(path)
    date_str = "-".join(dir_name.split("_")[0:3])
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    metadata = {
        "date": date,
        "type": "dir",
        "path": save_path,
        "dir-type": "unclassified",
        "dir-designed-by": "Joe Yesselman",
        "dir-summary": "",
        "dir-keywords": "",
        "project": "",
    }
    if "construct_design" in path:
        metadata["dir-type"] = "construct-design"
    elif "analysis" in path:
        metadata["dir-type"] = "analysis"
    elif "paper" in path:
        metadata["dir-type"] = "paper"
    constructs = []
    construct_codes = []
    construct_links = []
    if os.path.isdir(f"{path}/seq-deposit-output"):
        df_constructs = pd.read_csv(f"{path}/seq-deposit-output/constructs.csv")
        for i, row in df_constructs.iterrows():
            constructs.append(row["name"])
            construct_codes.append(row["code"])
            construct_links.append(f"{row['code']}--{row['name']}")
    metadata["dir-constructs-codes"] = "[" + " ".join(construct_codes) + "]"
    metadata["dir-constructs"] = "[" + " ".join(constructs) + "]"
    txt = get_metadata_str(metadata)
    txt += f"# {dir_name}\n\n"
    txt += f"## notes\n\n"
    if os.path.isfile(f"{path}/scripts/setup.py"):
        txt += f"## setup script\n\n"
        f = open(f"{path}/scripts/setup.py")
        script_lines = f.readlines()
        f.close()
        txt += f"```python\n{''.join(script_lines)}\n```\n\n"
    if len(construct_links) > 0:
        txt += f"## constructs \n\n"
        for cl in construct_links:
            txt += f"[[{cl}]]\n"
        txt += "\n\n"
    if os.path.isfile(f"{path}/seq-deposit-output/primers.csv"):
        txt += f"## primers \n\n"
        df_primers = pd.read_csv(f"{path}/seq-deposit-output/primers.csv")
        txt += tabulate(df_primers, headers="keys", tablefmt="github")
        txt += "\n\n"
        txt += f"## assemblies \n\n"
        df_assembly = pd.read_csv(f"{path}/seq-deposit-output/assemblies.csv")
        txt += tabulate(df_assembly, headers="keys", tablefmt="github")
        txt += "\n\n"
    protocol_run_files = get_protocol_run_files()
    current_runs = []
    for r_file in protocol_run_files:
        for code in construct_codes:
            if r_file.find(code) != -1:
                if r_file not in current_runs:
                    current_runs.append(r_file)
    gsheet_path = "https://docs.google.com/spreadsheets/d"
    if len(current_runs) > 0:
        txt += "## protocol runs\n\n"
    for run in current_runs:
        run_name = os.path.basename(run)
        run_info = json.load(open(run))
        txt += f"<a href={gsheet_path}/{run_info['doc_id']}>{run_name}</a>\n"
    f = open(f"{NOTES_PATH}/dirs/{metadata['dir-type']}/{dir_name}.md", "w")
    f.write(txt)
    f.close()


if __name__ == "__main__":
    cli()
