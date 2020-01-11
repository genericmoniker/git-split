from pathlib import Path
from unittest import mock

import pytest

from gitsplit.config import Config, ConfigError


def test_config_error_if_no_split_files():
    config_data = 'source="src"'
    with pytest.raises(ConfigError) as excinfo:
        Config(config_data, base_path=Path("/"))
    assert "split files" in str(excinfo.value)


def test_config_error_if_split_file_exists():
    config_data = 'source="src"\n[exists]\nlines="1"'
    with mock.patch.object(Path, "exists", return_value=True):
        with pytest.raises(ConfigError) as excinfo:
            Config(config_data, base_path=Path("/"))
    assert "exists" in str(excinfo.value)
