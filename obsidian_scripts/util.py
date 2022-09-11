import glob
from pathlib import Path

def get_plot_count(path):
    pngs = glob.glob(f"{path}*.png")
    num = -1
    for png in pngs:
        fname = Path(png).stem
        c_num = int(fname)
        if c_num > num:
            num = c_num
    return num + 1


