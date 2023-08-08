import os
import datetime


from obsidian_scripts.markdown import get_metadata_str


class ConstructNote:
    def __init__(self, dir_path, construct_row, df_pa):
        self.dir_path = dir_path
        self.construct_row = construct_row
        self.df_pa = df_pa

    def generate_text(self):
        txt = ""
        metadata = self.__generate_metadata(self.construct_row)

    def __generate_metadata(self, construct_row):
        cur_date = datetime.date.today()
        metadata = {
            "date": cur_date,
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
        return metadata


def __generate_construct_note(dir_path, construct_row, df_pa):
    txt = get_metadata_str(metadata) + "\n"
    txt += f"# {construct_row['code']} -- {construct_row['name']}\n\n"
    txt += "## How to make\n\n"
    if construct_row["type"] == "ASSEMBLY":
        txt += "make by primer assembly\n"
        txt += "```\n"
        primers = df_pa[df_pa["code"] == construct_row["code"]]
        if len(primers) < 0:
            log.error(f"no primers found for {construct_row['code']}")
        else:
            for _, primer in primers.iterrows():
                txt += f"{primer['p_name']}\t{primer['p_code']}\t{primer['code']}\n"
        txt += "```\n"
    txt += "## Sequence infomation\n\n"
    df_rna_seq = pd.read_csv(f"{os.environ['SEQPATH']}/rna/{construct_row['code']}.csv")
    df_dna_seq = pd.read_csv(f"{os.environ['SEQPATH']}/dna/{construct_row['code']}.csv")
    for i, row in df_rna_seq.iterrows():
        dna_row = df_dna_seq.iloc[i]
        txt += f"### {row['name']}\n"
        txt += f"```\nDNA seq: {dna_row['sequence']}\nRNA seq: {row['sequence']}\nRNA ss:  {row['structure']}\n```\n\n"
        if i > 100:
            break

    path = dir_path + construct_row["code"] + "--" + construct_row["name"] + ".md"
    f = open(path, "w")
    f.write(txt)
    f.close()
