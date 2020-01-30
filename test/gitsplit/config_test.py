from pathlib import Path

import pytest

from gitsplit.config import Config, ConfigError, SourceFile, SplitFile


def test_config_error_if_source_file_not_specified():
    config_data = '[file]\nlines="1"'
    with pytest.raises(ConfigError) as excinfo:
        Config(config_data, base_path=Path("/"))
    assert "Source" in str(excinfo.value)


@pytest.mark.usefixtures("fs")
def test_config_error_if_source_file_does_not_exist():
    config_data = 'source="src"\n[file]\nlines="1"'
    with pytest.raises(ConfigError) as excinfo:
        Config(config_data, base_path=Path("/"))
    assert "exist" in str(excinfo.value)


def test_config_error_if_no_split_files(fs):
    config_data = 'source="src"'
    fs.create_file("src")
    with pytest.raises(ConfigError) as excinfo:
        Config(config_data, base_path=Path("/"))
    assert "split files" in str(excinfo.value)


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"lines": ""},
        {"lines": " \t"},
        {"lines": "0-10"},
        {"lines": "2-1"},
        {"lines": "-2-1"},
        {"lines": "1-10-20"},
        {"lines": "1-q"},
        {"lines": "blah"},
        {"lines": "200-201"},
        {"lines": "201"},
    ],
)
def test_config_error_if_split_file_has_invalid_lines(data):
    with pytest.raises(ConfigError) as excinfo:
        SplitFile(Path(), data, max_line=200)
    assert "lines" in str(excinfo.value)


@pytest.mark.parametrize(
    "data, lines_in",
    [
        ({"lines": "1"}, [1]),
        ({"lines": "1,2"}, [1, 2]),
        ({"lines": "5-10"}, [5, 6, 7, 8, 9, 10]),
        ({"lines": "100-102, 25, 33-34"}, [25, 33, 34, 100, 101, 102]),
    ],
)
def test_split_file_lines(data, lines_in):
    split_file = SplitFile(Path(), data, max_line=200)
    assert all(line in split_file for line in lines_in)


@pytest.mark.parametrize(
    "config_data, lines_in",
    [
        ('source="src"\n[f1]\nlines="1,3,5"\n[star]\nlines="*"', [2, 4, 6]),
        ('source="src"\n[f1]\nlines="1,3,5"\n[star]\nlines="1, *"', [1, 2, 4, 6]),
        ('source="src"\n[f1]\nlines="1-3"\n[star]\nlines="*"\n[f2]\nlines="6"', [4, 5]),
        ('source="src"\n[star]\nlines="*"', [1, 2, 3, 4, 5, 6]),
    ],
)
def test_split_file_wildcard_line(config_data, lines_in, fs):
    fs.create_file("src", contents="A\nB\nC\nD\nE\nF\n")
    config = Config(config_data, base_path=Path("/"))
    star_split_file = next(split for split in config.split_files if split.has_star)
    assert all(line in star_split_file for line in lines_in)


def test_source_file_line_count(fs):
    fs.create_file("src", contents="one \n two \n three \n")
    source_file = SourceFile(Path("src"))
    assert source_file.line_count == 3


def test_source_file_lines(fs):
    fs.create_file("src", contents="one \n two \n three \n")
    source_file = SourceFile(Path("src"))
    assert list(source_file.lines) == ["one \n", " two \n", " three \n"]
