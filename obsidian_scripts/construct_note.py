import os
import datetime
import json
import glob
import pandas as pd

from obsidian_scripts.markdown import (
    get_metadata_str,
    add_dates_to_metadata,
    extract_markdown_section,
    extract_metadata,
    merge_metadatas,
)
from obsidian_scripts.paths import LIB_DIR
from obsidian_scripts.parameters import get_parameters
from obsidian_scripts.logger import get_logger

log = get_logger("CONSTRUCT_NOTE")


def get_protocol_run_files():
    path = "/Users/jyesselman2/gdrive/protocol_runs"
    protcol_run_files = glob.glob(f"{path}/*/*.gsheet")
    return protcol_run_files


def get_dir_note(construct_name):
    with open(f"{LIB_DIR}/resources/construct-design-dirs.json", "r") as f:
        construct_design_dict = json.load(f)
    for dir_name, metadata in construct_design_dict.items():
        # safe guard for older notes for now
        if "dir-constructs" not in metadata:
            continue
        if construct_name in metadata["dir-constructs"]:
            return [dir_name, metadata]
    return [None, None]


class ConstructNote:
    def __init__(self, dir_path, construct_row, df_pa):
        self.dir_path = dir_path
        self.construct_row = construct_row
        self.df_pa = df_pa

    def write_note(self):
        txt = ""
        params = get_parameters()
        note_name = f"{self.construct_row['code']}--{self.construct_row['name']}"
        dir_name, dir_metadata = get_dir_note(self.construct_row["name"])
        metadata = self.__generate_metadata(self.construct_row, dir_name, dir_metadata)
        note_file_path = f"{params['paths']['constructs']}/{note_name}.md"
        notes = "## notes\n\n"
        if os.path.exists(note_file_path):
            log.info(f"Note already exists for {note_name}")
            old_metadata = extract_metadata(note_file_path)
            metadata = merge_metadatas(old_metadata, metadata)
            notes = extract_markdown_section(note_file_path, "## notes")
        txt += get_metadata_str(metadata)
        txt += f"# {note_name}\n\n"
        if dir_name is not None:
            txt += f"construct design -> [[{dir_name}]]\n"
        txt += notes
        txt += self.__get_how_to_make_txt(self.construct_row)
        txt += self.__get_sequence_info_txt(self.construct_row)
        txt += self.__add_protocol_run_links_txt([self.construct_row["code"]])
        f = open(note_file_path, "w")
        f.write(txt)
        f.close()

    def __generate_metadata(self, construct_row, dir_name, dir_metadata):
        metadata = {
            "type": "construct",
            "construct-code": construct_row["code"],
            "construct-name": construct_row["name"],
            "construct-type": construct_row["type"],
            "construct-size": construct_row["size"],
            "construct-usable": construct_row["usuable"],
            "construct-rna-length": construct_row["rna_len"],
            "construct-dna-length": construct_row["dna_len"],
            "construct-fwd-primer": construct_row["fwd_p"],
            "construct-rev-primer": construct_row["rev_p"],
            "construct-seq-fwd-primer": construct_row["seq_fwd_p"],
            "construct-fasta-path": f"$SEQPATH/fastas/{construct_row['code']}.fasta",
            "construct-rna-path": f"$SEQPATH/rna/{construct_row['code']}.csv",
            "construct-dna-path": f"$SEQPATH/dna/{construct_row['code']}.csv",
            "comment": construct_row["comment"],
        }
        if construct_row["project"] is not None:
            metadata["project"] = construct_row["project"]
        if dir_name is None:
            metadata["construct-dir"] = ""
            add_dates_to_metadata(metadata, datetime.date.today())
        else:
            metadata["construct-dir"] = dir_name
            metadata["date"] = dir_metadata["date"]
            metadata["year"] = dir_metadata["year"]
            metadata["week"] = dir_metadata["week"]
        return metadata

    def __get_how_to_make_txt(self, construct_row):
        txt = ""
        if construct_row["type"] == "ASSEMBLY":
            txt += "## how make by primer assembly\n"
            txt += "```\n"
            primers = self.df_pa[self.df_pa["code"] == construct_row["code"]]
            if len(primers) < 0:
                log.error(f"no primers found for {construct_row['code']}")
            else:
                for _, primer in primers.iterrows():
                    txt += f"{primer['p_name']}\t{primer['p_code']}\t{primer['code']}\n"
            txt += "```\n\n"
            return txt
        else:
            return ""

    def __get_sequence_info_txt(self, construct_row):
        txt = "## sequence infomation\n\n"
        code = construct_row["code"]
        if not os.path.isfile(f"{os.environ['SEQPATH']}/rna/{code}.csv"):
            log.warn(f"no rna csv found for {code}")
            return ""
        if not os.path.isfile(f"{os.environ['SEQPATH']}/dna/{code}.csv"):
            log.warn(f"no rna csv found for {code}")
            return ""
        df_rna_seq = pd.read_csv(f"{os.environ['SEQPATH']}/rna/{code}.csv")
        df_dna_seq = pd.read_csv(f"{os.environ['SEQPATH']}/dna/{code}.csv")
        for i, row in df_rna_seq.iterrows():
            dna_row = df_dna_seq.iloc[i]
            txt += f"### {row['name']}\n"
            txt += f"```\nDNA seq: {dna_row['sequence']}\n"
            txt += f"RNA seq: {row['sequence']}\nRNA ss:  {row['structure']}\n```\n\n"
            if i > 100:
                break
        return txt

    def __add_protocol_run_links_txt(self, construct_codes):
        protocol_run_files = get_protocol_run_files()
        current_runs = []
        for r_file in protocol_run_files:
            for code in construct_codes:
                if r_file.find(code) != -1:
                    if r_file not in current_runs:
                        current_runs.append(r_file)
        gsheet_path = "https://docs.google.com/spreadsheets/d"
        if len(current_runs) == 0:
            return ""
        txt = "## protocol runs\n\n"
        for run in current_runs:
            run_name = os.path.basename(run)
            run_info = json.load(open(run))
            txt += f"<a href={gsheet_path}/{run_info['doc_id']}>{run_name}</a>\n"
        return txt
