import os
import shutil
from pathlib import Path
from obsidian_scripts.external_cmd import does_program_exist, run_nbconvert, run_mogrify

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
RESOURCE_DIR = TEST_DIR / "resources"


def test_does_program_exist():
    does_program_exist("jupyter")
    does_program_exist("mogrify")


def test_run_nbconvert():
    nb_path = RESOURCE_DIR / "notebooks/simple.ipynb"
    md_path = RESOURCE_DIR / "notebooks/simple.md"
    plot_path = RESOURCE_DIR / "notebooks/simple_files"
    run_nbconvert(nb_path)
    assert md_path.exists()
    assert plot_path.exists()
    os.remove(md_path)
    shutil.rmtree(plot_path)


def test_run_mogrify():
    nb_path = RESOURCE_DIR / "notebooks/simple.ipynb"
    plot_path = RESOURCE_DIR / "notebooks/simple_files"
    run_nbconvert(nb_path)
    run_mogrify(plot_path)
    shutil.rmtree(plot_path)
