import shutil
import subprocess
from typing import Optional
from dataclasses import dataclass

from obsidian_scripts.logger import get_logger

log = get_logger("EXTERNAL_CMD")


@dataclass(frozen=True, order=True)
class ProgOutput:
    """
    Class to store the output of an external program
    """

    output: Optional[str]
    error: Optional[str]


def does_program_exist(prog_name: str) -> bool:
    """
    Check if a program exists
    :param prog_name: name of the program
    """
    if shutil.which(prog_name) is None:
        return False
    else:
        return True


def run_command(cmd: str) -> ProgOutput:
    """
    Run a command and return the output
    :param cmd: command to run
    """
    output, error_msg = None, None
    try:
        output = subprocess.check_output(
                cmd, shell=True, stderr=subprocess.STDOUT
        ).decode("utf8")
    except subprocess.CalledProcessError as exc:
        error_msg = exc.output.decode("utf8")
    return ProgOutput(output, error_msg)


def run_nbconvert(notebook_path):
    pout = run_command(f"jupyter nbconvert --to markdown {notebook_path}")
    return pout


def run_mogrify(plot_path):
    pout = run_command(f"mogrify -background white -flatten {plot_path}/*.png")
    return pout
