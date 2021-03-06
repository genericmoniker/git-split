import collections
from os import fspath
from pathlib import Path

import toml
from ranges import Range, RangeSet


class Config:
    """File split configuration."""

    def __init__(self, data: collections.abc.Mapping, base_path: Path):
        """Create a configuration.

        :param data: configuration data.
        :param base_path: base path for any relative paths in `data`.
        """
        self.base_path = base_path
        source = data.get("source")
        if not source:
            raise ConfigError("Source file not specified in the config file.")
        self.source_file = SourceFile(base_path / source)

        self.split_files = [
            SplitFile(base_path / k, data[k], self.source_file.line_count)
            for k in data.keys()
            if isinstance(data[k], collections.abc.Mapping)
        ]
        if not self.split_files:
            raise ConfigError("No split files specified in the config file.")
        for split_file in self.split_files:
            if split_file.has_star:
                split_file.expand_star(
                    self.source_file.line_count,
                    (split for split in self.split_files if split != split_file),
                )
                break
        self.commit_no_verify = data.get("commit_no_verify", False)

    @classmethod
    def from_file(cls, config_file: Path) -> "Config":
        """Create a configuration from a file."""
        # Use TOML for now; other formats could be handled if desired.
        return cls.from_toml(config_file.read_text(), config_file.parent)

    @classmethod
    def from_toml(cls, toml_data: str, base_path: Path) -> "Config":
        return cls(toml.loads(toml_data), base_path)


class ConfigError(Exception):
    """Exception raised for configuration errors."""


class SourceFile:
    """A source file to be split."""

    def __init__(self, path: Path):
        if not path.exists():
            raise ConfigError(f'Source file "{path}" does not exist.')
        self._path = path
        self._line_count = None
        # We save the file contents early because splitting later involves using
        # git mv on the source file, and it won't be there anymore to read.
        self._lines = path.read_text().splitlines(keepends=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(path={self._path})"

    def __fspath__(self):
        return fspath(self._path)

    def __getattr__(self, attr):
        # Delegate any other attributes to `Path`.
        return getattr(self._path, attr)

    @property
    def line_count(self):
        if self._line_count is None:
            self._line_count = sum(1 for _ in self.lines)
        return self._line_count

    @property
    def lines(self):
        return self._lines

    def difference(self, split_file: "SplitFile") -> "SplitFile":
        """Create a SplitFile of the difference with another SplitFile.

        That is, create a SplitFile that has all of the lines of this SourceFile except
        for lines in `split_file`.
        """
        diff_split = SplitFile(self._path, {"lines": "*"}, self.line_count)
        diff_split.expand_star(self.line_count, [split_file])
        return diff_split


class SplitFile:
    """A target file for splitting into."""

    def __init__(self, path: Path, split_data: collections.abc.Mapping, max_line: int):
        self._path = path
        self._has_star = False
        self._lines = self._create_line_ranges(split_data, max_line)
        self._file = None

    def __repr__(self):
        return f"{self.__class__.__name__}(path={self._path})"

    def __fspath__(self):
        return fspath(self._path)

    def __contains__(self, item):
        return item in self._lines

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.close()

    def __getattr__(self, attr):
        # Delegate any other attributes to `Path`.
        return getattr(self._path, attr)

    def _create_line_ranges(self, split_data: collections.abc.Mapping, max_line: int):
        lines = split_data.get("lines")
        if not lines or not lines.strip():
            raise ConfigError(f'No lines specified for split file "{self._path}".')

        range_set = RangeSet()
        line_ranges = lines.split(",")
        for line_range in line_ranges:
            start, _, end = line_range.partition("-")
            if start.strip() == "*":
                self._has_star = True
                continue
            try:
                start = int(start)
                end = int(end) if end else start
                if not 0 < start <= max_line or not 0 < end <= max_line:
                    raise ValueError(f"Out of range (1-{max_line})")
                range_set.add(Range(start, end, include_end=True))
            except ValueError as ex:
                raise ConfigError(f'Invalid lines for split file "{self._path}": {ex}')
        return range_set

    def exists(self):
        return self._path.exists()

    @property
    def has_star(self):
        """Whether this split file has lines with "*".

        A star indicates that this split file includes all of the lines from the source
        file that aren't included in any other split file.
        """
        return self._has_star

    def expand_star(self, max_line: int, other_split_files):
        source_file_range = Range(1, max_line, include_end=True)
        union_of_splits = RangeSet()
        for split in other_split_files:
            lines = split._lines  # pylint: disable=protected-access
            union_of_splits = union_of_splits.union(lines)
        diff = source_file_range.symmetric_difference(union_of_splits)
        self._lines.extend(diff)

    def open(self):
        self.close()
        self._file = self._path.open("w")

    def close(self):
        if self._file:
            self._file.close()
            self._file = None

    def write(self, text: str):
        if not self._file:
            raise IOError("SplitFile is not open.")
        self._file.write(text)
