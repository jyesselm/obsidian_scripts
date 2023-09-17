import os

LIB_DIR = os.path.dirname(os.path.realpath(__file__))
# get one director back
ROOT_DIR = os.path.dirname(LIB_DIR)
# test dir
TEST_DIR = os.path.join(ROOT_DIR, "test")


DROPBOX_PATH = "/Users/jyesselman2/Dropbox"
NOTES_PATH = f"{DROPBOX_PATH}/notes/"
