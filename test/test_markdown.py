import os
from pathlib import Path
import pytest
from obsidian_scripts.markdown import (
    extract_metadata,
    extract_markdown_section,
    split_markdown_by_headings,
)

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
RESOURCE_DIR = TEST_DIR / "resources"


class TestExtractMetadata:
    def test_no_file(self):
        with pytest.raises(ValueError):
            extract_metadata("fake.md")

    def test_no_meta_data(self):
        path = RESOURCE_DIR / "md_files/no_meta_data.md"
        meta_data = extract_metadata(path)
        assert meta_data == {}

    def test_empty_meta_data(self):
        path = RESOURCE_DIR / "md_files/empty_meta_data.md"
        meta_data = extract_metadata(path)
        assert meta_data == {}

    def test_single(self):
        path = RESOURCE_DIR / "md_files/single_meta_data.md"
        meta_data = extract_metadata(path)
        assert meta_data["date"] == "2023-02-24"

    def test_list(self):
        path = RESOURCE_DIR / "md_files/list_meta_data.md"
        meta_data = extract_metadata(path)
        assert meta_data["constructs"] == ["C0001", "C0002", "C0003"]


class TestSplitMarkdownByHeadings:
    def test_simple(self):
        path = RESOURCE_DIR / "md_files/simple.md"
        with open(path, "r", encoding="utf8") as f:
            lines = f.readlines()
        text = "".join(lines)
        sections = split_markdown_by_headings(text)
        assert len(sections) == 5
        assert sections[0][0] == 1
        assert sections[0][1] == "# heading1 \n\n"


class TestExtractMarkdownSection:
    def _test_no_file(self):
        with pytest.raises(ValueError):
            extract_markdown_section("fake.md", "fake")

    def test(self):
        section = extract_markdown_section(
            RESOURCE_DIR / "md_files/simple.md", "# heading1"
        )
        assert section.split("\n")[0] == "# heading1 "
