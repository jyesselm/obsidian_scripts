import os
from pathlib import Path
import pytest
from obsidian_scripts.markdown import extract_meta_data

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
RESOURCE_DIR = TEST_DIR / "resources"



class TestExtractMetadata:
    def test_no_file(self):
        with pytest.raises(ValueError):
            extract_meta_data("fake.md")

    def test_no_meta_data(self):
        path = RESOURCE_DIR / "md_files/no_meta_data.md"
        meta_data = extract_meta_data(path)
        assert meta_data == {}

    def test_empty_meta_data(self):
        path = RESOURCE_DIR / "md_files/empty_meta_data.md"
        meta_data = extract_meta_data(path)
        assert meta_data == {}

    def test_single(self):
        path = RESOURCE_DIR / "md_files/single_meta_data.md"
        meta_data = extract_meta_data(path)
        assert meta_data['date'] == '2023-02-24'

    def test_list(self):
        path = RESOURCE_DIR / "md_files/list_meta_data.md"
        meta_data = extract_meta_data(path)
        assert meta_data['constructs'] == ['C0001', 'C0002', 'C0003']
