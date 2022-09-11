import glob
import click
from pathlib import Path

from obsidian_scripts.logger import setup_applevel_logger, get_logger
from obsidian_scripts.format_sequencing_run import format

@click.command()
@click.argument("start_dir")
def main(start_dir):
    setup_applevel_logger()
    log = get_logger("MAIN")
    #log.info("ARE YOU SURE YOU WANT TO DELETE ALL SEQUENCING RUNS??")
    #log.info("YES or NO?")
    #r = input()
    #if r.lower() != "yes":
    #    log.info("EXITING")
    #    exit()
    dirs = glob.glob(f"{start_dir}/*")
    for d in dirs:
        name = Path(d).stem
        spl = name.split("_")
        if len(spl) < 3:
            continue
        format(d)


if __name__ == '__main__':
    main()