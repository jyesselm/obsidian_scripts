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
from obsidian_scripts.dir_note import DirectoryNote

from gsheets.sheet import get_sequence_sheet, get_primer_assembly_sheet

log = get_logger("CLI")


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
    dn = DirectoryNote(path)
    dn.write_note()


@cli.command()
def rebuild_dirs():
    pass


if __name__ == "__main__":
    cli()
