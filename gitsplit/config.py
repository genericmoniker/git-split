import collections
from pathlib import Path

import toml


class Config:
    """File split configuration."""

    def __init__(self, config_data: str, base_path: Path):
        self._base_path = base_path
        data = toml.loads(config_data)
        source = data.get("source")
        if not source:
            raise ConfigError("Source file not specified in the config file.")
        self._source_file = SourceFile(base_path / source)

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


class SourceFile:
    """A source file to be split."""

    def __init__(self, path: Path):
        if not path.exists():
            raise ConfigError(f'Source file "{path}" does not exist.')
        self._path = path
        self._line_count = None

    @property
    def line_count(self):
        if self._line_count is None:
            self._line_count = sum(1 for _ in self.lines)
        return self._line_count

    @property
    def lines(self):
        with self._path.open("r") as f:
            yield from f


class SplitFile:
    """A target file for splitting into."""

    def __init__(self, path: Path, lines: str):
        self._path = path
        self._lines = lines

    def exists(self):
        return self._path.exists()

    def todo(self):
        pass
