import collections
from pathlib import Path

import toml


class Config:
    """File split configuration."""

    def __init__(self, config_data: str, base_path: Path):
        self._base_path = base_path
        data = toml.loads(config_data)
        self._split_files = [
            base_path / k
            for k in data.keys()
            if isinstance(data[k], collections.abc.Mapping)
        ]
        if not self._split_files:
            raise ConfigError("No split files specified in the config file.")
        for f in self._split_files:
            if f.exists():
                raise ConfigError(f'Split file "{f}" already exists.')

    @classmethod
    def from_file(cls, config_file: Path) -> "Config":
        return cls(config_file.read_text(), config_file.parent)

    @property
    def split_files(self):
        return self._split_files


class ConfigError(Exception):
    """Exception raised for configuration errors."""
