import collections
from pathlib import Path

import toml
from ranges import Range, RangeSet


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
            SplitFile(base_path / k, data[k], self._source_file.line_count)
            for k in data.keys()
            if isinstance(data[k], collections.abc.Mapping)
        ]
        if not self._split_files:
            raise ConfigError("No split files specified in the config file.")
        for f in self._split_files:
            if f.exists():  # No
                raise ConfigError(f'Split file "{f}" already exists.')
        for split_file in self._split_files:
            if split_file.has_star:
                split_file.expand_star(
                    self._source_file.line_count,
                    (split for split in self._split_files if split != split_file),
                )
                break

    @classmethod
    def from_file(cls, config_file: Path) -> "Config":
        """Create a configuration from a file."""
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

    def __init__(self, path: Path, split_data: collections.abc.Mapping, max_line: int):
        self._path = path
        self._has_star = False
        self._lines = self._create_line_ranges(split_data, max_line)

    def __contains__(self, item):
        return item in self._lines

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
        print("source_file_range:", source_file_range)
        union_of_splits = RangeSet()
        for split in other_split_files:
            lines = split._lines  # pylint: disable=protected-access
            union_of_splits = union_of_splits.union(lines)
        print("union_of_splits:", union_of_splits)
        diff = source_file_range.symmetric_difference(union_of_splits)
        print("diff:", diff)
        self._lines.extend(diff)
