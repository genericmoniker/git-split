import re
import shutil
import sys
from pathlib import Path
from subprocess import PIPE, run
from unittest import mock

import pytest

from gitsplit.main import main


@pytest.fixture(name="repo")
def repo_fixture(tmp_path):
    run(["git", "init"], check=True, cwd=str(tmp_path))
    file = tmp_path / "foods"
    edit(file, "apple\ncelery\ncheese\n", "Alice <alice>")
    edit(file, "eggs\ngrape\nlettuce\n", "Bob <bob>")
    edit(file, "milk\norange\npeas\n", "Carol <carol>")
    return tmp_path


def edit(path: Path, text: str, author: str):
    """Edit a file and commit the edited file with git.

    :param path: path to the file to edit, which must be in a git repo.
    :param text: text to append to the file.
    :param author: author to use for the commit.
    """
    cwd = str(path.parent)
    exists = path.exists()
    with path.open("a") as f:
        f.write(text)
    if not exists:
        run(["git", "add", str(path)], check=True, cwd=cwd)
    run(["git", "commit", "-am", "msg", f'--author="{author}"'], check=True, cwd=cwd)


def get_config(repo_path: Path, filename: str) -> Path:
    """Get a config file, copied from the test directory into repo_path.

    :param repo_path: path to the repo into which to copy the config file.
    :param filename: name of the file from the test directory.
    :return: the path to the copied config file.
    """
    config_src = Path(__file__).parent / filename
    config_file = repo_path / config_src.name
    shutil.copy(config_src, config_file)
    return config_file


def get_blame(repo_path: Path, filename: str) -> str:
    """Get the `git blame` output for a file."""
    return run(
        ["git", "blame", filename], check=True, cwd=str(repo_path), stdout=PIPE
    ).stdout.decode()


def is_author(author: str, text: str, blame: str) -> bool:
    """Determine if an author authored the given text."""
    for line in blame.splitlines():
        if re.match(f".*{author}.+{text}", line):
            return True
    return False


def test_split_source_into_multiple_destinations(repo):
    """Split a file into multiple files.

    https://devblogs.microsoft.com/oldnewthing/20190916-00/?p=102892
    """
    config_file = get_config(repo, "foods.split.toml")

    with mock.patch.object(sys, "argv", ["git-split", str(config_file)]):
        main()

    dairy = repo / "dairy"
    fruits = repo / "fruits"
    veggies = repo / "veggies"
    assert dairy.read_text() == "cheese\neggs\nmilk\n"
    assert fruits.read_text() == "apple\ngrape\norange\n"
    assert veggies.read_text() == "celery\nlettuce\npeas\n"

    blame = get_blame(repo, "dairy")
    assert is_author("Alice", "cheese", blame)
    assert is_author("Bob", "eggs", blame)
    assert is_author("Carol", "milk", blame)
    blame = get_blame(repo, "fruits")
    assert is_author("Alice", "apple", blame)
    assert is_author("Bob", "grape", blame)
    assert is_author("Carol", "orange", blame)
    blame = get_blame(repo, "veggies")
    assert is_author("Alice", "celery", blame)
    assert is_author("Bob", "lettuce", blame)
    assert is_author("Carol", "peas", blame)


def test_extract_section_from_source(repo):
    """Test extracting sections of the source into new files.

    https://devblogs.microsoft.com/oldnewthing/20190917-00/?p=102894
    """
    config_file = get_config(repo, "foods.extract.toml")

    with mock.patch.object(sys, "argv", ["git-split", str(config_file)]):
        main()

    foods = repo / "foods"
    fruits = repo / "fruits"
    veggies = repo / "veggies"
    assert foods.read_text() == "cheese\neggs\nmilk\n"
    assert fruits.read_text() == "apple\ngrape\norange\n"
    assert veggies.read_text() == "celery\nlettuce\npeas\n"

    blame = get_blame(repo, "foods")
    assert is_author("Alice", "cheese", blame)
    assert is_author("Bob", "eggs", blame)
    assert is_author("Carol", "milk", blame)
    blame = get_blame(repo, "fruits")
    assert is_author("Alice", "apple", blame)
    assert is_author("Bob", "grape", blame)
    assert is_author("Carol", "orange", blame)
    blame = get_blame(repo, "veggies")
    assert is_author("Alice", "celery", blame)
    assert is_author("Bob", "lettuce", blame)
    assert is_author("Carol", "peas", blame)
