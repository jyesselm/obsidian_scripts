import os
import glob
import datetime
import json
import pandas as pd
import shutil
from tabulate import tabulate
from pathlib import Path

from obsidian_scripts.logger import get_logger
from obsidian_scripts.paths import DROPBOX_PATH
from obsidian_scripts.parameters import get_parameters
from obsidian_scripts.markdown import (
    get_metadata_str,
    add_dates_to_metadata,
    extract_markdown_section,
    extract_metadata,
    merge_metadatas,
)

log = get_logger("SEQUENCING-RUN-NOTE")

people = {
    "SJ": "Sakshi Jain",
    "RN": "Riley Nigh",
    "RG": "Ricardo Gil",
    "JA": "Jay Aposhian",
    "CG": "Cristian Gonzalez",
    "BL": "Bret Lange",
    "BS": "Beaut Stearns",
    "AO": "Alabi Obadeji John",
    "SM": "Skylar Mosby",
    "SB": "Sarah Brady",
    "KN": "Kaitlyn Nein",
    "DA": "Darren Armstrong",
    "JDY": "Joe Yesselman",
}


def get_protocol_run_files():
    path = "/Users/jyesselman2/gdrive/protocol_runs"
    protcol_run_files = glob.glob(f"{path}/*/*.gsheet") + glob.glob(
        f"{path}/archive/*/*.gsheet"
    )
    return protcol_run_files


def get_protocol_sheet_link(protocol_file_path):
    gsheet_path = "https://docs.google.com/spreadsheets/d"
    run_name = os.path.basename(protocol_file_path).split(".")[0]
    run_info = json.load(open(protocol_file_path))
    return f"<a href={gsheet_path}/{run_info['doc_id']}>{run_name}</a>"


def get_plot_count(path):
    pngs = glob.glob(f"{path}*.png")
    num = -1
    for png in pngs:
        fname = Path(png).stem
        c_num = int(fname)
        if c_num > num:
            num = c_num
    return num + 1


class SequencingRunNote:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.save_path = self.path.replace(DROPBOX_PATH, "$DROPBOX")
        self.dir_name = os.path.basename(self.path)

    def write_note(self):
        params = get_parameters()
        # note probably want to start taking this from the sequencing run sheets instead
        df_data = pd.read_csv(f"{self.path}/data.csv")
        write_path = params["paths"]["sequencing-runs"] + "/" + self.dir_name + ".md"
        metadata = self.__generate_metadata(df_data)
        notes = "## notes\n\n"
        if os.path.exists(write_path):
            log.info(f"Note already exists for {self.dir_name}")
            old_metadata = extract_metadata(write_path)
            metadata = merge_metadatas(old_metadata, metadata)
            # overwrite the path in case files got moved
            notes = extract_markdown_section(write_path, "## notes")
        attach_path = params["paths"]["sequencing-runs"] + "/entries/attachments/"
        entry_txt, df_data = self.__generate_entry_txt(attach_path, df_data)
        txt = get_metadata_str(metadata)
        txt += f"# {self.dir_name}\n\n"
        txt += notes
        txt += "## summary\n\n"
        txt += f"[data directory link](file:///{self.path})\n"
        txt += self.__get_link_to_sequencing_run_gsheet() + "\n\n"
        txt += self.__generate_summary_txt(df_data)
        txt += entry_txt
        f = open(write_path, "w")
        f.write(txt)
        f.close()

    def __generate_metadata(self, df_data):
        date_str = "-".join(self.dir_name.split("_")[0:3])
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        metadata = {
            "type": "sequencing-run",
            "path": self.save_path,
            "run-usuable": "YES",
            "run-type": "ISEQ",
            "run-where": "LAB",
            "run-construct-codes": list(df_data["code"].unique()),
            "projects": [],
        }
        if self.dir_name.find("KU") != -1:
            metadata["run-type"] = "NOVASEQ"
            metadata["run-where"] = "KU"
        metadata = add_dates_to_metadata(metadata, date)
        return metadata

    def __get_link_to_sequencing_run_gsheet(self):
        gsheet_path = "https://docs.google.com/spreadsheets/d"
        protocol_runs = get_protocol_run_files()
        for pf in protocol_runs:
            name = os.path.basename(pf).split(".")[0]
            if name == self.dir_name:
                run_info = json.load(open(pf))
                return (
                    f"<a href={gsheet_path}/{run_info['doc_id']}>sequencing gsheet</a>"
                )
        return ""

    def __generate_summary_txt(self, df_data):
        df_sub = df_data[
            ["note_name", "construct", "code", "data_type", "exp_type"]
        ].copy()
        df_sub["note_name"] = [f"[[{c}]]" for c in df_sub["note_name"]]
        return (
            tabulate(df_sub, headers="keys", tablefmt="github", showindex=True) + "\n\n"
        )

    def __generate_entry_txt(self, attach_path, df_data):
        txt = ""
        date_str = "-".join(self.dir_name.split("_")[0:3])
        note_names = []
        os.makedirs(attach_path, exist_ok=True)
        pc = get_plot_count(attach_path)
        for i, row in df_data.iterrows():
            txt_construct = ""
            dir_name = row["construct"] + "_" + row["code"] + "_" + row["data_type"]
            if not os.path.exists(
                f"{self.path}/processed/{dir_name}/output/BitVector_Files/summary.csv"
            ):
                log.warn(f"no processed data for {dir_name}")
                note_names.append("")
                continue
            summary_csv = (
                f"{self.path}/processed/{dir_name}/output/BitVector_Files/summary.csv"
            )
            org_path = f"{self.path}/processed/{dir_name}/output/BitVector_Files/"
            df_sum = pd.read_csv(summary_csv)
            txt_construct += f"## {row['construct']}\n"
            txt_construct += (
                tabulate(df_sum, headers="keys", tablefmt="github", showindex=True)
                + "\n\n"
            )
            for j, row2 in df_sum.iterrows():
                org_plot_path = glob.glob(f"{org_path}/{row2['name']}_*.png")[0]
                if len(df_sum) > 1:
                    txt_construct += "### " + row2["name"] + "\n"
                shutil.copy(org_plot_path, f"{attach_path}/{pc}.png")
                txt_construct += f"![png](attachments/{pc}.png)\n"
                pc += 1
            txt_construct += "\n\n"
            entry_node = SequencingRunEntryNote(date_str, row, txt_construct, self.path)
            note_names.append(entry_node.write_note())
            txt += txt_construct.replace("attachments/", "entries/attachments/")
        df_data["note_name"] = note_names
        return txt, df_data


class SequencingRunEntryNote:
    def __init__(self, date, row, txt, dir_path):
        self.date = date
        self.row = row
        self.txt = txt
        self.dir_path = dir_path
        self.save_path = self.dir_path.replace(DROPBOX_PATH, "$DROPBOX")
        self.construct_name = (
            row["construct"] + "_" + row["code"] + "_" + row["data_type"]
        )
        self.construct_data_file_path = (
            self.dir_path
            + "/processed/"
            + self.construct_name
            + "/output/BitVector_Files/"
        )

    def write_note(self):
        params = get_parameters()
        metadata = self.__generate_metadata()
        notes = "## notes\n\n"
        date_str = "_".join(os.path.basename(self.dir_path).split("_")[0:3])
        note_name = (
            date_str
            + "_"
            + self.row["code"]
            + "_"
            + self.row["data_type"]
            + "_"
            + self.row["barcode"]
        )
        file_path = params["paths"]["sequencing-runs"] + "/entries/" + note_name + ".md"
        if os.path.exists(file_path):
            log.info(f"Note already exists for {self.construct_name}")
            old_metadata = extract_metadata(file_path)
            metadata = merge_metadatas(old_metadata, metadata)
            # overwrite the path in case files got moved
            notes = extract_markdown_section(file_path, "## notes")
        txt = get_metadata_str(metadata)
        txt += f"# {self.construct_name}\n"
        txt += f"## summary\n"
        txt += f"run link: [[{self.row['run_name']}]]\n"
        txt += f"directory link: [data directory link](file:///{self.construct_data_file_path})\n"
        protocol_files = get_protocol_run_files()
        for pf in protocol_files:
            name = os.path.basename(pf).split(".")[0]
            if name == self.row["exp_name"]:
                txt += f"protocol run: {get_protocol_sheet_link(pf)}\n"
        if len(metadata["exp-by"]) > 0:
            joined_names = " ".join(metadata["exp-by"])
            txt += "exp by: "
            for v in people.values():
                if v in joined_names:
                    txt += f"[[{v}]]\t"
            txt += "\n"
        txt += "\n"
        txt += notes
        txt += self.txt
        f = open(file_path, "w")
        f.write(txt)
        f.close()
        return note_name

    def __generate_metadata(self):
        metadata = {
            "type": "sequencing-run-entry",
            "dir-path": self.save_path,
            "path": self.construct_data_file_path,
            "run-name": self.row["run_name"],
            "exp-name": self.row["exp_name"],
            "construct": self.row["construct"],
            "code": self.row["code"],
            "data-type": self.row["data_type"],
            "exp-type": self.row["exp_type"],
            "barcode": self.row["barcode"],
            "barcode-seq": self.row["barcode_seq"],
            "buffer": self.row["buffer"],
            "buffer_conc": self.row["buffer_conc"],
            "mg_conc": self.row["mg_conc"],
            "run-usuable": "YES",
            "run-type": "ISEQ",
            "run-where": "LAB",
            "projects": [],
            "exp-by": [],
        }

        if self.dir_path.find("KU") != -1:
            metadata["run-type"] = "NOVASEQ"
            metadata["run-where"] = "KU"
        act_people = []
        try:
            spl = self.row["exp_name"].split("_")
        except:
            spl = []
        for k, v in people.items():
            if k in spl:
                act_people.append(v)
        metadata["exp-by"] = act_people
        date = datetime.datetime.strptime(self.date, "%Y-%m-%d")
        metadata = add_dates_to_metadata(metadata, date)

        return metadata
