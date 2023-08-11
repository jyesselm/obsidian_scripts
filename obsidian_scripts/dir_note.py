import os
import datetime
import glob
import json
import pandas as pd
from tabulate import tabulate


from obsidian_scripts.markdown import (
    add_dates_to_metadata,
    get_metadata_str,
    extract_metadata,
    merge_metadatas,
    extract_markdown_section,
)
from obsidian_scripts.paths import DROPBOX_PATH, NOTES_PATH
from obsidian_scripts.logger import get_logger

log = get_logger("DIR-NOTE")


def get_protocol_run_files():
    path = "/Users/jyesselman2/gdrive/protocol_runs"
    protcol_run_files = glob.glob(f"{path}/*/*.gsheet")
    return protcol_run_files


class DirectoryNote:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.save_path = self.path.replace(DROPBOX_PATH, "$DROPBOX")
        self.dir_name = os.path.basename(self.path)

    def write_note(self):
        constructs, construct_codes = self.__get_created_constructs()
        metadata = self.__generate_metadata(constructs, construct_codes)
        note_file_path = f"{NOTES_PATH}/dirs/{metadata['dir-type']}/{self.dir_name}.md"
        notes = "## notes\n\n"
        if os.path.exists(note_file_path):
            log.info(f"Note already exists for {self.dir_name}")
            old_metadata = extract_metadata(note_file_path)
            metadata = merge_metadatas(old_metadata, metadata)
            # overwrite the path in case files got moved
            metadata["path"] = self.save_path
            notes = extract_markdown_section(note_file_path, "## notes")
        # add in merge metadata here
        txt = get_metadata_str(metadata)
        txt += f"# {self.dir_name}\n\n"
        txt += f"[file link](file:///{self.path})\n\n"
        txt += notes
        # need to add logging statements to say if it found these segments
        txt += self.__add_command_txt()
        txt += self.__add_setup_script_txt()
        txt += self.__add_construct_links_txt(constructs, construct_codes)
        txt += self.__add_primer_info_txt()
        txt += self.__add_protocol_run_links_txt(construct_codes)
        f = open(note_file_path, "w")
        f.write(txt)
        f.close()

    def __get_created_constructs(self):
        constructs = []
        construct_codes = []
        if os.path.isdir(f"{self.path}/seq-deposit-output"):
            df_constructs = pd.read_csv(
                f"{self.path}/seq-deposit-output/constructs.csv"
            )
            for i, row in df_constructs.iterrows():
                constructs.append(row["name"])
                construct_codes.append(row["code"])
        return constructs, construct_codes

    def __generate_metadata(self, constructs, construct_codes):
        date_str = "-".join(self.dir_name.split("_")[0:3])
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        metadata = {
            "type": "dir",
            "path": self.save_path,
            "dir-type": "unclassified",
            "dir-designed-by": "Joe Yesselman",
            "dir-constructs-codes": "[" + " ".join(construct_codes) + "]",
            "dir-constructs": "[" + " ".join(constructs) + "]",
            "dir-summary": "",
            "dir-keywords": "",
            "dir-finished": "NO",
            "dir-constructs-ordered": "NO",
            "project": "",
        }
        if len(constructs) > 0:
            metadata["dir-constructs-ordered"] = "YES"
        add_dates_to_metadata(metadata, date)
        if "construct_design" in self.path:
            metadata["dir-type"] = "construct-design"
        elif "analysis" in self.path:
            metadata["dir-type"] = "analysis"
        elif "paper" in self.path:
            metadata["dir-type"] = "paper"
        return metadata

    # conditional adds if the data is present
    def __add_command_txt(self):
        if not os.path.isfile(f"{self.path}/COMMANDS"):
            return ""
        txt = f"## commands\n\n"
        f = open(f"{self.path}/COMMANDS")
        script_lines = f.readlines()
        f.close()
        txt += f"```bash\n{''.join(script_lines)}\n```\n\n"
        return txt

    def __add_setup_script_txt(self):
        if not os.path.isfile(f"{self.path}/scripts/setup.py"):
            return ""
        txt = f"## setup script\n\n"
        f = open(f"{self.path}/scripts/setup.py")
        script_lines = f.readlines()
        f.close()
        txt += f"```python\n{''.join(script_lines)}\n```\n\n"
        return txt

    def __add_construct_links_txt(self, constructs, construct_codes):
        if len(constructs) == 0:
            return ""
        txt = f"## constructs \n\n"
        for name, code in zip(constructs, construct_codes):
            txt += f"[[{code}--{name}]]\n"
        txt += "\n\n"
        return txt

    def __add_primer_info_txt(self):
        if not os.path.isfile(f"{self.path}/seq-deposit-output/primers.csv"):
            return ""
        txt = f"## primers \n\n"
        df_primers = pd.read_csv(f"{self.path}/seq-deposit-output/primers.csv")
        txt += tabulate(df_primers, headers="keys", tablefmt="github")
        txt += "\n\n"
        df_assembly = pd.read_csv(f"{self.path}/seq-deposit-output/assemblies.csv")
        txt += tabulate(df_assembly, headers="keys", tablefmt="github")
        txt += "\n\n"
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
