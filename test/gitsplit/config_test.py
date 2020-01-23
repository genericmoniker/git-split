from pathlib import Path

import pytest

from gitsplit.config import Config, ConfigError, SourceFile


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


@pytest.mark.xfail(reason="Not yet implemented.")
def test_config_error_if_split_file_has_no_lines(fs):
    config_data = 'source="src"\n[file]\n'
    fs.create_file("src")
    with pytest.raises(ConfigError) as excinfo:
        Config(config_data, base_path=Path("/"))
    assert "lines" in str(excinfo.value)


def test_source_file_line_count(fs):
    fs.create_file("src", contents="one \n two \n three \n")
    source_file = SourceFile(Path("src"))
    assert source_file.line_count == 3


def test_source_file_lines(fs):
    fs.create_file("src", contents="one \n two \n three \n")
    source_file = SourceFile(Path("src"))
    assert list(source_file.lines) == ["one \n", " two \n", " three \n"]
