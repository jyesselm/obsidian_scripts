import pandas as pd
import sys
import os
import click
import tabulate
import glob
import shutil
import datetime
from pathlib import Path
from dataclasses import dataclass

from obsidian_scripts.logger import setup_applevel_logger, get_logger
from obsidian_scripts.util import get_plot_count


@dataclass
class Pathes:
    target: str
    run: str


# CHECK INPUT #################################################################


def check_valid_dir(dir):
    log = get_logger("MAIN")
    if not os.path.isdir(dir):
        log.error(f"{dir} is not a valid directory")
        exit()
    if not os.path.isfile(f"{dir}/data.csv"):
        log.error(
                "directory must contain data.csv which is a summary of all run data"
        )
        exit()


def get_pathes(dir, test):
    log = get_logger("MAIN")
    if os.getenv("DROPBOX") is None:
        log.error(
                "$DROPBOX is NOT SET please set this path to where dropbox is"
        )
        exit()
    dropbox_path = os.getenv("DROPBOX")
    if not test:
        target_path = f"{dropbox_path}/notes/capture/sequencing_runs/"
    else:
        target_path = os.path.abspath(os.curdir)
    return Pathes(target_path, dir)


# MAIN FUNCS ##################################################################

def write_meta_data(name, df, f):
    # write meta data
    year, month, day = [int(x) for x in name.split("_")[0:3]]
    date = "-".join(name.split("_")[0:3])
    week = datetime.date(year, month, day).isocalendar()[1]
    constructs = " ".join(list(df['code'].unique()))
    f.write(f"---\n")
    f.write(f"date: {date}\n")
    f.write(f"year: {year}\n")
    f.write(f"week: {year}-{week}\n")
    f.write(f"type: sequencing-run\n")
    f.write(f"constructs: [{constructs}]\n")
    f.write(f"---\n\n")


def write_summary(name, df, f):
    f.write(f"## {name}\n")
    f.write(f"DIR = $DROPBOX/data/sequencing_analysis/{name}\n\n")
    df_sub = pd.DataFrame(
            df[["construct", "code", "barcode", "barcode_seq", "data_type"]]
    )
    df_sub["construct"] = [f"[[#{c}]]" for c in df_sub["construct"]]
    f.write(
            tabulate.tabulate(
                    df_sub, headers="keys", tablefmt="github", showindex=True
            )
            + "\n\n"
    )


def write_construct_infomation(pathes, df, f):
    target_path = pathes.target
    attach_path = f"{target_path}/attachments/"
    os.makedirs(attach_path, exist_ok=True)
    pc = get_plot_count(attach_path)
    for i, row in df.iterrows():
        f.write(f"## {row['construct']}\n")
        dir_name = row["construct"] + "_" + row["code"] + "_" + row["data_type"]
        summary_csv = f"{pathes.run}/processed/{dir_name}/output/BitVector_Files/summary.csv"
        org_path = f"{pathes.run}/processed/{dir_name}/output/BitVector_Files/"
        df_sum = pd.read_csv(summary_csv)
        f.write(
                tabulate.tabulate(
                        df_sum, headers="keys", tablefmt="github", showindex=True
                )
                + "\n\n"
        )
        for j, row2 in df_sum.iterrows():
            org_plot_path = glob.glob(f"{org_path}/{row2['name']}_*.png")[0]
            shutil.copy(org_plot_path, f"{attach_path}/{pc}.png")
            f.write(f"![png](attachments/{pc}.png)")
            pc += 1
        f.write("\n\n")


def format(dir, test=False):
    # setup
    check_valid_dir(dir)
    pathes = get_pathes(dir, test)
    # log initial info
    log = get_logger("MAIN")
    log.info(f"converting path {dir} to sequencing note")
    name = dir.split("/")[-1]
    log.info(f"sequencing run is named: {name}")
    df = pd.read_csv(f"{dir}/data.csv")
    log.info(f"{name} contains {len(df)} constructs")
    f = open(f"{pathes.target}/{name}.md", "w")
    write_meta_data(name, df, f)
    write_summary(name, df, f)
    write_construct_infomation(pathes, df, f)
    f.write("## tags\n")
    f.write(f"#source\n")
    f.close()


@click.command()
@click.argument("dir")
@click.option("-t", "--test", is_flag=True)
def main(dir, test):
    setup_applevel_logger()
    format(dir, test)


if __name__ == "__main__":
    main()
